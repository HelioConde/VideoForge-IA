"""Visual costume comparisons cannot auto-promote legacy artwork."""
import unittest
from videoforge.wardrobe_detail_qa import compare
class WardrobeDetailQATests(unittest.TestCase):
    def test_provenance_and_rejection(self):
        report=compare(sync=False)
        self.assertEqual(report["schema"],"videoforge/wardrobe-detail-qa/v1")
        self.assertEqual(report["owner_decision"],"rejected_wardrobe_inconsistency")
        self.assertEqual(len(report["comparisons"]),2)
        self.assertFalse(report["can_generate_r2"])
        self.assertFalse(report["human_visual_approval"])
        self.assertEqual(report["image_provider_calls"],0)
        self.assertFalse(report["new_images_generated"])
        for candidate in report["comparisons"]:
            self.assertEqual(len(candidate["source_images"]),4)
            self.assertFalse(candidate["detail_crop_is_subject_detection"])
            self.assertFalse(candidate["original_wardrobe_approved"])
            self.assertTrue(candidate["preserves_png_source_bytes"])
            self.assertEqual(len(candidate["qa_jpeg_sha256"]),64)
    def test_deterministic(self):
        self.assertEqual(compare(sync=False),compare(sync=False))
if __name__=="__main__":
    unittest.main()
