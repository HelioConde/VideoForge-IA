import hashlib
import unittest
from videoforge.wardrobe_roi_review import prepare
from videoforge.remake_autopilot import EPISODE,ROOT

class ROIDraftTests(unittest.TestCase):
    def test_real_source_sha_and_no_false_mask(self):
        result=prepare()
        self.assertEqual(result["schema"],"videoforge/wardrobe-roi-review/v1")
        self.assertEqual(len(result["region_slots"]),4)
        self.assertEqual(len(result["previews"]["aldric"]["sources"]),3)
        self.assertEqual(len(result["previews"]["elara"]["sources"]),3)
        self.assertEqual(len(result["previews"]["aldric"]["draft_polygons"]),3)
        self.assertTrue(result["king_polygons_from_unapproved_v1_rig"])
        self.assertFalse(result["actual_beard_roi_verified"])
        self.assertFalse(result["actual_outer_center_roi_verified"])
        self.assertFalse(result["automatic_approval"])
        self.assertFalse(result["king_c02_c03_pose_known"])
        self.assertEqual(result["provider_calls"],0)
        self.assertTrue(all(not row["auto_compare_ready"] and
                            row["source_a_polygon"] is None and
                            not row["mask_pair_human_verified"]
                            for row in result["region_slots"]))
    def test_no_original_png_changes(self):
        path=ROOT/EPISODE/"assets/cena-01/rig-drafts/aldric-origem/aldric-RGB-da-mae-CANDIDATO.png"
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(prepare(),prepare())
        self.assertEqual(sha,hashlib.sha256(path.read_bytes()).hexdigest())
if __name__=="__main__":
    unittest.main()
