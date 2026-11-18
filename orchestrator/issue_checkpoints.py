#!/usr/bin/env python3
"""Generate immutable, idempotent Issue checkpoint comment proposals.

This module never writes to GitHub. The Action validates and publishes these
comments only for open, uniquely matched task Issues after successful QA.
"""
import argparse
import hashlib
import json
from pathlib import Path

def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def prepare(dispatch_path, snapshot_path):
    dispatch=json.loads(Path(dispatch_path).read_text(encoding="utf-8"))
    issues=json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    if dispatch.get("mode")!="read_only_issue_gated_preview" or dispatch.get("github_writes")!=0:
        raise ValueError("Unsafe dispatch report")
    if not isinstance(issues,list):
        raise ValueError("Invalid Issue snapshot")
    result=[]
    for item in dispatch.get("issue_dispatched",[]):
        task_id=item["task_id"]
        if not item.get("qa_passed") or not item.get("result",{}).get("qa_12",{}).get("human_review_required"):
            continue
        matches=[x for x in issues if not x.get("pull_request") and x.get("state")=="open"
                 and ("<!-- videoforge-task:"+task_id+" -->") in (x.get("body") or "")]
        if len(matches)!=1:
            raise ValueError("Issue missing or duplicated for "+task_id)
        report_hash=digest(item["result"])
        token="videoforge-checkpoint:"+task_id+":"+report_hash[:20]
        body=("<!-- "+token+" -->\n"
              "## Checkpoint técnico automatizado (não é aprovação visual)\n"
              "- **Tarefa:** `"+task_id+"`\n"
              "- **Executor:** agente "+item["agent_id"]+" (Python determinístico)\n"
              "- **QA:** verificação técnica concluída; revisão humana pendente\n"
              "- **SHA-256 do relatório:** `"+report_hash+"`\n"
              "- **Limites:** sem IA, sem inspeção visual, sem proxy, sem publicação\n")
        result.append({"task_id":task_id,"issue_number":matches[0]["number"],
                       "marker":token,"body":body,"report_sha256":report_hash})
    return {"schema_version":1,"mode":"checkpoint_proposals_only",
            "comments":result,"github_writes":0,"human_approval":False,
            "proxy_calls":0,"youtube_publications":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dispatch",required=True)
    p.add_argument("--snapshot",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    data=prepare(a.dispatch,a.snapshot)
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"checkpoint_comments":len(data["comments"]),"github_writes":0}))
if __name__=="__main__":
    main()
