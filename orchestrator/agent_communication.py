#!/usr/bin/env python3
"""Deterministic, zero-network agent message protocol demo. No LLM/proxy calls."""
import argparse
import hashlib
import json
from pathlib import Path

AGENTS = {"01": "diretor-geral", "03": "diretor-cenas", "12": "supervisor-qa"}
TASK = "DEMO-EP01-C07-C08-CONTINUITY"

def event(sender, recipient, kind, message, sequence):
    payload = {"task_id": TASK, "sequence": sequence, "from": sender,
               "to": recipient, "kind": kind, "message": message}
    payload["event_id"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()[:24]
    return payload

def simulate():
    events = [
        event("01", "03", "task_assigned", "Revisar o blocking C07/C08 V2 sem modificar assets.", 1),
        event("03", "12", "review_requested", "Checklist de continuidade preparado; solicitar QA independente. Nenhuma arte alterada.", 2),
        event("12", "01", "review_result", "Simulação de protocolo OK; revisão visual humana do EP01 continua pendente.", 3),
    ]
    assert all(x["from"] in AGENTS and x["to"] in AGENTS for x in events)
    assert len({x["event_id"] for x in events}) == len(events)
    assert [(x["from"], x["to"]) for x in events] == [("01", "03"), ("03", "12"), ("12", "01")]
    return {"schema_version": 1, "simulation": True, "no_ai_calls": True,
            "no_proxy_calls": True, "no_publication": True,
            "ep01_human_visual_approval": False, "task_id": TASK,
            "status": "protocol_test_passed", "events": events}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = simulate()
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")
    print(payload)

if __name__ == "__main__":
    main()
