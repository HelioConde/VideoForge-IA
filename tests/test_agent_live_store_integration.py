"""Exercise 13 real runtime journals and budget reservations with a fake provider.

Unlike model_step stubs this test uses the actual Store, model_step, ledger,
event envelope, technical checkpoint and final provenance validator.
The fake provider is local: zero network, zero paid inference.
"""
import json
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from orchestrator.agent_live_roundtrip import (
    FOCUS, SPECIALISTS, run, validate_live_roundtrip_result,
)
from orchestrator.providers import ProviderResponse
from orchestrator.runtime_store import Store


class TextOnlyFakeAstra:
    name = "codex_proxy"
    model = "gpt-6.2-astra"

    def __init__(self, reject_qa=False):
        self.reject_qa = reject_qa
        self.calls = []

    def estimate_cost(self, request):
        return {"upper_bound_usd": Decimal("0.001"),
                "input_tokens_upper_bound": 1200,
                "output_tokens_upper_bound": request.max_output_tokens}

    def generate_response(self, request):
        payload = json.loads(request.input)
        stage = payload["runtime_stage"]
        role = request.agent_id
        self.calls.append((role, stage))
        if stage == "roundtrip_assignment":
            findings = [
                {"recipient": specialist, "focus": FOCUS[specialist],
                 "source_sha256": payload["source_sha256"],
                 "tools": ["read_only_text_analysis"]}
                for specialist in SPECIALISTS
            ]
        elif stage == "roundtrip_specialist":
            findings = [{
                "role_id": role, "focus": payload["focus"],
                "evidence_sha256": payload["evidence_sha256"],
                "production_ready": False,
                "blockers": ["Aprovacao criativa e QA de midia pendentes"],
                "recommendation": "Analisar fontes aprovadas antes da producao",
            }]
        elif stage == "roundtrip_independent_qa":
            findings = [
                {"role_id": specialist,
                 "decision": ("correction_requested"
                              if self.reject_qa and specialist == "07"
                              else "supported"),
                 "evidence_sha256": digest,
                 "reason": "Comparado com hashes de metadados independentes"}
                for specialist, digest in payload["expected_source_evidence"].items()
            ]
        elif stage == "roundtrip_consolidation":
            findings = [{
                "status": payload["safe_status"],
                "basis": "Auditoria textual sem aprovar midia",
                "next_steps": ["Concluir QA de arte e animacao"],
            }]
        else:
            raise AssertionError("Unexpected provider stage: " + stage)
        envelope = {"agent_id": role, "mode": "codex_proxy",
                    "analysis": "Resposta sintetica sem acesso a IA real",
                    "findings": findings, "human_visual_approval": False}
        return ProviderResponse(
            text=json.dumps(envelope, ensure_ascii=False),
            provider=self.name, model=self.model, reported_model=self.model,
            input_tokens=80, output_tokens=100, simulated=False,
            response_id=f"fake-resp-{len(self.calls):02}",
            cost_usd=Decimal("0.0002"),
        )


class DurableIntegrationTests(unittest.TestCase):
    def exercise(self, rejected):
        provider = TextOnlyFakeAstra(reject_qa=rejected)
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "audit.sqlite")
            try:
                with patch.dict(os.environ, {"AI_MODEL": provider.model}), patch(
                    "orchestrator.runtime.make_provider", return_value=provider
                ), patch("orchestrator.providers.urllib.request.build_opener") as network:
                    data = run(store, budget_usd=0.25)
                network.assert_not_called()
                expected_status = "blocked" if rejected else "completed"
                self.assertEqual(data["tasks"][0]["status"], expected_status)
                self.assertEqual(len(provider.calls), 13)
                self.assertEqual(data["live_roundtrip"]["actual_calls"], 13)
                self.assertEqual([u["agent_id"] for u in data["usage"]],
                                 ["01", *SPECIALISTS, "12", "01"])
                self.assertTrue(all(u["state"] == "settled" for u in data["usage"]))
                self.assertEqual(len(data["checkpoints"]), 1)
                expected = "blocked" if rejected else "needs_human_review"
                self.assertEqual(validate_live_roundtrip_result(data, provider.model),
                                 expected)
                self.assertEqual(sum(t["status"] == "completed" for t in data["tasks"]),
                                 0 if rejected else 1)
                self.assertFalse(data["live_roundtrip"]["production_ready"])
                self.assertFalse(data["safety"]["production_tools_enabled"])
                reopened = store.export_snapshot()
                store.close()
                fresh = Store(Path(tmp) / "reopened.sqlite")
                try:
                    fresh.import_snapshot(reopened)
                    self.assertEqual(fresh.export_snapshot(), reopened)
                    self.assertEqual(len(fresh.export_snapshot()["tables"]["usage"]), 13)
                finally:
                    fresh.close()
            finally:
                store.close()

    def test_full_thirteen_stage_journal_with_independent_qa(self):
        self.exercise(rejected=False)

    def test_independent_rejection_is_blocked_with_all_calls_settled(self):
        self.exercise(rejected=True)


if __name__ == "__main__":
    unittest.main()
