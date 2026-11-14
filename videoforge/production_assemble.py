"""Montagem de ASSETS REAIS pelo compositor canonico VideoForge (mvp.render).

Nao usa cartoes, SVG gerado por outro script, fixtures, imagens externas
nem publica no YouTube. Cenas e vozes sao lidas de artifacts rastreaveis
do mesmo projeto GitHub. A versao sem rig e apenas revisao editorial.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from . import mvp, production_art, scene_layers
from .errors import VideoForgeError
from .paths import _check_symlinks

ROOT=Path(__file__).resolve().parents[1]


def _sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(channel:str,video_id:str,images:Path,voice:Path,
            reference_report:Path,root:Path=ROOT)->dict:
    plan,story=production_art.read_plan(channel,video_id,root)
    video=root/"canal"/channel/"videos"/video_id
    scenes=story["scenes"]
    data=json.loads(reference_report.read_text(encoding="utf-8"))
    ref=data.get("sha256")
    if data.get("asset_id")!="character-bible" or not isinstance(ref,str) or len(ref)!=64:
        raise VideoForgeError("ASSEMBLY_REFERENCE_INVALID")
    meta=json.loads((voice/"audio-stage.qa.json").read_text(encoding="utf-8"))
    if meta.get("channel")!=channel or meta.get("video_id")!=video_id:
        raise VideoForgeError("ASSEMBLY_VOICE_ORIGIN_INVALID")
    if len(meta.get("audio",[]))!=len(scenes):
        raise VideoForgeError("ASSEMBLY_VOICE_COUNT_INVALID")
    to_copy=[]
    image_hashes=[]
    audio_hashes=[]
    for index,scene in enumerate(scenes,1):
        image_name=Path(scene["image"]).name
        voice_name=Path(scene["audio"]).name
        if (scene.get("number")!=index or image_name!=f"cena-{index:02d}.png"
            or voice_name!=f"cena-{index:02d}.wav"):
            raise VideoForgeError("ASSEMBLY_STORYBOARD_SCENE_INVALID")
        src=images/image_name
        report=images/f"cena-{index:02d}.production.json"
        if any(p.is_symlink() or not p.is_file() for p in (src,report)):
            raise VideoForgeError(f"ASSEMBLY_SCENE_ASSET_MISSING_{index}")
        info=json.loads(report.read_text(encoding="utf-8"))
        checksum=_sha(src)
        if (info.get("channel")!=channel or info.get("video_id")!=video_id
            or info.get("number")!=index or info.get("scene")!=scene["id"]
            or info.get("sha256")!=checksum
            or info.get("reference_sha256")!=ref):
            raise VideoForgeError(f"ASSEMBLY_IMAGE_HASH_ORIGIN_INVALID_{index}")
        image_info=scene_layers.png_info(src.read_bytes(),require_alpha=False)
        if (image_info["width"],image_info["height"])!=(1024,1536):
            raise VideoForgeError(f"ASSEMBLY_IMAGE_SIZE_INVALID_{index}")
        audio_src=voice/"audio"/voice_name
        if audio_src.is_symlink() or not audio_src.is_file():
            raise VideoForgeError(f"ASSEMBLY_VOICE_MISSING_{index}")
        voice_rec=meta["audio"][index-1]
        audio_sha=_sha(audio_src)
        if (voice_rec.get("scene")!=scene["id"] or voice_rec.get("sha256")!=audio_sha
            or voice_rec.get("audio")!=voice_name):
            raise VideoForgeError(f"ASSEMBLY_VOICE_HASH_ORIGIN_INVALID_{index}")
        image_hashes.append(checksum)
        audio_hashes.append(audio_sha)
        to_copy.extend([(src,video/"imagens"/image_name),
                        (audio_src,video/"voz"/voice_name)])
    # Nada e movido ate TODOS os arquivos e hashes estarem validados.
    for src,dst in to_copy:
        _check_symlinks(dst,stop_at=root)
        if dst.exists():
            raise VideoForgeError("ASSEMBLY_DESTINATION_ALREADY_EXISTS")
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
    report={
        "schema":"videoforge/real-art-assembly/v1",
        "channel":channel,"video_id":video_id,"scene_count":len(scenes),
        "reference_sha256":ref,
        "scene_image_sha256":image_hashes,
        "voice_sha256":audio_hashes,
        "provenance_verified":True,
        "status":"ready_for_mvp_technical_render",
        "art_visual_approved":False,
        "rig_animation_applied":False,
        "official_video_created":False,
        "youtube_uploaded":False,
    }
    return report


def render(channel:str,video_id:str,images:Path,voice:Path,
           reference_report:Path,root:Path=ROOT)->dict:
    status=prepare(channel,video_id,images,voice,reference_report,root)
    manifest=root/"canal"/channel/"videos"/video_id/"video.json"
    qa=mvp.render(manifest)
    if qa.get("status")!="technical_verified" or qa.get("scenes")!=status["scene_count"]:
        raise VideoForgeError("ASSEMBLY_MVP_RENDER_QA_INVALID")
    status.update({
        "status":"technical_real_art_mp4_for_review",
        "mp4_sha256":qa["sha256"],
        "mp4_duration_seconds":qa["duration_seconds"],
        "mp4_codec":qa["video_codec"],
        "art_type":"original_ai_generated_consistent_reference",
        "narration_type":"offline_draft_synthetic",
        "visual_review":"pending",
        "model_used":"imagem-estatica",
        "rig_animation_applied":False,
        "official_video_created":False,
        "youtube_uploaded":False,
    })
    output=root/"output"/channel/"videos"/video_id
    output.mkdir(parents=True,exist_ok=True)
    (output/"real-art.review.qa.json").write_text(
        json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return status


def main()->int:
    p=argparse.ArgumentParser(description="VideoForge canonical render with authentic art assets")
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--images",required=True,type=Path)
    p.add_argument("--voice",required=True,type=Path)
    p.add_argument("--reference-report",required=True,type=Path)
    a=p.parse_args()
    try:
        report=render(a.channel,a.video_id,a.images,a.voice,a.reference_report)
        print("VIDEOFORGE_REAL_ART_REVIEW_RENDER",json.dumps(
            {k:v for k,v in report.items() if k not in ("scene_image_sha256","voice_sha256")},
            ensure_ascii=False))
        return 0
    except (VideoForgeError,ValueError,OSError,KeyError) as exc:
        print("VIDEOFORGE_ASSEMBLY_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
