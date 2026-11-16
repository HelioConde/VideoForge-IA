"""Reusable rendering for five channels: real media only, no phantom official video."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from videoforge.errors import VideoForgeError
from videoforge.mvp import _load_manifest
from videoforge.paths import CHANNEL_IDS

class MultichannelRenderTests(unittest.TestCase):
    def test_accepted_channels_with_supplied_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            for channel in sorted(CHANNEL_IDS):
                with self.subTest(channel=channel):
                    folder=Path(tmp)/channel
                    folder.mkdir()
                    manifest=folder/"video.json"
                    manifest.write_text(json.dumps({
                        "schema":"videoforge/mvp/v1",
                        "channel":channel,"modelo":"imagem-estatica",
                        "youtube_upload":False,
                        "scenes":[{"image":"cena.png","audio":"cena.wav",
                                   "caption":"Narrativa original"}],
                    }),encoding="utf-8")
                    with patch("videoforge.mvp._safe_asset",
                               side_effect=lambda base,name,extensions: base/name):
                        loaded,scenes=_load_manifest(manifest)
                    self.assertEqual(loaded["channel"],channel)
                    self.assertEqual(len(scenes),1)
    def test_unknown_channel_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"video.json"
            p.write_text(json.dumps({
                "schema":"videoforge/mvp/v1","channel":"invalid",
                "youtube_upload":False,"scenes":[]}))
            with self.assertRaisesRegex(VideoForgeError,"MVP_CHANNEL_NOT_SUPPORTED"):
                _load_manifest(p)
    def test_media_required_and_upload_stays_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"video.json"
            p.write_text(json.dumps({
                "schema":"videoforge/mvp/v1","channel":"gamer",
                "youtube_upload":False,
                "scenes":[{"image":"does-not-exist.png",
                           "audio":"does-not-exist.wav","caption":"Teste"}]}))
            with self.assertRaisesRegex(VideoForgeError,"ASSET_MISSING"):
                _load_manifest(p)
            data=json.loads(p.read_text())
            data["youtube_upload"]=True
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(VideoForgeError,"YOUTUBE_UPLOAD_MUST_BE_DISABLED"):
                _load_manifest(p)
if __name__=="__main__":
    unittest.main()
