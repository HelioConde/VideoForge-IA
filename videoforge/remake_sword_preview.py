"""Fail-closed real-asset C01-P02 sword preview in ThreeCanvas/Remotion.

The package must contain a SAME-SHOT scene mother, provenance JSON and
independent full-canvas RGBA hand/sheath/blade plus an opaque reconstructed
underlay. No image API calls. A technical preview is NEVER an approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

from .cinematic_direction import load_active_remake_plan
from .remake_autopilot import ROOT,EPISODE,verified_asset
from .scene_layers import png_info
from .errors import VideoForgeError

CH="alchemy-lab"
VID="mmorpg-conquiste-a-princesa-ep01"
SHOT="C01-P02"
PARTS=("underlay","sheath","blade","hand")
W,H=1024,1536
SCHEMA="videoforge/remake-c01-p02-layer-bundle/v1"
OUT_SCHEMA="videoforge/remake-sword-technical-preview/v1"
DEST="vf-remake/c01-p02/"
ARTIFACT_PREFIX="vf-remake-c01-p02-sword-source-"

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_json(path:Path)->dict:
    if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<80000:
        raise VideoForgeError("REMAKE_SWORD_MANIFEST_MISSING_OR_UNSAFE")
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,OSError,UnicodeError) as exc:
        raise VideoForgeError("REMAKE_SWORD_MANIFEST_JSON_INVALID") from exc
    if not isinstance(data,dict):
        raise VideoForgeError("REMAKE_SWORD_MANIFEST_NOT_OBJECT")
    return data

def canonical_anchor(root:Path=ROOT)->dict:
    plan=load_active_remake_plan(CH,VID,root)
    if plan is None:
        raise VideoForgeError("REMAKE_SWORD_NO_ACTIVE_V2_PLAN")
    episode=Path(root)/EPISODE
    state=read_json(episode/"estado-atual.json")
    anchor=plan["identity_anchors"][0]
    if ((episode/"SEM-GERACAO-NOVAS-IMAGENS.lock").exists()
        or state.get("locks",{}).get("no_youtube_upload") is not True):
        raise VideoForgeError("REMAKE_SWORD_POLICY_NOT_ACTIVE")
    if (anchor.get("id")!="character-bible" or
        anchor.get("human_approved") is not True or
        anchor.get("status")!="approved" or
        not verified_asset(episode,anchor.get("path"),anchor.get("sha256"))):
        raise VideoForgeError("REMAKE_SWORD_V2_ANCHOR_NOT_APPROVED_OR_VERIFIED")
    return anchor

def preflight(root:Path=ROOT)->dict:
    plan=load_active_remake_plan(CH,VID,root)
    if plan is None:
        raise VideoForgeError("REMAKE_SWORD_ACTIVE_PLAN_MISSING")
    shot=next((x for x in plan["shots"] if x.get("shot_id")==SHOT),None)
    if shot is None or shot.get("frame_start")!=60 or shot.get("frame_end_exclusive")!=150:
        raise VideoForgeError("REMAKE_SWORD_SHOT_TIMELINE_MISMATCH")
    try:
        canonical_anchor(root)
        blocker="same_shot_rgba_bundle_and_neutral_qa_required"
    except VideoForgeError as exc:
        blocker=str(exc)
    return {
        "schema":"videoforge/remake-sword-preflight/v1",
        "channel":CH,"video_id":VID,"shot_id":SHOT,"global_frames":[60,150],
        "shot_duration_frames":90,"required_files":[
            "sword-bundle.json","scene-mother.png","scene-mother.production.json",
            *[part+".png" for part in PARTS]],
        "technical_preview_workflow":"remake-sword-preview.yml",
        "blocked_reason":blocker,
        "ready_for_render":False,
        "images_generated":0,"api_calls":0,
        "official_video_approved":False,"youtube_uploaded":False,
    }

def validate_package(package:Path,source_run_id:int,root:Path=ROOT)->dict:
    """Strong physical + contextual verification, before any Remotion render."""
    if (package.is_symlink() or not package.is_dir()
        or not isinstance(source_run_id,int) or source_run_id<=0):
        raise VideoForgeError("REMAKE_SWORD_SOURCE_ARTIFACT_REQUIRED")
    anchor=canonical_anchor(root)
    base=Path(root)/EPISODE
    plan=load_active_remake_plan(CH,VID,root)
    shot=next((s for s in plan["shots"] if s["shot_id"]==SHOT),None)
    if (shot is None or shot["frame_start"]!=60 or shot["frame_end_exclusive"]!=150
        or shot["cast"]!=["carrasco"] or shot["focus"]!="espada"):
        raise VideoForgeError("REMAKE_SWORD_SHOT_CONTRACT_MISMATCH")
    manifest=read_json(package/"sword-bundle.json")
    if (manifest.get("schema")!=SCHEMA or manifest.get("channel")!=CH
        or manifest.get("video_id")!=VID or manifest.get("shot_id")!=SHOT
        or type(manifest.get("source_run_id")) is not int
        or manifest["source_run_id"]!=source_run_id
        or manifest.get("source_artifact")!=ARTIFACT_PREFIX+str(source_run_id)
        or manifest.get("anchor_sha256")!=anchor["sha256"]
        or manifest.get("human_visual_approved") is not False
        or manifest.get("official_video_approved") is not False
        or manifest.get("youtube_uploaded") is not False):
        raise VideoForgeError("REMAKE_SWORD_BUNDLE_ORIGIN_OR_APPROVAL_INVALID")
    files={"scene-mother":"scene-mother.png",**{p:p+".png" for p in PARTS}}
    hashes=manifest.get("sha256",{})
    if not isinstance(hashes,dict) or set(hashes)!=set(files):
        raise VideoForgeError("REMAKE_SWORD_BUNDLE_HASH_LIST_INVALID")
    for name,file in files.items():
        src=package/file
        expected=hashes.get(name)
        if (src.is_symlink() or not src.is_file() or src.stat().st_size>24_000_000
            or not isinstance(expected,str) or len(expected)!=64
            or sha(src)!=expected):
            raise VideoForgeError("REMAKE_SWORD_SOURCE_SHA_MISMATCH:"+name)
        info=png_info(src.read_bytes(),require_alpha={
            "scene-mother":False,"underlay":False,
            "sheath":True,"blade":True,"hand":True}[name],
            min_visible_fraction=.0002)
        if (info["width"],info["height"])!=(W,H):
            raise VideoForgeError("REMAKE_SWORD_SOURCE_CANVAS_MISMATCH:"+name)
    source=read_json(package/"scene-mother.production.json")
    if (source.get("schema")!="videoforge/production-scene/v1"
        or source.get("channel")!=CH or source.get("video_id")!=VID
        or source.get("number")!=1 or source.get("scene")!="C01"
        or source.get("shot_id")!=SHOT or source.get("shot_specific") is not True
        or source.get("reference_sha256")!=anchor["sha256"]
        or source.get("sha256")!=hashes["scene-mother"]
        or source.get("technical_qa")!="valid_png_opaque"
        or source.get("youtube_uploaded") is not False):
        raise VideoForgeError("REMAKE_SWORD_MOTHER_PROVENANCE_INVALID")
    draw=manifest.get("draw")
    if (not isinstance(draw,dict) or set(draw)!={"beginFrame","finishFrame",
        "travelPx","axisDeg","handFollow","handRotationDeg"}):
        raise VideoForgeError("REMAKE_SWORD_DRAW_KEYS_INVALID")
    for key in draw:
        if type(draw[key]) not in (int,float) or not math.isfinite(draw[key]):
            raise VideoForgeError("REMAKE_SWORD_DRAW_VALUES_INVALID")
    if (type(draw["beginFrame"]) is not int or type(draw["finishFrame"]) is not int
        or not 0<=draw["beginFrame"]<draw["finishFrame"]-2<=87
        or not 1<=draw["travelPx"]<=240 or abs(draw["axisDeg"])>180
        or not 0<=draw["handFollow"]<=1
        or abs(draw["handRotationDeg"])>8):
        raise VideoForgeError("REMAKE_SWORD_DRAW_MOTION_LIMITS_INVALID")
    pivot=manifest.get("wristPivot")
    if (not isinstance(pivot,list) or len(pivot)!=2
        or any(type(v) not in (float,int) or not math.isfinite(v) for v in pivot)
        or not 0<=pivot[0]<=W or not 0<=pivot[1]<=H):
        raise VideoForgeError("REMAKE_SWORD_WRIST_PIVOT_INVALID")
    try:
        from PIL import Image,ImageChops,ImageStat
    except ImportError as exc:
        raise VideoForgeError("REMAKE_SWORD_RECOMPOSITION_REQUIRES_PILLOW") from exc
    # Distinct rendered layers; source artifacts are never considered human-approved.
    try:
        with Image.open(package/"scene-mother.png") as im:
            mother=im.convert("RGB")
        with Image.open(package/"underlay.png") as im:
            neutral=im.convert("RGBA")
        boxes={}
        for part in PARTS[1:]:
            with Image.open(package/(part+".png")) as im:
                rgba=im.convert("RGBA")
            bounds=rgba.getchannel("A").getbbox()
            if bounds is None:
                raise VideoForgeError("REMAKE_SWORD_EMPTY_MASK:"+part)
            boxes[part]=bounds
            neutral.alpha_composite(rgba)
        diff=ImageChops.difference(mother,neutral.convert("RGB"))
        stat=ImageStat.Stat(diff)
        mae=round(sum(stat.mean)/3,5)
        # Test a crop of hand mask: wrist pivot must touch actual pixel geometry.
        x0,y0,x1,y1=boxes["hand"]
        if not (x0-35<=pivot[0]<=x1+35 and y0-35<=pivot[1]<=y1+35):
            raise VideoForgeError("REMAKE_SWORD_WRIST_OUTSIDE_HAND_GEOMETRY")
        # Prevent blade going outside mother canvas; otherwise disjoint cut-outs.
        x0,y0,x1,y1=boxes["blade"]
        movement=draw["travelPx"]
        angle=math.radians(draw["axisDeg"])
        dx,dy=movement*math.cos(angle),movement*math.sin(angle)
        if min(x0,x0+dx)<-12 or max(x1,x1+dx)>W+12 or min(y0,y0+dy)<-12 or max(y1,y1+dy)>H+12:
            raise VideoForgeError("REMAKE_SWORD_BLADE_EXITING_FRAME")
        if mae>.5:
            raise VideoForgeError("REMAKE_SWORD_NEUTRAL_RECOMPOSITION_FAILED")
    except (OSError,ValueError) as exc:
        raise VideoForgeError("REMAKE_SWORD_RASTER_QA_FAILED") from exc
    return {"manifest":manifest,"hashes":hashes,
        "neutral_mae_rgb":mae,
        "neutral_mae_max":.5,
        "source_run_id":source_run_id,
        "anchor_sha256":anchor["sha256"],
        "source_artifact":manifest["source_artifact"],
        "human_visual_approved":False,
        "official_video_approved":False,
        "qa_status":"TECHNICAL_NEUTRAL_OK_HUMAN_REVIEW_PENDING",
    }

def prepare(package:Path,source_run_id:int,output:Path,public:Path,root:Path=ROOT)->dict:
    result=validate_package(package,source_run_id,root)
    output.mkdir(parents=True,exist_ok=True)
    public.mkdir(parents=True,exist_ok=True)
    if any(public.iterdir()):
        raise VideoForgeError("REMAKE_SWORD_PUBLIC_DIR_ALREADY_IN_USE")
    for part in PARTS:
        shutil.copyfile(package/(part+".png"),public/(part+".png"))
    layers={part:{
        "id":part,"file":DEST+part+".png","bbox":[0,0,W,H],
        "sha256":result["hashes"][part],"z":i*10,
    } for i,part in enumerate(PARTS)}
    props={"schema":OUT_SCHEMA,"shotId":SHOT,"durationFrames":90,
        "sourceRealArtworkVerified":True,"officialVideoApproved":False,
        "youtubeUploaded":False,
        "rig":{
            "schema":"videoforge/remake-sword-rig/v1",
            "shotId":SHOT,"canvas":{"width":W,"height":H},
            "motherSha256":result["hashes"]["scene-mother"],
            "anchorSha256":result["anchor_sha256"],
            "sourceRunId":source_run_id,"technicalDraftOnly":True,
            "technicalAssetsVerified":True,
            "neutralRoundtripQaPassed":True,
            "humanVisualReview":False,"youtubeUploaded":False,
            "wristPivot":result["manifest"]["wristPivot"],
            "draw":result["manifest"]["draw"],
            "layers":layers,
        },
    }
    (output/"props.json").write_text(json.dumps(props,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report={k:v for k,v in result.items() if k!="manifest"}
    report.update({"schema":"videoforge/remake-sword-stage-qa/v1",
        "render_ready":True,"renderer":"remotion-threecanvas",
        "technical_draft_only":True,"youtube_uploaded":False,
        "source_image_count":5,"generated_images":0,"api_calls":0})
    (output/"stage.qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["preflight","prepare"])
    parser.add_argument("--package",type=Path)
    parser.add_argument("--source-run-id",type=int,default=0)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--public",type=Path)
    args=parser.parse_args()
    try:
        if args.action=="preflight":
            report=preflight()
        else:
            if not args.package or not args.output or not args.public:
                raise VideoForgeError("REMAKE_SWORD_INPUTS_REQUIRED")
            report=prepare(args.package,args.source_run_id,args.output,args.public)
        print("REMAKE_C01_P02_"+args.action.upper(),json.dumps(report,ensure_ascii=False))
        return 0
    except (VideoForgeError,OSError,ValueError) as exc:
        print("REMAKE_C01_P02_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
