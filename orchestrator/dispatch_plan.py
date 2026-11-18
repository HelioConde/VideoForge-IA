#!/usr/bin/env python3
"""Create a deterministic, read-only dispatch plan. No workers are started."""
import argparse
import json
from pathlib import Path
from agent_bus import ROLES, fingerprint
from queue_audit import audit

PRIORITY = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
ROLE_IDS = {role: agent_id for agent_id, role in ROLES.items()}

def plan(queue_path):
    validation = audit(queue_path)
    if validation["errors"]:
        raise ValueError("Queue invalid: " + "; ".join(validation["errors"]))
    data = json.loads(Path(queue_path).read_text(encoding="utf-8"))
    tasks = data["tasks"]
    by_id = {task["task_id"]: task for task in tasks}
    ready, blocked = [], []
    for task in sorted(tasks, key=lambda t: (PRIORITY.get(t.get("priority"), 9), t["task_id"])):
        if task["status"] != "ready":
            continue
        dependencies = task.get("blocked_by") or []
        unresolved = [x for x in dependencies if x not in by_id or by_id[x]["status"] != "approved"]
        if unresolved:
            blocked.append({"task_id": task["task_id"], "unresolved": unresolved})
            continue
        owner = task["owner"]
        ready.append({
            "task_id": task["task_id"], "agent_id": ROLE_IDS[owner], "owner": owner,
            "reviewer": task.get("reviewer"), "priority": task.get("priority"),
            "issue_action": "propose_only", "execute": False,
            "requires_human_approval": task.get("requires_human_approval", False),
        })
    return {
        "schema_version": 1, "mode": "dry_run", "source_sha256": validation["queue_sha256"],
        "candidate_count": len(ready), "candidates": ready,
        "dependency_blocked": blocked, "worker_execution": False,
        "issue_creation": False, "ai_calls": 0, "proxy_calls": 0,
        "youtube_publications": 0, "ep01_visual_approval": False,
        "plan_sha256": fingerprint(ready),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default="orchestrator/tasks.json")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = plan(args.queue)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text)

if __name__ == "__main__":
    main()
