"""Gold interior motion cannot be faked by movement of pink hair."""
import tempfile
import unittest
from pathlib import Path

from videoforge.errors import VideoForgeError
from videoforge.rig_three_ornament_render_qa import stable_gold_motion


class AnyaOrnamentMotionTest(unittest.TestCase):
    def make(self,folder,side,moved:int):
        # 24x36 raw RGB; old and new must be distinguishable by the actual
        # yellow source pixels, not surrounding background or head bobbing.
        src=bytearray([220,170,70]*864)
        next_=bytearray(src)
        for i in range(moved):
            next_[3*i:3*i+3]=bytes((45,40,48))
        (folder/f"ornament-{side}-stable-0.rgb").write_bytes(src)
        (folder/f"ornament-{side}-stable-30.rgb").write_bytes(next_)

    def test_moves_original_gold_internally(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            for side in ("left","right"):
                self.make(folder,side,850)
                result=stable_gold_motion(folder,side)
                self.assertEqual(result["interior_source_patch_pixels_changed"],850)
                self.assertTrue(result["ornament_not_static"])

    def test_old_static_ornament_must_fail_even_if_hair_moves(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            self.make(folder,"left",0)
            with self.assertRaisesRegex(VideoForgeError,"STILL_STATIC_left"):
                stable_gold_motion(folder,"left")
            self.make(folder,"right",57)
            with self.assertRaisesRegex(VideoForgeError,"STILL_STATIC_right"):
                stable_gold_motion(folder,"right")

    def test_partial_source_movement_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            self.make(folder,"left",400)
            with self.assertRaisesRegex(VideoForgeError,"STILL_STATIC_left"):
                stable_gold_motion(folder,"left")


if __name__=="__main__":
    unittest.main()
