"""Preview geometry must be reversible proposals, never final rig assets."""
import unittest
from PIL import Image
from scripts import qa_ep01_c01p04_v3_native_registration as reg

class NativeRegistrationTest(unittest.TestCase):
    def test_proposal_ids_and_bounds(self):
        proposals=reg.proposals((981,1602))
        self.assertEqual([x["id"] for x in proposals],
            ["A-top-left-native","B-centered-native","C-uniform-fit"])
        self.assertEqual(proposals[0]["offset_xy"],[0,0])
        self.assertEqual(proposals[1]["offset_xy"],[-20,35])
        self.assertLess(proposals[2]["scale"],1)
    def test_alpha_bbox_and_overlay_preserves_inputs(self):
        mother=Image.new("RGB",(941,1672),"grey")
        src=Image.new("RGBA",(981,1602),(0,0,0,0))
        for y in range(200,370):
            for x in range(270,420):
                src.putpixel((x,y),(200,120,80,255))
        original=src.tobytes()
        bbox=reg.native_alpha_bbox(src)
        self.assertEqual(bbox,(270,200,420,370))
        for candidate in reg.proposals(src.size):
            over,box=reg.overlay(mother,src,candidate,bbox)
            self.assertEqual(over.size,(941,1672))
            self.assertEqual(len(box),4)
            self.assertEqual(src.tobytes(),original)
    def test_sources_can_be_read_only_at_approved_sha(self):
        source=reg.aligned_source()
        self.assertEqual(source["sha256"],reg.EXPECTED_MOTHER_SHA)
        qa=__import__("json").loads(reg.SOURCE_REPORT.read_text(encoding="utf-8"))
        for part in reg.TARGETS:
            frame,data=reg.source_entry(part,qa)
            self.assertEqual(frame.size,(981,1602))
            self.assertEqual(data["visual_approval"],False)
            self.assertIsNotNone(reg.native_alpha_bbox(frame))

if __name__=="__main__":
    unittest.main()
