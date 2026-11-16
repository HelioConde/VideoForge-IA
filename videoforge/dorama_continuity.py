"""Reutiliza bytes da imagem-mãe aprovada por estética, sem reconstruí-la por texto.

Valida identidade de canal/episódio, proveniência, SHA e pertencimento do
elenco à âncora. Somente PNG original do GitHub vira entrada real de edit.
Não transforma opinião de estilo em aprovação automática de máscara ou vídeo.
"""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE
from .scene_layers import png_info

REGISTRY="CONTINUIDADE-VISUAL-APROVADA-C01-P04.json"
STYLE="cinematic-semi-realistic-fantasy-anime"
MODE="dorama-approved-shot-anchor-v1"


def _file(ep:Path,rel:str):
    if not isinstance(rel,str) or "\\" in rel:
        raise VideoForgeError("CONTINUITY_UNSAFE_PATH")
    q=Path(rel)
    if q.is_absolute() or ".." in q.parts or not q.parts or not rel.startswith("assets/"):
        raise VideoForgeError("CONTINUITY_UNSAFE_PATH")
    target=ep/q
    if target.is_symlink() or not target.is_file() or target.stat().st_size>16_000_000:
        raise VideoForgeError("CONTINUITY_ORIGINAL_MISSING")
    return target


def reference(root:Path=ROOT):
    ep=Path(root)/EPISODE
    path=ep/REGISTRY
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("CONTINUITY_REGISTRY_MISSING")
    data=json.loads(path.read_text(encoding="utf-8"))
    if (data.get("schema")!="videoforge/approved-visual-continuity-anchor/v1"
        or data.get("channel")!="alchemy-lab"
        or data.get("episode")!="mmorpg-conquiste-a-princesa-ep01"
        or data.get("source_shot_id")!="C01-P04"
        or data.get("style_id")!=STYLE
        or data.get("approved_for_future_image_reference") is not True
        or data.get("limitations",{}).get("generation_must_attach_exact_original_png_bytes") is not True):
        raise VideoForgeError("CONTINUITY_ANCHOR_NOT_APPROVED")
    image=_file(ep,data["image_path"])
    report=json.loads(_file(ep,data["source_report_path"]).read_text(encoding="utf-8"))
    manifest=json.loads(_file(ep,data["source_archive_manifest"]).read_text(encoding="utf-8"))
    raw=image.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    info=png_info(raw)
    expected=(data["width"],data["height"])
    if (sha!=data.get("sha256")
        or (info["width"],info["height"])!=expected
        or report.get("sha256")!=sha
        or report.get("candidate_scene_shot_id")!="C01-P04"
        or report.get("youtube_uploaded") is not False
        or manifest.get("producer")!="production-art-request"
        or manifest.get("github_run_id")!=data.get("source_github_run")
        or len(manifest.get("images",[]))!=1
        or manifest["images"][0].get("sha256")!=sha
        or manifest["images"][0].get("width")!=expected[0]
        or manifest["images"][0].get("height")!=expected[1]):
        raise VideoForgeError("CONTINUITY_ANCHOR_SHA_MISMATCH")
    if not isinstance(data.get("characters_present"),list) or len(data["characters_present"])!=4:
        raise VideoForgeError("CONTINUITY_CAST_INVALID")
    return data,raw


def edit_payload(asset:dict, prompt:str, model:str, size:str, root:Path=ROOT):
    if asset.get("source_mode")!=MODE or asset.get("source_shot_id")!="C01-P04":
        raise VideoForgeError("CONTINUITY_SOURCE_MODE_INVALID")
    data,raw=reference(root)
    if (asset.get("source_continuity_registry")!=REGISTRY
        or asset.get("required_source_sha256")!=data["sha256"]
        or asset.get("reference_sources")!=[data["image_path"]]
        or model!="gpt-image-2" or size!="1024x1536"
        or not isinstance(prompt,str) or len(prompt)<200):
        raise VideoForgeError("CONTINUITY_REQUEST_MISMATCH")
    from .cinematic_direction import load_active_remake_plan
    plan=load_active_remake_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
    if not isinstance(plan,dict) or not isinstance(plan.get("shots"),list):
        raise VideoForgeError("CONTINUITY_SHOT_PLAN_MISSING")
    shots=[s for s in plan["shots"] if s.get("shot_id")==asset.get("shot_id")]
    if len(shots)!=1 or asset["shot_id"]=="C01-P04":
        raise VideoForgeError("CONTINUITY_SHOT_NOT_DISTINCT")
    cast=set(shots[0].get("cast",[]))
    if not cast or not cast.issubset(set(data["characters_present"])):
        raise VideoForgeError("CONTINUITY_CAST_NOT_IN_SOURCE")
    if cast!=set(asset.get("identity_cast",[])):
        raise VideoForgeError("CONTINUITY_REQUEST_CAST_MISMATCH")
    payload={"model":model,"prompt":prompt,"size":size,"n":1,
             "background":"opaque","output_format":"png",
             "response_format":"b64_json","stream":False,
             "images":[{"image_url":"data:image/png;base64,"+
                        base64.b64encode(raw).decode("ascii")}]}
    provenance=[{"actor":"scene-anchor-C01-P04","id":"approved-visual-reference",
                 "path":data["image_path"],"sha256":data["sha256"],
                 "source_shot_id":"C01-P04",
                 "source_style_approved":True}]
    return payload,provenance
