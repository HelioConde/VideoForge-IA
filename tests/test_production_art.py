"""Comprovar que a arte e especifica do canal e nao cria falso MP4."""
import unittest

from videoforge.production_art import read_plan, asset_prompt, inspect_generated_dimensions
from videoforge.errors import VideoForgeError


class ProductionArtTests(unittest.TestCase):
    def test_art_bible_exists_for_spy_x_family(self):
        plan,story=read_plan("otaku-br","spy-x-family-familia-de-mentira")
        self.assertEqual(len(story["scenes"]),16)
        prompt,size=asset_prompt(plan,story,"character-bible")
        self.assertEqual(size,"1024x1536")
        for character in ("Loid","Anya","Yor"):
            self.assertIn(character,prompt)
        self.assertLessEqual(len(prompt),5000)

    def test_exact_dimensions_do_not_need_resampling(self):
        report=inspect_generated_dimensions({"width":1024,"height":1536},"1024x1536")
        self.assertEqual(report["technical_qa"],"valid_png_dimensions")
        self.assertTrue(report["dimensions_match_requested"])
        self.assertFalse(report["pixel_resampling"])

    def test_noncanonical_real_image_preserved_for_review(self):
        report=inspect_generated_dimensions({"width":1199,"height":1312},"1024x1536")
        self.assertEqual(report["actual_width"],1199)
        self.assertEqual(report["actual_height"],1312)
        self.assertFalse(report["dimensions_match_requested"])
        self.assertIn("visual_review_pending",report["technical_qa"])
        self.assertFalse(report["pixel_resampling"])

    def test_invalid_dimensions_still_rejected(self):
        for dimensions in ((0,1000),(100,1000),(5000,1500),(True,1536)):
            with self.subTest(dimensions=dimensions),self.assertRaisesRegex(
                    VideoForgeError,"PRODUCTION_ART_DIMENSIONS_INVALID"):
                inspect_generated_dimensions({"width":dimensions[0],
                                              "height":dimensions[1]},"1024x1536")

    def test_wrong_channel_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_PLAN_MISSING"):
            read_plan("gamer","spy-x-family-familia-de-mentira")

    def test_unknown_asset_rejected_before_proxy_call(self):
        plan,story=read_plan("otaku-br","spy-x-family-familia-de-mentira")
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_UNKNOWN_ASSET"):
            asset_prompt(plan,story,"cena-falsa")

if __name__=="__main__":
    unittest.main()
