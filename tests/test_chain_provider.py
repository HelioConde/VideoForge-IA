"""Manual authorization is scoped to one four-call textual audit."""
import os
import unittest
from unittest.mock import patch

from orchestrator.providers import GenerationRequest, ProviderBlockedError, make_chain_provider


class ChainProviderTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "VF_CHAIN_AUTHORIZATION": "AUTHORIZE_FOUR_ASTRA_CALLS",
            "AI_MODEL": "gpt-6-astra",
            "AI_ENABLED": "true",
            "PAID_CALLS_ENABLED": "true",
            "CODEX_PROXY_TEXT_AUTHORIZED": "true",
            "CODEX_PROXY_API_KEY": "fake-local-test",
        }

    def test_unknown_cost_retains_token_reservation(self):
        with patch.dict(os.environ, self.env, clear=True):
            provider = make_chain_provider()
            estimate = provider.estimate_cost(GenerationRequest("03", "rules", "context"))
        self.assertIsNone(estimate["upper_bound_usd"])
        self.assertGreater(estimate["input_tokens_upper_bound"], 0)

    def test_each_gate_is_required_and_workflow_replay_is_denied(self):
        for field in self.env:
            with self.subTest(field=field), patch.dict(os.environ, {**self.env, field: ""}, clear=True):
                with self.assertRaises(ProviderBlockedError):
                    make_chain_provider()
        with patch.dict(os.environ, {**self.env, "GITHUB_RUN_ATTEMPT": "2"}, clear=True):
            with self.assertRaises(ProviderBlockedError):
                make_chain_provider()
