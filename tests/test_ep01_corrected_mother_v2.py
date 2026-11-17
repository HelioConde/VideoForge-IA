"""Versioned scene mother V2 source/shot checks without any paid call."""
import hashlib
import unittest
from unittest.mock import patch

from videoforge import ep01_corrected_mother_v2 as v2
from videoforge.errors import VideoForgeError


class V2MotherTests(unittest.TestCase):
    def test_rejected_p03_mother_is_sha_verified_and_corrected_narratively(self):
        with patch.object(v2, "existing_repair", return_value=None):
            with patch.object(v2.proxy_images, "call_proxy") as charged:
                spec=v2.prepare("C01-P03")
                charged.assert_not_called()
        self.assertEqual(hashlib.sha256(spec["source"]).hexdigest(),
                         v2.REJECTED_SOURCES["C01-P03"])
        self.assertIn("REMOVE BOTH GUARDS",spec["prompt"])
        self.assertIn("REMOVE the giant foreground sword",spec["prompt"])
        self.assertIn("KNEELING",spec["prompt"])
        self.assertLessEqual(len(spec["refs"])+1,v2.MAX_REFERENCE_PNGS_PER_REQUEST)
        self.assertEqual(spec["source_canvas"],[941,1672])

    def test_rejected_p04_mother_repaired_with_kneeling_and_lower_spear_grip(self):
        with patch.object(v2, "existing_repair", return_value=None):
            with patch.object(v2.proxy_images, "call_proxy") as charged:
                spec=v2.prepare("C01-P04")
                charged.assert_not_called()
        self.assertEqual(hashlib.sha256(spec["source"]).hexdigest(),
                         v2.REJECTED_SOURCES["C01-P04"])
        self.assertIn("WRONGLY STANDING",spec["prompt"])
        self.assertIn("KNEELING",spec["prompt"])
        self.assertIn("LOWER THIRD/BASE",spec["prompt"])
        self.assertLessEqual(len(spec["refs"])+1,v2.MAX_REFERENCE_PNGS_PER_REQUEST)

    def test_unsupported_shot_or_model_fails_before_any_proxy_call(self):
        with patch.object(v2.proxy_images, "call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,"UNAPPROVED_SHOT"):
                v2.prepare("C01-P05")
            with self.assertRaisesRegex(VideoForgeError,"MODEL_NOT_ALLOWED"):
                v2.generate("C01-P03","http://127.0.0.1:18080",model="bad")
            charged.assert_not_called()

    def test_archived_v2_never_rebilled(self):
        with patch.object(v2, "existing_repair", return_value={"sha256":"a"*64}):
            with patch.object(v2.proxy_images, "call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,"ALREADY_ARCHIVED_NO_REPEAT"):
                    v2.prepare("C01-P03")
                charged.assert_not_called()


if __name__=="__main__":
    unittest.main()
