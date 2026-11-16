"""Auditoria read-only de máscaras V3 já arquivadas na branch do checkout.

A geração testa buffers em memória. Esta auditoria verifica os PNGs de fato
versionados e seus SHA, geometria, pixels RGB e alfa contra fonte e contrato
V3, sem regenerar/substituir arte nem aprovar qualquer personagem.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE
from .wardrobe_roi_candidates import verified_file, board_to_source
from .wardrobe_roi_refine import refine_mask
from .wardrobe_roi_exclusions import apply_exclusions, verify_exclusion_pixels

REPORT = "QA-ROI-EXCLUSOES-V3.json"
MANIFEST = "ROI-EXCLUSOES-CANDIDATAS-V3.json"
STATUS = "QA-ROI-ARQUIVO-REMOTO-V3.json"
EXPECTED = [
    (a, r, s)
    for a, r in (
        ("aldric", "barba"),
        ("aldric", "tecido_externo"),
        ("aldric", "painel_central"),
        ("elara", "corpete_roxo_palacio"),
    )
    for s in ("a", "b")
]


def secure_rel(base: Path, rel: str, prefix: str) -> Path:
    if not isinstance(rel, str) or "\\" in rel:
        raise VideoForgeError("ROI_ARCHIVE_UNSAFE_PATH")
    path = Path(rel)
    if (path.is_absolute() or ".." in path.parts or
            not rel.startswith(prefix) or path.suffix.lower() != ".png"):
        raise VideoForgeError("ROI_ARCHIVE_UNSAFE_PATH")
    target = base / path
    if target.is_symlink() or not target.is_file():
        raise VideoForgeError("ROI_ARCHIVE_MISSING")
    return target


def check_archive_bytes(blob: bytes, sha: str, source, before, after,
                        box, removed: int) -> dict:
    if hashlib.sha256(blob).hexdigest() != sha:
        raise VideoForgeError("ROI_ARCHIVE_SHA_MISMATCH")
    return verify_exclusion_pixels(source, before, after, blob, box, removed)


def audit(root: Path = ROOT, sync=False) -> dict:
    from PIL import Image

    ep = Path(root) / EPISODE
    report_file, manifest_file = ep / REPORT, ep / MANIFEST
    if any(p.is_symlink() or not p.is_file() for p in (report_file, manifest_file)):
        raise VideoForgeError("ROI_ARCHIVE_MANIFEST_MISSING")
    report = json.loads(report_file.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    outputs, proposals = report.get("results", []), manifest.get("rows", [])
    if (report.get("status") != "EXCLUSION_PROPOSALS_ONLY"
            or report.get("r2_blocked") is not True
            or report.get("verified_semantic_masks") != 0
            or report.get("official_roi_pairs_ready") != 0
            or report.get("owner_rejections_remain") is not True
            or report.get("paid_calls") != 0
            or manifest.get("automatic_semantic_validation") is not False
            or manifest.get("promote_to_official_contract") is not False
            or len(outputs) != 8 or len(proposals) != 8
            or [(r.get("actor"), r.get("region"), r.get("side")) for r in outputs] != EXPECTED
            or [(r.get("actor"), r.get("region"), r.get("side")) for r in proposals] != EXPECTED):
        raise VideoForgeError("ROI_ARCHIVE_UNSAFE_CONTRACT")
    result_rows = []
    for row, instruction in zip(outputs, proposals):
        if (row.get("semantically_verified") is not False
                or row.get("official_art_usable") is not False
                or row.get("semantic_status") != "EVIDENCIA_INSUFICIENTE"
                or row.get("protected_board_polygons", []) != instruction.get("protected_board_polygons", [])):
            raise VideoForgeError("ROI_ARCHIVE_FALSE_APPROVAL")
        original = verified_file(ep, row["source_path"], row["source_sha256"], image_only=True)
        box = row["cleaned_candidate_crop_xyxy"]
        if (not isinstance(box, list) or len(box) != 4
                or any(type(v) is not int for v in box)):
            raise VideoForgeError("ROI_ARCHIVE_BAD_BOX")
        # Initial polygon is source-pixel provenance written during V2 refinement.
        seed_report = ep / "QA-ROI-MASCARAS-REFINADAS-V2.json"
        if seed_report.is_symlink() or not seed_report.is_file():
            raise VideoForgeError("ROI_ARCHIVE_SEED_MISSING")
        seed = json.loads(seed_report.read_text(encoding="utf-8"))
        matches = [
            src for region in seed.get("regions", []) if
            region.get("actor") == row["actor"] and
            region.get("semantic_region") == row["region"]
            for src in region.get("sources", []) if src.get("side") == row["side"]
        ]
        if (len(matches) != 1 or matches[0]["source_sha256"] != row["source_sha256"]
                or matches[0]["source_path"] != row["source_path"]):
            raise VideoForgeError("ROI_ARCHIVE_SEED_MISMATCH")
        vertices = matches[0]["candidate_polygon_native_px"]
        before, _, _, _ = refine_mask(original, vertices, row["region"])
        source_index = 0 if row["side"] == "a" else 1
        after, delta = apply_exclusions(
            before, instruction.get("exclude_board_polygons", []),
            original.size, source_index, instruction.get("protected_board_polygons"))
        if delta != row["candidate_exclusion"]:
            raise VideoForgeError("ROI_ARCHIVE_EXCLUSION_NOT_REPRODUCIBLE")
        path = secure_rel(ep, row["cleaned_candidate_path"],
                          "assets/qa-roi-exclusions-v3/")
        data = path.read_bytes()
        integrity = check_archive_bytes(
            data, row["cleaned_candidate_sha256"], original,
            before, after, box, delta["removed"])
        if integrity != row["pixel_integrity"]:
            raise VideoForgeError("ROI_ARCHIVE_INTEGRITY_NOT_MATCHED")
        result_rows.append({
            "actor": row["actor"], "region": row["region"], "side": row["side"],
            "sha256": row["cleaned_candidate_sha256"],
            "source_sha256": row["source_sha256"],
            "removed_pixels": delta["removed"],
            "archived_png_verified": True,
            "semantic_approval": False,
        })
    context = report.get("context_review_board")
    context_sha = report.get("context_review_board_sha256")
    if context != "QA-ROI-CONTEXTO-V3.jpg":
        raise VideoForgeError("ROI_ARCHIVE_CONTEXT_PATH")
    board = ep / context
    if board.is_symlink() or not board.is_file():
        raise VideoForgeError("ROI_ARCHIVE_CONTEXT_MISSING")
    if hashlib.sha256(board.read_bytes()).hexdigest() != context_sha:
        raise VideoForgeError("ROI_ARCHIVE_CONTEXT_SHA_MISMATCH")

    result = {
        "schema": "videoforge/roi-archived-asset-verification/v1",
        "status": "ARCHIVED_V3_PIXELS_VERIFIED_SEMANTICS_PENDING",
        "checked_masks": len(result_rows), "rows": result_rows,
        "context_board_sha_verified": True,
        "approved_semantic_masks": 0, "approved_pairs": 0,
        "r2_blocked": True, "owner_rejections_preserved": True,
        "provider_calls": 0, "source_images_modified": False,
        "official_mp4": False, "youtube_uploaded": False,
    }
    if sync:
        target = ep / STATUS
        if target.is_symlink():
            raise VideoForgeError("ROI_ARCHIVE_OUTPUT_SYMLINK")
        content = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            target.write_text(content, encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true")
    opts = parser.parse_args()
    value = audit(sync=opts.sync)
    print("ROI_V3_ARCHIVE", json.dumps({
        "archived_pngs_verified": value["checked_masks"],
        "approved": 0, "r2_blocked": True, "provider_calls": 0,
    }))


if __name__ == "__main__":
    main()
