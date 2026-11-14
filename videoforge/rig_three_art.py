"""Prepare real candidate head/body sprites from the SAME character art.

Uses VideoForge Codex Proxy only. Every sprite retains SHA provenance.
Outputs are CANDIDATES, never rig approval. No auto-publish, no private mode.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from . import proxy_images, scene_layers
from .errors import VideoForgeError
from .animation_manual import enforce_animation_manual

SCHEMA="videoforge/rig-three-art-plan/v1"
ROOT=Path(__file__).resolve().parents[1]
MANUAL=ROOT/"docs"/"MANUAL-PRINCIPAL-ANIMACAO-2D.md"
PARTS=("head-open","body-no-head")


def _sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_plan(channel:str,video_id:str)->dict:
    enforce_animation_manual()
    if not MANUAL.is_file() or not MANUAL.read_text(encoding="utf-8").startswith(
            "# MANUAL PRINCIPAL DE ANIMAÇÃO 2D"):
        raise VideoForgeError("RIG_ART_CANONICAL_MANUAL_REQUIRED")
    model=ROOT/"modelos"/"camadas-animadas"/"modelo.json"
    config=json.loads(model.read_text(encoding="utf-8"))
    if (config.get("manual_principal")!="docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md" or
            config.get("regra_principal_animacoes_obrigatoria") is not True):
        raise VideoForgeError("RIG_ART_MODEL_MUST_USE_MAIN_MANUAL")
    plan_path=ROOT/"canal"/channel/"videos"/video_id/"rig-three-art-plan.json"
    if not plan_path.is_file() or plan_path.is_symlink():
        raise VideoForgeError("RIG_ART_PLAN_MISSING")
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    if (plan.get("schema")!=SCHEMA or
        plan.get("canonical_manual")!="docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md" or
        plan.get("channel")!=channel or plan.get("video_id")!=video_id or
        plan.get("scene")!="cena-01" or
        plan.get("canvas")!={"width":1024,"height":1536} or
        plan.get("max_new_image_calls")!=2 or plan.get("retry_on_429") is not False or
        plan.get("workflow_mode")!="normal_push_no_private" or
        plan.get("humanReview",{}).get("roundTripComposition") is not False):
        raise VideoForgeError("RIG_ART_PLAN_MUST_BE_GUARDED")
    steps=plan.get("steps")
    if not isinstance(steps,list) or [x.get("id") for x in steps]!=list(PARTS):
        raise VideoForgeError("RIG_ART_STEPS_INVALID")
    return plan


def check_source(source_dir:Path,plan:dict)->bytes:
    m=scene_layers._read_manifest(source_dir/"manifest.json")
    if (m.get("channel"),m.get("video_id"),m.get("scene"))!=(
            plan["channel"],plan["video_id"],plan["scene"]):
        raise VideoForgeError("RIG_ART_MANIFEST_WRONG_SOURCE")
    source=source_dir/plan["reference_file"]
    if not source.is_file() or source.is_symlink():
        raise VideoForgeError("RIG_ART_ORIGINAL_NOT_FOUND")
    raw=source.read_bytes()
    if (hashlib.sha256(raw).hexdigest()!=plan["reference_sha256"] or
        m.get("layers",{}).get("character-main",{}).get("sha256")!=plan["reference_sha256"] or
        m.get("source",{}).get("sha256")!=plan["scene_mother_sha256"]):
        raise VideoForgeError("RIG_ART_REFERENCE_SHA_MISMATCH")
    img=scene_layers.png_info(raw,require_alpha=True)
    if (img["width"],img["height"])!=(1024,1536):
        raise VideoForgeError("RIG_ART_REFERENCE_SIZE_INVALID")
    return raw


def make_candidate(source_dir:Path,channel:str,video_id:str,part:str,
                   url:str,model:str,dest:Path)->dict:
    plan=load_plan(channel,video_id)
    if model!=plan.get("edit_model") or model not in proxy_images.IMAGE_MODELS:
        raise VideoForgeError("RIG_ART_MODEL_NOT_ALLOWED")
    if part not in PARTS:
        raise VideoForgeError("RIG_ART_UNEXPECTED_PART")
    source=check_source(source_dir,plan)
    step=next(v for v in plan["steps"] if v["id"]==part)
    roi=step.get("roi")
    if (not isinstance(roi,list) or len(roi)!=4 or
        not all(type(v) is int for v in roi) or
        not (0<=roi[0]<roi[2]<=1024 and 0<=roi[1]<roi[3]<=1536)):
        raise VideoForgeError("RIG_ART_ROI_INVALID")
    if not isinstance(step.get("prompt"),str) or len(step["prompt"])<250:
        raise VideoForgeError("RIG_ART_PROMPT_INCOMPLETE")
    dest.mkdir(parents=True,exist_ok=True)
    target=dest/step["output"]
    qa_file=dest/(part+".qa.json")
    if any(p.exists() or p.is_symlink() for p in (target,qa_file)):
        raise VideoForgeError("RIG_ART_CANDIDATE_ALREADY_EXISTS")
    request=(
        "REGRA PRINCIPAL DE ANIMACAO POR MALHA: edicao localizada da MESMA "
        "imagem fonte, NUNCA redesenho independente. "
        +step["prompt"]+
        " A saida deve conter apenas UM sprite RGBA8 com alfa transparente "
        "real fora da peca; nao incluir xadrez falso, fundo colorido, letras "
        "ou outros personagens; manter exatamente canvas 1024x1536. "
        "Este e um teste de recorte e reconstrucao, NAO renderizacao final."
    )
    result=proxy_images.call_proxy(
        url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),{
          "model":model,"prompt":request,
          "n":1,"size":"1024x1536",
          "background":"transparent","output_format":"png",
          "response_format":"b64_json","stream":False,"input_fidelity":"high",
          "images":[{"image_url":"data:image/png;base64,"+
                     base64.b64encode(source).decode("ascii")}],
        })
    blob,ext=proxy_images.decode_image(result)
    if ext!=".png":
        raise VideoForgeError("RIG_ART_OUTPUT_NOT_PNG")
    target.write_bytes(blob)
    try:
        info=scene_layers.png_info(blob,require_alpha=True)
        passed=(info["width"],info["height"])==(1024,1536)
    except scene_layers.LayerError as exc:
        passed=False
        info={"validation_error":str(exc)}
    report={
        "schema":"videoforge/rig-three-art-candidate/v1",
        "channel":channel,"video_id":video_id,"scene":"cena-01",
        "canonical_manual":plan["canonical_manual"],
        "part":part,"source_original_sha256":plan["reference_sha256"],
        "source_scene_mother_sha256":plan["scene_mother_sha256"],
        "output_file":target.name,
        "output_sha256":hashlib.sha256(blob).hexdigest(),
        "requested_roi_original_canvas":roi,
        "output_png_technical_status":"candidate_rgba_verified" if passed else "rejected_rgba_or_canvas",
        "png_info":info,
        "roundtrip_composition_qa":"pending",
        "no_duplicate_pixels_qa":"pending",
        "seam_and_hidden_anatomy_qa":"pending",
        "human_visual_approval":False,
        "rig_operational":False,
        "youtube_uploaded":False,
        "ai_image_calls":1,
    }
    qa_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RIG_ART_CANDIDATE_SAVED",json.dumps(report,ensure_ascii=False))
    return report


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--part",choices=PARTS,required=True)
    p.add_argument("--url",required=True)
    p.add_argument("--model",default="gpt-image-2")
    p.add_argument("--dest",type=Path,required=True)
    args=p.parse_args()
    try:
        report=make_candidate(args.source_dir,args.channel,args.video_id,args.part,
                              args.url,args.model,args.dest)
        # Return success even if AI ignored alpha; artifact must exist for diagnosis.
        # Rig validator will block any rejected candidate.
        return 0 if report["output_png_technical_status"]=="candidate_rgba_verified" else 3
    except (VideoForgeError,scene_layers.LayerError,proxy_images.ProxyImageError,
            OSError,ValueError,KeyError) as exc:
        print("RIG_ART_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
