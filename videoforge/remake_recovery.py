"""Rearm ONE EP01 V2 reference request after proven OAuth restoration.

Invoked only after the GitHub proxy health workflow has confirmed eligible OAuth
inside the runner. Does not touch secrets, perform model inference, grant
artistic approval or publish YouTube. Commits an idempotent reservation BEFORE
the separate generation workflow is dispatched.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE, _json, discover_archived_character_bible


def reserve_after_verified_proxy(root: Path = ROOT) -> dict:
    episode = Path(root) / EPISODE
    state_path = episode / "estado-atual.json"
    state = _json(state_path)
    policy = _json(episode / "autonomy-policy.json")
    plan = _json(episode / "remake-ep01-planos.json")
    intent = state.get("generation_dispatch_intent")
    result = {"schema": "videoforge/remake-oauth-resume/v1",
              "ready": False, "target": "character-bible",
              "workflow": "production-art-by-request.yml",
              "youtube_upload": False}
    if not isinstance(intent, dict):
        return dict(result, reason="no_existing_dispatch_intent")
    if (intent.get("status") != "blocked_oauth_expired_refresh_http_502"
            or intent.get("target") != "character-bible"
            or intent.get("workflow") != "production-art-by-request.yml"
            or intent.get("max_calls_per_run") != 1
            or intent.get("image_png_created") is not False):
        return dict(result, reason="not_a_recoverable_failed_request")
    if (state.get("active_production_version") != "remake-v2-20261115"
            or state.get("locks", {}).get("no_new_image_generation") is not False
            or state.get("locks", {}).get("no_youtube_upload") is not True
            or state.get("remake_v2", {}).get("generation_editorially_authorized") is not True
            or policy.get("scope") != "alchemy-lab/mmorpg-conquiste-a-princesa-ep01"
            or policy.get("paid_provider_calls_approved") is not True
            or policy.get("auto_dispatch_generation") is not True
            or policy.get("max_chargeable_calls_per_run") != 1
            or policy.get("standing_user_authorization", {}).get("per_call_reapproval_required") is not False
            or policy.get("auto_publish_youtube") is not False
            or plan.get("authorization", {}).get("paid_provider_spend_preapproved") is not True
            or (episode / "SEM-GERACAO-NOVAS-IMAGENS.lock").exists()):
        return dict(result, reason="scope_or_authorization_gate_denied")
    anchors = plan.get("identity_anchors", [])
    if (not isinstance(anchors, list) or not anchors
            or not isinstance(anchors[0], dict)
            or anchors[0].get("id") != "character-bible"
            or anchors[0].get("human_approved") is not False):
        return dict(result, reason="identity_anchor_not_pending")
    if discover_archived_character_bible(episode):
        return dict(result, reason="valid_reference_already_archived")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    intent["status"] = "recovery_dispatch_reserved_after_verified_oauth"
    intent["recovery_dispatch_reserved_utc"] = stamp
    intent["recovery_attempts_reserved"] = 1
    intent["recovery_requires_new_visual_approval"] = True
    intent["image_png_created"] = False
    intent["actual_provider_charge_confirmed"] = False
    intent["next_step"] = "One production-art-by-request.yml dispatch; inspect run, archive and SHA before any other attempt."
    state["autopilot_checkpoint"] = {
        "stage": "generate_character_bible",
        "target": "character-bible",
        "blocker": "recovery_dispatch_reserved_after_verified_oauth",
        "dispatch_allowed": False,
    }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note = ("\n## " + stamp + " — retomada apos OAuth validado no runner\n\n"
            "- Reserva unica de recuperacao persistida ANTES de redisparar o workflow de arte. "
            "Nenhuma imagem, cobranca confirmada, aprovacao humana ou upload ao criar reserva.\n"
            "- Proxy health autenticado e elegibilidade foram exigidos pelo workflow. "
            "Sem resultado de arte ainda; proximo passo: geracao e QA por SHA.\n")
    for name in ("ESTADO-ATUAL.md", "HISTORICO-DESENVOLVIMENTO.md"):
        path = episode / name
        if path.is_symlink() or not path.is_file():
            raise VideoForgeError("REMAKE_OAUTH_RECOVERY_MASTER_CHECKPOINT_MISSING")
        path.write_text(path.read_text(encoding="utf-8") + note, encoding="utf-8")
    return dict(result, ready=True, reason="one_dispatch_reserved",
                request_id=intent.get("request_id"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Reserve one OAuth-recovered remake image request, no provider calls")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = reserve_after_verified_proxy()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("REMAKE_OAUTH_RECOVERY", json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
