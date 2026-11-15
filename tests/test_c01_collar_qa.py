"""C01 collar QA tests only synthetic in-memory RGBA buffer samples.

Never generates or edits any project art; real gate runs on source SHA-verified
scene background and decoded H.264 on GitHub Actions.
"""
import unittest
from videoforge.c01_collar_qa import (
    C01CollarError, collar_background_exposure, collar_gate
)


def rgba(w, h, color):
    return bytearray(bytes(color) * (w*h))


class C01CollarExposureTest(unittest.TestCase):
    def setUp(self):
        self.w = 32
        self.h = 32
        self.bg = rgba(self.w, self.h, (83, 45, 49, 255))
        self.before = rgba(self.w, self.h, (83, 45, 49, 255))
        for y in range(7, 19):
            for x in range(8, 20):
                i=(y*self.w+x)*4
                self.before[i:i+4] = bytes((151,132,148,255))
        self.after = bytearray(self.before)

    def scan(self, before=None, after=None):
        return collar_background_exposure(
            self.before if before is None else before,
            self.after if after is None else after,
            self.bg, width=self.w,height=self.h,
            source_width=self.w,source_height=self.h,roi=(5,5,20,20))

    def test_no_new_background_if_pose_remains_covered(self):
        result = self.scan()
        self.assertEqual(result["newly_exposed_background_pixels"], 0)
        self.assertEqual(collar_gate([result])["status"],"PASS_TECHNICAL_NO_HUMAN_APPROVAL")

    def test_exposed_original_background_only_counts_new_gaps(self):
        for y in range(10, 14):
            for x in range(12, 17):
                i=(y*self.w+x)*4
                self.after[i:i+4] = self.bg[i:i+4]
        result = self.scan()
        self.assertEqual(result["newly_exposed_background_pixels"], 20)
        self.assertEqual(result["pixels_checked"],400)
        self.assertFalse(result["human_visual_approved"])

    def test_rejects_wide_exposed_original_background(self):
        for y in range(7, 19):
            for x in range(8, 20):
                i=(y*self.w+x)*4
                self.after[i:i+4] = self.bg[i:i+4]
        result = self.scan()
        self.assertEqual(result["newly_exposed_background_pixels"], 144)
        self.assertEqual(collar_gate([result])["status"],
                         "BLOCKED_EXPOSED_BACKGROUND_AT_NECK")

    def test_fidelity_tolerance_avoids_h264_noise_false_positive(self):
        for y in range(10, 14):
            for x in range(12, 17):
                i=(y*self.w+x)*4
                self.after[i:i+4] = bytes((130,100,110,255))
        result = self.scan()
        self.assertEqual(result["newly_exposed_background_pixels"], 0)

    def test_invalid_dimensions_and_outside_roi_fail_closed(self):
        with self.assertRaisesRegex(C01CollarError,"FRAME_DIMENSIONS"):
            self.scan(before=bytes(10))
        with self.assertRaisesRegex(C01CollarError,"UNSAFE_ROI"):
            collar_background_exposure(self.before,self.after,self.bg,
                width=32,height=32,source_width=32,source_height=32,roi=(30,30,4,4))

    def test_bad_gate_input_rejected(self):
        with self.assertRaisesRegex(C01CollarError,"GATE_PARAMETERS_INVALID"):
            collar_gate([])
        with self.assertRaisesRegex(C01CollarError,"GATE_PARAMETERS_INVALID"):
            collar_gate([self.scan()],max_new_background_pixels=-1)


if __name__ == "__main__":
    unittest.main()
