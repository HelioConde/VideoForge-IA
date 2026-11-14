"""Regression: eyelid overlays may never paint across original hair."""
import unittest
from videoforge.blink_hair_occlusion import (
    _hair_color, eye_weight, SCENE_01_EYES,
)

class BlinkHairOcclusionTests(unittest.TestCase):
    def test_eyelid_alpha_confined_to_both_eyes(self):
        self.assertGreater(eye_weight(421,1230),.99)
        self.assertGreater(eye_weight(611,1230),.99)
        for x,y in ((500,1000),(500,1100),(520,1330),(100,1230),(800,1230)):
            self.assertEqual(eye_weight(x,y),0,(x,y))
        self.assertEqual(len(SCENE_01_EYES),2)

    def test_hair_pixels_different_from_face_skin(self):
        self.assertTrue(_hair_color(245,152,141,254))
        self.assertTrue(_hair_color(239,153,140,254))
        self.assertFalse(_hair_color(254,203,182,254))
        self.assertFalse(_hair_color(255,220,198,254))
        self.assertFalse(_hair_color(245,152,141,0))

    def test_eyelid_alpha_feather_not_hard_rectangle(self):
        center=eye_weight(421,1230)
        border=eye_weight(495,1230)
        outside=eye_weight(560,1230)
        self.assertGreater(center,border)
        self.assertGreater(border,outside)
        self.assertEqual(outside,0)

if __name__=="__main__":
    unittest.main()
