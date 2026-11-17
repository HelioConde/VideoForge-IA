"""Cenas não podem ser liberadas usando itens planejados/rejeitados."""
import unittest
from videoforge.visual_bible_gate import require_ready
from videoforge.errors import VideoForgeError


class BibleSceneGateTests(unittest.TestCase):
    def test_black_opening_has_no_png_dependency(self):
        result = require_ready("alchemy-lab","mmorpg-conquiste-a-princesa-ep01","C01-P01")
        self.assertTrue(result["ready"])
        self.assertEqual(result["source"], "black_screen_no_image")

    def test_held_40_shots_do_not_generate_automatically(self):
        for shot in ("C01-P04", "C02-P02", "C07-P02", "C11-P01", "C14-P03"):
            with self.subTest(shot=shot):
                with self.assertRaisesRegex(VideoForgeError, "PRODUCTION_HOLD_ACTIVE"):
                    require_ready("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",shot)

    def test_unknown_shot_fails_closed(self):
        with self.assertRaisesRegex(VideoForgeError,"SHOT_NOT_IN_QUEUE"):
            require_ready("alchemy-lab","mmorpg-conquiste-a-princesa-ep01","C99-P99")


if __name__ == "__main__":
    unittest.main()
