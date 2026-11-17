#!/usr/bin/env python3
"""Compare verified C01-P02 V1, V3, and V4 without turning QA into approval."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps, ImageChops, ImageStat

from videoforge.ep01_shot_layers import mother_source
from videoforge.ep01_contact_repair_v4 import (
    ASSET, PATCH_ASSET, V3_ASSET, V3_SHA, PRODUCER, ROI, EXPECTED_MOTHER_SHA)
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

REGISTER = ROOT / "canal" / CHANNEL / "biblia-visual" / "REGISTRO-GERACOES.json"
EPISODE = ROOT / REL


def registered(asset: str, producer: str, registry: dict) -> tuple[Image.Image, dict]:
    matches = [row for row in registry.get("geracoes", []) if row.get("asset") == asset]
    if len(matches) != 1:
        raise RuntimeError("EP01_V4_ASSET_MISSING_OR_DUPLICATED " + asset)
    row = matches[0]
    relative = Path(row["arquivo"])
    if (relative.is_absolute() or ".." in relative.parts or
            not relative.is_relative_to(REL / "assets" / "geracoes" / producer)):
        raise RuntimeError("EP01_V4_ASSET_PATH_INVALID " + asset)
    path = ROOT / relative
    proof_path = path.with_suffix(".production.json")
    if (path.is_symlink() or proof_path.is_symlink() or
            not path.is_file() or not proof_path.is_file()):
        raise RuntimeError("EP01_V4_ASSET_SOURCE_MISSING")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise RuntimeError("EP01_V4_ASSET_SHA_INVALID")
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    if (proof.get("sha256") != row["sha256"] or
            proof.get("human_visual_approval") is not False):
        raise RuntimeError("EP01_V4_ASSET_PROVENANCE_INVALID")
    expected_source = EXPECTED_MOTHER_SHA if asset == V3_ASSET else V3_SHA
    actual_source = (proof.get("source_mother_sha256") if asset == V3_ASSET
                     else proof.get("source_image_sha256"))
    if actual_source != expected_source:
        raise RuntimeError("EP01_V4_SOURCE_CHAIN_INCONSISTENT")
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != "PNG":
            raise RuntimeError("EP01_V4_NOT_PNG")
        result = image.convert("RGB")
    return result.copy(), row


def build() -> None:
    mother_metadata, raw, _ = mother_source()
    if (mother_metadata["mother_sha256"] != EXPECTED_MOTHER_SHA or
            hashlib.sha256(raw).hexdigest() != EXPECTED_MOTHER_SHA):
        raise RuntimeError("EP01_V4_SOURCE_MOTHER_CHANGED")
    with Image.open(io.BytesIO(raw)) as im:
        v1 = im.convert("RGB")
    registry = json.loads(REGISTER.read_text(encoding="utf-8"))
    v3, v3_meta = registered(V3_ASSET, "production-contact-repair-v3", registry)
    if v3_meta["sha256"] != V3_SHA or v3.size != v1.size:
        raise RuntimeError("EP01_V4_REFERENCE_V3_INVALID")
    edited, edit_meta = registered(ASSET, PRODUCER, registry)
    if edited.size != v3.size:
        # Preserve original candidate and report canvas failure.
        raise RuntimeError("EP01_V4_MODEL_OUTPUT_CANVAS_MISMATCH")
    patch, patch_meta = registered(PATCH_ASSET, PRODUCER, registry)
    if patch.size != v3.size:
        raise RuntimeError("EP01_V4_PATCH_CANVAS_MISMATCH")
    delta = ImageChops.difference(v3, patch)
    outside = Image.new("L", v3.size, 255)
    ImageDraw.Draw(outside).rectangle(ROI, fill=0)
    preserved = ImageChops.multiply(delta.convert("L"), outside).getbbox() is None
    if not preserved:
        raise RuntimeError("EP01_V4_PATCH_BLED_OUTSIDE_REGION")
    metrics = {
        "schema": "videoforge/ep01-contact-v4-qa/v1",
        "ancestor_v1_sha256": EXPECTED_MOTHER_SHA,
        "v3_patch_sha256": V3_SHA,
        "v4_edit_sha256": edit_meta["sha256"],
        "v4_patch_sha256": patch_meta["sha256"],
        "canvas": list(v1.size),
        "same_canvas": True,
        "exact_v3_source_pixels_outside_roi": preserved,
        "mean_rgb_difference_v4_patch_from_v3":
            round(sum(ImageStat.Stat(delta).mean) / 3, 4),
        "roi": list(ROI),
        "human_visual_approval": False,
        "rig_ready": False,
        "mp4_generated": False,
        "youtube_uploaded": False,
        "comparison_type": "visual_candidates_not_approved"
    }
    titles = [
        ("V1: CONTATO REPROVADO", v1),
        ("V3 PATCH: CANDIDATA", v3),
        ("V4 EDICAO: CANDIDATA", edited),
        ("V4 PATCH: CANDIDATA", patch),
        ("CLOSE V1: REPROVADO", v1.crop(ROI)),
        ("CLOSE V3: REVISAR", v3.crop(ROI)),
        ("CLOSE V4 EDICAO: REVISAR", edited.crop(ROI)),
        ("CLOSE V4 PATCH: REVISAR", patch.crop(ROI))
    ]
    tw, th = 374, 665
    board = Image.new("RGB", (4 * tw + 40, 2 * th + 100), "#f2f2f2")
    draw = ImageDraw.Draw(board)
    draw.text((18, 12), "C01-P02 / V1 x V3 x V4 / CONTATO MAO, ESPADA E BAINHA",
              fill="#202020")
    for index, (title, img) in enumerate(titles):
        col = index % 4
        row = index // 4
        x, y = 14 + col * tw, 48 + row * th
        draw.text((x, y), title,
                  fill="#8b2727" if "REPROVADO" in title else "#202020")
        thumb = ImageOps.contain(img, (tw - 18, th - 62),
                                 Image.Resampling.LANCZOS)
        board.paste(thumb, (x + (tw - 18 - thumb.width) // 2, y + 23))
    draw.text((18, board.height - 35),
              "Somente candidatos. Conferir anatomia antes de recortar RGBA/rig.",
              fill="#8b2727")
    out = EPISODE / "QA-C01-P02-CONTATO-V4.jpg"
    board.save(out, "JPEG", quality=84, optimize=True)
    metrics["preview_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
    (EPISODE / "QA-C01-P02-CONTATO-V4.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("EP01_V4_CONTACT_COMPARE", json.dumps(metrics, ensure_ascii=False))


if __name__ == "__main__":
    build()
