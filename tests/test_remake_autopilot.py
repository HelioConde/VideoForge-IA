"""Autonomous remake must never invent generated assets or approval."""
import json
import shutil
from pathlib import Path
import tempfile
import unittest

from videoforge.remake_autopilot import EPISODE, choose_next, sync_checkpoint, reserve_generation_dispatch
from videoforge.image_generation_policy import assert_image_generation_allowed
from videoforge.errors import VideoForgeError


class RemakeAutonomyTests(unittest.TestCase):
    def test_next_action_is_anchor_and_no_paid_calls(self):
        result = choose_next()
        self.assertEqual(result["stage"], "generate_character_bible")
        self.assertEqual(result["blocker"], "no_verified_reference_png")
        self.assertTrue(result["dispatch_allowed"])
        self.assertEqual(result["next_workflow"], "production-art-by-request.yml")
        self.assertFalse(result["approved_human_review"])
        self.assertFalse(result["created_mp4"])

    def test_owner_standing_authorization_replaces_per_call_permission(self):
        self.assertIsNone(assert_image_generation_allowed(
            "alchemy-lab", "mmorpg-conquiste-a-princesa-ep01"))

    def test_auto_reservation_is_durable_and_prevents_double_spend(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            ep=root/EPISODE
            ep.mkdir(parents=True)
            source=Path(__file__).resolve().parents[1]/EPISODE
            for name in ("remake-ep01-planos.json","estado-atual.json",
                         "autonomy-policy.json","production-art.json","roteiro.json"):
                shutil.copyfile(source/name,ep/name)
            first=choose_next(root)
            self.assertTrue(first["dispatch_allowed"])
            reservation=reserve_generation_dispatch(first,root)
            self.assertTrue(reservation["ready"])
            self.assertEqual(reservation["max_calls_per_run"],1)
            self.assertFalse(reservation["youtube_upload"])
            again=choose_next(root)
            self.assertFalse(again["dispatch_allowed"])
            self.assertEqual(again["blocker"],
                "generation_dispatch_already_reserved_wait_for_artifact_or_investigation")
            duplicate=reserve_generation_dispatch(first,root)
            self.assertFalse(duplicate["ready"])
            self.assertEqual(duplicate["reason"],"already_reserved")
            state=json.loads((ep/"estado-atual.json").read_text(encoding="utf-8"))
            self.assertEqual(state["generation_dispatch_intent"]["request_id"],
                             reservation["request_id"])
            self.assertFalse(state["generation_dispatch_intent"]["human_visual_approved"])

    def test_unrelated_channels_unchanged(self):
        self.assertIsNone(assert_image_generation_allowed("otaku-multicena", "outro-video"))

    def test_legacy_lock_wins_if_reintroduced(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / EPISODE
            base.mkdir(parents=True)
            (base / "SEM-GERACAO-NOVAS-IMAGENS.lock").write_text("lock", encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError, "legacy lock"):
                assert_image_generation_allowed("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", Path(tmp))


    def test_archive_discovery_no_false_positive_without_real_manifest(self):
        from videoforge.remake_autopilot import discover_archived_character_bible
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / EPISODE
            bogus = base / "assets/geracoes/production-art-request/123"
            bogus.mkdir(parents=True)
            (bogus / "character-bible.png").write_bytes(b"not a real png")
            self.assertIsNone(discover_archived_character_bible(base))

    def test_checkpoint_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / EPISODE
            base.mkdir(parents=True)
            (base / "estado-atual.json").write_text("{}", encoding="utf-8")
            (base / "ESTADO-ATUAL.md").write_text("# Teste\n", encoding="utf-8")
            (base / "HISTORICO-DESENVOLVIMENTO.md").write_text("# Histórico\n", encoding="utf-8")
            report = choose_next()
            self.assertTrue(sync_checkpoint(report, Path(tmp)))
            previous = (base / "HISTORICO-DESENVOLVIMENTO.md").read_text(encoding="utf-8")
            self.assertFalse(sync_checkpoint(report, Path(tmp)))
            self.assertEqual(previous, (base / "HISTORICO-DESENVOLVIMENTO.md").read_text(encoding="utf-8"))
            state = json.loads((base / "estado-atual.json").read_text(encoding="utf-8"))
            self.assertEqual(state["autopilot_checkpoint"]["stage"], "generate_character_bible")


if __name__ == "__main__":
    unittest.main()
