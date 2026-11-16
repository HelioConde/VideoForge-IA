"""Main CI must prevent turning unannotated ROI pixels into visual approval."""
import json
import unittest
from videoforge.remake_autopilot import ROOT,EPISODE

class ROIMetadataTests(unittest.TestCase):
    def test_real_sources_unreviewed_and_owner_rejection_preserved(self):
        ep=ROOT/EPISODE
        preview=json.loads((ep/"QA-ROI-FIGURINOS-V2.json").read_text(encoding="utf-8"))
        compare=json.loads((ep/"QA-COMPARACAO-ROI-SEMANTICA-V2.json").read_text(encoding="utf-8"))
        state=json.loads((ep/"estado-atual.json").read_text(encoding="utf-8"))
        self.assertEqual(len(preview["region_slots"]),4)
        self.assertEqual(len(compare["pairs"]),4)
        self.assertEqual(compare["unverified_pairs"],4)
        self.assertFalse(preview["actual_beard_roi_verified"])
        self.assertFalse(preview["actual_elara_bodice_roi_verified"])
        self.assertFalse(preview["automatic_approval"])
        self.assertEqual(compare["automatic_approved_art_count"],0)
        self.assertTrue(compare["known_owner_rejections_still_active"])
        self.assertEqual(state["autopilot_checkpoint"]["blocker"],
                         "wardrobe_identity_rejected_reference_missing")
        self.assertFalse(state["wardrobe_semantic_roi_20261116"]["full_costume_approved"])
        self.assertEqual(preview["provider_calls"],0)
        self.assertEqual(compare["provider_calls"],0)
if __name__=="__main__":
    unittest.main()
