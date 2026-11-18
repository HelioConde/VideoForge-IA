"""Offline Codex proxy checks. Every network transport in this file is fake."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from orchestrator import runtime
from orchestrator.providers import from_environment, ProviderBlockedError
from orchestrator.proxy_preflight import probe, normalize_origin, PreflightError
from orchestrator.runtime_store import Store


PROXY_ENV = {
    "AI_PROVIDER": "codex_proxy",
    "AI_ENABLED": "true",
    "PAID_CALLS_ENABLED": "true",
    "CODEX_PROXY_TEXT_AUTHORIZED": "true",
    "CODEX_PROXY_BASE_URL": "http://127.0.0.1:18080",
    "CODEX_PROXY_API_KEY": "synthetic-unit-test-key-never-valid",
    "AI_MODEL": "offline-contract-test-model",
    "AI_INPUT_USD_PER_MILLION": "1",
    "AI_OUTPUT_USD_PER_MILLION": "1",
    "IMAGE_GENERATION_ENABLED": "false",
    "YOUTUBE_PUBLICATION_ENABLED": "false",
}


class FakeHTTPResponse:
    def __init__(self, payload):
        self.body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _limit):
        return self.body


class FakeProxy:
    """Only in-memory responses; never creates a network socket."""
    def __init__(self, reject_qa_facet=None):
        self.requests = []
        self.agents = iter(["01", "03", "12", "01"])
        self.reject_qa_facet = reject_qa_facet

    def open(self, request, timeout):
        self.requests.append(request)
        if request.get_method() != "POST" or request.full_url != "http://127.0.0.1:18080/v1/responses":
            raise AssertionError("Unexpected outbound HTTP operation")
        if request.get_header("Authorization") != "Bearer " + PROXY_ENV["CODEX_PROXY_API_KEY"]:
            raise AssertionError("Invalid proxy authentication contract")
        body = json.loads(request.data)
        if body.get("stream") is not False or body.get("model") != PROXY_ENV["AI_MODEL"]:
            raise AssertionError("Proxy must request an explicit non-streaming response")
        if not isinstance(body.get("instructions"), str) or not body["instructions"]:
            raise AssertionError("Agent instructions were omitted")
        agent = next(self.agents)
        try:
            payload = json.loads(body["input"])
        except (ValueError, TypeError):
            payload = {}
        instructions = body["instructions"]
        stage = next((candidate for candidate in (
            "director_dispatch", "scene_continuity_analysis", "independent_qa_review", "director_consolidation"
        ) if f"Runtime call stage: {candidate}." in instructions), None)
        findings = []
        if stage == "director_dispatch":
            findings = [{"kind": "task_assignment", "recipient": "03", "task_id": payload["selected_task"],
                         "objective": "Analyze the pinned C07/C08 continuity manifest in read-only mode.",
                         "input_refs": payload["input_refs"],
                         "acceptance_criteria": list(runtime.CHAIN_FACETS),
                         "restrictions": ["manifest text only", "no visual inspection claims", "no production edits"]}]
        elif stage in {"scene_continuity_analysis", "independent_qa_review"}:
            source_map = payload.get("context") or payload.get("source_context") or {}
            source_ref = runtime.MANIFEST.as_posix()
            document = json.loads(source_map[source_ref])
            pointers = {
                "escape_direction": "/rules/screen_flee_direction",
                "relative_positions": "/shots/2/required_axis",
                "pursuer_positions": "/rules/pursuers_origin",
                "cart_continuity": "/rules/cart_initial",
                "shot_order": "/shots/0/id",
                "narrative_consistency": "/creator_feedback",
                "transition_requirements": "/editorial_v2/adds",
            }
            citations = {}
            for facet, pointer in pointers.items():
                value = runtime._json_pointer(document, pointer)
                citations[facet] = {"source_ref": source_ref, "json_pointer": pointer}
            if stage == "scene_continuity_analysis":
                findings = [{"id": f"finding-{index}", "facet": facet,
                             "claim": f"Source-backed review of {facet}", "recommendation": "Check stated continuity",
                             "evidence": [citations[facet]]}
                            for index, facet in enumerate(runtime.CHAIN_FACETS, 1)]
            else:
                producer = payload["producer_report"]["analysis"]["response"]["findings"]
                findings = [{"facet": facet,
                             "decision": "correction_requested" if facet == self.reject_qa_facet else "supported",
                             "rationale": "Citation resolves to the pinned manifest value." if facet != self.reject_qa_facet else "The cited source does not support the reported relationship.",
                             "reviewed_finding_ids": [row["id"] for row in producer if row["facet"] == facet],
                             "evidence": [citations[facet]]} for facet in runtime.CHAIN_FACETS]
        elif stage == "director_consolidation":
            findings = [{"status": "needs_human_review", "basis": "Text audit only", "next_steps": ["Review production visuals"]}]
        response = {
            "model": PROXY_ENV["AI_MODEL"],
            "output": [{"type": "message", "content": [{"type": "output_text",
                       "text": json.dumps({"agent_id": agent, "mode": "proxy-contract-test",
                                           "analysis": "Synthetic response, no actual AI.",
                                           "findings": findings, "human_visual_approval": False})}]}],
            "usage": {"input_tokens": 10, "output_tokens": 15}
        }
        return FakeHTTPResponse(response)


class OfflineProxyContractTests(unittest.TestCase):
    def test_proxy_is_blocked_by_default_without_network(self):
        blocked = dict(PROXY_ENV, AI_ENABLED="false", PAID_CALLS_ENABLED="false")
        with patch.dict(os.environ, blocked, clear=True):
            with patch("orchestrator.providers.urllib.request.build_opener") as opener:
                with self.assertRaises(ProviderBlockedError):
                    from_environment("codex_proxy")
                opener.assert_not_called()

    def test_preflight_uses_only_non_generative_get_routes(self):
        requests = []
        class FakeGet:
            def open(self, req, timeout):
                requests.append((req.full_url, req.get_method()))
                if req.get_method() != "GET":
                    raise AssertionError("Preflight attempted a paid or mutating operation")
                if req.full_url.endswith("/health"):
                    return FakeHTTPResponse({"status": "ok", "accounts": 1})
                if req.full_url.endswith("/v1/models"):
                    return FakeHTTPResponse({"data": [{"id": "offline-model"}]})
                raise AssertionError("Unexpected route")
        result = probe("http://127.0.0.1:18080", "synthetic-unit-test-key-never-valid", opener=FakeGet())
        self.assertEqual(requests, [
            ("http://127.0.0.1:18080/health", "GET"),
            ("http://127.0.0.1:18080/v1/models", "GET"),
        ])
        self.assertTrue(result["authenticated"])
        self.assertEqual(result["model_count"], 1)
        self.assertEqual(result["inference_requests"], 0)
        self.assertFalse(result["agent_communication_proven"])

    def test_preflight_required_model_uses_get_catalog_only(self):
        requests = []
        class FakeGet:
            def open(self, request, timeout):
                requests.append((request.get_method(), request.full_url))
                if request.full_url.endswith("/health"):
                    return FakeHTTPResponse({"status": "ok", "accounts": 1})
                return FakeHTTPResponse({"data": [{"id": "model-present"}]})
        options = {"opener": FakeGet(), "require_model": "model-present"}
        result = probe("http://127.0.0.1:18080",
                       "synthetic-unit-test-key-never-valid", **options)
        self.assertEqual(result["model_count"], 1)
        self.assertEqual(len(requests), 2)
        self.assertTrue(all(method == "GET" for method, _ in requests))
        with self.assertRaises(PreflightError):
            probe("http://127.0.0.1:18080",
                  "synthetic-unit-test-key-never-valid",
                  opener=FakeGet(), require_model="model-absent")

    def test_get_only_model_catalog_lists_ids_without_generation(self):
        paths = []
        class FakeCatalog:
            def open(self, request, timeout):
                paths.append((request.full_url, request.get_method()))
                if request.full_url.endswith("/health"):
                    return FakeHTTPResponse({"status": "ok", "accounts": 1})
                return FakeHTTPResponse({"data": [{"id": "gpt-6.1-sol"}, {"id": "gpt-6.1-sol"},
                                                    {"id": "gpt-image-2"}]})
        result = probe("http://127.0.0.1:18080",
                       "synthetic-unit-test-key-never-valid",
                       opener=FakeCatalog(), list_models=True)
        self.assertEqual(result["model_ids"], ["gpt-6.1-sol", "gpt-image-2"])
        self.assertEqual(result["model_count"], 2)
        self.assertFalse(result["catalog_contains_text_capability_proof"])
        self.assertEqual([method for _, method in paths], ["GET", "GET"])
        self.assertEqual(result["inference_requests"], 0)

    def test_malformed_catalog_ids_cannot_appear_in_artifact(self):
        class FakeBadCatalog:
            def open(self, request, timeout):
                if request.full_url.endswith("/health"):
                    return FakeHTTPResponse({"status": "ok", "accounts": 1})
                return FakeHTTPResponse({"data": [{"id": "valid"}, {"id": "bad\\nkey"}]})
        result = probe("http://127.0.0.1:18080", "synthetic-unit-test-key-never-valid",
                       opener=FakeBadCatalog(), list_models=True)
        self.assertEqual(result["model_ids"], ["valid"])
        self.assertEqual(result["model_ids_omitted"], 1)
        self.assertNotIn("bad\\nkey", json.dumps(result))

    def test_preflight_rejects_insecure_endpoint_and_sanitizes_errors(self):
        for invalid in ("http://external.example:18080", "http://localhost:18080",
                        "https://user:secret@example.com", "https://example.com/proxy"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(PreflightError):
                    normalize_origin(invalid)
        class FailedGet:
            def open(self, req, timeout):
                raise urllib.error.URLError("secret-message-from-network")
        with self.assertRaises(PreflightError) as caught:
            probe("http://127.0.0.1:18080", "synthetic-unit-test-key-never-valid", opener=FailedGet())
        self.assertNotIn("secret-message", str(caught.exception))

    def test_ephemeral_proxy_bypasses_runner_http_proxy(self):
        import urllib.request
        from orchestrator.providers import GenerationRequest, _NoRedirectHandler
        fake = FakeProxy()
        with patch.dict(os.environ, {**PROXY_ENV, "HTTP_PROXY": "http://untrusted.proxy.invalid:8181",
                                     "HTTPS_PROXY": "http://untrusted.proxy.invalid:8181"}, clear=True):
            with patch("orchestrator.providers.urllib.request.build_opener", return_value=fake) as factory:
                provider = from_environment("codex_proxy")
                response = provider.generate_response(GenerationRequest(
                    agent_id="01", instructions="Director instructions", input="health contract",
                    input_token_limit=2048, max_output_tokens=100))
        self.assertEqual(len(fake.requests), 1)
        self.assertEqual(response.provider, "codex_proxy")
        handlers = factory.call_args.args
        self.assertTrue(any(isinstance(x, urllib.request.ProxyHandler) and x.proxies == {} for x in handlers))
        self.assertTrue(any(isinstance(x, _NoRedirectHandler) for x in handlers))

    def test_agent_01_03_12_01_proxy_contract_without_inference(self):
        fake = FakeProxy()
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory) / "state.sqlite")
            try:
                with patch.dict(os.environ, PROXY_ENV, clear=True), patch(
                    "orchestrator.providers.urllib.request.build_opener", return_value=fake
                ):
                    runtime.seed(store, mode="codex_proxy", continuity_only=True)
                    limits = {"usd": 100, "tokens": 1_000_000, "calls": 8}
                    first = runtime.step(store, mode="codex_proxy", limits=limits)
                    second = runtime.step(store, mode="codex_proxy", limits=limits)
                    self.assertEqual(first["status"], "needs_review")
                    self.assertEqual(second["status"], "completed")
                    snapshot = runtime.report(store)
                self.assertEqual(len(fake.requests), 4)
                self.assertEqual(len(snapshot["checkpoints"]), 1)
                self.assertEqual(len(snapshot["usage"]), 4)
                self.assertEqual([row["agent_id"] for row in snapshot["usage"]], ["01", "03", "12", "01"])
                self.assertTrue(all(row["state"] == "settled" and row["model"] == PROXY_ENV["AI_MODEL"]
                                    for row in snapshot["usage"]))
                calls = [event["content"] for event in snapshot["events"]
                         if event["type"] == "progress_update"]
                self.assertEqual([row["runtime_stage"] for row in calls], [
                    "director_dispatch", "scene_continuity_analysis",
                    "independent_qa_review", "director_consolidation"])
                self.assertTrue(all(row["report_sha256"] and row["request_sha256"] for row in calls))
                qa_findings = calls[2]["response"]["findings"]
                self.assertEqual({row["facet"] for row in qa_findings}, set(runtime.CHAIN_FACETS))
                self.assertTrue(all(row["reviewed_finding_ids"] and row["evidence"] for row in qa_findings))
                self.assertEqual(snapshot["safety"]["youtube_publications"], 0)
                self.assertFalse(snapshot["checkpoints"][0]["human_visual_approval"])
                routes = {(event["sender"], event["recipient"]) for event in snapshot["events"]}
                self.assertTrue({("01", "03"), ("03", "12"), ("12", "01")} <= routes)
            finally:
                store.close()

    def test_rejected_final_is_journaled_and_reconciles_without_another_call(self):
        from orchestrator.chain_recovery import reconcile
        class InvalidConsolidation(FakeProxy):
            def open(self, request, timeout):
                response = super().open(request, timeout)
                packet = json.loads(response.body)
                packet["id"] = f"resp_synthetic_{len(self.requests):04d}"
                if "Runtime call stage: director_consolidation." in json.loads(request.data)["instructions"]:
                    text_data = json.loads(packet["output"][0]["content"][0]["text"])
                    text_data["findings"] = [{"status": "unsupported", "basis": "Text only",
                                               "next_steps": []}]
                    packet["output"][0]["content"][0]["text"] = json.dumps(text_data)
                return FakeHTTPResponse(packet)
        fake = InvalidConsolidation()
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            PROXY_ENV, {"AI_MODEL": "gpt-6-astra"}
        ), patch.dict(os.environ, {**PROXY_ENV, "AI_MODEL": "gpt-6-astra"}, clear=True), patch(
            "orchestrator.providers.urllib.request.build_opener", return_value=fake
        ):
            store = Store(Path(directory) / "state.sqlite")
            try:
                runtime.seed(store, mode="codex_proxy", continuity_only=True)
                limits = {"usd": 100, "tokens": 1000000, "calls": 4}
                self.assertEqual(runtime.step(store, mode="codex_proxy", limits=limits)["status"], "needs_review")
                blocked = runtime.step(store, mode="codex_proxy", limits=limits)
                self.assertEqual(blocked["status"], "blocked")
                self.assertEqual(blocked["blocked_reason"], "ProviderError")
                self.assertEqual(len(fake.requests), 4)
                events = runtime.report(store)["events"]
                journal = [evt for evt in events if evt["type"] == "progress_update"
                           and evt["content"].get("call_id")]
                self.assertEqual(len(journal), 4)
                last = journal[-1]["content"]
                self.assertEqual(last["validation_status"], "rejected")
                self.assertEqual(last["validation_error"], "Director consolidation decision schema rejected")
                self.assertEqual(len(store.invocation_responses(blocked["task_id"])), 3)
                preview = reconcile(store, blocked["task_id"])
                self.assertEqual(preview["status"], "blocked")
                self.assertEqual(preview["final_validation_reason"], last["validation_error"])
                self.assertTrue(preview["final_output_journaled"])
                self.assertEqual(len(runtime.report(store)["checkpoints"]), 0)
                applied = reconcile(store, blocked["task_id"], apply=True)
                self.assertEqual(applied, preview)
                self.assertEqual(reconcile(store, blocked["task_id"], apply=True), applied)
                self.assertEqual(len(runtime.report(store)["checkpoints"]), 1)
                self.assertEqual(store.get(blocked["task_id"])["status"], "blocked")
                self.assertEqual(len(fake.requests), 4)
                copy = Store(Path(directory) / "reopened.sqlite")
                try:
                    copy.import_snapshot(store.export_snapshot())
                    self.assertEqual(len(runtime.report(copy)["checkpoints"]), 1)
                    self.assertEqual(copy.get(blocked["task_id"])["status"], "blocked")
                finally:
                    copy.close()
            finally:
                store.close()

    def test_legacy_missing_final_body_creates_only_blocked_reconciliation(self):
        from orchestrator.chain_recovery import reconcile
        class InvalidConsolidation(FakeProxy):
            def open(self, request, timeout):
                response = super().open(request, timeout)
                packet = json.loads(response.body)
                packet["id"] = f"resp_synthetic_{len(self.requests):04d}"
                if "Runtime call stage: director_consolidation." in json.loads(request.data)["instructions"]:
                    text_data = json.loads(packet["output"][0]["content"][0]["text"])
                    text_data["findings"] = [{"status": "wrong", "basis": "not valid",
                                               "next_steps": []}]
                    packet["output"][0]["content"][0]["text"] = json.dumps(text_data)
                return FakeHTTPResponse(packet)
        fake = InvalidConsolidation()
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            PROXY_ENV, {"AI_MODEL": "gpt-6-astra"}
        ), patch.dict(os.environ, {**PROXY_ENV, "AI_MODEL": "gpt-6-astra"}, clear=True), patch(
            "orchestrator.providers.urllib.request.build_opener", return_value=fake
        ):
            store = Store(Path(directory) / "legacy.sqlite")
            try:
                runtime.seed(store, mode="codex_proxy", continuity_only=True)
                limits = {"usd": 100, "tokens": 1000000, "calls": 4}
                runtime.step(store, mode="codex_proxy", limits=limits)
                task = runtime.step(store, mode="codex_proxy", limits=limits)
                self.assertEqual(task["status"], "blocked")
                last = store.db.execute(
                    "SELECT call_id FROM usage WHERE agent_id='01' ORDER BY rowid DESC LIMIT 1"
                ).fetchone()["call_id"]
                # Simulate the exact 2026-11-18 legacy bug: settled tokens and
                # SHA, but no saved final response envelope.
                for row in store.db.execute("SELECT event_id,envelope FROM events"):
                    if json.loads(row["envelope"]).get("content", {}).get("call_id") == last:
                        store.db.execute("DELETE FROM events WHERE event_id=?", (row["event_id"],))
                checkpoint = reconcile(store, task["task_id"], apply=True)
                self.assertFalse(checkpoint["final_output_journaled"])
                self.assertEqual(checkpoint["final_validation_reason"], "unavailable_in_legacy_journal")
                self.assertEqual(checkpoint["llm_calls_replayed"], 0)
                self.assertFalse(checkpoint["technical_completion_approved"])
                self.assertEqual(len(fake.requests), 4)
            finally:
                store.close()

    def test_invalid_final_json_shape_is_accounted_and_never_replayed(self):
        from orchestrator.chain_recovery import reconcile
        class InvalidShape(FakeProxy):
            def open(self, request, timeout):
                response = super().open(request, timeout)
                packet = json.loads(response.body)
                packet["id"] = f"resp_synthetic_{len(self.requests):04d}"
                if "Runtime call stage: director_consolidation." in json.loads(request.data)["instructions"]:
                    # Deliberately omit required analysis and return four valid transport envelopes.
                    payload = {"agent_id": "01", "mode": "codex_proxy",
                               "findings": [], "human_visual_approval": False}
                    packet["output"][0]["content"][0]["text"] = json.dumps(payload)
                return FakeHTTPResponse(packet)
        fake = InvalidShape()
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            PROXY_ENV, {"AI_MODEL": "gpt-6-astra"}
        ), patch.dict(os.environ, {**PROXY_ENV, "AI_MODEL": "gpt-6-astra"}, clear=True), patch(
            "orchestrator.providers.urllib.request.build_opener", return_value=fake
        ):
            store = Store(Path(directory) / "state.sqlite")
            try:
                runtime.seed(store, mode="codex_proxy", continuity_only=True)
                limits = {"usd": 100, "tokens": 1000000, "calls": 4}
                runtime.step(store, mode="codex_proxy", limits=limits)
                task = runtime.step(store, mode="codex_proxy", limits=limits)
                self.assertEqual(task["status"], "blocked")
                self.assertEqual(len(fake.requests), 4)
                usage = runtime.report(store)["usage"]
                self.assertTrue(all(row["state"] == "settled" for row in usage))
                last = [evt["content"] for evt in runtime.report(store)["events"]
                        if evt["type"] == "progress_update"][-1]
                self.assertEqual(last["validation_status"], "rejected")
                self.assertEqual(last["validation_error"], "Model report schema rejected")
                self.assertNotIn("response", last)
                self.assertEqual(len(store.invocation_responses(task["task_id"])), 3)
                checkpoint = reconcile(store, task["task_id"], apply=True)
                self.assertFalse(checkpoint["final_output_journaled"])
                self.assertEqual(checkpoint["final_validation_reason"], "Model report schema rejected")
                self.assertEqual(store.get(task["task_id"])["status"], "blocked")
            finally:
                store.close()

    def test_real_chain_qa_rejection_blocks_without_replaying_calls(self):
        fake = FakeProxy(reject_qa_facet="cart_continuity")
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory) / "state.sqlite")
            try:
                with patch.dict(os.environ, PROXY_ENV, clear=True), patch(
                    "orchestrator.providers.urllib.request.build_opener", return_value=fake
                ):
                    runtime.seed(store, mode="codex_proxy", continuity_only=True)
                    limits = {"usd": 100, "tokens": 1_000_000, "calls": 8}
                    runtime.step(store, mode="codex_proxy", limits=limits)
                    rejected = runtime.step(store, mode="codex_proxy", limits=limits)
                    self.assertEqual(rejected["status"], "blocked")
                    self.assertIsNone(runtime.step(store, mode="codex_proxy", limits=limits))
                self.assertEqual(len(fake.requests), 4)
                state = runtime.report(store)
                rejection = next(event for event in state["events"] if event["type"] == "review_rejected")
                self.assertIn("cart_continuity", json.dumps(rejection["content"], ensure_ascii=False))
                self.assertIn("does not support", json.dumps(rejection["content"], ensure_ascii=False))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
