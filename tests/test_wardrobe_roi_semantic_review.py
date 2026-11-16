"""Barreira contra aprovação implícita a partir de seleção cromática."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_semantic_review import verify
from videoforge.remake_autopilot import ROOT,EPISODE

class SemanticReviewTests(unittest.TestCase):
    def test_real_unreviewed_masks_remain_blocked(self):
        r=verify()
        self.assertEqual(r["candidate_count"],8)
        self.assertEqual(r["documented_human_reviews"],0)
        self.assertEqual(r["approved_canonical_pairs"],0)
        self.assertTrue(r["r2_blocked"])
        self.assertTrue(all(not x["ready_for_canonical_comparison"] for x in r["rows"]))
    def test_bad_hash_and_false_review_are_blocked(self):
        with tempfile.TemporaryDirectory() as t:
            ep=Path(t)/EPISODE
            ep.mkdir(parents=True)
            for name in ("REVISAO-SEMANTICA-ROI-V3.json","QA-ROI-EXCLUSOES-V3.json"):
                (ep/name).write_bytes((ROOT/EPISODE/name).read_bytes())
            review=json.loads((ep/"REVISAO-SEMANTICA-ROI-V3.json").read_text())
            review["rows"][0]["candidate_sha256"]="0"*64
            (ep/"REVISAO-SEMANTICA-ROI-V3.json").write_text(json.dumps(review))
            with self.assertRaisesRegex(VideoForgeError,"HASH_MISMATCH"):
                verify(Path(t))
            review["rows"][0]["candidate_sha256"]=json.loads(
                (ep/"QA-ROI-EXCLUSOES-V3.json").read_text())["results"][0]["cleaned_candidate_sha256"]
            review["rows"][0]["status"]="REVISAO_HUMANA_DOCUMENTADA"
            (ep/"REVISAO-SEMANTICA-ROI-V3.json").write_text(json.dumps(review))
            with self.assertRaisesRegex(VideoForgeError,"EVIDENCE_REQUIRED"):
                verify(Path(t))
    def test_never_autoapprove_even_when_review_metadata_populated(self):
        with tempfile.TemporaryDirectory() as t:
            ep=Path(t)/EPISODE
            ep.mkdir(parents=True)
            for name in ("REVISAO-SEMANTICA-ROI-V3.json","QA-ROI-EXCLUSOES-V3.json"):
                (ep/name).write_bytes((ROOT/EPISODE/name).read_bytes())
            p=ep/"REVISAO-SEMANTICA-ROI-V3.json"
            obj=json.loads(p.read_text())
            row=obj["rows"][0]
            for key in ("pose_identity_verified","garment_variant_verified",
                        "correct_anatomical_region_verified","occlusion_review_verified",
                        "lighting_difference_ruled_out"):
                row[key]=True
            row["human_reviewer"]="revisao-teste"
            row["review_evidence"]="somente-fixture"
            row["status"]="REVISAO_HUMANA_DOCUMENTADA"
            p.write_text(json.dumps(obj))
            outcome=verify(Path(t))
            self.assertEqual(outcome["documented_human_reviews"],1)
            self.assertEqual(outcome["approved_canonical_pairs"],0)
            self.assertTrue(outcome["r2_blocked"])

if __name__=="__main__":
    unittest.main()
