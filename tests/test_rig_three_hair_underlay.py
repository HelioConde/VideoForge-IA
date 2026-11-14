"""Fail-closed invariant tests for Anya's reconstructed hidden hair."""
import unittest

try:
    import cv2
    import numpy as np
except ImportError:  # The generic MVP runner is intentionally free of OpenCV.
    cv2 = np = None

from videoforge.errors import VideoForgeError
from videoforge.rig_three_hair_underlay import (
    H, W, pink_shoulder_mask, reconstruct,
)


@unittest.skipUnless(np is not None and cv2 is not None,
                     "art-preparation dependencies only on specialized rig runner")
class HairUnderlayTests(unittest.TestCase):
    def scene(self):
        zero=lambda:np.zeros((H,W,4),dtype=np.uint8)
        body,head,closed,hand,left,right,source=(
            zero(),zero(),zero(),zero(),zero(),zero(),zero())
        # A small neutral head silhouette and two real, separate moving locks.
        head[1120:1390,250:760]=[235,157,142,255]
        closed[:]=head
        closed[1150:1170,490:515,:3]=[185,93,73]
        left[1300:1380,300:400]=head[1300:1380,300:400]
        right[1300:1380,620:720]=head[1300:1380,620:720]
        body[1455:1501,400:650]=[58,42,36,255]
        # Two hair islands accidentally left on the original uniform.
        body[1463:1473,422:432]=[227,119,123,255]
        body[1465:1480,582:602]=[230,125,126,255]
        source[:]=body
        source[head[:,:,3]>0]=head[head[:,:,3]>0]
        return body,head,closed,hand,left,right,source

    def test_original_shoulder_pixels_are_transferred_not_repainted(self):
        body,head,closed,hand,left,right,source=self.scene()
        result=reconstruct(body,head,closed,hand,left,right,source,cv2,np)
        self.assertGreater(result["fragment_left"],60)
        self.assertGreater(result["fragment_right"],300)
        self.assertGreater(result["underlay_pixels"],15000)
        self.assertTrue(result["approved_blink_preserved"])
        self.assertEqual(tuple(result["hair-left"][1468,425]),
                         tuple(source[1468,425]))
        self.assertEqual(tuple(result["hair-right"][1470,590]),
                         tuple(source[1470,590]))
        # Body alpha retained for newly concealed shoulder underlays.
        np.testing.assert_array_equal(result["body"][:,:,3],body[:,:,3])
        # No outside-mask edits to the approved central face.
        np.testing.assert_array_equal(
            result["head-open"][1150:1170,490:515],
            head[1150:1170,490:515])

    def test_original_source_mismatch_is_blocking(self):
        body,head,closed,hand,left,right,source=self.scene()
        source[1470,590,:3]=[1,2,3]
        with self.assertRaisesRegex(VideoForgeError,
                                    "FRAGMENT_SOURCE_RGB_DIFFERENT"):
            reconstruct(body,head,closed,hand,left,right,source,cv2,np)

    def test_wrong_mask_or_canvas_is_blocking(self):
        body,head,closed,hand,left,right,source=self.scene()
        body[1463:1480,420:635]=[55,45,40,255]
        with self.assertRaisesRegex(VideoForgeError,
                                    "UNSAFE_PINK_BODY_FRAGMENT"):
            pink_shoulder_mask(body,head,hand,left,right,cv2,np)
        with self.assertRaisesRegex(VideoForgeError,
                                    "UNDERLAY_CANVAS_INVALID"):
            reconstruct(body[:-1],head,closed,hand,left,right,
                        source,cv2,np)


if __name__=="__main__":
    unittest.main()
