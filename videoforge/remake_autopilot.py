"""Remake orchestration on GitHub: evidence-driven next step, no simulated media.

Read the canonical state/shot registry. Never approve humans, spend money,
publish YouTube or make a proxy call. A workflow can run this periodically,
checkpoint changes only once, and delegate verified work to existing producers.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from .errors import VideoForgeError

ROOT = Path(__file__).resolve().parents[1]
EPISODE = Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
SHA = re.compile(r"^[0-9a-f]{64}$")
BEGIN = "<!-- REMAKE-AUTOPILOT-START -->"
END = "<!-- REMAKE-AUTOPILOT-END -->"


def _json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 400_000:
        raise VideoForgeError("REMAKE_AUTOPILOT_SOURCE_MISSING")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise VideoForgeError("REMAKE_AUTOPILOT_JSON_INVALID") from exc
    if not isinstance(data, dict):
        raise VideoForgeError("REMAKE_AUTOPILOT_JSON_ROOT_INVALID")
    return data


def verified_asset(episode: Path, relative: object, expected_sha: object) -> bool:
    if (not isinstance(relative, str) or "\\" in relative
            or not relative.startswith("assets/")
            or Path(relative).is_absolute() or ".." in Path(relative).parts
            or not isinstance(expected_sha, str) or SHA.fullmatch(expected_sha) is None):
        return False
    asset = episode / relative
    if asset.is_symlink() or not asset.is_file() or not asset.resolve().is_relative_to(episode.resolve()):
        return False
    return hashlib.sha256(asset.read_bytes()).hexdigest() == expected_sha


def discover_archived_character_bible(episode: Path) -> dict | None:
    """Find real PNG from an existing VideoForge art-run archive by manifest+SHA."""
    base = episode / "assets" / "geracoes" / "production-art-request"
    if not base.is_dir() or base.is_symlink():
        return None
    found = []
    for run in base.iterdir():
        if not run.is_dir() or run.is_symlink() or not run.name.isdigit():
            continue
        manifest_file = run / "manifesto-geracoes.json"
        if not manifest_file.is_file():
            continue
        try:
            manifest = _json(manifest_file)
        except VideoForgeError:
            continue
        if (manifest.get("schema") != "videoforge/permanent-generated-image-archive/v1"
                or manifest.get("channel") != "alchemy-lab"
                or manifest.get("video_id") != "mmorpg-conquiste-a-princesa-ep01"
                or manifest.get("producer") != "production-art-request"
                or manifest.get("github_run_id") != int(run.name)):
            continue
        for item in manifest.get("images", []):
            if not isinstance(item, dict) or item.get("file") != "character-bible.png":
                continue
            rel = "assets/geracoes/production-art-request/" + run.name + "/character-bible.png"
            if verified_asset(episode, rel, item.get("sha256")):
                from .scene_layers import png_info
                try:
                    info=png_info((episode / rel).read_bytes())
                except (VideoForgeError, ValueError, OSError):
                    continue
                width,height=info["width"],info["height"]
                if (width,height)!=(item.get("width"),item.get("height")):
                    continue
                found.append((int(run.name), {
                    "path": rel, "sha256": item["sha256"],
                    "run_id": int(run.name),
                    "width": width, "height": height,
                    "dimensions_match_requested": (width,height)==(1024,1536),
                    "human_approved": False,
                }))
    return max(found, key=lambda item: item[0])[1] if found else None


def choose_next(root: Path = ROOT) -> dict:
    episode = Path(root) / EPISODE
    data = _json(episode / "remake-ep01-planos.json")
    policy = _json(episode / "autonomy-policy.json")
    state = _json(episode / "estado-atual.json")
    if (data.get("schema") != "videoforge/alchemy-remake-autonomy-plan/v1"
            or policy.get("schema") != "videoforge/remake-autonomy-policy/v1"
            or policy.get("scope") != "alchemy-lab/mmorpg-conquiste-a-princesa-ep01"
            or state.get("active_production_version") != "remake-v2-20261115"):
        raise VideoForgeError("REMAKE_AUTOPILOT_SCOPE_OR_SCHEMA_INVALID")
    shots = data.get("shots")
    if (not isinstance(shots,list) or
            len(shots)<data.get("plan",{}).get("shots_minimum",40)):
        raise VideoForgeError("REMAKE_AUTOPILOT_PLAN_INCOMPLETE")
    cursor, ids = 0, set()
    for shot in shots:
        if not isinstance(shot, dict):
            raise VideoForgeError("REMAKE_AUTOPILOT_SHOT_NOT_OBJECT")
        ident = shot.get("shot_id")
        end = shot.get("frame_end_exclusive")
        if (not isinstance(ident, str)
                or re.fullmatch(r"C[0-9]{2}-P[0-9]{2}", ident) is None
                or ident in ids or shot.get("frame_start") != cursor
                or type(end) is not int or end <= cursor):
            raise VideoForgeError("REMAKE_AUTOPILOT_TIMELINE_INCONSISTENT")
        ids.add(ident)
        cursor = end
    if cursor != data.get("format", {}).get("total_frames"):
        raise VideoForgeError("REMAKE_AUTOPILOT_BAD_DURATION")
    if (shots[0].get("shot_id") != "C01-P01"
            or shots[0].get("require_new_mother") is not False
            or data.get("authorization", {}).get("new_image_generation_editorially_allowed") is not True
            or state.get("remake_v2", {}).get("generation_editorially_authorized") is not True):
        raise VideoForgeError("REMAKE_AUTOPILOT_AUTH_OR_BLACK_FRAME_INVALID")
    stage, target, blocker = None, None, None
    candidate = None
    if (episode / "SEM-GERACAO-NOVAS-IMAGENS.lock").exists():
        stage, blocker = "stop_old_lock", "historical_lock_still_active"
    else:
        anchors = data.get("identity_anchors")
        if not isinstance(anchors, list) or not anchors or anchors[0].get("id") != "character-bible":
            raise VideoForgeError("REMAKE_AUTOPILOT_ANCHOR_MANIFEST_INVALID")
        anchor = anchors[0]
        has_art = verified_asset(episode, anchor.get("path"), anchor.get("sha256"))
        if anchor.get("status") == "approved" and not has_art:
            stage, target, blocker = "stop_bad_reference_sha", "character-bible", "anchor_approval_without_real_matching_png"
        elif not has_art:
            candidate = discover_archived_character_bible(episode)
            if candidate:
                stage, target, blocker = "review_identity_reference", "character-bible", "archived_png_verified_human_review_pending"
            else:
                stage, target, blocker = "generate_character_bible", "character-bible", "no_verified_reference_png"
        elif anchor.get("human_approved") is not True:
            stage, target, blocker = "review_identity_reference", "character-bible", "human_visual_review_pending"
        else:
            for shot in shots:
                if shot.get("require_new_mother") is not True:
                    continue
                sid = shot["shot_id"]
                folder = "assets/remake-v2/" + sid + "/"
                if not verified_asset(episode, folder + "scene-mother.png", shot.get("art_mother_sha256")):
                    stage, target, blocker = "generate_shot_mother", sid, "shot_image_not_verified"
                    break
                if not verified_asset(episode, folder + "background-reconstructed.png", shot.get("background_sha256")):
                    stage, target, blocker = "make_scene_layers", sid, "background_and_rgba_qa_pending"
                    break
                if shot.get("motion_qa_passed") is not True:
                    stage, target, blocker = "build_mesh_rig_and_qa", sid, "articulated_rig_qa_pending"
                    break
                if shot.get("human_visual_approved") is not True:
                    stage, target, blocker = "review_shot", sid, "human_visual_review_pending"
                    break
            if stage is None:
                stage, blocker = "final_assembly_preflight", "audio_video_qa_and_final_review_pending"
    source_readiness = None
    if stage == "review_identity_reference":
        # An archived PNG is only a candidate. Do not ask for approval of
        # visual identity while the exact user-approved Kael/Elara originals
        # are absent. Use live SHA status, not stale historical v1 metadata.
        from .cinematic_chat_references import reference_status
        originals = reference_status(root)
        rows = originals["samples"]
        missing = [x["expected_repo_path"] for x in rows
                   if x["source_original_verified"] is not True]
        camera = originals["camera_candidate_C12_P02"]
        if camera["source_verified"] is not True:
            missing.append(camera["expected_repo_path"])
        source_readiness = {
            "original_style_source_count": 2,
            "verified_style_source_count": originals["original_source_files_sha_verified"],
            "c12_camera_source_verified": camera["source_verified"],
            "missing_original_paths": missing,
            "required_upload_zip": "uploads/alchemy-ep01-cinema-3-originais.zip",
            "import_script": "scripts/enviar-referencias-cinema.ps1",
            "readonly_import_workflow": "qa-alchemy-chat-cinematic-references.yml",
            "aldric_individual_sha_approved_reference_missing": True,
            "automatic_visual_approval": False,
        }
        if (originals["status"] == "BLOCKED_INVALID_REFERENCE_BYTES"
                or camera["status"] == "INVALID_SOURCE_BYTES"):
            blocker = "invalid_original_reference_sha_stop"
        elif originals["original_source_files_sha_verified"] < 2:
            blocker = "original_kael_elara_sha_sources_missing"
        # Once exact originals are imported, the next gate is HUMAN identity
        # comparison: never auto-approve merely because SHA matches.
    provider_enabled = (policy.get("paid_provider_calls_approved") is True
                        and type(policy.get("max_chargeable_calls_per_run")) is int
                        and policy["max_chargeable_calls_per_run"] >= 1)
    if stage in ("generate_character_bible", "generate_shot_mother") and not provider_enabled:
        blocker = "provider_cost_permission_required"
    existing_intent = state.get("generation_dispatch_intent")
    if stage == "generate_character_bible" and isinstance(existing_intent, dict):
        if existing_intent.get("target") == "character-bible":
            blocker = "generation_dispatch_already_reserved_wait_for_artifact_or_investigation"
    dispatch_allowed = (
        stage == "generate_character_bible"
        and not isinstance(existing_intent, dict)
        and provider_enabled
        and policy.get("auto_dispatch_generation") is True
        and policy.get("autonomy_enabled") is True
        and state.get("locks", {}).get("no_new_image_generation") is False
        and "production-art-by-request.yml" in policy.get("allowed_producer_workflows", [])
    )
    return {
        "schema": "videoforge/remake-autopilot-diagnostic/v1",
        "episode": "alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
        "stage": stage,
        "target": target,
        "discovered_candidate": candidate,
        "source_readiness": source_readiness,
        "blocker": blocker,
        "next_workflow": "production-art-by-request.yml" if dispatch_allowed else None,
        "dispatch_allowed": bool(dispatch_allowed),
        "planned_shots": len(shots),
        "art_required_shots": sum(s.get("require_new_mother") is True for s in shots),
        "master_checkpoint": "ESTADO-ATUAL.md",
        "created_images": 0,
        "created_mp4": False,
        "uploaded_youtube": False,
        "approved_human_review": False,
    }


def reserve_generation_dispatch(report: dict, root: Path = ROOT) -> dict:
    """Reserve one authorized candidate BEFORE triggering a paid workflow.

    The reservation is committed to main before GitHub workflow_dispatch.
    If dispatch fails, do NOT blindly repeat or charge again: investigate
    reservation/run evidence first. Never auto-approve artwork or publish.
    """
    root = Path(root)
    episode = root / EPISODE
    state_path = episode / "estado-atual.json"
    state = _json(state_path)
    policy = _json(episode / "autonomy-policy.json")
    current = choose_next(root)
    existing = state.get("generation_dispatch_intent")
    if isinstance(existing, dict):
        return {"schema": "videoforge/remake-dispatch-reservation/v1",
                "ready": False, "reason": "already_reserved",
                "request_id": existing.get("request_id")}
    if (report.get("stage") != current.get("stage")
        or report.get("target") != current.get("target")
        or report.get("dispatch_allowed") is not True
        or current.get("dispatch_allowed") is not True
        or current.get("next_workflow") != "production-art-by-request.yml"
        or policy.get("max_chargeable_calls_per_run") != 1
        or policy.get("standing_user_authorization", {}).get("per_call_reapproval_required") is not False
        or state.get("locks", {}).get("no_youtube_upload") is not True):
        return {"schema": "videoforge/remake-dispatch-reservation/v1",
                "ready": False, "reason": "not_authorized_or_not_pending"}
    from .image_generation_policy import assert_image_generation_allowed
    from .production_art import read_plan, asset_prompt
    assert_image_generation_allowed("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", root)
    art, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", root)
    if (art.get("request_limit", {}).get("per_run") != 1
        or art.get("request_limit", {}).get("strict_budget") != 1):
        raise VideoForgeError("REMAKE_DISPATCH_ART_LIMIT_NOT_ONE")
    asset_prompt(art, story, "character-bible")
    target = "character-bible"
    unique = hashlib.sha256((
        "alchemy-lab/mmorpg-conquiste-a-princesa-ep01|"
        "remake-v2-20261115|production-art-by-request.yml|"
        "character-bible|standing-2026-11-15"
    ).encode("utf-8")).hexdigest()
    state["generation_dispatch_intent"] = {
        "schema": "videoforge/remake-dispatch-intent/v1",
        "request_id": unique, "target": target,
        "workflow": "production-art-by-request.yml",
        "status": "reserved_before_external_dispatch",
        "reserved_utc": datetime.now(timezone.utc).isoformat(),
        "max_calls_per_run": 1,
        "provider_charge_possible": True,
        "actual_provider_charge_confirmed": False,
        "youtube_upload": False, "human_visual_approved": False,
    }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"schema": "videoforge/remake-dispatch-reservation/v1",
            "ready": True, "request_id": unique,
            "workflow": "production-art-by-request.yml",
            "channel": "alchemy-lab",
            "video_id": "mmorpg-conquiste-a-princesa-ep01",
            "asset": target, "max_calls_per_run": 1,
            "youtube_upload": False}


def sync_checkpoint(report: dict, root: Path = ROOT) -> bool:
    """Only write on a real change of stage/provenance, not at each schedule."""
    episode = Path(root) / EPISODE
    state_file = episode / "estado-atual.json"
    checkpoint = episode / "ESTADO-ATUAL.md"
    history = episode / "HISTORICO-DESENVOLVIMENTO.md"
    state = _json(state_file)
    record = {key: report.get(key) for key in ("stage", "target", "blocker", "dispatch_allowed")}
    source_readiness = report.get("source_readiness")
    if isinstance(source_readiness, dict):
        record["verified_style_source_count"] = source_readiness["verified_style_source_count"]
        record["missing_original_paths"] = source_readiness["missing_original_paths"]
        record["aldric_individual_sha_approved_reference_missing"] = True
    candidate = report.get("discovered_candidate")
    if isinstance(candidate, dict):
        record["candidate_sha256"] = candidate.get("sha256")
    if state.get("autopilot_checkpoint") == record:
        return False
    if candidate:
        plan_path = episode / "remake-ep01-planos.json"
        plan = _json(plan_path)
        anchor = plan["identity_anchors"][0]
        if not verified_asset(episode, candidate.get("path"), candidate.get("sha256")):
            raise VideoForgeError("REMAKE_AUTOPILOT_ARCHIVED_REFERENCE_NOT_VERIFIED")
        if anchor.get("status") in ("missing", "candidate_human_review_pending"):
            anchor.update({
                "path": candidate["path"],
                "sha256": candidate["sha256"],
                "run_id": candidate["run_id"],
                "status": "candidate_human_review_pending",
                "human_approved": False,
            })
            plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    original = checkpoint.read_text(encoding="utf-8")
    if (BEGIN in original) != (END in original):
        raise VideoForgeError("REMAKE_AUTOPILOT_CHECKPOINT_MARKER_BROKEN")
    status = (BEGIN + "\n### Diagnóstico autônomo mais recente\n"
              + "- Etapa: " + str(record["stage"]) + "\n"
              + "- Alvo: " + str(record["target"]) + "\n"
              + "- Bloqueio: " + str(record["blocker"]) + "\n"
              + "- Despacho de geração permitido: " + str(record["dispatch_allowed"]) + "\n"
              + "- Sem novas imagens, vídeo ou aprovação humana neste diagnóstico.\n"
              + END)
    if BEGIN in original:
        left = original.index(BEGIN)
        right = original.index(END, left) + len(END)
        updated = original[:left] + status + original[right:]
    else:
        updated = original.replace("\n", "\n\n" + status + "\n\n", 1)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = ("\n## " + date + " — diagnóstico automático de retomada\n\n"
            + "- Etapa: " + str(record["stage"]) + "; alvo: " + str(record["target"])
            + "; bloqueio: " + str(record["blocker"]) + ".\n"
            + "- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.\n")
    state["autopilot_checkpoint"] = record
    if isinstance(source_readiness, dict):
        # Independent live snapshot; historical audit records remain immutable.
        # SHA-verified references are never treated as human identity approval.
        missing=source_readiness["missing_original_paths"]
        state["reference_sources_current"] = {
            "schema":"videoforge/remake-source-readiness/v1",
            "status":("ready_for_human_identity_comparison" if not missing
                      else "waiting_for_exact_original_sources"),
            "kael_elara_verified":source_readiness["verified_style_source_count"],
            "kael_elara_required":source_readiness["original_style_source_count"],
            "c12_camera_verified":source_readiness["c12_camera_source_verified"],
            "missing_original_paths":missing,
            "aldric_individual_sha_reference_missing":
                source_readiness["aldric_individual_sha_approved_reference_missing"],
            "human_visual_approval":False,
            "provider_calls":0,
            "youtube_uploaded":False,
        }
    checkpoint.write_text(updated, encoding="utf-8")
    history.write_text(history.read_text(encoding="utf-8") + note, encoding="utf-8")
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Read and checkpoint next verified EP01 work; zero AI calls")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--sync", action="store_true")
    parser.add_argument("--reserve", action="store_true",
                        help="Reserve one approved image call; never call proxy here")
    args = parser.parse_args()
    report = choose_next()
    if args.reserve:
        if args.sync:
            parser.error("--reserve and --sync cannot be combined")
        reservation = reserve_generation_dispatch(report)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(reservation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("REMAKE_DISPATCH_RESERVATION", json.dumps(reservation, ensure_ascii=False))
        return 0
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.sync:
        print("MASTER_CHECKPOINT_CHANGED", sync_checkpoint(report))
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
