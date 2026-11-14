"""Pipeline oficial de origem: cena-mae -> background + sprite(s) RGBA.

A cena-mãe vem de um artifact REAL do próprio VideoForge-IA. Nenhuma cena
nova pode substituí-la. Gera só as camadas solicitadas, sem retry HTTP 429.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from . import scene_layers, production_art, proxy_images
from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
SCHEMA="videoforge/scene-mother-layer-plan/v1"


def read_plan(channel:str,video_id:str,number:int)->tuple[dict,dict,dict]:
    _art,story=production_art.read_plan(channel,video_id)
    path=ROOT/"canal"/channel/"videos"/video_id/"production-layer-plan.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size>200_000:
        raise VideoForgeError("SCENE_MOTHER_LAYER_PLAN_MISSING")
    try:
        plan=json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,OSError) as exc:
        raise VideoForgeError("SCENE_MOTHER_LAYER_PLAN_INVALID") from exc
    if plan.get("schema")!=SCHEMA or plan.get("channel")!=channel or plan.get("video_id")!=video_id:
        raise VideoForgeError("SCENE_MOTHER_PLAN_ORIGIN_INVALID")
    entries=plan.get("scenes")
    if not isinstance(entries,list) or len(entries)!=len(story["scenes"]):
        raise VideoForgeError("SCENE_MOTHER_SCENES_MISMATCH")
    if type(number) is not int or number<1 or number>len(entries):
        raise VideoForgeError("SCENE_MOTHER_NUMBER_INVALID")
    entry=entries[number-1]
    original=story["scenes"][number-1]
    if entry.get("number")!=number or entry.get("scene")!=original["id"]:
        raise VideoForgeError("SCENE_MOTHER_ORDER_INVALID")
    if entry.get("required_layers")!=["background","character-main"]:
        raise VideoForgeError("SCENE_MOTHER_REQUIRED_LAYERS_MISSING")
    if entry.get("human_visual_approval") is not False:
        raise VideoForgeError("SCENE_MOTHER_REVIEW_FLAG_INVALID")
    return plan,story,entry


def validate_source(source:Path,report:Path,entry:dict,channel:str,video_id:str)->str:
    if any(x.is_symlink() or not x.is_file() for x in (source,report)):
        raise VideoForgeError("SCENE_MOTHER_REAL_SOURCE_MISSING")
    try:
        metadata=json.loads(report.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise VideoForgeError("SCENE_MOTHER_SOURCE_REPORT_INVALID") from exc
    raw=scene_layers._read_png(source)
    checksum=hashlib.sha256(raw).hexdigest()
    if (metadata.get("schema")!="videoforge/production-scene/v1" or
        metadata.get("channel")!=channel or metadata.get("video_id")!=video_id or
        metadata.get("number")!=entry["number"] or
        metadata.get("scene")!=entry["scene"] or
        metadata.get("sha256")!=checksum):
        raise VideoForgeError("SCENE_MOTHER_SOURCE_SHA_OR_ORIGIN_MISMATCH")
    info=scene_layers.png_info(raw)
    if (info["width"],info["height"])!=(1024,1536):
        raise VideoForgeError("SCENE_MOTHER_SOURCE_CANVAS_MISMATCH")
    return checksum


def generate(channel:str,video_id:str,number:int,source:Path,report:Path,
             proxy_url:str,model:str)->dict:
    plan,story,entry=read_plan(channel,video_id,number)
    source_hash=validate_source(source,report,entry,channel,video_id)
    if model not in proxy_images.IMAGE_MODELS:
        raise VideoForgeError("SCENE_MOTHER_IMAGE_MODEL_INVALID")
    if plan.get("budget",{}).get("extra_images_this_test")!=2 or number!=1:
        # Este workflow é o teste de duas imagens autorizado. Para mais
        # cenas é necessário planejar o orçamento e executar novos jobs.
        raise VideoForgeError("SCENE_MOTHER_TEST_BUDGET_INVALID")
    scene=f"cena-{number:02d}"
    folder=scene_layers.initialize(channel,video_id,scene,source)
    common=f" Cena original {entry['scene']}: {entry['visual_direction']}. "
    for component,field in (
        ("background","instruction_background"),
        ("character-main","instruction_character"),
    ):
        instruction=plan.get(field,"")
        if not isinstance(instruction,str) or not instruction:
            raise VideoForgeError("SCENE_MOTHER_COMPONENT_INSTRUCTION_MISSING")
        scene_layers.generate_layer(
            folder,component,proxy_url,os.getenv("CODEX_PROXY_API_KEY",""),
            model,instruction=instruction+common)
    manifest=scene_layers._read_manifest(folder/"manifest.json")
    if manifest["source"]["sha256"]!=source_hash:
        raise VideoForgeError("SCENE_MOTHER_MANIFEST_SHA_MISMATCH")
    if set(manifest.get("layers",{}))!={"background","character-main"}:
        raise VideoForgeError("SCENE_MOTHER_GENERATED_LAYERS_INCOMPLETE")
    report={
        "schema":"videoforge/scene-mother-layer-qa/v1",
        "channel":channel,"video_id":video_id,
        "scene":entry["scene"],"number":number,
        "scene_mother_sha256":source_hash,
        "layers":{k:v["sha256"] for k,v in manifest["layers"].items()},
        "real_rgba_alpha_technical_qa":True,
        "background_reconstructed_technical_qa":True,
        "individual_sprites_generated":False,
        "objects_separated":False,
        "rig_animation_applied":False,
        "visual_approval":"pending",
        "video_official":False,
        "youtube_uploaded":False,
        "notes":"Background and group-character cutout are real; individual heads/eyes/hair/clothes and QA remain pending.",
    }
    (folder/"production-layer.qa.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SCENE_MOTHER_LAYERS_GENERATED",json.dumps(report,ensure_ascii=False))
    return report


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--number",type=int,required=True)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--source-report",required=True,type=Path)
    p.add_argument("--url",required=True)
    p.add_argument("--model",default="gpt-image-2")
    a=p.parse_args()
    try:
        generate(a.channel,a.video_id,a.number,a.source,a.source_report,a.url,a.model)
        return 0
    except (VideoForgeError,scene_layers.LayerError,proxy_images.ProxyImageError,
            ValueError,OSError) as exc:
        print("SCENE_MOTHER_LAYER_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
