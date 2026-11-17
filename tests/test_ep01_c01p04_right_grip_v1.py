"""Right guard rig-source preflight; does not make proxy calls."""
import unittest
from videoforge import ep01_c01p04_right_grip_v1 as engine

class RightGripV1Tests(unittest.TestCase):
    def test_right_independence(self):
        self.assertEqual(engine.ROLES,("forearm-cuff","palm-rear","fingers-front"))
        self.assertEqual(len({engine.name(x) for x in engine.ROLES}),3)
        self.assertTrue(all("right-grip" in engine.name(x) for x in engine.ROLES))
        self.assertEqual(len(engine.APPROVED_SHA),64)
        self.assertEqual(len(engine.ALIGNED_SHA),64)
    def test_sha_and_perspective(self):
        for role in engine.ROLES:
            if engine.archive(role):
                continue
            s=engine.prep(role)
            self.assertEqual(s["source_sha256"],engine.ALIGNED_SHA)
            self.assertEqual(len(s["images"]),5)
            self.assertEqual(len(s["right_guard_sha256"]),64)
            self.assertEqual(len(s["spear_sha256"]),64)
            self.assertIn("RIGHT",s["prompt"])
            self.assertIn("not to mirror handedness",s["prompt"])
            self.assertIn("No spear pixels",s["prompt"])
            self.assertIn(engine.ROLENAMES[role],s["prompt"])

if __name__=="__main__":
    unittest.main()
