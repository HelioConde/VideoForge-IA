#!/usr/bin/env python3
"""Optimistic-concurrency state transitions for future GitHub-backed task storage.

Pure functions: caller must compare expected revision and persist atomically.
No GitHub writes, paid calls or worker execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
from task_leases import claim, recover, checkpoint

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def transition(state, task_id, operation, expected_revision, now, worker=None,
               token=None, evidence=None):
    if not isinstance(state,dict) or not isinstance(state.get("tasks"),list):
        raise ValueError("Invalid state")
    if expected_revision!=digest(state):
        raise ValueError("State revision conflict")
    matches=[i for i,t in enumerate(state["tasks"]) if t.get("task_id")==task_id]
    if len(matches)!=1:
        raise ValueError("Task not uniquely identified")
    index=matches[0]
    old=state["tasks"][index]
    if operation=="claim":
        new=claim(old,worker,now)
    elif operation=="recover":
        new=recover(old,now)
    elif operation=="checkpoint":
        new=checkpoint(old,worker,token,evidence,now)
    else:
        raise ValueError("Unsupported operation")
    updated=json.loads(json.dumps(state))
    updated["tasks"][index]=new
    return {"schema_version":1,"mode":"proposed_atomic_transition",
            "task_id":task_id,"operation":operation,
            "previous_revision":expected_revision,
            "next_revision":digest(updated),"next_state":updated,
            "changed":digest(updated)!=expected_revision,
            "persisted":False,"github_writes":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",required=True)
    p.add_argument("--task-id",required=True)
    p.add_argument("--operation",choices=["claim","recover"],required=True)
    p.add_argument("--now",type=int,required=True)
    p.add_argument("--worker")
    p.add_argument("--expected-revision",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    state=json.loads(Path(a.snapshot).read_text(encoding="utf-8"))
    result=transition(state,a.task_id,a.operation,a.expected_revision,a.now,a.worker)
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"task_id":a.task_id,"changed":result["changed"],
                      "persisted":False,"next_revision":result["next_revision"]}))
if __name__=="__main__":
    main()
