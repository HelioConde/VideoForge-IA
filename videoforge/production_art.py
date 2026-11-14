"""Arte original para o VideoForge, usando SOMENTE Codex Proxy conectado.

Cada chamada é uma geração real e auditada, nunca fixture, cartão SVG ou
simulação. Planos/roteiros residem no canal. O comando gera UM asset por run,
sem retry 429 e sem ultrapassar o orçamento de chamadas definido no plano.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from .errors import VideoForgeError
from . import proxy_images
from .paths import CHANNEL_IDS, IDENTIFIER
from .scene_layers import png_info

ROOT=Path(__file__).resolve().parents[1]
PLAN_SCHEMA="videoforge/production-art-plan/v1"


def read_plan(channel:str, video_id:str, root:Path=ROOT)->tuple[dict,dict]:
    if channel not in CHANNEL_IDS or not isinstance(video_id,str) or not IDENTIFIER.fullmatch(video_id):
        raise VideoForgeError("PRODUCTION_ART_CHANNEL_INVALID")
    base=root/"canal"/channel/"videos"/video_id
    p=base/"production-art.json"
    s=base/"roteiro.json"
    if any(f.is_symlink() or not f.is_file() or f.stat().st_size>200_000 for f in (p,s)):
        raise VideoForgeError("PRODUCTION_ART_PLAN_MISSING")
    try:
        plan=json.loads(p.read_text(encoding="utf-8"))
        story=json.loads(s.read_text(encoding="utf-8"))
    except (ValueError,UnicodeError,OSError) as exc:
        raise VideoForgeError("PRODUCTION_ART_PLAN_INVALID") from exc
    if not isinstance(plan,dict) or plan.get("schema")!=PLAN_SCHEMA or plan.get("channel")!=channel or plan.get("video_id")!=video_id:
        raise VideoForgeError("PRODUCTION_ART_PLAN_ORIGIN_INVALID")
    if not isinstance(story,dict) or story.get("video_id")!=video_id:
        raise VideoForgeError("PRODUCTION_ART_STORY_INVALID")
    scenes=story.get("scenes")
    if not isinstance(scenes,list) or not scenes:
        raise VideoForgeError("PRODUCTION_ART_SCENES_MISSING")
    return plan,story


def asset_prompt(plan:dict,story:dict,asset_id:str)->tuple[str,str]:
    assets=plan.get("assets")
    if not isinstance(assets,list):
        raise VideoForgeError("PRODUCTION_ART_ASSETS_INVALID")
    selected=[a for a in assets if isinstance(a,dict) and a.get("id")==asset_id]
    if len(selected)!=1:
        raise VideoForgeError("PRODUCTION_ART_UNKNOWN_ASSET")
    a=selected[0]
    if a.get("kind")!="reference" or a.get("size") not in proxy_images.IMAGE_SIZES:
        raise VideoForgeError("PRODUCTION_ART_ASSET_INVALID")
    prompt=a.get("prompt")
    if not isinstance(prompt,str) or not 10<=len(prompt)<=3800:
        raise VideoForgeError("PRODUCTION_ART_PROMPT_INVALID")
    policy=plan.get("visual_rules")
    if not isinstance(policy,list) or not policy:
        raise VideoForgeError("PRODUCTION_ART_RULES_MISSING")
    prefix="\\n".join(str(rule) for rule in policy)
    full=prompt+"\nGuia de consistência:\n"+prefix
    if len(full)>5000:
        raise VideoForgeError("PRODUCTION_ART_PROMPT_TOO_LONG")
    return full,a["size"]


def create_image(channel:str,video_id:str,asset_id:str,url:str,
                 model:str="gpt-image-2")->dict:
    plan,story=read_plan(channel,video_id)
    budget=plan.get("request_limit",{})
    if budget.get("per_run")!=1 or budget.get("strict_budget",0)<1:
        raise VideoForgeError("PRODUCTION_ART_BUDGET_INVALID")
    if not isinstance(asset_id,str) or not IDENTIFIER.fullmatch(asset_id):
        raise VideoForgeError("PRODUCTION_ART_ID_INVALID")
    prompt,size=asset_prompt(plan,story,asset_id)
    if model not in proxy_images.IMAGE_MODELS:
        raise VideoForgeError("PRODUCTION_ART_MODEL_INVALID")
    predicted=proxy_images.destination(channel,video_id,asset_id)
    if predicted.with_suffix(".png").exists() or predicted.with_suffix(".jpg").exists():
        raise VideoForgeError("PRODUCTION_ART_ALREADY_GENERATED")
    output=proxy_images.generate(
        url,os.getenv("CODEX_PROXY_API_KEY",""),
        channel,video_id,asset_id,model,size,prompt,
    )
    if output.suffix.lower()!=".png":
        raise VideoForgeError("PRODUCTION_ART_REQUIRES_PNG")
    blob=output.read_bytes()
    info=png_info(blob)
    if info["width"]!=1024 or info["height"]!=1536:
        raise VideoForgeError("PRODUCTION_ART_DIMENSIONS_INVALID")
    sha=hashlib.sha256(blob).hexdigest()
    result={"schema":"videoforge/production-art-result/v1",
            "channel":channel,"video_id":video_id,
            "asset_id":asset_id,"file":str(output.relative_to(ROOT)),
            "size":size,"sha256":sha,
            "model":model,"technical_qa":"valid_png_dimensions",
            "human_visual_approval":False,"official_video_created":False,
            "youtube_uploaded":False}
    output.with_suffix(".production.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main()->int:
    ap=argparse.ArgumentParser(description="Generate 1 real art reference using VideoForge Codex Proxy")
    ap.add_argument("--channel",required=True)
    ap.add_argument("--video-id",required=True)
    ap.add_argument("--asset",required=True)
    ap.add_argument("--url",required=True)
    ap.add_argument("--model",default="gpt-image-2")
    args=ap.parse_args()
    try:
        qa=create_image(args.channel,args.video_id,args.asset,args.url,args.model)
        print("ART_GENERATION_SUCCEEDED",json.dumps(qa,ensure_ascii=False))
        return 0
    except (VideoForgeError,proxy_images.ProxyImageError,ValueError,OSError) as exc:
        print("ART_GENERATION_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
