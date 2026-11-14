"""Regra nº 1: não iniciar produção oficial sem pipeline real."""
import tempfile
from pathlib import Path
import unittest

from videoforge.official_production import preflight, REQUIRED_STAGES
from videoforge.errors import VideoForgeError


class OfficialProductionTests(unittest.TestCase):
    def test_spy_family_blocks_placeholder_approach(self):
        result = preflight("otaku-br", "spy-x-family-familia-de-mentira", env={})
        self.assertEqual(result["state"], "pipeline_pendente")
        self.assertFalse(result["official_mp4_created"])
        self.assertFalse(result["ready"])
        self.assertEqual(result["scene_count"], 16)
        self.assertIsNone(result["scene_limit"])
        self.assertIn("LAYERED_ANIMATION_MODEL_NOT_OPERATIONAL", result["blockers"])
        self.assertIn("OFFICIAL_RENDERER_HAS_NO_LAYERED_PIPELINE", result["blockers"])
        self.assertIn("OFFICIAL_AGENTS_NOT_INTEGRATED", result["blockers"])
        self.assertIn("SCENE_ART_GENERATOR_NOT_INTEGRATED", result["blockers"])
        self.assertIn("SCENE_ART_AND_RGBA_LAYERS_NOT_GENERATED", result["blockers"])

    def test_provider_present_does_not_falsely_approve_art(self):
        result = preflight("otaku-br", "spy-x-family-familia-de-mentira", env={
            "CODEX_PROXY_API_KEY": "redacted",
            "CODEX_PROXY_BASE_URL": "redacted",
        })
        self.assertTrue(result["checks"]["image_provider_configured"])
        self.assertFalse(result["ready"])
        self.assertEqual(result["requested_mode"], "official_program_only")

    def test_does_not_print_or_record_proxy_secrets(self):
        key = "super-secret-sentinel-value"
        result = preflight("otaku-br", "spy-x-family-familia-de-mentira",
                           env={"CODEX_PROXY_API_KEY": key,
                                "CODEX_PROXY_ACCOUNTS_JSON": "hidden"})
        self.assertNotIn(key, str(result))
        self.assertFalse(result["official_mp4_created"])
        self.assertIn("qa_visual", REQUIRED_STAGES)

    def test_invalid_channel_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"OFFICIAL_CHANNEL_OR_VIDEO_ID_INVALID"):
            preflight("../out", "spy-family")

    def test_unknown_video_is_blocked_not_faked(self):
        result = preflight("otaku-br", "video-inexistente", env={})
        self.assertFalse(result["ready"])
        self.assertIn("STORYBOARD_MISSING", result["blockers"])
        self.assertIn("VIDEO_MANIFEST_MISSING", result["blockers"])


if __name__ == "__main__":
    unittest.main()
