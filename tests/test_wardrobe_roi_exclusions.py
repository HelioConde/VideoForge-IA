"""Garantir que exclusões são condicionais e não aprovam a identidade."""
import unittest
from PIL import Image
from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_exclusions import run, apply_exclusions

class ROIExclusionTests(unittest.TestCase):
    def test_no_exclusion_preserves_alpha(self):
        src=Image.new("L",(1024,1536),0)
        for y in range(600,700):
            for x in range(300,400):src.putpixel((x,y),255)
        masked,report=apply_exclusions(src,[],src.size,0)
        self.assertEqual(masked.tobytes(),src.tobytes())
        self.assertEqual(report["removed"],0)
    def test_polygon_removal_cannot_promote(self):
        source=Image.new("L",(1024,1536),255)
        result,info=apply_exclusions(source,[[[280,370],[300,370],[300,380],[280,380]]],source.size,0)
        self.assertGreater(info["removed"],0)
        self.assertEqual(source.getpixel((420,700)),255)
        self.assertEqual(result.getpixel((420,700)),255)
    def test_out_of_frame_fails_closed(self):
        src=Image.new("L",(1024,1536),255)
        with self.assertRaisesRegex(VideoForgeError,"OUTSIDE_SOURCE"):
            apply_exclusions(src,[[[10,10],[20,10],[20,20]]],src.size,0)
    def test_ep01_eight_real_regions_still_rejected(self):
        data=run()
        self.assertEqual(data["candidate_count"],8)
        self.assertEqual(data["verified_semantic_masks"],0)
        self.assertEqual(data["official_roi_pairs_ready"],0)
        self.assertTrue(data["r2_blocked"])
        self.assertEqual(data["paid_calls"],0)
        self.assertEqual(len(data["results"]),8)
        for row in data["results"]:
            self.assertFalse(row["semantically_verified"])
            self.assertFalse(row["official_art_usable"])
            self.assertGreater(row["candidate_exclusion"]["after"],127)

if __name__=="__main__":
    unittest.main()
