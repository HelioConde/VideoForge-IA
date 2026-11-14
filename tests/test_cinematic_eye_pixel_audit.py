"""Tests for real alpha geometry with synthetic masks only in memory.

No PNG files, images, model calls or uploads are created.
These tiny L masks are not artwork and never mark a shot as approved.
"""
from __future__ import annotations

import unittest
from PIL import Image, ImageDraw

from videoforge.cinematic_eye_pixel_audit import (
    verify_alpha_sweep,translate_mask,pixel_count,
)
from videoforge.errors import VideoForgeError

W,H=128,64

def rectangle(x0:int,y0:int,x1:int,y1:int)->Image.Image:
    im=Image.new("L",(W,H),0)
    ImageDraw.Draw(im).rectangle((x0,y0,x1,y1),fill=255)
    return im

def fixture():
    head=rectangle(6,5,90,28)
    eye_masks={
        "left":rectangle(9,8,34,23),
        "right":rectangle(47,8,75,23),
    }
    parts={
        "pupil-left":rectangle(12,12,16,17),
        "pupil-right":rectangle(51,12,55,17),
        "eyelid-left":rectangle(12,10,30,11),
        "eyelid-right":rectangle(50,10,70,11),
    }
    return head,parts,eye_masks

class EyePixelGeometryTests(unittest.TestCase):
    def test_alpha_sweep_30_translations_inside_sclera_with_underlay(self):
        head,parts,safe=fixture()
        qa=verify_alpha_sweep(head,parts,safe)
        self.assertTrue(qa["alphaSafetyVerified"])
        self.assertEqual(qa["sweepsTested"],30)
        self.assertEqual(qa["imageGenerationCalls"],0)
        self.assertEqual(qa["newImagesCreated"],0)
        self.assertTrue(qa["humanVisualApprovalStillRequired"])
        self.assertTrue(qa["pupilDuplicatePaintNotProvenByMasks"])
        for eye in ("left","right"):
            self.assertEqual(qa["eyes"][eye]["pupil"]["maxShiftPx"],12)
            self.assertEqual(qa["eyes"][eye]["eyelid"]["maxShiftPx"],1)

    def test_clips_outside_safe_sclera_at_shift_12(self):
        head,parts,safe=fixture()
        safe["left"]=rectangle(9,8,24,23)
        with self.assertRaisesRegex(VideoForgeError,
                                    "CINEMATIC_EYE_PIXEL_BLEED_OR_UNDERLAY_MISSING"):
            verify_alpha_sweep(head,parts,safe)

    def test_eyelid_leaves_safe_area_after_one_pixel_shift(self):
        head,parts,safe=fixture()
        safe["right"]=rectangle(47,8,70,23)
        with self.assertRaisesRegex(VideoForgeError,
                                    "CINEMATIC_EYE_PIXEL_BLEED_OR_UNDERLAY_MISSING"):
            verify_alpha_sweep(head,parts,safe)

    def test_head_missing_pixels_under_moving_pupil(self):
        head,parts,safe=fixture()
        # Hole only appears at a shifted position, not in neutral pose.
        ImageDraw.Draw(head).rectangle((27,14,29,17),fill=0)
        with self.assertRaisesRegex(VideoForgeError,
                                    "CINEMATIC_EYE_PIXEL_BLEED_OR_UNDERLAY_MISSING"):
            verify_alpha_sweep(head,parts,safe)

    def test_image_edge_clipping_is_not_wrapped_to_other_side(self):
        head,parts,safe=fixture()
        parts["pupil-right"]=rectangle(120,12,127,17)
        # Full sclera-like mask does not permit a clipped pupil.
        safe["right"]=rectangle(50,8,127,23)
        head=rectangle(6,5,127,28)
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EYE_PIXEL_BLEED"):
            verify_alpha_sweep(head,parts,safe)
        self.assertEqual(pixel_count(translate_mask(parts["pupil-right"],12)),0)

    def test_eye_part_cannot_be_empty(self):
        head,parts,safe=fixture()
        parts["eyelid-left"]=Image.new("L",(W,H),0)
        with self.assertRaisesRegex(VideoForgeError,
                                    "CINEMATIC_EYE_PART_EMPTY"):
            verify_alpha_sweep(head,parts,safe)

    def test_reject_wrong_eye_part_names_or_size(self):
        head,parts,safe=fixture()
        del parts["pupil-left"]
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EYE_MASK_INPUT_INVALID"):
            verify_alpha_sweep(head,parts,safe)
        head,parts,safe=fixture()
        safe["left"]=Image.new("L",(20,20),255)
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EYE_MASK_INPUT_INVALID"):
            verify_alpha_sweep(head,parts,safe)

    def test_alpha_threshold_and_no_wrap(self):
        almost=Image.new("L",(W,H),0)
        almost.putpixel((100,10),127)
        self.assertEqual(pixel_count(translate_mask(almost,3)),0)
        almost.putpixel((100,10),255)
        self.assertEqual(translate_mask(almost,3).getpixel((103,10)),255)
        self.assertEqual(translate_mask(almost,3).getpixel((100,10)),0)

if __name__=="__main__":
    unittest.main()
