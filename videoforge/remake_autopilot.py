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
    if not isinstance(shots, list) or len(shots) < 37:
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
    provider_enabled = (policy.get("paid_provider_calls_approved") is True
                        and type(policy.get("max_chargeable_calls_per_run")) is int
                        and policy["max_chargeable_calls_per_run"] >= 1)
    if stage in ("generate_character_bible", "generate_shot_mother") and not provider_enabled:
        blocker = "provider_cost_permission_required"
    dispatch_allowed = (
        stage == "generate_character_bible"
        and provider_enabled
        and policy.get("auto_dispatch_generation") is True
        and policy.get("autonomy_enabled") is True
        and state.get("locks", {}).get("no_new_image_generation") is False
    )
    return {
        "schema": "videoforge/remake-autopilot-diagnostic/v1",
        "episode": "alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
        "stage": stage,
        "target": target,
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


def sync_checkpoint(report: dict, root: Path = ROOT) -> bool:
    """Only write on a real change of stage/provenance, not at each schedule."""
    episode = Path(root) / EPISODE
    state_file = episode / "estado-atual.json"
    checkpoint = episode / "ESTADO-ATUAL.md"
    history = episode / "HISTORICO-DESENVOLVIMENTO.md"
    state = _json(state_file)
    record = {key: report.get(key) for key in ("stage", "target", "blocker", "dispatch_allowed")}
    if state.get("autopilot_checkpoint") == record:
        return False
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
    checkpoint.write_text(updated, encoding="utf-8")
    history.write_text(history.read_text(encoding="utf-8") + note, encoding="utf-8")
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Read and checkpoint next verified EP01 work; zero AI calls")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    report = choose_next()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.sync:
        print("MASTER_CHECKPOINT_CHANGED", sync_checkpoint(report))
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
