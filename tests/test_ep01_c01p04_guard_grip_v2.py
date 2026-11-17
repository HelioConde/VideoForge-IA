"""Guard-grip V2 always uses the approved exact mother and independent source."""
import unittest
from videoforge import ep01_c01p04_v3_guard_grip_v2 as grip

class GuardGripTests(unittest.TestCase):
    def test_guard_targets_and_provenance(self):
        self.assertEqual(set(grip.GUARDS),
           {"character-guarda_esquerdo","character-guarda_direito"})
        self.assertTrue(grip.PRODUCER.endswith("guard-grip-v2"))
        self.assertEqual(len(grip.APPROVED_SOURCE_SHA),64)
    def test_preflight_reference_count_and_grip_requirement(self):
        for part in grip.GUARDS:
            if grip.archived(part):
                continue
            req=grip.prepare(part)
            self.assertEqual(req["part"],part)
            self.assertLessEqual(len(req["inputs"]),8)
            self.assertIn("five",req["prompt"])
            self.assertIn("DO NOT DRAW ANY SPEAR",req["prompt"])
            self.assertIn("LOWER THIRD",req["prompt"])
            self.assertIn("approved",req["prompt"])
            self.assertGreaterEqual(len(req["inputs"]),4)
            self.assertEqual(req["old"]["sha256"].__len__(),64)

if __name__=="__main__":
    unittest.main()
