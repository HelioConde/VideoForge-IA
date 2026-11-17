"""Bloquear o render C01-P02 até revisão de mãos e bainha sem distorção."""
import unittest
from videoforge.ep01_contact_gate import audit,require_ready,MAX_DELTA_RGB
from videoforge.errors import VideoForgeError

class ContactGateTests(unittest.TestCase):
    def test_all_four_native_sha_assets_are_present_but_not_approved(self):
        result=audit()
        self.assertEqual(len(result["candidate_sha256"]),4)
        self.assertFalse(result["render_ready"])
        self.assertFalse(result["mp4_claim"])
        self.assertTrue(result["improved"])
        self.assertIn("human_contact_review_missing",result["blocking_reasons"])

    def test_excessive_diff_never_passes_rig_gate(self):
        result=audit()
        self.assertGreater(result["new_diff_rgb"],MAX_DELTA_RGB)
        self.assertIn("recomposition_rgb_diff_exceeds_review_threshold",
                      result["blocking_reasons"])
        with self.assertRaisesRegex(VideoForgeError,"EP01_CONTACT_RIG_RENDER_BLOCKED"):
            require_ready()

if __name__=="__main__":
    unittest.main()
