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
from . import image_generation_policy
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


def inspect_generated_dimensions(info: dict, requested_size: str) -> dict:
    """Keep authentic PNG dimensions. Never rescale or silently discard AI output.

    Portrait reference size is requested, but some Codex proxy image backends
    return alternate dimensions. A valid but non-canonical PNG is a *candidate*
    for human art review, never accepted as the approved 1024x1536 anchor.
    """
    width, height = info.get("width"), info.get("height")
    if (type(width) is not int or type(height) is not int
            or width < 512 or height < 512
            or width > 4096 or height > 4096):
        raise VideoForgeError("PRODUCTION_ART_DIMENSIONS_INVALID")
    requested = requested_size.split("x")
    if len(requested) != 2 or not all(v.isdigit() for v in requested):
        raise VideoForgeError("PRODUCTION_ART_REQUESTED_SIZE_INVALID")
    exact = (width == int(requested[0]) and height == int(requested[1]))
    return {
        "actual_width": width, "actual_height": height,
        "requested_size": requested_size,
        "dimensions_match_requested": exact,
        "technical_qa": ("valid_png_dimensions" if exact
                         else "valid_png_noncanonical_dimensions_visual_review_pending"),
        "pixel_resampling": False,
    }


def archived_reference(channel: str, video_id: str, asset_id: str,
                       root: Path = ROOT) -> dict | None:
    """Detect SHA-verified, permanent producer art BEFORE any new billed call.

    All GitHub Actions runners have a fresh output/ directory, so checking
    output alone is insufficient. Corrupt or ambiguous existing archives are
    a fail-closed blocker; never treat them as permission to regenerate.
    """
    if (channel not in CHANNEL_IDS or
            not IDENTIFIER.fullmatch(video_id) or
            not IDENTIFIER.fullmatch(asset_id)):
        raise VideoForgeError("PRODUCTION_ART_ARCHIVE_SCOPE_INVALID")
    episode=Path(root)/"canal"/channel/"videos"/video_id
    base=episode/"assets"/"geracoes"/"production-art-request"
    if not base.exists() and not base.is_symlink():
        return None
    if base.is_symlink() or not base.is_dir():
        raise VideoForgeError("PRODUCTION_ART_ARCHIVE_ROOT_UNSAFE")
    found=[]
    for run in sorted(base.iterdir()):
        if run.is_symlink():
            raise VideoForgeError("PRODUCTION_ART_ARCHIVE_RUN_SYMLINK")
        if not run.is_dir() or not run.name.isdigit():
            continue
        filename=asset_id+".png"
        image=run/filename
        manifest=run/"manifesto-geracoes.json"
        if image.is_symlink() or manifest.is_symlink():
            raise VideoForgeError("PRODUCTION_ART_ARCHIVE_SOURCE_SYMLINK")
        if not image.exists() and not manifest.exists():
            continue
        if not manifest.is_file():
            if image.exists():
                raise VideoForgeError("PRODUCTION_ART_ARCHIVE_MISSING_MANIFEST_BLOCK_REPEAT")
            continue
        try:
            obj=json.loads(manifest.read_text(encoding="utf-8"))
        except (ValueError,OSError,UnicodeError):
            raise VideoForgeError("PRODUCTION_ART_ARCHIVE_MANIFEST_INVALID_BLOCK_REPEAT") from None
        if (not isinstance(obj,dict) or
                obj.get("schema")!="videoforge/permanent-generated-image-archive/v1" or
                obj.get("channel")!=channel or
                obj.get("video_id")!=video_id or
                obj.get("producer")!="production-art-request" or
                obj.get("github_run_id")!=int(run.name) or
                not isinstance(obj.get("images"),list)):
            raise VideoForgeError("PRODUCTION_ART_ARCHIVE_MANIFEST_ORIGIN_INVALID_BLOCK_REPEAT")
        matches=[item for item in obj["images"] if isinstance(item,dict)
                 and item.get("file")==filename]
        if not matches and not image.exists():
            continue
        if len(matches)!=1 or not image.is_file():
            raise VideoForgeError("PRODUCTION_ART_ARCHIVE_INCOMPLETE_BLOCK_REPEAT")
        item=matches[0]
        try:
            data=image.read_bytes()
            digest=hashlib.sha256(data).hexdigest()
            info=png_info(data)
        except (OSError,ValueError):
            raise VideoForgeError("PRODUCTION_ART_ARCHIVE_INVALID_PNG_BLOCK_REPEAT") from None
        if (digest!=item.get("sha256") or
                info["width"]!=item.get("width") or
                info["height"]!=item.get("height") or
                len(data)!=item.get("bytes")):
            raise VideoForgeError("PRODUCTION_ART_ARCHIVE_SHA_OR_DIMENSIONS_MISMATCH_BLOCK_REPEAT")
        found.append({
            "asset_id":asset_id,
            "run_id":int(run.name),
            "path":str(image.relative_to(episode)).replace("\\","/"),
            "sha256":digest,"width":info["width"],"height":info["height"],
            "bytes":len(data),"human_visual_approved":False,
        })
    return max(found,key=lambda item:item["run_id"]) if found else None


def create_image(channel:str,video_id:str,asset_id:str,url:str,
                 model:str="gpt-image-2")->dict:
    image_generation_policy.assert_image_generation_allowed(channel,video_id)
    plan,story=read_plan(channel,video_id)
    budget=plan.get("request_limit",{})
    if budget.get("per_run")!=1 or budget.get("strict_budget",0)<1:
        raise VideoForgeError("PRODUCTION_ART_BUDGET_INVALID")
    if not isinstance(asset_id,str) or not IDENTIFIER.fullmatch(asset_id):
        raise VideoForgeError("PRODUCTION_ART_ID_INVALID")
    prompt,size=asset_prompt(plan,story,asset_id)
    if model not in proxy_images.IMAGE_MODELS:
        raise VideoForgeError("PRODUCTION_ART_MODEL_INVALID")
    if archived_reference(channel,video_id,asset_id) is not None:
        raise VideoForgeError("PRODUCTION_ART_ALREADY_ARCHIVED_SHA_VERIFIED")
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
    dimension_qa=inspect_generated_dimensions(info,size)
    sha=hashlib.sha256(blob).hexdigest()
    result={"schema":"videoforge/production-art-result/v1",
            "channel":channel,"video_id":video_id,
            "asset_id":asset_id,"file":str(output.relative_to(ROOT)),
            "size":size,"sha256":sha,
            "model":model,**dimension_qa,
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
