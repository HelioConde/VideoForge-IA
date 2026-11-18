#!/usr/bin/env python3
"""Read-only recovery plan for a persisted task-state snapshot.

Never changes the canonical queue or reclaims a task on GitHub. Intended to
validate recovery decisions before a future atomic persistence integration.
"""
import argparse
import hashlib
import json
from pathlib import Path
from task_leases import recover

def sha(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def plan(snapshot_path, now):
    if not isinstance(now,int) or now<0:
        raise ValueError("Invalid timestamp")
    snapshot=json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    tasks=snapshot.get("tasks")
    if not isinstance(tasks,list):
        raise ValueError("Snapshot tasks must be a list")
    ids=[t.get("task_id") for t in tasks]
    if len(set(ids))!=len(ids) or any(not x for x in ids):
        raise ValueError("Duplicate or missing task IDs")
    decisions=[]
    for task in tasks:
        before=task.get("status")
        if before!="running":
            continue
        lease=task.get("lease")
        if not isinstance(lease,dict):
            decisions.append({"task_id":task["task_id"],"decision":"manual_review",
                              "reason":"running_without_lease"})
            continue
        if not isinstance(lease.get("expires_at"),int):
            decisions.append({"task_id":task["task_id"],"decision":"manual_review",
                              "reason":"invalid_lease_expiry"})
            continue
        if lease["expires_at"]>now:
            decisions.append({"task_id":task["task_id"],"decision":"still_running",
                              "expires_at":lease["expires_at"]})
            continue
        updated=recover(task,now)
        decisions.append({"task_id":task["task_id"],"decision":"retry_ready" if updated["status"]=="ready" else "retry_exhausted",
                          "previous_status":before,"proposed_status":updated["status"],
                          "attempts":updated.get("attempts",0),
                          "old_lease_key":lease.get("lease_key"),
                          "state_before_sha256":sha(task),
                          "state_after_sha256":sha(updated)})
    return {"schema_version":1,"mode":"recovery_plan_only","source_sha256":sha(snapshot),
            "decisions":decisions,"state_written":False,"github_writes":0,
            "worker_executions":0,"proxy_calls":0,"youtube_publications":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",required=True)
    p.add_argument("--now",type=int,required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=plan(args.snapshot,args.now)
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"decisions":len(result["decisions"]),"github_writes":0}))
if __name__=="__main__":
    main()
