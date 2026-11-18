import json
import os
from decimal import Decimal
from unittest.mock import Mock, patch
import unittest

from orchestrator.agent_ping import agent_01_ping
from orchestrator.providers import ProviderBlockedError, ProviderResponse


class Agent01PingTests(unittest.TestCase):
    def test_mock_ping_does_not_use_network_or_fake_real_ai(self):
        with patch.dict(os.environ, {"AI_ENABLED": "false", "PAID_CALLS_ENABLED": "false"}, clear=True):
            with patch("orchestrator.providers.urllib.request.build_opener") as network:
                result = agent_01_ping(mode="mock")
        self.assertTrue(result["simulated"])
        self.assertFalse(result["llm_executed"])
        self.assertEqual(result["agent_id"], "01")
        self.assertEqual(result["reply"]["status"], "received")
        network.assert_not_called()

    def test_live_ping_is_blocked_when_authorization_is_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderBlockedError):
                agent_01_ping(mode="codex_proxy", budget_usd="0.05")

    def test_live_contract_validates_reply_with_fake_provider_only(self):
        provider = Mock()
        provider.estimate_cost.return_value = {"upper_bound_usd": Decimal("0.005")}
        provider.generate_response.return_value = ProviderResponse(
            text=json.dumps({"agent_id": "01", "status": "received",
                             "message": "Teste recebido.", "human_visual_approval": False}),
            provider="codex_proxy", model="synthetic-model",
            input_tokens=10, output_tokens=11, simulated=False, cost_usd=Decimal("0.0001"))
        with patch("orchestrator.agent_ping.make_provider", return_value=provider):
            result = agent_01_ping(mode="codex_proxy", budget_usd="0.05")
        self.assertTrue(result["llm_executed"])
        self.assertEqual(result["reply"]["message"], "Teste recebido.")
        self.assertEqual(result["usage"]["input_tokens"], 10)
        provider.generate_response.assert_called_once()
        self.assertFalse(result["human_visual_approval"])
        self.assertEqual(result["production_actions"], 0)

    def test_budget_blocks_before_any_provider_request(self):
        provider = Mock()
        provider.estimate_cost.return_value = {"upper_bound_usd": Decimal("0.2")}
        with patch("orchestrator.agent_ping.make_provider", return_value=provider):
            with self.assertRaises(ValueError):
                agent_01_ping(mode="codex_proxy", budget_usd="0.05")
        provider.generate_response.assert_not_called()

    def test_malformed_response_is_not_success(self):
        provider = Mock()
        provider.estimate_cost.return_value = {"upper_bound_usd": Decimal("0.01")}
        provider.generate_response.return_value = ProviderResponse(
            text=json.dumps({"agent_id": "01", "status": "received",
                             "message": "ok", "human_visual_approval": True}),
            provider="codex_proxy", model="synthetic-model",
            input_tokens=None, output_tokens=None, simulated=False)
        with patch("orchestrator.agent_ping.make_provider", return_value=provider):
            with self.assertRaises(ValueError):
                agent_01_ping(mode="codex_proxy", budget_usd="0.05")

if __name__ == "__main__":
    unittest.main()
