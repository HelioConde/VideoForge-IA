"""Testes sem IA ou Node da integracao de PNGs reais com o Remotion antigo."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videoforge import proxy_images, remotion_preview as r


class RemotionPreviewTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        config = self.root / "canal/otaku-br/canal.json"
        config.parent.mkdir(parents=True)
        config.write_text('{"id":"otaku-br"}', encoding="utf-8")
        p = patch.object(proxy_images, "ROOT", self.root)
        p.start()
        self.addCleanup(p.stop)

    def test_legacy_props_only_reference_real_layers(self):
        props = r.make_props(
            channel="otaku-br", video_id="teste-001", scene="cena-01",
            duration=8, preset="equilibrado", source_sha="1"*64,
        )
        self.assertEqual(props["durationFrames"], 240)
        self.assertEqual(props["animationEngine"], "remotion")
        self.assertEqual(props["preset"], "equilibrado")
        self.assertFalse(props["capeOverlayEnabled"])
        self.assertEqual(props["character"], "vf-scene/character-main.png")
        self.assertNotIn("cape.png", json.dumps(props))
        self.assertIn("AutoEditorVideo/motion-remotion/src/character-idle.ts",
                      props["motionAuthors"])

    def test_invalid_channel_duration_preset_hash(self):
        base = dict(channel="otaku-br",video_id="teste-001",scene="cena-01",
                    duration=8,preset="equilibrado",source_sha="1"*64)
        for key,value in [("channel","invalid"),("video_id","../fora"),
                          ("duration",20),("preset","inexistente"),
                          ("source_sha","falso")]:
            with self.subTest(key=key):
                arg = dict(base)
                arg[key] = value
                with self.assertRaises((ValueError, r.proxy_images.ProxyImageError)):
                    r.make_props(**arg)

    def test_prepare_copies_just_three_verified_layers(self):
        source = self.root / "previous-artifact"
        source.mkdir()
        for name in r.FILES + ("cape.png","manifest.json"):
            (source / name).write_bytes(("asset-"+name).encode("utf-8"))
        incoming = {
            "source": {"sha256": "a"*64, "width": 1024, "height": 1536}
        }
        def silence_ffmpeg(command, **kwargs):
            Path(command[-1]).write_bytes(b"RIFF"+b"\x00"*200)
            return ""
        with patch.object(r.animate_layers, "_trusted_assets", return_value=(source,incoming)), \
             patch.object(r.mvp, "_command", side_effect=silence_ffmpeg):
            output = r.prepare(source, "otaku-br", "teste-001", "cena-01",
                               duration=8, preset="equilibrado")
        self.assertTrue((output / "remotion-props.json").is_file())
        public = self.root / "motion-remotion/public/vf-scene"
        self.assertTrue((public / "background.png").is_file())
        self.assertTrue((public / "character-main.png").is_file())
        self.assertTrue((public / "foreground-roof.png").is_file())
        self.assertFalse((public / "cape.png").exists())
        self.assertTrue((public / "silence.wav").is_file())
        with self.assertRaises(r.RemotionPreviewError):
            r.prepare(source, "otaku-br", "teste-001", "cena-01",
                      duration=8,preset="equilibrado")

    def test_verify_rejects_missing_or_unchanged_frames(self):
        props = r.make_props(
            channel="otaku-br",video_id="teste-001",scene="cena-01",
            duration=8,preset="equilibrado",source_sha="0"*64,
        )
        output = r.target_dir("otaku-br","teste-001","cena-01")
        output.mkdir(parents=True)
        (output / "remotion-props.json").write_text(json.dumps(props))
        with self.assertRaises(r.RemotionPreviewError):
            r.verify("otaku-br","teste-001","cena-01")
        (output / "remotion-teste.mp4").write_bytes(b"0"*25_000)
        with patch.object(r.mvp,"_verify_mp4",return_value={
                "status":"technical_verified",
                "video_codec":"h264", "audio_codec":"aac",
                "duration_seconds":8.0,
             }), patch.object(r.animate_layers, "_frame_md5",return_value="MD5=abc"):
            with self.assertRaises(r.RemotionPreviewError):
                r.verify("otaku-br","teste-001","cena-01")
        with patch.object(r.mvp,"_verify_mp4",return_value={
                "status":"technical_verified",
                "video_codec":"h264", "audio_codec":"aac",
                "duration_seconds":8.0,
             }), patch.object(r.animate_layers, "_frame_md5",
                              side_effect=["MD5=a1","MD5=b2"]):
            report = r.verify("otaku-br","teste-001","cena-01")
        self.assertTrue(report["motion_detected"])
        self.assertFalse(report["cape_overlay_enabled"])
        self.assertFalse(report["youtube_uploaded"])
        self.assertTrue((output / "remotion-teste.qa.json").is_file())


if __name__ == "__main__":
    unittest.main()
