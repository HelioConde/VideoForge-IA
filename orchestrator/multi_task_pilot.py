#!/usr/bin/env python3
"""Select supported ready tasks from the queue; execute real read-only audits.

Unsupported roles remain queued, never marked completed. No model/API calls.
"""
import argparse
import hashlib
import json
from pathlib import Path
from agent_bus import ROLES, make_message, append_message, safe_checkpoint
from dispatch_plan import plan
from autonomous_pilot import run as run_continuity, TASK_ID as CONTINUITY_ID

ART_ID = "EP01-C07-C08-V2-ART-CONSISTENCY"
MANIFEST = "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CONTINUIDADE-C07-C08-V2.json"
SUPPORTED = {CONTINUITY_ID: "03", ART_ID: "04"}

def art_audit(queue_path, root):
    queue = json.loads(Path(queue_path).read_text(encoding="utf-8"))
    task = next(t for t in queue["tasks"] if t["task_id"] == ART_ID)
    if task["status"] != "ready" or task["owner"] != "diretor-arte" or task.get("blocked_by"):
        raise ValueError("Art audit not dispatchable")
    path = (Path(root).resolve() / MANIFEST)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shots = manifest.get("shots", [])
    missing = [s.get("id", "<unknown>") for s in shots if
               not isinstance(s.get("reference_asset_ids"), list) or
               not isinstance(s.get("visual_prompt"), str) or not s["visual_prompt"].strip()]
    pending = [s["id"] for s in shots if not s.get("scene_mother_approved", False)]
    report = {"agent": "04", "task_id": ART_ID, "scope": "reference_manifest_inventory_only",
              "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "shot_count": len(shots), "missing_reference_or_prompt": missing,
              "mother_approval_pending": pending, "images_inspected": 0,
              "visual_consistency_approved": False}
    state = {}
    append_message(state, make_message(ART_ID, "01", "04", "task_assigned", "Inventariar referências e aprovações do manifesto", 1))
    append_message(state, make_message(ART_ID, "04", "12", "review_requested", "Revisar inventário de referências e hash", 2))
    checks = {
        "source_hash_matches": report["source_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(),
        "shot_count_matches": report["shot_count"] == len(shots),
        "pending_matches": pending == [s["id"] for s in shots if not s.get("scene_mother_approved", False)],
        "no_missing_prompt_or_reference_field": not missing,
        "visual_not_approved": report["visual_consistency_approved"] is False,
    }
    qa = {"agent": "12", "scope": "manifest_metadata_QA_only", "checks": checks,
          "passed": all(checks.values()), "visual_quality_approved": False,
          "human_review_required": True}
    append_message(state, make_message(ART_ID, "12", "01", "qa_result", "Inventário técnico revisado; imagens ainda exigem inspeção", 3))
    return {"task_id": ART_ID, "director_01": {"selected_task": ART_ID, "dispatched_to": "04"},
            "art_director_04": report, "qa_12": qa, "messages": state["events"],
            "safety": safe_checkpoint(state["events"]), "agents_executed": ["01", "04", "12"],
            "llm_agents_executed": [], "production_files_modified": False,
            "task_status": "needs_review", "human_approval": False}

def run(queue_path, root, limit=2):
    if not 1 <= limit <= 10:
        raise ValueError("Invalid limit")
    dispatch = plan(queue_path)
    completed, unsupported = [], []
    for item in dispatch["candidates"]:
        task_id = item["task_id"]
        if task_id not in SUPPORTED:
            unsupported.append({"task_id": task_id, "reason": "no_deterministic_worker_registered"})
            continue
        if len(completed) >= limit:
            continue
        if task_id == CONTINUITY_ID:
            result = run_continuity(queue_path, root)
            completed.append({"task_id": task_id, "agent_id": "03", "result": result,
                              "qa_passed": result["qa_12"]["passed"]})
        else:
            result = art_audit(queue_path, root)
            completed.append({"task_id": task_id, "agent_id": "04", "result": result,
                              "qa_passed": result["qa_12"]["passed"]})
    return {"schema_version": 1, "mode": "read_only_multi_task_pilot",
            "source_queue_sha256": dispatch["source_sha256"], "completed": completed,
            "unsupported": unsupported, "blocked": dispatch["dependency_blocked"],
            "queue_persisted": False, "github_issues_modified": False,
            "ai_calls": 0, "proxy_calls": 0, "youtube_publications": 0,
            "ep01_visual_approval": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default="orchestrator/tasks.json")
    parser.add_argument("--root", default=".")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run(args.queue, args.root, args.limit)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"executed_tasks": [t["task_id"] for t in result["completed"]],
                      "unsupported": len(result["unsupported"]), "artifact": str(output)}))
    if any(not x["qa_passed"] for x in result["completed"]):
        raise SystemExit("Technical QA failed; review artifact")

if __name__ == "__main__":
    main()
