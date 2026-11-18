#!/usr/bin/env python3
"""Read-only queue audit. Does not execute agents or modify EP01."""
import argparse
import json
from collections import Counter
from pathlib import Path
from agent_bus import ROLES, STATES, fingerprint

def audit(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])
    ids = [t.get("task_id") for t in tasks]
    errors = []
    if len(ids) != len(set(ids)):
        errors.append("Duplicate task IDs")
    for t in tasks:
        task_id = t.get("task_id", "<missing>")
        if t.get("owner") not in ROLES.values():
            errors.append(f"{task_id}: invalid owner")
        if t.get("status") not in STATES:
            errors.append(f"{task_id}: invalid status")
        if t.get("status") == "running" and t.get("blocked_by"):
            errors.append(f"{task_id}: running with unresolved blockers")
        if t.get("status") == "approved" and t.get("requires_human_approval"):
            errors.append(f"{task_id}: human gate cannot be auto-approved")
        if t.get("reviewer") == t.get("owner"):
            errors.append(f"{task_id}: self-review")
    return {
        "schema_version": 1, "mode": "read_only", "dispatch_enabled": False,
        "task_count": len(tasks), "owners": dict(sorted(Counter(t.get("owner") for t in tasks).items())),
        "states": dict(sorted(Counter(t.get("status") for t in tasks).items())),
        "queue_sha256": fingerprint(data), "errors": errors,
        "ai_calls": 0, "proxy_calls": 0, "youtube_publications": 0,
        "ep01_visual_approval": False,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default="orchestrator/tasks.json")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = audit(args.queue)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    print(payload)
    if result["errors"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
