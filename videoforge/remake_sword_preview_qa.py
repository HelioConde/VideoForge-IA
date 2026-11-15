"""C01-P02 MP4 technical QA: prove separate Three.js layers actually move."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from .errors import VideoForgeError

FPS=30
FRAMES=90
W,H=1080,1920

def cmd(args:list[str])->bytes:
    try:
        p=subprocess.run(args,check=True,capture_output=True,timeout=120)
        return p.stdout
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired,OSError) as exc:
        raise VideoForgeError("REMAKE_SWORD_MP4_MEDIA_QA_COMMAND_FAILED") from exc

def verify(output:Path)->dict:
    file=output/"c01-p02-three-sword-technical.mp4"
    props=output/"props.json"
    stage=output/"stage.qa.json"
    for x in (file,props,stage):
        if x.is_symlink() or not x.is_file() or x.stat().st_size<100:
            raise VideoForgeError("REMAKE_SWORD_MP4_OR_PROVENANCE_MISSING")
    data=json.loads(props.read_text(encoding="utf-8"))
    stage_data=json.loads(stage.read_text(encoding="utf-8"))
    if data.get("officialVideoApproved") is not False or data.get("youtubeUploaded") is not False or data.get("rig",{}).get("humanVisualReview") is not False:
        raise VideoForgeError("REMAKE_SWORD_PREVIEW_UNSAFE_PUBLISHABLE_FLAG")
    if stage_data.get("qa_status")!="TECHNICAL_NEUTRAL_OK_HUMAN_REVIEW_PENDING":
        raise VideoForgeError("REMAKE_SWORD_NEUTRAL_GATE_MISSING")
    probe=json.loads(cmd(["ffprobe","-v","error","-count_frames","-show_streams","-show_format","-of","json",str(file)]))
    streams=probe.get("streams",[])
    vids=[x for x in streams if x.get("codec_type")=="video"]
    audios=[x for x in streams if x.get("codec_type")=="audio"]
    if len(vids)!=1 or audios:
        raise VideoForgeError("REMAKE_SWORD_PREVIEW_STREAMS_INVALID")
    v=vids[0]
    if (v.get("codec_name")!="h264" or (v.get("width"),v.get("height"))!=(W,H)
        or v.get("avg_frame_rate")!="30/1"
        or int(v.get("nb_read_frames") or v.get("nb_frames") or -1)!=FRAMES
        or not 2.98<=float(probe.get("format",{}).get("duration",0))<=3.1):
        raise VideoForgeError("REMAKE_SWORD_PREVIEW_FORMAT_INVALID")
    # Compare two decoded internal frames; do NOT mistake moving camera for rig.
    # A distinct fixed/anchored sheath is verified in the actor's rig contract.
    raw=cmd(["ffmpeg","-nostdin","-v","error","-i",str(file),
        "-vf","select=eq(n\\,7)+eq(n\\,71),scale=192:342,format=rgb24",
        "-vsync","0","-an","-f","rawvideo","-pix_fmt","rgb24","pipe:1"])
    size=192*342*3
    if len(raw)!=size*2:
        raise VideoForgeError("REMAKE_SWORD_PREVIEW_FRAME_DECODING_INVALID")
    differences=sum(abs(a-b)>16 for a,b in zip(raw[:size],raw[size:]))
    if differences<200:
        raise VideoForgeError("REMAKE_SWORD_PREVIEW_NO_LOCALIZED_MOTION_DETECTED")
    report={"schema":"videoforge/remake-sword-preview-qa/v1",
        "shot":"C01-P02","technical_preview_only":True,"official_video_approved":False,
        "human_visual_approved":False,"youtube_uploaded":False,
        "renderer":"remotion-ThreeCanvas","rig":"separate-underlay-sheath-blade-hand",
        "fps":FPS,"frames":FRAMES,"width":W,"height":H,
        "duration_seconds":3,"decoded_frame_changed_channels":differences,
        "mp4_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
        "source_artifact":stage_data["source_artifact"],
        "source_run_id":stage_data["source_run_id"],
        "neutral_mae_rgb":stage_data["neutral_mae_rgb"],
        "source_mother_sha256":stage_data["hashes"]["scene-mother"],
        "anchor_sha256":stage_data["anchor_sha256"],"new_image_calls":0,
        "youtube_publication":False}
    (output/"preview.qa.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    try:
        print("REMAKE_SWORD_MP4_QA",json.dumps(verify(a.output),ensure_ascii=False))
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError) as exc:
        print("REMAKE_SWORD_MP4_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
