"""Source-verified count of generated shots, not approvals (no proxy)."""
import unittest
from videoforge.ep01_image_inventory import calculate


class InventoryTests(unittest.TestCase):
    def test_counts_are_derived_from_exact_original_mothers(self):
        result=calculate()
        self.assertEqual(result["shots_total"],40)
        self.assertEqual(result["visual_shots"],39)
        self.assertEqual(result["black_shot"],"C01-P01")
        self.assertEqual(result["visual_shots_with_original_mother"]
                         + result["visual_shots_missing_original_mother"],39)
        self.assertEqual(len(set(result["original_mother_shot_ids"])),
                         result["visual_shots_with_original_mother"])
        self.assertEqual(len(result["original_mothers"]),
                         result["visual_shots_with_original_mother"])
        self.assertNotIn("C01-P01", result["original_mother_shot_ids"])
        self.assertTrue(result["counts_are_generated_not_approved"])
        self.assertFalse(result["human_visual_approval"])
        self.assertFalse(result["rig_ready"])
        self.assertFalse(result["mp4_generated"])
        self.assertFalse(result["youtube_uploaded"])
        self.assertTrue(result["no_provider_calls"])
        self.assertIn("C01-P03", result["original_mothers"])

    def test_separate_proxy_assets_are_not_mothers(self):
        result=calculate()
        self.assertGreaterEqual(result["separate_proxy_generated_asset_count"],3)
        for item in result["separate_proxy_generated_assets"]:
            self.assertFalse(item["human_visual_approval"])
            self.assertIn("/production-proxy-separate-part-v1/",item["file"])
            self.assertNotIn(item["asset"], result["original_mother_shot_ids"])


if __name__=="__main__":
    unittest.main()
