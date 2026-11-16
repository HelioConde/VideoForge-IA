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
from . import image_generation_policy, cinematic_direction
from .production_art import read_plan
from .scene_layers import png_info

ROOT=Path(__file__).resolve().parents[1]


def scene_prompt(channel:str,video_id:str,number:int,shot_id:str|None=None)->tuple[str,dict]:
    plan,story=read_plan(channel,video_id)
    scenes=story["scenes"]
    if type(number) is not int or number<1 or number>len(scenes):
        raise VideoForgeError("PRODUCTION_SCENE_NUMBER_INVALID")
    scene=scenes[number-1]
    if not isinstance(scene,dict) or scene.get("number")!=number:
        raise VideoForgeError("PRODUCTION_SCENE_ORDER_INVALID")
    cinematic=cinematic_direction.resolve_shot(channel,video_id,number,shot_id)
    # O template legado foi escrito para corpos inteiros. Em close de olhos,
    # cortar cabelo/ombro é uma decisão de câmera válida; usar outro template.
    # Cada tomada ganha imagem-mãe distinta antes de sprites/rig.
    if cinematic is not None:
        guide=("Um único frame de dorama MMORPG 2D, uma tomada de câmera cinematográfica; "
               "não criar pôster, montagem, múltiplos quadros nem grupo de personagens se não pedido. "
               "{visual_direction} "
               "Contexto narrativo: {story_goal} "
               "O enquadramento pode cortar intencionalmente cabelo, corpo ou cenário "
               "quando o plano é close de rosto/olhos. Nunca cortar a expressão ou "
               "deformar olhos, mãos, boca, anatomia nem o objeto focal. "
               "Preservar identidade e luz entre planos do mesmo local. "
               "Nenhuma UI ou texto pintado. Arte vertical com área segura para 9:16.")
    else:
        guide=plan.get("scene_prompt_template","")
    if not isinstance(guide,str) or not guide:
        raise VideoForgeError("PRODUCTION_SCENE_TEMPLATE_MISSING")
    try:
        prompt=guide.format(
            visual_direction=(cinematic_direction.prompt_direction(cinematic) if cinematic else scene["visual_direction"]),
            story_goal=(f"Tomada individual {cinematic['id']} deste episodio; manter evento, local e cronologia." if cinematic else scene["story_goal"]),
        )
    except VideoForgeError:
        # Quadros pretos e planos invalidados precisam manter erro explícito.
        raise
    except (KeyError,ValueError) as exc:
        raise VideoForgeError("PRODUCTION_SCENE_PROMPT_INVALID") from exc
    bible=plan.get("character_bible")
    if not isinstance(bible,dict) or not 1<=len(bible)<=12 or any(
        not isinstance(name,str) or not name.isidentifier()
        or not isinstance(description,str) or not 15<=len(description)<=600
        for name,description in bible.items()
    ):
        raise VideoForgeError("PRODUCTION_SCENE_BIBLE_MISSING")
    # Para vídeos com elenco explícito, NÃO enviar descrição de
    # personagens fora do enquadramento. Mantém formato legado Spy Family.
    cast=scene.get("reference_cast") if cinematic is None else list(cinematic_direction.canon_cast_for_shot(cinematic,bible)[0])
    if cast is not None:
        if (not isinstance(cast,list) or (not cast and cinematic is None) or len(cast)>len(bible)
                or len(set(cast))!=len(cast)
                or any(not isinstance(name,str) or name not in bible for name in cast)):
            raise VideoForgeError("PRODUCTION_SCENE_CAST_INVALID")
        ordering=tuple(cast)
        absent=[name for name in bible if name not in cast]
    else:
        ordering=("loid","yor","anya") if {"loid","yor","anya"}<=set(bible) else tuple(bible)
        absent=[]
    character_lines=[name.title()+": "+bible[name] for name in ordering]
    exclusion=("Personagens PROIBIDOS neste quadro, apesar de aparecerem na prancha: "
               +", ".join(absent)+". Nunca desenhar estes rostos, roupas, sombras, reflexos ou silhuetas."
               if absent else "")
    suffix="\n".join([
        "A PRANCHA anexada e referencia de IDENTIDADE, NAO de COMPOSICAO.",
        "Direcao de arte: "+plan["style"],
        *character_lines,
        "Desenhar SOMENTE as figuras presentes na direcao visual.",
        *(["Nao repetir cartaz: camera, lente e foco devem ser especificos desta tomada.",
           "Close ou over-the-shoulder exige imagem-mae propria: jamais zoom do rosto minusculo de um plano geral.",
           "Separar camadas RGBA da propria imagem-mae para rig real, nao pan/zoom de PNG."] if cinematic else []),
        exclusion,
        "Mensagem da cena: "+str(scene.get("narration","")),
        "NUNCA desenhar personagens ausentes do enquadramento descrito.",
        "Imagem de cena completa, NUNCA cartao, poster ou fluxograma.",
        "Composicao vertical sem texto ou marca d'agua, area de legenda livre.",
    ])
    prompt=prompt+"\n"+suffix
    if len(prompt)>5000:
        raise VideoForgeError("PRODUCTION_SCENE_PROMPT_TOO_LONG")
    return prompt,scene


def reference_bytes(image:Path,report:Path,allow_grounded:bool=False)->tuple[bytes,str]:
    if any(p.is_symlink() or not p.is_file() or not p.stat().st_size for p in (image,report)):
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_MISSING")
    try:
        metadata=json.loads(report.read_text(encoding="utf-8"))
    except (ValueError,OSError) as exc:
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_REPORT_INVALID") from exc
    raw=image.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    allowed={"character-bible","character-bible-grounded"} if allow_grounded else {"character-bible"}
    if (metadata.get("sha256")!=digest or metadata.get("asset_id") not in allowed
        or metadata.get("official_video_created") is not False):
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_SHA_MISMATCH")
    if metadata.get("asset_id")=="character-bible-grounded":
        from .grounded_identity import EXPECTED
        expected=[{"actor":actor,"id":sid,"path":path,"sha256":source_sha}
                  for actor,(sid,path,source_sha) in EXPECTED.items()]
        if (metadata.get("source_images_attached_to_request")!=2
                or metadata.get("source_originals_sha_verified")!=expected):
            raise VideoForgeError("PRODUCTION_SCENE_GROUNDED_INPUT_PROOF_MISSING")
    dimensions=png_info(raw)
    width,height=dimensions["width"],dimensions["height"]
    if allow_grounded:
        valid=512<=width<=2048 and 512<=height<=3072 and width<=height
    else:
        valid=(width,height)==(1024,1536)
    if not valid:
        raise VideoForgeError("PRODUCTION_SCENE_REFERENCE_SIZE_MISMATCH")
    return raw,digest


def generate_scene(channel:str,video_id:str,number:int,reference:Path,
                   report:Path,url:str,model:str="gpt-image-2",
                   shot_id:str|None=None)->dict:
    image_generation_policy.assert_image_generation_allowed(channel,video_id)
    cinematic_direction.assert_shot_generation_ready(channel,video_id)
    prompt,scene=scene_prompt(channel,video_id,number,shot_id)
    if model not in proxy.IMAGE_MODELS:
        raise VideoForgeError("PRODUCTION_SCENE_MODEL_INVALID")
    remake=cinematic_direction.load_active_remake_plan(channel,video_id) is not None
    source,source_sha=reference_bytes(reference,report,allow_grounded=remake)
    cinematic_direction.assert_scene_reference_matches_anchor(channel,video_id,source_sha)
    scene_id=f"cena-{number:02d}" + (f"-{shot_id.lower()}" if shot_id else "")
    target=proxy.destination(channel,video_id,scene_id).with_suffix(".png")
    if target.exists() or target.is_symlink():
        raise VideoForgeError("PRODUCTION_SCENE_ALREADY_EXISTS")
    response=proxy.call_proxy(url,"/v1/images/edits",
        os.getenv("CODEX_PROXY_API_KEY",""),{
            "model":model,"prompt":prompt,"n":1,"size":"1024x1536",
            "background":"opaque","output_format":"png",
            "response_format":"b64_json","stream":False,
            # gpt-image-2 rejects input_fidelity; use actual input PNG without it.
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
        "shot_id":shot_id,"shot_specific":shot_id is not None,
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
    p.add_argument("--shot-id",default=None,help="Tomada individual CXX-PXX, opcional")
    a=p.parse_args()
    try:
        result=generate_scene(a.channel,a.video_id,a.number,a.reference,
                              a.reference_report,a.url,a.model,a.shot_id)
        print("PRODUCTION_SCENE_OK",json.dumps(result,ensure_ascii=False))
        return 0
    except (VideoForgeError,proxy.ProxyImageError,ValueError,OSError) as exc:
        print("PRODUCTION_SCENE_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
