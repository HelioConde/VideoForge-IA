"""Split Anya's real pointing hand from her head, without new image calls.

PREVIEW CANDIDATE only: hand/skin/sleeve pixels come verbatim from the
original source. Only pixels previously occluded by that hand may be
reconstructed, using the prior same-source AI head candidate. Both open and
closed head variants share the identical new alpha geometry. Strict QA and
human approval are still required before the real Three rig can run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from .animation_manual import enforce_animation_manual
from .rig_three_art import load_plan,check_source
from .errors import VideoForgeError


def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_rgba(path:Path,cv2,np):
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("RIG_HAND_FILE_MISSING")
    a=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
    if a is None or a.dtype!=np.uint8 or a.ndim!=3 or a.shape[2]!=4:
        raise VideoForgeError("RIG_HAND_EXPECTS_RGBA_PNG")
    return cv2.cvtColor(a,cv2.COLOR_BGRA2RGBA)


def write(path:Path,data,cv2):
    if path.exists():
        raise VideoForgeError("RIG_HAND_NO_OVERWRITE")
    if not cv2.imwrite(str(path),cv2.cvtColor(data,cv2.COLOR_RGBA2BGRA)):
        raise VideoForgeError("RIG_HAND_SAVE_FAILED")


def unique(folder:Path,name:str)->Path:
    found=list(folder.rglob(name))
    if len(found)!=1:raise VideoForgeError("RIG_HAND_UNIQUE_ASSET_REQUIRED_"+name)
    return found[0]



def repair_body_and_partition(original, iso, head, hand, body, np):
    """Restore only EXPOSED source pixels; retain hidden body underlay.

    The first isolation covered the head but omitted part of Anya's uniform.
    Do not erase those pixels or leave them in 'other characters'. The
    AI-edited body is used exclusively as an occluded reconstruction.
    """
    if any(a.shape != original.shape for a in (iso, head, hand, body)):
        raise VideoForgeError("RIG_HAND_ROUNDTRIP_DIMENSIONS_INVALID")
    if np.any((head[:, :, 3] > 0) & (iso[:, :, 3] == 0)):
        raise VideoForgeError("RIG_HAND_FOREIGN_PIXELS_IN_HEAD")
    exposed = (head[:, :, 3] == 0) & (hand[:, :, 3] == 0) & (body[:, :, 3] > 0)
    restored = body.copy()
    restored[exposed] = original[exposed]
    # Add the torso pixels missing from the earlier head-heavy isolation.
    anya_mask = (iso[:, :, 3] > 0) | (
        (body[:, :, 3] > 0) & (original[:, :, 3] > 0)
    )
    anya = original.copy()
    others = original.copy()
    anya[:, :, 3] = np.where(anya_mask, original[:, :, 3], 0)
    others[:, :, 3] = np.where(~anya_mask, original[:, :, 3], 0)
    if np.any(anya[:, :, 3].astype(np.int16) +
              others[:, :, 3].astype(np.int16) != original[:, :, 3]):
        raise VideoForgeError("RIG_HAND_PARTITION_NOT_LOSSLESS")
    return restored, anya, others, int(np.count_nonzero(exposed)), int(
        np.count_nonzero(anya_mask & (iso[:, :, 3] == 0)))


def rgba_over(back, front, np):
    """Straight alpha-over with no PNG or FFmpeg resampling."""
    fa = front[:, :, 3:4].astype(np.float32) / 255.0
    ba = back[:, :, 3:4].astype(np.float32) / 255.0
    a = fa + ba * (1 - fa)
    rgb = (front[:, :, :3].astype(np.float32) * fa +
           back[:, :, :3].astype(np.float32) * ba * (1 - fa))
    rgb /= np.maximum(a, 0.000001)
    out = np.empty_like(back)
    out[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[:, :, 3] = np.clip(a[:, :, 0] * 255, 0, 255).astype(np.uint8)
    return out


def roundtrip_metrics(assembled, anya, original, np):
    target = anya[:, :, 3] > 0
    source_opaque = anya[:, :, 3] > 200
    rgb_error = np.mean(np.abs(
        assembled[:, :, :3].astype(np.int16) -
        original[:, :, :3].astype(np.int16)), axis=2)
    return {
        "visible_pixels": int(np.count_nonzero(target)),
        "mean_abs_rgb_error": round(float(np.mean(rgb_error[target])), 4),
        "large_rgb_error_pixels_gt20": int(np.count_nonzero(target & (rgb_error > 20))),
        "missing_opaque_pixels": int(np.count_nonzero(
            source_opaque & (assembled[:, :, 3] < 100))),
        "stray_alpha_pixels": int(np.count_nonzero(
            (assembled[:, :, 3] > 32) & ~target)),
        "alpha_error_pixels_gt30": int(np.count_nonzero(
            target & (np.abs(assembled[:, :, 3].astype(np.int16) -
                             original[:, :, 3].astype(np.int16)) > 30))),
    }


def prepare(original_dir:Path,heads_dir:Path,iso_dir:Path,
            head_ai_dir:Path,dest:Path,channel:str,video_id:str)->dict:
    enforce_animation_manual()
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise VideoForgeError("RIG_HAND_PINNED_OPENCV_PREP_REQUIRED") from exc
    plan=load_plan(channel,video_id)
    check_source(original_dir,plan)
    original_file=original_dir/"character-main.png"
    original=read_rgba(original_file,cv2,np)
    H,W=original.shape[:2]
    if (W,H)!=(1024,1536):
        raise VideoForgeError("RIG_HAND_SOURCE_SIZE_INVALID")
    iso_p=unique(iso_dir,"anya-original-isolated.png")
    iso_qa=json.loads(unique(iso_dir,"qa.json").read_text(encoding="utf-8"))
    if (iso_qa.get("original_sha256")!=sha(original_file) or
        iso_qa.get("files",{}).get("anya-original-isolated.png")!=sha(iso_p) or
        iso_qa.get("original_partition_alpha_differences")!=0 or
        iso_qa.get("human_visual_approval") is not False):
        raise VideoForgeError("RIG_HAND_ISOLATION_SOURCE_INVALID")
    iso=read_rgba(iso_p,cv2,np)
    revised_qa=json.loads(unique(heads_dir,"qa.json").read_text(encoding="utf-8"))
    bbox=revised_qa.get("head_open_bbox")
    if (revised_qa.get("silhouette_isolation_qa")!=
            "refined_with_same_image_anya_mask_review_pending" or
        revised_qa.get("non_anya_original_pixels_in_head")!=0 or
        revised_qa.get("source_original_sha256")!=sha(original_file) or
        not isinstance(bbox,list) or len(bbox)!=4 or
        revised_qa.get("ready_for_rig") is not False):
        raise VideoForgeError("RIG_HAND_HEAD_REFINEMENT_NOT_VERIFIED")
    x,y,w,h=bbox
    head_open_crop=read_rgba(unique(heads_dir,"head-open.png"),cv2,np)
    head_closed_crop=read_rgba(unique(heads_dir,"head-closed.png"),cv2,np)
    if head_open_crop.shape!=(h,w,4) or head_closed_crop.shape!=head_open_crop.shape:
        raise VideoForgeError("RIG_HAND_HEAD_BBOX_MISMATCH")
    ai_p=unique(head_ai_dir,"head-open-candidate.png")
    ai_qa=json.loads(unique(head_ai_dir,"head-open.qa.json").read_text(encoding="utf-8"))
    if (ai_qa.get("output_sha256")!=sha(ai_p) or
        ai_qa.get("source_original_sha256")!=sha(original_file) or
        ai_qa.get("human_visual_approval") is not False):
        raise VideoForgeError("RIG_HAND_HIDDEN_UNDERLAY_NOT_FROM_SOURCE")
    ai_head=read_rgba(ai_p,cv2,np)
    if ai_head.shape!=original.shape:
        raise VideoForgeError("RIG_HAND_UNDERLAY_SIZE_INVALID")
    open_full=np.zeros_like(original)
    closed_full=np.zeros_like(original)
    open_full[y:y+h,x:x+w]=head_open_crop
    closed_full[y:y+h,x:x+w]=head_closed_crop

    # The finger/hand is a distinct connected skin component (unlike the
    # cheek). Disallow changing its source pixels. Never GrabCut a new face.
    r,g,b,a=[original[:,:,i].astype(np.float32) for i in range(4)]
    skin=(r>185)&(g>115)&(b>85)&(g/np.maximum(r,1)>.70)&(
        (r-g)<86)&(a>100)
    skin[:1300]=False
    n,labels,stats,_=cv2.connectedComponentsWithStats(skin.astype(np.uint8),8)
    index=int(labels[1430,476])
    if not (0<index<n and 5500<int(stats[index,cv2.CC_STAT_AREA])<10500):
        raise VideoForgeError("RIG_HAND_FINGER_NOT_DISCONNECTED_FROM_FACE")
    hand=cv2.dilate((labels==index).astype(np.uint8),
                     np.ones((5,5),np.uint8),iterations=1)
    hand=cv2.morphologyEx(hand,cv2.MORPH_CLOSE,
                          np.ones((5,5),np.uint8))
    # Small gold cuff and sleeve belong to the pointing arm, not the head.
    sleeve=np.array([[437,1473],[454,1493],[490,1518],[486,1535],
                     [379,1535],[385,1520],[414,1491]],np.int32)
    cv2.fillPoly(hand,[sleeve],1)
    hand=((hand>0)&(iso[:,:,3]>0))
    count=int(hand.sum())
    if not 10000<=count<=17500:
        raise VideoForgeError("RIG_HAND_MASK_UNSAFE")
    fore=original.copy()
    fore[:,:,3]=np.where(hand,original[:,:,3],0).astype(np.uint8)
    # No possible duplication: the same region is removed from the head.
    # The art drawn behind the hand was never visible in original, so the
    # prior candidate AI is used only *there*, with head alpha preserved.
    reconstruction_pixels=0
    for variant in (open_full,closed_full):
        affected=hand & (variant[:,:,3]>0)
        base=affected & (np.indices(hand.shape)[0]<1480)&(ai_head[:,:,3]>80)
        reconstruction_pixels+=int(np.count_nonzero(base))
        variant[:,:,:3][base]=ai_head[:,:,:3][base]
        # For the missing part below the collar leave body responsible.
        drop=affected & ~base
        variant[:,:,3][drop]=0
    if np.any((open_full[:,:,3]>0)&(fore[:,:,3]>0)&(hand)&(
            np.indices(hand.shape)[0]>=1480)):
        raise VideoForgeError("RIG_HAND_DUPLICATED_VISIBLE_CUFF")
    # Open/closed head variants may ONLY differ where they already differed,
    # i.e. the previously approved eyes. Under-hand pixels are common.
    delta=np.any(open_full[:,:,:3]!=closed_full[:,:,:3],axis=2)
    if int(np.count_nonzero(delta))<1000 or int(np.count_nonzero(delta))>30000:
        raise VideoForgeError("RIG_HAND_BLINK_REGION_UNEXPECTED")
    if np.any(open_full[:,:,3]!=closed_full[:,:,3]):
        raise VideoForgeError("RIG_HAND_BLINK_ALPHAS_MISMATCH")
    if dest.exists():raise VideoForgeError("RIG_HAND_OUTPUT_ALREADY_EXISTS")
    dest.mkdir(parents=True)
    yy,xx=np.where(hand)
    hb=[int(xx.min()),int(yy.min()),int(xx.max()+1-xx.min()),
        int(yy.max()+1-yy.min())]
    write(dest/"head-open-without-hand-candidate.png",
          open_full[y:y+h,x:x+w],cv2)
    write(dest/"head-closed-without-hand-candidate.png",
          closed_full[y:y+h,x:x+w],cv2)
    write(dest/"hand-foreground-candidate.png",
          fore[hb[1]:hb[1]+hb[3],hb[0]:hb[0]+hb[2]],cv2)
    # Preview the exact layers, NOT approval of their movement.
    backdrop=np.empty((H,W,3),np.float32)
    backdrop[:]=[34,38,49]
    body_files=list(heads_dir.rglob("body-no-head.png"))
    if len(body_files)!=1:raise VideoForgeError("RIG_HAND_BODY_MISSING")
    body=read_rgba(body_files[0],cv2,np)
    bx,by,bw,bh=revised_qa["body_no_head_bbox"]
    body_full=np.zeros_like(original)
    body_full[by:by+bh,bx:bx+bw]=body
    body_full, corrected_anya, corrected_others, body_restored, mask_recovered = (
        repair_body_and_partition(original,iso,open_full,fore,body_full,np))
    neutral = rgba_over(rgba_over(body_full,open_full,np),fore,np)
    metrics = roundtrip_metrics(neutral,corrected_anya,original,np)
    if (metrics["mean_abs_rgb_error"] > 0.5 or
        metrics["large_rgb_error_pixels_gt20"] > 250 or
        metrics["missing_opaque_pixels"] > 500 or
        metrics["stray_alpha_pixels"] > 0 or
        metrics["alpha_error_pixels_gt30"] > 50):
        raise VideoForgeError("RIG_HAND_NEUTRAL_ROUNDTRIP_REJECTED_"+str(metrics))
    write(dest/"body-visible-restored-candidate.png",
          body_full[by:by+bh,bx:bx+bw],cv2)
    write(dest/"anya-complete-source-isolated-candidate.png",corrected_anya,cv2)
    write(dest/"other-characters-without-anya-candidate.png",corrected_others,cv2)
    write(dest/"neutral-composition-corrected-candidate.png",neutral,cv2)
    diff=np.zeros_like(original)
    diff[:,:,:3]=np.clip(
        np.abs(neutral[:,:,:3].astype(np.int16) -
               original[:,:,:3].astype(np.int16))*3,0,255).astype(np.uint8)
    diff[:,:,3]=corrected_anya[:,:,3]
    write(dest/"neutral-diff-corrected.png",diff,cv2)
    for part in (body_full,open_full,fore):
        alpha=part[:,:,3:4].astype(np.float32)/255
        backdrop=part[:,:,:3].astype(np.float32)*alpha+backdrop*(1-alpha)
    preview=np.uint8(np.clip(backdrop,0,255))
    cv2.imwrite(str(dest/"hand-head-neutral-review.jpg"),
                cv2.cvtColor(preview,cv2.COLOR_RGB2BGR))
    result={
      "schema":"videoforge/rig-three-hand-separation-candidate/v1",
      "manual":"docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md",
      "channel":channel,"video_id":video_id,"scene":"cena-01",
      "source_original_sha256":sha(original_file),
      "isolated_anya_sha256":sha(iso_p),
      "underlay_ai_head_sha256":sha(ai_p),
      "head_bbox_original_canvas":bbox,
      "hand_bbox_original_canvas":hb,
      "hand_visible_pixels":count,
      "original_exposed_body_pixels_restored":body_restored,
      "original_anya_torso_pixels_recovered_from_other_characters":mask_recovered,
      "original_partition_alpha_differences_after_correction":0,
      "neutral_open_roundtrip_qa":metrics,
      "neutral_open_roundtrip_status":"pixel_qa_passed_visual_review_pending",
      "hair_neutral_and_motion_underlay_qa":"pending",
      "neck_and_collar_motion_qa":"pending",
      "hidden_underlay_pixels_reconstructed_in_two_frames":reconstruction_pixels,
      "finger_separate_from_face_component":True,
      "hand_foreground_original_pixels_preserved":True,
      "underlay_changed_only_where_hand_used_to_occlude":True,
      "closed_eye_original_pixels_maintained":True,
      "hair_mesh_pending_underlay":True,
      "original_face_seam_review":"pending",
      "rig_operational":False,
      "human_visual_approval":False,
      "video_official":False,
      "youtube_uploaded":False,
      "files":{p.name:sha(p) for p in dest.glob("*.png")},
    }
    (dest/"qa.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("RIG_THREE_HAND_SEPARATION_CANDIDATE_QA",
          json.dumps(result,ensure_ascii=False))
    return result


def main()->int:
    a=argparse.ArgumentParser()
    a.add_argument("--original",required=True,type=Path)
    a.add_argument("--heads",required=True,type=Path)
    a.add_argument("--isolation",required=True,type=Path)
    a.add_argument("--ai-head",required=True,type=Path)
    a.add_argument("--dest",required=True,type=Path)
    a.add_argument("--channel",default="otaku-br")
    a.add_argument("--video-id",default="spy-x-family-familia-de-mentira")
    args=a.parse_args()
    try:
        prepare(args.original,args.heads,args.isolation,
                args.ai_head,args.dest,args.channel,args.video_id)
        return 0
    except (VideoForgeError,ValueError,OSError,KeyError) as exc:
        print("RIG_THREE_HAND_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
