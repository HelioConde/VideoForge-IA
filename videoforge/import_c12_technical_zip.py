"""Import seven PREEXISTING C12 RGBA/background PNGs by exact SHA from chat ZIP.

No generated artwork, no modification of source pixels, no approval.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import stat
import sys
import zipfile
from .c12_technical_preview import (
    EP, PART_SHAS, SHOT_PARTS, SOURCES, bbox, plan, validate_png, ROOT,
    AssetGateError,
)

ZIP = ROOT / "uploads/alchemy-c12-rig-camadas-tecnicas-v2.zip"
MAX_ZIP = 12_000_000
MAX_RAW_TOTAL = 26_000_000

def targets():
    mapping = {}
    for shot, (_, _, bg_sha) in SOURCES.items():
        mapping[bg_sha] = (EP/"assets/planos"/shot/"background-inpaint-technical.png",
                           (941,1672), False)
    for mesh in plan()["meshParts"]:
        shot, name = mesh["shot"], mesh["id"]
        if name not in SHOT_PARTS.get(shot, []):
            raise AssetGateError("C12_PART_SHOT_INVALID")
        _,_,w,h = bbox(mesh["polygon"])
        mapping[PART_SHAS[name]] = (
            EP/"assets/planos"/shot/(name+".png"), (w,h), True
        )
    if len(mapping) != 7:
        raise AssetGateError("C12_SEVEN_UNIQUE_SHA_REQUIRED")
    return mapping

def import_zip():
    if ZIP.is_symlink() or not ZIP.is_file():
        raise AssetGateError("C12_EXISTING_TECHNICAL_ZIP_NOT_UPLOADED")
    if ZIP.stat().st_size > MAX_ZIP:
        raise AssetGateError("C12_TECHNICAL_ZIP_TOO_LARGE")
    wanted = targets()
    staged = {}
    with zipfile.ZipFile(ZIP) as archive:
        infos = archive.infolist()
        if len(infos) > 30 or sum(i.file_size for i in infos) > MAX_RAW_TOTAL:
            raise AssetGateError("C12_ZIP_TOO_MANY_ENTRIES")
        for info in infos:
            if info.is_dir():
                continue
            mode = info.external_attr >> 16
            if (info.flag_bits & 1 or info.file_size > 6_000_000
                or info.filename.startswith("/") or ".." in Path(info.filename).parts
                or (mode and stat.S_IFMT(mode) == stat.S_IFLNK)):
                raise AssetGateError("C12_ZIP_UNSAFE_ENTRY")
            if not info.filename.lower().endswith(".png"):
                if not info.filename.lower().endswith((".json", ".txt", ".md")):
                    raise AssetGateError("C12_ZIP_UNEXPECTED_ENTRY")
                continue
            data = archive.read(info)
            sha = hashlib.sha256(data).hexdigest()
            if sha not in wanted or sha in staged:
                raise AssetGateError("C12_ZIP_UNKNOWN_OR_DUPLICATE_PNG_SHA")
            staged[sha] = data
    if set(staged) != set(wanted):
        raise AssetGateError("C12_ZIP_MISSING_SOME_ORIGINAL_PNGS")
    # Verify all bytes and PNG metadata before mutating any target file.
    for sha, data in staged.items():
        target, size, alpha = wanted[sha]
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if ROOT in parent.parents):
            raise AssetGateError("C12_DESTINATION_SYMLINK")
        if target.exists() and target.read_bytes() != data:
            raise AssetGateError("C12_WOULD_OVERWRITE_EXISTING_ART")
        # Validate source through temporary file only when necessary for PNG header.
        # PNG header is decoded directly; never re-encode pixels.
        if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            raise AssetGateError("C12_ZIP_INVALID_PNG")
        import struct
        w,h,depth,color=struct.unpack(">IIBB",data[16:26])
        if (w,h)!=size or depth!=8 or color not in (2,6) or (alpha and color!=6):
            raise AssetGateError("C12_ZIP_INVALID_DIMENSIONS_OR_ALPHA:"+target.name)
    for sha,data in staged.items():
        target,_,_=wanted[sha]
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        # SHA proof based on stored exact pixels, not a generated replacement.
        if hashlib.sha256(target.read_bytes()).hexdigest()!=sha:
            raise AssetGateError("C12_POST_ARCHIVE_SHA_FAILED")
    report={
        "schema":"videoforge/c12-technical-archive/v1",
        "source_zip":ZIP.name,"png_originals_archived":7,
        "files":[{"path":str(wanted[sha][0].relative_to(ROOT)),"sha256":sha}
                 for sha in sorted(wanted)],
        "reencoded_pixels":0,"image_generation_calls":0,
        "human_visual_approved":False,"official_mp4_approved":False,
        "render_only_after_sources_present":True,
    }
    report_path=EP/"qa-c12-technical-import.json"
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("C12_EXACT_SHA_TECHNICAL_PNGS_ARCHIVED",len(staged))
    return report

if __name__=="__main__":
    try:
        import_zip()
    except (OSError,AssetGateError,KeyError,ValueError,zipfile.BadZipFile) as exc:
        print("C12_TECHNICAL_ASSETS_IMPORT_BLOCKED",str(exc),file=sys.stderr)
        raise SystemExit(2)
