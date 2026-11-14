"""Comprovar que a arte e especifica do canal e nao cria falso MP4."""
import unittest

from videoforge.production_art import read_plan, asset_prompt
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

    def test_wrong_channel_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_PLAN_MISSING"):
            read_plan("gamer","spy-x-family-familia-de-mentira")

    def test_unknown_asset_rejected_before_proxy_call(self):
        plan,story=read_plan("otaku-br","spy-x-family-familia-de-mentira")
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_UNKNOWN_ASSET"):
            asset_prompt(plan,story,"cena-falsa")

if __name__=="__main__":
    unittest.main()
