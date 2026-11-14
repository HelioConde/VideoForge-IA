"""Recorta personagens e objetos INDEPENDENTES da mesma cena-mae real.

Uma chamada de edicao por job, sem retries, sem figurinhas vetoriais e sem
rig/QA ficticios. A aprovacao visual permanece obrigatoriamente falsa.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from . import proxy_images, scene_layers, production_scene_layers
from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
SCHEMA="videoforge/rgba-part-extraction-plan/v1"
PART_RE=re.compile(r"^[a-z][a-z0-9-]{1,47}$")

def plan_entry(channel:str,video_id:str,scene_number:int,part_id:str)->dict:
    _,story,entry=production_scene_layers.read_plan(channel,video_id,scene_number)
    path=ROOT/"canal"/channel/"videos"/video_id/"production-parts-plan.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size>100_000:
        raise VideoForgeError("RGBA_PARTS_PLAN_MISSING")
    try: doc=json.loads(path.read_text(encoding="utf8"))
    except (ValueError,OSError) as exc: raise VideoForgeError("RGBA_PARTS_PLAN_INVALID") from exc
    if (doc.get("schema")!=SCHEMA or doc.get("channel")!=channel or
        doc.get("video_id")!=video_id or doc.get("scene_number")!=scene_number or
        doc.get("source_scene_id")!=entry["scene"] or
        doc.get("image_model") not in proxy_images.IMAGE_MODELS or
        doc.get("retry_on_429") is not False or
        doc.get("human_visual_approval") is not False):
        raise VideoForgeError("RGBA_PARTS_ORIGIN_INVALID")
    parts=doc.get("parts")
    if not isinstance(parts,list) or not parts or len(parts)>48:
        raise VideoForgeError("RGBA_PARTS_LIST_INVALID")
    if not isinstance(part_id,str) or not PART_RE.fullmatch(part_id):
        raise VideoForgeError("RGBA_PARTS_ID_INVALID")
    matches=[x for x in parts if isinstance(x,dict) and x.get("id")==part_id]
    if len(matches)!=1:
        raise VideoForgeError("RGBA_PARTS_UNKNOWN_ID_OR_DUPLICATE")
    selected=matches[0]
    if not isinstance(selected.get("prompt"),str) or not 150<=len(selected["prompt"])<=2800:
        raise VideoForgeError("RGBA_PARTS_PROMPT_INVALID")
    if (selected.get("source_sha256")!=doc.get("source_scene_sha256") or
        not re.fullmatch(r"[a-f0-9]{64}",doc.get("source_scene_sha256",""))):
        raise VideoForgeError("RGBA_PARTS_SHA_INVALID")
    return selected

def make_part(channel:str,video_id:str,scene_number:int,part_id:str,
              mother:Path,report:Path,url:str,model:str="gpt-image-2")->dict:
    entry=plan_entry(channel,video_id,scene_number,part_id)
    plan,_story,scene=production_scene_layers.read_plan(channel,video_id,scene_number)
    actual=production_scene_layers.validate_source(mother,report,scene,channel,video_id)
    if actual!=entry["source_sha256"]:
        raise VideoForgeError("RGBA_PARTS_SOURCE_SHA_MISMATCH")
    if model not in proxy_images.IMAGE_MODELS:
        raise VideoForgeError("RGBA_PARTS_MODEL_INVALID")
    folder=ROOT/"output"/channel/"videos"/video_id/"parts"/f"cena-{scene_number:02d}"
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/(part_id+".png")
    metadata=folder/(part_id+".qa.json")
    if target.exists() or target.is_symlink() or metadata.exists():
        raise VideoForgeError("RGBA_PARTS_DEST_ALREADY_EXISTS")
    prompt=(
      "Use a IMAGEM-MAE anexada como fonte OBRIGATORIA. Edicao LOCAL da mesma imagem "
      "e NUNCA ilustracao independente. "+entry["prompt"]+
      " Nao incluir ambiente, pisos, vitrais, trono, personagens ou armas fora "
      "da peca especifica. Preserve exatamente a pose, escala, cores, "
      "coordenadas do canvas 1024x1536 e anatomia presente. Se algo esta "
      "encoberto, reconstrua a anatomia sob a sobreposicao sem alterar a pose. "
      "Todos os pixels fora do alvo devem ser RGBA com alfa 0 real. "
      "NUNCA xadrez falso, sombra difusa do cenario, poster, texto, borda "
      "preta ou personagem inteiro quando pedido for prop. "
      "Aprovacao humana e recomposicao ainda obrigatorias."
    )
    if len(prompt)>4300: raise VideoForgeError("RGBA_PARTS_PROMPT_TOO_LONG")
    source=mother.read_bytes()
    data=proxy_images.call_proxy(url,"/v1/images/edits",
      os.getenv("CODEX_PROXY_API_KEY",""),{
        "model":model,"prompt":prompt,"n":1,"size":"1024x1536",
        "background":"transparent","output_format":"png",
        "response_format":"b64_json","stream":False,"input_fidelity":"high",
        "images":[{"image_url":"data:image/png;base64,"+
          base64.b64encode(source).decode("ascii")}],
      })
    blob,ext=proxy_images.decode_image(data)
    if ext!=".png": raise VideoForgeError("RGBA_PARTS_OUTPUT_NOT_PNG")
    target.write_bytes(blob)
    try:
        quality=scene_layers.png_info(blob,require_alpha=True)
        if (quality["width"],quality["height"])!=(1024,1536):
            raise VideoForgeError("RGBA_PARTS_OUTPUT_SIZE_INVALID")
        state="candidate_rgba_verified"
    except (scene_layers.LayerError,VideoForgeError) as exc:
        quality={"error":str(exc)}
        state="rejected_invalid_alpha_or_size"
    qa={"schema":"videoforge/rgba-part-candidate/v1","channel":channel,
       "video_id":video_id,"scene_number":scene_number,"part_id":part_id,
       "scene_mother_sha256":actual,"source_png":"cena-01.png",
       "output_sha256":hashlib.sha256(blob).hexdigest(),
       "technical_status":state,"png_info":quality,
       "roundtrip_diff":"pending","no_duplicate_pixels":"pending",
       "underlays_verified":False,"human_visual_approval":False,
       "rig_applied":False,"official_video":False,"youtube_uploaded":False}
    metadata.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("RGBA_PART_CANDIDATE",json.dumps(qa,ensure_ascii=False))
    return qa

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--number",type=int,required=True)
    p.add_argument("--part",required=True)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--source-report",type=Path,required=True)
    p.add_argument("--url",required=True)
    p.add_argument("--model",default="gpt-image-2")
    x=p.parse_args()
    try:
        out=make_part(x.channel,x.video_id,x.number,x.part,x.source,x.source_report,x.url,x.model)
        return 0 if out["technical_status"]=="candidate_rgba_verified" else 3
    except (VideoForgeError,scene_layers.LayerError,proxy_images.ProxyImageError,
            ValueError,OSError,KeyError) as exc:
        print("RGBA_PART_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
