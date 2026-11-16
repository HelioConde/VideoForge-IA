"""Garantir que exclusões são condicionais e não aprovam a identidade."""
import unittest
import io
from PIL import Image
from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_exclusions import run, apply_exclusions, verify_exclusion_pixels

class ROIExclusionTests(unittest.TestCase):
    def test_protected_cloth_rejects_overlapping_exclusion(self):
        mask=Image.new("L",(1024,1536),255)
        polygon=[[280,370],[300,370],[300,380],[280,380]]
        before=mask.tobytes()
        with self.assertRaisesRegex(VideoForgeError,"TOUCHES_PROTECTED"):
            apply_exclusions(mask,[polygon],mask.size,0,[polygon])
        self.assertEqual(mask.tobytes(),before)

    def test_empty_and_wrong_geometry_fail_closed(self):
        with self.assertRaisesRegex(VideoForgeError,"REMOVED_TOO_MUCH"):
            apply_exclusions(Image.new("L",(1024,1536)),[],(1024,1536),0)
        with self.assertRaisesRegex(VideoForgeError,"MASK_GEOMETRY"):
            apply_exclusions(Image.new("L",(100,100)),[],(1024,1536),0)

    def test_integrity_rejects_color_alpha_crop_and_count_corruption(self):
        source=Image.new("RGB",(20,20),(30,60,90))
        before=Image.new("L",source.size,255)
        after=before.copy()
        after.putpixel((2,2),0)
        image=source.convert("RGBA")
        image.putalpha(after)
        def encoded(im):
            stream=io.BytesIO()
            im.save(stream,format="PNG")
            return stream.getvalue()
        blob=encoded(image)
        result=verify_exclusion_pixels(source,before,after,blob,(0,0,20,20),1)
        self.assertTrue(result["rgb_matches_source_crop"])
        self.assertFalse(result["semantic_approval"])
        corrupt=image.copy()
        corrupt.putpixel((3,3),(31,60,90,255))
        with self.assertRaisesRegex(VideoForgeError,"RGB_CHANGED"):
            verify_exclusion_pixels(source,before,after,encoded(corrupt),(0,0,20,20),1)
        corrupt=image.copy()
        corrupt.putpixel((2,2),(30,60,90,255))
        with self.assertRaisesRegex(VideoForgeError,"PNG_ALPHA_CHANGED"):
            verify_exclusion_pixels(source,before,after,encoded(corrupt),(0,0,20,20),1)
        with self.assertRaisesRegex(VideoForgeError,"COUNT_MISMATCH"):
            verify_exclusion_pixels(source,before,after,blob,(0,0,20,20),2)
        with self.assertRaisesRegex(VideoForgeError,"CROP_LOSES_PIXELS"):
            verify_exclusion_pixels(source,before,after,blob,(1,0,20,20),1)

    def test_integrity_rejects_new_or_partially_erased_pixels(self):
        source=Image.new("RGB",(20,20))
        before=Image.new("L",source.size,128)
        for alpha in (64,255):
            after=before.copy()
            after.putpixel((0,0),alpha)
            with self.assertRaisesRegex(VideoForgeError,"NOT_SUBTRACTION"):
                verify_exclusion_pixels(source,before,after,b"",(0,0,20,20),0)

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
            self.assertTrue(row["pixel_integrity"]["rgb_matches_source_crop"])
            self.assertTrue(row["pixel_integrity"]["crop_preserves_all_retained_pixels"])
            self.assertFalse(row["pixel_integrity"]["semantic_approval"])

if __name__=="__main__":
    unittest.main()
