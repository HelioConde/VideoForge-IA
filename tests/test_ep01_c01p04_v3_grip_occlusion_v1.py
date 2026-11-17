"""Offline reference verification for SHA-locked, independent palm/finger calls."""
import unittest
from videoforge import ep01_c01p04_v3_grip_occlusion_v1 as grip

class GripOcclusionV1(unittest.TestCase):
    def test_four_independent_assets(self):
        names={grip.asset(s,r) for s in grip.SIDES for r in grip.ROLES}
        self.assertEqual(len(names),4)
        self.assertEqual(grip.ROLES,("palm-rear","fingers-front"))
        self.assertTrue(all("grip" in x for x in names))

    def test_approved_hand_is_reference_only(self):
        for side in grip.SIDES:
            for role in grip.ROLES:
                if grip.archived(side,role):
                    continue
                q=grip.prepare(side,role)
                self.assertEqual((q["side"],q["role"]),(side,role))
                self.assertGreaterEqual(len(q["images"]),4)
                self.assertLessEqual(len(q["images"]),8)
                self.assertEqual(len(q["guide_sha256"]),64)
                self.assertEqual(q["mother"]["sha256"],grip.ALIGNED_SHA)
                self.assertIn("rear palm -> real spear shaft ->",q["prompt"])
                self.assertIn("NO spear pixels",q["prompt"])
                self.assertIn("not an approved sprite",q["prompt"])
                self.assertIn("near original hand location",q["prompt"])
                self.assertIn("independent",q["prompt"])

if __name__=="__main__":
    unittest.main()
