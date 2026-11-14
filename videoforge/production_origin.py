"""Portao de proveniencia: workflow experimental nao e producao oficial.

Este modulo verifica apenas os campos locais. Mesmo quando os campos
passarem, o revisor precisa conferir o run/artefato no proprio GitHub
e a qualidade humana; metadados autodeclarados nunca provam isso sozinhos.
"""
from __future__ import annotations

import json
from pathlib import Path

REPOSITORY = "HelioConde/VideoForge-IA"
OFFICIAL = "producao_oficial"
TECHNICAL_PREVIEW = "preview_tecnico_nao_oficial"
MANDATORY_STAGES = (
    "pesquisa",
    "roteiro",
    "geracao_arte",
    "separacao_camadas",
    "animacao",
    "narracao",
    "edicao",
    "qa_tecnico",
    "qa_visual",
)


class ProvenanceError(ValueError):
    """Registro nao pode ser anunciado como producao oficial."""


def validate_editorial_origin(editorial: dict) -> bool:
    """Retorna True somente quando ha comprovantes declarados completos.

    Registros experimentais continuam validos desde que identificados como
    tais. Run IDs e hashes sao referencias a verificar no GitHub, NAO
    certificacoes automaticas de identidade ou qualidade do video.
    """
    if not isinstance(editorial, dict) or not isinstance(editorial.get("producao"), dict):
        raise ProvenanceError("ORIGIN_MISSING_PRODUCTION_RECORD")
    production = editorial["producao"]
    classification = production.get("classificacao", TECHNICAL_PREVIEW)
    official = production.get("video_oficial_do_programa", False)
    if not isinstance(official, bool):
        raise ProvenanceError("ORIGIN_OFFICIAL_FLAG_MUST_BE_BOOL")
    if not official:
        if classification == OFFICIAL:
            raise ProvenanceError("ORIGIN_PREVIEW_MISLABELED_OFFICIAL")
        return False
    if classification != OFFICIAL:
        raise ProvenanceError("ORIGIN_OFFICIAL_REQUIRES_CLASSIFICATION")
    if production.get("programa_origem") != REPOSITORY:
        raise ProvenanceError("ORIGIN_OFFICIAL_REQUIRES_VIDEOFORGE_REPO")
    workflow = production.get("workflow_arquivo")
    if not isinstance(workflow, str) or not workflow.startswith(".github/workflows/") or not workflow.endswith(".yml"):
        raise ProvenanceError("ORIGIN_WORKFLOW_MISSING")
    if any(s in workflow.lower() for s in ("pilot", "preview", "smoke", "experimental", "spy-family-animated")):
        raise ProvenanceError("ORIGIN_EXPERIMENTAL_WORKFLOW_NOT_OFFICIAL")
    run = production.get("github_actions_run_id")
    if type(run) is not int or run <= 0:
        raise ProvenanceError("ORIGIN_WORKFLOW_RUN_MISSING")
    if production.get("workflow_url") != f"https://github.com/{REPOSITORY}/actions/runs/{run}":
        raise ProvenanceError("ORIGIN_RUN_URL_MISMATCH")
    artifact = production.get("artefato_url", "")
    if not isinstance(artifact, str) or not artifact.startswith(
            f"https://github.com/{REPOSITORY}/actions/runs/{run}/artifacts/"):
        raise ProvenanceError("ORIGIN_ARTIFACT_NOT_FROM_RUN")
    sha = production.get("sha256", "")
    if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
        raise ProvenanceError("ORIGIN_MP4_SHA256_MISSING")
    stages = production.get("etapas_comprovadas")
    if not isinstance(stages, dict) or any(
        not isinstance(stages.get(stage), dict) or
        stages[stage].get("status") != "verified" or
        not isinstance(stages[stage].get("evidence_url"), str) or
        not stages[stage]["evidence_url"].startswith(
            f"https://github.com/{REPOSITORY}/actions/runs/")
        for stage in MANDATORY_STAGES
    ):
        raise ProvenanceError("ORIGIN_PRODUCTION_STAGES_NOT_PROVEN")
    qa = editorial.get("qa", {})
    if qa.get("aprovado_tecnicamente") is not True or qa.get("aprovado_editorialmente") is not True:
        raise ProvenanceError("ORIGIN_QA_NOT_APPROVED")
    art = editorial.get("arte", {})
    if art.get("consistencia_verificada") is not True:
        raise ProvenanceError("ORIGIN_VISUAL_ART_NOT_APPROVED")
    # Regra nº 1: um MP4 com pan, mesmo com 16 imagens e boa narração,
    # NÃO é animação aprovada. Exigir provas por cena-mãe e partes RGBA.
    if (production.get("rig_animado_aplicado") is not True or
        production.get("animacao_motor") != "remotion-rig-rgba-scene-mother"):
        raise ProvenanceError("ORIGIN_ACTUAL_LAYERED_RIG_REQUIRED")
    story = editorial.get("roteiro", {})
    expected = story.get("cenas_previstas") if isinstance(story,dict) else None
    verified = production.get("cenas_animadas_verificadas")
    if (not isinstance(expected,list) or not expected or
        not isinstance(verified,list) or len(verified)!=len(expected)):
        raise ProvenanceError("ORIGIN_SCENE_MOTHER_COVERAGE_INCOMPLETE")
    for identifier,row in zip(expected,verified):
        if (not isinstance(identifier,str) or not isinstance(row,dict) or
            row.get("scene")!=identifier or
            row.get("scene_mother_sha256") is None or
            any(not isinstance(row.get(k),str) or len(row[k])!=64
                for k in ("scene_mother_sha256","background_sha256",
                          "characters_rgba_sha256")) or
            row.get("individual_character_parts_verified") is not True or
            row.get("all_movable_objects_separated") is not True or
            row.get("seam_and_opaque_face_qa") is not True or
            row.get("rig_motion_qa") is not True or
            row.get("human_visual_approval") is not True):
            raise ProvenanceError("ORIGIN_SCENE_MOTHER_RIG_EVIDENCE_INCOMPLETE")
    return True


def audit_repo(root: Path) -> int:
    scanned = 0
    for path in sorted(root.glob("canal/*/videos/*/editorial.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        validate_editorial_origin(record)
        scanned += 1
    return scanned


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(f"PROVENANCE_AUDIT_OK: {audit_repo(root)} editorial records")
