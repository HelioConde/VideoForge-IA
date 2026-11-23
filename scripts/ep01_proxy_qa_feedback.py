"""Render an honest, cost-free GitHub Actions summary for one EP01 proxy image.

This runs after archival, even if generation failed. It never approves an asset,
retries a provider call, changes its pixels, or claims an archive commit succeeded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

CHANNEL = "alchemy-lab"
VIDEO = "mmorpg-conquiste-a-princesa-ep01"
SCHEMA = "videoforge/ep01-proxy-separate-part/v1"
PART_RE = re.compile(r"background-clean|character-[a-z0-9_-]+|object-[a-z0-9_-]+", re.ASCII)
SHOT_RE = re.compile(r"C[0-9]{2}-P[0-9]{2}", re.ASCII)


def _clean(value: object) -> str:
    """Avoid turning untrusted model metadata into Markdown, links or markup."""
    return re.sub(r"[\r\n|<>\x60\[\]]", " ", str(value))[:170]


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def _canvas(value: object) -> str:
    if (not isinstance(value, list) or len(value) != 2
            or any(type(v) is not int or v <= 0 or v > 16384 for v in value)):
        raise ValueError("invalid source/provider canvas")
    return f"{value[0]} × {value[1]}"


def inspect(image_dir: Path, shot: str, part: str) -> tuple[str, bool]:
    """Return Markdown summary and integrity-check success (no external calls)."""
    if not SHOT_RE.fullmatch(shot) or not PART_RE.fullmatch(part):
        raise ValueError("invalid shot or part")
    stem = f"{shot.lower()}-{part}"
    source = image_dir / (stem + ".png")
    metadata = image_dir / (stem + ".production.json")
    heading = f"## EP01 — imagem separada {shot} / {part}\n\n"
    if not source.exists() and not metadata.exists():
        return (heading + "**Sem PNG/relatório produzido nesta execução.** Consulte a etapa de geração "
                "para o motivo da falha. Nenhuma imagem foi aprovada ou deve ser repetida "
                "automaticamente.\n", True)
    if (not source.is_file() or source.is_symlink() or not metadata.is_file()
            or metadata.is_symlink() or metadata.stat().st_size > 1_000_000):
        return (heading + "**Erro de integridade:** PNG e metadados válidos devem existir "
                "juntos. Não promover este arquivo.\n", False)
    try:
        info = json.loads(metadata.read_text(encoding="utf-8"))
        if (not isinstance(info, dict) or info.get("schema") != SCHEMA
                or info.get("channel") != CHANNEL or info.get("video_id") != VIDEO
                or info.get("candidate_scene_shot_id") != shot
                or info.get("component") != part or info.get("asset_id") != stem
                or info.get("generation_method") != "proxy_generated_separate_image"
                or type(info.get("provider_image_calls")) is not int
                or info["provider_image_calls"] != 1
                or info.get("human_visual_approval") is not False
                or info.get("rig_ready") is not False
                or info.get("youtube_uploaded") is not False):
            raise ValueError("metadata provenance or safety gate mismatch")
        sha = info.get("sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError("invalid SHA")
        if _digest(source) != sha:
            raise ValueError("PNG SHA-256 mismatch")
        expected = _canvas(info.get("source_canvas"))
        actual = _canvas(info.get("provider_canvas"))
        qa = info.get("technical_qa")
        if not isinstance(qa, str) or not re.fullmatch(r"[a-z0-9_]{3,120}", qa):
            raise ValueError("invalid technical QA status")
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return (heading + f"**Erro de integridade:** {_clean(exc)}. "
                "Arte, rig e publicação bloqueados.\n", False)
    if qa.startswith("rejected_"):
        verdict = "Reprovada no QA técnico — PNG preservado localmente"
    elif qa.startswith("candidate_"):
        verdict = "Candidata para revisão — NÃO aprovada"
    else:
        verdict = "Estado de QA desconhecido — bloqueado"
    rows = [
        ("Resultado", verdict),
        ("QA técnico", qa),
        ("Canvas da imagem-mãe", expected),
        ("Canvas recebido", actual),
        ("SHA-256 recebido", sha),
        ("Chamadas informadas pelo gerador", "1"),
        ("Aprovação visual / rig / YouTube", "não / não / não"),
    ]
    table = "| Campo | Valor |\n|---|---|\n" + "".join(
        f"| {_clean(k)} | {_clean(v)} |\n" for k, v in rows)
    if qa == "rejected_canvas_mismatch_no_pixel_resizing" and expected != actual:
        if (info["source_canvas"] == list(reversed(info["provider_canvas"]))):
            advice = ("**Causa provável:** o provedor devolveu a orientação trocada "
                      "(largura e altura invertidas). Corrigir o contrato/prompt em uma "
                      "nova versão revisada; não girar, esticar ou aprovar o PNG atual. ")
        else:
            advice = ("**Próxima ação:** revisar dimensões e orientação no contrato "
                      "da tomada antes de propor nova versão. Não redimensionar "
                      "automaticamente. ")
    elif qa.startswith("rejected_"):
        advice = "**Próxima ação:** revisar a reprovação técnica e criar nova versão somente após decisão registrada. "
    else:
        advice = "**Próxima ação:** conferir alinhamento, transparência e consistência visual antes de autorizar rig. "
    return (heading + table + "\n" + advice +
            "O PNG e o SHA foram verificados **localmente**. Confirme o commit na "
            "etapa de arquivamento; este relatório não comprova publicação nem aprovação.\n",
            qa.startswith(("candidate_", "rejected_")))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True, type=Path)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--part", required=True)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    report, valid = inspect(args.images_dir, args.shot_id, args.part)
    args.summary.open("a", encoding="utf-8").write(report + "\n")
    print("EP01_PROXY_QA_FEEDBACK", "verified" if valid else "integrity_error")
    if not valid:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
