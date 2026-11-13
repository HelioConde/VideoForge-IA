"""Testes totalmente offline do pipeline de separacao generativa de cena."""
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

from videoforge import scene_layers as sl


def fixture(*, alpha=False, width=12, height=8, transparent=False):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    mode = 6 if alpha else 2
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # scanline PNG filtro None
        for x in range(width):
            raw.extend([51, 83, 120])
            if alpha:
                raw.append(0 if transparent and x < width // 2 else 255)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, mode, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


class SceneLayersTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        cfg = self.root / "canal" / "otaku-br" / "canal.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text('{"id":"otaku-br"}', encoding="utf-8")
        p = patch.object(sl.proxy, "ROOT", self.root)
        p.start()
        self.addCleanup(p.stop)
        self.source = self.root / "scene.png"
        self.source.write_bytes(fixture())

    def test_png_rgb_and_real_alpha(self):
        d = sl.png_info(fixture())
        self.assertEqual((d["width"], d["height"], d["has_alpha"]), (12, 8, False))
        alpha = sl.png_info(fixture(alpha=True, transparent=True), require_alpha=True)
        self.assertEqual(alpha["alpha_zero_fraction"], .5)
        with self.assertRaises(sl.LayerError):
            sl.png_info(fixture(), require_alpha=True)
        with self.assertRaises(sl.LayerError):
            sl.png_info(fixture(alpha=True), require_alpha=True)
        with self.assertRaises(sl.LayerError):
            sl.png_info(fixture(alpha=True, transparent=True), require_alpha=False)

    def test_png_reject_corrupt_and_trailing_data(self):
        original = fixture()
        corrupted = bytearray(original)
        corrupted[-9] ^= 8
        with self.assertRaises(sl.LayerError):
            sl.png_info(bytes(corrupted))
        with self.assertRaises(sl.LayerError):
            sl.png_info(original + b"extra")

    def test_channel_and_video_isolation(self):
        with self.assertRaises(sl.proxy.ProxyImageError):
            sl.output_dir("gamer", "video-01", "cena-01")
        for video in ("../fora", "/fora", "MAIUSCULA", ""):
            with self.subTest(video=video), self.assertRaises((sl.LayerError, sl.proxy.ProxyImageError)):
                sl.output_dir("otaku-br", video, "cena-01")

    def test_manifest_hash_is_scoped_and_resume_safe(self):
        folder = sl.initialize("otaku-br", "video-001", "cena-01", self.source)
        report = json.loads((folder / "manifest.json").read_text())
        self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertFalse(report["human_visual_approval"])
        self.assertFalse(report["pixel_alignment_verified"])
        with self.assertRaises(sl.LayerError):
            sl.resume("otaku-br", "video-001", "cena-01", folder)  # nao sobrescrever

    def test_fake_edit_includes_reference_image(self):
        folder = sl.initialize("otaku-br", "video-001", "cena-01", self.source)
        calls = []
        def fake(url, route, key, data):
            calls.append((route, data))
            return {"data": [{"b64_json": base64.b64encode(fixture(alpha=True, transparent=True)).decode()}]}
        with patch.object(sl.proxy, "call_proxy", side_effect=fake):
            output = sl.generate_layer(folder, "character-main", "https://proxy.test", "token-not-printed", "gpt-image-2")
        self.assertEqual(calls[0][0], "/v1/images/edits")
        self.assertEqual(calls[0][1]["background"], "transparent")
        self.assertTrue(calls[0][1]["images"][0]["image_url"].startswith("data:image/png;base64,"))
        self.assertTrue(output.is_file())
        record = json.loads((folder / "manifest.json").read_text())["layers"]["character-main"]
        self.assertEqual(record["technical_status"], "verified")
        self.assertEqual(record["z_index"], 20)
        self.assertEqual(record["human_visual_review"], "pending")

    def test_opaque_cutout_is_rejected_not_approved(self):
        folder = sl.initialize("otaku-br", "video-001", "cena-01", self.source)
        with patch.object(sl.proxy, "call_proxy", return_value={"data": [{"b64_json": base64.b64encode(fixture()).decode()}]}):
            with self.assertRaises(sl.LayerError):
                sl.generate_layer(folder, "cape", "https://proxy.test", "hidden", "gpt-image-2")
        record = json.loads((folder / "manifest.json").read_text())["layers"]["cape"]
        self.assertEqual(record["technical_status"], "rejected")

    def test_advanced_requires_basic(self):
        folder = sl.initialize("otaku-br", "video-001", "cena-01", self.source)
        with self.assertRaises(sl.LayerError):
            sl.run_stage(folder, "advanced", "pair", "https://proxy.test", "hidden", "gpt-image-2")


if __name__ == "__main__":
    unittest.main()
