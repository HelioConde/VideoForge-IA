"""Protect no-crop animation and time-aligned captions in the main compositor."""
import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from videoforge.mvp import _drawtext_filter, _load_manifest, VideoForgeError


class FemaleMotionRenderTests(unittest.TestCase):
    def test_subtitles_replace_fixed_card_and_pan_without_cropping(self):
        filt=_drawtext_filter("caption-001.txt",
                             subtitle_filename="subtitle-001.srt",
                             motion="cinematic-pan")
        self.assertIn("subtitles=filename=subtitle-001.srt",filt)
        self.assertNotIn("textfile=caption-001.txt",filt)
        self.assertIn("scale=1024:1536",filt)
        self.assertIn("8*sin(t*0.45)",filt)
        self.assertIn("boxblur=28:2",filt)

    def test_legacy_static_render_untouched_when_no_subtitles(self):
        filt=_drawtext_filter("caption-001.txt")
        self.assertIn("textfile=caption-001.txt",filt)
        self.assertNotIn("subtitles=",filt)
        self.assertNotIn("8*sin(",filt)

    def test_manifest_requires_existing_srt_if_female_motion_enabled(self):
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/"video.json"
            f.write_text(json.dumps({
                "schema":"videoforge/mvp/v1",
                "channel":"otaku-br","youtube_upload":False,
                "scenes":[{"image":"a.png","audio":"b.wav",
                           "caption":"Teste","subtitles":"legendas/1.srt",
                           "motion":"cinematic-pan"}]
            }),encoding="utf-8")
            def fake_asset(path,name,allowed):
                if name.endswith(".srt"):
                    raise VideoForgeError("ASSET_MISSING_OR_TOO_LARGE")
                return path/name
            with patch("videoforge.mvp._safe_asset",side_effect=fake_asset):
                with self.assertRaisesRegex(VideoForgeError,"ASSET_MISSING"):
                    _load_manifest(f)

if __name__=="__main__":
    unittest.main()
