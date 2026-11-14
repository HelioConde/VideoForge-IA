"""Gerar uma cena anime real a partir de referencia visual persistida em artifact.

Executado SOMENTE dentro do VideoForge/Actions, via proxy do projeto.
Um request por run, sem retries e sem cenas artificiais. Roteiro/art bible
e hashes são obrigatórios, as 16 cenas mantêm a mesma referencia.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from . import proxy_images as proxy
from .errors import VideoForgeError
from .production_art import read_plan
from .scene_layers import png_info

ROOT=Path(__file__).resolve().parents[1]


def scene_prompt(channel:str,video_id:str,number:int)->tuple[str,dict]:
    plan,story=read_plan(channel,video_id)
    scenes=story["scenes"]
    if type(number) is not int or number<1 or number>len(scenes):
        raise VideoForgeError("PRODUCTION_SCENE_NUMBER_INVALID")
    scene=scenes[number-1]
    if not isinstance(scene,dict) or scene.get("number")!=number:
        raise VideoForgeError("PRODUCTION_SCENE_ORDER_INVALID")
    guide=plan.get("scene_prompt_template","")
    if not isinstance(guide,str) or not guide:
        raise VideoForgeError("PRODUCTION_SCENE_TEMPLATE_MISSING")
    try:
        prompt=guide.format(
            visual_direction=scene["visual_direction"],
            story_goal=scene["story_goal"],
        )
    except (KeyError,ValueError) as exc:
        raise VideoForgeError("PRODUCTION_SCENE_PROMPT_INVALID") from exc
    bible=plan.get("character_bible")
    if not isinstance(bible,dict) or not all(
        isinstance(bible.get(name),str) for name in ("anya","loid","yor")
    ):
        raise VideoForgeError("PRODUCTION_SCENE_BIBLE_MISSING")
    suffix="\n".join([
        "A PRANCHA anexada e a referencia unica de design; nao copie o fundo.",
        "Direcao de arte: "+plan["style"],
        "Loid: "+bible["loid"],
        "Yor: "+bible["yor"],
        "Anya: "+bible["anya"],
        "Mensagem da cena: "+scene["narration"],
        "Imagem de cena completa, NUNCA cartao, poster ou fluxograma.",
        "Composicao vertical sem texto ou marca d'agua, area de legenda livre.",
    ])
    prompt=prompt+"\n"+suffix
    if len(prompt)>5000:
        raise VideoForgeError("PRODUCTION_SCENE_PROMPT_TOO_LONG")
    return prompt,scene


def reference_bytes(image:Path,report:Path)->tuple[bytes,str]:
    if any(p.is_symlink() or not p.is_file() or not p.stat().st_size for p in (image,report)):
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_MISSING")
    try:
        metadata=json.loads(report.read_text(encoding="utf-8"))
    except (ValueError,OSError) as exc:
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_REPORT_INVALID") from exc
    raw=image.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if (metadata.get("sha256")!=digest or metadata.get("asset_id")!="character-bible"
        or metadata.get("official_video_created") is not False):
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_SHA_MISMATCH")
    dimensions=png_info(raw)
    if (dimensions["width"],dimensions["height"])!=(1024,1536):
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_SIZE_MISMATCH")
    return raw,digest


def generate_scene(channel:str,video_id:str,number:int,reference:Path,
                   report:Path,url:str,model:str="gpt-image-2")->dict:
    prompt,scene=scene_prompt(channel,video_id,number)
    if model not in proxy.IMAGE_MODELS:
        raise VideoForgeError("PRODUCTION_SCENE_MODEL_INVALID")
    source,source_sha=reference_bytes(reference,report)
    scene_id=f"cena-{number:02d}"
    target=proxy.destination(channel,video_id,scene_id).with_suffix(".png")
    if target.exists() or target.is_symlink():
        raise VideoForgeError("PRODUCTION_SCENE_ALREADY_EXISTS")
    response=proxy.call_proxy(url,"/v1/images/edits",
        os.getenv("CODEX_PROXY_API_KEY",""),{
            "model":model,"prompt":prompt,"n":1,"size":"1024x1536",
            "background":"opaque","output_format":"png",
            "response_format":"b64_json","stream":False,
            "input_fidelity":"high",
            "images":[{"image_url":"data:image/png;base64,"+
                       base64.b64encode(source).decode("ascii")}],
        })
    blob,extension=proxy.decode_image(response)
    if extension!=".png":
        raise VideoForgeError("PRODUCTION_SCENE_PNG_REQUIRED")
    info=png_info(blob,require_alpha=False)
    if (info["width"],info["height"])!=(1024,1536):
        raise VideoForgeError("PRODUCTION_SCENE_DIMENSIONS_INVALID")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(blob)
    result={
        "schema":"videoforge/production-scene/v1",
        "channel":channel,"video_id":video_id,
        "number":number,"scene":scene["id"],
        "reference_sha256":source_sha,"sha256":hashlib.sha256(blob).hexdigest(),
        "model":model,"size":"1024x1536","technical_qa":"valid_png_opaque",
        "visual_consistency_review":"pending","layers_generated":False,
        "mp4_generated":False,"youtube_uploaded":False,
    }
    target.with_suffix(".production.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main()->int:
    p=argparse.ArgumentParser(description="Generate real, reference-consistent scene via VideoForge")
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--number",required=True,type=int)
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--reference-report",type=Path,required=True)
    p.add_argument("--url",required=True)
    p.add_argument("--model",default="gpt-image-2")
    a=p.parse_args()
    try:
        result=generate_scene(a.channel,a.video_id,a.number,a.reference,
                              a.reference_report,a.url,a.model)
        print("PRODUCTION_SCENE_OK",json.dumps(result,ensure_ascii=False))
        return 0
    except (VideoForgeError,proxy.ProxyImageError,ValueError,OSError) as exc:
        print("PRODUCTION_SCENE_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
