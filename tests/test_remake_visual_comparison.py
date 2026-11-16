"""Deterministic comparisons must never modify source PNGs or approve art."""
import hashlib
import unittest
from unittest.mock import patch
from videoforge.cinematic_chat_references import reference_status
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

    def test_original_source_order_cannot_swap_kael_and_elara(self):
        audited=reference_status()
        audited["samples"]=list(reversed(audited["samples"]))
        with patch("videoforge.remake_visual_comparison.reference_status",return_value=audited):
            result=comparison(sync=False)
        self.assertEqual(result["comparisons"][0]["actor"],"kael")
        self.assertEqual(result["comparisons"][0]["original_sha256"],"edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f")
        self.assertEqual(result["comparisons"][1]["actor"],"elara")
        self.assertEqual(result["comparisons"][1]["original_sha256"],"bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a")

    def test_previews_are_deterministic_and_not_user_approved(self):
        self.assertEqual(comparison(sync=False),comparison(sync=False))

if __name__=="__main__":
    unittest.main()
