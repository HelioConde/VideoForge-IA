"""Wardrobe rejection is an actionable hard gate, not a quality note."""
import unittest
from unittest.mock import patch

from videoforge.wardrobe_review import (
    owner_review,rejected_reference_sha,source_readiness,
    r2_edit_payload,REJECTED_SHA,
)
from videoforge.remake_autopilot import choose_next
from videoforge.errors import VideoForgeError


class WardrobeReviewTests(unittest.TestCase):
    def test_explicit_owner_rejection_protects_aldric_elara(self):
        owner,contract=owner_review()
        self.assertEqual(owner["decision"],"rejected_wardrobe_inconsistency")
        self.assertEqual(owner["sha256"],REJECTED_SHA)
        self.assertEqual({x["code"] for x in owner["issues"] if x["status"]=="rejected"},
                         {"wardrobe_mismatch_aldric",
                          "wardrobe_mismatch_elara_purple_bodice"})
        self.assertTrue(rejected_reference_sha(REJECTED_SHA))
        self.assertFalse(rejected_reference_sha("0"*64))
        self.assertFalse(contract["canonical_identity_approved"])

    def test_r2_waits_for_explicit_full_costume_sha_sources(self):
        proof=source_readiness()
        self.assertEqual(proof["verified"],0)
        self.assertEqual(proof["required"],2)
        self.assertFalse(proof["r2_ready"])
        with self.assertRaisesRegex(VideoForgeError,"WARDROBE_R2_SOURCES_NOT_OWNER_APPROVED"):
            r2_edit_payload("Preservar exatamente os figurinos de Elara e Aldric. "*5,
                            "gpt-image-2","1024x1536")

    def test_autopilot_keeps_rejected_sha_out_of_canonical_art(self):
        result=choose_next()
        self.assertEqual(result["stage"],"review_identity_reference")
        self.assertEqual(result["blocker"],"wardrobe_identity_rejected_reference_missing")
        self.assertFalse(result["dispatch_allowed"])
        self.assertEqual(result["grounded_candidate"]["status"],
                         "rejected_wardrobe_inconsistency")
        self.assertEqual(result["wardrobe_source_readiness"]["verified"],0)
        self.assertFalse(result["grounded_candidate"]["canonical_identity_approved"])

    def test_forged_approved_anchor_cannot_bypass_owner_wardrobe_rejection(self):
        import copy
        from videoforge.cinematic_direction import (
            load_active_remake_plan,_remake_anchor_state,
        )
        from videoforge.remake_autopilot import ROOT
        source=load_active_remake_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
        altered=copy.deepcopy(source)
        altered["identity_anchors"][0].update({
            "path":"assets/geracoes/production-art-request/43868021687/character-bible-grounded.png",
            "sha256":REJECTED_SHA,
            "status":"approved",
            "human_approved":True,
        })
        with patch("videoforge.cinematic_direction.load_active_remake_plan",return_value=altered):
            result=_remake_anchor_state("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",ROOT)
        self.assertTrue(result["source_image_files_verified"])
        self.assertFalse(result["human_approved"])

    def test_r2_no_provider_call_before_full_wardrobe_source(self):
        from videoforge.production_art import create_image
        with patch("videoforge.production_art.proxy_images.call_proxy") as proxy:
            with self.assertRaisesRegex(VideoForgeError,"WARDROBE_R2_SOURCES_NOT_OWNER_APPROVED"):
                create_image("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                             "character-bible-grounded-r2","http://127.0.0.1:18080")
            proxy.assert_not_called()


if __name__=="__main__":
    unittest.main()
