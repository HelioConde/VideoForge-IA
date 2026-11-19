"""Offline, non-approving canvas and recomposition QA for EP01 part PNGs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

REGISTRY = Path("canal") / CHANNEL / "biblia-visual" / "REGISTRO-GERACOES.json"
EPISODE = REL
GUARD = {
    "asset": "c01-p05-character-guarda_direito-native-aligned-v1",
    "source_sha256": "7091af3214d3c04dc174d55941f525ab543f055b024632315195b97b4af24afd",
    "mother_sha256": "6a599ab681994790b3e9b07bf573817781a448bcf9f77081bc03764448028553",
    "rejected_asset": "c01-p05-character-guarda_direito",
    "rejected_sha256": "7091af3214d3c04dc174d55941f525ab543f055b024632315195b97b4af24afd",
    "rejected_run_id": 44524006117,
    "rejected_path": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-proxy-separate-part-v1/44524006117/c01-p05-character-guarda_direito.png",
    "rejected_classification": "rejected_canvas_mismatch_no_pixel_resizing",
}
CROWN = {
    "asset": "c02-p01-object-coroa-aldric-v2",
    "mother_sha256": "0d1f8367c76cdf0c9b63f10071406a567b5a5a10cf799e1aa6c5d814019fa2a0",
    "bible_sha256": "37c48afcaa240f03406c280af1af4ca49304ead552f0dd89f0bbb25d0080e417",
    "predecessor_sha256": "acf47957dfc7cc92a443b065cb348014a2132ab742bc0040391dc4bc76282b9f",
    "rejected_sha256": "acf47957dfc7cc92a443b065cb348014a2132ab742bc0040391dc4bc76282b9f",
    "rejected_asset": "c02-p01-object-coroa-aldric",
    "rejected_run_id": 44530692682,
    "rejected_path": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-proxy-separate-part-v1/44530692682/c02-p01-object-coroa-aldric.png",
    "rejected_classification": "rejected_canvas_mismatch_no_pixel_resizing",
}


def build(shot_id: str, part_id: str, root: Path = ROOT) -> dict:
    from PIL import Image, ImageDraw

    root = Path(root)
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    if (shot_id, part_id) == ("C01-P05", "character-guarda_direito"):
        policy = GUARD
        producer = "production-proxy-separate-alignment-v1"
    elif (shot_id, part_id) == ("C02-P01", "object-coroa-aldric-v2"):
        policy = CROWN
        producer = "production-proxy-separate-part-v1"
    else:
        raise VideoForgeError("EP01_PART_CANVAS_QA_UNSUPPORTED_ASSET")
    rows = [x for x in registry.get("geracoes", [])
            if x.get("asset") == policy["asset"]
            and x.get("producer") == producer]
    if len(rows) != 1:
        raise VideoForgeError("EP01_PART_CANVAS_QA_ARCHIVE_NOT_UNIQUE")
    row = rows[0]
    original_rows = [x for x in registry.get("geracoes", [])
                     if x.get("asset") == policy["rejected_asset"]
                     and x.get("sha256") == policy["rejected_sha256"]]
    if len(original_rows) != 1:
        raise VideoForgeError("EP01_PART_CANVAS_QA_REJECTED_ORIGINAL_NOT_UNIQUE")
    rejected_original = original_rows[0]
    if (rejected_original.get("github_run_id") != policy["rejected_run_id"]
            or rejected_original.get("arquivo") != policy["rejected_path"]
            or rejected_original.get("qa_tecnica") != policy["rejected_classification"]):
        raise VideoForgeError("EP01_PART_CANVAS_QA_REJECTED_ORIGINAL_PROVENANCE_CHANGED")
    rel = Path(row["arquivo"])
    if rel.is_absolute() or ".." in rel.parts or not rel.is_relative_to(EPISODE / "assets" / "geracoes"):
        raise VideoForgeError("EP01_PART_CANVAS_QA_UNSAFE_ARCHIVE")
    image_path = root / rel
    proof_path = image_path.with_suffix(".production.json")
    if any(p.is_symlink() or not p.is_file() for p in (image_path, proof_path)):
        raise VideoForgeError("EP01_PART_CANVAS_QA_ARCHIVE_BYTES_MISSING")
    raw = image_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    if digest != row.get("sha256") or digest != proof.get("sha256"):
        raise VideoForgeError("EP01_PART_CANVAS_QA_ARCHIVE_SHA_MISMATCH")
    from .ep01_proxy_separate_parts import mother_source
    mother, mother_proof = mother_source(shot_id, root)
    checks = {
        "canvas_941x1672": False,
        "rgba_alpha": False,
        "source_lineage": mother_proof.get("sha256") == policy["mother_sha256"],
        "visual_recomposition_approved": False,
        "human_visual_approval": False,
        "rig_ready": False,
    }
    with Image.open(image_path) as candidate:
        candidate.load()
        with Image.open(__import__("io").BytesIO(mother)) as background:
            background.load()
            checks["canvas_941x1672"] = candidate.size == (941, 1672) == background.size
            checks["rgba_alpha"] = candidate.mode == "RGBA" and candidate.getchannel("A").getextrema()[0] == 0
            if shot_id == "C01-P05":
                source_row = next(x for x in registry["geracoes"]
                                  if x.get("asset") == "c01-p05-character-guarda_direito"
                                  and x.get("sha256") == GUARD["source_sha256"])
                source_path = root / source_row["arquivo"]
                with Image.open(source_path) as source:
                    source.load()
                    exact = candidate.size == (941, 1672) and source.size == (941, 1671)
                    exact = exact and candidate.crop((0, 0, 941, 1671)).tobytes() == source.convert("RGBA").tobytes()
                    exact = exact and candidate.crop((0, 1671, 941, 1672)).getchannel("A").getextrema() == (0, 0)
                    checks["source_pixels_unchanged_one_row_alpha_pad"] = exact
                checks["source_lineage"] = checks["source_lineage"] and proof.get("source_image_sha256") == GUARD["source_sha256"]
            else:
                refs = proof.get("source_originals_sha_verified", [])
                ref_shas = {x.get("sha256") for x in refs}
                predecessor = proof.get("versioned_from_rejected_predecessor", {})
                checks["source_lineage"] = (checks["source_lineage"]
                    and CROWN["bible_sha256"] in ref_shas
                    and predecessor.get("sha256") == CROWN["predecessor_sha256"]
                    and predecessor.get("attached_to_generation_request") is False)
            # A contact sheet is only a review aid. It is deliberately not used
            # to resize or rewrite either source image.
            sheet = Image.new("RGB", (941 * 2, 1672 + 48), "#20242b")
            bg = background.convert("RGB")
            sheet.paste(bg, (0, 48))
            if candidate.size == background.size and candidate.mode == "RGBA":
                composite = Image.alpha_composite(background.convert("RGBA"), candidate).convert("RGB")
                sheet.paste(composite, (941, 48))
            else:
                visual = candidate.convert("RGBA")
                visual.thumbnail((941, 1672))
                x = 941 + (941 - visual.width) // 2
                y = 48 + (1672 - visual.height) // 2
                checker = Image.new("RGB", (visual.width, visual.height), "#777777")
                draw = ImageDraw.Draw(checker)
                size = 24
                for yy in range(0, visual.height, size):
                    for xx in range(0, visual.width, size):
                        if (xx // size + yy // size) % 2:
                            draw.rectangle((xx, yy, xx + size - 1, yy + size - 1), fill="#aaaaaa")
                sheet.paste(Image.alpha_composite(checker.convert("RGBA"), visual).convert("RGB"), (x, y))
            draw = ImageDraw.Draw(sheet)
            draw.text((12, 14), "SOURCE MOTHER", fill="white")
            draw.text((953, 14), f"CANDIDATE OVERLAY / {candidate.width}x{candidate.height}", fill="white")
    destination = root / "output" / CHANNEL / "videos" / VIDEO / "qa"
    destination.mkdir(parents=True, exist_ok=True)
    sheet_path = destination / f"{policy['asset']}-canvas-qa.jpg"
    sheet.save(sheet_path, quality=88)
    result = {
        "schema": "videoforge/ep01-proxy-part-canvas-qa/v1",
        "shot_id": shot_id,
        "asset": policy["asset"],
        "candidate_path": rel.as_posix(),
        "candidate_sha256": digest,
        "rejected_original": {
            "asset": policy["rejected_asset"],
            "sha256": policy["rejected_sha256"],
            "run_id": rejected_original["github_run_id"],
            "path": rejected_original["arquivo"],
            "classification": policy["rejected_classification"],
            "qa_status": rejected_original.get("qa_tecnica"),
            "status": "rejected_preserved_never_overwritten",
        },
        "contact_sheet": str(sheet_path),
        "checks": checks,
        "technical_candidate": all(v for k, v in checks.items()
                                    if k not in ("visual_recomposition_approved", "human_visual_approval", "rig_ready")),
        "visual_recomposition_approved": False,
        "human_visual_approval": False,
        "rig_ready": False,
        "mp4_generated": False,
        "youtube_uploaded": False,
        "provider_image_calls": 0,
        "review_required": True,
    }
    report_path = destination / f"{policy['asset']}-canvas-qa.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("EP01_PART_CANVAS_QA", json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--part", required=True)
    args = parser.parse_args()
    try:
        result = build(args.shot_id, args.part)
        if not result["technical_candidate"]:
            raise VideoForgeError("EP01_PART_CANVAS_QA_TECHNICAL_CHECK_FAILED")
    except (OSError, ValueError, KeyError, StopIteration, VideoForgeError) as exc:
        print("EP01_PART_CANVAS_QA_STOPPED", str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
