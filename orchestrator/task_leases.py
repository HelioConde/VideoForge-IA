#!/usr/bin/env python3
"""Pure, deterministic task leases/checkpoints for agent workers (no worker execution)."""
import hashlib
import json

def lease_key(task_id, owner, input_shas, attempt=0, claimed_at=0):
    if not task_id or not owner or not isinstance(input_shas, dict):
        raise ValueError("Invalid lease request")
    raw = json.dumps({"task_id": task_id, "owner": owner, "input_shas": input_shas, "attempt": attempt, "claimed_at": claimed_at},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

def claim(task, worker, now, ttl_seconds=900):
    """Return updated copy. Caller must persist atomically (e.g. GitHub concurrency)."""
    if not isinstance(now, int) or now < 0 or not 60 <= ttl_seconds <= 3600:
        raise ValueError("Invalid lease timing")
    if task.get("status") not in {"ready", "running"}:
        raise ValueError("Task not claimable")
    if task.get("blocked_by"):
        raise ValueError("Task dependencies unresolved")
    if worker != task.get("owner"):
        raise ValueError("Worker does not own task")
    new = dict(task)
    old = new.get("lease")
    if old and old["expires_at"] > now and old["worker"] != worker:
        raise ValueError("Lease held by another worker")
    if old and old["expires_at"] > now and old["worker"] == worker:
        return new
    if new["status"] == "running":
        raise ValueError("Recover expired lease before claiming again")
    attempts = int(new.get("attempts", 0))
    if attempts >= 3:
        raise ValueError("Retry budget exhausted")
    new["attempts"] = attempts + 1
    new["status"] = "running"
    new["lease"] = {"worker": worker, "claimed_at": now,
                    "expires_at": now + ttl_seconds,
                    "lease_key": lease_key(task["task_id"], worker, task.get("input_shas", {}), attempts + 1, now)}
    return new

def recover(task, now):
    if not isinstance(now, int) or now < 0:
        raise ValueError("Invalid timestamp")
    new = dict(task)
    lease = new.get("lease")
    if new.get("status") != "running" or not lease or lease["expires_at"] > now:
        return new
    new["status"] = "failed" if new.get("attempts", 0) >= 3 else "ready"
    new["lease"] = None
    return new

def checkpoint(task, worker, lease_key_value, evidence, now=None):
    if task.get("status") != "running":
        raise ValueError("Task is not running")
    lease = task.get("lease") or {}
    if lease.get("worker") != worker or lease.get("lease_key") != lease_key_value:
        raise ValueError("Lease mismatch")
    if now is not None and (not isinstance(now, int) or now < lease.get("claimed_at", 0) or now >= lease.get("expires_at", 0)):
        raise ValueError("Lease expired or invalid checkpoint timestamp")
    if not isinstance(evidence, dict) or not evidence.get("artifact_sha256"):
        raise ValueError("Missing verifiable artifact SHA")
    new = dict(task)
    new["status"] = "needs_review"
    new["lease"] = None
    new["checkpoint"] = {"worker": worker, "evidence": evidence, "approval": False}
    return new
