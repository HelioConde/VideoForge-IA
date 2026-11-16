"""Deterministic comparisons must never modify source PNGs or approve art."""
import hashlib
import unittest
from videoforge.remake_visual_comparison import comparison
from videoforge.remake_autopilot import ROOT,EPISODE

class CompareIdentityTests(unittest.TestCase):
    def test_only_sha_verified_originals_and_preserved_candidate(self):
        orig=ROOT/EPISODE/"assets/referencias/chat-aprovadas/kael-close-salao.png"
        digest=hashlib.sha256(orig.read_bytes()).hexdigest()
        d=comparison(sync=False)
        self.assertEqual(d["status"],"ready_for_explicit_human_identity_review")
        self.assertEqual(len(d["comparisons"]),2)
        self.assertTrue(d["camera_c12_sha_verified"])
        self.assertFalse(d["human_approved"])
        self.assertFalse(d["new_art_created"])
        self.assertFalse(d["original_pixels_modified"])
        self.assertEqual(d["provider_calls"],0)
        self.assertEqual(digest,hashlib.sha256(orig.read_bytes()).hexdigest())
        self.assertTrue(all(not x["identity_match_approved"] for x in d["comparisons"]))

    def test_previews_are_deterministic_and_not_user_approved(self):
        self.assertEqual(comparison(sync=False),comparison(sync=False))

if __name__=="__main__":
    unittest.main()
