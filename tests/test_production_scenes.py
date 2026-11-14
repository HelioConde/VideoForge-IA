"""Scenarios for reference-anchored artwork requests without contacting IA."""
import unittest

from videoforge.production_scenes import scene_prompt
from videoforge.errors import VideoForgeError


class ProductionScenesTests(unittest.TestCase):
    def test_all_16_scenes_use_the_same_character_bible(self):
        for number in range(1,17):
            prompt,scene=scene_prompt("otaku-br","spy-x-family-familia-de-mentira",number)
            self.assertLess(len(prompt),5001)
            self.assertIn("Anya",prompt)
            self.assertIn("Loid",prompt)
            self.assertIn("Yor",prompt)
            self.assertIn(scene["visual_direction"],prompt)
            self.assertEqual(scene["number"],number)

    def test_scene_id_out_of_range_is_refused(self):
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_SCENE_NUMBER_INVALID"):
            scene_prompt("otaku-br","spy-x-family-familia-de-mentira",0)
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_SCENE_NUMBER_INVALID"):
            scene_prompt("otaku-br","spy-x-family-familia-de-mentira",17)

    def test_other_channel_does_not_get_spy_bible(self):
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_PLAN_MISSING"):
            scene_prompt("gamer","spy-x-family-familia-de-mentira",1)


if __name__=="__main__":
    unittest.main()
