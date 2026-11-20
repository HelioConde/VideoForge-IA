"""Read-only, source-pinned EP01 audit of candidate RGBA parts and rig readiness.

Does not call the image proxy, create cutouts, approve art/rigs or render video.
Runs independently from the ten-slot production controller and its CAS ledger.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from PIL import Image

from videoforge import ep01_camera_batch as camera
from videoforge import ep01_proxy_separate_parts as parts

ROOT = Path(__file__).resolve().parents[1]
EP = Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
LEGACY_PLAN = EP / "PLANO-CAMADAS-CAMERA-EP01.json"
SCHEMA = "videoforge/ep01-rig-readiness-audit/v1"
NO_LEGACY_LAYERS = {"C01-P02", "C01-P04"}
CONTINUITY = {f"C07-P{i:02d}" for i in range(1,5)} | {f"C08-P{i:02d}" for i in range(1,6)}
ALLOWED_QA = {
    "candidate_proxy_generated_separate_image",
    "candidate_minor_edge_delta_requires_alignment_qa",
    "candidate_native_model_canvas_requires_placement_qa",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def policy_checks(meta: dict, source_sha: str, shot_id: str, part_id: str,
                  canvas: tuple[int, int], dimensions: tuple[int, int],
                  mode: str, alpha: tuple[int, int] | None) -> list[str]:
    """Positive geometry alone never establishes correct contact or visual identity."""
    issues = []
    if (meta.get("schema") != "videoforge/ep01-proxy-separate-part/v1"
            or meta.get("candidate_scene_shot_id") != shot_id
            or meta.get("component") != part_id
            or meta.get("generation_method") != "proxy_generated_separate_image"):
        issues.append("unverified_provenance")
    if meta.get("source_mother_sha256") != source_sha:
        issues.append("wrong_scene_mother_sha")
    if meta.get("human_visual_approval") is not False or meta.get("rig_ready") is not False:
        issues.append("unexpected_approval_or_rig_flag")
    if meta.get("youtube_uploaded") is not False:
        issues.append("unexpected_publish_flag")
    technical = str(meta.get("technical_qa", ""))
    if technical.startswith("rejected_"):
        issues.append("archived_candidate_rejected")
    elif technical not in ALLOWED_QA:
        issues.append("technical_status_not_verified")
    if dimensions != canvas:
        issues.append("native_canvas_alignment_required")
    if part_id.startswith(("character-", "object-")):
        if mode != "RGBA" or alpha is None or alpha[0] != 0 or alpha[1] < 128:
            issues.append("rgba_transparency_invalid_or_empty")
    return sorted(set(issues))


def inspect_part(root: Path, shot: dict, part_id: str) -> dict:
    sid = shot["id"]
    base = {
        "part": part_id, "shot_id": sid, "human_visual_approval": False,
        "rig_ready": False, "technical_candidate": False,
    }
    try:
        entry = parts.existing_part(sid, part_id, root)
    except (OSError, ValueError, KeyError) as exc:
        return dict(base, status="integrity_problem",
                    issues=["registry_or_archive_integrity_error"],
                    detail=type(exc).__name__)
    if entry is None:
        return dict(base, status="missing",
                    issues=["no_sha_verified_independent_asset"])
    rel = Path(entry["file"])
    path = root / rel
    metadata_file = path.with_suffix(".production.json")
    if (rel.is_absolute() or ".." in rel.parts
            or not rel.is_relative_to(EP / "assets" / "geracoes")
            or not path.is_file() or path.is_symlink()
            or not metadata_file.is_file() or metadata_file.is_symlink()):
        return dict(base, status="integrity_problem", issues=["unsafe_or_missing_source"])
    try:
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        image_sha = digest(path)
        if (image_sha != entry["sha256"] or
                image_sha != metadata.get("sha256")):
            raise ValueError("SHA256 mismatch")
        with Image.open(path) as image:
            image.load()
            if image.format != "PNG":
                raise ValueError("File not PNG")
            dimensions = tuple(image.size)
            mode = image.mode
            alpha = image.getchannel("A").getextrema() if "A" in image.getbands() else None
        canvas = tuple(shot["source"]["dimensions"])
        issues = policy_checks(metadata, shot["source"]["sha256"],
                               sid, part_id, canvas, dimensions, mode, alpha)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return dict(base, status="integrity_problem",
                    issues=["image_or_metadata_unverifiable"],
                    detail=type(exc).__name__)
    status = ("rejected_archived" if "archived_candidate_rejected" in issues
              else "needs_technical_review" if issues
              else "geometry_candidate_only")
    return dict(base, status=status, issues=issues, source_file=rel.as_posix(),
                sha256=image_sha, metadata_technical_qa=metadata.get("technical_qa"),
                canvas_expected=list(canvas), canvas_actual=list(dimensions),
                mode=mode, alpha_extrema=list(alpha) if alpha is not None else None,
                technical_candidate=status == "geometry_candidate_only",
                visual_contact_qa="pending", source_mother_sha=shot["source"]["sha256"])


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    plan = camera.build_plan(root, revision="continuity-v2")
    if (len(plan["shots"]) != 42 or
            sum(s["duration_frames"] for s in plan["shots"]) != 4890 or
            plan["youtube_upload"] is not False):
        raise ValueError("EP01_42_SHOT_SOURCE_DRIFT")
    raw = json.loads((root / LEGACY_PLAN).read_text(encoding="utf-8"))
    legacy = {s["id"]: s for s in raw["shots"]}
    if len(legacy) != 40:
        raise ValueError("EP01_LEGACY_EDL_SOURCE_DRIFT")
    result = []
    totals = Counter()
    for shot in plan["shots"]:
        sid = shot["id"]
        if sid == "C01-P01":
            result.append({"shot_id":sid, "status":"not_applicable_black",
                           "parts":[], "human_visual_approval":False,"rig_ready":False})
            continue
        mother = shot["source"]
        if not mother:
            raise ValueError("EP01_MISSING_MOTHER " + sid)
        # camera.checked_source verifies the approved/pinned source PNG,
        # original dimensions and SHA; no modification or resizing.
        camera.checked_source(root, mother)
        old = legacy.get(sid)
        expected = [x["id"] for x in old.get("images", {}).get("proxy_generation_requests", [])] if old else []
        parts_report = [inspect_part(root, shot, part) for part in expected]
        for item in parts_report:
            totals[item["status"]] += 1
        flags = []
        if sid in CONTINUITY:
            flags.append("continuity_v2_requires_shot_specific_layer_plan")
        if sid in NO_LEGACY_LAYERS:
            flags.append("rejected_or_restricted_original_layer_plan")
        if not expected:
            flags.append("no_independent_layer_plan")
        if len(parts_report) != len(expected):
            raise ValueError("EP01_COMPONENT_COUNT_DRIFT")
        if any(p["status"] == "integrity_problem" for p in parts_report):
            flags.append("integrity_problem_manual_reconciliation")
        if any(p["status"] == "missing" for p in parts_report):
            flags.append("missing_independent_assets")
        if any(p["status"] == "rejected_archived" for p in parts_report):
            flags.append("rejected_archive_no_paid_auto_retry")
        if any(p["status"] == "needs_technical_review" for p in parts_report):
            flags.append("canvas_or_reference_qa_needed")
        if parts_report and all(p["status"] == "geometry_candidate_only" for p in parts_report):
            flags.append("candidate_set_complete_pending_visual_recomposition")
        result.append({
            "shot_id": sid, "mother_sha256": mother["sha256"],
            "mother_file": mother["file"], "expected_parts": len(expected),
            "candidate_geometry_passed":sum(p["status"]=="geometry_candidate_only" for p in parts_report),
            "parts": parts_report, "flags": flags,
            "status": "blocked_rig_pending_independent_visual_qa",
            "human_visual_approval": False, "recomposition_approved":False,
            "rig_ready":False,"independent_hands":False,
        })
    report = {
        "schema":SCHEMA, "shot_count":42, "fps":30, "duration_frames":4890,
        "scope":"alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
        "source_revision":"continuity-v2",
        "component_counts":dict(totals),
        "shots":result,
        "visual_review_required":True, "human_visual_approval":False,
        "rig_ready_shots":0, "youtube_uploaded":False, "image_provider_calls":0,
        "technical_limits":[
            "Exact canvas and alpha checks cannot verify hands, anatomy, costume or continuity",
            "A completed candidate set is not an approved rig and cannot unlock animation",
            "Continuity V2 requires shot-specific separations; old C07/C08 part plans are blocked",
            "No parts or scenes are modified and no paid provider is called",
        ],
    }
    return report


def to_markdown(report: dict) -> str:
    names = {name: report["component_counts"].get(name,0) for name in (
        "geometry_candidate_only", "needs_technical_review",
        "rejected_archived", "missing", "integrity_problem")}
    lines = [
        "# EP01 — auditoria offline das camadas para rig",
        "",
        "Revisão de **42 tomadas** da continuidade V2. **Nenhuma** imagem, rig ou",
        "animação foi aprovado; o resultado é diagnóstico técnico somente.",
        "",
        "Componentes por situação: " + ", ".join(f"{k}: **{v}**" for k,v in names.items()) + ".",
        "",
        "| Tomada | Peças válidas geometricamente | Requeridas | Pendências |",
        "|---|---:|---:|---|",
    ]
    for row in report["shots"]:
        flags = ", ".join(row.get("flags", [])) or "aguarda revisão visual de identidade/contato"
        lines.append(
            f"| {row['shot_id']} | {row.get('candidate_geometry_passed',0)} | "
            f"{row.get('expected_parts',0)} | {flags} |"
        )
    lines += [
        "", "Os PNGs existentes são preservados. Não corrigir rejeições regenerando",
        "automaticamente nem substituir imagens por recortes falsos. Para desbloquear",
        "rig, validar camadas RGBA, recomposição contra mãe, juntas/pivôs e revisão visual",
        "independente, sempre com o mesmo SHA de origem.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = build()
    folder = args.output
    folder.mkdir(parents=True, exist_ok=True)
    (folder/"EP01-rig-readiness.json").write_text(json.dumps(
        report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = to_markdown(report)
    (folder/"EP01-rig-readiness.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"shots":42,"components":report["component_counts"],
                      "rig_ready_shots":0, "image_provider_calls":0,
                      "report_dir":str(folder)},ensure_ascii=False))
    print("NO_AUTO_RIG_APPROVAL", flush=True)


if __name__ == "__main__":
    main()
