"""Autonomous remake must never invent generated assets or approval."""
import json
from pathlib import Path
import tempfile
import unittest

from videoforge.remake_autopilot import EPISODE, choose_next, sync_checkpoint
from videoforge.image_generation_policy import assert_image_generation_allowed
from videoforge.errors import VideoForgeError


class RemakeAutonomyTests(unittest.TestCase):
    def test_next_action_is_anchor_and_no_paid_calls(self):
        result = choose_next()
        self.assertEqual(result["stage"], "generate_character_bible")
        self.assertEqual(result["blocker"], "provider_cost_permission_required")
        self.assertFalse(result["dispatch_allowed"])
        self.assertFalse(result["approved_human_review"])
        self.assertFalse(result["created_mp4"])

    def test_paid_provider_is_blocked_without_separate_permission(self):
        with self.assertRaisesRegex(VideoForgeError, "IMAGE_GENERATION_DENIED_ALCHEMY_EP01"):
            assert_image_generation_allowed("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")

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
