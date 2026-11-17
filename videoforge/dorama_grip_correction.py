"""C01-P04 V4: edição por imagem real para corrigir lanças não seguradas.

Não atribuir aprovação de anatomia a um prompt ou ao SHA. Preserva a
referência visual V3 e exige revisão visual da nova pega mão-haste.
"""
from __future__ import annotations
import base64
import json
from pathlib import Path
from .dorama_continuity import reference, REGISTRY
from .remake_autopilot import ROOT, EPISODE
from .errors import VideoForgeError

ASSET="c01-p04-pegada-lancas-v4"
MODE="dorama-physical-spear-grip-correction-v1"

def batch_hold(root:Path=ROOT):
    ep=Path(root)/EPISODE
    p=ep/"EP01-40-TOMADAS-PRODUCAO.json"
    if p.is_symlink() or not p.is_file():
        raise VideoForgeError("SPEAR_GRIP_BATCH_STATUS_MISSING")
    obj=json.loads(p.read_text(encoding="utf-8"))
    h=obj.get("generation_hold") or {}
    if not (obj.get("schema")=="videoforge/episode-image-factory-plan/v1"
            and h.get("active") is True
            and h.get("replacement_candidate_asset")==ASSET
            and h.get("corrected_anchor_promoted") is False):
        raise VideoForgeError("SPEAR_GRIP_BATCH_HOLD_REQUIRED")
    return h

def block_batch(root:Path=ROOT):
    batch_hold(root)
    raise VideoForgeError("DORAMA_NEW_SHOTS_PAUSED_UNTIL_SPEAR_GRIP_FIXED")

def edit_payload(asset:dict,prompt:str,model:str,size:str,root:Path=ROOT):
    if (not isinstance(asset,dict) or asset.get("id")!=ASSET
        or asset.get("source_mode")!=MODE
        or asset.get("source_shot_id")!="C01-P04"
        or asset.get("shot_id")!="C01-P04"
        or asset.get("source_continuity_registry")!=REGISTRY
        or asset.get("physical_grip_required") is not True
        or asset.get("corrected_anchor_promotion_requires_human_review") is not True
        or asset.get("visual_approval") is not False
        or asset.get("youtube_upload") is not False):
        raise VideoForgeError("SPEAR_GRIP_CORRECTION_CONTRACT_INVALID")
    batch_hold(root)
    anchor,png=reference(root)
    if (asset.get("required_source_sha256")!=anchor["sha256"]
        or asset.get("reference_sources")!=[anchor["image_path"]]
        or model!="gpt-image-2" or size!="1024x1536"):
        raise VideoForgeError("SPEAR_GRIP_SOURCE_SHA_OR_MODEL_MISMATCH")
    if (not isinstance(prompt,str) or len(prompt)<350
        or "SEGURAM" not in prompt.upper()
        or "MÃOS" not in prompt.upper()
        or "DUAS LANÇAS" not in prompt.upper()):
        raise VideoForgeError("SPEAR_GRIP_CORRECTION_PROMPT_MISSING_CONTACT")
    payload={"model":model,"prompt":prompt,"size":size,"n":1,
             "background":"opaque","output_format":"png",
             "response_format":"b64_json","stream":False,
             "images":[{"image_url":"data:image/png;base64,"+
                        base64.b64encode(png).decode("ascii")}]}
    source=[{"actor":"tribunal","id":"approved-visual-reference",
             "path":anchor["image_path"],"sha256":anchor["sha256"],
             "source_shot_id":"C01-P04","source_style_approved":True,
             "source_spear_grip_approved":False}]
    return payload,source
