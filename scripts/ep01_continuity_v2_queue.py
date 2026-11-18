"""Sequence seven versioned image generations, one provider call per child Action."""
from __future__ import annotations
import json
import os
import subprocess
import sys
import time

REPO = "HelioConde/VideoForge-IA"
WORKFLOW = "ep01-continuity-v2.yml"
SHOTS = ["C07-P02","C07-P03","C08-P01","C08-P02","C08-P03","C08-P04","C08-P05"]

def command(*args, capture=False):
    r = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE if capture else None)
    return r.stdout if capture else ""

def child_runs():
    return json.loads(command("gh","run","list","-R",REPO,"--workflow",WORKFLOW,
                              "--event","workflow_dispatch","--limit","100",
                              "--json","databaseId,displayTitle,status,conclusion",capture=True))

def reload_main():
    command("git","fetch","--quiet","origin","main")
    command("git","reset","--hard","origin/main")

def main():
    if not os.environ.get("GH_TOKEN"):
        raise RuntimeError("GH_TOKEN_MISSING")
    for sid in SHOTS:
        reload_main()
        from videoforge.ep01_continuity_v2 import archived, prepare
        old = archived(sid)
        if old:
            print("SKIP_VERIFIED_ARCHIVE",sid,old["sha256"],flush=True)
            continue
        shot, images, refs, prompt = prepare(sid)
        before = {str(x["databaseId"]) for x in child_runs()}
        print("REQUEST_IMAGE",sid,"reference_images",len(refs),flush=True)
        command("gh","workflow","run",WORKFLOW,"-R",REPO,"--ref","main","-f",f"shot_id={sid}")
        matching = None
        for _ in range(24):
            matching = next((x for x in child_runs()
                             if str(x["databaseId"]) not in before
                             and sid in x.get("displayTitle","")),None)
            if matching:
                break
            time.sleep(10)
        if matching is None:
            raise RuntimeError(f"CHILD_NOT_VISIBLE {sid}")
        rid = str(matching["databaseId"])
        print("IMAGE_ACTION",sid,rid,flush=True)
        command("gh","run","watch",rid,"-R",REPO,"--exit-status","--interval","15")
        success = False
        for _ in range(12):
            reload_main()
            if archived(sid):
                success = True
                break
            time.sleep(10)
        if not success:
            raise RuntimeError(f"NO_ARCHIVE_AFTER_ACTION {sid} {rid}")
        print("ARCHIVED_PENDING_CREATOR_QA",sid,rid,flush=True)
    print("C07_C08_CONTINUITY_V2_SEVEN_MOTHERS_ARCHIVED_REVIEW_REQUIRED",flush=True)
    command("gh", "workflow", "run", "ep01-continuity-v2-review.yml", "-R", REPO, "--ref", "main")
    print("CONTINUITY_V2_42_SHOT_REVIEW_MP4_DISPATCHED",flush=True)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("STOP_NO_PAID_RETRY",repr(exc),file=sys.stderr,flush=True)
        raise SystemExit(2)
