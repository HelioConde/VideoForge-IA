"""Reconstruct hidden side-hair and collar pixels from the Anya source art.

This job is *art-preparation only*: OpenCV never replaces ThreeCanvas as an
animation engine. No image-model call. All visible detached pixels remain
identical to the frozen original, while concealed underlays are derived from
the original scene by deterministic inpainting. Human review stays required.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .animation_manual import enforce_animation_manual
from .errors import VideoForgeError
from .rig_three_hand_split import read_rgba, rgba_over, sha, unique, write
from .rig_three_hair_draft import SOURCE_SHA, W, H, _full


def pink_shoulder_mask(body, head, hand, left, right, cv2, np):
    """Select only visible pink hairs stranded on Anya's uniform."""
    if any(a.shape != (H,W,4) for a in (body,head,hand,left,right)):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_CANVAS_INVALID")
    y,x=np.indices((H,W))
    red,green,blue,alpha=(body[:,:,i].astype(np.int16) for i in range(4))
    guard=(((x>=416)&(x<=452))|((x>=577)&(x<=635))) & (y>=1454)&(y<=1500)
    pink=guard&(alpha>0)&(red>165)&(green>85)&(green<205)&(
        blue>90)&(red-green>65)&(red-blue>45)
    mask=(cv2.dilate(pink.astype(np.uint8),
                     np.ones((3,3),np.uint8),iterations=1)>0)
    mask &= guard & (body[:,:,3]>0)&(head[:,:,3]==0)&(
        hand[:,:,3]==0)&(left[:,:,3]==0)&(right[:,:,3]==0)
    count=int(mask.sum())
    if not 350<=count<=750:
        raise VideoForgeError("RIG_HAIR_UNSAFE_PINK_BODY_FRAGMENT_"+str(count))
    return mask


def reconstruct(body, head_open, head_closed, base_open, base_closed,
                hand, left, right, original, cv2, np):
    """Transfer exposed hair to lock sprites; inpaint only hidden counterparts."""
    if any(a.shape != (H,W,4) for a in (
            body,head_open,head_closed,hand,left,right,original)):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_CANVAS_INVALID")
    # Input head here is the entire head, before removing either side-lock.
    if np.any(head_open[:,:,3]!=head_closed[:,:,3]):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_BLINK_ALPHA_UNSAFE")
    if np.any((base_open[:,:,3]>0) & (
            (left[:,:,3]>0) | (right[:,:,3]>0))):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_DUPLICATED_VISIBLE_LOCKS")
    if np.any(base_open[:,:,3]!=base_closed[:,:,3]):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_BASE_BLINK_ALPHA_UNSAFE")
    hair_alpha=(left[:,:,3]>0)|(right[:,:,3]>0)
    # Save original masks for QA: detached original visible colors must not change.
    pre_left=left.copy()
    pre_right=right.copy()
    fragment=pink_shoulder_mask(body,head_open,hand,left,right,cv2,np)
    # Every moved pixel is from the source art (not from reconstructed body).
    if np.any(np.any(body[:,:,:3][fragment]!=original[:,:,:3][fragment],axis=1)):
        raise VideoForgeError("RIG_HAIR_FRAGMENT_SOURCE_RGB_DIFFERENT")
    if np.any(body[:,:,3][fragment]!=original[:,:,3][fragment]):
        raise VideoForgeError("RIG_HAIR_FRAGMENT_SOURCE_ALPHA_DIFFERENT")
    y,x=np.indices((H,W))
    new_left=left.copy()
    new_right=right.copy()
    left_fragment=fragment&(x<500)
    right_fragment=fragment&(x>=500)
    new_left[left_fragment]=original[left_fragment]
    new_right[right_fragment]=original[right_fragment]
    if int(left_fragment.sum())<60 or int(right_fragment.sum())<300:
        raise VideoForgeError("RIG_HAIR_SHOULDER_FRAGMENT_REGION_UNSAFE")
    # The original head/hair line is preserved outside the detachable area.
    # Only concealed pixels are synthesized, using the same original head
    # as the inpainting context. No prior synthetic character is introduced.
    inpaint_source=head_open.copy()
    inpaint_source[:,:,:3][hair_alpha]=0
    rgb=cv2.cvtColor(inpaint_source[:,:,:3],cv2.COLOR_RGB2BGR)
    repaired=cv2.inpaint(rgb,hair_alpha.astype(np.uint8)*255,7,
                         cv2.INPAINT_TELEA)
    repaired=cv2.cvtColor(repaired,cv2.COLOR_BGR2RGB)
    new_base=base_open.copy()
    new_base[:,:,:3][hair_alpha]=repaired[hair_alpha]
    # Source artwork peaks at alpha=254 rather than 255. We use every
    # fully opaque source pixel, PLUS a narrow 7px inward edge band where
    # source alpha is 253. This fills cracks revealed by independent hair
    # movement without exposing the hidden art across the entire face.
    # An external or large inpainted patch is NOT authorized by this mask.
    source_max_alpha=int(head_open[:,:,3].max())
    if source_max_alpha<250:
        raise VideoForgeError("RIG_HAIR_UNDERLAY_SOURCE_OPACITY_UNSAFE")
    distance=cv2.distanceTransform(hair_alpha.astype(np.uint8),
                                    cv2.DIST_L2,3)
    source_alpha=head_open[:,:,3]
    opaque_core=hair_alpha & (source_alpha==source_max_alpha)
    near_edge=hair_alpha & (source_alpha==source_max_alpha-1) & (distance<=7)
    source_reconstructed=opaque_core|near_edge
    actual_underlay_pixels=int(np.count_nonzero(source_reconstructed))
    if actual_underlay_pixels<10000 or int(np.count_nonzero(near_edge))<1000:
        raise VideoForgeError("RIG_HAIR_UNDERLAY_NO_VISIBLE_EDGE_RECONSTRUCTION")
    new_base[:,:,3][hair_alpha]=np.where(
        source_reconstructed[hair_alpha],source_alpha[hair_alpha],0).astype(np.uint8)
    new_closed=base_closed.copy()
    new_closed[:,:,:3][hair_alpha]=repaired[hair_alpha]
    new_closed[:,:,3][hair_alpha]=new_base[:,:,3][hair_alpha]
    # Protect the original approved blink and make both head variants identical
    # outside the eyes, irrespective of new underlay.
    eye_change_before=np.any(head_open[:,:,:3]!=head_closed[:,:,:3],axis=2)
    eye_change_after=np.any(new_base[:,:,:3]!=new_closed[:,:,:3],axis=2)
    if not np.array_equal(eye_change_before,eye_change_after):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_BLINK_CHANGED")
    # Restore shoulder cloth UNDER relocated fragments with local original
    # colors. No part of the visible cloth outside the mask may change.
    torso=body.copy()
    torso_inpaint=cv2.inpaint(cv2.cvtColor(body[:,:,:3],cv2.COLOR_RGB2BGR),
                              fragment.astype(np.uint8)*255,3,
                              cv2.INPAINT_TELEA)
    torso[:,:,:3][fragment]=cv2.cvtColor(
        torso_inpaint,cv2.COLOR_BGR2RGB)[fragment]
    if np.any(torso[:,:,3]!=body[:,:,3]):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_TORSO_ALPHA_CHANGED")
    if np.any(torso[:,:,:3][~fragment]!=body[:,:,:3][~fragment]):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_EXPOSED_CLOTH_REPAINTED")
    if (np.any(new_left[:,:,:3][pre_left[:,:,3]>0]!=
               pre_left[:,:,:3][pre_left[:,:,3]>0]) or
        np.any(new_right[:,:,:3][pre_right[:,:,3]>0]!=
               pre_right[:,:,:3][pre_right[:,:,3]>0])):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_APPROVED_COLOR_CHANGED")
    return {
        "body":torso,"head-open":new_base,"head-closed":new_closed,
        "hair-left":new_left,"hair-right":new_right,"hand":hand,
        "fragment_pixels":int(fragment.sum()),
        "fragment_left":int(left_fragment.sum()),
        "fragment_right":int(right_fragment.sum()),
        "hair_mask_pixels":int(hair_alpha.sum()),
        "underlay_pixels":actual_underlay_pixels,
        "source_max_alpha":source_max_alpha,
        "edge_band_width_pixels":7,
        "edge_band_source_alpha":source_max_alpha-1,
        "edge_band_underlay_pixels":int(np.count_nonzero(near_edge)),
        "original_visible_pixels_changed_outside_repaired_areas":0,
        "approved_blink_preserved":True,
    }


def _stress_look(body,head,hand,left,right,rotation,cv2,np):
    result=rgba_over(body,head,np)
    for image,pivot in ((left,(345,1280)),(right,(675,1280))):
        matrix=cv2.getRotationMatrix2D(pivot,rotation,1)
        rotated=cv2.warpAffine(image,matrix,(W,H),
                               flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_CONSTANT,
                               borderValue=(0,0,0,0))
        result=rgba_over(result,rotated,np)
    return rgba_over(result,hand,np)


def _checker(image,np):
    bg=np.full((H,W,3),[35,39,52],np.float32)
    alpha=image[:,:,3:4].astype(np.float32)/255.0
    return np.clip(image[:,:,:3].astype(np.float32)*alpha+
                   bg*(1-alpha),0,255).astype(np.uint8)


def produce(original_dir:Path,corrected_dir:Path,hair_dir:Path,dest:Path)->dict:
    enforce_animation_manual()
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise VideoForgeError("RIG_HAIR_UNDERLAY_PINNED_OPENCV_REQUIRED") from exc
    source=unique(original_dir,"character-main.png")
    if sha(source)!=SOURCE_SHA:
        raise VideoForgeError("RIG_HAIR_UNDERLAY_SOURCE_SHA_INVALID")
    correct=json.loads(unique(corrected_dir,"qa.json").read_text(encoding="utf8"))
    hairqa=json.loads(unique(hair_dir,"qa.json").read_text(encoding="utf8"))
    if (correct.get("source_original_sha256")!=SOURCE_SHA or
        correct.get("rig_operational") is not False or
        hairqa.get("source_original_sha256")!=SOURCE_SHA or
        hairqa.get("head_hair_disjoint_neutral_rgb_alpha_exact") is not True or
        hairqa.get("human_visual_approval") is not False or
        hairqa.get("rig_operational") is not False):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_INPUT_QA_REJECTED")
    def from_verified(folder,qa,name):
        p=unique(folder,name)
        if qa.get("files",{}).get(name)!=sha(p):
            raise VideoForgeError("RIG_HAIR_UNDERLAY_SHA_MISMATCH_"+name)
        return read_rgba(p,cv2,np)
    original=read_rgba(source,cv2,np)
    head_open=_full(from_verified(corrected_dir,correct,
                      "head-open-without-hand-candidate.png"),
                    correct["head_bbox_original_canvas"],np)
    head_closed=_full(from_verified(corrected_dir,correct,
                      "head-closed-without-hand-candidate.png"),
                    correct["head_bbox_original_canvas"],np)
    base_open=from_verified(hair_dir,hairqa,
                           "head-open-without-side-locks-draft.png")
    base_closed=from_verified(hair_dir,hairqa,
                             "head-closed-without-side-locks-draft.png")
    left=from_verified(hair_dir,hairqa,"hair-left-side-tip-draft.png")
    right=from_verified(hair_dir,hairqa,"hair-right-side-tip-draft.png")
    body=_full(from_verified(corrected_dir,correct,
                "body-visible-restored-candidate.png"),
               [285,1407,454,129],np)
    hand=_full(from_verified(corrected_dir,correct,
                "hand-foreground-candidate.png"),
               correct["hand_bbox_original_canvas"],np)
    if np.any((base_open[:,:,3]>0)&(
            (left[:,:,3]>0)|(right[:,:,3]>0))):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_OVERLAPPING_SOURCE_LOCKS")
    result=reconstruct(body,head_open,head_closed,base_open,base_closed,
                       hand,left,right,original,cv2,np)
    original_pose=rgba_over(rgba_over(body,head_open,np),hand,np)
    rebuilt=rgba_over(result["body"],result["head-open"],np)
    rebuilt=rgba_over(rebuilt,result["hair-left"],np)
    rebuilt=rgba_over(rebuilt,result["hair-right"],np)
    rebuilt=rgba_over(rebuilt,hand,np)
    valid=original_pose[:,:,3]>0
    err=np.mean(np.abs(original_pose[:,:,:3].astype(np.int16)-
                       rebuilt[:,:,:3].astype(np.int16)),axis=2)
    alpha_diff=np.abs(original_pose[:,:,3].astype(np.int16)-
                      rebuilt[:,:,3].astype(np.int16))
    err_mean=round(float(err[valid].mean()),5)
    gt20=int(np.count_nonzero(valid&(err>20)))
    changed_alpha=int(np.count_nonzero(valid&(alpha_diff>3)))
    if err_mean>0.25 or gt20>0 or changed_alpha>0:
        raise VideoForgeError("RIG_HAIR_UNDERLAY_NEUTRAL_QA_REJECTED_"+str(
            (err_mean,gt20,changed_alpha)))
    if dest.exists():
        raise VideoForgeError("RIG_HAIR_UNDERLAY_OUTPUT_EXISTS")
    dest.mkdir(parents=True)
    names={
        "body-no-hair-residue-draft.png":"body",
        "head-open-with-side-hair-underlay-draft.png":"head-open",
        "head-closed-with-side-hair-underlay-draft.png":"head-closed",
        "hair-left-with-original-shoulder-fragment-draft.png":"hair-left",
        "hair-right-with-original-shoulder-fragment-draft.png":"hair-right",
    }
    for name,key in names.items():
        write(dest/name,result[key],cv2)
    strips=[]
    missing={}
    original_opaque=original_pose[:,:,3]>200
    for angle in (-2,0,2):
        candidate=_stress_look(result["body"],result["head-open"],hand,
                                result["hair-left"],result["hair-right"],
                                angle,cv2,np)
        # A changing silhouette is natural at the OUTER boundary. Measure
        # this strictly as a diagnostic, not an animation acceptance score.
        interior=(slice(1320,1520),slice(360,680))
        holes=original_opaque & (candidate[:,:,3]<140)
        missing[str(angle)]=int(np.count_nonzero(holes[interior]))
        strips.append(_checker(candidate,np)[1190:1536,205:805])
    sheet=np.concatenate(strips,axis=1)
    if not cv2.imwrite(str(dest/"side-hair-underlay-motion-stress.jpg"),
                       cv2.cvtColor(sheet,cv2.COLOR_RGB2BGR)):
        raise VideoForgeError("RIG_HAIR_UNDERLAY_CONTACT_SHEET_SAVE_FAILED")
    diagnostic={
        "schema":"videoforge/rig-three-anya-hair-underlay-draft/v1",
        "channel":"otaku-br","video_id":"spy-x-family-familia-de-mentira",
        "scene":"cena-01","reference_original_sha256":SOURCE_SHA,
        "previous_hair_artifact_run":43593183590,
        "previous_torso_artifact_run":43591918632,
        "method":"same_source_OpenCV_Telea_inpainting_plus_original_pixel_transfer",
        "new_image_calls":0,
        "side_hair_reconstructed_underlay_pixels":result["underlay_pixels"],
        "hair_mask_pixel_count":result["hair_mask_pixels"],
        "source_opaque_alpha_plateau":result["source_max_alpha"],
        "actually_opaque_underlay_pixel_count":result["underlay_pixels"],
        "near_opaque_edge_band_pixels":result["edge_band_underlay_pixels"],
        "edge_band_width_px":result["edge_band_width_pixels"],
        "stranded_shoulder_hair_pixels_reparented":result["fragment_pixels"],
        "left_fragment_pixels":result["fragment_left"],
        "right_fragment_pixels":result["fragment_right"],
        "neutral_rgba_composition_mean_rgb_delta":err_mean,
        "neutral_pixels_with_rgb_error_gt20":gt20,
        "neutral_pixels_with_alpha_error_gt3":changed_alpha,
        "approved_blink_preserved":result["approved_blink_preserved"],
        "rotation_stress_missing_alpha_pixels_roi":missing,
        "render_engine_for_stress":"OpenCV affine DIAGNOSTIC ONLY",
        "required_next_checks":[
            "independent deformation on ThreeCanvas 7x9 with roots fixed",
            "inspect hair/face and neck seams at frames 0,30,74,76,173,175",
            "compare hair silhouettes and antialiasing on bright and dark backgrounds",
            "visual human review of reconstituted hidden hair and collar",
        ],
        "human_visual_approval":False,
        "real_threecanvas_render_passed":False,
        "rig_operational":False,"video_official":False,"youtube_uploaded":False,
        "files":{p.name:sha(p) for p in dest.glob("*.png")},
    }
    (dest/"qa.json").write_text(json.dumps(diagnostic,ensure_ascii=False,
                                          indent=2)+"\n",encoding="utf8")
    print("RIG_THREE_ANYA_HAIR_UNDERLAY_DRAFT",json.dumps(diagnostic))
    return diagnostic


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original",required=True,type=Path)
    ap.add_argument("--corrected",required=True,type=Path)
    ap.add_argument("--hair",required=True,type=Path)
    ap.add_argument("--dest",required=True,type=Path)
    args=ap.parse_args()
    try:
        produce(args.original,args.corrected,args.hair,args.dest)
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError) as exc:
        print("RIG_THREE_ANYA_HAIR_UNDERLAY_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
