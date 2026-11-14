"""Import two canonical style PNGs and optionally C12-P02 camera candidate from ZIP.

No AI, no editing, no resize/crop. Verify BOTH full source SHA-256 values
and IHDR before extracting any bytes, then preserve original files exactly.
Importing is NOT artistic, rig, or render approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile

from .cinematic_chat_references import (
    CHANNEL,VIDEO,MANIFEST,SOURCE_DIR,
    check_png_source,reference_status,
)
from .cinematic_direction import ROOT
from .errors import VideoForgeError

UPLOAD_REL="uploads/alchemy-ep01-refs-estilo.zip"
UPLOAD_THREE_REL="uploads/alchemy-ep01-cinema-3-originais.zip"
MAX_ZIP_BYTES=11_000_000
MAX_ENTRY_BYTES=6_000_000
MAX_TOTAL_BYTES=12_000_000

def validate_and_extract(root:Path=ROOT)->dict:
    third_archive=root/UPLOAD_THREE_REL
    archive=third_archive if third_archive.is_file() else root/UPLOAD_REL
    if archive.is_symlink():
        raise VideoForgeError("CINEMATIC_STYLE_ZIP_SYMLINK_BLOCKED")
    if not archive.is_file():
        raise VideoForgeError("CINEMATIC_STYLE_ZIP_NOT_YET_UPLOADED")
    if archive.stat().st_size>MAX_ZIP_BYTES:
        raise VideoForgeError("CINEMATIC_STYLE_ZIP_OVERSIZE")
    base=root/"canal"/CHANNEL/"videos"/VIDEO
    manifest=json.loads((base/MANIFEST).read_text(encoding="utf8"))
    items=manifest["approved_samples"]
    required={
      Path(x["expected_repo_path"]).name:x for x in items
    }
    if len(required)!=2:
        raise VideoForgeError("CINEMATIC_STYLE_ZIP_WRONG_MANIFEST")
    is_three=archive==third_archive
    if is_three:
        candidate_file=base/"candidato-camera-c12-p02.json"
        if candidate_file.is_symlink():
            raise VideoForgeError("CINEMATIC_CAMERA_CANDIDATE_SYMLINK")
        candidate=json.loads(candidate_file.read_text(encoding="utf8"))
        if (candidate.get("shot_id")!="C12-P02" or
                candidate.get("expected_repo_path")!="assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png"):
            raise VideoForgeError("CINEMATIC_CAMERA_CANDIDATE_MANIFEST_INVALID")
        required["confronto-trono-c12-p02.png"]={
            "expected_repo_path":candidate["expected_repo_path"],
            "dimensions_px":[candidate["original_width_px"],
                              candidate["original_height_px"]],
            "original_sha256":candidate["source_sha256"],
            "expected_bytes":candidate["original_bytes"]
        }
    payload={}
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist()
        if len(infos)!=len(required) or {info.filename for info in infos}!=set(required):
            raise VideoForgeError("CINEMATIC_STYLE_ZIP_UNEXPECTED_ENTRIES")
        if sum(i.file_size for i in infos)>MAX_TOTAL_BYTES:
            raise VideoForgeError("CINEMATIC_STYLE_ZIP_DECOMPRESSION_LIMIT")
        for info in infos:
            if (info.is_dir() or info.file_size>MAX_ENTRY_BYTES
                    or info.file_size<1024 or info.flag_bits & 1
                    or info.filename.startswith("/")
                    or ".." in Path(info.filename).parts):
                raise VideoForgeError("CINEMATIC_STYLE_ZIP_UNSAFE_ENTRY")
            user=required[info.filename]
            data=z.read(info, pwd=None)
            errors=check_png_source(
                data,*user["dimensions_px"],
                user["original_sha256"],user["expected_bytes"]
            )
            if errors:
                raise VideoForgeError(
                    "CINEMATIC_STYLE_SOURCE_MISMATCH:"
                    +info.filename+":"+",".join(errors)
                )
            payload[user["expected_repo_path"]]=data
    # All bytes verified BEFORE any target directory or file is written.
    for rel,data in payload.items():
        dest=base/rel
        for p in (dest,*dest.parents):
            if p.is_symlink():
                raise VideoForgeError("CINEMATIC_STYLE_IMPORT_SYMLINK_BLOCKED")
            if p==base:
                break
        if dest.exists() and dest.read_bytes()!=data:
            raise VideoForgeError("CINEMATIC_STYLE_IMPORT_WOULD_OVERWRITE_DIFFERENT_ART")
    for rel,data in payload.items():
        dest=base/rel
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
    result=reference_status(root)
    if result["original_source_files_sha_verified"]!=2:
        raise VideoForgeError("CINEMATIC_STYLE_IMPORT_POST_SHA_CHECK_FAILED")
    if is_three and not result["camera_candidate_C12_P02"]["source_verified"]:
        raise VideoForgeError("CINEMATIC_CAMERA_IMPORT_POST_SHA_CHECK_FAILED")
    return result

def main()->int:
    ap=argparse.ArgumentParser(description="Import exact existing chat PNGs; no AI/edit")
    args=ap.parse_args()
    try:
        result=validate_and_extract()
        print("CINEMATIC_STYLE_ORIGINAL_PNGS_IMPORTED",result["status"],
              result["original_source_files_sha_verified"],
              "cameraC12",result["camera_candidate_C12_P02"]["status"],
              "zero changed pixels; no render approved")
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
        print("CINEMATIC_STYLE_IMPORT_BLOCKED",str(e),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
