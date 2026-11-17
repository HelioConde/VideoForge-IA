"""Checks exact approved grip references before paid generation."""
import unittest
from videoforge import ep01_c01p04_v3_canonical_grip_guide as guide

class CanonicalGripGuideTest(unittest.TestCase):
    def test_source_and_prompt(self):
        self.assertEqual(len(guide.SHA_APPROVED),64)
        self.assertEqual(len(guide.SHA_ALIGNED),64)
        if guide.existing():
            return
        r=guide.prepare()
        self.assertEqual(len(r["images"]),4)
        self.assertIn("PHYSICALLY HOLDING",r["prompt"])
        self.assertIn("palm BEHIND",r["prompt"])
        self.assertIn("fingers and",r["prompt"])
        self.assertIn("THUMB wrap IN FRONT",r["prompt"])
        self.assertIn("used to generate separate",r["prompt"])
        self.assertEqual(r["aligned_source"]["sha256"],guide.SHA_ALIGNED)

if __name__=="__main__":
    unittest.main()
