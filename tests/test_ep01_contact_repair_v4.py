"""Guarantee C01-P02 V4 is a new non-canonical image from real V3 pixels."""
import hashlib
import unittest
from unittest.mock import patch

from videoforge import ep01_contact_repair_v4 as repair
from videoforge.errors import VideoForgeError


class ContactV4Tests(unittest.TestCase):
    def test_v3_sha_verified_and_prompt_is_anatomical(self):
        with patch.object(repair.proxy_images, "call_proxy") as paid:
            spec = repair.prepare()
            paid.assert_not_called()
        self.assertEqual(hashlib.sha256(spec["original"]).hexdigest(), repair.V3_SHA)
        self.assertEqual((spec["width"], spec["height"]), (941, 1672))
        self.assertIn("ONE continuous straight axis", spec["prompt"])
        self.assertIn("OUTSIDE and IN FRONT", spec["prompt"])
        self.assertIn("fingers curl naturally", spec["prompt"])
        self.assertEqual(repair.PRODUCER, "production-contact-repair-v4")

    def test_v4_already_archived_blocks_paid_generation(self):
        with patch.object(repair, "archived_candidate", return_value={"sha256": "a" * 64}):
            with patch.object(repair.proxy_images, "call_proxy") as paid:
                with self.assertRaisesRegex(VideoForgeError, "EP01_V4_ALREADY_ARCHIVED"):
                    repair.prepare()
                paid.assert_not_called()

    def test_model_restriction_before_provider_call(self):
        with patch.object(repair.proxy_images, "call_proxy") as paid:
            with self.assertRaisesRegex(VideoForgeError, "EP01_V4_MODEL_NOT_ALLOWED"):
                repair.generate("http://127.0.0.1:18080", model="unapproved")
            paid.assert_not_called()

    def test_v1_and_v3_remain_unmodified(self):
        spec = repair.prepare()
        self.assertIn("production-contact-repair-v3", spec["source_path"])
        self.assertEqual(repair.ROI, (370, 790, 900, 1660))
        self.assertTrue(repair.ASSET.endswith("-v4"))
        self.assertTrue(repair.PATCH_ASSET.endswith("-v4"))


if __name__ == "__main__":
    unittest.main()
