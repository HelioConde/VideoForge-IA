#!/usr/bin/env python3
"""Build a bounded, read-only agent dispatch from a reconciled Issue inbox.

Only registered deterministic workers execute; Issue content is never executed.
"""
import argparse
import json
from pathlib import Path
from issue_reconcile import reconcile
from multi_task_pilot import SUPPORTED, run as execute

def run(queue_path, snapshot_path, root, limit=2):
    if not 1 <= limit <= 2:
        raise ValueError("Only two safe deterministic tasks may execute per run")
    inbox = reconcile(queue_path, snapshot_path, 10)
    if inbox["duplicate_conflicts"]:
        raise ValueError("Duplicate task Issues: manual resolution required")
    eligible = {item["task_id"] for item in inbox["already_present"]
                if item["issue"]["state"] == "open"}
    # Existing Issues are an additional gate, not an instruction source.
    # The canonical repository queue determines owner, dependencies and worker.
    output = execute(queue_path, root, limit)
    dispatched = [item for item in output["completed"] if item["task_id"] in eligible]
    skipped = [item["task_id"] for item in output["completed"] if item["task_id"] not in eligible]
    # Note: execute() is read-only and may audit unsupported-by-Issue tasks in
    # memory before filtering. Never claim those were dispatched from Issues.
    return {"schema_version": 1, "mode": "read_only_issue_gated_preview",
            "issue_dispatched": dispatched, "not_issue_eligible": skipped,
            "registered_workers": SUPPORTED, "issue_count": len(eligible),
            "github_writes": 0, "production_files_modified": False,
            "proxy_calls": 0, "youtube_publications": 0,
            "visual_approval": False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--queue", default="orchestrator/tasks.json")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--root", default=".")
    p.add_argument("--limit", type=int, default=2)
    p.add_argument("--output", required=True)
    a=p.parse_args()
    result=run(a.queue,a.snapshot,a.root,a.limit)
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"issue_dispatched":len(result["issue_dispatched"]),
                      "not_issue_eligible":len(result["not_issue_eligible"])}))

if __name__=="__main__":
    main()
