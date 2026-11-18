"""GitHub Contents API snapshot store with blob-SHA compare-and-swap.

GitHub is only a remote CAS transport here; task snapshots remain canonical JSON.
Never logs or serializes the supplied token.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import re
from typing import Any


class GitHubStateError(RuntimeError):
    """Remote state operation failed safely."""


class StateConflict(GitHubStateError):
    """The remote file changed since the snapshot was loaded."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Prevent bearer credentials from following redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHubState:
    API = "https://api.github.com"
    API_HOST = "api.github.com"
    MAX_RESPONSE_BYTES = 8_000_000
    MAX_ERROR_BYTES = 64_000
    MAX_ENCODED_STATE_BYTES = 800_000

    def __init__(self, repo: str | None = None, branch: str = "state/multi-agent-runtime",
                 path: str = "runtime/state.json", token: str | None = None,
                 initialize: bool = False, timeout: int = 20):
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY", "")
        self.branch = branch
        self.path = path.strip("/")
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")
        self.initialize = initialize
        self.timeout = timeout
        self._blob_sha: str | None = None
        self._loaded = False
        repo_parts = self.repo.split("/")
        if len(repo_parts) != 2 or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", p) or p in {".", ".."} for p in repo_parts):
            raise ValueError("repo must be an owner/name repository")
        if not self.token:
            raise ValueError("GitHub token is required")
        if (not self.branch or any(p in {"", ".", ".."} for p in self.branch.split("/"))
                or not self.path or any(p in {"", ".", ".."} for p in self.path.split("/"))):
            raise ValueError("branch and relative state path are required")
        if not isinstance(self.timeout, int) or not 1 <= self.timeout <= 120:
            raise ValueError("timeout must be between 1 and 120 seconds")

    def _request(self, method: str, url: str, payload: dict[str, Any] | None = None):
        self._validate_url(url)
        if method not in {"GET", "POST", "PUT"}:
            raise GitHubStateError("Unsupported GitHub API method")
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, method=method, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self.token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "VideoForge-agent-runtime",
            **({"Content-Type": "application/json"} if body is not None else {}),
        })
        try:
            opener = urllib.request.build_opener(_NoRedirect())
            with opener.open(req, timeout=self.timeout) as response:
                raw = response.read(self.MAX_RESPONSE_BYTES + 1)
                if len(raw) > self.MAX_RESPONSE_BYTES:
                    raise GitHubStateError("GitHub response exceeded the size limit")
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            if 300 <= exc.code < 400:
                raise GitHubStateError("Unexpected GitHub API redirect; request refused") from None
            raw = exc.read(self.MAX_ERROR_BYTES + 1)
            if len(raw) > self.MAX_ERROR_BYTES:
                raw = b""
            try:
                data = json.loads(raw) if raw else {}
            except (ValueError, UnicodeDecodeError):
                data = {}
            return exc.code, data
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise GitHubStateError(f"GitHub request failed ({type(exc).__name__})") from None

    def _validate_url(self, url: str) -> None:
        try:
            parsed = urllib.parse.urlsplit(url)
            port = parsed.port
        except ValueError:
            raise GitHubStateError("Invalid GitHub API URL") from None
        owner, name = self.repo.split("/")
        repo_root = f"/repos/{urllib.parse.quote(owner, safe='')}/{urllib.parse.quote(name, safe='')}"
        if (parsed.scheme != "https" or parsed.hostname != self.API_HOST
                or port not in (None, 443) or parsed.username or parsed.password
                or parsed.fragment or not (parsed.path == repo_root or parsed.path.startswith(repo_root + "/"))):
            raise GitHubStateError("Refused request outside the fixed GitHub repository API")

    @property
    def _encoded_path(self) -> str:
        return "/".join(urllib.parse.quote(part, safe="") for part in self.path.split("/"))

    def _contents_url(self, ref: str | None = None) -> str:
        url = f"{self.API}/repos/{self.repo}/contents/{self._encoded_path}"
        return url + ("?ref=" + urllib.parse.quote(ref, safe="") if ref else "")

    def _ensure_branch(self) -> None:
        code, ref = self._request("GET", f"{self.API}/repos/{self.repo}/git/ref/heads/{urllib.parse.quote(self.branch, safe='/')}")
        if code == 200:
            return
        if code != 404:
            raise GitHubStateError(f"Cannot inspect state branch (HTTP {code})")
        if not self.initialize:
            raise GitHubStateError("State branch is absent; explicit initialization is required")
        code, repo = self._request("GET", f"{self.API}/repos/{self.repo}")
        if code != 200 or not repo.get("default_branch"):
            raise GitHubStateError(f"Cannot resolve repository default branch (HTTP {code})")
        default = urllib.parse.quote(repo["default_branch"], safe="")
        code, head = self._request("GET", f"{self.API}/repos/{self.repo}/git/ref/heads/{default}")
        sha = head.get("object", {}).get("sha") if code == 200 else None
        if not sha:
            raise GitHubStateError(f"Cannot resolve default branch head (HTTP {code})")
        code, _ = self._request("POST", f"{self.API}/repos/{self.repo}/git/refs",
                                {"ref": "refs/heads/" + self.branch, "sha": sha})
        if code in (201, 422):  # 422 can mean a concurrent initializer won.
            verify, _ = self._request("GET", f"{self.API}/repos/{self.repo}/git/ref/heads/{urllib.parse.quote(self.branch, safe='/')}")
            if verify == 200:
                return
        raise GitHubStateError(f"Cannot initialize state branch (HTTP {code})")

    @staticmethod
    def _validate_snapshot(snapshot: dict[str, Any]) -> None:
        if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
            raise ValueError("Unsupported snapshot schema")
        tables = snapshot.get("tables")
        required = {"tasks", "attempts", "events", "results", "checkpoints", "usage", "meta"}
        if not isinstance(tables, dict) or set(tables) != required:
            raise ValueError("Snapshot must contain all runtime tables")
        if any(not isinstance(tables[name], list) or any(not isinstance(row, dict) for row in tables[name])
               for name in required):
            raise ValueError("Snapshot tables must be arrays of row objects")

    def load(self) -> dict[str, Any] | None:
        code, data = self._request("GET", self._contents_url(self.branch))
        if code == 404:
            if not self.initialize:
                raise GitHubStateError("State snapshot is absent; explicit initialization is required")
            self._loaded = True
            self._blob_sha = None
            return None
        if code != 200:
            raise GitHubStateError(f"Cannot load state snapshot (HTTP {code})")
        try:
            encoded = "".join(str(data["content"]).split())
            content = base64.b64decode(encoded, validate=True)
            snapshot = json.loads(content.decode("utf-8"))
            self._validate_snapshot(snapshot)
        except (KeyError, ValueError, UnicodeDecodeError, TypeError, binascii.Error) as exc:
            raise GitHubStateError(f"Remote state snapshot is invalid ({type(exc).__name__})") from None
        if not data.get("sha"):
            raise GitHubStateError("Remote state has no blob SHA")
        self._blob_sha = data["sha"]
        self._loaded = True
        return snapshot

    def save(self, snapshot: dict[str, Any], expected_sha: str | None = None) -> str:
        self._validate_snapshot(snapshot)
        if not self._loaded and expected_sha is None:
            raise GitHubStateError("Load state before saving, or explicitly initialize it")
        self._ensure_branch()
        current_sha = self._blob_sha if expected_sha is None else expected_sha
        if current_sha is None and not self.initialize:
            raise GitHubStateError("Missing state file; explicit initialization is required")
        content = (json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        encoded = base64.b64encode(content).decode("ascii")
        if len(encoded.encode("ascii")) > self.MAX_ENCODED_STATE_BYTES:
            raise GitHubStateError("Encoded state snapshot exceeded the upload size limit")
        payload: dict[str, Any] = {
            "message": "runtime: persist multi-agent state snapshot",
            "content": encoded,
            "branch": self.branch,
        }
        if current_sha is not None:
            payload["sha"] = current_sha
        code, data = self._request("PUT", self._contents_url(), payload)
        if code in (409, 422):
            raise StateConflict("Remote state revision changed; reload and reconcile before continuing")
        if code not in (200, 201):
            raise GitHubStateError(f"Cannot save state snapshot (HTTP {code})")
        new_sha = data.get("content", {}).get("sha")
        if not new_sha:
            raise GitHubStateError("GitHub did not return the saved blob SHA")
        self._blob_sha = new_sha
        self._loaded = True
        self.initialize = False
        return new_sha
