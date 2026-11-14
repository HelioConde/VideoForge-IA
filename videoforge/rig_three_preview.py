"""Production adapter for approved RGBA rigs rendered by Remotion ThreeCanvas.

Fails closed if scene-mother, hashes, real alpha, layers or head pivot are
missing. No proxy calls, no off-repo render, no automatic YouTube upload.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from . import scene_layers, mvp
from .rig_three_contract import validate_rig_folder,ThreeRigError
from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
FPS=30


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target(channel:str,video_id:str,scene:str)->Path:
    scene_layers.output_dir(channel,video_id,scene)
    return ROOT/"output"/channel/"videos"/video_id/"rig-three"/scene


def prepare(channel:str,video_id:str,scene:str,source_dir:Path,
            rig_dir:Path,frames:int,voice:Path|None=None)->dict:
    if type(frames) is not int or not 90<=frames<=18000:
        raise VideoForgeError("RIG_THREE_DURATION_FRAMES_INVALID")
    manifest=scene_layers._read_manifest(source_dir/"manifest.json")
    if (manifest.get("channel"),manifest.get("video_id"),manifest.get("scene"))!=(
            channel,video_id,scene):
        raise VideoForgeError("RIG_THREE_SCENE_PROVENANCE_INVALID")
    image=source_dir/"character-main.png"
    background=source_dir/"background.png"
    source=source_dir/"cena-base.png"
    if any(p.is_symlink() or not p.is_file() for p in (image,background,source)):
        raise VideoForgeError("RIG_THREE_SOURCE_FILES_MISSING")
    source_sha=sha(source)
    if manifest.get("source",{}).get("sha256")!=source_sha:
        raise VideoForgeError("RIG_THREE_SCENE_SHA_INVALID")
    info=scene_layers.png_info(background.read_bytes(),require_alpha=False)
    if sha(background)!=manifest.get("layers",{}).get("background",{}).get("sha256"):
        raise VideoForgeError("RIG_THREE_BACKGROUND_SHA_INVALID")
    if sha(image)!=manifest.get("layers",{}).get("character-main",{}).get("sha256"):
        raise VideoForgeError("RIG_THREE_CHARACTER_ORIGINAL_SHA_INVALID")
    rig=validate_rig_folder(
        rig_dir,channel=channel,video_id=video_id,scene=scene,
        scene_mother_sha256=source_sha,frames=frames,
    )
    if rig["canvas"]!={"width":info["width"],"height":info["height"]}:
        raise VideoForgeError("RIG_THREE_CANVAS_DOES_NOT_MATCH_BACKGROUND")
    output=target(channel,video_id,scene)
    public=ROOT/"motion-remotion"/"public"/"vf-scene"
    if output.exists() or public.exists():
        raise VideoForgeError("RIG_THREE_OUTPUT_ALREADY_EXISTS")
    output.mkdir(parents=True)
    asset_dir=public/"rig-three"
    asset_dir.mkdir(parents=True)
    shutil.copyfile(background,public/"background.png")
    for layer in rig["layers"]:
        name=Path(layer["file"]).name
        shutil.copyfile(rig_dir/name,asset_dir/name)
        if sha(asset_dir/name)!=layer["sha256"]:
            raise VideoForgeError("RIG_THREE_POSTCOPY_SHA_INVALID")
    if voice is None:
        audio=public/"rig-silence.wav"
        mvp._command([
            "ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
            "-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-t",
            str(frames/FPS),"-c:a","pcm_s16le",str(audio),
        ],timeout=90)
    else:
        if voice.is_symlink() or not voice.is_file():
            raise VideoForgeError("RIG_THREE_VOICE_MISSING")
        audio=public/"rig-narration.wav"
        shutil.copyfile(voice,audio)
        actual=mvp._duration(mvp._media_info(audio))
        if abs(actual-frames/FPS)>.8:
            raise VideoForgeError("RIG_THREE_VOICE_DURATION_MISMATCH")
    props={
        "id":video_id,"scene":scene,"durationFrames":frames,
        "background":"vf-scene/background.png",
        "rig":rig,"foreground":None,"audio":"vf-scene/"+audio.name,
        "draftPreview":True
    }
    (output/"props.json").write_text(json.dumps(props,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    result={
        "schema":"videoforge/rig-three-stage/v1",
        "channel":channel,"video_id":video_id,"scene":scene,
        "source_scene_mother_sha256":source_sha,
        "character_original_sha256":sha(image),"background_sha256":sha(background),
        "rig_schema":rig["schema"],"rig_parts":len(rig["layers"]),
        "deformable_meshes":sum(bool(l.get("mesh")) for l in rig["layers"]),
        "duration_frames":frames,"fps":FPS,
        "renderer":"remotion-three-swangle","real_layer_rig_requested":True,
        "rig_assets_reviewed":True,"render_visual_review":"pending",
        "youtube_uploaded":False,"video_official":False,
    }
    (output/"stage.qa.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RIG_THREE_STAGE_VERIFIED",json.dumps(result,ensure_ascii=False))
    return result


def verify(channel:str,video_id:str,scene:str)->dict:
    dest=target(channel,video_id,scene)
    stage=json.loads((dest/"stage.qa.json").read_text(encoding="utf-8"))
    video=dest/"mesh-preview.mp4"
    if not video.is_file() or video.is_symlink() or video.stat().st_size<30000:
        raise VideoForgeError("RIG_THREE_PREVIEW_MP4_MISSING")
    seconds=stage["duration_frames"]/FPS
    info=mvp._verify_mp4(video,expected=seconds,minimum=seconds-.5,maximum=seconds+.7)
    info.update({
        "schema":"videoforge/rig-three-preview-qa/v1",
        "scene":scene,"channel":channel,"video_id":video_id,
        "source_scene_mother_sha256":stage["source_scene_mother_sha256"],
        "deformable_mesh_count":stage["deformable_meshes"],
        "real_mesh_renderer":"remotion-three-swangle",
        "render_visual_review":"pending",
        "video_official":False,"youtube_uploaded":False,
    })
    (dest/"mesh-preview.qa.json").write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RIG_THREE_PREVIEW_MP4_QA",json.dumps(info,ensure_ascii=False))
    return info


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("prepare","verify"))
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--scene",required=True)
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--rig-dir",type=Path)
    p.add_argument("--voice",type=Path)
    p.add_argument("--frames",type=int,default=240)
    a=p.parse_args()
    try:
        if a.command=="prepare":
            if a.source_dir is None or a.rig_dir is None:
                raise VideoForgeError("RIG_THREE_INPUTS_REQUIRED")
            prepare(a.channel,a.video_id,a.scene,a.source_dir,a.rig_dir,a.frames,a.voice)
        else:
            verify(a.channel,a.video_id,a.scene)
        return 0
    except (VideoForgeError,ThreeRigError,scene_layers.LayerError,
            ValueError,OSError,KeyError) as exc:
        print("RIG_THREE_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
