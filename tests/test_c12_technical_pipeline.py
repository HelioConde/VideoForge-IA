"""Fail-closed tests for importing the existing C12 technical mesh package.

All PNG bytes in these tests are tiny synthetic fixtures created in a temporary
directory. They are not shot artwork and are never copied into the repository.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import stat
import struct
import tempfile
import unittest
import warnings
import zlib
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo

from videoforge import c12_technical_pipeline as c12
from videoforge.errors import VideoForgeError
from videoforge.scene_layers import LayerError


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))


def _png(width: int, height: int, *, rgba: bool, color: int) -> bytes:
    """Small valid PNG; RGBA fixtures contain transparent and visible pixels."""
    channels, color_type = (4, 6) if rgba else (3, 2)
    row = bytearray()
    for x in range(width):
        row.extend(((color + x) % 255, (color + 31) % 255, (color + 67) % 255))
        if rgba:
            row.append(0 if x == 0 else 255)
    raw = b"".join(b"\0" + bytes(row) for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(raw))
            + _chunk(b"IEND", b""))


def _asset(asset_id: str, shot: str, role: str, data: bytes,
           dimensions: tuple[int, int], *, bbox=None) -> dict:
    item = {"id": asset_id, "shot": shot, "role": role,
            "sha256": hashlib.sha256(data).hexdigest(),
            "dimensions": list(dimensions)}
    if role == "sprite":
        item.update({"bbox": bbox or [0, 0, *dimensions], "z": 10,
                     "mesh": {"kind": "cape", "columns": 2, "rows": 2,
                              "pinnedRows": [0], "amplitudePx": 1.0}})
    return item


class C12TechnicalPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = self._make_spec()
        self.bytes_by_id = self._bytes_by_id()

    @staticmethod
    def _make_spec() -> dict:
        assets = []
        for i, (asset_id, shot, role, rgba, dims) in enumerate([
            ("P02-mother", "C12-P02", "mother", False, (64, 64)),
            ("P02-background", "C12-P02", "background", False, (64, 64)),
            ("P03-mother", "C12-P03", "mother", False, (64, 64)),
            ("P03-background", "C12-P03", "background", False, (64, 64)),
            ("P02-cape", "C12-P02", "sprite", True, (8, 8)),
            ("P03-lock", "C12-P03", "sprite", True, (8, 8)),
            ("P03-fall", "C12-P03", "sprite", True, (8, 8)),
            ("P03-earring", "C12-P03", "sprite", True, (8, 8)),
            ("P03-cloth", "C12-P03", "sprite", True, (8, 8)),
        ]):
            data = _png(*dims, rgba=rgba, color=15 + i * 19)
            item = _asset(asset_id, shot, role, data, dims)
            if role == "sprite":
                item["mesh"]["kind"] = "earring" if asset_id.endswith("earring") else "cloth"
                item["mesh"]["pivotPx"] = [2, 2]
            assets.append(item)
        return {"schema": "videoforge/c12-technical-import/v1",
                "sourceCanvas": [64, 64], "assets": assets}

    def _bytes_by_id(self):
        result = {}
        for i, item in enumerate(self.spec["assets"]):
            w, h = item["dimensions"]
            result[item["id"]] = _png(w, h, rgba=item["role"] == "sprite", color=15 + i * 19)
        return result

    def _source_dir(self, *, root=None):
        root = root or self.root
        folder = root / "fixtures"
        folder.mkdir(parents=True, exist_ok=True)
        for item in self.spec["assets"]:
            (folder / (item["id"] + ".png")).write_bytes(self.bytes_by_id[item["id"]])
        return folder

    def _zip(self, entries):
        path = self.root / "candidate.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(path, "w") as bundle:
                for entry, contents in entries:
                    if isinstance(entry, ZipInfo):
                        bundle.writestr(entry, contents)
                    else:
                        bundle.writestr(entry, contents)
        return path

    def test_empty_preflight_reports_every_missing_asset_and_never_prepares_props(self):
        report, found = c12.scan([], self.spec)
        self.assertFalse(report["ready"])
        self.assertEqual(report["foundCount"], 0)
        self.assertEqual(report["requiredCount"], len(self.spec["assets"]))
        self.assertEqual({item["id"] for item in report["missing"]},
                         {item["id"] for item in self.spec["assets"]})
        self.assertEqual(found, {})
        with patch.object(c12, "manifest", return_value=self.spec):
            with self.assertRaisesRegex(VideoForgeError, "REQUIRED_EXISTING_ASSETS_MISSING"):
                c12.prepare(self.root)
        self.assertFalse((self.root / c12.OUT / "props.json").exists())
        self.assertFalse((self.root / "motion-remotion" / "public").exists())

    def test_scan_requires_each_sha_native_dimensions_and_rgba_sprite(self):
        source = self._source_dir()
        report, found = c12.scan([source], self.spec)
        self.assertTrue(report["ready"])
        self.assertEqual(set(found), {item["id"] for item in self.spec["assets"]})
        self.assertFalse(report["officialVideoApproved"])
        self.assertFalse(report["humanVisualReview"])

        wrong_sha_spec = copy.deepcopy(self.spec)
        wrong_sha_spec["assets"][0]["sha256"] = "0" * 64
        mismatch, _ = c12.scan([source], wrong_sha_spec)
        self.assertFalse(mismatch["ready"])
        self.assertIn("P02-mother", {item["id"] for item in mismatch["missing"]})
        self.assertEqual(mismatch["ignoredUnrecognizedPngs"], 1)

        wrong_dimensions = copy.deepcopy(self.spec)
        wrong_dimensions["assets"][0]["dimensions"] = [63, 64]
        with self.assertRaisesRegex(VideoForgeError, "CANVAS_DIMENSIONS_MISMATCH"):
            c12.scan([source], wrong_dimensions)

        wrong_bbox = copy.deepcopy(self.spec)
        sprite = next(item for item in wrong_bbox["assets"] if item["role"] == "sprite")
        sprite["bbox"][2] -= 1
        with self.assertRaisesRegex(VideoForgeError, "BBOX"):
            c12.scan([source], wrong_bbox)

        no_alpha = _png(8, 8, rgba=False, color=210)
        bad = copy.deepcopy(self.spec)
        sprite = next(item for item in bad["assets"] if item["role"] == "sprite")
        sprite["sha256"] = hashlib.sha256(no_alpha).hexdigest()
        sprite_file = source / "P02-cape.png"
        sprite_file.write_bytes(no_alpha)
        with self.assertRaises(LayerError):
            c12.scan([source], bad)

    def test_zip_traversal_backslash_duplicate_names_and_symlink_are_rejected(self):
        sample = self.bytes_by_id[self.spec["assets"][0]["id"]]
        unsafe = [
            (("../escape.png", sample),),
            (("folder/../../escape.png", sample),),
            (("same.png", sample), ("SAME.PNG", sample)),
        ]
        for entries in unsafe:
            with self.subTest(entries=tuple(e[0] for e in entries)):
                archive = self._zip(entries)
                with self.assertRaises(VideoForgeError):
                    list(c12.candidates([archive]))
        link = ZipInfo("link.png")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive = self._zip([(link, b"target.png")])
        with self.assertRaisesRegex(VideoForgeError, "ZIP_UNSAFE_ENTRY"):
            list(c12.candidates([archive]))

    def test_source_symlink_is_rejected_when_platform_allows_creating_one(self):
        target = self.root / "target"
        target.mkdir()
        link = self.root / "source-link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("This Windows environment does not permit symlink fixtures")
        with self.assertRaisesRegex(VideoForgeError, "SYMLINK_OR_JUNCTION"):
            list(c12.candidates([link]))

    def test_require_committed_compares_exact_git_bytes_under_archive_only(self):
        archived = self.root / c12.ARCHIVE / "42" / "sample.png"
        archived.parent.mkdir(parents=True)
        data = b"fixture bytes"
        archived.write_bytes(data)
        success = unittest.mock.Mock(returncode=0, stdout=data)
        with patch.object(c12.subprocess, "run", return_value=success) as run:
            c12.require_committed(archived, data, self.root)
        self.assertEqual(run.call_args.args[0][0:2], ["git", "show"])
        self.assertEqual(run.call_args.kwargs["cwd"], self.root)

        not_committed = unittest.mock.Mock(returncode=128, stdout=b"")
        with patch.object(c12.subprocess, "run", return_value=not_committed):
            with self.assertRaisesRegex(VideoForgeError, "ORIGINALS_NOT_COMMITTED_EXACTLY"):
                c12.require_committed(archived, data, self.root)

        changed_bytes = unittest.mock.Mock(returncode=0, stdout=b"different")
        with patch.object(c12.subprocess, "run", return_value=changed_bytes):
            with self.assertRaisesRegex(VideoForgeError, "ORIGINALS_NOT_COMMITTED_EXACTLY"):
                c12.require_committed(archived, data, self.root)

        outside = self.root / "outside.png"
        outside.write_bytes(data)
        with self.assertRaisesRegex(VideoForgeError, "ASSET_OUTSIDE_ARCHIVE"):
            c12.require_committed(outside, data, self.root)

    def test_import_uses_real_archive_for_synthetic_manifest_and_writes_false_approval_receipt(self):
        source = self._source_dir()
        expected = len(self.spec["assets"])
        import_id = 731042
        with patch.object(c12, "manifest", return_value=self.spec):
            receipt = c12.import_assets([source], import_id, root=self.root)
        self.assertEqual(receipt["archived_image_count"], expected)
        self.assertEqual(receipt["gitCommitAndPushRequired"], True)
        self.assertFalse(receipt["production_approved"])
        archived = self.root / c12.ARCHIVE / str(import_id)
        for item in self.spec["assets"]:
            self.assertEqual((archived / (item["id"] + ".png")).read_bytes(),
                             self.bytes_by_id[item["id"]])
        archive_manifest = json.loads((archived / "manifesto-geracoes.json").read_text())
        self.assertEqual(archive_manifest["archived_image_count"], expected)
        self.assertFalse(archive_manifest["production_approved"])
        receipt_path = self.root / c12.OUT / "import-receipt.json"
        self.assertEqual(json.loads(receipt_path.read_text()), receipt)
        manifest = json.loads((self.root / c12.OUT / "incoming" / str(import_id) / "manifest.json").read_text())
        self.assertEqual(manifest["generatedImages"], 0)
        self.assertFalse(manifest["humanVisualReview"])

    def test_prepare_builds_two_shot_three_manifest_only_after_archive_sha_checks(self):
        source = self._source_dir()
        archive_root = self.root / c12.ARCHIVE / "731043"
        archive_root.mkdir(parents=True)
        for item in self.spec["assets"]:
            (archive_root / (item["id"] + ".png")).write_bytes(self.bytes_by_id[item["id"]])
        def fake_scan(sources, specification):
            found = {item["id"]: (self.bytes_by_id[item["id"]], archive_root / (item["id"] + ".png"))
                     for item in self.spec["assets"]}
            return ({"ready": True, "missing": []}, found)
        with patch.object(c12, "manifest", return_value=self.spec), \
                patch.object(c12, "scan", side_effect=fake_scan), \
                patch.object(c12, "require_committed") as committed:
            path = c12.prepare(self.root)
        self.assertEqual(path, self.root / c12.OUT / "props.json")
        props = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual([shot["id"] for shot in props["shots"]], ["C12-P02", "C12-P03"])
        self.assertEqual(sum(len(shot["layers"]) for shot in props["shots"]), 5)
        self.assertFalse(props["officialVideoApproved"])
        self.assertEqual(props["imageGenerationCalls"], 0)
        self.assertEqual(committed.call_count, len(self.spec["assets"]))
        self.assertTrue(all(not p.is_symlink() for p in (self.root / "motion-remotion/public").rglob("*")))

    def test_duplicate_asset_sha_in_manifest_is_rejected(self):
        duplicate = copy.deepcopy(self.spec)
        duplicate["assets"][1]["sha256"] = duplicate["assets"][0]["sha256"]
        with self.assertRaisesRegex(VideoForgeError, "MANIFEST_DUPLICATE_HASH"):
            c12.scan([], duplicate)

    def _make_review_bundle(self, *, no_visible_change=False):
        video_dir = self.root / "render"
        review = video_dir / "review-frames"
        review.mkdir(parents=True, exist_ok=True)
        video = video_dir / "draft.mp4"
        video.write_bytes(b"synthetic mp4 placeholder; ffprobe is mocked")
        props = video_dir / "props.json"
        props.write_text('{"schema":"fixture"}\n', encoding="utf-8")
        for frame in c12.REVIEW_FRAMES:
            if no_visible_change and frame in (0, 30):
                color = 19
            else:
                color = (frame + 3) % 250
            data = _png(720, 1280, rgba=False, color=color)
            (review / f"frame-{frame}.png").write_bytes(data)
            (review / f"frame-{frame}-repeat.png").write_bytes(data)
        return video

    @staticmethod
    def _ffprobe_result(*, audio=False):
        streams = [{"codec_type": "video", "codec_name": "h264", "pix_fmt": "yuv420p",
                    "width": 720, "height": 1280, "r_frame_rate": "30/1", "nb_frames": "240"}]
        if audio:
            streams.append({"codec_type": "audio", "codec_name": "aac"})
        return unittest.mock.Mock(stdout=json.dumps({"streams": streams}))

    def test_verify_accepts_silent_h264_only_with_repeated_stills_and_visible_change(self):
        video = self._make_review_bundle()
        output = self.root / "verification.json"
        with patch.object(c12.subprocess, "run", return_value=self._ffprobe_result()) as probe:
            report = c12.verify(video, output)
        self.assertEqual(probe.call_args.args[0][0], "ffprobe")
        self.assertTrue(report["repeatFramesIdentical"])
        self.assertFalse(report["humanVisualReview"])
        self.assertFalse(report["officialVideoApproved"])
        self.assertFalse(report["fullRigReady"])
        self.assertEqual(len(report["repeatedFrameHashes"]), len(c12.REVIEW_FRAMES))
        self.assertEqual(report["inputPropsSha256"],
                         hashlib.sha256((video.parent / "props.json").read_bytes()).hexdigest())
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)

    def test_verify_rejects_nondeterministic_repeat_and_static_shots(self):
        video = self._make_review_bundle()
        repeat = video.parent / "review-frames" / "frame-74-repeat.png"
        repeat.write_bytes(_png(720, 1280, rgba=False, color=222))
        with patch.object(c12.subprocess, "run", return_value=self._ffprobe_result()):
            with self.assertRaisesRegex(VideoForgeError, "NONDETERMINISTIC_FRAME_74"):
                c12.verify(video, self.root / "nondeterministic.json")

        video = self._make_review_bundle(no_visible_change=True)
        with patch.object(c12.subprocess, "run", return_value=self._ffprobe_result()):
            with self.assertRaisesRegex(VideoForgeError, "SHOT_HAS_NO_VISIBLE_CHANGE"):
                c12.verify(video, self.root / "static.json")

    def test_verify_rejects_audio_stream(self):
        video = self._make_review_bundle()
        with patch.object(c12.subprocess, "run", return_value=self._ffprobe_result(audio=True)):
            with self.assertRaisesRegex(VideoForgeError, "DRAFT_MUST_BE_SILENT"):
                c12.verify(video, self.root / "audio.json")


if __name__ == "__main__":
    unittest.main()
