"""C01-P02 shot-specific one-image editor for hand, blade, sheath, underlay.

Uses the existing VideoForge proxy client and permanent SHA archive. EXACTLY
one image API edit per authorized run; no auto-dispatch, retries or publication.
An image candidate is NOT a visually approved layer or rig.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from . import proxy_images, image_generation_policy
from .errors import VideoForgeError
from .scene_layers import png_info, LayerError
from .remake_autopilot import ROOT,EPISODE
from .remake_sword_pack import _find_mother,_find_part,PARTS,CH,VID,SHOT,UNDERLAY_PRODUCER,PART_PRODUCER
from .remake_sword_preview import canonical_anchor

SCHEMA = "videoforge/remake-sword-component-generation/v1"
PROMPTS={
  "underlay": (
    "Edite SOMENTE a imagem-mãe da tomada C01-P02 anexada. "
    "Recrie o FUNDO OPACO que fica atrás da mão enluvada do carrasco, "
    "da lâmina e da bainha da espada. Remova cada elemento móvel do fundo, "
    "reconstruindo o que estava oculto com a mesma iluminação, perspectiva, "
    "tons e textura originais. Não mantenha fantasmas, duplicações, bordas "
    "de máscara, linhas de espada nem sobras de mãos. "
    "Retorne a cena estática COMPLETA em PNG RGB opaco 1024x1536; "
    "nenhum texto, UI ou marca d'água. A revisão visual é obrigatória."
  ),
  "sheath": (
    "Use obrigatoriamente a imagem-mãe C01-P02 anexada. "
    "Extraia APENAS a BAINHA ORIGINAL da espada empunhada pelo CARRASCO, "
    "incluindo seu acabamento e detalhe visível. Nada de lâmina, mão, corpo, "
    "rei, Kael, trono, cenário ou sombras de ambiente. Reconstrua porções "
    "encobertas quando necessário mantendo cor/perspectiva. "
    "Preserve localização e escala da arte fonte no canvas RGBA 1024x1536. "
    "Fora da bainha todos os pixels devem possuir ALFA ZERO REAL, "
    "sem tabuleiro falso, sem contorno preto, sem texto."
  ),
  "blade": (
    "Use a mesma imagem-mãe original da tomada C01-P02 anexada. "
    "Extraia APENAS a LÂMINA metálica e a empunhadura ligada a ela "
    "desembainhada pelo CARRASCO. Nunca desenhe uma segunda espada, "
    "sangue, Kael, guardas, mão, bainha, trono ou fundo. "
    "Mantenha exatamente a perspectiva, cor, luz, brilho e localização "
    "do prop na imagem mãe 1024x1536. Complete partes escondidas apenas "
    "onde preciso para o movimento real do objeto. O resto do PNG "
    "deve ficar com alfa 0 real, sem texto/UI/moldura."
  ),
  "hand": (
    "Edite a imagem-mãe verdadeira C01-P02 anexada. "
    "Recorte APENAS a MÃO ENLUVADA e antebraço visível do CARRASCO "
    "que puxa a espada, preservando dedos, articulação do pulso, "
    "contato e manga correspondente. Nunca substituir pela mão de Kael, "
    "nem desenhar arma, bainha, fundo, guarda, rosto ou trono. "
    "Reconstrua palma e dedos encobertos coerentemente sem alterar "
    "tamanho/posição na composição original. PNG RGBA 1024x1536, "
    "transparência total fora da anatomia, sem efeito fake checkerboard."
  ),
}

def source_info(root:Path=ROOT,source_run_id:int=0)->dict:
    if type(source_run_id) is not int or source_run_id<=0:
        raise VideoForgeError("REMAKE_SWORD_SOURCE_RUN_ID_REQUIRED")
    anchor=canonical_anchor(root)
    episode=Path(root)/EPISODE
    mother=_find_mother(episode,anchor["sha256"])
    if mother is None:
        raise VideoForgeError("REMAKE_SWORD_SOURCE_MOTHER_NOT_ARCHIVED")
    if mother["run_id"]!=source_run_id:
        raise VideoForgeError("REMAKE_SWORD_SOURCE_RUN_ID_NOT_CURRENT")
    return {"mother":mother,"anchor":anchor}

def _reject_existing_component(part:str,mother:dict,root:Path)->None:
    """Never spend another edit on a SHA-verified, same-mother component.

    Fresh GitHub Actions runners have empty local output directories; only the
    permanent per-run archive can prevent duplicate paid generations.
    Rejected or invalid PNGs do not satisfy _find_part and may be retried after
    review according to the separate retry policy.
    """
    existing=_find_part(Path(root)/EPISODE,part,mother["sha256"],mother["run_id"])
    if existing is not None:
        raise VideoForgeError(
            f"REMAKE_SWORD_COMPONENT_ALREADY_ARCHIVED_SAME_MOTHER:{part}:run={existing['run_id']}"
        )


def preflight(part:str,source_run_id:int,root:Path=ROOT)->dict:
    if part not in PARTS:
        raise VideoForgeError("REMAKE_SWORD_UNKNOWN_COMPONENT")
    try:
        mother=source_info(root,source_run_id)["mother"]
        _reject_existing_component(part,mother,root)
        image_generation_policy.assert_image_generation_allowed(CH,VID,root)
    except VideoForgeError as exc:
        return {"schema":SCHEMA,"shot_id":SHOT,"part_id":part,
                "source_run_id":source_run_id,"ready":False,
                "blocked_reason":str(exc),"provider_calls_executed":0,
                "youtube_uploaded":False,"human_visual_approved":False}
    return {"schema":SCHEMA,"shot_id":SHOT,"part_id":part,
            "source_run_id":source_run_id,"ready":True,
            "blocked_reason":None,"provider_calls_executed":0,
            "youtube_uploaded":False,"human_visual_approved":False}

def produce(part:str,source_run_id:int,url:str,model:str="gpt-image-2",
            root:Path=ROOT)->dict:
    if part not in PARTS:
        raise VideoForgeError("REMAKE_SWORD_UNKNOWN_COMPONENT")
    # Provenance, deduplication and cost gates all run before the proxy/API.
    info=source_info(root,source_run_id)
    mother=info["mother"]
    _reject_existing_component(part,mother,root)
    image_generation_policy.assert_image_generation_allowed(CH,VID,root)
    if model not in proxy_images.IMAGE_MODELS:
        raise VideoForgeError("REMAKE_SWORD_MODEL_INVALID")
    original=mother["path"].read_bytes()
    digest=hashlib.sha256(original).hexdigest()
    if digest!=mother["sha256"]:
        raise VideoForgeError("REMAKE_SWORD_SOURCE_CHANGED")
    output=(Path(root)/"output"/CH/"videos"/VID/"sword-components"/
            "c01-p02"/part)
    target=output/(part+".png")
    report_path=output/(part+".qa.json")
    if output.is_symlink() or target.exists() or target.is_symlink() or report_path.exists() or report_path.is_symlink():
        raise VideoForgeError("REMAKE_SWORD_COMPONENT_ALREADY_EXISTS")
    original_prompt=PROMPTS[part]
    if not 150<=len(original_prompt)<=2800:
        raise VideoForgeError("REMAKE_SWORD_PROMPT_INVALID")
    background="opaque" if part=="underlay" else "transparent"
    response=proxy_images.call_proxy(url,"/v1/images/edits",
        os.getenv("CODEX_PROXY_API_KEY",""),{
          "model":model,"prompt":original_prompt,
          "n":1,"size":"1024x1536",
          "background":background,"output_format":"png",
          "response_format":"b64_json","stream":False,"input_fidelity":"high",
          "images":[{"image_url":"data:image/png;base64,"+
                     base64.b64encode(original).decode("ascii")}],
        })
    blob,ext=proxy_images.decode_image(response)
    if ext!=".png":
        raise VideoForgeError("REMAKE_SWORD_OUTPUT_NOT_PNG")
    file_hash=hashlib.sha256(blob).hexdigest()
    output.mkdir(parents=True,exist_ok=True)
    target.write_bytes(blob)  # Preserve even a technically invalid candidate.
    try:
        dims=png_info(blob,require_alpha=part!="underlay",
                      min_visible_fraction=.0002)
        if (dims["width"],dims["height"])!=(1024,1536):
            raise VideoForgeError("REMAKE_SWORD_COMPONENT_SIZE_INVALID")
        if part=="underlay" and dims["color_type"]!=2:
            raise VideoForgeError("REMAKE_SWORD_UNDERLAY_MUST_BE_OPAQUE_RGB8")
        status=("candidate_opaque_verified" if part=="underlay"
                else "candidate_rgba_verified")
    except (LayerError,VideoForgeError) as exc:
        dims={"error":str(exc)}
        status="rejected_png_or_alpha_invalid"
    qa={"schema":("videoforge/remake-underlay-candidate/v1" if part=="underlay"
                    else "videoforge/rgba-part-candidate/v1"),
        "channel":CH,"video_id":VID,"scene_number":1,"scene":"c01",
        "shot_id":SHOT,"part_id":part,
        "source_archive_producer":"production-scene-request",
        "source_archive_run_id":source_run_id,
        "scene_mother_sha256":digest,
        "output_sha256":file_hash,"technical_status":status,
        "png_info":dims,"human_visual_approval":False,
        "neutral_roundtrip":"pending","underlay_restoration_review":"pending",
        "rig_applied":False,"official_video":False,"youtube_uploaded":False,
        "api_edit_calls_executed":1,"image_generation_authorized_by_policy":True}
    report_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    return qa

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["preflight","produce"])
    ap.add_argument("--part",required=True,choices=PARTS)
    ap.add_argument("--source-run-id",type=int,required=True)
    ap.add_argument("--url",default="")
    ap.add_argument("--model",default="gpt-image-2")
    args=ap.parse_args()
    try:
        if args.action=="preflight":
            data=preflight(args.part,args.source_run_id)
        else:
            data=produce(args.part,args.source_run_id,args.url,args.model)
        print("REMAKE_SWORD_COMPONENT",json.dumps(data,ensure_ascii=False))
        return 0 if (args.action=="preflight" or
                     data["technical_status"].startswith("candidate_")) else 3
    except (VideoForgeError,proxy_images.ProxyImageError,LayerError,
            OSError,ValueError,KeyError) as exc:
        print("REMAKE_SWORD_COMPONENT_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
