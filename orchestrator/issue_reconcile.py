#!/usr/bin/env python3
"""Read-only reconcile of GitHub Issue snapshots against queue proposals.

Snapshot must come from an authenticated, separately controlled GitHub API reader.
No network, mutations, agent execution or approvals here.
"""
import argparse
import json
import re
from pathlib import Path
from issue_proposals import proposals

MARKER = re.compile(r"<!-- videoforge-task:([A-Za-z0-9_-]+) -->")

def reconcile(queue_path, snapshot_path, limit=10):
    proposed = proposals(queue_path, limit)
    snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    if not isinstance(snapshot, list):
        raise ValueError("Snapshot must be an array")
    existing = {}
    for issue in snapshot:
        if issue.get("pull_request"):
            continue
        body = issue.get("body") or ""
        markers = MARKER.findall(body)
        for task_id in markers:
            existing.setdefault(task_id, []).append({
                "number": issue.get("number"), "state": issue.get("state"),
                "url": issue.get("html_url")})
    new, present, conflicts = [], [], []
    for proposal in proposed["issues"]:
        matches = existing.get(proposal["task_id"], [])
        if len(matches) > 1:
            conflicts.append({"task_id": proposal["task_id"], "issues": matches})
        elif len(matches) == 1:
            present.append({"task_id": proposal["task_id"], "issue": matches[0]})
        else:
            new.append(proposal)
    return {"schema_version": 1, "mode": "read_only_issue_reconciliation",
            "new_proposals": new, "already_present": present,
            "duplicate_conflicts": conflicts, "github_writes": 0,
            "agents_executed": [], "proxy_calls": 0, "youtube_publications": 0}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--queue", default="orchestrator/tasks.json")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--limit", type=int, default=10)
    args = p.parse_args()
    result = reconcile(args.queue, args.snapshot, args.limit)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"new": len(result["new_proposals"]),
                      "existing": len(result["already_present"]),
                      "conflicts": len(result["duplicate_conflicts"])}))
    if result["duplicate_conflicts"]:
        raise SystemExit("Duplicate Issues require manual review")

if __name__ == "__main__":
    main()
