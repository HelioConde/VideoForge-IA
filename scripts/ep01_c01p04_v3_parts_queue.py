"""Sequential GitHub Actions queue for independent C01-P04 V3 component images.

One provider-image call is made exclusively in each child workflow.
Safe to resume. No repeat on failure, no blind acceptance, no rig/render/upload.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

WORKFLOW="ep01-approved-v3-independent-part.yml"
SCHEMA="videoforge/ep01-c01p04-v3-parts-batch/v1"
REQUEST=Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PEDIDO-LOTE-PECAS-C01-P04-V3.json")

def command(*args: str, capture: bool=False) -> str:
    result=subprocess.run(args,text=True,check=True,
                          stdout=subprocess.PIPE if capture else None)
    return result.stdout if capture else ""

def gh_json(*args: str):
    return json.loads(command("gh",*args,capture=True))

def reload_repo():
    command("git","fetch","--quiet","origin","main")
    command("git","reset","--quiet","--hard","origin/main")

def recent_children() -> list[dict]:
    rows=gh_json("run","list","--workflow",WORKFLOW,"--event","workflow_dispatch",
                 "--limit","100","--json",
                 "databaseId,displayTitle,status,conclusion,createdAt")
    if not isinstance(rows,list):
        raise RuntimeError("EP01_V3_QUEUE_CHILD_LIST_INVALID")
    return rows

def dispatch(part: str) -> int:
    before={int(x["databaseId"]) for x in recent_children()}
    command("gh","workflow","run",WORKFLOW,"--ref","main","-f","part="+part)
    title="EP01 C01-P04 V3 / parte "+part
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        found=[x for x in recent_children()
               if int(x["databaseId"]) not in before
               and x.get("displayTitle")==title]
        if found:
            run_id=max(int(x["databaseId"]) for x in found)
            print("EP01_V3_QUEUE_CHILD",part,run_id,flush=True)
            return run_id
        time.sleep(10)
    raise RuntimeError("EP01_V3_QUEUE_CHILD_NOT_VISIBLE "+part)

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--max-new",type=int,default=6)
    args=parser.parse_args()
    if not os.environ.get("GH_TOKEN"):
        raise RuntimeError("EP01_V3_QUEUE_GITHUB_TOKEN_MISSING")
    from videoforge import ep01_approved_v3_parts as engine
    reload_repo()
    config=json.loads(REQUEST.read_text(encoding="utf-8"))
    if (config.get("schema")!=SCHEMA
        or config.get("channel")!="alchemy-lab"
        or config.get("video_id")!=engine.VIDEO
        or config.get("shot_id")!=engine.SHOT
        or config.get("approved_original_sha256")!=engine.SOURCE_SHA
        or config.get("one_paid_call_per_child") is not True
        or config.get("retry_on_failure") is not False
        or config.get("allow_spurious_parts") is not False
        or config.get("human_visual_approval") is not False
        or config.get("rig_ready") is not False
        or config.get("youtube_upload") is not False):
        raise RuntimeError("EP01_V3_QUEUE_CONFIG_INVALID")
    ordered=config.get("parts")
    if (not isinstance(ordered,list) or len(ordered)!=len(set(ordered))
        or not ordered or any(part not in engine.ROLE_CONFIG for part in ordered)
        or not 1<=args.max_new<=7):
        raise RuntimeError("EP01_V3_QUEUE_INVALID_PARTS")
    engine.aligned_source()
    completed=[]
    for part in ordered:
        if len(completed)>=args.max_new:
            break
        reload_repo()
        current=engine.existing_part(part)
        if current:
            print("EP01_V3_QUEUE_EXISTING",part,current["sha256"],flush=True)
            continue
        preflight=engine.prepare(part)
        print("EP01_V3_QUEUE_PREFLIGHT",part,
              "references",len(preflight["images"]),"source",
              preflight["source"]["sha256"],flush=True)
        run=dispatch(part)
        command("gh","run","watch",str(run),"--exit-status","--interval","15")
        for _ in range(8):
            reload_repo()
            existing=engine.existing_part(part)
            if existing:
                break
            time.sleep(5)
        else:
            raise RuntimeError("EP01_V3_QUEUE_SUCCESS_BUT_NO_SHA_ARCHIVE "+part)
        completed.append({"part":part,"run_id":run,"sha256":existing["sha256"]})
        print("EP01_V3_QUEUE_ARCHIVED",part,run,flush=True)
    print("EP01_V3_QUEUE_REPORT",json.dumps({
        "created":completed,
        "source_visual_approved":True,
        "parts_visual_approved":False,
        "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False,
    },ensure_ascii=False),flush=True)
    return 0

if __name__=="__main__":
    try:sys.exit(main())
    except (ValueError,OSError,RuntimeError,subprocess.CalledProcessError) as exc:
        print("EP01_V3_QUEUE_STOP_NO_RETRY",repr(exc),file=sys.stderr,flush=True)
        sys.exit(2)
