"""Non-generative Codex proxy preflight: GET /health and /v1/models ONLY.

Never sends inference or image requests. Requires an explicitly configured
authorized proxy; credentials are never printed or written to the report.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


class PreflightError(ValueError):
    """A sanitized, actionable preflight failure."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def normalize_origin(value: str) -> tuple[str, str]:
    if not value or not isinstance(value, str):
        raise PreflightError("CODEX_PROXY_BASE_URL is not configured")
    try:
        url = urllib.parse.urlsplit(value.strip())
        port = url.port
    except ValueError:
        raise PreflightError("Invalid proxy URL") from None
    local = url.scheme == "http" and url.hostname == "127.0.0.1" and port == 18080
    remote = url.scheme == "https" and bool(url.hostname) and url.hostname not in {"localhost", "127.0.0.1", "::1"}
    if (not (local or remote) or url.username or url.password or url.query or url.fragment
            or url.path.rstrip("/") not in {"", "/v1"}):
        raise PreflightError("Expected an authorized HTTPS origin or http://127.0.0.1:18080")
    return f"{url.scheme}://{url.netloc}", "local_loopback" if local else "remote_https"


def probe(base_url: str, api_key: str, *, opener=None) -> dict:
    origin, kind = normalize_origin(base_url)
    if not isinstance(api_key, str) or len(api_key) < 20 or "\r" in api_key or "\n" in api_key:
        raise PreflightError("CODEX_PROXY_API_KEY is not configured or is invalid")
    if opener is None:
        opener = urllib.request.build_opener(NoRedirect())
    common = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    results = {}
    for route in ("/health", "/v1/models"):
        request = urllib.request.Request(origin + route, headers=common, method="GET")
        try:
            with opener.open(request, timeout=8) as response:
                raw = response.read(1_000_001)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            raise PreflightError("Proxy unreachable, unauthorized, rate limited, or unavailable") from None
        if len(raw) > 1_000_000:
            raise PreflightError("Proxy response exceeded size limit")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError):
            raise PreflightError("Proxy returned invalid JSON") from None
        if not isinstance(data, dict):
            raise PreflightError("Proxy returned invalid response format")
        results[route] = data
    health = results["/health"]
    if health.get("status") != "ok" or type(health.get("accounts")) is not int or health["accounts"] < 1:
        raise PreflightError("Proxy health did not confirm an authenticated account")
    models = results["/v1/models"].get("data")
    if not isinstance(models, list):
        raise PreflightError("Proxy did not return a model catalog")
    count = sum(isinstance(m, dict) and isinstance(m.get("id"), str) and bool(m["id"]) for m in models)
    return {"schema_version": 1, "mode": "proxy_preflight_read_only",
            "proxy_kind": kind, "authenticated": True, "accounts_configured": health["accounts"],
            "model_count": count, "inference_requests": 0, "image_requests": 0,
            "youtube_publications": 0, "paid_inference_authorized": False,
            "agent_communication_proven": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = probe(os.environ.get("CODEX_PROXY_BASE_URL", ""),
                       os.environ.get("CODEX_PROXY_API_KEY", ""))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False))
    except PreflightError as error:
        # No endpoint URL, request contents or credentials are printed.
        print(json.dumps({"status": "blocked", "reason": str(error),
                          "inference_requests": 0, "image_requests": 0,
                          "youtube_publications": 0}))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
