"""9:16 close protection maths; verifies geometry only, no image creation."""
from __future__ import annotations

import unittest

from videoforge.cinematic_frame_fit import (
    cover_viewport,validate_focal_box
)
from videoforge.errors import VideoForgeError

class FrameFitTests(unittest.TestCase):
    def test_native_941x1672_is_nearly_exact_9_by_16_without_stretch(self):
        f=cover_viewport((941,1672))
        self.assertAlmostEqual(f["cropLeftPx"],0.25,places=5)
        self.assertAlmostEqual(f["cropRightPx"],0.25,places=5)
        self.assertAlmostEqual(f["cropTopPx"],0.0,places=5)
        self.assertAlmostEqual(f["cropBottomPx"],0.0,places=5)
        self.assertFalse(f["nonUniformStretch"])
        self.assertTrue(validate_focal_box((941,1672),[10,350,45,80])[
            "focalVisibleAfter9x16Cover"
        ])

    def test_legacy_1024x1536_crops_80_pixels_from_each_side(self):
        f=cover_viewport((1024,1536))
        self.assertAlmostEqual(f["cropLeftPx"],80,places=5)
        self.assertAlmostEqual(f["cropRightPx"],80,places=5)
        self.assertEqual(f["cropTopPx"],0)
        with self.assertRaisesRegex(VideoForgeError,"FOCAL_POINT_CLIPPED"):
            validate_focal_box((1024,1536),[10,350,45,80])
        self.assertTrue(validate_focal_box((1024,1536),[120,350,45,80])[
            "focalVisibleAfter9x16Cover"
        ])

    def test_borderline_focal_boxes_and_wrong_dimensions_rejected(self):
        for bbox in (
            [0,350,45,80],[920,350,20,80],
            [-1,10,20,20],[30,30,0,30],
            [941,100,1,5],[10.1,100,30,30]
        ):
            with self.subTest(bbox=bbox):
                with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_FOCAL"):
                    validate_focal_box((941,1672),bbox)
        for invalid in ((0,1672),(941,-1),(941.0,1672),(True,1672)):
            with self.subTest(source=invalid):
                with self.assertRaisesRegex(VideoForgeError,"DIMENSIONS_INVALID"):
                    cover_viewport(invalid)

    def test_close_must_be_bounded_by_its_native_frame_not_output_pixels(self):
        f=validate_focal_box((941,1672),[120,400,320,180])
        self.assertEqual(f["nativeCanvas"],[941,1672])
        self.assertEqual(f["focalBbox"],[120,400,320,180])

if __name__=="__main__":
    unittest.main()
