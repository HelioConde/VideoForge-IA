"""Fail-closed priority gate for ALL official VideoForge animation workflows.

Old prototype code may remain as legacy previews, but cannot claim official
animated rig compliance without reading the user's canonical manual.
"""
from __future__ import annotations
import json
from pathlib import Path
from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
MANUAL_REL="docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md"
REQUIRED=(
    "Three.js","Remotion","imagem-mãe","PNG RGBA","body-no-head",
    "head-open","head-closed","recomposição","--gl=swangle",
    "não","pivô","malha",
)


def enforce_animation_manual(root:Path=ROOT)->dict:
    path=root/MANUAL_REL
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("ANIMATION_MANUAL_MISSING")
    contents=path.read_text(encoding="utf-8")
    if not contents.startswith("# MANUAL PRINCIPAL DE ANIMAÇÃO 2D"):
        raise VideoForgeError("ANIMATION_MANUAL_HEADER_INVALID")
    if any(term.lower() not in contents.lower() for term in REQUIRED):
        raise VideoForgeError("ANIMATION_MANUAL_INCOMPLETE")
    agents=root/"AGENTS.md"
    readme=root/"README.md"
    for item in (agents,readme):
        if not item.is_file() or MANUAL_REL not in item.read_text(encoding="utf-8")[:8000]:
            raise VideoForgeError("ANIMATION_MANUAL_NOT_TOP_PRIORITY_IN_"+item.name)
    model_path=root/"modelos"/"camadas-animadas"/"modelo.json"
    model=json.loads(model_path.read_text(encoding="utf-8"))
    if (model.get("manual_principal")!=MANUAL_REL or
        model.get("regra_principal_animacoes_obrigatoria") is not True or
        model.get("operacional") is not False or
        model.get("etapas",{}).get("animacao",{}).get("rig_individual_partes_implementado_para_spy_family") is True):
        raise VideoForgeError("ANIMATION_MANUAL_MODEL_POLICY_INVALID")
    return {
        "manual":MANUAL_REL,
        "policy":"rig_three_real_layers_only",
        "allows_flat_png_as_official":False,
        "user_visual_review_required":True,
        "no_private_workflow_mode":True,
    }
