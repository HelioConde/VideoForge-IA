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
if __name__=="__main__":
    unittest.main()
