"""Ornament segmentation safety: original brown/gold, not Loid/Yor."""
import unittest
try:
    import numpy as np
    import cv2
except ImportError:
    np = cv2 = None

from videoforge.errors import VideoForgeError
from videoforge.rig_three_anya_ornaments import (
    _component_mask, ORNAMENT_POLYGONS, H, W
)


@unittest.skipUnless(np is not None and cv2 is not None,
                     "opencv/numpy run on the specialized rig-art runner")
class OrnamentSourceTests(unittest.TestCase):
    def fixture(self):
        image=np.zeros((H,W,4),dtype=np.uint8)
        image[:]=[53,52,55,253]  # Loid neutral-grey jacket
        return image

    def test_left_horn_picks_brown_gold_and_skips_loid(self):
        art=self.fixture()
        polygon=np.asarray(ORNAMENT_POLYGONS["left"],np.int32)
        cv2.fillPoly(art,[polygon],(62,47,40,253))
        # Place gold within the accessory polygon only.
        cv2.rectangle(art,(308,1081),(328,1130),(252,193,90,253),-1)
        mask,count,gold=_component_mask(art,polygon,cv2,np)
        self.assertGreater(count,4700)
        self.assertGreater(gold,1000)
        self.assertEqual(int(mask[1090,265]),0)
        self.assertEqual(int(mask[1110,319]),1)

    def test_invalid_foreign_colours_cannot_fake_an_ornament(self):
        art=self.fixture()
        poly=np.asarray(ORNAMENT_POLYGONS["right"],np.int32)
        cv2.fillPoly(art,[poly],(110,36,42,253)) # Yor red blouse
        with self.assertRaisesRegex(VideoForgeError,"ORNAMENT_NOT_FOUND"):
            _component_mask(art,poly,cv2,np)


if __name__=="__main__":
    unittest.main()
