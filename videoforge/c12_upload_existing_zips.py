"""Stage TWO already existing C12 ZIPs without creating or editing any PNG.

ZIP validation uses the exact hashes recorded in the current project's
manifests. Produces the two original archives in root/uploads/ for the
already-installed GitHub Actions importers. No AI, rendering, approval or
YouTube operations. Never accepts replacement/approximate artwork.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import sys
import tempfile
from zipfile import ZipFile, BadZipFile

from .c12_technical_preview import ROOT, PART_SHAS, SOURCES
from .import_c12_technical_zip import targets as technical_targets

ORIGINAL_NAME = "alchemy-ep01-cinema-3-originais.zip"
TECHNICAL_NAME = "alchemy-c12-rig-camadas-tecnicas-v2.zip"
KAEL_CLOSE_SHA = "edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f"
MAX_SOURCE_ARCHIVE = 11_000_000
MAX_TECHNICAL_ARCHIVE = 12_000_000
MAX_DECOMPRESSED = 26_000_000
MAX_PNG_BYTES = 6_000_000


class C12BundleError(ValueError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def original_requirements() -> dict[str, tuple[str, tuple[int, int], bool]]:
    """SHA -> (fixed filename, required PNG canvas, must be RGBA)."""
    return {
        KAEL_CLOSE_SHA: ("kael-close-salao.png", (941, 1672), False),
        SOURCES["C12-P02"][1]: ("confronto-trono-c12-p02.png", (941, 1672), False),
        SOURCES["C12-P03"][1]: ("elara-close-trono.png", (941, 1672), False),
    }


def technical_requirements() -> dict[str, tuple[str | None, tuple[int, int], bool]]:
    items = technical_targets()
    if set(PART_SHAS.values()) - set(items):
        raise C12BundleError("C12_MESH_SHA_MISSING_FROM_TECHNICAL_IMPORTER")
    return {
        sha: (None, dimensions, alpha)
        for sha, (_, dimensions, alpha) in items.items()
    }


def _check_png(data: bytes, size: tuple[int, int], alpha: bool) -> None:
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise C12BundleError("C12_ZIP_INVALID_PNG_HEADER")
    width, height, depth, mode = struct.unpack(">IIBB", data[16:26])
    if (width, height) != size or depth != 8 or mode not in (2, 6) or (alpha and mode != 6):
        raise C12BundleError("C12_ZIP_DIMENSIONS_OR_ALPHA_MISMATCH")


def inspect_zip(path: Path,
                required: dict[str, tuple[str | None, tuple[int, int], bool]],
                *, allow_metadata: bool, max_archive_bytes: int) -> dict:
    """Read all ZIP bytes, verify each PNG SHA, and never extract or mutate."""
    if path.is_symlink() or not path.is_file():
        raise C12BundleError("C12_EXISTING_ZIP_NOT_AVAILABLE:" + str(path))
    if path.stat().st_size == 0 or path.stat().st_size > max_archive_bytes:
        raise C12BundleError("C12_ZIP_ARCHIVE_SIZE_INVALID:" + path.name)
    if len(required) not in (3, 7) or len(set(required)) != len(required):
        raise C12BundleError("C12_EXPECTED_ARCHIVE_HASHES_INVALID")
    verified = {}
    metadata_count = 0
    with ZipFile(path, "r") as archive:
        entries = archive.infolist()
        if len(entries) > 30 or sum(entry.file_size for entry in entries) > MAX_DECOMPRESSED:
            raise C12BundleError("C12_ZIP_TOO_MANY_OR_TOO_LARGE_ENTRIES")
        filenames = set()
        for entry in entries:
            name = entry.filename
            if (entry.is_dir() or entry.flag_bits & 1 or
                name.startswith(("/", "\\")) or "\\" in name or
                ".." in Path(name).parts or name in filenames or
                entry.file_size > MAX_PNG_BYTES or entry.file_size < 1):
                raise C12BundleError("C12_ZIP_UNSAFE_ENTRY:" + name)
            filenames.add(name)
            unix_mode = entry.external_attr >> 16
            if unix_mode and stat.S_IFMT(unix_mode) == stat.S_IFLNK:
                raise C12BundleError("C12_ZIP_SYMLINK_BLOCKED")
            # No highly compressed ZIP bomb even for non-PNG metadata.
            if entry.compress_size == 0 or entry.file_size / entry.compress_size > 250:
                raise C12BundleError("C12_ZIP_SUSPICIOUS_COMPRESSION")
            if not name.lower().endswith(".png"):
                if not allow_metadata or not name.lower().endswith((".md", ".json", ".txt")):
                    raise C12BundleError("C12_ZIP_EXTRA_FILE:" + name)
                metadata_count += 1
                continue
            data = archive.read(entry)
            digest = _sha(data)
            if digest not in required or digest in verified:
                raise C12BundleError("C12_ZIP_UNRECOGNIZED_OR_DUPLICATED_ORIGINAL:" + name)
            fixed_name, size, alpha = required[digest]
            if fixed_name is not None and name != fixed_name:
                raise C12BundleError("C12_ZIP_ORIGINAL_FILENAME_MISMATCH:" + name)
            _check_png(data, size, alpha)
            verified[digest] = {"sha256": digest, "name_in_zip": name, "dimensions": list(size),
                                "must_be_rgba": alpha}
    if set(verified) != set(required):
        raise C12BundleError("C12_ZIP_MISSING_REQUIRED_ORIGINALS")
    return {
        "source_filename": path.name,
        "zip_sha256": _sha(path.read_bytes()),
        "zip_bytes": path.stat().st_size,
        "verified_pngs": len(verified),
        "metadata_files": metadata_count,
        "source_png_shas": sorted(verified),
    }


def stage_two_zips(originals: Path, technical: Path, root: Path = ROOT) -> dict:
    """Prevalidate BOTH archives before creating or modifying any upload path."""
    originals = originals.expanduser().resolve(strict=True)
    technical = technical.expanduser().resolve(strict=True)
    root = root.expanduser().resolve(strict=True)
    if originals == technical:
        raise C12BundleError("C12_BOTH_DISTINCT_ZIPS_REQUIRED")
    a = inspect_zip(originals, original_requirements(),
                    allow_metadata=False, max_archive_bytes=MAX_SOURCE_ARCHIVE)
    b = inspect_zip(technical, technical_requirements(),
                    allow_metadata=True, max_archive_bytes=MAX_TECHNICAL_ARCHIVE)
    dest = root / "uploads"
    if dest.is_symlink() or (dest.exists() and not dest.is_dir()):
        raise C12BundleError("C12_UPLOAD_TARGET_IS_SYMLINK_OR_NOT_DIRECTORY")
    destinations = [(originals, dest / ORIGINAL_NAME), (technical, dest / TECHNICAL_NAME)]
    # Refuse overwrites even when both inputs validate against the known SHAs.
    for src, path in destinations:
        if path.is_symlink():
            raise C12BundleError("C12_UPLOAD_ARCHIVE_SYMLINK_BLOCKED:" + path.name)
        if path.exists() and _sha(path.read_bytes()) != _sha(src.read_bytes()):
            raise C12BundleError("C12_UPLOAD_WOULD_OVERWRITE_DIFFERENT_ARCHIVE:" + path.name)
    dest.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for src, target in destinations:
            if target.is_file():
                continue
            with tempfile.NamedTemporaryFile(dir=dest, prefix=".c12-staging-", delete=False) as tmp:
                name = Path(tmp.name)
                with src.open("rb") as stream:
                    shutil.copyfileobj(stream, tmp)
            try:
                if _sha(name.read_bytes()) != _sha(src.read_bytes()):
                    raise C12BundleError("C12_ARCHIVE_COPY_SHA_MISMATCH")
                if target.exists():
                    raise C12BundleError("C12_ARCHIVE_CONCURRENT_OVERWRITE_BLOCKED")
                os.replace(name, target)
                created.append(target)
            finally:
                name.unlink(missing_ok=True)
    except Exception:
        # Roll back only files created by this call, never any earlier source.
        for target in created:
            target.unlink(missing_ok=True)
        raise
    return {
        "schema": "videoforge/alchemy-c12-exact-original-zips-staged/v1",
        "archive_files": [
            {"path": str(target.relative_to(root)),
             "zip_sha256": _sha(target.read_bytes())}
            for _, target in destinations
        ],
        "original_source_pngs_verified": a["verified_pngs"],
        "existing_technical_pngs_verified": b["verified_pngs"],
        "total_unique_pngs_verified_in_zips": 10,
        "c12_preview_sources_required": 9,
        "new_images_generated": 0,
        "pixel_edits": 0,
        "official_video_approved": False,
        "youtube_upload": False,
        "github_commit_or_import_performed": False,
        "next_step": "git add uploads/*.zip; commit/push main; GitHub importers and after-import coordinator run"
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals", type=Path, required=True)
    parser.add_argument("--technical", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = stage_two_zips(args.originals, args.technical, args.root)
    except (C12BundleError, OSError, BadZipFile, KeyError, ValueError) as exc:
        print("C12_EXISTING_ORIGINAL_BUNDLE_STAGING_BLOCKED:", str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
