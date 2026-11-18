"""Astra model priority is selected only by GET, before any inference."""
import json
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

from orchestrator.agent_ping import agent_01_ping
from orchestrator.proxy_preflight import PreflightError, probe
from orchestrator.providers import ProviderResponse


class FakeResponse:
    def __init__(self, payload):
        self.body = json.dumps(payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, size):
        return self.body


class ModelCatalog:
    def __init__(self, models):
        self.models = models
        self.requests = []
    def open(self, request, timeout):
        self.requests.append((request.get_method(), request.full_url))
        if request.full_url.endswith("/health"):
            return FakeResponse({"status": "ok", "accounts": 1})
        if request.full_url.endswith("/v1/models"):
            return FakeResponse({"data": [{"id": model} for model in self.models]})
        raise AssertionError("Unexpected endpoint")


class AstraModelSelectionTests(unittest.TestCase):
    def _get(self, listed):
        fake = ModelCatalog(listed)
        return probe("http://127.0.0.1:18080", "synthetic-unit-test-key-never-valid",
                     opener=fake, prefer_model="gpt-6.2-astra",
                     fallback_model="gpt-6-astra"), fake

    def test_preferred_astra_62_selected_if_both_present(self):
        selected, fake = self._get(["gpt-6-astra", "gpt-6.2-astra"])
        self.assertEqual(selected["selected_model"], "gpt-6.2-astra")
        self.assertEqual(selected["model_selection_reason"], "preferred_catalog_available")
        self.assertEqual([method for method, _ in fake.requests], ["GET", "GET"])
        self.assertEqual(selected["inference_requests"], 0)

    def test_fallback_to_astra_6_only_when_primary_absent(self):
        selected, fake = self._get(["gpt-6-astra", "gpt-image-2"])
        self.assertEqual(selected["selected_model"], "gpt-6-astra")
        self.assertEqual(selected["model_selection_reason"], "fallback_primary_absent_from_catalog")
        self.assertEqual([method for method, _ in fake.requests], ["GET", "GET"])
        self.assertFalse(selected["automatic_retry_after_unknown_inference_outcome"])

    def test_refuse_if_both_are_absent(self):
        fake = ModelCatalog(["gpt-image-2"])
        with self.assertRaises(PreflightError):
            probe("http://127.0.0.1:18080", "synthetic-unit-test-key-never-valid",
                  opener=fake, prefer_model="gpt-6.2-astra", fallback_model="gpt-6-astra")
        self.assertEqual([method for method, _ in fake.requests], ["GET", "GET"])

    def test_missing_fallback_and_conflicting_selection_block_before_network(self):
        fake = ModelCatalog(["gpt-6-astra"])
        for options in [
            {"prefer_model": "gpt-6.2-astra"},
            {"fallback_model": "gpt-6-astra"},
            {"require_model": "gpt-6-astra", "prefer_model": "gpt-6.2-astra",
             "fallback_model": "gpt-6-astra"},
        ]:
            with self.subTest(options=options), self.assertRaises(PreflightError):
                probe("http://127.0.0.1:18080", "synthetic-unit-test-key-never-valid",
                      opener=fake, **options)
        self.assertEqual(fake.requests, [])

    def test_ping_accepts_selected_astra_62_but_rejects_proxy_model_mismatch(self):
        provider = Mock(model="gpt-6.2-astra")
        provider.estimate_cost.return_value = {"upper_bound_usd": Decimal("0.005")}
        provider.generate_response.return_value = ProviderResponse(
            text=json.dumps({"agent_id": "01", "status": "received",
                             "message": "Recebido", "human_visual_approval": False}),
            provider="codex_proxy", model="gpt-6.2-astra",
            reported_model="gpt-6.2-astra", simulated=False, input_tokens=12,
            output_tokens=14)
        with patch("orchestrator.agent_ping.make_provider", return_value=provider):
            report = agent_01_ping(mode="codex_proxy", budget_usd="0.05")
        self.assertEqual(report["model"], "gpt-6.2-astra")
        self.assertTrue(report["llm_executed"])
        provider.generate_response.assert_called_once()
        provider.generate_response.return_value.reported_model = "gpt-6-astra"
        with patch("orchestrator.agent_ping.make_provider", return_value=provider):
            with self.assertRaisesRegex(ValueError, "not from the configured"):
                agent_01_ping(mode="codex_proxy", budget_usd="0.05")

    def test_workflow_defaults_to_auto_and_never_retries_a_post(self):
        flow = (Path(__file__).resolve().parents[1] /
                ".github/workflows/agent-proxy-runtime.yml").read_text()
        self.assertIn("default: 'auto'", flow)
        self.assertIn("--prefer-model gpt-6.2-astra --fallback-model gpt-6-astra", flow)
        self.assertIn("AI_MODEL='+model", flow)
        self.assertIn("PAID_CALLS_ENABLED: 'false'", flow)
        self.assertNotIn("curl -X POST", flow)


if __name__ == "__main__":
    unittest.main()
