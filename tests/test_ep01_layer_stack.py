"""Regressão: bainha visível à frente da roupa e atrás das duas mãos."""
import unittest
from PIL import ImageChops

from videoforge.ep01_layer_stack import (
    read_layers, compose, sheath_contact_region, measure,
    REQUIRED_ORDER, REJECTED_ORDER,
)
from videoforge.errors import VideoForgeError


class LayerOrderTests(unittest.TestCase):
    def test_explicit_depth_order(self):
        self.assertEqual(REQUIRED_ORDER,(
            "background","body","sheath","sword","upper_hand","lower_hand"))
        self.assertLess(REQUIRED_ORDER.index("body"),REQUIRED_ORDER.index("sheath"))
        self.assertGreater(REQUIRED_ORDER.index("lower_hand"),REQUIRED_ORDER.index("sheath"))
        self.assertGreater(REQUIRED_ORDER.index("upper_hand"),REQUIRED_ORDER.index("sword"))

    def test_sheath_is_placed_above_clothing_in_visible_contact_region(self):
        mother,old,fixed,report=measure()
        self.assertEqual(mother.size,fixed.size)
        self.assertGreater(report["sheath_coat_overlap_pixels_exact"],0)
        self.assertTrue(report["z_order_alone_not_proof_of_fix"])
        self.assertEqual(report["rejected_legacy_offsets"][0],[0,300])
        self.assertTrue(report["sheath_above_coat"])
        self.assertTrue(report["gloves_foreground"])
        self.assertFalse(report["automatic_visual_approval"])
        self.assertFalse(report["rig_authorized"])
        self.assertFalse(report["youtube_uploaded"])
        self.assertEqual(report["provider_calls"],0)
        self.assertGreaterEqual(report["old_mean_rgb_difference"],0)
        self.assertGreaterEqual(report["corrected_mean_rgb_difference"],0)

    def test_a_wrong_order_is_not_executable(self):
        _,layers,_=read_layers()
        with self.assertRaisesRegex(VideoForgeError,"EP01_STACK_UNKNOWN_ORDER"):
            compose(layers,("background","sword","body","sheath","upper_hand","lower_hand"))

    def test_same_original_pixel_and_no_pixel_stretch(self):
        mother,layers,proof=read_layers()
        self.assertEqual(len(proof),6)
        self.assertTrue(all(x.size==mother.size for x in layers.values()))
        self.assertGreater(sheath_contact_region(layers).histogram()[255],0)


if __name__=="__main__":
    unittest.main()
