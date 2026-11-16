"""Offline gates for safe one-shot OAuth recovery; no inference/network."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from videoforge.remake_autopilot import EPISODE
from videoforge.remake_recovery import reserve_after_verified_proxy

ROOT = Path(__file__).resolve().parents[1]

class RecoveryTests(unittest.TestCase):
    def fixture(self, folder: str) -> Path:
        root=Path(folder)
        episode=root/EPISODE
        episode.mkdir(parents=True)
        original=ROOT/EPISODE
        for name in ("estado-atual.json","autonomy-policy.json",
                     "remake-ep01-planos.json","ESTADO-ATUAL.md",
                     "HISTORICO-DESENVOLVIMENTO.md"):
            shutil.copyfile(original/name,episode/name)
        state_path=episode/"estado-atual.json"
        state=json.loads(state_path.read_text(encoding="utf-8"))
        state["generation_dispatch_intent"]["status"]="blocked_oauth_expired_refresh_http_502"
        state_path.write_text(json.dumps(state),encoding="utf-8")
        return root

    def test_one_valid_resume_then_never_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=self.fixture(tmp)
            first=reserve_after_verified_proxy(root)
            self.assertTrue(first["ready"])
            self.assertFalse(first["youtube_upload"])
            self.assertEqual(first["workflow"],"production-art-by-request.yml")
            second=reserve_after_verified_proxy(root)
            self.assertFalse(second["ready"])
            self.assertEqual(second["reason"],"not_a_recoverable_failed_request")
            state=json.loads((root/EPISODE/"estado-atual.json").read_text(encoding="utf-8"))
            self.assertEqual(state["generation_dispatch_intent"]["recovery_attempts_reserved"],1)
            self.assertFalse(state["generation_dispatch_intent"]["human_visual_approved"])

    def test_prevent_resume_if_artifact_exists_or_paid_permission_revoked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=self.fixture(tmp)
            with patch("videoforge.remake_recovery.discover_archived_character_bible",
                       return_value={"path":"assets/test.png","sha256":"a"*64}):
                self.assertEqual(reserve_after_verified_proxy(root)["reason"],
                                 "valid_reference_already_archived")
            policy_path=root/EPISODE/"autonomy-policy.json"
            p=json.loads(policy_path.read_text(encoding="utf-8"))
            p["paid_provider_calls_approved"]=False
            policy_path.write_text(json.dumps(p),encoding="utf-8")
            self.assertEqual(reserve_after_verified_proxy(root)["reason"],
                             "scope_or_authorization_gate_denied")

    def test_non_failed_or_already_generated_must_not_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=self.fixture(tmp)
            state_path=root/EPISODE/"estado-atual.json"
            state=json.loads(state_path.read_text(encoding="utf-8"))
            for patch_status in ({"status":"recovery_dispatch_reserved_after_verified_oauth"},
                                 {"image_png_created":True}):
                new=json.loads(state_path.read_text(encoding="utf-8"))
                new["generation_dispatch_intent"].update(patch_status)
                state_path.write_text(json.dumps(new),encoding="utf-8")
                self.assertFalse(reserve_after_verified_proxy(root)["ready"])
                state_path.write_text(json.dumps(state),encoding="utf-8")

if __name__=="__main__":
    unittest.main()
