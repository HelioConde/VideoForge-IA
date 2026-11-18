"""Optional, explicitly authorized text-only Astra roundtrip for all 12 agents.

Agent 01 dispatches ten independent source-bound specialist briefs; Agent 12
reviews them against a second source read; Agent 01 consolidates. Thirteen model
calls in total. Persistent GitHub CAS journaling prevents silent duplicate calls.
No tools for image generation, shell, rig, audio, rendering or publication.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from .agent_bus import ROLES, fingerprint
from .all_roles_diagnostic import CONTRACT as DIAGNOSTIC_CONTRACT, FOCUS, SPECIALISTS, diagnostic
from .providers import ProviderError
from .runtime import MANIFEST, ROOT, instructions, model_step, report, source, write_report
from .runtime_store import BudgetBlocked, Conflict, Store

CONTRACT = "all-12-text-roundtrip-v1"
STATE_PATH = "runtime/agent-12-text-roundtrip-v1.json"
NUMBER_OF_CALLS = 13


def seed(store: Store, *, root=ROOT, mode="codex_proxy", model="") -> str:
    if mode != "codex_proxy" or model not in {"gpt-6.2-astra", "gpt-6-astra"}:
        raise ValueError("Only a manually approved Astra text pilot is supported")
    _, manifest_sha = source(root, MANIFEST.as_posix())
    role_shas = {role: instructions(root, role)[1] for role in ROLES}
    version = fingerprint({"model": model, "source": manifest_sha,
                           "instructions": role_shas, "contract": CONTRACT})[:16]
    task_id = "EP01-ALL-ROLES-TEXT-" + version
    store.enqueue({
        "task_id": task_id, "owner": "01", "reviewer": "12",
        "mode": mode, "operation": "read_only_analysis",
        "input_refs": {MANIFEST.as_posix(): manifest_sha},
        "instructions_shas": role_shas,
        "priority": 0, "max_attempts": 1, "stop_on_review_rejection": True,
        "human_visual_approval": False, "scope": CONTRACT,
        "model": model, "limit_calls": NUMBER_OF_CALLS,
    })
    return task_id


def ensure_response(result: dict, role: str, *, real=True) -> dict:
    if (not isinstance(result, dict) or result.get("agent_id") != role
            or not isinstance(result.get("response"), dict)
            or result["response"].get("agent_id") != role
            or result["response"].get("human_visual_approval") is not False
            or not isinstance(result["response"].get("findings"), list)):
        raise ProviderError("Agent response missing structured role provenance")
    if real and (result.get("llm_executed") is not True
                 or result.get("simulated") is not False
                 or result.get("provider") != "codex_proxy"
                 or not result.get("response_id")
                 or not result.get("response_sha256")):
        raise ProviderError("A real, journaled Astra response is required")
    return result["response"]


def _validate_specialist(response: dict, role: str, evidence_sha: str) -> None:
    findings = response["findings"]
    if len(findings) != 1 or not isinstance(findings[0], dict):
        raise ProviderError("Specialist must return one source-bound diagnostic")
    finding = findings[0]
    if (set(finding) != {"role_id", "focus", "evidence_sha256", "production_ready",
                        "blockers", "recommendation"}
            or finding["role_id"] != role or finding["focus"] != FOCUS[role]
            or finding["evidence_sha256"] != evidence_sha
            or finding["production_ready"] is not False
            or not isinstance(finding["blockers"], list)
            or not finding["blockers"]
            or any(not isinstance(s, str) or not s for s in finding["blockers"])
            or not isinstance(finding["recommendation"], str)
            or not finding["recommendation"].strip()):
        raise ProviderError("Specialist source/production safety contract rejected")


def _validate_qa(response: dict, specialist_reports: dict) -> bool:
    findings = response["findings"]
    if len(findings) != len(SPECIALISTS):
        raise ProviderError("Independent QA must review all specialists")
    seen = set()
    for item in findings:
        if (not isinstance(item, dict)
                or set(item) != {"role_id", "decision", "evidence_sha256", "reason"}
                or item.get("role_id") not in SPECIALISTS
                or item["role_id"] in seen
                or item["decision"] not in {"supported", "correction_requested", "insufficient_evidence"}
                or item.get("evidence_sha256") != specialist_reports[item["role_id"]]["evidence_sha256"]
                or not isinstance(item.get("reason"), str) or not item["reason"].strip()):
            raise ProviderError("Independent QA decision provenance rejected")
        seen.add(item["role_id"])
    if seen != set(SPECIALISTS):
        raise ProviderError("Independent QA did not cover every specialist")
    return all(row["decision"] == "supported" for row in findings)


def _validate_director(response: dict, qa_passed: bool) -> None:
    findings = response["findings"]
    expected_status = "needs_human_review" if qa_passed else "blocked"
    if (len(findings) != 1 or not isinstance(findings[0], dict)
            or set(findings[0]) != {"status", "basis", "next_steps"}
            or findings[0]["status"] != expected_status
            or not isinstance(findings[0]["basis"], str) or not findings[0]["basis"].strip()
            or not isinstance(findings[0]["next_steps"], list)
            or not findings[0]["next_steps"]
            or any(not isinstance(s, str) or not s for s in findings[0]["next_steps"])):
        raise ProviderError("Director consolidation must match independent QA")


def step(store: Store, *, root=ROOT, limits=None) -> dict | None:
    if limits is None:
        raise ValueError("Explicit priced call/token budgets required")
    task = store.claim(mode="codex_proxy", ttl=3600)
    if task is None:
        return None
    try:
        if (task.get("scope") != CONTRACT or task["owner"] != "01"
                or task["reviewer"] != "12" or task["limit_calls"] != NUMBER_OF_CALLS):
            raise ValueError("Unrecognized roundtrip task")
        _, source_hash = source(root, MANIFEST.as_posix(), task["input_refs"][MANIFEST.as_posix()])
        for role in ROLES:
            if instructions(root, role)[1] != task["instructions_shas"][role]:
                raise Conflict("Pinned agent instructions changed")
        role_evidence = {}
        for role in SPECIALISTS:
            evidence = diagnostic({"owner": role, "operation": "read_only_analysis",
                                   "input_refs": task["input_refs"]}, root)
            role_evidence[role] = {"focus": FOCUS[role],
                                   "evidence": evidence,
                                   "evidence_sha256": fingerprint(evidence)}
        if task["phase"] == "produce":
            coordinator = model_step(store, task, root, "01", {
                "runtime_stage": "roundtrip_assignment", "source_sha256": source_hash,
                "specialists": {r: item["focus"] for r, item in role_evidence.items()},
                "instructions": "Delegate read-only textual analysis only; no production tools.",
            }, "codex_proxy", limits)
            ensure_response(coordinator, "01")
            results = {}
            for role in SPECIALISTS:
                evidence = role_evidence[role]
                result = model_step(store, task, root, role, {
                    "runtime_stage": "roundtrip_specialist",
                    "task_id": task["task_id"], "role_id": role, "focus": evidence["focus"],
                    "source_evidence": evidence["evidence"],
                    "evidence_sha256": evidence["evidence_sha256"],
                    "restriction": "Only text and metadata; no visual inspection claims or media operations.",
                }, "codex_proxy", limits)
                _validate_specialist(ensure_response(result, role), role, evidence["evidence_sha256"])
                results[role] = {
                    "response": result["response"],
                    "response_sha256": result["response_sha256"],
                    "evidence_sha256": evidence["evidence_sha256"],
                    "model": result["model"], "response_id": result["response_id"],
                }
            store.deliver(task["task_id"], task["attempt_id"], task["revision"], {
                "agent_id": "01", "input_refs": task["input_refs"],
                "task_id": task["task_id"], "model": task["model"],
                "director_assignment": coordinator,
                "specialists": results,
                "human_visual_approval": False, "youtube_publication": False,
                "production_ready": False,
            })
        else:
            prior = store.result(task["task_id"])
            results = prior["specialists"]
            if set(results) != set(SPECIALISTS):
                raise ProviderError("Not all ten specialist outputs were journaled")
            # Reopen and recalculate independently before Agent 12 sees any result.
            for role in SPECIALISTS:
                if (results[role]["evidence_sha256"] != role_evidence[role]["evidence_sha256"]
                        or results[role]["response_sha256"] != fingerprint(results[role]["response"])):
                    raise ProviderError("Tampered specialist output or stale source")
            qa = model_step(store, task, root, "12", {
                "runtime_stage": "roundtrip_independent_qa",
                "source_hash": source_hash,
                "submitted_reports": {r: v["response"]["findings"] for r, v in results.items()},
                "expected_source_evidence": {r: v["evidence_sha256"] for r, v in role_evidence.items()},
                "restriction": "Review metadata only; do not grant visual/art/production approval.",
            }, "codex_proxy", limits)
            qa_passed = _validate_qa(ensure_response(qa, "12"), results)
            director = model_step(store, task, root, "01", {
                "runtime_stage": "roundtrip_consolidation",
                "qa_passed": qa_passed, "qa_findings": qa["response"]["findings"],
                "safe_status": "needs_human_review" if qa_passed else "blocked",
                "restriction": "Never mark all agents production-ready or authorize YouTube.",
            }, "codex_proxy", limits)
            _validate_director(ensure_response(director, "01"), qa_passed)
            store.review(task["task_id"], task["attempt_id"], task["revision"], {
                "agent_id": "12", "technical_passed": qa_passed,
                "reviewed_result_sha256": task["result_sha256"],
                "human_visual_approval": False, "youtube_publication": False,
                "production_ready": False, "qa_response": qa,
                "coordinator": director, "scope": "real_astra_text_only_no_media",
            })
    except Conflict:
        raise
    except (ValueError, ProviderError, BudgetBlocked, KeyError, TypeError, OSError) as exc:
        store.fail(task["task_id"], task["attempt_id"], task["revision"],
                   type(exc).__name__, retry=False)
    return store.get(task["task_id"])


def run(store: Store, *, root=ROOT, budget_usd: float) -> dict:
    if type(budget_usd) not in (float, int) or not 0 < budget_usd <= 0.25:
        raise ValueError("Explicit finite budget required (USD 0.01-0.25)")
    model = os.getenv("AI_MODEL", "")
    task_id = seed(store, root=root, model=model)
    store.recover()
    limits = {"usd": budget_usd, "tokens": 1_000_000, "calls": NUMBER_OF_CALLS}
    steps = []
    for _ in range(2):
        result = step(store, root=root, limits=limits)
        if result is None:
            break
        steps.append({"task_id": result["task_id"], "status": result["status"],
                      "phase": result["phase"]})
    data = report(store, root=root)
    data["live_roundtrip"] = {
        "task_id": task_id, "model": model,
        "steps": steps, "required_real_calls": NUMBER_OF_CALLS,
        "actual_calls": len(data["usage"]),
        "all_roles": list(ROLES), "specialists": list(SPECIALISTS),
        "production_ready": False, "visual_quality_approved": False,
        "media_created": 0, "youtube_publications": 0,
    }
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget-usd", type=float, required=True)
    parser.add_argument("--github-state", action="store_true")
    parser.add_argument("--initialize-store", action="store_true")
    args = parser.parse_args()
    if os.getenv("VF_ALL_ROLES_AUTHORIZATION") != "AUTHORIZE_THIRTEEN_ASTRA_CALLS":
        parser.error("Fresh explicit authorization required for thirteen real model calls")
    if os.getenv("GITHUB_RUN_ATTEMPT", "1") != "1":
        parser.error("Re-running the live workflow is prohibited")
    if args.initialize_store and not args.github_state:
        parser.error("initialize-store requires --github-state")
    temporary = None
    if args.github_state:
        from .github_state import GitHubState
        remote = GitHubState(path=STATE_PATH, initialize=args.initialize_store)
        snapshot = remote.load()
        temporary = tempfile.TemporaryDirectory(prefix="vf-roundtrip-")
        store = Store(Path(temporary.name) / "state.sqlite")
        if snapshot is not None:
            store.import_snapshot(snapshot)
        store.persist_callback = remote.save
    else:
        db = args.db.resolve()
        if db.is_relative_to((ROOT / "canal").resolve()) or db.is_relative_to((ROOT / "agents").resolve()):
            parser.error("Database may not be within production sources")
        store = Store(db)
    try:
        result = run(store, budget_usd=args.budget_usd)
        write_report(args.output, result)
        records = result["live_roundtrip"]
        print(json.dumps({"actual_calls": records["actual_calls"],
                          "task_status": result["tasks"][0]["status"],
                          "production_ready": False}))
        if (records["actual_calls"] != NUMBER_OF_CALLS
                or len(result["checkpoints"]) != 1
                or result["tasks"][0]["status"] not in ("completed", "blocked")
                or result["tasks"][0].get("blocked_reason") in ("ProviderError", "BudgetBlocked")):
            raise SystemExit("Incomplete text-only agent roundtrip; inspect journal without replay")
    finally:
        store.close()
        if temporary:
            temporary.cleanup()


if __name__ == "__main__":
    main()
