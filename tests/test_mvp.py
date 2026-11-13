"""MVP contracts and real FFmpeg smoke test (no AI or YouTube)."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from videoforge.mvp import VideoForgeError, _load_manifest, smoke

ROOT = Path(__file__).resolve().parents[1]


class MvpTests(unittest.TestCase):
    def test_missing_media_blocks_before_render(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "video.json"
            manifest.write_text(json.dumps({
                "schema": "videoforge/mvp/v1",
                "channel": "otaku-br",
                "youtube_upload": False,
                "scenes": [{"image": "missing.png", "audio": "missing.wav", "caption": "Texto"}] * 3,
            }), encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError, "ASSET_MISSING"):
                _load_manifest(manifest)

    def test_path_traversal_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "video.json"
            path.write_text(json.dumps({
                "schema": "videoforge/mvp/v1",
                "channel": "otaku-br",
                "youtube_upload": False,
                "scenes": [{"image": "../photo.png", "audio": "voice.wav", "caption": "Texto"}] * 3,
            }), encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError, "ASSET_PATH_INVALID"):
                _load_manifest(path)

    def test_upload_cannot_be_enabled(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "video.json"
            path.write_text(json.dumps({
                "schema": "videoforge/mvp/v1",
                "channel": "otaku-br",
                "youtube_upload": True,
                "scenes": [{"image": "a.png", "audio": "b.wav", "caption": "Texto"}] * 3,
            }), encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError, "YOUTUBE_UPLOAD_MUST_BE_DISABLED"):
                _load_manifest(path)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg unavailable")
    def test_real_smoke_mp4_has_video_audio_and_qa(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "smoke.mp4"
            result = smoke(target)
            self.assertTrue(target.exists())
            self.assertGreater(target.stat().st_size, 10000)
            self.assertEqual(result["status"], "technical_verified")
            self.assertEqual(result["kind"], "synthetic_smoke_not_production")
            self.assertEqual(result["scenes"], 3)
            self.assertFalse(result["youtube_uploaded"])
            qa = json.loads(target.with_suffix(".qa.json").read_text())
            self.assertEqual(qa["width"], 1080)
            self.assertEqual(qa["height"], 1920)
            with self.assertRaisesRegex(VideoForgeError, "OUTPUT_ALREADY_EXISTS"):
                smoke(target)


if __name__ == "__main__":
    unittest.main()
