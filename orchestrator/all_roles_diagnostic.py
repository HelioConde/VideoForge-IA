"""Durable read-only EP01 capability diagnostics for all 12 registered roles.

The ten specialists independently inspect real, pinned repository sources.
Agent 01 dispatches and Agent 12 independently reopens the sources in review.
This DOES NOT execute models, create media, approve visual art, or publish video.
A completed diagnostic must never be interpreted as production readiness.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from .agent_bus import ROLES, fingerprint
from .runtime import EP, MANIFEST, ROOT, instructions, report, source, write_report
from .runtime_store import Conflict, Store

STATE_PATH = "runtime/all-roles-diagnostic-v1.json"
CONTRACT = "ep01-role-source-diagnostic-v1"
SPECIALISTS = tuple(f"{i:02}" for i in range(2, 12))
FOCUS = {
    "02": "narrative_and_shot_intent",
    "03": "scene_blocking_and_axis",
    "04": "visual_reference_inventory",
    "05": "archived_mother_provenance",
    "06": "layer_separation_readiness",
    "07": "skeletal_rig_readiness",
    "08": "animation_keyframe_readiness",
    "09": "camera_only_plan",
    "10": "audio_cue_timeline",
    "11": "final_render_dependencies",
}


def diagnostic(task: dict, root=ROOT) -> dict:
    """Inspect actual source facts without pretending to perform production work."""
    root = Path(root)
    from videoforge.ep01_continuity_v2 import archived, read_plan
    from videoforge.ep01_continuity_motion import read as read_motion, validate_keyframes
    from videoforge.ep01_camera_batch import build_plan

    for rel, digest in task["input_refs"].items():
        source(root, rel, digest)
    role = task["owner"]
    if role not in SPECIALISTS or task.get("operation") != "read_only_analysis":
        raise ValueError("Unregistered specialist diagnostic")
    doc = read_plan(root)
    shots = doc["shots"]
    if len(shots) != 9:
        raise ValueError("Expected nine C07/C08 continuity shots")
    facts = {"shot_count": len(shots), "episode": EP.name}
    blockers = []
    if role == "02":
        story = json.loads((root / EP / "roteiro.json").read_text(encoding="utf-8-sig"))
        if not isinstance(story.get("format"), dict) or story["format"].get("duration_frames") != 4890:
            raise ValueError("Original narrative duration changed")
        facts.update(original_frames=4890, revised_beats=[s["beat"] for s in shots],
                     separate_meeting_and_dialogue=shots[2]["id"] == "C07-P03" and shots[3]["id"] == "C07-P04")
        blockers.append("narrative_creative_review_pending")
    elif role == "03":
        from .continuity_evidence import validated_shot_timeline
        timeline = validated_shot_timeline(shots)
        if (timeline[0]["start_frame"] != 2070 or timeline[-1]["end_exclusive"] != 2940
                or doc["rules"]["cart_action"] != "only_kael_pushes"):
            raise ValueError("Blocking or continuity constraints drifted")
        facts.update(first_frame=2070, last_exclusive=2940,
                     escape_direction=doc["rules"]["screen_flee_direction"])
        blockers.append("C07_P03_visual_axis_review_pending")
    elif role == "04":
        facts["reference_ids_by_shot"] = {s["id"]: list(s["reference_asset_ids"]) for s in shots}
        facts["mother_approved_shots"] = [s["id"] for s in shots if s.get("scene_mother_approved") is True]
        blockers.append("creator_visual_approval_pending")
    elif role == "05":
        candidates = {}
        for shot in shots:
            if shot["source_policy"] == "generate":
                found = archived(shot["id"], root)
                if found is not None:
                    candidates[shot["id"]] = found["sha256"]
        facts.update(generation_policy_shots=sum(s["source_policy"] == "generate" for s in shots),
                     archived_sha256=candidates, image_generation_calls=0)
        if len(candidates) != facts["generation_policy_shots"]:
            blockers.append("missing_archived_mother_images")
        blockers.append("visual_qa_pending_no_regeneration_authorized")
    elif role == "06":
        motion = read_motion(root)
        manifest = root / EP / motion["missing_layer_manifest"]
        if manifest.is_symlink() or not manifest.resolve().is_relative_to((root / EP).resolve()):
            raise ValueError("Untrusted layer manifest path")
        facts.update(required_layer_ids=motion["required_layer_ids"],
                     layer_manifest_present=manifest.is_file(),
                     image_edits=0, independent_hands=False)
        blockers.append("layer_approval_and_rgba_recomposition_qa_required")
        if not manifest.is_file():
            blockers.append("approved_layer_manifest_missing")
    elif role == "07":
        from videoforge.ep01_continuity_motion import validate
        gate = validate(root)
        facts.update(proposed_rotation_degrees=gate["cart_rotation_degrees_proposed"],
                     pinned_sources_checked=gate["source_shas_verified"],
                     rig_approved=gate["rig_approved"])
        blockers.extend(gate["blocked_reasons"])
    elif role == "08":
        motion = read_motion(root)
        turn = next(s for s in motion["shots"] if s["id"] == "C08-P02")
        validate_keyframes(turn)
        facts.update(proposed_keyframes=len(turn["frames"]),
                     end_yaw_degrees=turn["frames"][-1]["cart_yaw_degrees"],
                     actual_animated_frames_verified=0)
        blockers.append("approved_layers_and_rig_required_before_animation")
    elif role in {"09", "10", "11"}:
        plan = build_plan(root, "continuity-v2")
        planned = plan["shots"]
        frames = sum(s["duration_frames"] for s in planned)
        if len(planned) != 42 or frames != 4890 or plan["youtube_upload"] is not False:
            raise ValueError("Camera/timeline or publication policy drifted")
        facts.update(shot_count=42, duration_frames=4890, fps=30,
                     preview_only=plan["technical_preview_only"])
        if role == "09":
            facts["true_parallax_shots"] = sum(s["camera"].get("true_parallax") is True for s in planned)
            blockers.append("camera_only_does_not_prove_rig_or_spatial_continuity")
        elif role == "10":
            facts.update(audio_generated=False, cue_windows=42)
            blockers.append("final_audio_and_dialogue_not_approved")
        else:
            facts.update(final_mp4_verified=False, video_publications=0)
            blockers.extend(["approved_rig_and_animation_missing",
                             "final_audio_missing", "human_visual_review_pending"])
    return {
        "agent_id": role,
        "role": ROLES[role],
        "focus": FOCUS[role],
        "input_refs": task["input_refs"],
        "facts": facts,
        "production_blockers": sorted(set(blockers)),
        "diagnostic_completed": True,
        "production_ready": False,
        "model_calls": 0,
        "media_actions": 0,
        "human_visual_approval": False,
        "youtube_publication": False,
    }


def seed(store: Store, root=ROOT) -> list[str]:
    root = Path(root)
    _, sha = source(root, MANIFEST.as_posix())
    created = []
    for owner in SPECIALISTS:
        agent_shas = {name: instructions(root, name)[1] for name in ("01", owner, "12")}
        key = fingerprint({"role": owner, "manifest": sha, "instructions": agent_shas,
                           "contract": CONTRACT})[:16]
        task_id = f"EP01-DIAGNOSTIC-{owner}-{key}"
        task = {
            "task_id": task_id,
            "owner": owner, "reviewer": "12",
            "mode": "deterministic", "operation": "read_only_analysis",
            "input_refs": {MANIFEST.as_posix(): sha},
            "instructions_shas": agent_shas,
            "priority": int(owner),
            "max_attempts": 1,
            "stop_on_review_rejection": True,
            "human_visual_approval": False,
            "scope": "specialist_source_diagnostic_not_production",
        }
        if store.enqueue(task):
            created.append(task_id)
    return created


def worker_step(store: Store, root=ROOT):
    task = store.claim(mode="deterministic")
    if task is None:
        return None
    try:
        if (task["owner"] not in SPECIALISTS or task["reviewer"] != "12"
                or task.get("scope") != "specialist_source_diagnostic_not_production"):
            raise ValueError("Unexpected task")
        for role, sha in task["instructions_shas"].items():
            if instructions(root, role)[1] != sha:
                raise Conflict("Agent instructions changed since dispatch")
        if task["phase"] == "produce":
            evidence = diagnostic(task, root)
            store.deliver(task["task_id"], task["attempt_id"], task["revision"], {
                "agent_id": task["owner"], "task_id": task["task_id"],
                "input_refs": task["input_refs"],
                "evidence": evidence, "evidence_sha256": fingerprint(evidence),
                "execution_mode": "deterministic_read_only_diagnostic_no_llm",
                "human_visual_approval": False, "youtube_publication": False,
            })
        else:
            prior = store.result(task["task_id"])
            replay = diagnostic(task, root)
            passed = (
                prior.get("agent_id") == task["owner"]
                and prior.get("input_refs") == task["input_refs"]
                and prior.get("evidence_sha256") == fingerprint(replay)
                and prior.get("evidence") == replay
                and prior.get("execution_mode") == "deterministic_read_only_diagnostic_no_llm"
                and replay["production_ready"] is False
                and replay["human_visual_approval"] is False
                and replay["youtube_publication"] is False
            )
            store.review(task["task_id"], task["attempt_id"], task["revision"], {
                "agent_id": "12", "reviewed_result_sha256": task["result_sha256"],
                "technical_passed": bool(passed), "human_visual_approval": False,
                "scope": "recomputed_source_diagnostic_not_media_qa",
                "production_ready": False, "youtube_publication": False,
            })
    except Conflict:
        raise
    except (ValueError, KeyError, TypeError, OSError) as exc:
        store.fail(task["task_id"], task["attempt_id"], task["revision"],
                   type(exc).__name__, retry=False)
    return store.get(task["task_id"])


def run(store: Store, root=ROOT) -> dict:
    created = seed(store, root)
    recovered = store.recover()
    steps = []
    for _ in range(len(SPECIALISTS) * 2):
        task = worker_step(store, root)
        if task is None:
            break
        steps.append({"task_id": task["task_id"], "phase": task["phase"],
                      "status": task["status"]})
    data = report(store, root=root)
    readiness = []
    for row in sorted(data["tasks"], key=lambda item: item["owner"]):
        if row["status"] == "completed":
            result = store.result(row["task_id"])
            evidence = result["evidence"]
            readiness.append({
                "agent_id": row["owner"], "role": ROLES[row["owner"]],
                "diagnostic_status": "completed", "scope": evidence["focus"],
                "source_evidence_sha256": result["evidence_sha256"],
                "production_ready": False,
                "production_blockers": evidence["production_blockers"],
                "llm_executed": False,
            })
        else:
            readiness.append({
                "agent_id": row["owner"], "role": ROLES[row["owner"]],
                "diagnostic_status": row["status"], "scope": FOCUS[row["owner"]],
                "source_evidence_sha256": None, "production_ready": False,
                "production_blockers": ["source_diagnostic_unavailable"],
                "llm_executed": False,
            })
    data["role_diagnostic"] = {
        "contract": CONTRACT, "coordinator": "01", "independent_qa": "12",
        "specialists": list(SPECIALISTS), "roles_covered": list(ROLES),
        "readiness": readiness,
        "coordinator_scope": "durable_task_dispatch_no_model_or_media",
        "reviewer_scope": "independent_recomputation_not_visual_QA",
        "created": created, "recovered": recovered, "steps": steps,
        "diagnostic_completed_count": sum(t["status"] == "completed" for t in data["tasks"]),
        "blocked_task_ids": [t["task_id"] for t in data["tasks"] if t["status"] != "completed"],
        "ai_agents_executed": [], "production_roles_executed": [],
        "media_created": 0, "model_calls": 0, "youtube_publications": 0,
        "source_queue_modified": False, "production_ready": False,
        "visual_quality_approved": False,
    }
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-state", action="store_true")
    parser.add_argument("--initialize-store", action="store_true")
    args = parser.parse_args()
    if args.initialize_store and not args.github_state:
        parser.error("initialize-store requires --github-state")
    if not args.db and not args.github_state:
        parser.error("--db required for local diagnostics")
    temp = None
    if args.github_state:
        from .github_state import GitHubState
        remote = GitHubState(path=STATE_PATH, initialize=args.initialize_store)
        snapshot = remote.load()
        temp = tempfile.TemporaryDirectory(prefix="vf-roles-")
        store = Store(Path(temp.name) / "roles.sqlite")
        if snapshot is not None:
            store.import_snapshot(snapshot)
        store.persist_callback = remote.save
    else:
        db = args.db.resolve()
        if db.is_relative_to((ROOT / "canal").resolve()) or db.is_relative_to((ROOT / "agents").resolve()):
            parser.error("Diagnostic DB cannot overwrite production sources")
        store = Store(db)
    try:
        result = run(store)
        write_report(args.output, result)
        summary = result["role_diagnostic"]
        print(json.dumps({key: summary[key] for key in
                          ("diagnostic_completed_count", "blocked_task_ids", "model_calls",
                           "media_created", "production_ready")}))
        if summary["blocked_task_ids"] or summary["diagnostic_completed_count"] != len(SPECIALISTS):
            raise SystemExit("Role source diagnostics did not all pass")
    finally:
        store.close()
        if temp is not None:
            temp.cleanup()


if __name__ == "__main__":
    main()
