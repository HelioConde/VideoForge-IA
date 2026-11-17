"""Zero-cost checks for fresh proxy-generated separate PNGs (not masks)."""
import hashlib
import unittest
from unittest.mock import patch

from videoforge import ep01_proxy_separate_parts as p
from videoforge.errors import VideoForgeError


class SeparatePartsTests(unittest.TestCase):
    def test_new_shot_background_has_sha_verified_mother_and_reference(self):
        # The real background may already be archived by subsequent runs.
        # These prompt/provenance tests never bypass the production no-repeat gate.
        with patch.object(p, "existing_part", return_value=None):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                spec=p.prepare("C01-P03","background-clean")
                charged.assert_not_called()
        self.assertEqual(spec["role"],"background")
        self.assertFalse(spec["transparent"])
        self.assertEqual(spec["source_dimensions"],(941,1672))
        self.assertEqual(hashlib.sha256(spec["mother"]).hexdigest(),
                         spec["mother_proof"]["sha256"])
        self.assertTrue(spec["ref_proofs"])
        self.assertIn("NEW INDEPENDENT image",spec["prompt"])
        self.assertIn("NO",spec["prompt"])
        self.assertLessEqual(len(spec["refs"])+1,p.MAX_REFERENCE_PNGS_PER_REQUEST)

    def test_character_is_requested_as_new_png_not_cutout(self):
        with patch.object(p, "existing_part", return_value=None):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                spec=p.prepare("C01-P03","character-kael")
                charged.assert_not_called()
        self.assertEqual(spec["role"],"character")
        self.assertTrue(spec["transparent"])
        self.assertIn("REAL transparent RGBA",spec["prompt"])
        self.assertIn("no cropping/segmentation",spec["prompt"])

    def test_unapproved_c01_p02_v1_cannot_be_used_for_rig(self):
        with patch.object(p.proxy_images, "call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,
                 "EP01_PROXY_PARTS_C01_P02_MOTHER_NOT_CANONICAL"):
                p.prepare("C01-P02","background-clean")
            charged.assert_not_called()

    def test_earlier_archive_never_rebilled(self):
        with patch.object(p,"existing_part",return_value={"sha256":"a"*64}):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,
                     "EP01_PROXY_PARTS_ALREADY_ARCHIVED_NO_REPEAT"):
                    p.prepare("C01-P03","background-clean")
                charged.assert_not_called()

    def test_wrong_asset_or_model_fail_before_proxy(self):
        with patch.object(p.proxy_images, "call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,"NOT_IN_SHOT_PLAN"):
                p.prepare("C01-P03","character-elara")
            with self.assertRaisesRegex(VideoForgeError,"MODEL_NOT_ALLOWED"):
                p.generate("C01-P03","background-clean","http://127.0.0.1:18080",
                           model="invalid")
            with self.assertRaisesRegex(VideoForgeError,"INVALID_SHOT"):
                p.prepare("C01-P01","background-clean")
            charged.assert_not_called()


if __name__=="__main__":
    unittest.main()
