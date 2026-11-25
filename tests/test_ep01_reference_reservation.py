"""Offline tests of real GitHub Contents CAS semantics; no HTTP or provider."""
import base64
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from orchestrator.github_state import GitHubStateError, StateConflict
from scripts import ep01_action_production_queue as queue
from videoforge import ep01_reference_request as request
from videoforge import ep01_reference_reservation as reservation
from videoforge.errors import VideoForgeError

REAL_REMOTE = queue.QueueRemote
ENV = {"GITHUB_REPOSITORY": "HelioConde/VideoForge-IA",
       "GITHUB_REF": "refs/heads/main", "GITHUB_TOKEN": "offline-test",
       "GH_TOKEN": "offline-test", "GITHUB_RUN_ID": "1234", "GITHUB_RUN_ATTEMPT": "1"}


class CasServer:
    """Only the HTTP boundary is faked; load/save/schema/CAS code stays real."""
    def __init__(self):
        self.snapshot = None
        self.sha = None
        self.puts = 0
        self.failure = None
        self.before_put = None

    def call(self, method, url, payload=None):
        if method == "GET" and "/git/ref/" in url:
            return 200, {"object": {"sha": "a" * 40}}
        if method == "GET":
            if self.snapshot is None:
                return 404, {}
            return 200, {"sha": self.sha, "content": base64.b64encode(
                json.dumps(self.snapshot).encode()).decode()}
        assert method == "PUT"
        self.puts += 1
        if self.before_put:
            callback, self.before_put = self.before_put, None
            callback()
        if self.failure == "before":
            raise GitHubStateError("Simulated network failure")
        if payload.get("sha") != self.sha:
            return 409, {}
        self.snapshot = json.loads(base64.b64decode(payload["content"]))
        self.sha = str(self.puts).zfill(40)
        if self.failure == "after":
            raise GitHubStateError("Simulated lost acknowledgement")
        return 200, {} if self.failure == "missing_sha" else {"content": {"sha": self.sha}}


class ReferenceReservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = request.prepare_request(
            "C11-P03", "character-kael",
            "9a03b7c13414707b34256c95cfc3d675f80588c9547d54c6374d7bcd26d73603")

    def setUp(self):
        self.server = CasServer()
        self.enterContext(patch.dict("os.environ", ENV))
        self.enterContext(patch.object(REAL_REMOTE, "_request", side_effect=self.server.call))
        self.provider = self.enterContext(patch.object(request.parts.proxy_images, "call_proxy",
            side_effect=AssertionError("Provider must never be called")))

    def reserve(self, bundle=None):
        bundle = self.bundle if bundle is None else bundle
        return reservation.reserve_request(bundle, bundle["request_sha256"])

    def test_durable_receipt_contains_no_payload_or_approval_and_freezes_legacy_queue(self):
        before = deepcopy(self.bundle)
        receipt = self.reserve()
        row = self.server.snapshot["attempts"][receipt["reservation_key"]]
        self.assertEqual(receipt["ledger_blob_sha"], self.server.sha)
        self.assertEqual(row["request_sha256"], self.bundle["request_sha256"])
        self.assertEqual(row["reference_sha256"],
                         self.bundle["reference_manifest"]["reference_sha256"])
        self.assertEqual(row["reserved_by_run_attempt"], "1")
        self.assertNotIn("payload", row)
        self.assertNotIn("prompt", row)
        self.assertNotIn("offline-test", json.dumps(self.server.snapshot))
        self.assertFalse(receipt["generation_authorized"])
        self.assertEqual(receipt["provider_calls"], 0)
        self.assertEqual(self.bundle, before)
        with patch.object(queue, "reconcile_rejected_archives", return_value=[]), patch.object(
                queue, "reconcile_failed_preflight", return_value=[]), patch.object(
                queue, "dispatch_child") as dispatch:
            with self.assertRaisesRegex(RuntimeError, "UNRESOLVED_EXTERNAL_ATTEMPT"):
                queue.run_remote({"tasks": []}, 1, 0)
            dispatch.assert_not_called()
        self.provider.assert_not_called()

    def test_restart_and_action_rerun_never_replay_or_replace_reservation(self):
        self.reserve()
        original = deepcopy(self.server.snapshot)
        for attempt in ("1", "2"):
            with patch.dict("os.environ", {"GITHUB_RUN_ATTEMPT": attempt}):
                with self.assertRaisesRegex(VideoForgeError, "ALREADY_RESERVED_NO_REPLAY"):
                    self.reserve()
        self.assertEqual(self.server.snapshot, original)
        self.assertEqual(self.server.puts, 1)

    def test_two_writers_racing_on_absent_ledger_only_one_gets_receipt(self):
        receipts = []
        self.server.before_put = lambda: receipts.append(self.reserve())
        with self.assertRaises(StateConflict):
            self.reserve()
        self.assertEqual(len(receipts), 1)
        self.assertEqual(len(self.server.snapshot["attempts"]), 1)
        self.assertEqual(self.server.puts, 2)
        self.provider.assert_not_called()

    def test_lost_acknowledgement_never_returns_receipt_and_restart_sees_fence(self):
        for failure in ("after", "missing_sha"):
            with self.subTest(failure=failure):
                self.server.snapshot, self.server.sha = None, None
                self.server.failure = failure
                with self.assertRaises(GitHubStateError):
                    self.reserve()
                self.assertEqual(len(self.server.snapshot["attempts"]), 1)
                self.server.failure = None
                puts = self.server.puts
                with self.assertRaisesRegex(VideoForgeError, "ALREADY_RESERVED_NO_REPLAY"):
                    self.reserve()
                self.assertEqual(self.server.puts, puts)

    def test_failed_write_before_commit_returns_no_receipt_or_side_effect(self):
        self.server.failure = "before"
        with self.assertRaises(GitHubStateError):
            self.reserve()
        self.assertIsNone(self.server.snapshot)
        self.provider.assert_not_called()

    def test_unresolved_legacy_attempts_block_new_version_without_ledger_changes(self):
        for status in ("reserved", "dispatched", "blocked_uncertain", "blocked_failed"):
            with self.subTest(status=status):
                self.server.snapshot = {
                    "schema_version": 1, "schema": queue.STATE_SCHEMA,
                    "attempts": {"image:older": {"status": status, "workflow": queue.IMAGE_WORKFLOW}}}
                self.server.sha = "a" * 40
                before = deepcopy(self.server.snapshot)
                with self.assertRaisesRegex(VideoForgeError, "UNRESOLVED_EXTERNAL_ATTEMPT"):
                    self.reserve()
                self.assertEqual(self.server.snapshot, before)
        self.assertEqual(self.server.puts, 0)

    def test_completed_and_preflight_legacy_receipts_are_preserved_not_reopened(self):
        old = {"image:old": {"status": "rejected_archived", "workflow": queue.IMAGE_WORKFLOW},
               "image:preflight": {"status": "blocked_preflight", "workflow": queue.IMAGE_WORKFLOW,
                                   "provider_calls_confirmed": 0}}
        self.server.snapshot = {"schema_version": 1, "schema": queue.STATE_SCHEMA,
                                "attempts": deepcopy(old)}
        self.server.sha = "a" * 40
        self.reserve()
        for key, value in old.items():
            self.assertEqual(self.server.snapshot["attempts"][key], value)
        self.assertEqual(len(self.server.snapshot["attempts"]), 3)

    def test_mutated_summary_stale_source_and_policy_fail_before_remote_write(self):
        changed = deepcopy(self.bundle)
        changed["payload"]["n"] = 2
        for bundle in (changed, request.summary(self.bundle)):
            with self.assertRaisesRegex(VideoForgeError, "FINGERPRINT_MISMATCH"):
                self.reserve(bundle)
        unsigned = deepcopy(changed)
        unsigned.pop("request_sha256")
        changed["request_sha256"] = request.fingerprint(unsigned)
        with self.assertRaisesRegex(VideoForgeError, "REQUEST_CHANGED"):
            self.reserve(changed)
        with patch.object(request, "prepare_request", side_effect=VideoForgeError("source changed")):
            with self.assertRaisesRegex(VideoForgeError, "source changed"):
                self.reserve()
        with patch.object(queue, "policy_guard", side_effect=ValueError("policy changed")):
            with self.assertRaisesRegex(ValueError, "policy changed"):
                self.reserve()
        self.assertEqual(self.server.puts, 0)

    def test_same_id_new_fingerprint_cannot_bypass_old_reservation(self):
        self.reserve()
        changed = deepcopy(self.bundle)
        changed["payload"]["prompt"] += " Updated."
        changed.pop("request_sha256")
        changed["request_sha256"] = request.fingerprint(changed)
        with patch.object(request, "prepare_request", return_value=changed):
            with self.assertRaisesRegex(VideoForgeError, "REQUEST_CHANGED"):
                self.reserve(changed)
        self.assertEqual(self.server.puts, 1)

    def test_main_repo_run_identity_required_before_accessing_remote_state(self):
        for field, value in (("GITHUB_REF", "refs/pull/133/merge"),
                             ("GITHUB_REPOSITORY", "someone/other"),
                             ("GITHUB_RUN_ID", ""), ("GITHUB_RUN_ATTEMPT", "0"),
                             ("GITHUB_TOKEN", "")):
            with self.subTest(field=field), patch.dict("os.environ", {field: value}):
                with self.assertRaisesRegex(VideoForgeError, "MAIN_ACTION_REQUIRED"):
                    self.reserve()
        self.assertEqual(self.server.puts, 0)

    def test_corrupt_or_falsely_approved_persisted_reservation_fails_closed(self):
        receipt = self.reserve()
        original = deepcopy(self.server.snapshot)
        key = receipt["reservation_key"]
        changes = {"status": "archived", "request_sha256": "bad",
                   "generation_authorized": True, "rig_ready": True,
                   "reserved_by_run_attempt": 2, "request_id": "another",
                   "workflow": queue.IMAGE_WORKFLOW, "payload": {"token": "unsafe"}}
        for field, value in changes.items():
            with self.subTest(field=field):
                self.server.snapshot = deepcopy(original)
                self.server.snapshot["attempts"][key][field] = value
                with self.assertRaises(GitHubStateError):
                    self.reserve()
        self.assertEqual(self.server.puts, 1)


if __name__ == "__main__":
    unittest.main()
