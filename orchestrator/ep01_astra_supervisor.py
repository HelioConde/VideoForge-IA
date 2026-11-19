"""One-shot REAL Astra supervisory handoff over SIX verified technical tool outputs.

Agent 01 proposes source-pinned work orders; Agent 12 independently reviews;
Agent 01 consolidates. Three and ONLY three unpriced model calls, bounded by a
durable 100k conservative token allowance. Historical tool work is reopened
and verified, not regenerated. No model is given production tools.
"""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
import tempfile

from videoforge.ep01_cart_kinematics import HOLD_FRAME_COUNT, HOLD_SHOT, SOURCE_FRAME_COUNT, TURN_SHOT

from .agent_bus import fingerprint
from .agent_live_roundtrip import ensure_response
from .ep01_specialist_dispatch import CONTRACT as TECH_CONTRACT, RUN_SEQUENCE, SPECS, STATE as TECH_STATE
from .github_state import GitHubState
from .providers import ProviderError
from .runtime import ROOT, MANIFEST, instructions, model_step, report, source, write_report
from .runtime_store import BudgetBlocked, Conflict, Store

CONTRACT="ep01-six-tool-astra-supervision-v1"
STATE="runtime/ep01-astra-supervisor-v1.json"
N_CALLS=3
EXPECTED=["01","12","01"]


def verified_technical_journal(snapshot:dict, *, root=ROOT) -> dict:
    with tempfile.TemporaryDirectory(prefix="vf-ep01-verify-specialists-") as folder:
        store=Store(Path(folder)/"tech.sqlite")
        try:
            store.import_snapshot(snapshot)
            data=report(store,root=root)
            rows=data["tasks"]
            cps={c["task_id"]:c for c in data["checkpoints"]}
            if (len(rows)!=6 or len(cps)!=6 or data["usage"]
                    or data["safety"]["youtube_publications"]!=0):
                raise ValueError("Six-role technical journal is incomplete")
            evidence={}
            for row in rows:
                role=row.get("owner")
                cp=cps.get(row["task_id"])
                if (role not in RUN_SEQUENCE or role in evidence
                        or row.get("reviewer")!="12"
                        or row.get("source_scope")!=TECH_CONTRACT
                        or row.get("status")!="completed"
                        or not cp or cp.get("result_sha256")!=row["result_sha256"]
                        or cp.get("review",{}).get("agent_id")!="12"
                        or cp.get("review",{}).get("technical_passed") is not True
                        or cp.get("human_visual_approval") is not False
                        or cp.get("scope")!="read_only_technical_audit"):
                    raise ValueError("Specialist role or independent QA proof is invalid")
                for rel,digest in row["input_refs"].items():
                    from .ep01_specialist_dispatch import pinned_file
                    pinned_file(root,rel,digest)
                result=store.result(row["task_id"])
                payload=result.get("evidence")
                if (result.get("agent_id")!=role
                        or not isinstance(payload,dict)
                        or result.get("evidence_sha256")!=fingerprint(payload)
                        or payload.get("role_id")!=role
                        or payload.get("new_model_calls")!=0
                        or payload.get("new_generated_image_calls")!=0
                        or payload.get("human_visual_approval") is not False
                        or payload.get("youtube_publication") is not False
                        or not payload.get("outputs_sha256")):
                    raise ValueError("Specialist output does not match archived execution")
                role_evidence={
                    "role_id":role,"operation":SPECS[role][0],
                    "checkpoint_sha256":cp["sha256"],
                    "result_sha256":row["result_sha256"],
                    "output_hashes":payload["outputs_sha256"],
                    "observed_output":payload["outcome"],
                    "original_execution_run_id":result.get("origin_run_id"),
                    "media_and_visual_approved":False,
                }
                evidence[role]={
                    **role_evidence,
                    "evidence_sha256":fingerprint(role_evidence),
                }
            if set(evidence)!=set(RUN_SEQUENCE):
                raise ValueError("Six source-bound specialist roles not all completed")
            return {
                "source_snapshot_sha256":fingerprint(snapshot),
                "source_state_sha256":data["state_sha256"],
                "specialist_evidence":{role:evidence[role] for role in RUN_SEQUENCE},
                "verified_role_count":6,
                "model_calls_performed_for_this_verification":0,
                "approved_for_real_rig":False,
            }
        finally:
            store.close()


def seed(store:Store,evidence:dict,*,root=ROOT,model:str) -> str:
    if model not in ("gpt-6.2-astra","gpt-6-astra"):
        raise ValueError("Only the catalog-pinned Astra models are allowed")
    _,manifest_sha=source(root,MANIFEST.as_posix())
    shas={a:instructions(root,a)[1] for a in ("01","12")}
    identifier=fingerprint({"scope":CONTRACT,"model":model,"manifest":manifest_sha,
                            "source_snapshot":evidence["source_snapshot_sha256"],
                            "instructions":shas})[:16]
    task_id="EP01-ASTRA-HANDOFF-"+identifier
    store.enqueue({
        "task_id":task_id,"owner":"01","reviewer":"12",
        "operation":"read_only_analysis","mode":"codex_proxy",
        "input_refs":{MANIFEST.as_posix():manifest_sha,
                      TECH_STATE:evidence["source_snapshot_sha256"]},
        "instructions_shas":shas,"priority":0,
        "max_attempts":1,"stop_on_review_rejection":True,
        "human_visual_approval":False,"scope":CONTRACT,
        "limit_calls":N_CALLS,"model":model,
        "six_technical_snapshot_sha256":evidence["source_snapshot_sha256"],
        "evidence_digest":fingerprint(evidence["specialist_evidence"]),
    })
    return task_id


def validate_proposals(data:dict,evidence:dict) -> None:
    if len(data.get("findings",[]))!=6:
        raise ProviderError("Director must assign exactly six source-bound next steps")
    for role,row in zip(RUN_SEQUENCE,data["findings"]):
        if (not isinstance(row,dict) or set(row)!={"role_id","evidence_sha256",
                "next_action","blockers","production_ready"}
                or row["role_id"]!=role
                or row["evidence_sha256"]!=evidence["specialist_evidence"][role]["evidence_sha256"]
                or row["production_ready"] is not False
                or not isinstance(row["next_action"],str)
                or not 8<=len(row["next_action"].strip())<=1200
                or not isinstance(row["blockers"],list) or not row["blockers"]
                or any(not isinstance(x,str) or not x.strip() for x in row["blockers"])):
            raise ProviderError("Director proposal is missing verified source and blocking context")


def validate_qa(data:dict,evidence:dict) -> bool:
    if len(data.get("findings",[]))!=6:
        raise ProviderError("Agent 12 omitted a specialist review")
    for role,row in zip(RUN_SEQUENCE,data["findings"]):
        if (not isinstance(row,dict)
                or set(row)!={"role_id","evidence_sha256","decision","reason"}
                or row["role_id"]!=role
                or row["evidence_sha256"]!=evidence["specialist_evidence"][role]["evidence_sha256"]
                or row["decision"] not in {"supported","correction_requested","insufficient_evidence"}
                or not isinstance(row["reason"],str) or not row["reason"].strip()):
            raise ProviderError("Agent 12 decision is not independently source-bound")
    return all(row["decision"]=="supported" for row in data["findings"])


MOTION_TOTAL = SOURCE_FRAME_COUNT + HOLD_FRAME_COUNT
FRAME_CLAIM = re.compile(
    rf"\b(?:{MOTION_TOTAL}[\s-]+(?:quadros?|frames?|poses?|fotogramas?)|"
    rf"(?:quadros?|frames?|poses?|fotogramas?)\s*[:=]\s*{MOTION_TOTAL})\b", re.I)
SHOT_ID = re.compile(r"\b(C\d+)-(P\d+)(?:\s*/\s*(P\d+))?\b", re.I)


def validate_motion_attribution(text: str) -> None:
    """Require an explicit shot pair whenever the director cites the combined frame count."""
    for sentence in re.split(r"[.!?;\n]+", text):
        if not FRAME_CLAIM.search(sentence):
            continue
        shots = set()
        for scene, first, second in SHOT_ID.findall(sentence.upper()):
            shots.add(f"{scene}-{first}")
            if second:
                shots.add(f"{scene}-{second}")
        if shots != {TURN_SHOT, HOLD_SHOT}:
            raise ProviderError(f"The combined {MOTION_TOTAL}-frame evidence requires {TURN_SHOT} and {HOLD_SHOT}")


def validate_consolidation(data:dict,approved:bool) -> None:
    rows=data.get("findings",[])
    expected="needs_human_review" if approved else "blocked"
    if (not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict)
            or set(rows[0])!={"status","basis","next_steps"}
            or rows[0]["status"]!=expected
            or not isinstance(rows[0]["basis"],str) or not rows[0]["basis"].strip()
            or not isinstance(rows[0]["next_steps"],list) or not rows[0]["next_steps"]
            or any(not isinstance(x,str) or not x.strip() for x in rows[0]["next_steps"])):
        raise ProviderError("Supervisor consolidation contradicts independent QA")
    for text in (data.get("analysis", ""), rows[0]["basis"], *rows[0]["next_steps"]):
        validate_motion_attribution(text)


def step(store:Store,evidence:dict,*,root=ROOT,limits:dict):
    task=store.claim(mode="codex_proxy",ttl=3600)
    if task is None:
        return None
    try:
        if (task.get("scope")!=CONTRACT or task["owner"]!="01"
                or task["reviewer"]!="12" or task.get("limit_calls")!=N_CALLS
                or task.get("six_technical_snapshot_sha256")!=evidence["source_snapshot_sha256"]
                or task.get("evidence_digest")!=fingerprint(evidence["specialist_evidence"])):
            raise Conflict("Supervisor task changed sources or scope")
        source(root,MANIFEST.as_posix(),task["input_refs"][MANIFEST.as_posix()])
        for role in ("01","12"):
            if instructions(root,role)[1]!=task["instructions_shas"][role]:
                raise Conflict("Pinned supervisor instructions changed")
        if task["phase"]=="produce":
            assigned=model_step(store,task,root,"01",{
                "runtime_stage":"ep01_tool_supervisor_assignment",
                "specialist_evidence":list(evidence["specialist_evidence"].values()),
                "technical_source_sha256":evidence["source_snapshot_sha256"],
                "must_preserve":["no visual approval","no new images","no automatic rig",
                                 "no final MP4","no YouTube publishing"],
            },"codex_proxy",limits)
            validate_proposals(ensure_response(assigned,"01"),evidence)
            if (assigned["model"]!=task["model"]
                    or assigned.get("response_id") is None):
                raise ProviderError("Director Astra response identity missing")
            store.deliver(task["task_id"],task["attempt_id"],task["revision"],{
                "agent_id":"01","input_refs":task["input_refs"],
                "source_technical_snapshot":evidence["source_snapshot_sha256"],
                "source_evidence":evidence["specialist_evidence"],
                "assignment":assigned,
                "human_visual_approval":False,"youtube_publication":False,
                "production_ready":False,
            })
        else:
            previous=store.result(task["task_id"])
            if (previous["source_technical_snapshot"]!=evidence["source_snapshot_sha256"]
                    or previous["source_evidence"]!=evidence["specialist_evidence"]
                    or previous["assignment"]["response_sha256"]!=fingerprint(
                        previous["assignment"]["response"])):
                raise Conflict("Technical or assignment evidence changed before review")
            qa=model_step(store,task,root,"12",{
                "runtime_stage":"ep01_tool_supervisor_independent_qa",
                "specialist_evidence":list(evidence["specialist_evidence"].values()),
                "director_proposals":previous["assignment"]["response"]["findings"],
                "no_visual_frames_inspected":True,
            },"codex_proxy",limits)
            passed=validate_qa(ensure_response(qa,"12"),evidence)
            final=model_step(store,task,root,"01",{
                "runtime_stage":"ep01_tool_supervisor_consolidation",
                "qa_findings":qa["response"]["findings"],
                "combined_motion_evidence": {"total_frames": MOTION_TOTAL,
                                             "frames_by_shot": {TURN_SHOT: SOURCE_FRAME_COUNT, HOLD_SHOT: HOLD_FRAME_COUNT}},
                "safe_status":"needs_human_review" if passed else "blocked",
                "await_human_approval":True,
            },"codex_proxy",limits)
            validate_consolidation(ensure_response(final,"01"),passed)
            if qa["model"]!=task["model"] or final["model"]!=task["model"]:
                raise ProviderError("QA or final Astra response model changed")
            store.review(task["task_id"],task["attempt_id"],task["revision"],{
                "agent_id":"12","technical_passed":passed,
                "reviewed_result_sha256":task["result_sha256"],
                "human_visual_approval":False,"youtube_publication":False,
                "production_ready":False,"qa_response":qa,
                "coordinator":final,"scope":"astra_source_handoff_no_media",
            })
    except Conflict:
        raise
    except (ProviderError,BudgetBlocked,ValueError,KeyError,TypeError,OSError) as exc:
        store.fail(task["task_id"],task["attempt_id"],task["revision"],
                   type(exc).__name__,retry=False)
    return store.get(task["task_id"])


def run(store:Store,evidence:dict,*,root=ROOT)->dict:
    if (os.getenv("VF_EP01_SUPERVISOR_AUTHORIZATION")!="AUTHORIZE_THREE_ASTRA_HANDOFF_CALLS"
            or os.getenv("GITHUB_RUN_ATTEMPT","0")!="1"):
        raise ValueError("Three-call first-attempt authorization required")
    model=os.getenv("AI_MODEL","")
    limits={"usd":None,"tokens":100_000,"calls":N_CALLS}
    task_id=seed(store,evidence,root=root,model=model)
    store.recover()
    steps=[]
    for _ in range(2):
        updated=step(store,evidence,root=root,limits=limits)
        if updated is None:
            break
        steps.append({"phase":updated.get("phase"),"status":updated["status"]})
    data=report(store,root=root)
    data["astra_tool_supervision"]={
        "contract":CONTRACT,"task_id":task_id,"steps":steps,
        "technical_sources_verified":6,
        "technical_snapshot_sha256":evidence["source_snapshot_sha256"],
        "role_source_evidence_sha256":{
            r:row["evidence_sha256"] for r,row in evidence["specialist_evidence"].items()},
        "actual_calls":len(data["usage"]),"call_limit":N_CALLS,
        "conservative_token_limit":limits["tokens"],
        "billing_cap_verified":False,"billing_cap_usd":None,
        "image_generation_calls":0,"media_production_calls":0,
        "visual_approval":False,"rig_approval":False,
        "youtube_publications":0,
    }
    return data


def validate_real(data:dict,model:str)->str:
    info=data.get("astra_tool_supervision",{})
    tasks=data.get("tasks",[])
    cp=data.get("checkpoints",[])
    usage=data.get("usage",[])
    if (len(tasks)!=1 or len(cp)!=1 or len(usage)!=N_CALLS
            or [x.get("agent_id") for x in usage]!=EXPECTED
            or any(x.get("provider")!="codex_proxy" or x.get("model")!=model
                   or x.get("state")!="settled" or not x.get("response_id")
                   for x in usage)
            or tasks[0].get("status") not in ("completed","blocked")
            or cp[0].get("result_sha256")!=tasks[0].get("result_sha256")
            or cp[0].get("review",{}).get("agent_id")!="12"
            or cp[0].get("review",{}).get("human_visual_approval") is not False
            or cp[0].get("human_visual_approval") is not False
            or info.get("actual_calls")!=N_CALLS
            or info.get("technical_sources_verified")!=6
            or info.get("billing_cap_verified") is not False
            or data["safety"]["youtube_publications"]!=0):
        raise ValueError("Incomplete real Astra 01-12-01 supervisory checkpoint")
    expected_stages=["ep01_tool_supervisor_assignment",
                     "ep01_tool_supervisor_independent_qa",
                     "ep01_tool_supervisor_consolidation"]
    events=[e for e in data.get("events",[])
            if e.get("type")=="progress_update"
            and isinstance(e.get("content"),dict)
            and isinstance(e["content"].get("call_id"),str)]
    if len(events)!=N_CALLS or len({e["content"]["call_id"] for e in events})!=N_CALLS:
        raise ValueError("Three individual Astra response journals are required")
    for agent,stage,usage_row,event in zip(EXPECTED,expected_stages,usage,events):
        detail=event["content"]
        resp=detail.get("response")
        if (usage_row.get("call_id")!=detail.get("call_id")
                or usage_row.get("agent_id")!=agent
                or event.get("sender")!=agent
                or detail.get("runtime_stage")!=stage
                or detail.get("model")!=model
                or detail.get("validation_status")!="accepted"
                or not detail.get("response_id")
                or detail["response_id"]!=usage_row.get("response_id")
                or not isinstance(resp,dict)
                or set(resp)!={"agent_id","mode","analysis","findings","human_visual_approval"}
                or resp["agent_id"]!=agent or resp["mode"]!="codex_proxy"
                or resp["human_visual_approval"] is not False
                or fingerprint(resp)!=usage_row.get("report_sha256")
                or fingerprint(resp)!=detail.get("report_sha256")):
            raise ValueError("Reported supervisor response is not a real accepted model journal")
    hashes=info.get("role_source_evidence_sha256")
    if (not isinstance(hashes,dict) or set(hashes)!=set(RUN_SEQUENCE)
            or any(not isinstance(v,str) or len(v)!=64 for v in hashes.values())):
        raise ValueError("Six specialist technical reference hashes missing")
    evidence={"specialist_evidence":{
        role:{"evidence_sha256":digest} for role,digest in hashes.items()}}
    proposal=events[0]["content"]["response"]
    qa=events[1]["content"]["response"]
    director=events[2]["content"]["response"]
    validate_proposals(proposal,evidence)
    passed=validate_qa(qa,evidence)
    validate_consolidation(director,passed)
    if (cp[0]["review"]["qa_response"]["response"]!=qa
            or cp[0]["review"]["coordinator"]["response"]!=director):
        raise ValueError("Independent QA checkpoint differs from real model journals")
    if cp[0]["review"]["technical_passed"] is not passed:
        raise ValueError("QA decision has changed")
    expected="needs_human_review" if passed else "blocked"
    if tasks[0]["status"]!=("completed" if passed else "blocked"):
        raise ValueError("Astra technical handoff checkpoint disagrees with QA")
    return expected


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--github-state",action="store_true")
    parser.add_argument("--initialize-store",action="store_true")
    args=parser.parse_args()
    if args.initialize_store and not args.github_state:
        parser.error("initialize-store requires github-state")
    if os.getenv("GITHUB_RUN_ATTEMPT","0")!="1":
        parser.error("Paid rerun forbidden; previous call may have settled")
    tech=GitHubState(path=TECH_STATE).load()
    if tech is None:
        parser.error("Six previous technical specialist checkpoints missing")
    evidence=verified_technical_journal(tech)
    tmp=None
    if args.github_state:
        remote=GitHubState(path=STATE,initialize=args.initialize_store)
        snapshot=remote.load()
        tmp=tempfile.TemporaryDirectory(prefix="vf-astra-supervisor-")
        store=Store(Path(tmp.name)/"supervisor.sqlite")
        if snapshot is not None:
            store.import_snapshot(snapshot)
        store.persist_callback=remote.save
    else:
        store=Store(args.db)
    try:
        result=run(store,evidence)
        write_report(args.output,result)
        print(json.dumps({
            "real_model_calls":result["astra_tool_supervision"]["actual_calls"],
            "confirmed_technical_sources":6,
            "status":result["tasks"][0]["status"],
            "model":os.getenv("AI_MODEL"),
            "usd_billing_cap_verified":False,
        }))
        validate_real(result,os.getenv("AI_MODEL",""))
    finally:
        store.close()
        if tmp:
            tmp.cleanup()

if __name__=="__main__":
    main()
