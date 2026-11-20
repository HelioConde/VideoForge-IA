"""Serial, zero-retry V3 generation: three real location backgrounds FIRST, then shots.

Stops on provider/canvas/archive/ambiguity errors. GitHub artifacts are not
equivalent to SHA-verified permanent history. Never autoapprove or publish.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import time

from videoforge.ep01_continuity_v3 import (
    EXPECTED_PLACES, EXPECTED_SHOTS, archived, prepare, load_plan
)

REPO="HelioConde/VideoForge-IA"
WORKFLOW="ep01-continuity-v3.yml"
REVIEW_WORKFLOW="ep01-continuity-v3-review.yml"


def cmd(*args,capture=False):
    result=subprocess.run(args,text=True,check=True,
                          stdout=subprocess.PIPE if capture else None,timeout=270)
    return result.stdout if capture else ""


def children():
    data=json.loads(cmd("gh","run","list","-R",REPO,"--workflow",WORKFLOW,
        "--event","workflow_dispatch","--limit","100",
        "--json","databaseId,displayTitle,status,conclusion",capture=True))
    if not isinstance(data,list):
        raise RuntimeError("EP01_V3_UNKNOWN_CHILD_LIST")
    return data


def refresh_main():
    cmd("git","fetch","--quiet","origin","main")
    cmd("git","reset","--hard","origin/main")


def main():
    if (not os.environ.get("GH_TOKEN")
        or os.environ.get("GITHUB_REPOSITORY")!=REPO
        or os.environ.get("GITHUB_REF")!="refs/heads/main"):
        raise RuntimeError("EP01_V3_QUEUE_MAIN_ONLY")
    load_plan()
    expected=[*EXPECTED_PLACES,*EXPECTED_SHOTS]
    for ident in expected:
        refresh_main()
        already=archived(ident)
        if already:
            print("EP01_V3_ARCHIVED_SKIP_BILLABLE",ident,already["sha256"],flush=True)
            continue
        item,images,refs,prompt=prepare(ident)
        before={x["databaseId"] for x in children()}
        print("EP01_V3_NEW_REQUEST",ident,"ref_shas",[x["sha256"][:9] for x in refs],flush=True)
        cmd("gh","workflow","run",WORKFLOW,"-R",REPO,"--ref","main",
            "-f",f"asset_id={ident}")
        child=None
        for _ in range(30):
            matched=[x for x in children()
                     if x["databaseId"] not in before
                     and ident in str(x.get("displayTitle",""))]
            if len(matched)>1:
                raise RuntimeError("EP01_V3_AMBIGUOUS_CHILD_NO_RETRY "+ident)
            if matched:
                child=matched[0]
                break
            time.sleep(8)
        if child is None:
            raise RuntimeError("EP01_V3_CHILD_NOT_DISCOVERABLE_NO_RETRY "+ident)
        rid=str(child["databaseId"])
        print("EP01_V3_CHILD_STARTED",ident,rid,flush=True)
        subprocess.run(["gh","run","watch",rid,"-R",REPO,
                        "--exit-status","--interval","15"],check=True)
        verified=False
        for _ in range(14):
            refresh_main()
            found=archived(ident)
            if found:
                verified=True
                print("EP01_V3_ARCHIVED_PROOF",ident,found["sha256"],rid,flush=True)
                break
            time.sleep(10)
        if not verified:
            raise RuntimeError("EP01_V3_ARCHIVE_NOT_VISIBLE "+ident+" "+rid)
    if any(archived(x) is None for x in expected):
        raise RuntimeError("EP01_V3_INCOMPLETE_GENERATION_NO_RENDER")
    # A valid PNG is still unapproved. Request a FULL CAMERA REVIEW MP4 only,
    # never animation, an artistic approval or a YouTube publication.
    cmd("gh","workflow","run",REVIEW_WORKFLOW,"-R",REPO,"--ref","main")
    print("EP01_V3_FULL_CAMERA_REVIEW_REQUESTED_42_SHOTS",flush=True)


if __name__=="__main__":
    try:
        main()
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as error:
        print("EP01_V3_QUEUE_STOP_NO_PAID_RETRY",type(error).__name__,
              str(error),file=sys.stderr,flush=True)
        raise SystemExit(2)
