import base64
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from github_state import GitHubState, GitHubStateError, StateConflict, _NoRedirect

SNAPSHOT = {"schema_version": 1, "tables": {
    "tasks": [], "attempts": [], "events": [], "results": [],
    "checkpoints": [], "usage": [], "meta": [],
}}


class FakeGitHubState(GitHubState):
    def __init__(self, responses, **kwargs):
        super().__init__(repo="owner/repo", token="test-secret", **kwargs)
        self.responses = list(responses)
        self.calls = []

    def _request(self, method, url, payload=None):
        self.calls.append((method, url, payload))
        status, body = self.responses.pop(0)
        return status, body


class GitHubStateTests(unittest.TestCase):
    def test_refuses_arbitrary_host_or_repository_before_auth_request(self):
        client = FakeGitHubState([])
        client._validate_url("https://api.github.com/repos/owner/repo")
        for url in (
            "https://attacker.example/repos/owner/repo/contents/runtime/state.json",
            "http://api.github.com/repos/owner/repo/contents/runtime/state.json",
            "https://api.github.com/repos/other/repo/contents/runtime/state.json",
            "https://user@api.github.com/repos/owner/repo/contents/runtime/state.json",
        ):
            with self.subTest(url=url), self.assertRaises(GitHubStateError):
                client._validate_url(url)

    def test_redirect_handler_never_follows_redirects(self):
        handler = _NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "Found", {}, "https://attacker.example/"))

    def test_response_size_is_bounded(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def read(self, amount): return b"x" * amount
        class Opener:
            def open(self, *_args, **_kwargs): return Response()
        client = GitHubState(repo="owner/repo", token="test-secret")
        client.MAX_RESPONSE_BYTES = 32
        with patch("github_state.urllib.request.build_opener", return_value=Opener()):
            with self.assertRaisesRegex(GitHubStateError, "size limit"):
                client._request("GET", client._contents_url("main"))

    def test_load_then_save_uses_blob_sha_compare_and_swap(self):
        encoded = base64.b64encode(json.dumps(SNAPSHOT).encode()).decode()
        client = FakeGitHubState([
            (200, {"content": encoded, "sha": "blob-v1"}),
            (200, {"object": {"sha": "branch-head"}}),
            (200, {"content": {"sha": "blob-v2"}}),
        ])
        self.assertEqual(client.load(), SNAPSHOT)
        updated = {**SNAPSHOT, "tables": {**SNAPSHOT["tables"], "meta": [{"revision": 2}]}}
        self.assertEqual(client.save(updated), "blob-v2")
        put = client.calls[-1][2]
        self.assertEqual(put["sha"], "blob-v1")
        self.assertEqual(put["branch"], "state/multi-agent-runtime")
        self.assertNotIn("test-secret", json.dumps(put))
        self.assertNotIn("test-secret", " ".join(call[1] for call in client.calls))

    def test_conflicting_write_fails_without_retry(self):
        encoded = base64.b64encode(json.dumps(SNAPSHOT).encode()).decode()
        client = FakeGitHubState([
            (200, {"content": encoded, "sha": "old"}),
            (200, {"object": {"sha": "branch-head"}}),
            (409, {"message": "conflict"}),
        ])
        client.load()
        with self.assertRaises(StateConflict):
            client.save(SNAPSHOT)
        self.assertEqual(len(client.calls), 3)

    def test_missing_state_cannot_silently_reset(self):
        client = FakeGitHubState([(404, {})], initialize=False)
        with self.assertRaises(GitHubStateError):
            client.load()

    def test_explicit_initialization_creates_branch_and_initial_file(self):
        client = FakeGitHubState([
            (404, {}),                 # state file absent on target branch
            (404, {}),                 # target branch absent
            (200, {"default_branch": "main"}),
            (200, {"object": {"sha": "main-head"}}),
            (201, {}),                 # create target branch
            (200, {}),                 # verify branch exists
            (201, {"content": {"sha": "initial-blob"}}),
        ], initialize=True)
        self.assertIsNone(client.load())
        self.assertEqual(client.save(SNAPSHOT), "initial-blob")
        self.assertEqual([c[0] for c in client.calls].count("POST"), 1)
        self.assertNotIn("sha", client.calls[-1][2])

    def test_rejects_incomplete_snapshot_before_network_write(self):
        client = FakeGitHubState([], initialize=True)
        with self.assertRaises(ValueError):
            client.save({"schema_version": 1, "tables": {"tasks": []}})
        self.assertEqual(client.calls, [])

    def test_encoded_snapshot_upload_size_is_bounded(self):
        client = FakeGitHubState([(200, {"object": {"sha": "branch-head"}})])
        client._loaded = True
        client._blob_sha = "current-blob"
        client.MAX_ENCODED_STATE_BYTES = 10
        with self.assertRaisesRegex(GitHubStateError, "upload size limit"):
            client.save(SNAPSHOT)
        self.assertEqual(len(client.calls), 1)  # branch lookup only; no Contents PUT

    def test_rejects_extra_or_malformed_snapshot_tables(self):
        client = FakeGitHubState([])
        extra = {**SNAPSHOT, "tables": {**SNAPSHOT["tables"], "unknown": []}}
        malformed = {**SNAPSHOT, "tables": {**SNAPSHOT["tables"], "tasks": ["not-a-row"]}}
        for snapshot in (extra, malformed):
            with self.subTest(snapshot=snapshot), self.assertRaises(ValueError):
                client._validate_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
