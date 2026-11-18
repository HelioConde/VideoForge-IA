"""SHA-locked camera-only Remotion preview of approved C01-P04 image.

This makes a technical video proof only; it never authorizes the 40-shot
episode, any fake character rig, image generation, or YouTube publication.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

from .layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from .errors import VideoForgeError

SCHEMA="videoforge/ep01-c01p04-static-camera-preview/v1"
PLAN=REL/"PLANO-PREVIA-CAMERA-C01-P04.json"
APPROVAL=REL/"APROVACOES-VISUAIS-C01-V3.json"
DECISION=REL/"POLITICA-SEM-MAOS-INDEPENDENTES-C01-P04.json"
MOTHER_SHA="a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
ALIGNED_SHA="b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
STATIC_REL=Path("vf-ep01-c01p04-camera/scene-mother-approved-aligned.png")
OUT_REL=Path("output")/CHANNEL/"videos"/VIDEO/"previews"/"c01-p04-camera-only-v1"
FPS,DURATION,WIDTH,HEIGHT=30,70,540,960

def require_doc(path:Path,root:Path)->dict:
    source=root/path
    if source.is_symlink() or not source.is_file():
        raise VideoForgeError("CAMERA_PREVIEW_MANIFEST_MISSING "+str(path))
    return json.loads(source.read_text(encoding="utf-8"))

def image_sha(root:Path,path:str,expect:str,dimensions:list[int])->bytes:
    file=root/path
    if not file.is_file() or file.is_symlink() or ".." in Path(path).parts:
        raise VideoForgeError("CAMERA_PREVIEW_IMAGE_MISSING_OR_UNSAFE")
    blob=file.read_bytes()
    if sha256(blob).hexdigest()!=expect:
        raise VideoForgeError("CAMERA_PREVIEW_SOURCE_SHA_MISMATCH")
    if (len(blob)<24 or blob[:8]!=b"\x89PNG\\r\\n\x1a\\n"
        or blob[12:16]!=b"IHDR"):
        raise VideoForgeError("CAMERA_PREVIEW_SOURCE_NOT_PNG")
    w,h=struct.unpack(">II",blob[16:24])
    if [w,h]!=dimensions:
        raise VideoForgeError("CAMERA_PREVIEW_INVALID_SOURCE_DIMENSIONS")
    return blob

def preflight(root:Path=ROOT)->dict:
    root=Path(root)
    plan=require_doc(PLAN,root)
    approval=require_doc(APPROVAL,root)
    policy=require_doc(DECISION,root)
    if (plan.get("schema")!=SCHEMA or plan.get("channel")!=CHANNEL
        or plan.get("video_id")!=VIDEO or plan.get("shot_id")!="C01-P04"
        or plan.get("source_approved_original",{}).get("sha256")!=MOTHER_SHA
        or plan.get("source_technical_aligned",{}).get("sha256")!=ALIGNED_SHA
        or plan.get("timeline",{}).get("duration_frames")!=DURATION
        or plan.get("timeline",{}).get("start_frame")!=240
        or plan.get("timeline",{}).get("end_frame_exclusive")!=310
        or plan.get("timeline",{}).get("fps")!=FPS
        or plan.get("render",{}).get("preview_only") is not True
        or plan.get("render",{}).get("no_youtube_upload") is not True
        or plan.get("official_episode_render_authorized") is not False
        or plan.get("hand_parts_required") is not False):
        raise VideoForgeError("CAMERA_PREVIEW_PLAN_INVALID")
    approvals=approval.get("approvals",[])
    allowed=[x for x in approvals if x.get("shot_id")=="C01-P04"
             and x.get("sha256")==MOTHER_SHA
             and x.get("visual_status")=="approved_by_creator"]
    if approval.get("approval_scope")!="individual_exact_sha_only" or len(allowed)!=1:
        raise VideoForgeError("CAMERA_PREVIEW_CREATOR_APPROVAL_NOT_FOUND")
    if (policy.get("status")!="active" or
        policy.get("scope",{}).get("skip_independent_fingers") is not True or
        policy.get("animation_approach",{}).get("guards_in_c01_p04")!="static_approved_integrated_character_and_weapon_visual"):
        raise VideoForgeError("CAMERA_PREVIEW_HAND_SPLIT_POLICY_NOT_APPLIED")
    a=plan["source_approved_original"]
    b=plan["source_technical_aligned"]
    original=image_sha(root,a["path"],MOTHER_SHA,[941,1671])
    aligned=image_sha(root,b["path"],ALIGNED_SHA,[941,1672])
    # The immutable aligned file SHA is already validated pixel-for-pixel
    # by its archive proof, not by trusting the filename or a recomputation.
    proof=Path(root/b["path"]).with_suffix(".production.json")
    if proof.is_symlink() or not proof.is_file():
        raise VideoForgeError("CAMERA_PREVIEW_ALIGNED_PROOF_MISSING")
    evidence=json.loads(proof.read_text(encoding="utf-8"))
    if (evidence.get("sha256")!=ALIGNED_SHA
        or evidence.get("source_image_sha256")!=MOTHER_SHA
        or evidence.get("source_pixels_unchanged") is not True
        or evidence.get("pixel_qa")!="full_source_region_exact_and_bottom_row_identical"
        or evidence.get("output_canvas")!=[941,1672]
        or evidence.get("human_visual_approval") is not False):
        raise VideoForgeError("CAMERA_PREVIEW_ALIGNED_PIXEL_QA_INVALID")
    return {"original_sha256":sha256(original).hexdigest(),
            "aligned_sha256":sha256(aligned).hexdigest(),
            "aligned_bytes":aligned}

def prepare(root:Path=ROOT)->dict:
    root=Path(root)
    doc=preflight(root)
    dest=root/"motion-remotion"/"public"/STATIC_REL
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_symlink():
        raise VideoForgeError("CAMERA_PREVIEW_STATIC_SYMLINK")
    dest.write_bytes(doc["aligned_bytes"])
    out=root/OUT_REL
    out.mkdir(parents=True,exist_ok=True)
    props={
       "schema":SCHEMA,"shotId":"C01-P04","durationFrames":DURATION,
       "sourceFile":STATIC_REL.as_posix(),
       "approvedOriginalSha256":MOTHER_SHA,
       "alignedTechnicalSha256":ALIGNED_SHA,
       "approvedOriginalVerified":True,
       "alignedSourceVerified":True,
       "cameraOnly":True,"separateHandParts":False,
       "characterRigApproved":False,
       "officialEpisodeApproved":False,"youtubeUpload":False,
    }
    file=out/"props.json"
    file.write_text(json.dumps(props,indent=2)+"\n",encoding="utf-8")
    report={
       "schema":SCHEMA,
       "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
       "original_approved_sha256":MOTHER_SHA,
       "technical_aligned_sha256":ALIGNED_SHA,
       "static_file_sha256":sha256(dest.read_bytes()).hexdigest(),
       "remotion_props_file":str(file.relative_to(root)),
       "duration_frames":DURATION,"fps":FPS,
       "resolution":[WIDTH,HEIGHT],
       "visual_source_approved":True,"technical_preview_only":True,
       "no_hand_rig":True,"no_character_mesh_animation":True,
       "simulated_camera_only_no_true_parallax":True,
       "rendered_mp4":False,"official_episode_rendered":False,
       "youtube_uploaded":False,"image_provider_calls":0,
       "human_approval_of_camera_motion":False,
    }
    (out/"preview.qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

def verify(root:Path=ROOT)->dict:
    root=Path(root)
    report_path=root/OUT_REL/"preview.qa.json"
    report=json.loads(report_path.read_text(encoding="utf-8"))
    if (report.get("schema")!=SCHEMA or report.get("original_approved_sha256")!=MOTHER_SHA
        or report.get("technical_aligned_sha256")!=ALIGNED_SHA
        or report.get("technical_preview_only") is not True
        or report.get("no_hand_rig") is not True):
        raise VideoForgeError("CAMERA_PREVIEW_REPORT_INVALID")
    mp4=root/OUT_REL/"camera-preview.mp4"
    if not mp4.is_file() or mp4.stat().st_size<4000:
        raise VideoForgeError("CAMERA_PREVIEW_MP4_MISSING")
    command=["ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=codec_name,width,height,nb_frames,avg_frame_rate",
        "-of","json",str(mp4)]
    details=json.loads(subprocess.check_output(command,text=True))
    streams=details.get("streams",[])
    if len(streams)!=1:raise VideoForgeError("CAMERA_PREVIEW_VIDEO_STREAM_INVALID")
    stream=streams[0]
    if (stream.get("codec_name")!="h264" or
        stream.get("width")!=WIDTH or stream.get("height")!=HEIGHT or
        stream.get("avg_frame_rate")!="30/1" or
        int(stream.get("nb_frames","0"))!=DURATION):
        raise VideoForgeError("CAMERA_PREVIEW_WRONG_VIDEO_DIMENSIONS_FRAMES")
    report.update({
      "rendered_mp4":True,
      "mp4_sha256":sha256(mp4.read_bytes()).hexdigest(),
      "mp4_size_bytes":mp4.stat().st_size,
      "codec_verified":"h264",
      "frames_verified":DURATION,
      "human_approval_of_camera_motion":False,
      "official_episode_rendered":False,
      "youtube_uploaded":False,
      "rig_ready":False
    })
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("operation",choices=["preflight","prepare","verify"])
    args=parser.parse_args()
    try:
        if args.operation=="preflight": data=preflight();data.pop("aligned_bytes",None)
        elif args.operation=="prepare":data=prepare()
        else:data=verify()
        print("EP01_C01P04_STATIC_CAMERA",json.dumps(data,ensure_ascii=False))
        return 0
    except (OSError,ValueError,subprocess.CalledProcessError,VideoForgeError) as ex:
        print("EP01_C01P04_STATIC_CAMERA_BLOCKED",str(ex),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
