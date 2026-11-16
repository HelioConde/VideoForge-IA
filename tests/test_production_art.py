"""Comprovar que a arte e especifica do canal e nao cria falso MP4."""
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from videoforge.production_art import read_plan, asset_prompt, inspect_generated_dimensions, archived_reference, create_image
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

    def test_existing_alchemy_png_is_verified_before_another_ai_call(self):
        art=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01","character-bible")
        self.assertEqual(art["run_id"],43784005362)
        self.assertEqual((art["width"],art["height"]),(1199,1312))
        self.assertEqual(art["sha256"],"47b7b0cd83689a72a44e7e44dd61c5ba6beabcfc1e411f0e3850fc78f0e8b5c4")
        self.assertFalse(art["human_visual_approved"])
        with patch("videoforge.production_art.proxy_images.generate") as generator:
            with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_ALREADY_ARCHIVED_SHA_VERIFIED"):
                create_image("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                             "character-bible","http://127.0.0.1:18080")
            generator.assert_not_called()

    def test_unrecognized_or_unarchived_reference_allows_normal_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertIsNone(archived_reference(
                "alchemy-lab","mmorpg-conquiste-a-princesa-ep01","character-bible",
                Path(temp)))

    def test_corrupted_archive_rejected_before_paid_repetition(self):
        with tempfile.TemporaryDirectory() as temp:
            ep=Path(temp)/"canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
            dest=ep/"assets/geracoes/production-art-request/42"
            dest.mkdir(parents=True)
            (dest/"character-bible.png").write_bytes(b"NOT_A_PNG")
            with self.assertRaisesRegex(VideoForgeError,"MISSING_MANIFEST_BLOCK_REPEAT"):
                archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                                   "character-bible",Path(temp))
            (dest/"manifesto-geracoes.json").write_text(json.dumps({
                "schema":"videoforge/permanent-generated-image-archive/v1",
                "channel":"alchemy-lab",
                "video_id":"mmorpg-conquiste-a-princesa-ep01",
                "producer":"production-art-request",
                "github_run_id":42,
                "images":[{"file":"character-bible.png","sha256":"0"*64,
                           "width":1024,"height":1536,"bytes":9}],
            }),encoding="utf-8")
            with self.assertRaisesRegex(Exception,"(PNG|Png|png|BLOCK_REPEAT|imagem|Arquivo)"):
                archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                                   "character-bible",Path(temp))

    def test_wrong_channel_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_PLAN_MISSING"):
            read_plan("gamer","spy-x-family-familia-de-mentira")

    def test_unknown_asset_rejected_before_proxy_call(self):
        plan,story=read_plan("otaku-br","spy-x-family-familia-de-mentira")
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_UNKNOWN_ASSET"):
            asset_prompt(plan,story,"cena-falsa")

if __name__=="__main__":
    unittest.main()
