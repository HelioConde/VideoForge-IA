"""Recover evidence of a blocked four-response Astra audit without inference.

This is a provenance checkpoint, NEVER a completed creative/technical approval.
The legacy fourth response was not journaled; hashes cannot reconstruct its text.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from .agent_bus import fingerprint
from .runtime_store import Store, Conflict, encode

STAGES = ("director_dispatch", "scene_continuity_analysis",
          "independent_qa_review", "director_consolidation")
AGENTS = ("01", "03", "12", "01")
MODEL = "gpt-6-astra"
STATE_PATH = "runtime/c07-c08-astra-v1.json"


def assess(store: Store, task_id: str) -> dict:
    """Validate all existing provenance; do not change state or invoke a provider."""
    task = store.get(task_id)
    if not (task.get("mode") == "codex_proxy"
            and task.get("operation") == "continuity_audit"
            and task.get("status") == "blocked"
            and task.get("phase") == "review"
            and task.get("blocked_reason") == "ProviderError"
            and task.get("owner") == "03" and task.get("reviewer") == "12"
            and task.get("human_visual_approval") is False
            and task.get("result_sha256")):
        raise ValueError("Only the pinned, blocked C07/C08 Astra review is reconcilable")
    store.result(task_id)  # Checks the existing producer result and hash.

    usage = [dict(x) for x in store.db.execute(
        """SELECT usage.* FROM usage JOIN attempts ON usage.attempt_id = attempts.id
           WHERE attempts.task_id = ? ORDER BY usage.rowid""", (task_id,))]
    if (len(usage) != 4 or len({u["call_id"] for u in usage}) != 4
            or any(u["agent_id"] != agent or u["model"] != MODEL
                   or u["provider"] != "codex_proxy"
                   or u["state"] != "settled" or u["actual_input"] is None
                   or u["actual_output"] is None
                   or not u["response_id"] or not u["report_sha256"]
                   for u, agent in zip(usage, AGENTS))):
        raise ValueError("Four distinct settled Astra responses are required")
    attempts = {x["id"]: dict(x) for x in store.db.execute(
        "SELECT * FROM attempts WHERE task_id=?", (task_id,))}
    if (len(attempts) != 2 or
            {a["phase"] for a in attempts.values()} != {"produce", "review"}
            or any(a["status"] not in {"delivered", "failed"} for a in attempts.values())):
        raise ValueError("Unexpected historical attempt status")

    progress = {}
    for row in store.db.execute("SELECT envelope FROM events ORDER BY seq"):
        evt = json.loads(row["envelope"])
        body = evt.get("content", {})
        if (evt.get("task_id") == task_id and evt.get("type") == "progress_update"
                and isinstance(body, dict) and body.get("call_id") in {u["call_id"] for u in usage}):
            if body["call_id"] in progress:
                raise ValueError("Duplicate journaled response")
            progress[body["call_id"]] = evt

    for index in range(3):
        u = usage[index]
        evt = progress.get(u["call_id"])
        if not evt:
            raise ValueError("Director, specialist, and QA accepted outputs must be journaled")
        body = evt["content"]
        response = body.get("response")
        if (evt.get("sender") != AGENTS[index]
                or body.get("agent_id") != AGENTS[index]
                or body.get("runtime_stage") != STAGES[index]
                or body.get("validation_status") == "rejected"
                or body.get("model") != MODEL
                or body.get("response_id") != u["response_id"]
                or not isinstance(response, dict)
                or response.get("agent_id") != AGENTS[index]
                or response.get("human_visual_approval") is not False
                or body.get("report_sha256") != u["report_sha256"]
                or fingerprint(response) != u["report_sha256"]):
            raise ValueError("Historical accepted output provenance is inconsistent")
    qa = progress[usage[2]["call_id"]]["content"]["response"]["findings"]
    from .runtime import CHAIN_FACETS
    if (not isinstance(qa, list) or len(qa) != len(CHAIN_FACETS)
            or {f.get("facet") for f in qa if isinstance(f, dict)} != set(CHAIN_FACETS)
            or any(not isinstance(f, dict) or
                   f.get("decision") not in {"supported", "correction_requested", "insufficient_evidence"}
                   for f in qa)):
        raise ValueError("Independent QA findings do not meet the documented shape")
    last = usage[3]
    final_evt = progress.get(last["call_id"])
    reason = "unavailable_in_legacy_journal"
    if final_evt:
        body = final_evt["content"]
        if (body.get("runtime_stage") != STAGES[3] or
                body.get("validation_status") != "rejected" or
                body.get("response_id") != last["response_id"] or
                not isinstance(body.get("response"), dict) or
                fingerprint(body["response"]) != last["report_sha256"]):
            raise ValueError("Final output has contradictory provenance")
        reason = body.get("validation_error") or "unclassified_validator_rejection"

    return {
        "task_id": task_id,
        "status": "blocked",
        "scope": "read_only_failed_chain_reconciliation",
        "reconciliation_status": "requires_manual_resolution",
        "blocked_reason": task["blocked_reason"],
        "result_sha256": task["result_sha256"],
        "input_refs": task["input_refs"],
        "provider": "codex_proxy",
        "model": MODEL,
        "calls": [
            {"agent_id": u["agent_id"], "response_id": u["response_id"],
             "call_id": u["call_id"], "response_sha256": u["report_sha256"],
             "input_tokens": u["actual_input"], "output_tokens": u["actual_output"],
             "validation_status": ("accepted" if i < 3 else "rejected_or_unavailable")}
            for i, u in enumerate(usage)
        ],
        "qa_supported_facets": sorted(f["facet"] for f in qa if f["decision"] == "supported"),
        "final_output_journaled": final_evt is not None,
        "final_validation_reason": reason,
        "final_director_decision_accepted": False,
        "llm_calls_replayed": 0,
        "additional_inference": 0,
        "technical_completion_approved": False,
        "human_visual_approval": False,
        "youtube_publication": False,
        "next_action": "Manual reconciliation of original response; do not replay inference.",
    }


def reconcile(store: Store, task_id: str, *, apply: bool = False) -> dict:
    checkpoint = assess(store, task_id)
    previous = store.db.execute("SELECT * FROM checkpoints WHERE task_id=?", (task_id,)).fetchone()
    if previous:
        content = json.loads(previous["content"])
        if (previous["sha256"] != fingerprint(content)
                or content.get("scope") != checkpoint["scope"]
                or content.get("status") != "blocked"):
            raise Conflict("An incompatible checkpoint already exists")
        return content
    if apply:
        with store.transaction():
            store.db.execute(
                "INSERT INTO checkpoints (task_id,content,sha256) VALUES (?,?,?)",
                (task_id, encode(checkpoint), fingerprint(checkpoint)))
    return checkpoint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--apply", action="store_true",
                        help="CAS-write only a blocked provenance checkpoint, never complete task")
    parser.add_argument("--confirm", default="", help="Must equal RECONCILE_WITHOUT_INFERENCE when applying")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.apply and args.confirm != "RECONCILE_WITHOUT_INFERENCE":
        parser.error("Explicit no-inference confirmation required")
    if args.apply and (os.getenv("AI_ENABLED", "false").lower() == "true"
                       or os.getenv("PAID_CALLS_ENABLED", "false").lower() == "true"):
        parser.error("Reconciliation may not run with real inference gates enabled")
    from .github_state import GitHubState
    remote = GitHubState(path=STATE_PATH, initialize=False)
    snapshot = remote.load()
    if snapshot is None:
        parser.error("Expected existing remote state; do not initialize a new one")
    with tempfile.TemporaryDirectory(prefix="vf-reconcile-") as temp:
        store = Store(Path(temp) / "state.sqlite")
        try:
            store.import_snapshot(snapshot)
            task_ids = [row["task_id"] for row in store.db.execute("SELECT task_id FROM tasks")]
            if len(task_ids) != 1 or (args.task_id and args.task_id != task_ids[0]):
                parser.error("Expected the single pinned continuity audit")
            if args.apply:
                store.persist_callback = remote.save
            checkpoint = reconcile(store, task_ids[0], apply=args.apply)
            output = {
                "mode": "no_inference_reconciliation",
                "applied": args.apply,
                "task_status": store.get(task_ids[0])["status"],
                "checkpoint_sha256": fingerprint(checkpoint),
                "checkpoint": checkpoint,
                "state_sha256": fingerprint(store.export_snapshot()),
            }
        finally:
            store.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in (
        "mode", "applied", "task_status", "checkpoint_sha256", "state_sha256")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
