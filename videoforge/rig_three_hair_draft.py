"""Deterministic SIDE-HAIR drafts and neck seam stress QA for Anya scene 01.

Creates genuine disjoint original-pixel layers, NOT an approved hair rig.
Rotation is only geometric stress inspection, never an official renderer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from .animation_manual import enforce_animation_manual
from .errors import VideoForgeError
from .rig_three_hand_split import read_rgba, unique, sha, write, rgba_over


W, H = 1024, 1536
SOURCE_SHA = "c3b21ecd072d3fbf6978f04e6cde5db5d9083e13871b475e6f8c9229a15b0b2c"


def _full(crop, box, np):
    x,y,w,h=box
    if crop.shape != (h,w,4) or not (0<=x<x+w<=W and 0<=y<y+h<=H):
        raise VideoForgeError("RIG_HAIR_INVALID_BBOX")
    out=np.zeros((H,W,4),dtype=np.uint8)
    out[y:y+h,x:x+w]=crop
    return out


def _hair_partition(head_open, head_closed, hair_seed, np):
    """Extract two lower side-locks without taking any approved eye pixel."""
    if any(a.shape != (H,W,4) for a in (head_open,head_closed,hair_seed)):
        raise VideoForgeError("RIG_HAIR_CANVAS_MISMATCH")
    if np.any(head_open[:,:,3] != head_closed[:,:,3]):
        raise VideoForgeError("RIG_HAIR_BLINK_ALPHA_CHANGED")
    y,x=np.indices((H,W))
    # Derive pixels from source hair mask, not from a fresh drawing.
    # Side-tip roots at y=1280; no center fringe or facial pixels.
    candidate=(hair_seed[:,:,3]>0)&(head_open[:,:,3]>0)&(y>=1280)&(y<1505)
    left=candidate&(x<(320+0.40*(y-1100)))
    right=candidate&(x>(720-0.40*(y-1100)))
    if np.any(left&right):
        raise VideoForgeError("RIG_HAIR_LOCKS_OVERLAP")
    counts=(int(left.sum()),int(right.sum()))
    if not (18000<=counts[0]<=45000 and 18000<=counts[1]<=45000):
        raise VideoForgeError("RIG_HAIR_UNSAFE_SIDE_LOCK_AREA_"+str(counts))
    eyes=np.any(head_open[:,:,:3] != head_closed[:,:,:3],axis=2)
    if np.any(eyes & (left|right)):
        raise VideoForgeError("RIG_HAIR_CUT_APPROVED_BLINK")
    locks=[]
    for mask in (left,right):
        out=head_open.copy()
        out[:,:,3] = np.where(mask,head_open[:,:,3],0).astype(np.uint8)
        locks.append(out)
    base_open=head_open.copy()
    base_closed=head_closed.copy()
    for a in (base_open,base_closed):
        a[:,:,3][left|right]=0
    if np.any((base_open[:,:,3]>0)&
              ((locks[0][:,:,3]>0)|(locks[1][:,:,3]>0))):
        raise VideoForgeError("RIG_HAIR_HEAD_DUPLICATED")
    # Since these are disjoint alpha partitions, they reconstruct the source
    # in neutral pose EXACTLY. This does not validate motion or underlays.
    reassembled=rgba_over(rgba_over(base_open,locks[0],np),locks[1],np)
    if not np.array_equal(reassembled[:,:,3],head_open[:,:,3]):
        raise VideoForgeError("RIG_HAIR_NEUTRAL_ALPHA_MISMATCH")
    visible=head_open[:,:,3]>0
    if np.any(reassembled[:,:,:3][visible]!=head_open[:,:,:3][visible]):
        raise VideoForgeError("RIG_HAIR_NEUTRAL_RGB_MISMATCH")
    return base_open,base_closed,locks,counts


def _stress_frame(body, head, hand, rotation, cv2, np):
    # Diagnostics only, NOT ThreeCanvas, mesh or motion approval.
    m=cv2.getRotationMatrix2D((515,1429),rotation,1.0)
    rotated=cv2.warpAffine(head,m,(W,H),flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    return rgba_over(rgba_over(body,rotated,np),hand,np)


def _preview_rgba(a, np):
    bg=np.full((H,W,3),[34,38,49],np.uint8).astype(np.float32)
    alpha=a[:,:,3:4].astype(np.float32)/255
    return np.clip(a[:,:,:3]*alpha+bg*(1-alpha),0,255).astype(np.uint8)


def produce(original_dir, correct_dir, isolation_dir, dest):
    enforce_animation_manual()
    try:
        import numpy as np
        import cv2
    except ImportError as exc:
        raise VideoForgeError("RIG_HAIR_PINNED_OPENCV_REQUIRED") from exc
    original=unique(original_dir,"character-main.png")
    if sha(original)!=SOURCE_SHA:
        raise VideoForgeError("RIG_HAIR_ORIGINAL_SHA_MISMATCH")
    manifest=json.loads(unique(correct_dir,"qa.json").read_text(encoding="utf8"))
    isoqa=json.loads(unique(isolation_dir,"qa.json").read_text(encoding="utf8"))
    if (manifest.get("source_original_sha256")!=SOURCE_SHA or
        manifest.get("neutral_open_roundtrip_status")!="pixel_qa_passed_visual_review_pending" or
        manifest.get("rig_operational") is not False or
        isoqa.get("original_sha256")!=SOURCE_SHA or
        isoqa.get("human_visual_approval") is not False):
        raise VideoForgeError("RIG_HAIR_PREVIOUS_QA_NOT_TRUSTED")
    original_rgba=read_rgba(original,cv2,np)
    box=manifest["head_bbox_original_canvas"]
    eye_paths=[unique(correct_dir,name) for name in (
        "head-open-without-hand-candidate.png",
        "head-closed-without-hand-candidate.png")]
    for f in eye_paths:
        if manifest["files"].get(f.name)!=sha(f):
            raise VideoForgeError("RIG_HAIR_HEAD_SHA_MISMATCH")
    head_open,head_closed=[
        _full(read_rgba(f,cv2,np),box,np) for f in eye_paths]
    hair_file=unique(isolation_dir,"hair-front-mask-draft.png")
    if isoqa.get("files",{}).get(hair_file.name)!=sha(hair_file):
        raise VideoForgeError("RIG_HAIR_SEED_SHA_MISMATCH")
    hair_seed=read_rgba(hair_file,cv2,np)
    base_open,base_closed,locks,counts=_hair_partition(
        head_open,head_closed,hair_seed,np)
    bodyfile=unique(correct_dir,"body-visible-restored-candidate.png")
    handfile=unique(correct_dir,"hand-foreground-candidate.png")
    for f in (bodyfile,handfile):
        if manifest["files"].get(f.name)!=sha(f):
            raise VideoForgeError("RIG_HAIR_COMPANION_SHA_MISMATCH")
    # Torso bbox is in verified upstream candidate report, preserve source coords.
    body=read_rgba(bodyfile,cv2,np)
    # The body crop in the previous run is 454x129 at x=281,y=1407.
    # Validate this bounded reference instead of inferring from a raster edge.
    if body.shape!=(129,454,4):
        raise VideoForgeError("RIG_HAIR_BODY_BBOX_CHANGED")
    body_full=_full(body,[281,1407,454,129],np)
    hand=_full(read_rgba(handfile,cv2,np),
               manifest["hand_bbox_original_canvas"],np)
    neutral=rgba_over(rgba_over(body_full,head_open,np),hand,np)
    if dest.exists():
        raise VideoForgeError("RIG_HAIR_NO_OVERWRITE")
    dest.mkdir(parents=True)
    for name,data in (
        ("head-open-without-side-locks-draft.png",base_open),
        ("head-closed-without-side-locks-draft.png",base_closed),
        ("hair-left-side-tip-draft.png",locks[0]),
        ("hair-right-side-tip-draft.png",locks[1])):
        write(dest/name,data,cv2)
    exposures={}
    strips=[]
    roi=(slice(1360,1530),slice(365,675))
    for rot in (-2,0,2):
        state=_stress_frame(body_full,head_open,hand,rot,cv2,np)
        miss=(neutral[:,:,3]>200)&(state[:,:,3]<140)
        exposures[str(rot)]=int(np.count_nonzero(miss[roi]))
        strips.append(_preview_rgba(state,np)[925:1536,190:830])
    sheet=np.concatenate(strips,axis=1)
    cv2.imwrite(str(dest/"neck-rotation-stress-review.jpg"),
                cv2.cvtColor(sheet,cv2.COLOR_RGB2BGR))
    rgb_part=rgba_over(rgba_over(body_full,base_open,np),locks[0],np)
    rgb_part=rgba_over(rgba_over(rgb_part,locks[1],np),hand,np)
    visible=(neutral[:,:,3]>0)
    if np.any(rgb_part[:,:,3]!=neutral[:,:,3]) or np.any(
            rgb_part[:,:,:3][visible]!=neutral[:,:,:3][visible]):
        raise VideoForgeError("RIG_HAIR_FULL_NEUTRAL_PARTITION_FAILED")
    result={
        "schema":"videoforge/rig-three-anya-hair-side-draft/v1",
        "channel":"otaku-br","video_id":"spy-x-family-familia-de-mentira",
        "scene":"cena-01",
        "source_original_sha256":SOURCE_SHA,
        "source_previous_run_id":43591918632,
        "source_hair_seed_run_id":43589190537,
        "new_image_calls":0,
        "left_hair_source_pixels":counts[0],
        "right_hair_source_pixels":counts[1],
        "head_hair_disjoint_neutral_rgb_alpha_exact":True,
        "approved_blink_delta_retained":True,
        "neck_rotation_preview_pivot_original":[515,1429],
        "neck_rotation_stress_missing_alpha_pixels_roi":exposures,
        "neck_underlay_review":"pending",
        "hair_face_underlay_review":"pending",
        "hair_mesh_motion_test":"pending_ThreeCanvas",
        "compositor_note":"Affine +/-2 degrees is an inspection stress preview, NOT a Three.js render",
        "human_visual_approval":False,
        "rig_operational":False,
        "video_official":False,
        "youtube_uploaded":False,
        "files":{p.name:sha(p) for p in dest.glob("*.png")}
    }
    (dest/"qa.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("RIG_THREE_ANYA_HAIR_SIDE_DRAFT",json.dumps(result))
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--corrected",type=Path,required=True)
    p.add_argument("--isolation",type=Path,required=True)
    p.add_argument("--dest",type=Path,required=True)
    a=p.parse_args()
    try:
        produce(a.original,a.corrected,a.isolation,a.dest)
        return 0
    except (VideoForgeError,ValueError,OSError,KeyError) as exc:
        print("RIG_THREE_ANYA_HAIR_DRAFT_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
