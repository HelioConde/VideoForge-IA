"""Offline fake-provider coverage for the optional thirteen-call Astra contract."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestrator.agent_bus import fingerprint
from orchestrator.agent_live_roundtrip import (
    SPECIALISTS, NUMBER_OF_CALLS, seed, step,
    _validate_director, _validate_specialist, _validate_qa,
)
from orchestrator.providers import ProviderError
from orchestrator.runtime_store import Store


class FakeModel:
    def __init__(self, rejected=None):
        self.rejected = rejected
        self.calls = []

    def __call__(self, store, task, root, role, payload, mode, limits):
        stage = payload["runtime_stage"]
        self.calls.append((role, stage))
        if stage == "roundtrip_specialist":
            findings = [{
                "role_id": role, "focus": payload["focus"],
                "evidence_sha256": payload["evidence_sha256"],
                "production_ready": False,
                "blockers": ["Visual and media production approval pending"],
                "recommendation": "Request QA and creator approval.",
            }]
        elif stage == "roundtrip_independent_qa":
            findings = [{
                "role_id": specialist,
                "decision": "correction_requested" if specialist == self.rejected else "supported",
                "evidence_sha256": expected,
                "reason": "Source-grounded metadata audit only.",
            } for specialist, expected in payload["expected_source_evidence"].items()]
        elif stage == "roundtrip_consolidation":
            findings = [{
                "status": payload["safe_status"],
                "basis": "Text review only, no production approval.",
                "next_steps": ["Keep visual approval and publishing gated."],
            }]
        else:
            findings = []
        response = {"agent_id": role, "mode": mode,
                    "analysis": "Synthetic test result (no actual model/network).",
                    "findings": findings, "human_visual_approval": False}
        return {"agent_id": role, "model": "gpt-6.2-astra",
                "provider": "codex_proxy", "llm_executed": True,
                "simulated": False, "response_id": "fake-response-" + str(len(self.calls)),
                "response_sha256": fingerprint(response), "response": response}


class LiveRoundtripContractTests(unittest.TestCase):
    def test_all_roles_route_through_real_provider_contract_without_network(self):
        fake = FakeModel()
        with tempfile.TemporaryDirectory() as temp, patch(
            "orchestrator.agent_live_roundtrip.model_step", side_effect=fake
        ):
            store = Store(Path(temp) / "pilot.sqlite")
            try:
                task_id = seed(store, model="gpt-6.2-astra")
                limits = {"usd": 0.25, "tokens": 1000000, "calls": NUMBER_OF_CALLS}
                first = step(store, limits=limits)
                self.assertEqual(first["status"], "needs_review")
                second = step(store, limits=limits)
                self.assertEqual(second["status"], "completed")
                self.assertEqual(len(fake.calls), NUMBER_OF_CALLS)
                self.assertEqual(fake.calls[0], ("01", "roundtrip_assignment"))
                self.assertEqual(fake.calls[-2:], [("12", "roundtrip_independent_qa"),
                                                    ("01", "roundtrip_consolidation")])
                self.assertEqual({r for r, stage in fake.calls if stage == "roundtrip_specialist"},
                                 set(SPECIALISTS))
                self.assertIsNone(step(store, limits=limits))
                self.assertEqual(len(store.export_snapshot()["tables"]["checkpoints"]), 1)
                self.assertFalse(store.result(task_id)["production_ready"])
            finally:
                store.close()

    def test_qa_rejection_creates_blocked_checkpoint_not_false_completion(self):
        fake = FakeModel(rejected="07")
        with tempfile.TemporaryDirectory() as temp, patch(
            "orchestrator.agent_live_roundtrip.model_step", side_effect=fake
        ):
            store = Store(Path(temp) / "pilot.sqlite")
            try:
                seed(store, model="gpt-6.2-astra")
                limits = {"usd": 0.25, "tokens": 1000000, "calls": NUMBER_OF_CALLS}
                self.assertEqual(step(store, limits=limits)["status"], "needs_review")
                result = step(store, limits=limits)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["blocked_reason"], "independent_review_rejected")
                self.assertEqual(len(fake.calls), NUMBER_OF_CALLS)
                self.assertEqual(len(store.export_snapshot()["tables"]["checkpoints"]), 1)
            finally:
                store.close()

    def test_source_mismatch_and_production_approval_are_rejected(self):
        with self.assertRaises(ProviderError):
            _validate_specialist({"findings": [{
                "role_id": "06", "focus": "layer_separation_readiness",
                "evidence_sha256": "invalid", "production_ready": True,
                "blockers": ["missing"], "recommendation": "review",
            }]}, "06", "a" * 64)
        with self.assertRaises(ProviderError):
            _validate_qa({"findings": []}, {"02": {"evidence_sha256": "a" * 64}})
        with self.assertRaises(ProviderError):
            _validate_director({"findings": [{"status": "completed", "basis": "wrong",
                                             "next_steps": ["publish"]}]}, True)


if __name__ == "__main__":
    unittest.main()
