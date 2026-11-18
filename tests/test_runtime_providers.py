import json
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from providers import (  # noqa: E402
    CodexProxyResponsesProvider,
    GenerationRequest,
    MockProvider,
    OpenAIResponsesProvider,
    ProviderBlockedError,
    ProviderError,
    from_environment,
)


class RuntimeProviderTests(unittest.TestCase):
    def setUp(self):
        self.request = GenerationRequest(
            agent_id="diretor-cenas", instructions="Audit manifest structure.",
            input='{"task_id":"T-1","shots":[]}', max_output_tokens=100,
            input_token_limit=1000, timeout_seconds=3,
        )

    def test_mock_is_deterministic_structured_and_zero_cost(self):
        provider = MockProvider()
        first = provider.generate_response(self.request)
        second = provider.generate_response(self.request)
        self.assertEqual(first, second)
        result = json.loads(first.text)
        self.assertEqual(result["agent_id"], "diretor-cenas")
        self.assertEqual(result["mode"], "mock")
        self.assertEqual(result["findings"], [])
        self.assertFalse(result["human_visual_approval"])
        self.assertTrue(first.simulated)
        self.assertEqual(first.usage, {"input_tokens": 0, "output_tokens": 0})
        self.assertEqual(first.cost_usd, Decimal("0"))
        self.assertEqual(provider.estimate_cost(self.request)["upper_bound_usd"], Decimal("0"))

    def test_mock_changes_with_input_and_is_network_free(self):
        provider = MockProvider()
        changed = GenerationRequest(**{**self.request.__dict__, "input": "different"})
        self.assertNotEqual(provider.generate_response(self.request).text,
                            provider.generate_response(changed).text)
        self.assertFalse(provider.get_capabilities()["uses_network"])

    def test_factory_defaults_to_mock_even_when_ai_gates_are_closed(self):
        with patch.dict(os.environ, {"AI_ENABLED": "false", "PAID_CALLS_ENABLED": "false"}, clear=True):
            self.assertIsInstance(from_environment(), MockProvider)

    def test_real_provider_is_blocked_by_default_and_does_not_fallback(self):
        with patch.dict(os.environ, {"AI_PROVIDER": "openai", "AI_ENABLED": "false",
                                     "PAID_CALLS_ENABLED": "false"}, clear=True):
            with self.assertRaises(ProviderBlockedError):
                from_environment()

    def test_real_provider_requires_explicit_model_prices_and_key(self):
        valid = {"AI_PROVIDER": "openai", "AI_ENABLED": "true", "PAID_CALLS_ENABLED": "true",
                 "AI_MODEL": "model-explicit", "AI_INPUT_USD_PER_MILLION": "1.00",
                 "AI_OUTPUT_USD_PER_MILLION": "2.00", "OPENAI_API_KEY": "secret-not-logged"}
        with patch.dict(os.environ, valid, clear=True):
            provider = from_environment()
        self.assertIsInstance(provider, OpenAIResponsesProvider)
        self.assertEqual(provider.get_capabilities()["endpoint"], "https://api.openai.com/v1/responses")
        estimate = provider.estimate_cost(self.request)
        self.assertEqual(estimate["upper_bound_usd"], Decimal("0.001279"))
        self.assertEqual(estimate["request_overhead_tokens_budget"], 1024)
        self.assertIn("not_invoice_or_billing_guarantee", estimate["pricing_source"])
        with patch.dict(os.environ, {key: value for key, value in valid.items() if key != "AI_MODEL"}, clear=True):
            with self.assertRaises(ProviderBlockedError):
                from_environment()

    def test_proxy_requires_explicit_authorization_and_safe_base_url(self):
        base = {"AI_PROVIDER": "codex_proxy", "AI_ENABLED": "true", "PAID_CALLS_ENABLED": "true",
                "AI_MODEL": "model-explicit", "AI_INPUT_USD_PER_MILLION": "1",
                "AI_OUTPUT_USD_PER_MILLION": "2", "CODEX_PROXY_API_KEY": "proxy-secret",
                "CODEX_PROXY_BASE_URL": "https://proxy.example"}
        with patch.dict(os.environ, base, clear=True):
            with self.assertRaises(ProviderBlockedError):
                from_environment()
        with patch.dict(os.environ, {**base, "CODEX_PROXY_TEXT_AUTHORIZED": "true"}, clear=True):
            provider = from_environment()
        self.assertIsInstance(provider, CodexProxyResponsesProvider)
        self.assertEqual(provider.get_capabilities()["endpoint"], "https://proxy.example/v1/responses")
        with self.assertRaises(ProviderBlockedError):
            CodexProxyResponsesProvider(api_key="x", model="m", input_price_per_million=Decimal("1"),
                                        output_price_per_million=Decimal("1"),
                                        base_url="http://proxy.example")

    def test_input_output_timeout_limits_fail_before_network(self):
        provider = MockProvider()
        too_large = GenerationRequest(**{**self.request.__dict__, "input": "x" * 1001})
        with self.assertRaises(ValueError):
            provider.generate_response(too_large)
        with self.assertRaises(ValueError):
            provider.generate_response(GenerationRequest(**{**self.request.__dict__, "max_output_tokens": 16_385}))
        with self.assertRaises(ValueError):
            provider.generate_response(GenerationRequest(**{**self.request.__dict__, "timeout_seconds": 121}))

    def test_openai_response_parses_usage_without_logging_credentials(self):
        provider = OpenAIResponsesProvider(api_key="secret-never-print", model="model-explicit",
                                           input_price_per_million=Decimal("1"),
                                           output_price_per_million=Decimal("2"))

        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, _limit):
                return json.dumps({"output": [{"type": "message", "content": [
                    {"type": "output_text", "text": "ok"}]}],
                    "usage": {"input_tokens": 10, "output_tokens": 5}}).encode()

        class FakeOpener:
            def open(self, _request, timeout):
                self.timeout = timeout
                return FakeResponse()

        fake_opener = FakeOpener()
        with patch.dict(os.environ, {"AI_ENABLED": "true", "PAID_CALLS_ENABLED": "true"}, clear=True):
            with patch("providers.urllib.request.build_opener", return_value=fake_opener) as build_opener:
                result = provider.generate_response(self.request)
        self.assertEqual(result.text, "ok")
        self.assertEqual(result.usage, {"input_tokens": 10, "output_tokens": 5})
        self.assertEqual(result.cost_usd, Decimal("0.000020"))
        self.assertTrue(result.cost_is_configured_price_estimate)
        self.assertEqual(fake_opener.timeout, 3.0)
        build_opener.assert_called_once()
        self.assertIsInstance(build_opener.call_args.args[0], urllib.request.HTTPRedirectHandler)

    def test_direct_constructor_still_honors_disabled_flags(self):
        provider = OpenAIResponsesProvider(api_key="secret", model="model-explicit",
                                           input_price_per_million=Decimal("1"),
                                           output_price_per_million=Decimal("2"))
        with patch.dict(os.environ, {}, clear=True):
            with patch("providers.urllib.request.build_opener") as build_opener:
                with self.assertRaises(ProviderBlockedError):
                    provider.generate_response(self.request)
        build_opener.assert_not_called()

    def test_direct_constructor_revalidates_endpoint_and_prices_before_network(self):
        bad_configurations = (
            {"endpoint": "https://attacker.example/v1/responses"},
            {"input_price_per_million": Decimal("NaN")},
            {"output_price_per_million": Decimal("-1")},
            {"api_key": ""},
            {"model": ""},
        )
        for overrides in bad_configurations:
            config = {"api_key": "direct-secret", "model": "model-explicit",
                      "input_price_per_million": Decimal("1"),
                      "output_price_per_million": Decimal("2")}
            config.update(overrides)
            provider = OpenAIResponsesProvider(**config)
            with self.subTest(overrides=overrides):
                with patch.dict(os.environ, {"AI_ENABLED": "true", "PAID_CALLS_ENABLED": "true"}, clear=True):
                    with patch("providers.urllib.request.build_opener") as build_opener:
                        with self.assertRaises(ProviderBlockedError):
                            provider.generate_response(self.request)
                build_opener.assert_not_called()

    def test_redirect_is_rejected_without_following_or_exposing_credentials(self):
        provider = OpenAIResponsesProvider(api_key="redirect-secret", model="model-explicit",
                                           input_price_per_million=Decimal("1"),
                                           output_price_per_million=Decimal("2"))
        redirected = urllib.error.HTTPError("https://attacker.example/collect", 302,
                                            "redirect", {}, None)

        class FakeOpener:
            def open(self, _request, timeout):
                raise redirected

        fake_opener = FakeOpener()
        with patch.dict(os.environ, {"AI_ENABLED": "true", "PAID_CALLS_ENABLED": "true"}, clear=True):
            with patch("providers.urllib.request.build_opener", return_value=fake_opener) as build_opener:
                with self.assertRaises(ProviderError) as raised:
                    provider.generate_response(self.request)
        self.assertIn("302", str(raised.exception))
        self.assertNotIn("redirect-secret", str(raised.exception))
        self.assertNotIn("attacker.example", str(raised.exception))
        handler = build_opener.call_args.args[0]
        self.assertIsInstance(handler, urllib.request.HTTPRedirectHandler)
        self.assertIsNone(handler.redirect_request(
            urllib.request.Request("https://api.openai.com/v1/responses"), None,
            302, "redirect", {}, "https://attacker.example/collect"))

    def test_timeout_error_is_sanitized(self):
        provider = OpenAIResponsesProvider(api_key="timeout-secret", model="model-explicit",
                                           input_price_per_million=Decimal("1"),
                                           output_price_per_million=Decimal("2"))

        class FakeOpener:
            def open(self, _request, timeout):
                raise TimeoutError("timeout with timeout-secret and private URL")

        with patch.dict(os.environ, {"AI_ENABLED": "true", "PAID_CALLS_ENABLED": "true"}, clear=True):
            with patch("providers.urllib.request.build_opener", return_value=FakeOpener()):
                with self.assertRaises(ProviderError) as raised:
                    provider.generate_response(self.request)
        self.assertIn("timed out", str(raised.exception))
        self.assertNotIn("timeout-secret", str(raised.exception))
        self.assertNotIn("private URL", str(raised.exception))

    def test_http_429_is_sanitized_and_not_retried(self):
        provider = OpenAIResponsesProvider(api_key="super-secret", model="model-explicit",
                                           input_price_per_million=Decimal("1"),
                                           output_price_per_million=Decimal("2"))
        error = urllib.error.HTTPError(
            "https://api.openai.com/v1/responses", 429, "limited", {}, None)
        class FakeOpener:
            def open(self, _request, timeout):
                raise error

        fake_opener = FakeOpener()
        with patch.dict(os.environ, {"AI_ENABLED": "true", "PAID_CALLS_ENABLED": "true"}, clear=True):
            with patch("providers.urllib.request.build_opener", return_value=fake_opener):
                with self.assertRaises(ProviderError) as raised:
                    provider.generate_response(self.request)
        self.assertIn("429", str(raised.exception))
        self.assertNotIn("super-secret", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
