"""Non-destructive 941x1671 -> 941x1672 alignment of the creator-approved C01-P04 V3.

The approved PNG is immutable. We copy its pixels exactly and extend only the
bottom border by duplicating its last row; no generation, cropping, scaling or
artistic modification. A derived technical image is NOT an additional visual
approval, nor authorization for rig/render/upload.
"""
from __future__ import annotations

import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys

from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from .scene_layers import png_info

SHOT = "C01-P04"
SOURCE_RUN = 44152300579
SOURCE_PRODUCER = "production-scene-mother-orientation-v3"
SOURCE_ASSET = "c01-p04-scene-mother-facing-throne-v3"
SOURCE_SHA = "a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
PRODUCER = "production-scene-mother-orientation-v3-aligned"
ASSET = "c01-p04-scene-mother-facing-throne-v3-native-aligned"
SCHEMA = "videoforge/ep01-approved-v3-one-row-technical-alignment/v1"

def approved_original(root: Path = ROOT) -> dict:
    root = Path(root)
    manifest = root / REL / "APROVACOES-VISUAIS-C01-V3.json"
    if manifest.is_symlink() or not manifest.is_file():
        raise VideoForgeError("EP01_V3_ALIGN_APPROVAL_MANIFEST_MISSING")
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    if (doc.get("schema") != "videoforge/ep01-shot-mother-visual-approvals/v1"
            or doc.get("channel") != CHANNEL or doc.get("video_id") != VIDEO
            or doc.get("approval_scope") != "individual_exact_sha_only"):
        raise VideoForgeError("EP01_V3_ALIGN_APPROVAL_MANIFEST_INVALID")
    approvals = [x for x in doc.get("approvals", [])
                 if x.get("shot_id") == SHOT and x.get("variant") == SHOT]
    if len(approvals) != 1:
        raise VideoForgeError("EP01_V3_ALIGN_NO_UNIQUE_CREATOR_APPROVAL")
    entry = approvals[0]
    expected = REL / "assets" / "geracoes" / SOURCE_PRODUCER / str(SOURCE_RUN) / (SOURCE_ASSET + ".png")
    if (entry.get("file") != expected.as_posix()
            or entry.get("sha256") != SOURCE_SHA
            or entry.get("native_dimensions") != [941, 1671]
            or entry.get("visual_status") != "approved_by_creator"
            or entry.get("approved_for_visual_reference") is not True
            or entry.get("rig_ready") is not False):
        raise VideoForgeError("EP01_V3_ALIGN_APPROVAL_SHA_OR_STATUS_INVALID")
    original = root / expected
    proof = original.with_suffix(".production.json")
    archive_manifest = original.parent / "manifesto-geracoes.json"
    if any(p.is_symlink() or not p.is_file() for p in (original, proof, archive_manifest)):
        raise VideoForgeError("EP01_V3_ALIGN_ARCHIVED_ORIGINAL_MISSING")
    blob = original.read_bytes()
    if hashlib.sha256(blob).hexdigest() != SOURCE_SHA:
        raise VideoForgeError("EP01_V3_ALIGN_SOURCE_SHA_CHANGED")
    record = json.loads(proof.read_text(encoding="utf-8"))
    archive = json.loads(archive_manifest.read_text(encoding="utf-8"))
    matching = [x for x in archive.get("images", []) if x.get("file") == original.name]
    if (record.get("sha256") != SOURCE_SHA
            or record.get("candidate_scene_shot_id") != SHOT
            or record.get("target_variant") != SHOT
            or record.get("width") != 941 or record.get("height") != 1671
            or record.get("human_visual_approval") is not False
            or archive.get("producer") != SOURCE_PRODUCER
            or archive.get("github_run_id") != SOURCE_RUN
            or len(matching) != 1 or matching[0].get("sha256") != SOURCE_SHA):
        raise VideoForgeError("EP01_V3_ALIGN_ARCHIVE_PROVENANCE_INVALID")
    info = png_info(blob, require_alpha=False)
    if info["width"] != 941 or info["height"] != 1671:
        raise VideoForgeError("EP01_V3_ALIGN_UNEXPECTED_SOURCE_CANVAS")
    return {"blob": blob, "file": expected.as_posix(), "approval_file": manifest.relative_to(root).as_posix()}

def already_archived(root: Path = ROOT) -> dict | None:
    folder = Path(root) / REL / "assets" / "geracoes" / PRODUCER
    if not folder.exists():
        return None
    if folder.is_symlink():
        raise VideoForgeError("EP01_V3_ALIGN_ARCHIVE_SYMLINK")
    matches = []
    for run in folder.iterdir():
        if not run.is_dir() or not run.name.isdecimal():
            continue
        png = run / (ASSET + ".png")
        proof = png.with_suffix(".production.json")
        manifest = run / "manifesto-geracoes.json"
        if not png.exists():
            continue
        if any(p.is_symlink() or not p.is_file() for p in (png, proof, manifest)):
            raise VideoForgeError("EP01_V3_ALIGN_ARCHIVE_INCOMPLETE")
        digest = hashlib.sha256(png.read_bytes()).hexdigest()
        data = json.loads(proof.read_text(encoding="utf-8"))
        register = json.loads(manifest.read_text(encoding="utf-8"))
        images = [row for row in register.get("images", []) if row.get("file") == png.name]
        if (data.get("sha256") != digest
                or data.get("source_image_sha256") != SOURCE_SHA
                or register.get("producer") != PRODUCER
                or len(images) != 1 or images[0].get("sha256") != digest):
            raise VideoForgeError("EP01_V3_ALIGN_ARCHIVE_INVALID")
        matches.append({"run_id": int(run.name), "sha256": digest,
                        "file": png.relative_to(root).as_posix()})
    return max(matches, key=lambda item: item["run_id"]) if matches else None

def generate(root: Path = ROOT) -> dict:
    from PIL import Image, ImageChops
    root = Path(root)
    if already_archived(root):
        raise VideoForgeError("EP01_V3_ALIGN_ALREADY_ARCHIVED")
    original = approved_original(root)
    with Image.open(BytesIO(original["blob"])) as im:
        im.load()
        if im.format != "PNG" or im.size != (941, 1671):
            raise VideoForgeError("EP01_V3_ALIGN_INPUT_INVALID")
        original_mode = "RGBA" if "A" in im.getbands() else "RGB"
        rgb = im.convert(original_mode)
    dest = Image.new(original_mode, (941, 1672))
    dest.paste(rgb, (0, 0))
    last = rgb.crop((0, 1670, 941, 1671))
    dest.paste(last, (0, 1671))
    if ImageChops.difference(dest.crop((0, 0, 941, 1671)), rgb).getbbox():
        raise VideoForgeError("EP01_V3_ALIGN_ORIGINAL_PIXELS_CHANGED")
    if ImageChops.difference(dest.crop((0, 1671, 941, 1672)), last).getbbox():
        raise VideoForgeError("EP01_V3_ALIGN_BOTTOM_ROW_NOT_DUPLICATED")
    buffer = BytesIO()
    dest.save(buffer, "PNG", optimize=True)
    raw = buffer.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    out_dir = root / "output" / CHANNEL / "videos" / VIDEO / "imagens"
    png = out_dir / (ASSET + ".png")
    proof = out_dir / (ASSET + ".production.json")
    if any(p.is_symlink() or p.exists() for p in (png, proof)):
        raise VideoForgeError("EP01_V3_ALIGN_OUTPUT_EXISTS")
    out_dir.mkdir(parents=True, exist_ok=True)
    png.write_bytes(raw)
    result = {
        "schema": SCHEMA, "channel": CHANNEL, "video_id": VIDEO,
        "candidate_scene_shot_id": SHOT, "asset_id": ASSET,
        "sha256": digest, "source_image_sha256": SOURCE_SHA,
        "source_originals_sha_verified": [{"asset_id": SOURCE_ASSET,
                                           "sha256": SOURCE_SHA,
                                           "path": original["file"]}],
        "original_visual_approval_manifest": original["approval_file"],
        "source_canvas": [941, 1671], "output_canvas": [941, 1672],
        "technical_postprocess": "duplicate_last_scanline_no_resize_no_crop",
        "source_pixels_unchanged": True,
        "pixel_qa": "full_source_region_exact_and_bottom_row_identical",
        "approved_original_sha256": SOURCE_SHA,
        "derived_image_visual_approval": False,
        "human_visual_approval": False, "rig_ready": False,
        "mp4_generated": False, "youtube_uploaded": False,
        "provider_image_calls": 0,
    }
    proof.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("EP01_V3_ALIGNED", json.dumps({"sha256": digest, "source_sha256": SOURCE_SHA,
          "canvas": [941,1672], "paid_calls": 0, "rig_ready": False}))
    return result

if __name__ == "__main__":
    try:
        generate()
    except (OSError, ValueError, VideoForgeError, ImportError) as exc:
        print("EP01_V3_ALIGNMENT_STOPPED", str(exc), file=sys.stderr)
        sys.exit(2)
