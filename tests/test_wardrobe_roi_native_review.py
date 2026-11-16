"""Regressões 1:1 de revisão visual (não equivalem a aprovação)."""
import unittest
from PIL import Image
from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_native_review import run,source_pixel_sheet

class NativeROIReviewTests(unittest.TestCase):
    def test_real_native_eight_tiles_are_pending(self):
        result=run()
        self.assertEqual(result["tile_count"],8)
        self.assertEqual(result["semantic_masks_verified"],0)
        self.assertEqual(result["canonical_pairs_ready"],0)
        self.assertTrue(result["r2_blocked"])
        for r in result["tiles"]:
            self.assertEqual(r["tile_scale_factor"],1)
            self.assertFalse(r["geometry_interpolated"])
    def test_source_pixels_preserved_exactly(self):
        im=Image.new("RGB",(36,30),(111,77,52))
        prior=Image.new("L",im.size,0)
        prior.putpixel((7,8),255)
        after=prior.copy()
        after.putpixel((7,8),0)
        removed=prior.copy()
        sheet=source_pixel_sheet(im,prior,removed,after,[3,4,23,24])
        self.assertEqual(sheet.size,(80,64))
        self.assertEqual(sheet.crop((0,44,20,64)).tobytes(),
                         im.crop((3,4,23,24)).tobytes())
    def test_corruption_in_removed_mask_is_rejected(self):
        im=Image.new("RGB",(36,30),(111,77,52))
        prior=Image.new("L",im.size,0)
        after=prior.copy()
        removed=Image.new("L",im.size,0)
        removed.putpixel((5,5),255)
        with self.assertRaisesRegex(VideoForgeError,"REMOVED_PIXELS_INVALID"):
            source_pixel_sheet(im,prior,removed,after,[0,0,20,20])

if __name__=="__main__":
    unittest.main()
