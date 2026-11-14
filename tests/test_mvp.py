"""MVP contracts and real FFmpeg smoke test (no AI or YouTube)."""
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from videoforge.mvp import VideoForgeError, _load_manifest, _compose, smoke

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


    def test_manifest_accepts_more_than_24_scenes_without_fixed_ceiling(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "video.json"
            manifest.write_text(json.dumps({
                "schema": "videoforge/mvp/v1",
                "channel": "otaku-br", "youtube_upload": False,
                "scenes": [{"image": f"img-{i:03d}.png",
                            "audio": f"voice-{i:03d}.wav", "caption": f"Cena {i}"}
                           for i in range(32)],
            }), encoding="utf-8")
            with patch("videoforge.mvp._safe_asset",
                       side_effect=lambda folder, name, allowed: folder / name):
                meta, scenes = _load_manifest(manifest)
            self.assertEqual(len(scenes), 32)
            self.assertEqual(len(meta["scenes"]), 32)

    def test_empty_manifest_rejected_not_one_scene(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "video.json"
            manifest.write_text(json.dumps({
                "schema": "videoforge/mvp/v1",
                "channel": "otaku-br", "youtube_upload": False,
                "scenes": [],
            }), encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError, "SCENE_COUNT_INVALID"):
                _load_manifest(manifest)

    def test_compose_accepts_25_scenes_when_duration_is_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "render.mp4"
            scenes = [{"audio": Path(folder) / f"a{i}.wav",
                       "image": Path(folder) / f"i{i}.png",
                       "caption": f"Frame {i}"} for i in range(25)]
            fake_info = {"format": {"duration": "4.0"},
                         "streams": [{"codec_type": "audio"}]}
            def fake_cmd(args, cwd=None, **kwargs):
                # Simula somente a saída FFmpeg sem codificar 25 clipes no teste.
                (cwd / "combined.mp4").write_bytes(b"mocked-ci-video")
                return ""
            with patch("videoforge.mvp._require_tools"), \
                 patch("videoforge.mvp._media_info", return_value=fake_info), \
                 patch("videoforge.mvp._command", side_effect=fake_cmd), \
                 patch("videoforge.mvp._render_scene"), \
                 patch("videoforge.mvp._verify_mp4",
                       return_value={"status": "technical_verified"}):
                qa = _compose(scenes, output, minimum=90, maximum=180,
                              kind="test_without_25_scene_ceiling")
            self.assertEqual(qa["scenes"], 25)
            self.assertTrue(output.is_file())

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
