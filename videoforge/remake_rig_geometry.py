"""Audited REAL-mask geometry candidates for C01-P02 articulated ThreeCanvas.

Read-only inputs: a SHA-verified same-shot sword bundle and the canonical 40
shot motion direction. FFmpeg is used ONLY to decode PNGs for QA, never animate.
Output is a measured technical proposal, NOT automatic anatomical approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

from .errors import VideoForgeError
from .remake_autopilot import ROOT
from .remake_motion_directions import load_motion_directions
from .remake_sword_preview import (
    CH,VID,SHOT,PARTS,W,H,sha,validate_package,decode_rgba_for_qa,
)
from .scene_layers import png_info

SCHEMA="videoforge/remake-rig-mask-geometry/v1"
FILE_NAME="mask-geometry.qa.json"
VISUAL_PARTS=("sheath","blade","hand")
FRAMES=(0,7,72,89)


def _alpha_metrics(raw:bytes,part:str)->dict:
    if len(raw)!=W*H*4:
        raise VideoForgeError("REMAKE_RIG_GEOMETRY_PIXEL_COUNT_INVALID")
    min_x,min_y,max_x,max_y=W,H,-1,-1
    area=0
    sum_x=sum_y=0
    alpha=raw[3::4]
    for i,a in enumerate(alpha):
        if a<=127:
            continue
        x=i%W
        y=i//W
        area+=1
        sum_x+=x
        sum_y+=y
        if x<min_x:min_x=x
        if y<min_y:min_y=y
        if x>max_x:max_x=x
        if y>max_y:max_y=y
    if area<32 or max_x<0:
        raise VideoForgeError("REMAKE_RIG_MASK_TOO_SMALL_OR_EMPTY:"+part)
    return {
        "bbox_xyxy":[min_x,min_y,max_x+1,max_y+1],
        "opaque_pixel_count":area,
        "alpha_threshold":127,
        "coverage_fraction":round(area/(W*H),8),
        "centroid_px":[round(sum_x/area,3),round(sum_y/area,3)],
        "measured_from_mask_pixels":True,
        "anatomically_approved":False,
    }


def _pose_at(frame:int,draw:dict)->dict:
    if (type(frame) is not int or frame<0 or frame>=90):
        raise VideoForgeError("REMAKE_RIG_MOTION_FRAME_OUT_OF_BOUNDS")
    start,end=draw["beginFrame"],draw["finishFrame"]
    t=max(0.,min(1.,(frame-start)/(end-start)))
    smooth=t*t*(3-2*t)
    angle=math.radians(draw["axisDeg"])
    dx=draw["travelPx"]*math.cos(angle)*smooth
    dy=draw["travelPx"]*math.sin(angle)*smooth
    return {
        "local_frame":frame,"progress":round(smooth,7),
        "blade_offset_px":[round(dx,3),round(dy,3)],
        "hand_offset_px":[round(dx*draw["handFollow"],3),
                          round(dy*draw["handFollow"],3)],
        "hand_wrist_rotation_deg":round(draw["handRotationDeg"]*smooth,4),
        "source":"real_mask_and_unapproved_draft_draw",
    }


def analyze(package:Path,run_id:int,root:Path=ROOT)->dict:
    result=validate_package(package,run_id,root)  # strong provenance, SHA, alpha and neutral QA
    bundle=result["manifest"]
    cue=next((s for s in load_motion_directions(root)["shots"]
              if s["shot_id"]==SHOT),None)
    if cue is None or cue["frames"]["local_duration"]!=90:
        raise VideoForgeError("REMAKE_RIG_C01_P02_MOTION_SOURCE_INVALID")
    stages=cue["stages"]
    timings=[p["local_frame"] for p in stages]
    if timings!=list(FRAMES):
        raise VideoForgeError("REMAKE_RIG_CUE_FRAMES_CHANGED")
    draw=bundle["draw"]
    if (draw["beginFrame"]!=7 or draw["finishFrame"]!=72
        or list(PARTS)!=["underlay","sheath","blade","hand"]):
        raise VideoForgeError("REMAKE_RIG_DRAW_AND_DIRECTED_PHASES_DIVERGED")
    masks={}
    for part in VISUAL_PARTS:
        png=package/(part+".png")
        if png.is_symlink() or not png.is_file():
            raise VideoForgeError("REMAKE_RIG_MASK_MISSING:"+part)
        info=png_info(png.read_bytes(),require_alpha=True,
                      min_visible_fraction=.0002)
        if (info["width"],info["height"],info["color_type"])!=(W,H,6):
            raise VideoForgeError("REMAKE_RIG_SOURCE_NOT_NATIVE_RGBA:"+part)
        masks[part]={
          "sha256":sha(png),
          **_alpha_metrics(decode_rgba_for_qa(png),part),
        }
    underlay=package/"underlay.png"
    underlay_info=png_info(underlay.read_bytes(),require_alpha=False)
    if (underlay_info["width"],underlay_info["height"],
        underlay_info["color_type"])!=(W,H,2):
        raise VideoForgeError("REMAKE_RIG_UNDERLAY_NOT_OPAQUE_RGB")
    hand=masks["hand"]["bbox_xyxy"]
    pivot=bundle["wristPivot"]
    if not (hand[0]-35<=pivot[0]<=hand[2]+35
            and hand[1]-35<=pivot[1]<=hand[3]+35):
        raise VideoForgeError("REMAKE_RIG_PIVOT_OFF_HAND_MASK")
    fingerprint=hashlib.sha256(json.dumps(
        cue,sort_keys=True,separators=(",",":"),ensure_ascii=False
    ).encode("utf-8")).hexdigest()
    return {
      "schema":SCHEMA,
      "shot_id":SHOT,"channel":CH,"video_id":VID,
      "motion_direction_sha256":fingerprint,
      "source_run_id":run_id,
      "source_artifact":bundle["source_artifact"],
      "source_mother_sha256":result["hashes"]["scene-mother"],
      "canonical_anchor_sha256":result["anchor_sha256"],
      "source_canvas":{"width":W,"height":H},
      "parts":{
        "underlay":{"sha256":sha(underlay),"opaque_rgb_verified":True,
                    "human_visual_approval":False},
        **masks,
      },
      "draft_wrist_pivot_px":pivot,
      "draft_draw":draw,
      "directed_frame_poses":[_pose_at(f,draw) for f in FRAMES],
      "neutral_roundtrip_mae_rgb":result["neutral_mae_rgb"],
      "neutral_roundtrip_max":result["neutral_mae_max"],
      "technical_qa":"source_sha_alpha_bbox_and_roundtrip_verified",
      "candidate_only":True,
      "pivots_measured_from_actual_rgba":True,
      "pivot_is_heuristic_not_anatomical_approval":True,
      "human_anatomy_contact_review_required":True,
      "human_visual_approved":False,
      "rig_approved_for_official_render":False,
      "official_video_approved":False,
      "youtube_uploaded":False,
      "new_generated_images":0,
      "paid_provider_calls":0,
    }


def persist(package:Path,run_id:int,root:Path=ROOT)->dict:
    qa=analyze(package,run_id,root)
    path=Path(package)/FILE_NAME
    if path.is_symlink():
        raise VideoForgeError("REMAKE_RIG_GEOMETRY_OUTPUT_SYMLINK")
    binary=(json.dumps(qa,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    if path.exists():
        if not path.is_file() or path.read_bytes()!=binary:
            raise VideoForgeError("REMAKE_RIG_GEOMETRY_QA_ALREADY_EXISTS_DIFFERENT")
    else:
        path.write_bytes(binary)
    return qa


def verify_report(package:Path,run_id:int,root:Path=ROOT)->dict:
    """Verify the artifact's saved evidence against decoded source pixels again."""
    fresh=analyze(package,run_id,root)
    path=Path(package)/FILE_NAME
    if path.is_symlink() or not path.is_file() or not 50<path.stat().st_size<100000:
        raise VideoForgeError("REMAKE_RIG_GEOMETRY_ATTESTATION_MISSING")
    try:
        existing=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise VideoForgeError("REMAKE_RIG_GEOMETRY_ATTESTATION_INVALID") from exc
    if existing!=fresh:
        raise VideoForgeError("REMAKE_RIG_GEOMETRY_ATTESTATION_CHANGED")
    return fresh


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--package",type=Path,required=True)
    p.add_argument("--source-run-id",type=int,required=True)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument("--write",action="store_true")
    mode.add_argument("--verify-report",action="store_true")
    args=p.parse_args()
    try:
        qa=(persist if args.write else verify_report if args.verify_report
            else analyze)(args.package,args.source_run_id)
        print("REMAKE_RIG_GEOMETRY_QA",json.dumps({
          "shot_id":qa["shot_id"],
          "source_mother_sha256":qa["source_mother_sha256"],
          "parts":{k:v.get("bbox_xyxy") for k,v in qa["parts"].items()},
          "staged":args.write,"official_video_approved":False,
        }))
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError,TypeError) as exc:
        print("REMAKE_RIG_GEOMETRY_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
