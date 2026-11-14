"""Checks rápidos do piloto Spy x Family sem gerar mídia."""
import unittest
from pathlib import Path

from videoforge import spy_family_pilot as pilot


class SpyFamilyPilotTests(unittest.TestCase):
    def test_storyboard_is_10_scenes_and_channel_safe(self):
        story = pilot.load_storyboard()
        self.assertEqual(story["channel"], "otaku-br")
        self.assertEqual(len(story["scenes"]), 10)
        self.assertFalse(story["youtube_upload"])
        self.assertEqual(story["source"]["item_id"], "5027-spy-x-family")

    def test_narration_has_meaningful_ptbr_story_not_a_stub(self):
        data = pilot.load_storyboard()
        text = " ".join(x["narration"] for x in data["scenes"]).lower()
        for marker in ("loid", "yor", "anya", "família", "segredo"):
            self.assertIn(marker, text)
        self.assertGreaterEqual(len(text.split()), 180)
        self.assertLessEqual(len(text.split()), 290)

    def test_assets_are_channel_local_and_nonexisting_in_git(self):
        data = pilot.load_storyboard()
        for scene in data["scenes"]:
            for key, stem in (("image", "imagens/"), ("audio", "voz/")):
                self.assertTrue(scene[key].startswith(stem))
                self.assertNotIn("..", Path(scene[key]).parts)
                self.assertFalse((pilot.FOLDER / scene[key]).is_file())


if __name__ == "__main__":
    unittest.main()
