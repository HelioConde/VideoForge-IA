"""No-provider tests for 1-column correction of archived C08-P02 background."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from videoforge import ep01_proxy_c08_alignment as a

class EdgeAlignmentTests(unittest.TestCase):
    def test_archived_source_is_true_proxy_generation_and_immutable(self):
        p,meta=a.checked_source()
        self.assertEqual(meta["generation_method"],"proxy_generated_separate_image")
        self.assertTrue(meta["not_a_pixel_cutout"])
        self.assertEqual(meta["source_mother_sha256"],
                         "3c21b7d82d69b1445b45cb1a23582e556c910530b568c26ae0d48b4873c38721")
        self.assertEqual(meta["width"],1054)
        self.assertEqual(meta["height"],1493)
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),a.PROVIDER_SHA)

    def test_one_column_edge_correction_retains_provider_original(self):
        before,meta=a.checked_source()
        digest_before=hashlib.sha256(before.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"qa"
            result=a.align(a.ROOT,out)
            with Image.open(out/result["aligned_candidate_png"]) as img:
                self.assertEqual(img.size,(1053,1493))
                self.assertIn(img.mode,("RGB","RGBA"))
            self.assertEqual(result["source_sha256"],digest_before)
            self.assertEqual(result["edge_columns_removed_right"],1)
            self.assertFalse(result["pixel_resampling"])
            self.assertFalse(result["pixel_translation"])
            self.assertFalse(result["original_provider_png_changed"])
            self.assertFalse(result["final_visual_alignment_approved"])
            self.assertFalse(result["hidden_background_geometry_verified"])
            self.assertFalse(result["rig_ready"])
            self.assertEqual(result["new_provider_calls"],0)
            self.assertEqual(result["youtube_publications"],0)
            with self.assertRaises(ValueError):
                a.align(a.ROOT,out)
        self.assertEqual(hashlib.sha256(before.read_bytes()).hexdigest(),digest_before)

    def test_sha_drift_fails_without_touching_png(self):
        with patch.object(a,"PROVIDER_SHA","0"*64),self.assertRaises(ValueError):
            a.checked_source()

if __name__=="__main__":
    unittest.main()
