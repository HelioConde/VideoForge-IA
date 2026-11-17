"""Second Aldric attempt must not reuse an incorrectly sized PNG."""
import unittest
from videoforge import ep01_approved_v3_aldric_repair as fix

class AldricRepairV2Tests(unittest.TestCase):
    def test_rejected_source_provenance(self):
        bad=fix.rejected_original()
        self.assertEqual(bad["sha256"],fix.REJECTED_SHA)
        self.assertEqual(bad["reason"],"wrong_canvas_and_character_scale")

    def test_source_provenance_prompt(self):
        if fix.archived():
            return
        data=fix.prepare()
        self.assertTrue(data["source"]["path"].endswith(
            "c01-p04-scene-mother-facing-throne-v3-native-aligned.png"))
        self.assertIn("1200x1310",data["prompt"])
        self.assertIn("941x1672",data["prompt"])
        self.assertIn("FULLY TRANSPARENT",data["prompt"])
        self.assertLessEqual(len(data["images"]),8)

if __name__=="__main__":
    unittest.main()
