"""Text generation providers for the multi-agent runtime.

The deterministic provider is free and is not an LLM. Real providers are
fail-closed: callers must explicitly enable AI and paid calls, configure a
model, and provide a conservative price ceiling before any request is sent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import hashlib
import json
import math
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Mapping, Protocol


OFFICIAL_RESPONSES_URL = "https://api.openai.com/v1/responses"
MAX_OUTPUT_TOKENS = 16_384
MAX_TIMEOUT_SECONDS = 120
MAX_INPUT_BYTES = 1_000_000
REQUEST_OVERHEAD_TOKEN_BUDGET = 1024


class ProviderError(RuntimeError):
    """Sanitized provider failure; messages must never contain secrets/body."""


class ProviderBlockedError(ProviderError):
    """A real provider was selected but safety/configuration gates are closed."""


@dataclass(frozen=True)
class GenerationRequest:
    agent_id: str
    instructions: str
    input: str
    model: str | None = None
    max_output_tokens: int = 1200
    input_token_limit: int = 12_000
    timeout_seconds: float = 30
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderResponse:
    """Output plus provider-reported token usage.

    `cost_usd` for a real provider is only calculated from the configured
    price schedule and reported usage. It is not a billing record or guarantee.
    """
    text: str
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    simulated: bool
    cost_usd: Decimal | None = None
    cost_is_configured_price_estimate: bool = False

    @property
    def usage(self) -> dict[str, int | None]:
        return {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens}


class TextProvider(Protocol):
    def generate_response(self, request: GenerationRequest) -> ProviderResponse: ...
    def validate_configuration(self) -> dict[str, Any]: ...
    def estimate_cost(self, request: GenerationRequest) -> dict[str, Any]: ...
    def get_capabilities(self) -> dict[str, Any]: ...


def _validate_request(request: GenerationRequest) -> tuple[str, int]:
    if not isinstance(request, GenerationRequest):
        raise TypeError("request must be GenerationRequest")
    if not isinstance(request.agent_id, str) or not request.agent_id.strip():
        raise ValueError("agent_id is required")
    if not isinstance(request.instructions, str) or not isinstance(request.input, str):
        raise ValueError("instructions and input must be strings")
    if not isinstance(request.input_token_limit, int) or not 1 <= request.input_token_limit <= MAX_INPUT_BYTES:
        raise ValueError("input_token_limit is outside the supported range")
    if not isinstance(request.max_output_tokens, int) or not 1 <= request.max_output_tokens <= MAX_OUTPUT_TOKENS:
        raise ValueError("max_output_tokens is outside the supported range")
    if (isinstance(request.timeout_seconds, bool)
            or not isinstance(request.timeout_seconds, (int, float))
            or not math.isfinite(request.timeout_seconds)
            or not 1 <= request.timeout_seconds <= MAX_TIMEOUT_SECONDS):
        raise ValueError("timeout_seconds is outside the supported range")
    combined = f"{request.instructions}\n\n{request.input}"
    input_bytes = len(combined.encode("utf-8"))
    # Bytes are used as a deliberately conservative upper bound on tokens;
    # every token must encode at least one byte, though this can reject valid
    # large inputs earlier than a tokenizer-specific estimate would.
    if input_bytes > request.input_token_limit:
        raise ValueError("input exceeds the configured conservative token limit")
    return combined, input_bytes


def _positive_price(value: str | None, name: str) -> Decimal:
    if value is None or not value.strip():
        raise ProviderBlockedError(f"{name} must be explicitly configured before paid calls")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ProviderBlockedError(f"{name} must be a finite non-negative decimal") from None
    if not result.is_finite() or result < 0:
        raise ProviderBlockedError(f"{name} must be a finite non-negative decimal")
    return result


def _valid_price(value: Decimal) -> bool:
    return isinstance(value, Decimal) and value.is_finite() and value >= 0


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Do not forward authenticated provider requests through redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class MockProvider:
    """Deterministic local executor. It does not call an AI model or network."""

    name = "mock"
    model = "mock-deterministic-v1"

    def validate_configuration(self) -> dict[str, Any]:
        return {"valid": True, "provider": self.name, "simulated": True, "errors": []}

    def estimate_cost(self, request: GenerationRequest) -> dict[str, Any]:
        _validate_request(request)
        return {"provider": self.name, "currency": "USD", "upper_bound_usd": Decimal("0"),
                "input_tokens_upper_bound": 0, "output_tokens_upper_bound": 0,
                "pricing_source": "deterministic_mock_no_api_call"}

    def get_capabilities(self) -> dict[str, Any]:
        return {"provider": self.name, "simulated": True, "uses_network": False,
                "supports_text": True, "supports_tools": False, "reports_usage": False,
                "max_output_tokens": MAX_OUTPUT_TOKENS, "max_timeout_seconds": MAX_TIMEOUT_SECONDS}

    def generate_response(self, request: GenerationRequest) -> ProviderResponse:
        _validate_request(request)
        instructions_sha = hashlib.sha256(request.instructions.encode("utf-8")).hexdigest()
        input_sha = hashlib.sha256(request.input.encode("utf-8")).hexdigest()
        analysis = f"Deterministic mock; instructions_sha256={instructions_sha}; input_sha256={input_sha}."
        envelope = {"agent_id": request.agent_id, "mode": "mock", "analysis": analysis,
                    "findings": [], "human_visual_approval": False}
        return ProviderResponse(text=json.dumps(envelope, ensure_ascii=False, sort_keys=True),
                                provider=self.name, model=self.model, input_tokens=0,
                                output_tokens=0, simulated=True, cost_usd=Decimal("0"))


class OpenAIResponsesProvider:
    """Official OpenAI Responses API adapter implemented with stdlib HTTP."""

    name = "openai"

    def __init__(self, *, api_key: str, model: str, input_price_per_million: Decimal,
                 output_price_per_million: Decimal, endpoint: str = OFFICIAL_RESPONSES_URL):
        self._api_key = api_key
        self.model = model
        self._input_price = input_price_per_million
        self._output_price = output_price_per_million
        self._endpoint = endpoint

    def validate_configuration(self) -> dict[str, Any]:
        gates_open = (os.getenv("AI_ENABLED", "false").strip().lower() == "true"
                      and os.getenv("PAID_CALLS_ENABLED", "false").strip().lower() == "true")
        valid = bool(self._api_key and self.model and self._endpoint == OFFICIAL_RESPONSES_URL
                     and _valid_price(self._input_price) and _valid_price(self._output_price)
                     and gates_open)
        return {"valid": valid, "provider": self.name, "simulated": False,
                "endpoint": self._endpoint, "model_configured": bool(self.model),
                "api_key_configured": bool(self._api_key), "ai_enabled": gates_open,
                "errors": [] if valid else ["configuration_incomplete_or_gates_closed"]}

    def estimate_cost(self, request: GenerationRequest) -> dict[str, Any]:
        _, input_upper = _validate_request(request)
        output_upper = request.max_output_tokens
        billable_input_upper = input_upper + REQUEST_OVERHEAD_TOKEN_BUDGET
        estimate = (Decimal(billable_input_upper) * self._input_price
                    + Decimal(output_upper) * self._output_price) / Decimal(1_000_000)
        # Round upward to a micro-dollar so a displayed budget ceiling never
        # understates the configured price calculation.
        ceiling = estimate.quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
        return {"provider": self.name, "currency": "USD", "upper_bound_usd": ceiling,
                "input_tokens_upper_bound": billable_input_upper,
                "request_content_bytes": input_upper,
                "request_overhead_tokens_budget": REQUEST_OVERHEAD_TOKEN_BUDGET,
                "output_tokens_upper_bound": output_upper,
                "pricing_source": "explicit_configured_prices_heuristic_not_invoice_or_billing_guarantee"}

    def get_capabilities(self) -> dict[str, Any]:
        return {"provider": self.name, "simulated": False, "uses_network": True,
                "endpoint": self._endpoint, "supports_text": True, "supports_tools": False,
                "reports_usage": True, "max_output_tokens": MAX_OUTPUT_TOKENS,
                "max_timeout_seconds": MAX_TIMEOUT_SECONDS, "automatic_retries": False}

    def generate_response(self, request: GenerationRequest) -> ProviderResponse:
        combined, _ = _validate_request(request)
        self._assert_network_call_allowed()
        if request.model and request.model != self.model:
            raise ProviderBlockedError("request model must match the explicitly configured AI_MODEL")
        payload = {"model": self.model, "instructions": request.instructions,
                   "input": request.input, "max_output_tokens": request.max_output_tokens,
                   "store": False}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = urllib.request.Request(
            self._endpoint, data=body,
            headers={"Authorization": f"Bearer {self._api_key}",
                     "Content-Type": "application/json", "Accept": "application/json"},
            method="POST")
        try:
            opener = urllib.request.build_opener(_NoRedirectHandler())
            with opener.open(http_request, timeout=float(request.timeout_seconds)) as response:
                raw = response.read(4 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            status = exc.code
            if status == 429:
                raise ProviderError("provider rate limited request (HTTP 429); no retry was attempted") from None
            raise ProviderError(f"provider returned HTTP {status}; response details omitted") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ProviderError("provider request failed or timed out; request details omitted") from None
        if len(raw) > 4 * 1024 * 1024:
            raise ProviderError("provider response exceeded the configured size limit")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            raise ProviderError("provider returned invalid JSON") from None
        if not isinstance(data, dict):
            raise ProviderError("provider returned an invalid response shape")
        text = data.get("output_text")
        if not isinstance(text, str):
            text = _extract_output_text(data)
        if not text:
            raise ProviderError("provider response contained no text output")
        usage = data.get("usage")
        usage = usage if isinstance(usage, dict) else {}
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        if not isinstance(input_tokens, int) or isinstance(input_tokens, bool) or input_tokens < 0:
            input_tokens = None
        if not isinstance(output_tokens, int) or isinstance(output_tokens, bool) or output_tokens < 0:
            output_tokens = None
        actual_cost = None
        if input_tokens is not None and output_tokens is not None:
            actual_cost = ((Decimal(input_tokens) * self._input_price
                            + Decimal(output_tokens) * self._output_price) / Decimal(1_000_000))
        return ProviderResponse(text=text, provider=self.name, model=self.model,
                                input_tokens=input_tokens, output_tokens=output_tokens,
                                simulated=False, cost_usd=actual_cost,
                                cost_is_configured_price_estimate=actual_cost is not None)

    def _assert_network_call_allowed(self) -> None:
        if os.getenv("AI_ENABLED", "false").strip().lower() != "true":
            raise ProviderBlockedError("AI_ENABLED is false; real provider is disabled")
        if os.getenv("PAID_CALLS_ENABLED", "false").strip().lower() != "true":
            raise ProviderBlockedError("PAID_CALLS_ENABLED is false; real provider is disabled")
        if not isinstance(self._api_key, str) or not self._api_key:
            raise ProviderBlockedError("API credential is required for the real provider")
        if not isinstance(self.model, str) or not self.model.strip():
            raise ProviderBlockedError("model must be explicitly configured for the real provider")
        if not _valid_price(self._input_price) or not _valid_price(self._output_price):
            raise ProviderBlockedError("finite non-negative input and output prices are required")
        if self.name == "openai":
            if self._endpoint != OFFICIAL_RESPONSES_URL:
                raise ProviderBlockedError("official provider endpoint is fixed")
            return
        if self.name == "codex_proxy":
            if os.getenv("CODEX_PROXY_TEXT_AUTHORIZED", "false").strip().lower() != "true":
                raise ProviderBlockedError("CODEX_PROXY_TEXT_AUTHORIZED is required for proxy calls")
            parsed = urllib.parse.urlsplit(self._endpoint)
            is_loopback = parsed.scheme == "http" and parsed.hostname == "127.0.0.1" and parsed.port == 18080
            is_https = parsed.scheme == "https" and bool(parsed.hostname)
            if (not (is_https or is_loopback) or parsed.username or parsed.password
                    or parsed.query or parsed.fragment or parsed.path != "/v1/responses"):
                raise ProviderBlockedError("proxy response endpoint failed its URL safety check")
            return
        raise ProviderBlockedError("unrecognized real provider")


def _extract_output_text(data: Mapping[str, Any]) -> str:
    chunks: list[str] = []
    output = data.get("output", [])
    if not isinstance(output, list):
        return ""
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content", [])
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") in {"output_text", "text"}:
                value = part.get("text")
                if isinstance(value, str):
                    chunks.append(value)
    return "".join(chunks)


class CodexProxyResponsesProvider(OpenAIResponsesProvider):
    """Explicitly authorized OpenAI-compatible proxy adapter (not official API)."""

    name = "codex_proxy"

    def __init__(self, *, api_key: str, model: str, input_price_per_million: Decimal,
                 output_price_per_million: Decimal, base_url: str):
        parsed = urllib.parse.urlsplit(base_url.strip())
        is_loopback = parsed.scheme == "http" and parsed.hostname == "127.0.0.1" and parsed.port == 18080
        is_https = parsed.scheme == "https" and bool(parsed.hostname)
        if not (is_https or is_loopback) or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ProviderBlockedError("proxy base URL must be an explicit HTTPS origin or fixed local loopback")
        if parsed.path.rstrip("/") not in {"", "/v1"}:
            raise ProviderBlockedError("proxy base URL path must be an origin or /v1")
        origin = f"{parsed.scheme}://{parsed.netloc}"
        super().__init__(api_key=api_key, model=model,
                         input_price_per_million=input_price_per_million,
                         output_price_per_million=output_price_per_million,
                         endpoint=origin + "/v1/responses")

    def validate_configuration(self) -> dict[str, Any]:
        gates_open = (os.getenv("AI_ENABLED", "false").strip().lower() == "true"
                      and os.getenv("PAID_CALLS_ENABLED", "false").strip().lower() == "true"
                      and os.getenv("CODEX_PROXY_TEXT_AUTHORIZED", "false").strip().lower() == "true")
        valid = bool(self._api_key and self.model and _valid_price(self._input_price)
                     and _valid_price(self._output_price) and gates_open)
        return {"valid": valid, "provider": self.name,
                "simulated": False, "endpoint_configured": True,
                "model_configured": bool(self.model), "api_key_configured": bool(self._api_key),
                "ai_enabled": gates_open,
                "errors": [] if valid else ["configuration_incomplete_or_gates_closed"]}


def from_environment(provider_name: str | None = None) -> TextProvider:
    """Build a provider from environment; defaults to the deterministic mock.

    Set AI_PROVIDER=openai or AI_PROVIDER=codex_proxy explicitly. Real requests
    also require AI_ENABLED=true and PAID_CALLS_ENABLED=true. For the proxy,
    CODEX_PROXY_TEXT_AUTHORIZED=true is an additional explicit authorization.
    """
    selected = (provider_name or os.getenv("AI_PROVIDER", "mock")).strip().lower()
    if selected == "mock":
        return MockProvider()
    if selected not in {"openai", "codex_proxy"}:
        raise ProviderBlockedError("unsupported AI_PROVIDER; choose mock, openai, or codex_proxy")
    if os.getenv("AI_ENABLED", "false").strip().lower() != "true":
        raise ProviderBlockedError("AI_ENABLED is false; real provider is disabled")
    if os.getenv("PAID_CALLS_ENABLED", "false").strip().lower() != "true":
        raise ProviderBlockedError("PAID_CALLS_ENABLED is false; real provider is disabled")
    model = os.getenv("AI_MODEL", "").strip()
    if not model:
        raise ProviderBlockedError("AI_MODEL must be explicitly configured for a real provider")
    input_price = _positive_price(os.getenv("AI_INPUT_USD_PER_MILLION"), "AI_INPUT_USD_PER_MILLION")
    output_price = _positive_price(os.getenv("AI_OUTPUT_USD_PER_MILLION"), "AI_OUTPUT_USD_PER_MILLION")
    if selected == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ProviderBlockedError("OPENAI_API_KEY is required for the official OpenAI API")
        return OpenAIResponsesProvider(api_key=key, model=model,
                                       input_price_per_million=input_price,
                                       output_price_per_million=output_price)
    if os.getenv("CODEX_PROXY_TEXT_AUTHORIZED", "false").strip().lower() != "true":
        raise ProviderBlockedError("CODEX_PROXY_TEXT_AUTHORIZED is required to select the proxy")
    key = os.getenv("CODEX_PROXY_API_KEY", "")
    base_url = os.getenv("CODEX_PROXY_BASE_URL", "")
    if not key or not base_url:
        raise ProviderBlockedError("proxy API key and base URL are required")
    return CodexProxyResponsesProvider(api_key=key, model=model,
                                       input_price_per_million=input_price,
                                       output_price_per_million=output_price,
                                       base_url=base_url)


def make_provider(mode: str | None = None) -> TextProvider:
    """Compatibility alias for the runtime factory."""
    return from_environment(mode)
