"""Prévia verificável de camadas REAIS dentro do motor Remotion VideoForge.

É teste de UMA cena com BG reconstruído + sprite de personagens RGBA.
Não declara cabeça/olhos/cabelo ou objetos individuais já separados.
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

from . import mvp, scene_layers, production_scene_layers
from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
FPS=30


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_dir(channel:str,video_id:str,scene:str)->Path:
    return ROOT/"output"/channel/"videos"/video_id/"layers-review"/scene


def prepare(channel:str,video_id:str,number:int,layer_dir:Path,voice_dir:Path,blink_dir:Path|None=None)->dict:
    plan,story,entry=production_scene_layers.read_plan(channel,video_id,number)
    scene=f"cena-{number:02d}"
    manifest=scene_layers._read_manifest(layer_dir/"manifest.json")
    qa=json.loads((layer_dir/"production-layer.qa.json").read_text(encoding="utf-8"))
    if ((manifest.get("channel"),manifest.get("video_id"),manifest.get("scene"))
            !=(channel,video_id,scene) or
        qa.get("schema")!="videoforge/scene-mother-layer-qa/v1" or
        qa.get("scene_mother_sha256")!=manifest["source"]["sha256"] or
        qa.get("scene")!=entry["scene"] or
        qa.get("visual_approval")!="pending" or
        qa.get("rig_animation_applied") is not False):
        raise VideoForgeError("LAYER_REVIEW_PROVENANCE_INVALID")
    bg=layer_dir/"background.png"
    character=layer_dir/"character-main.png"
    source=layer_dir/"cena-base.png"
    for name,p,alpha in (("background",bg,False),("character-main",character,True)):
        record=manifest.get("layers",{}).get(name)
        if not isinstance(record,dict) or record.get("technical_status")!="verified" or not p.is_file() or p.is_symlink():
            raise VideoForgeError("LAYER_REVIEW_MISSING_VERIFIED_LAYER")
        if sha(p)!=record.get("sha256") or qa["layers"].get(name)!=sha(p):
            raise VideoForgeError("LAYER_REVIEW_LAYER_SHA_MISMATCH")
        info=scene_layers.png_info(p.read_bytes(),require_alpha=alpha)
        if (info["width"],info["height"])!=(1024,1536):
            raise VideoForgeError("LAYER_REVIEW_CANVAS_MISMATCH")
    if not source.is_file() or sha(source)!=manifest["source"]["sha256"]:
        raise VideoForgeError("LAYER_REVIEW_SCENE_MOTHER_MISMATCH")

    speech=json.loads((voice_dir/"audio-stage.qa.json").read_text(encoding="utf-8"))
    if (speech.get("schema")!="videoforge/female-voice-stage/v1" or
        (speech.get("channel"),speech.get("video_id"))!=(channel,video_id) or
        speech.get("voice")!="pt-br+f3"):
        raise VideoForgeError("LAYER_REVIEW_FEMALE_VOICE_ORIGIN_INVALID")
    rows=speech.get("audio",[])
    if len(rows)!=len(story["scenes"]):
        raise VideoForgeError("LAYER_REVIEW_VOICE_SCENE_COUNT_MISMATCH")
    data=rows[number-1]
    wav=voice_dir/"audio"/f"cena-{number:02d}.wav"
    srt=voice_dir/"subtitles"/f"cena-{number:02d}.srt"
    if (data.get("scene")!=entry["scene"] or
        data.get("spoken_text")!=story["scenes"][number-1]["narration"] or
        not wav.is_file() or not srt.is_file() or
        sha(wav)!=data.get("audio_sha256") or
        sha(srt)!=data.get("subtitle_sha256")):
        raise VideoForgeError("LAYER_REVIEW_FEMALE_AUDIO_OR_SUBTITLE_INVALID")
    duration=mvp._duration(mvp._media_info(wav))
    if not 2<duration<100:
        raise VideoForgeError("LAYER_REVIEW_AUDIO_DURATION_INVALID")
    frames=math.ceil(duration*FPS)
    blink_asset=None
    hair_asset=None
    blink_centers=[]
    blink_record=None
    hair_record=None
    occlusion_record=None
    if blink_dir is not None:
        bm=scene_layers._read_manifest(blink_dir/"manifest.json")
        bqa=json.loads((blink_dir/"eye-overlay.qa.json").read_text(encoding="utf-8"))
        original_eyes=blink_dir/"eyes-closed.png"
        blink_asset=blink_dir/"eyes-closed-safe.png"
        hair_asset=blink_dir/"hair-foreground.png"
        occlusion_path=blink_dir/"occlusion.qa.json"
        if not occlusion_path.is_file() or occlusion_path.is_symlink():
            raise VideoForgeError("LAYER_REVIEW_HAIR_OCCLUSION_QA_REQUIRED")
        occlusion=json.loads(occlusion_path.read_text(encoding="utf-8"))
        record=bm.get("layers",{}).get("eyes-closed")
        if (bm.get("source",{}).get("sha256")!=manifest["source"]["sha256"] or
            not isinstance(record,dict) or record.get("technical_status")!="verified" or
            not original_eyes.is_file() or original_eyes.is_symlink() or
            not blink_asset.is_file() or blink_asset.is_symlink() or
            hair_asset is None or not hair_asset.is_file() or hair_asset.is_symlink() or
            record.get("sha256")!=sha(original_eyes) or
            bqa.get("eyes_rgba_sha256")!=sha(original_eyes) or
            bqa.get("scene_mother_sha256")!=manifest["source"]["sha256"] or
            bqa.get("tech_roi_qa")!="passed" or
            bqa.get("visual_review")!="pending"):
            raise VideoForgeError("LAYER_REVIEW_EYES_NOT_VALIDATED")
        if (occlusion.get("schema")!="videoforge/blink-hair-occlusion/v1" or
            occlusion.get("scene_mother_sha256")!=manifest["source"]["sha256"] or
            occlusion.get("character_original_sha256")!=sha(character) or
            occlusion.get("raw_eyes_sha256")!=sha(original_eyes) or
            occlusion.get("safe_eyes_sha256")!=sha(blink_asset) or
            occlusion.get("hair_foreground_sha256")!=sha(hair_asset) or
            occlusion.get("occlusion_qa")!="eye_matte_excludes_original_hair" or
            occlusion.get("visual_approval") is not False or
            occlusion.get("pixels_outside_safe_eyes")!=0 or
            occlusion.get("face_base_opacity_untouched") is not True):
            raise VideoForgeError("LAYER_REVIEW_EYE_OVER_HAIR_QA_INVALID")
        scene_layers.png_info(blink_asset.read_bytes(),require_alpha=True)
        scene_layers.png_info(hair_asset.read_bytes(),require_alpha=True)
        occlusion_record=occlusion
        hair_record=sha(hair_asset)
        blink_centers=bqa.get("blink_centers_frames",[])
        if (not isinstance(blink_centers,list) or not blink_centers or
            any(type(t) is not int or t<3 or t>=frames-2 for t in blink_centers)):
            raise VideoForgeError("LAYER_REVIEW_BLINK_TIMING_INVALID")
        blink_record=sha(blink_asset)
    dest=output_dir(channel,video_id,scene)
    public=ROOT/"motion-remotion"/"public"/"vf-scene"
    if dest.exists() or public.exists():
        raise VideoForgeError("LAYER_REVIEW_CANNOT_OVERWRITE")
    public.mkdir(parents=True)
    dest.mkdir(parents=True)
    for src,target in ((bg,"background.png"),(character,"character-main.png"),
                       (wav,"narracao-feminina.wav")):
        shutil.copyfile(src,public/target)
    if blink_asset is not None:
        shutil.copyfile(blink_asset,public/"eyes-closed-safe.png")
        shutil.copyfile(hair_asset,public/"hair-foreground.png")
    shutil.copyfile(srt,dest/"legenda-original.srt")
    props={
        "id":video_id,"scene":scene,"durationFrames":frames,
        "preset":"equilibrado",
        "background":"vf-scene/background.png",
        "character":"vf-scene/character-main.png",
        "foreground":None,  # sobrescreve defaultProps legado do Remotion
        "eyesClosed":"vf-scene/eyes-closed-safe.png" if blink_asset is not None else None,
        "hairForeground":"vf-scene/hair-foreground.png" if hair_asset is not None else None,
        "blinkFrames":blink_centers,
        "animatedObjects":[],  # nunca inventar objetos ausentes
        "silence":"vf-scene/narracao-feminina.wav",
        "layerSourceHash":sha(source),
        "draftPreview":True
    }
    (dest/"props.json").write_text(
        json.dumps(props,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    details={
        "schema":"videoforge/layer-review-stage/v1",
        "channel":channel,"video_id":video_id,"scene":scene,
        "source_sha256":sha(source),"background_sha256":sha(bg),
        "character_sha256":sha(character),"voice_sha256":sha(wav),
        "subtitle_sha256":sha(srt),"duration_frames":frames,
        "duration_seconds":duration,"individual_parts_animated":False,
        "layered_motion":True,"camera_motion_not_rig":True,
        "eyes_closed_rgba_verified":blink_record is not None,
        "eyes_closed_sha256":blink_record,
        "hair_foreground_rgba_verified":hair_record is not None,
        "hair_foreground_sha256":hair_record,
        "hair_occlusion_qa":occlusion_record.get("occlusion_qa") if occlusion_record else "not_applicable",
        "separate_object_layers":0,
        "character_micro_motion_px_max":2.8,
        "human_visual_review":"pending","youtube_uploaded":False,
        "official_video_created":False
    }
    (dest/"stage.qa.json").write_text(
        json.dumps(details,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("LAYER_REVIEW_STAGE_OK",json.dumps(details,ensure_ascii=False))
    return details


def verify(channel:str,video_id:str,number:int)->dict:
    scene=f"cena-{number:02d}"
    dest=output_dir(channel,video_id,scene)
    stage=json.loads((dest/"stage.qa.json").read_text(encoding="utf-8"))
    video=dest/"layered-preview.mp4"
    if not video.is_file() or video.stat().st_size<30000:
        raise VideoForgeError("LAYER_REVIEW_MP4_MISSING")
    duration=stage["duration_frames"]/FPS
    result=mvp._verify_mp4(video,expected=duration,
        minimum=duration-.5,maximum=duration+.7)
    def image_hash(second:float)->str:
        p=subprocess.run([
            "ffmpeg","-nostdin","-hide_banner","-loglevel","error",
            "-i",str(video),"-ss",str(second),"-frames:v","1","-f","md5","-",
        ],capture_output=True,timeout=60,check=False)
        if p.returncode!=0:
            raise VideoForgeError("LAYER_REVIEW_FRAME_DECODE_FAILED")
        return p.stdout.decode().strip()
    if image_hash(duration*.18)==image_hash(duration*.74):
        raise VideoForgeError("LAYER_REVIEW_MOVEMENT_NOT_FOUND")
    result.update({
        "schema":"videoforge/layer-review-qa/v1",
        "channel":channel,"video_id":video_id,"scene":scene,
        "scene_mother_sha256":stage["source_sha256"],
        "background_rgba_verified":True,
        "characters_real_alpha_verified":True,
        "female_voice_and_srt_present":True,
        "eyes_blink_rgba_verified":bool(stage.get("eyes_closed_rgba_verified")),
        "eyes_blink_visual_review":"pending",
        "bangs_over_blink_technical_qa":stage.get("hair_occlusion_qa")=="eye_matte_excludes_original_hair",
        "hair_foreground_rgba_verified":bool(stage.get("hair_foreground_rgba_verified")),
        "character_motion_reduced_to_max_px":stage.get("character_micro_motion_px_max"),
        "remotion_layered_motion_verified":True,
        "rig_head_eyes_hair_clothes":False,
        "visual_review":"pending","official_video_created":False,
        "youtube_uploaded":False
    })
    (dest/"layered-preview.qa.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("prepare","verify"))
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--number",type=int,required=True)
    p.add_argument("--layers",type=Path)
    p.add_argument("--voice",type=Path)
    p.add_argument("--blink",type=Path)
    args=p.parse_args()
    try:
        if args.command=="prepare":
            if args.layers is None or args.voice is None:
                raise VideoForgeError("LAYER_REVIEW_INPUTS_MISSING")
            prepare(args.channel,args.video_id,args.number,args.layers,args.voice,args.blink)
        else:
            result=verify(args.channel,args.video_id,args.number)
            print("LAYER_REVIEW_MP4_QA_OK",json.dumps(result,ensure_ascii=False))
        return 0
    except (VideoForgeError,scene_layers.LayerError,ValueError,OSError,KeyError) as exc:
        print("LAYER_REVIEW_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
