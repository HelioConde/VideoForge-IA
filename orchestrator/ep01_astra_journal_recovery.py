"""Offline recovery of an ACTUAL three-call Astra journal, without replay.

The original supervisor task is blocked. Recover its six source-bound Agent 01
proposals and independent Agent 12 textual reviews, but NEVER promote an
invalid model consolidation to approval or a new technical checkpoint.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from .agent_bus import fingerprint
from .ep01_astra_supervisor import (
    STATE, TECH_STATE, RUN_SEQUENCE, validate_proposals, validate_qa,
    validate_consolidation, verified_technical_journal)
from .github_state import GitHubState
from .providers import ProviderError
from .runtime import write_report

EXPECTED_ROLES=("01","12","01")
STAGES=("ep01_tool_supervisor_assignment",
        "ep01_tool_supervisor_independent_qa",
        "ep01_tool_supervisor_consolidation")
ISSUE=95
RUN_ID=44454660648
MODEL="gpt-6.2-astra"


def reconcile(supervisor_snapshot:dict, technical_proof:dict)->dict:
    tables=supervisor_snapshot.get("tables",{})
    tasks=tables.get("tasks",[])
    usage=tables.get("usage",[])
    checkpoints=tables.get("checkpoints",[])
    rows=tables.get("events",[])
    if (len(tasks)!=1 or len(usage)!=3 or checkpoints
            or not isinstance(rows,list)
            or not isinstance(technical_proof,dict)
            or technical_proof.get("verified_role_count")!=6
            or set(technical_proof.get("specialist_evidence",{}))!=set(RUN_SEQUENCE)):
        raise ValueError("Incomplete or unexpected blocked supervisor snapshot")
    task=json.loads(tasks[0]["payload"])
    if (task.get("status")!="blocked" or task.get("blocked_reason")!="ProviderError"
            or task.get("phase")!="review"
            or task.get("scope")!="ep01-six-tool-astra-supervision-v1"
            or task.get("six_technical_snapshot_sha256")!=technical_proof["source_snapshot_sha256"]
            or task.get("evidence_digest")!=fingerprint(technical_proof["specialist_evidence"])):
        raise ValueError("Original paid task is not the expected blocked handoff")
    events=[]
    for r in rows:
        event=json.loads(r["envelope"])
        if (event.get("type")=="progress_update"
                and isinstance(event.get("content"),dict)
                and isinstance(event["content"].get("call_id"),str)):
            events.append(event)
    if len(events)!=3 or len({e["content"]["call_id"] for e in events})!=3:
        raise ValueError("Exactly three accepted source-bound Astra responses required")
    for agent,stage,paid,ev in zip(EXPECTED_ROLES,STAGES,usage,events):
        detail=ev["content"]
        raw=detail.get("response")
        if (paid.get("agent_id")!=agent
                or paid.get("state")!="settled"
                or paid.get("model")!=MODEL
                or paid.get("provider")!="codex_proxy"
                or not paid.get("response_id")
                or ev.get("sender")!=agent
                or ev.get("recipient")!=("12" if agent=="01" and stage==STAGES[0] else "01")
                or paid.get("call_id")!=detail.get("call_id")
                or detail.get("validation_status")!="accepted"
                or paid["response_id"]!=detail.get("response_id")
                or detail.get("runtime_stage")!=stage
                or not isinstance(raw,dict)
                or set(raw)!={"agent_id","mode","analysis","findings","human_visual_approval"}
                or raw.get("agent_id")!=agent
                or raw.get("mode")!="codex_proxy"
                or raw.get("human_visual_approval") is not False
                or paid.get("report_sha256")!=fingerprint(raw)
                or detail.get("report_sha256")!=fingerprint(raw)):
            raise ValueError("Model receipt or durable response body does not match source")
    original_01=events[0]["content"]["response"]
    independent_12=events[1]["content"]["response"]
    consolidation=events[2]["content"]["response"]
    validate_proposals(original_01,technical_proof)
    reviewer_supported=validate_qa(independent_12,technical_proof)
    if not reviewer_supported:
        raise ValueError("This reconciliation is scoped to six supported advisory proposals")
    try:
        validate_consolidation(consolidation,reviewer_supported)
    except ProviderError:
        invalid_consolidation=True
    else:
        raise ValueError("Original model conclusion unexpectedly passed; do not misclassify it")
    findings=consolidation.get("findings",[])
    if (len(findings)!=1 or not isinstance(findings[0],dict)
            or findings[0].get("status")!="needs_human_review"
            or not isinstance(findings[0].get("next_steps"),str)
            or not findings[0]["next_steps"].strip()):
        raise ValueError("Observed final consolidation error changed")
    incorrect_shot_reference=(
        "C01-P04" in findings[0].get("basis","")
        and "240 quadros" in findings[0].get("basis",""))
    if not incorrect_shot_reference:
        raise ValueError("The actual cross-shot attribution issue is missing")
    pending=[]
    for recommendation,review in zip(original_01["findings"],
                                     independent_12["findings"]):
        role=recommendation["role_id"]
        pending.append({
            "agent_id":role,"assigned_by":"01","independent_text_qa_by":"12",
            "technical_source_evidence_sha256":recommendation["evidence_sha256"],
            "source_technical_checkpoint_sha256":
                technical_proof["specialist_evidence"][role]["checkpoint_sha256"],
            "next_action":recommendation["next_action"],
            "blockers":recommendation["blockers"],
            "qa_text_decision":review["decision"],
            "qa_text_reason":review["reason"],
            "status":"proposed_waiting_for_actual_execution_and_visual_gates",
            "executed_after_astra_call":False,"human_visual_approval":False,
            "rig_ready":False,"youtube_publication":False,
        })
    return {
        "schema":"videoforge/ep01-astra-supervisor-blocked-response-recovery/v1",
        "original_run_id":RUN_ID,
        "original_run_url":f"https://github.com/HelioConde/VideoForge-IA/actions/runs/{RUN_ID}",
        "original_state_path":STATE,
        "source_technical_state_path":TECH_STATE,
        "original_state_sha256":fingerprint(supervisor_snapshot),
        "source_technical_snapshot_sha256":technical_proof["source_snapshot_sha256"],
        "original_task_id":task["task_id"],
        "original_task_status":"blocked",
        "original_task_blocked_reason":"ProviderError",
        "original_checkpoints":0,
        "accepted_real_astra_model":MODEL,
        "model_call_order":list(EXPECTED_ROLES),
        "real_model_calls_observed":3,
        "additional_model_calls":0,
        "actual_tokens_reported_input":sum(u.get("actual_input",0) or 0 for u in usage),
        "actual_tokens_reported_output":sum(u.get("actual_output",0) or 0 for u in usage),
        "financial_usd_cap_verified":False,
        "verified_previous_specialist_outputs":6,
        "proposals_accepted_by_text_qa":6,
        "original_last_model_response_sha256":fingerprint(consolidation),
        "original_final_schema_valid":False if invalid_consolidation else True,
        "original_final_next_steps_type":"string",
        "original_final_misattributes_240_frames_to_c01p04":incorrect_shot_reference,
        "actual_240_frame_motion_shots":["C08-P02","C08-P03"],
        "c01p04_rule":"do_not_separate_hands",
        "advisory_work_orders":pending,
        "global_status":"BLOCKED_REVIEW_REQUIRED_NO_AUTO_EXECUTION",
        "human_visual_approval":False,
        "real_rig_ready":False,
        "final_mp4_approved":False,
        "youtube_publication":False,
        "notes":"Preserves all original model bytes and attribution. This is a read-only "
                "triage of six valid proposals, not acceptance of the invalid final "
                "response. No Astra replays, no image/video tools and no paid calls.",
    }


def markdown(data:dict)->str:
    rows=[
        "# EP01 — recuperação segura das 3 respostas reais do Astra",
        "",
        f"Fonte: [Action #{data['original_run_id']}]({data['original_run_url']}) "
        "e branch `state/multi-agent-runtime`.",
        "",
        "**Resultado original:** bloqueado; **3/3 chamadas Astra genuínas** "
        "arquivadas. O Agente 12 avaliou as seis propostas textuais como "
        "fundamentadas, mas a resposta de consolidação não passou no contrato.",
        "",
        "**Falhas do fechamento:** `next_steps` veio como string, não array; "
        "há mistura de C01-P04 com as poses de 240 quadros do carrinho C08-P02/P03. "
        "Nenhum checkpoint final de aprovação foi criado.",
        "",
        "## Encaminhamentos existentes (ainda não executados)",
        "",
        "| Agente | Ação proposta | Bloqueio |",
        "|---|---|---|",
    ]
    for row in data["advisory_work_orders"]:
        rows.append(f"| **{row['agent_id']}** | {row['next_action']} | "
                    f"{'; '.join(row['blockers'])} |")
    rows.extend([
        "",
        "**Integridade:** SHA do snapshot original: "
        f"`{data['original_state_sha256']}`.",
        "",
        "**Contadores:** 6 propostas textuais respaldadas, zero ferramentas de produção "
        "invocadas nesta recuperação, zero novas chamadas Astra e nenhuma "
        "aprovação de imagem, rig, MP4 final ou YouTube.",
        "",
        f"Fila de revisão: [issue #{ISSUE}]"
        f"(https://github.com/HelioConde/VideoForge-IA/issues/{ISSUE}).",
        "",
    ])
    return "\n".join(rows)


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    tech=GitHubState(path=TECH_STATE).load()
    paid=GitHubState(path=STATE).load()
    if paid is None or tech is None:
        raise SystemExit("Missing original state — no inference or recreation attempted")
    evidence=verified_technical_journal(tech)
    report=reconcile(paid,evidence)
    path=args.output_dir.resolve()
    path.mkdir(parents=True,exist_ok=True)
    write_report(path/"recovered-six-agent-work-orders.json",report)
    (path/"recovery-qa.md").write_text(markdown(report),encoding="utf-8")
    print(json.dumps({
        "validated_real_call_receipts":3,
        "verified_text_qa_proposals":6,
        "original_task_blocked":True,
        "final_consolidation_valid":False,
        "new_paid_calls":0,
        "publication_or_visual_approval":False,
    }))

if __name__=="__main__":
    main()
