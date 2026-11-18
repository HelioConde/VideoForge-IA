"""Single-response Agent 01 ping over the existing text provider.

The CLI never enables inference gates. A caller must separately authorize
AI_ENABLED, PAID_CALLS_ENABLED and CODEX_PROXY_TEXT_AUTHORIZED. No retries,
no shell tools, no image calls, no YouTube and no EP01 writes.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

from .providers import GenerationRequest, make_provider
from .runtime import ROOT, instructions, write_report

PING = ("Teste de comunicação VideoForge-IA. Você é o Agente 01, Diretor Geral. "
        "Não execute tarefas, não faça alterações. Confirme apenas que recebeu "
        "uma mensagem de teste da coordenação. Responda exclusivamente em JSON.")


def agent_01_ping(*, mode: str, budget_usd: str = "0", root=ROOT) -> dict:
    if mode not in {"mock", "codex_proxy"}:
        raise ValueError("Only mock or explicitly authorized Codex text is accepted")
    agent_text, sha = instructions(root, "01")
    contract = ('\nIMPORTANT: Read-only connection test. Never claim to call another agent. '
                'No tools and no media. Reply strictly as one JSON object with exactly '
                'agent_id="01", status="received", message (short string), '
                'human_visual_approval=false. Do not use Markdown.')
    request = GenerationRequest(agent_id="01", instructions=agent_text + contract,
                                input=PING, max_output_tokens=500,
                                input_token_limit=25000, timeout_seconds=60)
    provider = make_provider(mode)
    if mode == "mock":
        simulated = provider.generate_response(request)
        reply = {"agent_id": "01", "status": "received",
                 "message": "Synthetic ping; no model invoked.",
                 "human_visual_approval": False}
        return {"schema_version": 1, "mode": "mock", "agent_id": "01",
                "model": simulated.model, "simulated": True, "llm_executed": False,
                "instructions_sha256": sha, "reply": reply,
                "usage": simulated.usage, "estimated_cost_usd": "0",
                "human_visual_approval": False, "youtube_publication": False,
                "production_actions": 0}
    try:
        budget = Decimal(budget_usd)
    except (InvalidOperation, TypeError):
        raise ValueError("Explicit positive finite budget is required") from None
    if not budget.is_finite() or not Decimal("0.01") <= budget <= Decimal("0.25"):
        raise ValueError("Pilot budget must be between 0.01 and 0.25 USD")
    estimate = provider.estimate_cost(request)
    expected = Decimal(str(estimate["upper_bound_usd"]))
    if expected <= 0 or expected > budget:
        raise ValueError("Estimated model cost exceeds the explicit budget")
    response = provider.generate_response(request)
    if response.simulated or response.provider != "codex_proxy":
        raise ValueError("Live response was not from the configured Codex provider")
    try:
        reply = json.loads(response.text)
    except (ValueError, TypeError):
        raise ValueError("Agent 01 did not return valid JSON") from None
    if (not isinstance(reply, dict)
            or set(reply) != {"agent_id", "status", "message", "human_visual_approval"}
            or reply["agent_id"] != "01" or reply["status"] != "received"
            or reply["human_visual_approval"] is not False
            or not isinstance(reply["message"], str)
            or not 1 <= len(reply["message"]) <= 300):
        raise ValueError("Agent 01 returned an invalid message contract")
    return {"schema_version": 1, "mode": "codex_proxy_text_one_call",
            "agent_id": "01", "model": response.model, "simulated": False,
            "llm_executed": True, "instructions_sha256": sha, "reply": reply,
            "usage": response.usage,
            "estimated_cost_usd": str(expected),
            "observed_cost_configured_price_usd": str(response.cost_usd) if response.cost_usd is not None else None,
            "human_visual_approval": False, "youtube_publication": False,
            "production_actions": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["mock", "codex_proxy"], default="mock")
    parser.add_argument("--budget-usd", default="0")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = agent_01_ping(mode=args.mode, budget_usd=args.budget_usd)
    write_report(args.output, result)
    print(json.dumps({"agent_id": "01", "mode": result["mode"],
                      "llm_executed": result["llm_executed"],
                      "production_actions": 0, "youtube_publications": 0}))


if __name__ == "__main__":
    main()
