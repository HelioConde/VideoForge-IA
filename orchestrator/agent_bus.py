"""Safe local message bus for all 12 roles. No API, network, AI or production mutations."""
import hashlib
import json
from pathlib import Path

ROLES = {
    "01": "diretor-geral", "02": "roteirista", "03": "diretor-cenas",
    "04": "diretor-arte", "05": "gerador-visual", "06": "separador-camadas",
    "07": "especialista-rig", "08": "animador", "09": "diretor-camera",
    "10": "especialista-audio", "11": "montador", "12": "supervisor-qa",
}
STATES = {"pending", "ready", "running", "blocked", "needs_review", "approved", "rejected", "failed"}
TRANSITIONS = {
    "pending": {"ready", "blocked"},
    "ready": {"running", "blocked"},
    "running": {"needs_review", "blocked", "failed"},
    "needs_review": {"approved", "rejected", "blocked"},
    "rejected": {"ready", "blocked"},
    "blocked": {"ready"},
    "failed": {"ready"},
    "approved": set(),
}

def fingerprint(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()

def make_message(task_id, sender, recipient, kind, body, sequence):
    if sender not in ROLES or recipient not in ROLES or not task_id or not kind or not body:
        raise ValueError("Invalid agent message")
    if not isinstance(sequence, int) or sequence < 1:
        raise ValueError("Invalid message sequence")
    payload = {"schema_version": 1, "task_id": task_id, "sequence": sequence,
               "from": sender, "to": recipient, "kind": kind, "body": body,
               "simulation": True}
    payload["event_id"] = fingerprint(payload)[:24]
    return payload

def append_message(state, message):
    if message["from"] not in ROLES or message["to"] not in ROLES:
        raise ValueError("Unknown role")
    events = state.setdefault("events", [])
    if any(e["event_id"] == message["event_id"] for e in events):
        return False
    if events and message["sequence"] != events[-1]["sequence"] + 1:
        raise ValueError("Out-of-order message")
    if not events and message["sequence"] != 1:
        raise ValueError("First sequence must be 1")
    events.append(message)
    return True

def transition(task, new_status, actor):
    old = task.get("status")
    if old not in STATES or new_status not in TRANSITIONS[old]:
        raise ValueError("Illegal state transition")
    if actor not in ROLES:
        raise ValueError("Unknown actor")
    actor_role = ROLES[actor]
    if old == "needs_review" and new_status in {"approved", "rejected"} and actor_role == task.get("owner"):
        raise ValueError("Owner cannot self-review")
    if old == "needs_review" and new_status in {"approved", "rejected"} and task.get("reviewer") and actor_role != task["reviewer"]:
        raise ValueError("Only assigned reviewer can decide")
    if new_status == "approved" and task.get("requires_human_approval", False):
        raise ValueError("Human approval cannot be automated")
    if new_status == "running" and task.get("blocked_by"):
        raise ValueError("Unresolved dependencies")
    task["status"] = new_status
    return task

def load_queue(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])
    for task in tasks:
        if task.get("owner") not in ROLES.values() or task.get("status") not in STATES:
            raise ValueError("Invalid task owner or state")
    return data

def safe_checkpoint(events):
    return {"schema_version": 1, "mode": "simulation", "agent_count": len(ROLES),
            "event_count": len(events), "events_sha256": fingerprint(events),
            "ai_calls": 0, "proxy_calls": 0, "youtube_publications": 0,
            "ep01_approved": False}
