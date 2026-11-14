import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from videoforge.directed_rig_qa import neutral_review, verify_render


class DirectedRigQaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.props = {"schema": "videoforge/directed-rig-preview/v1",
                      "mode": "technical_draft", "publishable": False,
                      "humanVisualReview": False, "width": 20, "height": 120,
                      "fps": 30, "durationFrames": 90, "channel": "a",
                      "videoId": "v", "warnings": ["underlays missing"]}
        self.props_path = self.output / "props.json"
        self.save_props()
        for name in ("directed-rig-preview.mp4", "frame-0.png", "frame-30.png", "frame-repeat.png"):
            (self.output / name).write_bytes(b"fixture")
        self.stream = {"codec_type": "video", "codec_name": "h264", "pix_fmt": "yuv420p",
                       "width": 20, "height": 120, "r_frame_rate": "30/1", "nb_frames": "90"}

    def save_props(self):
        self.props_path.write_text(json.dumps(self.props), encoding="utf-8")

    def verify(self, image_reader, video_reader=None):
        probe = SimpleNamespace(stdout=json.dumps({"streams": [self.stream]}))
        if video_reader is None:
            video_reader = lambda path, frame, w, h: bytearray([0 if frame == 0 else 32] * w * h * 4)
        with patch("videoforge.directed_rig_qa.subprocess.run", return_value=probe), \
                patch("videoforge.directed_rig_qa._image", side_effect=image_reader), \
                patch("videoforge.directed_rig_qa._video_frame", side_effect=video_reader):
            return verify_render(self.props_path, self.output)

    def test_motion_and_repeat_are_technical_evidence_only(self):
        report = self.verify(lambda path, w, h: bytearray([0 if path.name == "frame-0.png" else 1] * w * h * 4))
        self.assertGreater(report["changedArtPixelsAtFrame"]["pixels"], 50)
        for flag in ("humanVisualReview", "publishable", "rigProductionReady", "videoOficialDoPrograma"):
            self.assertIs(report[flag], False)
        self.assertFalse(report["audioPresent"])
        self.assertIn("directed-rig-preview.mp4", report["sha256"])

    def test_changing_frame_label_does_not_prove_animation(self):
        def image_reader(path, w, h):
            pixels = bytearray(w * h * 4)
            if path.name != "frame-0.png":
                pixels[-w * 10 * 4:] = b"\xff" * (w * 10 * 4)
            return pixels
        with self.assertRaisesRegex(ValueError, "NO_ART_MOTION"):
            self.verify(image_reader)

    def test_repeated_frame_and_format_must_match(self):
        (self.output / "frame-repeat.png").write_bytes(b"different")
        with self.assertRaisesRegex(ValueError, "NONDETERMINISTIC"):
            self.verify(lambda *args: bytearray())

    def test_moving_stills_do_not_validate_a_static_mp4(self):
        with self.assertRaisesRegex(ValueError, "NO_MP4_ART_MOTION"):
            self.verify(
                lambda path, w, h: bytearray([0 if path.name == "frame-0.png" else 1] * w * h * 4),
                lambda path, frame, w, h: bytearray(w * h * 4))
        self.stream["nb_frames"] = "89"
        with self.assertRaisesRegex(ValueError, "FORMAT_MISMATCH"):
            self.verify(lambda *args: bytearray())

    def test_qa_cannot_promote_a_draft(self):
        self.props["publishable"] = True
        self.save_props()
        with self.assertRaisesRegex(ValueError, "DRAFT_FLAGS_REQUIRED"):
            verify_render(self.props_path, self.output)

    def test_neutral_comparison_measures_real_pixel_difference(self):
        binding = {"shots": {"S": {"canvas": {"width": 2, "height": 2},
                    "sourceMother": {"file": "mother.png"}, "background": {"file": "background.png"},
                    "nodes": [{"file": "part.png", "bbox": [0, 0, 1, 1], "z": 0}]}}}
        path = self.output / "bindings.json"
        path.write_text(json.dumps(binding), encoding="utf-8")
        def pixels(path, w, h):
            result = bytearray([0, 0, 0, 255] * 4)
            if path.name == "part.png":
                result[:4] = bytes([90, 30, 0, 255])
            return result
        with patch("videoforge.directed_rig_qa._image", side_effect=pixels), \
                patch("videoforge.directed_rig_qa._write_png"):
            report = neutral_review(path, "S", self.output)
        self.assertEqual(report["changedPixels"], 1)
        self.assertEqual(report["meanAbsoluteRgbError"], 10)
        self.assertFalse(report["pixelExactRecomposition"])
        self.assertFalse(report["humanVisualReview"])


if __name__ == "__main__":
    unittest.main()
