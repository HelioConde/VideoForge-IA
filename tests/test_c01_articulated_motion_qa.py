"""C01 rig-motion QA tests without generated art and without network assets."""
import unittest

from videoforge.directed_rig_qa import c01_actor_motion_pixels


def shot():
    return {
        "id": "C01-P03", "canvas": {"width": 64, "height": 96},
        "camera": {"type": "perspective_3d", "move": "locked",
                   "keyframes": [{"frame": 150, "z": 14, "fovDeg": 30,
                                  "lookAt": [0, 0, 0]}]},
        "nodes": [{"id": f"kael.part-{i}", "bbox": [24,24,8,8]} for i in range(8)]
    }


class C01ActualVideoMotionQATest(unittest.TestCase):
    def test_actor_pixel_motion_measured_without_overlay(self):
        width, height = 64,96
        before = bytearray(width*height*4)
        after = bytearray(before)
        for x,y in ((28,29),(30,30),(0,0)):
            at=(y*width+x)*4
            after[at:at+4] = bytes([90,30,0,255])
        report = c01_actor_motion_pixels(before,after,shot(),width,height)
        self.assertEqual(report["changed_pixels"], 2)
        self.assertEqual(report["source"], "decoded_real_h264_frames")
        self.assertFalse(report["human_visual_review"])

    def test_static_video_does_not_create_motion(self):
        data = bytearray(64*96*4)
        report=c01_actor_motion_pixels(data,data,shot(),64,96)
        self.assertEqual(report["changed_pixels"],0)

    def test_camera_move_rejected_as_fake_rig_motion(self):
        s=shot()
        s["camera"]["move"]="dolly_in"
        with self.assertRaisesRegex(ValueError,"LOCKED_CAMERA"):
            c01_actor_motion_pixels(bytearray(64*96*4),bytearray(64*96*4),s,64,96)

    def test_missing_independent_character_parts_rejected(self):
        s=shot()
        s["nodes"]=[]
        with self.assertRaisesRegex(ValueError,"INDEPENDENT_KAEL_SPRITES"):
            c01_actor_motion_pixels(bytearray(64*96*4),bytearray(64*96*4),s,64,96)

    def test_wrong_output_dimensions_rejected(self):
        with self.assertRaisesRegex(ValueError,"VIDEO_DIMENSIONS"):
            c01_actor_motion_pixels(b"missing",b"missing",shot(),64,96)


if __name__ == "__main__":
    unittest.main()
