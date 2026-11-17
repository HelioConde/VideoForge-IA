import unittest
from videoforge.art_request_gate import decide
C="alchemy-lab"
V="mmorpg-conquiste-a-princesa-ep01"
class ArtRequestGateTests(unittest.TestCase):
    def test_closed_push_not_billable(self):
        a=decide(C,V,"character-bible-grounded","push","completed_but_rejected_by_owner_wardrobe_mismatch")
        self.assertFalse(a["ready"])
        self.assertEqual(a["reason"],"already_archived_sha_no_repeat")
    def test_manual_replay_of_previous_image_does_nothing(self):
        a=decide(C,V,"character-bible-grounded")
        self.assertFalse(a["ready"])
    def test_r2_cannot_go_ahead_without_approved_outfits(self):
        a=decide(C,V,"character-bible-grounded-r2")
        self.assertFalse(a["ready"])
        self.assertEqual(a["reason"],"r2_full_outfit_approval_missing")
        self.assertEqual(a["provider_calls"],0)
    def test_unarchived_other_asset_not_blocked_by_costume_feedback(self):
        self.assertTrue(decide(C,V,"throne-hall")["ready"])
    def test_old_pose_requests_are_blocked_even_when_manually_dispatched(self):
        for asset in (
            "biblia-guarda-esquerdo-cruzando-lanca-v1",
            "biblia-guardas-cruzando-lancas-base-v1",
            "biblia-rei-sentado-no-trono-base-v1",
            "biblia-kael-ajoelhado-base-v1",
            "biblia-perseguicao-beco-base-v1",
        ):
            with self.subTest(asset=asset):
                result=decide(C,V,asset,event="workflow_dispatch")
                self.assertFalse(result["ready"])
                self.assertEqual(result["reason"],"legacy_pose_deprecated_use_layered_scene_pipeline")
                self.assertEqual(result["provider_calls"],0)

if __name__=="__main__":
    unittest.main()
