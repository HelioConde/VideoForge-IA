"""Offline SHA tests for rear palm V2; no proxy call."""
import unittest
from videoforge import ep01_c01p04_v3_rear_palm_v2 as palm

class RearPalmV2Test(unittest.TestCase):
    def test_locked_reference_provenance(self):
        self.assertEqual(len(palm.GUIDE_SHA),64)
        self.assertEqual(len(palm.MOTHER_SHA),64)
        self.assertEqual(len(palm.V1_REJECTED_SHA),64)
        if palm.previous():
            return
        p=palm.prepare()
        self.assertEqual(len(p["images"]),5)
        self.assertIn("DO NOT DRAW A CLENCHED FIST",p["prompt"])
        self.assertIn("DELETE ALL VISIBLE FINGERS",p["prompt"])
        self.assertIn("C-shaped OPEN EMPTY SPACE",p["prompt"])
        self.assertIn("DO NOT DRAW THE SPEAR",p["prompt"])
        self.assertIn("NOT a crop",p["prompt"])

if __name__=="__main__":
    unittest.main()
