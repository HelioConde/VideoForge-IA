"""Source-pixel extraction of Anya's two black/gold horn-shaped hair clips.

These were incorrectly retained in the static Loid/Yor image. Split them
into rigid, independently cropped sprites for the head pivot. This code
does NOT generate AI images or approve the rig. OpenCV merely reconstructs
the occluded static character area so motion cannot reveal the old horns.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .animation_manual import enforce_animation_manual
from .errors import VideoForgeError
from .rig_three_hand_split import read_rgba, rgba_over, sha, unique, write
from .rig_three_hair_draft import SOURCE_SHA, W, H


# Tight source-canvas polygons around the two ornaments of the LARGE Anya
# at the bottom of scene 01. Do not include the smaller Anya at the top.
ORNAMENT_POLYGONS = {
    "left": ((267,1072),(349,1044),(358,1054),(311,1159),
             (296,1168),(278,1106)),
    "right": ((639,1039),(746,1071),(750,1179),(727,1190),
              (665,1090),(649,1064)),
}


def _component_mask(static, polygon, cv2, np):
    if static.shape!=(H,W,4):
        raise VideoForgeError("ANYA_ORNAMENT_SOURCE_CANVAS_INVALID")
    region=np.zeros((H,W),np.uint8)
    cv2.fillPoly(region,[np.asarray(polygon,dtype=np.int32)],1)
    r,g,b,a=[static[:,:,i].astype(np.int16) for i in range(4)]
    # Brown-black and yellow-gold original-source material. This excludes
    # neutral-grey Loid jacket and saturated-red Yor coat around the horns.
    brown=((a>180)&(r>18)&(r<125)&(g>10)&(g<105)&
           (b>8)&(b<96)&((r-g)>=4)&((r-g)<40)&
           ((r-b)>6)&((g-b)>=0))
    gold=((a>180)&(r>117)&(g>78)&(r-g>14)&(g-b>9)&(b<170))
    candidate=((brown|gold)&(region>0)).astype(np.uint8)
    candidate=cv2.morphologyEx(candidate,cv2.MORPH_CLOSE,
                              np.ones((3,3),np.uint8))
    candidate=cv2.dilate(candidate,np.ones((3,3),np.uint8),iterations=1)
    candidate=((candidate>0)&(region>0)&(a>180)).astype(np.uint8)
    n,labels,stats,_=cv2.connectedComponentsWithStats(candidate,8)
    if n<2:
        raise VideoForgeError("ANYA_ORNAMENT_NOT_FOUND")
    winner=int(1+np.argmax(stats[1:,cv2.CC_STAT_AREA]))
    result=labels==winner
    count=int(result.sum())
    gold_count=int(np.count_nonzero(result&gold))
    if not (4700<=count<=5900 and 1000<=gold_count<=1700):
        raise VideoForgeError("ANYA_ORNAMENT_SUSPECT_SOURCE_PIXEL_COUNT")
    return result,count,gold_count


def _tight_rgba(full,mask,np):
    ys,xs=np.nonzero(mask)
    if not len(xs):
        raise VideoForgeError("ANYA_ORNAMENT_EMPTY")
    x,y=int(xs.min()),int(ys.min())
    w,h=int(xs.max()-x+1),int(ys.max()-y+1)
    layer=full[y:y+h,x:x+w].copy()
    layer[:,:,3][~mask[y:y+h,x:x+w]]=0
    return layer,[x,y,w,h]


def separate(original_dir:Path,corrected_dir:Path,dest:Path):
    enforce_animation_manual()
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise VideoForgeError("ANYA_ORNAMENT_OPENCV_REQUIRED") from exc
    source=unique(original_dir,"character-main.png")
    if sha(source)!=SOURCE_SHA:
        raise VideoForgeError("ANYA_ORNAMENT_REFERENCE_SHA_MISMATCH")
    original=read_rgba(source,cv2,np)
    qa=json.loads(unique(corrected_dir,"qa.json").read_text(encoding="utf8"))
    static=unique(corrected_dir,
                  "other-characters-without-anya-candidate.png")
    if (qa.get("source_original_sha256")!=SOURCE_SHA or
        qa.get("files",{}).get(static.name)!=sha(static) or
        qa.get("original_partition_alpha_differences_after_correction")!=0 or
        qa.get("human_visual_approval") is not False or
        qa.get("rig_operational") is not False):
        raise VideoForgeError("ANYA_ORNAMENT_UPSTREAM_QA_INVALID")
    others=read_rgba(static,cv2,np)
    if original.shape!=others.shape or original.shape!=(H,W,4):
        raise VideoForgeError("ANYA_ORNAMENT_INPUT_SIZE_INVALID")
    masks={}
    counts={}
    gold_counts={}
    for side,polygon in ORNAMENT_POLYGONS.items():
        m,c,g=_component_mask(others,polygon,cv2,np)
        masks[side]=m
        counts[side]=c
        gold_counts[side]=g
        if np.any(others[m]!=original[m]):
            raise VideoForgeError("ANYA_ORNAMENT_ORIGINAL_PIXELS_ALTERED")
    if np.any(masks["left"] & masks["right"]):
        raise VideoForgeError("ANYA_ORNAMENT_OVERLAPPING_MASKS")
    mask=masks["left"]|masks["right"]
    # The existing static image contains Loid/Yor and the clips. Reconstruct
    # ONLY hidden background RGB inside these source-qualified pixels.
    # Original RGB under fully transparent Anya pixels still contains PINK
    # hair colours. Feeding those RGB values to Telea created a pink ghost
    # on Loid/Yor; sampling residual GOLD on the horn edges duplicated the
    # ornament in the static plate. Neutralize inpainting *context only*
    # using the original Loid jacket/Yor coat pixels nearest each horn.
    # Outside the actual horn masks the saved source image is unchanged.
    working=others[:,:,:3].copy()
    anchors={
       "left":((260,1030,375,1182),(250,1100)),
       "right":((630,1020,761,1200),(763,1110)),
    }
    for side,((x1,y1,x2,y2),(ax,ay)) in anchors.items():
        if others[ay,ax,3]<250:
            raise VideoForgeError("ANYA_ORNAMENT_UNDERLAY_ANCHOR_INVALID")
        donor=others[ay,ax,:3]
        r,g,b,a=[others[y1:y2,x1:x2,i].astype(np.int16)
                 for i in range(4)]
        gold_context=((r>117)&(g>78)&((r-g)>14)&
                      ((g-b)>9)&(b<170))
        contaminated=(a<100)|gold_context
        working[y1:y2,x1:x2][contaminated]=donor
    bgr=cv2.cvtColor(working,cv2.COLOR_RGB2BGR)
    reconstructed=cv2.inpaint(bgr,mask.astype(np.uint8)*255,
                             5,cv2.INPAINT_TELEA)
    backdrop=others.copy()
    backdrop[:,:,:3][mask]=cv2.cvtColor(
        reconstructed,cv2.COLOR_BGR2RGB)[mask]
    # At the antialiased edge preserve the exact alpha roundtrip:
    # an opaque inpainted backdrop behind a semitransparent clip would
    # otherwise duplicate opacity. The solid core gets a real underlay.
    backdrop[:,:,3][mask&(others[:,:,3]<252)]=0
    sprites={}
    bboxes={}
    for side in ("left","right"):
        sprite,box=_tight_rgba(others,masks[side],np)
        sprites[side]=sprite
        bboxes[side]=box
    # Neutral source proof (strictly compare original static layer before
    # and after splitting; do not pretend this verifies the moving rig).
    l=np.zeros_like(others);r=np.zeros_like(others)
    for side,full in (("left",l),("right",r)):
        x,y,w,h=bboxes[side]
        full[y:y+h,x:x+w]=sprites[side]
    recomposed=rgba_over(rgba_over(backdrop,l,np),r,np)
    visible=(others[:,:,3]>0)
    diff=np.mean(np.abs(
        recomposed[:,:,:3].astype(np.int16)-
        others[:,:,:3].astype(np.int16)),axis=2)
    alpha_diff=np.abs(
        recomposed[:,:,3].astype(np.int16)-others[:,:,3].astype(np.int16))
    delta=float(np.mean(diff[mask]))
    gt20=int(np.count_nonzero(mask&(diff>20)))
    alpha_gt3=int(np.count_nonzero(mask&(alpha_diff>3)))
    # Reject a stationary yellow double-exposure under the new moving
    # ornaments. Both source-local regions had hundreds of gold pixels.
    residual_gold={}
    for side,(x1,y1,x2,y2) in (
        ("left",(260,1040,370,1180)),
        ("right",(630,1030,760,1190))):
        sub=backdrop[y1:y2,x1:x2].astype(np.int16)
        r,g,b,a=[sub[:,:,i] for i in range(4)]
        gold=((a>100)&(r>170)&(g>95)&(b<155)&
              ((r-g)>20)&((g-b)>10))
        residual_gold[side]=int(np.count_nonzero(gold))
    if any(value>20 for value in residual_gold.values()):
        raise VideoForgeError("ANYA_ORNAMENT_YELLOW_GHOST_REMAINS")
    if (delta>2 or gt20>0 or alpha_gt3>0 or
        not np.array_equal(others[~mask],backdrop[~mask])):
        raise VideoForgeError("ANYA_ORNAMENT_NEUTRAL_QA_FAILED_"+str(
            (round(delta,4),gt20,alpha_gt3)))
    if dest.exists() or dest.is_symlink():
        raise VideoForgeError("ANYA_ORNAMENT_NO_OVERWRITE")
    dest.mkdir(parents=True)
    static_name="other-characters-without-ornaments-candidate.png"
    write(dest/static_name,backdrop,cv2)
    for side in ("left","right"):
        write(dest/("ornament-"+side+".png"),sprites[side],cv2)
    document={
        "schema":"videoforge/anya-head-ornaments-source-split/v1",
        "channel":"otaku-br",
        "video_id":"spy-x-family-familia-de-mentira",
        "scene":"cena-01",
        "original_character_sha256":SOURCE_SHA,
        "original_static_other_sha256":sha(static),
        "source_corrected_run_id":43591918632,
        "pixels_moved_per_ornament":counts,
        "original_gold_pixels_per_ornament":gold_counts,
        "bbox_original_canvas":bboxes,
        "total_original_pixels_moved":int(mask.sum()),
        "static_underlay_donor_pixels_original_scene":{
            "left":[250,1100],"right":[763,1110]
        },
        "remaining_stationary_gold_pixels_in_source_regions":residual_gold,
        "original_pixels_preserved_inside_sprites":True,
        "other_characters_unchanged_outside_exact_ornament_mask":True,
        "neutral_recomposition_mean_rgb_delta":round(delta,5),
        "neutral_rgb_error_pixels_gt20":gt20,
        "neutral_alpha_error_pixels_gt3":alpha_gt3,
        "source_character_count_to_animate":1,
        "moving_parent":"anya-head-neck-pivot",
        "ornament_motion":"rigid_with_head_no_independent_wobble",
        "new_image_calls":0,
        "human_visual_approval":False,
        "real_threecanvas_reviewer":"pending",
        "rig_operational":False,
        "video_official":False,
        "youtube_uploaded":False,
        "files":{p.name:sha(p) for p in dest.glob("*.png")},
    }
    (dest/"qa.json").write_text(
        json.dumps(document,ensure_ascii=False,indent=2)+"\n",
        encoding="utf8")
    print("ANYA_ORNAMENT_SOURCE_SPLIT",json.dumps(document,
                                               ensure_ascii=False))
    return document


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--corrected",type=Path,required=True)
    p.add_argument("--dest",type=Path,required=True)
    a=p.parse_args()
    try:
        separate(a.original,a.corrected,a.dest)
        return 0
    except (VideoForgeError,ValueError,KeyError,OSError) as exc:
        print("ANYA_ORNAMENT_SPLIT_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
