"""Reserve a versioned reference request in the existing EP01 CAS ledger.

This module never sends images. A reservation is a permanent no-replay fence,
not permission to generate. No CLI or workflow invokes it in production yet.
"""
from __future__ import annotations

import os
import re
from copy import deepcopy

from . import ep01_reference_request as request
from .errors import VideoForgeError

PREFIX = "reference_image:"
WORKFLOW = "ep01-reference-request-transport-disabled"
FIELDS = {
    "status", "workflow", "request_id", "request_sha256", "source_sha256",
    "reference_sha256", "shot_id", "base_component", "versioned_component",
    "reserved_by_run", "reserved_by_run_attempt", "generation_authorized",
    "human_visual_approval", "rig_ready", "youtube_uploaded",
}


def validate_record(key, record):
    """Strict, credential-free reservation schema; no fake completion states."""
    def match(pattern, value):
        return isinstance(value, str) and re.fullmatch(pattern, value) is not None

    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError("Invalid reference reservation fields")
    if (record["status"] != "reserved" or record["workflow"] != WORKFLOW
            or not match(r"C\d\d-P\d\d", record["shot_id"])
            or not match(r"(background-clean|character-[a-z0-9_-]+|object-[a-z0-9_-]+)",
                         record["base_component"])
            or record["versioned_component"] != record["base_component"] + "-" + request.REVISION
            or record["request_id"] != record["shot_id"].lower() + "-" + record["versioned_component"]
            or key != PREFIX + record["request_id"]
            or any(not match(r"[0-9a-f]{64}", record[name])
                   for name in ("request_sha256", "source_sha256", "reference_sha256"))
            or any(not match(r"[1-9][0-9]*", record[name])
                   for name in ("reserved_by_run", "reserved_by_run_attempt"))
            or any(record[name] is not False for name in (
                "generation_authorized", "human_visual_approval", "rig_ready", "youtube_uploaded"))):
        raise ValueError("Invalid reference reservation contract")


def reserve_request(bundle, expected_request_sha256, root=request.parts.ROOT):
    """Return a receipt only after the shared remote CAS write succeeds.

    Restart, conflict or ambiguous save failure never grants a retry. The
    ordinary queue sees the same reserved row and stops before paid dispatch.
    Future transport must use that queue's concurrency group and reconcile the
    persisted attempt; it must not treat this receipt as generation approval.
    """
    from scripts import ep01_action_production_queue as queue

    run_id = os.getenv("GITHUB_RUN_ID", "")
    run_attempt = os.getenv("GITHUB_RUN_ATTEMPT", "")
    if (os.getenv("GITHUB_REPOSITORY") != "HelioConde/VideoForge-IA"
            or os.getenv("GITHUB_REF") != "refs/heads/main"
            or not os.getenv("GITHUB_TOKEN")
            or not re.fullmatch(r"[1-9][0-9]*", run_id)
            or not re.fullmatch(r"[1-9][0-9]*", run_attempt)):
        raise VideoForgeError("EP01_REFERENCE_RESERVATION_MAIN_ACTION_REQUIRED")
    unsigned = dict(bundle)
    claimed = unsigned.pop("request_sha256", None)
    if (not isinstance(expected_request_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_request_sha256)
            or claimed != expected_request_sha256
            or request.fingerprint(unsigned) != expected_request_sha256):
        raise VideoForgeError("EP01_REFERENCE_REQUEST_FINGERPRINT_MISMATCH")
    # Rebuild from CURRENT policy, archives, source bytes, prompt and Bible.
    # A self-consistent but stale/modified payload must not consume a reservation.
    current = request.prepare_request(bundle["shot_id"], bundle["base_component"],
                                      bundle["source_sha256"], root)
    if current["request_sha256"] != expected_request_sha256:
        raise VideoForgeError("EP01_REFERENCE_RESERVATION_REQUEST_CHANGED")
    queue.policy_guard(root)
    row = {
        "status": "reserved", "workflow": WORKFLOW,
        **{name: deepcopy(current[name]) for name in (
            "request_id", "request_sha256", "source_sha256", "shot_id",
            "base_component", "versioned_component")},
        "reference_sha256": current["reference_manifest"]["reference_sha256"],
        "reserved_by_run": run_id, "reserved_by_run_attempt": run_attempt,
        "generation_authorized": False, "human_visual_approval": False,
        "rig_ready": False, "youtube_uploaded": False,
    }
    key = PREFIX + row["request_id"]
    validate_record(key, row)
    remote = queue.QueueRemote(path=queue.STATE_PATH,
                               branch="state/multi-agent-runtime", initialize=True)
    ledger = remote.load()
    if ledger is None:
        ledger = {"schema_version": 1, "schema": queue.STATE_SCHEMA, "attempts": {}}
    queue.QueueRemote._validate_snapshot(ledger)
    attempts = ledger["attempts"]
    if key in attempts:
        reason = ("REQUEST_CHANGED" if attempts[key]["request_sha256"] != expected_request_sha256
                  else "ALREADY_RESERVED_NO_REPLAY")
        raise VideoForgeError("EP01_REFERENCE_RESERVATION_" + reason)
    if any(item["status"] in {"reserved", "dispatched", "blocked_uncertain", "blocked_failed"}
           for item in attempts.values()):
        raise VideoForgeError("EP01_REFERENCE_RESERVATION_UNRESOLVED_EXTERNAL_ATTEMPT")
    attempts[key] = row
    # No retry on conflict, timeout or a missing acknowledgement. If the server
    # accepted a write before losing the response, the next load sees the fence.
    saved_sha = remote.save(ledger)
    if not isinstance(saved_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", saved_sha):
        raise VideoForgeError("EP01_REFERENCE_RESERVATION_UNCONFIRMED_SAVE_NO_REPLAY")
    return {
        "reservation_key": key, "ledger_blob_sha": saved_sha,
        "request_sha256": expected_request_sha256,
        "reserved_by_run": run_id, "reserved_by_run_attempt": run_attempt,
        "generation_authorized": False, "provider_calls": 0,
        "human_visual_approval": False, "rig_ready": False, "youtube_uploaded": False,
    }
