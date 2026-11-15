"""Safety and exact-source regression tests for staging pre-existing C12 ZIPs.

Only temporary 2x2 PNG fixtures are generated in memory; none are C12
artwork, and no generated image is archived in the episode.
"""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile
import zlib

from videoforge import c12_upload_existing_zips as upload


def chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))


def tiny_png(*, rgba=False, seed=55):
    channels = 4 if rgba else 3
    row = bytes((seed, 90, 130, 255)[:channels]) * 2
    raw = (b"\0" + row) * 2
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 6 if rgba else 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(raw)) +
            chunk(b"IEND", b""))


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def make_bundle(path, files):
    with ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)


class ExactOriginalZipUploadTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original = self.root / "3-originais.zip"
        self.technical = self.root / "7-tecnicos.zip"
        self.rgb = tiny_png()
        self.rgba = tiny_png(rgba=True)
        self.rgb_requirements = {
            checksum(self.rgb): ("source.png", (2, 2), False),
        }
        self.tech_requirements = {
            checksum(self.rgba): (None, (2, 2), True)
        }

    def test_validates_exact_original_png_sha(self):
        make_bundle(self.original, {"source.png": self.rgb})
        # The production loader requires 3/7 distinct original PNG hashes,
        # so this one-image test must fail closed.
        with self.assertRaisesRegex(upload.C12BundleError, "EXPECTED_ARCHIVE_HASHES_INVALID"):
            upload.inspect_zip(self.original, self.rgb_requirements,
                               allow_metadata=False, max_archive_bytes=100_000)

    def test_success_stages_exact_two_archive_bytes_and_is_idempotent(self):
        rgb = {f"original-{i}.png": tiny_png(seed=55 + i) for i in range(3)}
        parts = {f"technical-{i}.png": tiny_png(rgba=True, seed=72 + i) for i in range(7)}
        make_bundle(self.original, rgb)
        make_bundle(self.technical, parts)
        expected_rgb = {
            checksum(data): (name, (2, 2), False) for name, data in rgb.items()
        }
        expected_tech = {
            checksum(data): (None, (2, 2), True) for data in parts.values()
        }
        with patch.object(upload, "original_requirements", return_value=expected_rgb):
            with patch.object(upload, "technical_requirements", return_value=expected_tech):
                receipt = upload.stage_two_zips(self.original, self.technical, self.root)
                receipt_twice = upload.stage_two_zips(self.original, self.technical, self.root)
        self.assertEqual(receipt["total_unique_pngs_verified_in_zips"], 10)
        self.assertEqual(receipt["new_images_generated"], 0)
        self.assertFalse(receipt["github_commit_or_import_performed"])
        self.assertEqual(receipt["archive_files"], receipt_twice["archive_files"])
        self.assertEqual((self.root / "uploads" / upload.ORIGINAL_NAME).read_bytes(),
                         self.original.read_bytes())
        self.assertEqual((self.root / "uploads" / upload.TECHNICAL_NAME).read_bytes(),
                         self.technical.read_bytes())

    def test_rejects_existing_different_zip_without_overwrite(self):
        rgb = {f"original-{i}.png": tiny_png(seed=55 + i) for i in range(3)}
        parts = {f"technical-{i}.png": tiny_png(rgba=True, seed=72 + i) for i in range(7)}
        make_bundle(self.original, rgb)
        make_bundle(self.technical, parts)
        expected_rgb = {
            checksum(data): (name, (2, 2), False) for name, data in rgb.items()
        }
        expected_tech = {
            checksum(data): (None, (2, 2), True) for data in parts.values()
        }
        (self.root / "uploads").mkdir()
        previous = self.root / "uploads" / upload.ORIGINAL_NAME
        previous.write_bytes(b"archive already stored (must never be overwritten)")
        with patch.object(upload, "original_requirements", return_value=expected_rgb):
            with patch.object(upload, "technical_requirements", return_value=expected_tech):
                with self.assertRaisesRegex(upload.C12BundleError, "WOULD_OVERWRITE_DIFFERENT_ARCHIVE"):
                    upload.stage_two_zips(self.original, self.technical, self.root)
        self.assertEqual(previous.read_bytes(), b"archive already stored (must never be overwritten)")
        self.assertFalse((self.root / "uploads" / upload.TECHNICAL_NAME).exists())

    def test_rejects_unexpected_png_without_writing_outputs(self):
        make_bundle(self.original, {"source.png": self.rgb})
        required = {f"{i:064x}": ("source.png", (2, 2), False) for i in range(3)}
        with self.assertRaisesRegex(upload.C12BundleError, "UNRECOGNIZED"):
            upload.inspect_zip(self.original, required,
                               allow_metadata=False, max_archive_bytes=100_000)
        self.assertFalse((self.root / "uploads").exists())

    def test_rejects_unsafe_archive_paths_and_extra_files(self):
        fake_requirement = {
            f"{i:064x}": (None, (2, 2), True) for i in range(3)
        }
        for name, error in (("../payload.png", "UNSAFE_ENTRY"),
                            ("metadata.exe", "EXTRA_FILE")):
            with self.subTest(name=name):
                make_bundle(self.original, {name: self.rgb})
                with self.assertRaisesRegex(upload.C12BundleError, error):
                    upload.inspect_zip(self.original, fake_requirement,
                                       allow_metadata=False, max_archive_bytes=100_000)

    def test_rejects_empty_and_oversized_archives(self):
        self.original.write_bytes(b"")
        with self.assertRaisesRegex(upload.C12BundleError, "ARCHIVE_SIZE_INVALID"):
            upload.inspect_zip(self.original, self.rgb_requirements,
                               allow_metadata=False, max_archive_bytes=100_000)

    def test_canonical_requirements_count_and_source_shas(self):
        real_sources = upload.original_requirements()
        technical = upload.technical_requirements()
        self.assertEqual(len(real_sources), 3)
        self.assertEqual(len(technical), 7)
        self.assertEqual(sum(bool(a) for _, _, a in technical.values()), 5)
        self.assertEqual(len(set(real_sources).intersection(technical)), 0)
        self.assertEqual(set(upload.PART_SHAS.values()).issubset(technical), True)

    def test_reject_missing_files_before_creating_upload_folder(self):
        with self.assertRaises(FileNotFoundError):
            upload.stage_two_zips(self.original, self.technical, self.root)
        self.assertFalse((self.root / "uploads").exists())

    def test_existing_uploads_are_never_overwritten(self):
        (self.root / "uploads").mkdir()
        target = self.root / "uploads" / upload.ORIGINAL_NAME
        target.write_bytes(b"previously archived immutable ZIP")
        # The path to original inputs isn't valid; no alteration of target.
        with self.assertRaises(FileNotFoundError):
            upload.stage_two_zips(self.original, self.technical, self.root)
        self.assertEqual(target.read_bytes(), b"previously archived immutable ZIP")

    def test_alpha_header_rejects_rgb_for_technical_sprite(self):
        with self.assertRaisesRegex(upload.C12BundleError, "DIMENSIONS_OR_ALPHA_MISMATCH"):
            upload._check_png(self.rgb, (2, 2), True)

    def test_dimensions_rejects_resized_art(self):
        with self.assertRaisesRegex(upload.C12BundleError, "DIMENSIONS_OR_ALPHA_MISMATCH"):
            upload._check_png(self.rgba, (941, 1672), True)

    def test_zip_is_read_only_no_extraction(self):
        make_bundle(self.original, {"source.png": self.rgb})
        required = {f"{i:064x}": ("source.png", (2, 2), False) for i in range(3)}
        with self.assertRaises(upload.C12BundleError):
            upload.inspect_zip(self.original, required,
                               allow_metadata=False, max_archive_bytes=100_000)
        self.assertFalse((self.root / "source.png").exists())


if __name__ == "__main__":
    unittest.main()
