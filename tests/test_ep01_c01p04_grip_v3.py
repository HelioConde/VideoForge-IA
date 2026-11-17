"""EP01 grip V3 preflight. No proxy calls or final-art claims."""
import unittest
from videoforge import ep01_c01p04_grip_v3 as engine

class GripV3Tests(unittest.TestCase):
    def test_roles_and_grip_topology(self):
        self.assertEqual(engine.ROLES,("forearm-cuff","palm-rear","fingers-front"))
        self.assertEqual(len({engine.name(x) for x in engine.ROLES}),3)
        self.assertEqual(len(engine.APPROVED_SHA),64)
        self.assertEqual(len(engine.ALIGNED_SHA),64)
    def test_exact_sha_and_no_repeat(self):
        for role in engine.ROLES:
            if engine.archive(role):
                continue
            spec=engine.prep(role)
            self.assertEqual(spec["source_sha256"],engine.ALIGNED_SHA)
            self.assertEqual(spec["guide_sha256"],engine.GUIDE_SHA)
            self.assertEqual(len(spec["images"]),4)
            self.assertIn("NOT asking for a whole hand",spec["prompt"])
            self.assertIn("No spear pixels",spec["prompt"])
            self.assertIn("Do NOT create a complete clenched fist",spec["prompt"])
            self.assertIn(engine.ROLENAMES[role],spec["prompt"])

if __name__=="__main__":
    unittest.main()
