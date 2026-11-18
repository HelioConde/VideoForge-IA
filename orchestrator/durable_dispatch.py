"""Safe durable task dispatcher: 01 -> specialist -> 12 -> 01.

Four explicitly allowlisted documentary tasks. Specialist work consists of real,
deterministic source checks, never language-model inference or media production.
The original task queue is only an input definition, not an approval signal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from .agent_bus import ROLES, fingerprint
from .runtime import ROOT, EP, instructions, report as runtime_report, source, write_report
from .runtime_store import Store, Conflict

STATE_FILE = "runtime/agent-deterministic-dispatch-v1.json"
CONTRACT = "deterministic-safe-dispatch-v1"
SUPPORTED = {
    "EP01-C07-C08-V2-CONTINUITY-AUDIT": ("03", "continuity_audit"),
    "EP01-C07-C08-V2-ART-CONSISTENCY": ("04", "reference_audit"),
    "EP01-42-MOTION-READINESS-AUDIT": ("07", "read_only_analysis"),
    "EP01-42-AUDIO-PLAN": ("10", "read_only_analysis"),
}


def select_and_seed(store: Store, root=ROOT, queue_path=None) -> list[str]:
    root = Path(root)
    queue = json.loads((Path(queue_path) if queue_path else root / "orchestrator/tasks.json")
                       .read_text(encoding="utf-8"))
    rows = queue.get("tasks")
    if (queue.get("schema_version") != 1 or queue.get("mode") != "planning_only"
            or queue.get("dispatch_enabled") is not False or not isinstance(rows, list)
            or any(not isinstance(t, dict) or not isinstance(t.get("task_id"), str) for t in rows)):
        raise ValueError("Unsafe or malformed declarative queue")
    by_id = {t["task_id"]: t for t in rows}
    if len(by_id) != len(rows):
        raise ValueError("Duplicate source task IDs")
    created = []
    for task_id, (owner, operation) in SUPPORTED.items():
        row = by_id.get(task_id)
        if row is None or row.get("status") != "ready" or row.get("blocked_by"):
            continue
        if (row.get("owner") != ROLES[owner] or row.get("reviewer") != ROLES["12"]
                or row.get("requires_human_approval") is not False
                or not isinstance(row.get("inputs"), list) or not 1 <= len(row["inputs"]) <= 5
                or len(set(row["inputs"])) != len(row["inputs"])
                or not isinstance(row.get("acceptance_criteria"), list)):
            raise ValueError("Unsafe specialist assignment")
        refs = {}
        for name in row["inputs"]:
            if not isinstance(name, str) or not name.startswith(EP.as_posix() + "/"):
                raise ValueError("Only EP01 source files can enter this dispatcher")
            _, refs[name] = source(root, name)
            declared = row.get("input_shas", {}).get(name)
            if declared:
                raw = (root / name).read_bytes()
                blob = hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                if declared not in {refs[name], blob}:
                    raise ValueError("Declared input SHA no longer matches original file")
        roles_sha = {id: instructions(root, id)[1] for id in {"01", owner, "12"}}
        version = fingerprint({"task": task_id, "inputs": refs, "roles": roles_sha,
                               "acceptance": row["acceptance_criteria"],
                               "contract": CONTRACT})[:16]
        task = {
            "task_id": task_id + "-DURABLE-" + version,
            "source_task_id": task_id,
            "owner": owner, "reviewer": "12",
            "operation": operation, "mode": "deterministic", "input_refs": refs,
            "instructions_shas": roles_sha, "priority": 0 if row["priority"] == "P0" else 1,
            "max_attempts": 1, "stop_on_review_rejection": True,
            "human_visual_approval": False,
            "scope": "read_only_source_metadata_not_human_visual_approval",
        }
        if store.enqueue(task):
            created.append(task["task_id"])
    return created


def specialist_evidence(task: dict, root=ROOT) -> dict:
    root = Path(root)
    from videoforge.ep01_continuity_v2 import read_plan, archived
    from .runtime import MANIFEST
    for name, sha in task["input_refs"].items():
        source(root, name, sha)
    doc = read_plan(root)
    source_task = task["source_task_id"]
    if source_task == "EP01-C07-C08-V2-CONTINUITY-AUDIT":
        from .continuity_evidence import validated_shot_timeline
        timeline = validated_shot_timeline(doc["shots"])
        if (len(timeline) != 9 or timeline[0]["start_frame"] != 2070
                or timeline[-1]["end_exclusive"] != 2940
                or doc["rules"].get("screen_flee_direction") != "left_to_right"
                or doc["rules"].get("cart_action") != "only_kael_pushes"):
            raise ValueError("Continuity source does not meet pinned timing/axis checks")
        result = {"shot_ids": [x["id"] for x in timeline],
                  "frame_range": [2070, 2940],
                  "screen_direction_declared": "left_to_right",
                  "only_kael_pushes_declared": True,
                  "visual_axis_verified": False}
    elif source_task == "EP01-C07-C08-V2-ART-CONSISTENCY":
        candidates = {}
        for shot in doc["shots"]:
            if shot["source_policy"] == "generate":
                item = archived(shot["id"], root)
                if item is None:
                    raise ValueError("Archived mother missing")
                candidates[shot["id"]] = {"sha256": item["sha256"], "file": item["file"]}
        if len(candidates) != 7:
            raise ValueError("Seven archived continuity images are required")
        status = json.loads((root / "canal/alchemy-lab/biblia-visual/objetos/carrinho/status.json")
                            .read_text(encoding="utf-8"))
        result = {"archived_mothers": candidates, "archived_count": len(candidates),
                  "cart_master_approved": status.get("aprovacao_mestra") is True,
                  "visual_consistency_verified": False}
    elif source_task == "EP01-42-MOTION-READINESS-AUDIT":
        from videoforge.ep01_continuity_motion import validate
        gate = validate(root)
        if (gate["rig_approved"] is not False or gate["animated_motion_verified"] is not False
                or not gate["blocked_reasons"]):
            raise ValueError("Rig readiness falsely reported as approved")
        result = {"source_hashes_verified": gate["source_shas_verified"],
                  "blocked_reasons": gate["blocked_reasons"],
                  "cart_rotation_proposed_degrees": gate["cart_rotation_degrees_proposed"],
                  "rig_approved": False, "animation_verified": False}
    elif source_task == "EP01-42-AUDIO-PLAN":
        from videoforge.ep01_camera_batch import build_plan
        shots = build_plan(root, "continuity-v2")["shots"]
        if len(shots) != 42 or sum(x["duration_frames"] for x in shots) != 4890:
            raise ValueError("Expected 42 shots and 4890 frames")
        result = {"shot_count": 42, "fps": 30, "duration_frames": 4890,
                  "cue_windows": [{"shot_id": x["id"], "start_frame": x["start_frame"],
                                   "end_exclusive": x["start_frame"]+x["duration_frames"]}
                                  for x in shots],
                  "dialogue_recorded": False, "mixing_complete": False}
    else:
        raise ValueError("No registered read-only specialist for source task")
    result.update({"visual_frames_inspected": 0, "human_visual_approval": False,
                   "video_published": False})
    return result


def worker_step(store: Store, root=ROOT) -> dict | None:
    task = store.claim(mode="deterministic")
    if task is None:
        return None
    try:
        if (task.get("source_task_id") not in SUPPORTED
                or task["owner"] != SUPPORTED[task["source_task_id"]][0]
                or task["reviewer"] != "12"):
            raise ValueError("Task route not on safe allowlist")
        if task["phase"] == "produce":
            data = specialist_evidence(task, root)
            store.deliver(task["task_id"], task["attempt_id"], task["revision"], {
                "agent_id": task["owner"], "task_id": task["task_id"],
                "source_task_id": task["source_task_id"], "input_refs": task["input_refs"],
                "evidence": data, "evidence_sha256": fingerprint(data),
                "execution_mode": "deterministic_source_audit_no_llm",
                "human_visual_approval": False, "youtube_publication": False,
                "production_files_modified": False, "model_calls": 0,
            })
        else:
            prior = store.result(task["task_id"])
            recomputed = specialist_evidence(task, root)
            passed = (
                prior.get("agent_id") == task["owner"]
                and prior.get("source_task_id") == task["source_task_id"]
                and prior.get("input_refs") == task["input_refs"]
                and prior.get("evidence_sha256") == fingerprint(recomputed)
                and prior.get("evidence") == recomputed
                and prior.get("execution_mode") == "deterministic_source_audit_no_llm"
                and prior.get("human_visual_approval") is False
                and prior.get("youtube_publication") is False
                and prior.get("production_files_modified") is False
                and prior.get("model_calls") == 0)
            store.review(task["task_id"], task["attempt_id"], task["revision"], {
                "agent_id": "12", "reviewed_result_sha256": task["result_sha256"],
                "technical_passed": bool(passed), "human_visual_approval": False,
                "scope": "source_metadata_only_not_visual_or_production_approval",
                "source_recomputed": True, "visual_frames_inspected": 0,
                "rig_approved": False, "publishing_authorized": False,
            })
    except Conflict:
        raise
    except (ValueError, KeyError, TypeError, OSError) as exc:
        store.fail(task["task_id"], task["attempt_id"], task["revision"],
                   type(exc).__name__, retry=False)
    return store.get(task["task_id"])


def run(store: Store, root=ROOT, queue_path=None, max_tasks=4) -> dict:
    if type(max_tasks) is not int or not 1 <= max_tasks <= 4:
        raise ValueError("At most four allowlisted technical audits per run")
    created = select_and_seed(store, root=root, queue_path=queue_path)
    recovered = store.recover()
    steps = []
    for _ in range(max_tasks * 2):
        task = worker_step(store, root=root)
        if task is None:
            break
        steps.append({"task_id": task["task_id"], "phase": task.get("phase"),
                      "status": task["status"]})
    result = runtime_report(store, root=root)
    result["dispatch"] = {
        "contract": CONTRACT, "new_task_ids": created, "steps": steps,
        "recovered": recovered, "source_queue_mutated": False,
        "roles_dispatched": ["01", "03", "04", "07", "10", "12"],
        "model_inference_requests": 0, "image_requests": 0,
        "rig_executions": 0, "audio_generations": 0, "youtube_publications": 0,
        "visual_quality_approved": False,
        "technical_completed": sum(t["status"] == "completed" for t in result["tasks"]),
        "blocked_task_ids": [t["task_id"] for t in result["tasks"] if t["status"] == "blocked"],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-tasks", type=int, default=4)
    parser.add_argument("--github-state", action="store_true")
    parser.add_argument("--initialize-store", action="store_true")
    args = parser.parse_args()
    if args.initialize_store and not args.github_state:
        parser.error("initialize-store requires --github-state")
    if not args.github_state and args.db is None:
        parser.error("--db required for local dispatcher")
    temporary = None
    if args.github_state:
        from .github_state import GitHubState
        remote = GitHubState(path=STATE_FILE, initialize=args.initialize_store)
        snapshot = remote.load()
        temporary = tempfile.TemporaryDirectory(prefix="videoforge-dispatch-")
        store = Store(Path(temporary.name) / "durable.sqlite")
        if snapshot is not None:
            store.import_snapshot(snapshot)
        store.persist_callback = remote.save
    else:
        target = args.db.resolve()
        if (target.is_relative_to((ROOT / "canal").resolve())
                or target.is_relative_to((ROOT / "agents").resolve())):
            parser.error("Refused runtime database inside production assets")
        store = Store(target)
    try:
        result = run(store, max_tasks=args.max_tasks)
        write_report(args.output, result)
        print(json.dumps({
            "completed_source_audits": result["dispatch"]["technical_completed"],
            "steps": len(result["dispatch"]["steps"]),
            "blocked": len(result["dispatch"]["blocked_task_ids"]),
            "model_calls": 0, "media_actions": 0,
            "state_sha256": result["state_sha256"],
        }))
        if result["dispatch"]["blocked_task_ids"]:
            raise SystemExit("Some technical tasks blocked; inspect artifact before retry")
    finally:
        store.close()
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    main()
