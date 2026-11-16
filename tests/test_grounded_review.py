"""Never infer approval, pay for images or alter imported source PNGs."""
import hashlib
import unittest
from unittest.mock import patch
from videoforge.grounded_review import compare,provenance
from videoforge.production_art import archived_reference
from videoforge.remake_autopilot import ROOT,EPISODE
from videoforge.errors import VideoForgeError

class GroundedReviewTests(unittest.TestCase):
    def test_three_way_review_uses_real_archives(self):
        report=compare()
        self.assertEqual(report["status"],"grounded_png_sha_verified_visual_review_pending")
        self.assertEqual(report["grounded_run_id"],43868021687)
        self.assertEqual(report["grounded_sha256"],"6ed16d498df46b59c38e9c34ab25127b5b032159ab3289c073ac0058fcda6fc3")
        self.assertEqual(report["grounded_dimensions"],[1199,1312])
        self.assertEqual([s["actor"] for s in report["sha_verified_provider_input_sources"]],["kael","elara"])
        self.assertEqual(len(report["comparisons"]),2)
        self.assertFalse(report["human_approved"])
        self.assertFalse(report["canonical_approved"])
        self.assertFalse(report["new_art_generated_during_qa"])
        self.assertEqual(report["provider_calls"],0)
        self.assertTrue(report["aldric_individual_reference_sha_missing"])

    def test_no_png_source_mutation_or_nondeterminism(self):
        path=ROOT/EPISODE/"assets/referencias/chat-aprovadas/kael-close-salao.png"
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(compare(),compare())
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)

    def test_bad_producer_provenance_rejected(self):
        grounded=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                                    "character-bible-grounded")
        self.assertEqual(len(provenance(ROOT/EPISODE,grounded)),2)
        with patch("videoforge.grounded_review.EXPECTED",{}):
            with self.assertRaisesRegex(VideoForgeError,"ORIGINAL_PROVENANCE_INVALID"):
                provenance(ROOT/EPISODE,grounded)

if __name__=="__main__":
    unittest.main()
