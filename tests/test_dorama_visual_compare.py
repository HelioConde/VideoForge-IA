"""A prancha usa duas fontes arquivadas reais sem aprovar figurino."""
import unittest
from videoforge.dorama_visual_compare import compare
class VisualCompareTests(unittest.TestCase):
    def test_real_comparison_sha_and_manual_review(self):
        result=compare()
        self.assertTrue(result["source_attached_to_generation"])
        self.assertTrue(result["reference_sha_verified"])
        self.assertTrue(result["image_pixels_unchanged"])
        self.assertFalse(result["visual_character_continuity_approved"])
        self.assertFalse(result["youtube_uploaded"])
        self.assertEqual(result["new_shot"],"C01-P05")
        self.assertEqual(result["anchor_size"],[941,1672])
        self.assertEqual(result["new_size"],[941,1671])
        self.assertEqual(result["generation_calls"],0)
    def test_aldric_closeup_uses_exact_same_anchor(self):
        result=compare(shot_id="C02-P01",
            asset_id="c02-p01-aldric-rosto-v1",run_id=43970462482)
        self.assertEqual(result["new_shot"],"C02-P01")
        self.assertEqual(result["anchor_size"],[941,1672])
        self.assertEqual(result["new_size"],[941,1672])
        self.assertTrue(result["source_attached_to_generation"])
        self.assertFalse(result["visual_character_continuity_approved"])
if __name__=="__main__":unittest.main()
