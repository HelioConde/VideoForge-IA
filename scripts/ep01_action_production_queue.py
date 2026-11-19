"""EP01: source-aware queue of ONE GitHub Action per image or preview shot.

The queue covers the current 42-shot continuity-v2 editorial timeline,
legacy per-part generation requests, and proposed rig-animation slots.
Mother/part SHAs are checked before any paid dispatch. Child image Actions
are limited to ONE proxy request; failures are permanently fenced, not retried.
Remote CAS reservation happens BEFORE child dispatch. No auto art approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import tempfile

from orchestrator.github_state import GitHubState
from videoforge import ep01_camera_batch as camera
from videoforge import ep01_proxy_separate_parts as parts
from videoforge import image_generation_policy

ROOT = Path(__file__).resolve().parents[1]
EP = Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
PLAN = EP / "PLANO-CAMADAS-CAMERA-EP01.json"
POLICY = EP / "autonomy-policy.json"
STATE_PATH = "runtime/ep01-production-action-queue-v1.json"
SCHEMA = "videoforge/ep01-production-action-queue/v1"
STATE_SCHEMA = "videoforge/ep01-production-action-queue-state/v1"
IMAGE_WORKFLOW = "ep01-proxy-separate-part-by-request.yml"
PREVIEW_WORKFLOW = "ep01-camera-batch-preview.yml"
CONTINUITY_SHOTS = {"C07-P01", "C07-P02", "C07-P03", "C07-P04",
                    "C08-P01", "C08-P02", "C08-P03", "C08-P04", "C08-P05"}
SHOTS_BLOCKED_FROM_LEGACY_PARTS = CONTINUITY_SHOTS | {"C01-P02", "C01-P04"}
SPECIAL_C08 = (
    ("C08-P02", "character-kael-v3", "new version must integrate both grip hands to the SAME archived V2 cart"),
    ("C08-P02", "object-wheel-left-v1", "requires approved cart wheel geometry/transparent part prompt"),
    ("C08-P02", "object-wheel-right-v1", "requires approved cart wheel geometry/transparent part prompt"),
    ("C08-P03", "object-carrinho-v2", "requires the SAME physical identity and 90-degree pose as C08-P02"),
)
CHILD = {"image": IMAGE_WORKFLOW, "image_correction": IMAGE_WORKFLOW, "camera_preview": PREVIEW_WORKFLOW}


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1<<20), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise ValueError("Missing or unsafe EP01 source file: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def policy_guard(root: Path) -> None:
    policy=load_json(root/POLICY)
    if (policy.get("scope")!="alchemy-lab/mmorpg-conquiste-a-princesa-ep01"
        or policy.get("paid_provider_calls_approved") is not True
        or policy.get("auto_dispatch_generation") is not True
        or policy.get("max_chargeable_calls_per_run") != 1
        or policy.get("human_visual_review_required_for_canonical_identity") is not True
        or policy.get("auto_publish_youtube") is not False):
        raise ValueError("EP01 standing authorization / safety gates changed")
    image_generation_policy.assert_image_generation_allowed(
        "alchemy-lab","mmorpg-conquiste-a-princesa-ep01",root)


def id_for(kind: str, shot: str, part: str | None, source_sha: str) -> str:
    raw=f"{kind}:{shot}:{part or '-'}:{source_sha[:20]}"
    if not re.fullmatch(r"[A-Za-z0-9_:\-]+",raw):
        raise ValueError("Unsafe action task identifier")
    return raw


def build(root:Path=ROOT) -> dict:
    root=Path(root).resolve()
    policy_guard(root)
    legacy=load_json(root/PLAN)
    camera_plan=camera.build_plan(root,"continuity-v2")
    if (len(legacy["shots"])!=40 or len(camera_plan["shots"])!=42
            or camera_plan.get("revision")!="continuity-v2"
            or sum(s["duration_frames"] for s in camera_plan["shots"])!=4890):
        raise ValueError("EP01 editorial 42-shot source plan drift")
    indexed={shot["id"]:shot for shot in camera_plan["shots"]}
    if len(indexed)!=42:
        raise ValueError("Duplicate 42-shot EDL IDs")
    tasks=[]
    known=set()
    def add(kind,shot,part,source_sha,status,why,agent,priority):
        if not isinstance(source_sha,str) or len(source_sha)!=64:
            raise ValueError("Image/plan origin SHA missing")
        tid=id_for(kind,shot,part,source_sha)
        if tid in known:
            raise ValueError("Duplicate task identity "+tid)
        known.add(tid)
        tasks.append({"task_id":tid,"kind":kind,"shot_id":shot,
                      "part":part,"source_sha256":source_sha,
                      "status":status,"reason":why,"owner":agent,
                      "reviewer":"12","priority":priority,
                      "paid_image_requests_per_child":1 if kind in ("image","image_correction") else 0,
                      "human_visual_approval":False,"rig_ready":False,
                      "youtube_publication":False})
    # Every image mother is already archived for this current 42-shot plan.
    for i,shot in enumerate(camera_plan["shots"]):
        sid=shot["id"]
        mother=shot["source"]
        if mother:
            image=camera.checked_source(root,mother)  # exact pinned SHA/dimensions
            origin=digest(image)
        else:
            if sid!="C01-P01":
                raise ValueError("Unexpected black/empty source in 42-shot EDL")
            origin=digest(root/PLAN)
        add("mother",sid,None,origin,"archived" if mother else "not_required",
            "V2 source remains a visual candidate, not a rig approval", "05",0)
        if mother:
            tasks[-1].update(source_file=mother["file"], file_sha256=origin)
    # All 146 requests in the original planning document remain represented.
    for shot in legacy["shots"]:
        sid=shot["id"]
        components=shot.get("images",{}).get("proxy_generation_requests",[])
        if sid=="C01-P01":
            if components:
                raise ValueError("Black C01-P01 has image-generation requests")
            continue
        frame=indexed.get(sid)
        if frame is None:
            raise ValueError("Legacy shot is missing from revised 42-shot EDL: "+sid)
        mother=frame["source"]
        if not mother:
            raise ValueError("Layer task lacks scene image")
        for part in components:
            name=part["id"]
            if (part.get("method")!="proxy_generated_separate_image"
                    or not re.fullmatch(r"(background-clean|character-[a-z0-9_-]+|object-[a-z0-9_-]+)",name)):
                raise ValueError("Unsafe or unsupported image request")
            previous=parts.existing_part(sid,name,root)
            if previous:
                metadata=load_json(root/Path(previous["file"]).with_suffix(".production.json"))
                if (metadata.get("sha256")!=previous["sha256"]
                        or metadata.get("source_mother_sha256") is None
                        or metadata.get("human_visual_approval") is not False):
                    raise ValueError("Unverified archived image source or approval state")
                rejected=str(metadata.get("technical_qa","")).startswith("rejected_")
                status="archived_rejected_needs_review" if rejected else "archived"
                reason=("Existing provider image rejected by technical QA; "
                        "never repeat payment automatically" if rejected else
                        "SHA-verified independently generated candidate already archived")
            else:
                status="ready_for_preflight"
                reason="source-bound one-image child workflow"
            if sid in SHOTS_BLOCKED_FROM_LEGACY_PARTS:
                status="archived_version_check_needed" if previous else "blocked_reference_revision"
                reason=(
                    "C07/C08 continuity V2: old image-part plan cannot be used as a proxy for the approved framing"
                    if sid in CONTINUITY_SHOTS else
                    "C01-P02 source mother rejected; build corrected mother first"
                    if sid=="C01-P02" else
                    "C01-P04: preserve individually approved V3 and do not generate standalone hands"
                )
            elif shot.get("qa",{}).get("require_versioned_mother_v2_before_more_proxy_parts") is True:
                status="blocked_reference_revision"
                reason="shot-specific QA forbids reusing the old mother"
            add("image",sid,name,mother["sha256"],status,reason,"05",10)
            if previous:
                tasks[-1].update(source_file=previous["file"], file_sha256=previous["sha256"])
    # These are explicit NEW V2 revision requirements; they do NOT silently
    # route through the older image prompts, nor inherit past art approval.
    c08_sha=indexed["C08-P02"]["source"]["sha256"]
    c08p03_sha=indexed["C08-P03"]["source"]["sha256"]
    for sid,part,reason in SPECIAL_C08:
        state="blocked_needs_shot_specific_prompt_and_art_qa"
        if (sid,part)==("C08-P02","character-kael-v3"):
            version=parts.existing_part(sid,part,root)
            if version:
                meta=load_json(root/Path(version["file"]).with_suffix(".production.json"))
                state="archived_rejected_needs_review" if meta["technical_qa"].startswith("rejected") else "archived"
            else:
                state="ready_for_preflight"
        add("image_correction",sid,part,c08_sha if sid=="C08-P02" else c08p03_sha,
            state,reason,"05",1)
    # Technical camera previews are ALLOWED, not character animation.
    for i,shot in enumerate(camera_plan["shots"]):
        sid=shot["id"]
        source=shot["source"]
        src_sha=source["sha256"] if source else digest(root/PLAN)
        add("camera_preview",sid,None,src_sha,"ready_for_preflight",
            "technical 30fps camera-only preview; source image remains unapproved", "09",20+i)
        add("rig_animation",sid,None,src_sha,"blocked_waiting_for_verified_rgba_and_rig",
            "requires independent genuine RGBA pieces, motion QA, then human visual acceptance; not camera-only", "08",100+i)
    tallies={}
    for task in tasks:
        k=task["kind"]+":"+task["status"]
        tallies[k]=tallies.get(k,0)+1
    return {
        "schema":SCHEMA,"source_revision":"continuity-v2",
        "shots":42,"original_image_requests":146,
        "total_tasks":len(tasks),
        "per_child_paid_image_cap":1,
        "scope":"alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
        "original_art_modified":False,"image_approval_automatic":False,
        "rig_approval_automatic":False,"youtube_publication":False,
        "status_counts":tallies,"tasks":tasks,
    }


class QueueRemote(GitHubState):
    """Separate small CAS ledger: reserved means NEVER launch again blindly."""
    @staticmethod
    def _validate_snapshot(data:dict)->None:
        if (not isinstance(data,dict)
                or data.get("schema_version")!=1
                or data.get("schema")!=STATE_SCHEMA
                or set(data)!={"schema_version","schema","attempts"}
                or not isinstance(data["attempts"],dict)
                or len(data["attempts"])>1000):
            raise ValueError("Invalid production queue state")
        for key,value in data["attempts"].items():
            if (not isinstance(key,str) or len(key)>200
                    or not isinstance(value,dict)
                    or value.get("status") not in {
                        "reserved","dispatched","archived","preview_complete",
                        "blocked_uncertain","blocked_failed","blocked_preflight","rejected_archived"}
                    or not isinstance(value.get("workflow"),str)):
                raise ValueError("Invalid queue attempt state")


def gh(*args:str, json_out:bool=False):
    command=["gh",*args]
    result=subprocess.run(command,check=True,text=True,capture_output=True,timeout=150)
    return json.loads(result.stdout) if json_out else result.stdout


def child_runs(workflow:str):
    rows=gh("run","list","--workflow",workflow,"--event","workflow_dispatch",
            "--limit","100","--json","databaseId,status,conclusion,createdAt",
            json_out=True)
    if not isinstance(rows,list):
        raise ValueError("GitHub workflow run listing invalid")
    return rows


def dispatch_child(task:dict)->int:
    workflow=CHILD[task["kind"]]
    before={int(row["databaseId"]) for row in child_runs(workflow)}
    if task["kind"] in ("image","image_correction"):
        gh("workflow","run",workflow,"--ref","main",
           "-f","shot_id="+task["shot_id"],
           "-f","part="+task["part"])
    elif task["kind"]=="camera_preview":
        gh("workflow","run",workflow,"--ref","main",
           "-f","shots="+task["shot_id"],"-f","revision=continuity-v2")
    else:
        raise ValueError("Workflow not supported")
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        rows=[row for row in child_runs(workflow)
              if int(row["databaseId"]) not in before]
        if len(rows)==1:
            return int(rows[0]["databaseId"])
        if len(rows)>1:
            raise RuntimeError("Ambiguous child Actions IDs; no retry")
        time.sleep(7)
    raise RuntimeError("New child Action not visible; no retry")


def reload_main():
    subprocess.run(["git","fetch","--quiet","origin","main"],check=True,timeout=120)
    subprocess.run(["git","reset","--hard","origin/main"],check=True,
                   stdout=subprocess.DEVNULL,timeout=60)


def verify_child(task:dict,run_id:int):
    if task["kind"] in ("image","image_correction"):
        reload_main()
        item=parts.existing_part(task["shot_id"],task["part"])
        if not item or not re.fullmatch(r"[a-f0-9]{64}",item["sha256"]):
            raise ValueError("Child returned but independently generated PNG was not archived by SHA")
        path=ROOT/item["file"]
        metadata=load_json(path.with_suffix(".production.json"))
        if (path.parent.name!=str(run_id) or digest(path)!=item["sha256"]
                or metadata.get("source_mother_sha256")!=task["source_sha256"]
                or metadata.get("technical_qa") not in {"candidate_proxy_generated_separate_image",
                                                     "candidate_minor_edge_delta_requires_alignment_qa",
                                                     "candidate_native_model_canvas_requires_placement_qa"}):
            raise ValueError("Archived candidate differs from child, pinned mother or expected technical QA")
        return {"status":"archived","technical_qa":metadata["technical_qa"],"sha256":item["sha256"],
                "source_file":item["file"]}
    if task["kind"]=="camera_preview":
        repo=os.getenv("GH_REPO","HelioConde/VideoForge-IA")
        data=gh("api",f"repos/{repo}/actions/runs/{run_id}/artifacts",json_out=True)
        archive=[a for a in data.get("artifacts",[])
                 if a.get("name")==f"ep01-camera-batch-{run_id}" and
                 a.get("expired") is False and a.get("size_in_bytes",0)>0]
        if len(archive)!=1:
            raise ValueError("Camera Action has no verified nonempty artifact")
        return {"status":"preview_complete","artifact_id":archive[0]["id"],
                "technical_camera_only":True,"animation_rig_approved":False}
    raise ValueError("Unsupported production task kind")


def reconcile_rejected_archives(plan:dict,remote:QueueRemote,ledger:dict)->list[str]:
    """Repair only proven REJECTED archived results, without replaying a call.

    Unlike a network-unknown reservation, a failed child with an archived PNG
    and rejected technical QA is known to have billed/produced an image.
    Mark it as terminal/rejected, not completed or retried. Refuse to
    reconcile if the archival source SHA, run ID or actual child status differ.
    """
    changed=[]
    items={task["task_id"]:task for task in plan["tasks"]}
    for key,entry in ledger["attempts"].items():
        if (entry.get("status")!="blocked_failed"
                or entry.get("workflow")!=IMAGE_WORKFLOW):
            continue
        item=items.get(key)
        child=entry.get("child_run_id")
        if (not item or item["kind"] not in ("image","image_correction") or type(child) is not int
                or child<1 or entry.get("source_sha256")!=item["source_sha256"]):
            continue
        archived=parts.existing_part(item["shot_id"],item["part"])
        if not archived:
            continue
        meta=load_json(ROOT/Path(archived["file"]).with_suffix(".production.json"))
        if (meta.get("sha256")!=archived["sha256"]
                or meta.get("source_mother_sha256")!=item["source_sha256"]
                or meta.get("asset_id")!=item["shot_id"].lower()+"-"+item["part"]
                or not str(meta.get("technical_qa","")).startswith("rejected_")
                or meta.get("human_visual_approval") is not False
                or meta.get("rig_ready") is not False
                or meta.get("youtube_uploaded") is not False
                or f"/{child}/" not in "/"+archived["file"]):
            continue
        repository=os.environ.get("GH_REPO","HelioConde/VideoForge-IA")
        child_report=gh("api",f"repos/{repository}/actions/runs/{child}",json_out=True)
        if (child_report.get("conclusion")!="failure"
                or child_report.get("event")!="workflow_dispatch"
                or child_report.get("head_branch")!="main"):
            continue
        entry.update({
            "status":"rejected_archived",
            "sha256":archived["sha256"],
            "source_file":archived["file"],
            "technical_qa":meta["technical_qa"],
            "needs_human_visual_review":True,
            "cannot_be_used_as_approved_rig":True,
            "youtube_publication":False,
        })
        remote.save(ledger)
        changed.append(key)
    return changed



def reconcile_failed_preflight(plan:dict,remote:QueueRemote,ledger:dict)->list[str]:
    """Fence verified child failures BEFORE proxy invocation, without replay.

    A failed workflow run by itself is insufficient evidence. Require the
    exact child, pinned task, a failed validation step, and a skipped provider
    step; otherwise leave the hard stop in place.
    """
    changed=[]
    by_id={task["task_id"]:task for task in plan["tasks"]}
    repository=os.environ.get("GH_REPO","HelioConde/VideoForge-IA")
    for key,entry in ledger["attempts"].items():
        if entry.get("status")!="blocked_failed" or entry.get("workflow")!=IMAGE_WORKFLOW:
            continue
        task=by_id.get(key)
        child=entry.get("child_run_id")
        if (not task or task["kind"]!="image" or type(child) is not int or child<1
                or entry.get("source_sha256")!=task["source_sha256"]):
            continue
        # No artifact or existing generated part may be present.
        if parts.existing_part(task["shot_id"],task["part"]):
            continue
        run=gh("api",f"repos/{repository}/actions/runs/{child}",json_out=True)
        if (run.get("conclusion")!="failure" or run.get("event")!="workflow_dispatch"
                or run.get("head_branch")!="main"
                or not str(run.get("path","")).endswith("/"+IMAGE_WORKFLOW)):
            continue
        jobs=gh("api",f"repos/{repository}/actions/runs/{child}/jobs",json_out=True).get("jobs",[])
        if len(jobs)!=1 or jobs[0].get("name")!="gerar-imagem-separada":
            continue
        steps={step.get("name"):step.get("conclusion") for step in jobs[0].get("steps",[])}
        if (steps.get("Validar 39 planos, PNG-mãe e componente sem pagar proxy")!="failure"
                or steps.get("Gerar uma imagem NOVA pelo proxy sem recortar a mae")!="skipped"):
            continue
        artifact=gh("api",f"repos/{repository}/actions/runs/{child}/artifacts",json_out=True)
        if artifact.get("total_count",0)!=0 or artifact.get("artifacts"):
            continue
        entry.update({"status":"blocked_preflight",
                      "reason":"child_validation_failed_before_provider",
                      "provider_step":"skipped","provider_calls_confirmed":0,
                      "review_required":True,"retry_original_task":False})
        remote.save(ledger)
        changed.append(key)
    return changed


def publish_active_child(task:dict, child_id:int) -> None:
    """Display the reserved child on the dashboard; status publishing cannot replay a child."""
    if os.environ.get("EP01_SHOW_ACTIVE_CHILD") != "true":
        return
    try:
        dashboard=gh("api","repos/HelioConde/VideoForge-IA/issues/98",json_out=True)
        body=dashboard["body"]
        marker="<!-- videoforge-ep01-production-queue:v1 -->"
        active_marker="<!-- ep01-active-child -->"
        if dashboard["state"]!="open" or not body.startswith(marker):
            return
        lines=[line for line in body.splitlines() if not line.startswith(active_marker)]
        lines.insert(2, f"{active_marker} **Em processamento:** Agente {task['owner']} · "
                     f"{task['shot_id']} · {task.get('part') or task['kind']} · "
                     f"[Action {child_id}](https://github.com/HelioConde/VideoForge-IA/actions/runs/{child_id})")
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"panel.md"
            path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            gh("issue","edit","98","--body-file",str(path))
    except (subprocess.SubprocessError,OSError,ValueError,KeyError,TypeError):
        print("EP01_DASHBOARD_UPDATE_UNAVAILABLE",flush=True)


def run_remote(plan:dict,max_images:int,max_previews:int)->dict:
    if (not os.getenv("GH_TOKEN") or not os.getenv("GITHUB_TOKEN")
            or os.getenv("GITHUB_REPOSITORY")!="HelioConde/VideoForge-IA"
            or os.getenv("GITHUB_REF")!="refs/heads/main"):
        raise ValueError("GitHub Actions main-only authenticated queue required")
    if not (0<=max_images<=20 and 0<=max_previews<=12
            and max_images+max_previews>0):
        raise ValueError("Bounded queue batch limits required")
    remote=QueueRemote(
        path=STATE_PATH,branch="state/multi-agent-runtime",initialize=True)
    ledger=remote.load()
    if ledger is None:
        ledger={"schema_version":1,"schema":STATE_SCHEMA,"attempts":{}}
    attempts=ledger["attempts"]
    reconciled=reconcile_rejected_archives(plan,remote,ledger)
    if reconciled:
        print("EP01_REJECTED_SOURCE_ARCHIVED_NO_REBILL",
              json.dumps(reconciled,ensure_ascii=False),flush=True)
    preflight_reconciled=reconcile_failed_preflight(plan,remote,ledger)
    if preflight_reconciled:
        print("EP01_PROVEN_PREFLIGHT_FAILURE_NO_PROVIDER_NO_REPLAY",
              json.dumps(preflight_reconciled,ensure_ascii=False),flush=True)
    # Explicit freeze on any unresolved previous external side effect. Never
    # rerun an uncertain billed call just because the current job restarted.
    uncertain=[k for k,v in attempts.items() if v["status"] in
               {"reserved","dispatched","blocked_uncertain","blocked_failed"}]
    if uncertain:
        raise RuntimeError("EP01_QUEUE_UNRESOLVED_EXTERNAL_ATTEMPT "+",".join(uncertain[:5]))
    results=[]
    counters={"image":0,"camera_preview":0}
    for task in sorted(plan["tasks"],key=lambda t:(t["priority"],t["task_id"])):
        kind="image" if task["kind"]=="image_correction" else task["kind"]
        if kind not in CHILD or task["status"]!="ready_for_preflight":
            continue
        limit=max_images if kind=="image" else max_previews
        if counters[kind]>=limit:
            continue
        key=task["task_id"]
        if key in attempts:
            continue
        # Never send a child with unverified scene/reference bytes.
        if kind=="image":
            try:
                current=parts.existing_part(task["shot_id"],task["part"])
                if current:
                    # Source archive changed since the initial planning run:
                    # omit from queue rather than overwrite/charge again.
                    continue
                pre=parts.prepare(task["shot_id"],task["part"])
                if pre["mother_proof"]["sha256"]!=task["source_sha256"]:
                    raise ValueError("Scene mother changed after queue plan")
            except (ValueError,OSError,RuntimeError) as exc:
                # Enqueue a source-specific BLOCK, never bill when preflight fails.
                attempts[key]={"status":"blocked_preflight","workflow":IMAGE_WORKFLOW,
                               "reason":type(exc).__name__,"source_sha256":task["source_sha256"]}
                remote.save(ledger)
                results.append({"task_id":key,"status":"blocked_preflight",
                                "reason":type(exc).__name__})
                continue
        # Save the hard anti-duplicate reservation BEFORE invoking external
        # workflow_dispatch. If a host/network failure happens in between, the
        # reserved task remains blocked for explicit human reconciliation.
        attempts[key]={"status":"reserved","workflow":CHILD[kind],
                       "source_sha256":task["source_sha256"],
                       "reserved_by_run":os.getenv("GITHUB_RUN_ID","")}
        remote.save(ledger)
        started=time.monotonic()
        child_id=None
        try:
            child_id=dispatch_child(task)
            attempts[key]["status"]="dispatched"
            attempts[key]["child_run_id"]=child_id
            remote.save(ledger)
            publish_active_child(task,child_id)
            gh("run","watch",str(child_id),"--exit-status","--interval","15")
            proven=verify_child(task,child_id)
            attempts[key]["elapsed_seconds"]=int(time.monotonic()-started)
            attempts[key].update(proven)
            remote.save(ledger)
            results.append({"task_id":key,"child_run_id":child_id,**proven})
            counters[kind]+=1
        except (subprocess.CalledProcessError,subprocess.TimeoutExpired,
                ValueError,RuntimeError,OSError) as exc:
            attempts[key]["status"]="blocked_failed" if child_id else "blocked_uncertain"
            attempts[key]["elapsed_seconds"]=int(time.monotonic()-started)
            attempts[key]["failure_type"]=type(exc).__name__
            remote.save(ledger)
            # If the failed child generated a real PNG and archived it with
            # rejected technical QA, reconcile that exact billed attempt.
            # Never retry it. Preserve failures with unknown side effects.
            if child_id and kind=="image":
                reload_main()
                rejected=reconcile_rejected_archives(plan,remote,ledger)
                if key in rejected:
                    results.append({"task_id":key,"child_run_id":child_id,
                                    "status":"rejected_archived",
                                    "technical_qa":attempts[key]["technical_qa"]})
                    counters[kind]+=1
                    print("EP01_REJECTED_CHILD_RECONCILED_NO_REPLAY",
                          key,child_id,flush=True)
                    continue
            raise RuntimeError("EP01_QUEUE_CHILD_FAILED_NO_RETRY "+
                               key+" run="+str(child_id or "unknown")) from None
    return {"executed":results,"processed_images":counters["image"],
            "processed_camera_previews":counters["camera_preview"],
            "external_workflow_dispatch_calls":sum(counters.values()),
            "human_visual_approval":False,"rig_ready":False,
            "youtube_publications":0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=["plan","run"],default="plan")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--max-images",type=int,default=2)
    parser.add_argument("--max-previews",type=int,default=2)
    args=parser.parse_args()
    plan=build()
    payload={"queue":plan}
    if args.mode=="run":
        payload["execution"]=run_remote(plan,args.max_images,args.max_previews)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({"shots":plan["shots"],"tasks":plan["total_tasks"],
                      "status_counts":plan["status_counts"],
                      "execution":payload.get("execution")},ensure_ascii=False))


if __name__=="__main__":
    try:
        main()
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as exc:
        print("EP01_ACTION_QUEUE_STOP_NO_RETRY",type(exc).__name__,str(exc),
              file=sys.stderr,flush=True)
        raise SystemExit(2)
