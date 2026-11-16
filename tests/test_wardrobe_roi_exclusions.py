"""Garantir que exclusões são condicionais e não aprovam a identidade."""
import unittest
import io
import json
from pathlib import Path
from PIL import Image
from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_exclusions import run, apply_exclusions, verify_exclusion_pixels, review_crops

class ROIExclusionTests(unittest.TestCase):
    def test_v4_collar_cleanup_preserves_beard_pixels(self):
        ep=Path(__file__).resolve().parents[1]/"canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
        previous=json.loads((ep/"QA-ROI-EXCLUSOES-V3.json").read_text(encoding="utf-8"))["results"][0]
        proposal=json.loads((ep/"ROI-EXCLUSOES-CANDIDATAS-V4.json").read_text(encoding="utf-8"))["rows"][0]
        mask=Image.new("L",(1024,1536),0)
        with Image.open(ep/previous["cleaned_candidate_path"]) as patch:
            mask.paste(patch.getchannel("A"),tuple(previous["cleaned_candidate_crop_xyxy"][:2]))
        cleaned,delta=apply_exclusions(mask,proposal["exclude_board_polygons"],mask.size,0,proposal["protected_board_polygons"])
        self.assertEqual(cleaned.crop((0,0,1024,339)).tobytes(),mask.crop((0,0,1024,339)).tobytes())
        self.assertIsNotNone(mask.crop((0,339,1024,1536)).getbbox())
        self.assertIsNone(cleaned.crop((0,339,1024,1536)).getbbox())
        self.assertGreater(delta["removed"],0)

    def test_context_panels_are_aligned_and_removed_pixels_are_exact(self):
        source=Image.new("RGB",(100,100),(20,40,80))
        before=Image.new("L",source.size,0)
        for x in range(35,55):
            for y in range(35,55):before.putpixel((x,y),255)
        after=before.copy()
        after.putpixel((40,40),0)
        snapshots=[im.tobytes() for im in (source,before,after)]
        panels,box=review_crops(source,before,after,(30,30,60,60))
        self.assertEqual(len(set(p.size for p in panels)),1)
        self.assertEqual(panels[0].tobytes(),source.crop(box).tobytes())
        self.assertEqual(sum(bool(x) for x in panels[2].getchannel("A").tobytes()),1)
        self.assertEqual(panels[2].getpixel((40-box[0],40-box[1])),(20,40,80,255))
        self.assertEqual(snapshots,[im.tobytes() for im in (source,before,after)])

    def test_context_at_image_edge_does_not_pad_or_shift(self):
        source=Image.new("RGB",(50,50),(1,2,3))
        mask=Image.new("L",source.size,255)
        panels,box=review_crops(source,mask,mask,(0,0,10,10))
        self.assertEqual(box,(0,0,34,34))
        self.assertEqual(panels[0].size,(34,34))
        self.assertIsNone(panels[2].getchannel("A").getbbox())

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
        ep=Path(__file__).resolve().parents[1]/"canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
        previous=json.loads((ep/"QA-ROI-EXCLUSOES-V3.json").read_text(encoding="utf-8"))["results"]
        self.assertEqual([r["cleaned_candidate_sha256"] for r in previous[1:]],
                         [r["cleaned_candidate_sha256"] for r in data["results"][1:]])
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
