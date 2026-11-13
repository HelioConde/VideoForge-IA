"""Verificacoes offline de montagem de movimento por camadas."""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from videoforge import animate_layers, scene_layers, proxy_images


def png(*, alpha=False, width=24, height=36):
    def chunk(tag, value):
        return struct.pack(">I", len(value)) + tag + value + struct.pack(">I", zlib.crc32(tag + value) & 0xffffffff)
    mode = 6 if alpha else 2
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            pixels.extend([45, 76, 98])
            if alpha:
                pixels.append(0 if x < width // 2 else 255)
    hdr = struct.pack(">IIBBBBB", width, height, 8, mode, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", hdr) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


class AnimationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        cfg = self.root / "canal/otaku-br/canal.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text('{"id":"otaku-br"}', encoding="utf-8")
        root_patch = patch.object(proxy_images, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.src = self.root / "original.png"
        self.src.write_bytes(png())

    def test_filter_uses_three_independent_motions(self):
        s = animate_layers.filter_graph(1024, 1536, 8, "cinematic")
        self.assertIn("[background][character]overlay", s)
        self.assertIn("[scene][foreground]overlay", s)
        self.assertIn("sin(n/29)", s)
        self.assertIn("sin(t*1.75)", s)
        self.assertIn("crop=1080:1920", s)
        self.assertNotIn("cape.png", s)
        self.assertNotIn("drawtext", s)

    def test_bad_duration_or_preset_is_blocked(self):
        for duration in (3, 13):
            with self.subTest(duration=duration), self.assertRaises(animate_layers.AnimationError):
                animate_layers.filter_graph(1024, 1536, duration, "cinematic")
        with self.assertRaises(animate_layers.AnimationError):
            animate_layers.filter_graph(1024, 1536, 8, "unknown")

    def _make_artifact(self):
        folder = scene_layers.initialize("otaku-br", "video-001", "cena-01", self.src)
        records = {}
        for name, transparent in (("background", False), ("character-main", True), ("foreground-roof", True)):
            payload = png(alpha=transparent)
            (folder / (name + ".png")).write_bytes(payload)
            records[name] = {
                "file": name + ".png", "sha256": hashlib.sha256(payload).hexdigest(),
                "technical_status": "verified",
            }
        manifest = json.loads((folder / "manifest.json").read_text())
        manifest["layers"] = records
        (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return folder

    def test_trusted_assets_verify_hashes_and_alpha(self):
        incoming = self._make_artifact()
        other = self.root / "other"
        cfg = other / "canal/otaku-br/canal.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text('{"id":"otaku-br"}', encoding="utf-8")
        with patch.object(proxy_images, "ROOT", other):
            folder, report = animate_layers._trusted_assets(incoming, "otaku-br", "video-001", "cena-01")
            self.assertTrue((folder / "background.png").is_file())
            self.assertFalse(report["human_visual_approval"])
            self.assertIn("foreground-roof", report["layers"])

    def test_tampered_artifact_fails_closed(self):
        incoming = self._make_artifact()
        (incoming / "foreground-roof.png").write_bytes(png())
        second = self.root / "other"
        cfg = second / "canal/otaku-br/canal.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text('{"id":"otaku-br"}')
        with patch.object(proxy_images, "ROOT", second):
            with self.assertRaises(scene_layers.LayerError):
                animate_layers._trusted_assets(incoming, "otaku-br", "video-001", "cena-01")

    def test_unknown_channel_and_missing_inputs_rejected(self):
        with self.assertRaises(proxy_images.ProxyImageError):
            scene_layers.output_dir("other", "video-001", "cena-01")
        with self.assertRaises(animate_layers.AnimationError):
            animate_layers.render_preview(self.root, "otaku-br", "video-001", "cena-01", duration=25)


if __name__ == "__main__":
    unittest.main()
