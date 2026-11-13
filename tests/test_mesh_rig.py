"""Rig SVG: hashes, RGBA, alinhamento declarado e integracao opt-in."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from videoforge import mesh_rig, proxy_images, remotion_preview as remotion


def _png(width: int, height: int, color: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            alpha = 255 if 4 <= x < width - 4 and 4 <= y < height - 4 else 0
            rows.extend((color, 50, 70, alpha))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(bytes(rows))) +
            chunk(b"IEND", b""))


class MeshRigTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.rig_dir = self.root / "rig"
        self.rig_dir.mkdir()
        self.source_sha = "a" * 64
        hashes = {}
        for i, name in enumerate(mesh_rig.ASSET_NAMES.values()):
            data = _png(32, 48, 60 + i * 15)
            (self.rig_dir / name).write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
        self.manifest = {
            "schema": mesh_rig.SCHEMA,
            "channel": "otaku-br", "video_id": "teste-001", "scene": "cena-01",
            "source_sha256": self.source_sha,
            "canvas": {"width": 32, "height": 48},
            "assets": hashes,
            "neck_pivot": {"x": 16, "y": 18},
            "head_max_deg": 1.6,
            "blink_frames": [40, 132],
            "cape_mesh": {
                "bounds": {"x": 4, "y": 8, "width": 23, "height": 32},
                "columns": 4, "rows": 6, "amplitude_px": 6.0,
            },
            "human_review": {
                "no_duplicate_parts": True,
                "pixel_alignment": True,
                "occlusion_order": True,
            },
        }
        self.write_manifest()

    def write_manifest(self):
        (self.rig_dir / "rig.json").write_text(
            json.dumps(self.manifest), encoding="utf-8")

    def validate(self):
        return mesh_rig.validate_rig_dir(
            self.rig_dir, channel="otaku-br", video_id="teste-001",
            scene="cena-01", source_sha=self.source_sha,
            width=32, height=48, duration_frames=240)

    def test_validated_assets_produce_safe_remotion_props(self):
        rig = self.validate()
        self.assertEqual(rig["schema"], mesh_rig.RIG_SCHEMA)
        self.assertEqual(rig["layers"]["cape"], "vf-scene/rig/cape.png")
        self.assertEqual(rig["blinkFrames"], [40, 132])
        props = remotion.make_props(
            channel="otaku-br", video_id="teste-001", scene="cena-01",
            duration=8, preset="equilibrado", source_sha=self.source_sha, rig=rig)
        self.assertTrue(props["capeOverlayEnabled"])
        self.assertTrue(props["bodyPartRiggingImplemented"])
        self.assertEqual(props["rig"], rig)

    def test_optional_seam_underlay_requires_sha_and_full_canvas(self):
        png=self.rig_dir/"seam-underlay.png"
        data=_png(32,48,27)
        png.write_bytes(data)
        self.manifest["assets"]["seam-underlay.png"]=hashlib.sha256(data).hexdigest()
        self.write_manifest()
        rig=self.validate()
        self.assertEqual(rig["layers"]["seamUnderlay"],"vf-scene/rig/seam-underlay.png")
        png.write_bytes(data+b"corrupted")
        with self.assertRaises(mesh_rig.RigAssetError):
            self.validate()

    def test_fail_closed_on_bad_manifest_and_files(self):
        cases = [
            ("cross channel", lambda: self.manifest.update(channel="gamer")),
            ("source hash", lambda: self.manifest.update(source_sha256="b" * 64)),
            ("missing human review", lambda: self.manifest["human_review"].update(pixel_alignment=False)),
            ("cape bounds", lambda: self.manifest["cape_mesh"]["bounds"].update(x=30)),
            ("head angle", lambda: self.manifest.update(head_max_deg=3.0)),
            ("blinks", lambda: self.manifest.update(blink_frames=[40, 42])),
            ("duplicate hash", lambda: self.manifest["assets"].update({
                "cape.png": self.manifest["assets"]["head-no-eyes.png"]})),
        ]
        original = json.dumps(self.manifest)
        for label, change in cases:
            with self.subTest(label=label):
                self.manifest = json.loads(original)
                change()
                self.write_manifest()
                with self.assertRaises(mesh_rig.RigAssetError):
                    self.validate()
        self.manifest = json.loads(original)
        self.write_manifest()
        with (self.rig_dir / "cape.png").open("ab") as f:
            f.write(b"alterado")
        with self.assertRaises(mesh_rig.RigAssetError):
            self.validate()

    def test_validated_wind_profile_is_optional_and_strict(self):
        self.assertNotIn("wind", self.validate()["capeMesh"])
        wind = {
            "direction": -1, "baseStrength": .85,
            "gustStrength": 1.15, "flutterStrength": .65,
            "tipLagSeconds": .34, "liftStrength": .62,
        }
        self.manifest["cape_mesh"]["wind"] = wind
        self.write_manifest()
        self.assertEqual(self.validate()["capeMesh"]["wind"], wind)
        bad_cases = [
            dict(wind, direction=0),
            dict(wind, direction=2),
            dict(wind, gustStrength=4),
            dict(wind, flutterStrength=float("nan")),
            dict(wind, tipLagSeconds=1),
            dict(wind, liftStrength=-.1),
            dict(wind, unwanted="unsafe"),
        ]
        for bad in bad_cases:
            with self.subTest(bad=bad):
                self.manifest["cape_mesh"]["wind"] = bad
                self.write_manifest()
                with self.assertRaises(mesh_rig.RigAssetError):
                    self.validate()
        self.manifest["cape_mesh"].pop("wind")
        self.write_manifest()
        self.assertNotIn("wind", self.validate()["capeMesh"])

    def test_prepare_with_real_rgba_fixture_does_not_duplicate_legacy_character(self):
        config = self.root / "canal/otaku-br/canal.json"
        config.parent.mkdir(parents=True)
        config.write_text('{"id":"otaku-br"}', encoding="utf-8")
        source = self.root / "input"
        source.mkdir()
        for name in remotion.FILES:
            (source / name).write_bytes(_png(32, 48, 200))
        def fake_ffmpeg(command, **_):
            Path(command[-1]).write_bytes(b"RIFF" + b"\x00" * 256)
            return ""
        manifest = {"source": {"sha256": self.source_sha, "width": 32, "height": 48}}
        with patch.object(proxy_images, "ROOT", self.root), \
             patch.object(remotion.animate_layers, "_trusted_assets", return_value=(source, manifest)), \
             patch.object(remotion.mvp, "_command", side_effect=fake_ffmpeg):
            out = remotion.prepare(source, "otaku-br", "teste-001", "cena-01",
                                  duration=8, preset="equilibrado", rig_dir=self.rig_dir)
        props = json.loads((out / "remotion-props.json").read_text())
        self.assertTrue(props["capeOverlayEnabled"])
        self.assertEqual(props["rig"]["capeMesh"]["columns"], 4)
        public = self.root / "motion-remotion/public/vf-scene"
        self.assertTrue((public / "character-main.png").is_file())  # fallback
        self.assertTrue((public / "rig/cape.png").is_file())
        self.assertTrue((public / "rig/body-no-head-no-cape.png").is_file())
        self.assertFalse((public / "cape.png").exists())  # no legacy overlay

    def test_verify_reports_mesh_rig_without_claiming_visual_approval(self):
        config = self.root / "canal/otaku-br/canal.json"
        config.parent.mkdir(parents=True)
        config.write_text('{"id":"otaku-br"}', encoding="utf-8")
        with patch.object(proxy_images, "ROOT", self.root):
            out = remotion.target_dir("otaku-br", "teste-001", "cena-01")
            out.mkdir(parents=True)
            props = remotion.make_props(
                channel="otaku-br", video_id="teste-001", scene="cena-01",
                duration=8, preset="equilibrado", source_sha=self.source_sha,
                rig=self.validate())
            (out / "remotion-props.json").write_text(json.dumps(props))
            (out / "remotion-teste.mp4").write_bytes(b"0" * 25_000)
            with patch.object(remotion.mvp, "_verify_mp4", return_value={
                "status": "technical_verified", "video_codec": "h264",
                "audio_codec": "aac", "duration_seconds": 8.0,
            }), patch.object(remotion.animate_layers, "_frame_md5",
                             side_effect=["MD5=a", "MD5=b"]):
                qa = remotion.verify("otaku-br", "teste-001", "cena-01")
        self.assertTrue(qa["cape_overlay_enabled"])
        self.assertTrue(qa["body_part_rigging_implemented"])
        self.assertEqual(qa["visual_review"], "pending")
        self.assertFalse(qa["publishable"])


if __name__ == "__main__":
    unittest.main()
