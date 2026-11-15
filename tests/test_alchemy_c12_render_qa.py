"""No new project artwork. Test QA math on in-memory synthetic RGB arrays."""
from __future__ import annotations

import unittest

from videoforge import c12_render_qa as qa
from videoforge.c12_technical_preview import plan, bbox

try:
    from PIL import Image
except ImportError:
    Image = None


def frame(width: int, height: int, *, rect=None) -> bytes:
    pixels = bytearray(width * height * 3)
    if rect:
        x0, y0, x1, y1 = rect
        for y in range(y0, y1):
            for x in range(x0, x1):
                at = 3 * (y * width + x)
                pixels[at:at + 3] = b"\xe0\x99\x55"
    return bytes(pixels)


class C12AutomatedQATest(unittest.TestCase):
    def test_five_independent_real_mesh_regions(self):
        p = plan()
        self.assertEqual(len(p["meshParts"]), 5)
        self.assertEqual(sum(2 * m["columns"] * m["rows"] for m in p["meshParts"]), 512)
        rects = [bbox(m["polygon"]) for m in p["meshParts"]]
        self.assertEqual(len(qa.project_boxes(rects)), 5)

    def test_projection_from_native_to_video_is_clipped(self):
        boxes = qa.project_boxes([[0, 0, 50, 50], [850, 1600, 91, 72]])
        for x0, y0, x1, y1 in boxes:
            self.assertLessEqual(0, x0)
            self.assertLessEqual(0, y0)
            self.assertLessEqual(x0, x1)
            self.assertLessEqual(y0, y1)
            self.assertLessEqual(x1, 720)
            self.assertLessEqual(y1, 1280)

    def test_rejects_static_mp4_even_when_codec_would_be_valid(self):
        a = frame(96, 96)
        result = qa.measure_local_motion(a, a, 96, 96, [(20, 20, 70, 70)])
        self.assertFalse(result["passed_localized_motion"])
        self.assertEqual(result["changed_pixels_inside_original_sprite_rois"], 0)

    def test_accepts_visible_changes_only_inside_real_sprite_roi(self):
        a = frame(96, 96)
        b = frame(96, 96, rect=(31, 31, 50, 50))
        result = qa.measure_local_motion(a, b, 96, 96, [(20, 20, 70, 70)])
        self.assertTrue(result["passed_localized_motion"])
        self.assertEqual(result["changed_pixels_inside_original_sprite_rois"], 361)
        self.assertEqual(result["changed_pixels_outside_original_sprite_rois"], 0)

    def test_rejects_whole_image_pan_or_global_color_change(self):
        a = frame(96, 96)
        b = frame(96, 96, rect=(0, 0, 96, 96))
        result = qa.measure_local_motion(a, b, 96, 96, [(20, 20, 70, 70)])
        self.assertFalse(result["passed_localized_motion"])
        self.assertGreater(result["changed_pixels_outside_original_sprite_rois"],
                           result["max_allowed_outside"])

    def test_rejects_wrong_frame_size_and_empty_roi(self):
        with self.assertRaisesRegex(qa.C12QAError, "MOTION_FRAME_OR_ROI_INVALID"):
            qa.measure_local_motion(b"\0" * 12, b"\0" * 12, 96, 96, [(20, 20, 50, 50)])
        a = frame(96, 96)
        with self.assertRaisesRegex(qa.C12QAError, "MOTION_FRAME_OR_ROI_INVALID"):
            qa.measure_local_motion(a, a, 96, 96, [])

    def test_rejects_invalid_bbox_projection(self):
        with self.assertRaisesRegex(qa.C12QAError, "PROJECT_INVALID_BOX"):
            qa.project_boxes([[0, 0, 0, 80]])
        with self.assertRaisesRegex(qa.C12QAError, "PROJECT_INVALID_CANVAS"):
            qa.project_boxes([[0, 0, 10, 10]], output_width=0)

    @unittest.skipUnless(Image is not None, "Pillow only installed in prebuilt media runner")
    def test_neutral_error_counts_color_and_threshold(self):
        a = Image.new("RGB", (8, 8), (0, 0, 0))
        b = Image.new("RGB", (8, 8), (0, 0, 0))
        b.putpixel((2, 3), (30, 25, 17))
        mae, bad = qa.neutral_difference(a, b)
        self.assertAlmostEqual(mae, 72 / (8 * 8 * 3))
        self.assertEqual(bad, 1)

    @unittest.skipUnless(Image is not None, "Pillow only installed in prebuilt media runner")
    def test_reject_neutral_with_nonmatching_canvas(self):
        a = Image.new("RGB", (8, 8), (0, 0, 0))
        b = Image.new("RGB", (9, 8), (0, 0, 0))
        with self.assertRaisesRegex(qa.C12QAError, "NEUTRAL_RGB_DIMENSIONS_MISMATCH"):
            qa.neutral_difference(a, b)


if __name__ == "__main__":
    unittest.main()
