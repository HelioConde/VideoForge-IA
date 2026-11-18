"""Offline visual QA contact sheet from archived EP01 C07/C08 PNGs.

SHA-verify every original byte. Thumbnail generation never overwrites sources,
never calls proxy and never grants creative approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .runtime import ROOT, MANIFEST

SOURCES = [
    {
        "shot_id": "C07-P01",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-scene-mother-v2/44094654952/c07-p01-scene-mother.png",
        "sha256": "1fd042f2a7cde4e6afb126cb8640ad5178cdea16ca60d8650e1e88a98c75e319",
        "type": "archived_original"
    },
    {
        "shot_id": "C07-P02",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-continuity-v2-mother/44264179761/c07-p02-continuity-v2-scene-mother.png",
        "sha256": "c575af1ef7487370e1b0beba84e09809d3c16723d649fa9113119a8abc859899",
        "type": "v2_candidate"
    },
    {
        "shot_id": "C07-P03",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-continuity-v2-mother/44264707976/c07-p03-continuity-v2-scene-mother.png",
        "sha256": "5e7e890298bd692fc0aa3fa3c1473ce0d36fcefb3bb94c2be3cc9129f9ad2f9c",
        "type": "v2_candidate"
    },
    {
        "shot_id": "C07-P04",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-scene-mother-v2/44095398312/c07-p03-scene-mother.png",
        "sha256": "9f00c738d5abf9c9b3fc7314ffbb31a56b3d051b36ec753268f97bc5ce0a433e",
        "type": "reuse_archived_original_C07-P03"
    },
    {
        "shot_id": "C08-P01",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-continuity-v2-mother/44264889930/c08-p01-continuity-v2-scene-mother.png",
        "sha256": "fbce36d3ed98224912e047d79f581c621ebfe65bf7d3e857aad61b53a94bf57a",
        "type": "v2_candidate"
    },
    {
        "shot_id": "C08-P02",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-continuity-v2-mother/44265114014/c08-p02-continuity-v2-scene-mother.png",
        "sha256": "3c21b7d82d69b1445b45cb1a23582e556c910530b568c26ae0d48b4873c38721",
        "type": "v2_candidate"
    },
    {
        "shot_id": "C08-P03",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-continuity-v2-mother/44265340634/c08-p03-continuity-v2-scene-mother.png",
        "sha256": "8462678d0a8d8e9ddb748981c32951a7037ab70f7b596490de1ad4e9b1aa4299",
        "type": "v2_candidate"
    },
    {
        "shot_id": "C08-P04",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-continuity-v2-mother/44265573380/c08-p04-continuity-v2-scene-mother.png",
        "sha256": "3b4eb375bec32879d831c9d025997c1977dd9f9fde8cf48cd5368cf213bf0b64",
        "type": "v2_candidate"
    },
    {
        "shot_id": "C08-P05",
        "file": "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-continuity-v2-mother/44265834974/c08-p05-continuity-v2-scene-mother.png",
        "sha256": "151061b3bb6954d0b5bf0fa5b26c0fc07f5c50a79411bd164fc7a18068c71ced",
        "type": "v2_candidate"
    }
]
DIMENSIONS = (320, 568)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(root=ROOT) -> dict:
    """Integrity/source inventory only, not semantic image QA."""
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    shots = manifest["shots"]
    if [shot["id"] for shot in shots] != [row["shot_id"] for row in SOURCES]:
        raise ValueError("Pinned C07/C08 shot order no longer matches the contact sheet")
    # Match the EXACT sources used by the official 42-shot Remotion preview.
    # For C07-P04 this is the *original* C07-P03, not its V2 replacement.
    from videoforge.ep01_camera_batch import build_plan
    rendered = {shot["id"]: shot for shot in build_plan(root, "continuity-v2")["shots"]}
    rows = []
    prev = None
    for shot, row in zip(shots, SOURCES):
        planned = rendered[row["shot_id"]]["source"]
        if (not planned or planned["file"] != row["file"]
                or planned["sha256"] != row["sha256"]):
            raise ValueError(f"Visual QA source differs from Remotion plan: {row['shot_id']}")
        candidate = (root / row["file"]).resolve(strict=True)
        if not candidate.is_relative_to(root.resolve()):
            raise ValueError("Source outside repository")
        digest = sha256_file(candidate)
        if digest != row["sha256"]:
            raise ValueError(f"Source SHA mismatch for {row['shot_id']}")
        if prev is not None and shot["start_frame"] != prev:
            raise ValueError("Frame gap or overlap in pinned manifest")
        if shot["start_frame"] >= shot["end_exclusive"]:
            raise ValueError("Invalid shot duration")
        if shot.get("scene_mother_approved") is not False:
            raise ValueError("Source visual approval flag changed unexpectedly")
        prev = shot["end_exclusive"]
        rows.append({
            "shot_id": row["shot_id"],
            "asset_path": row["file"],
            "sha256": digest,
            "asset_kind": row["type"],
            "beat": shot["beat"],
            "start_frame": shot["start_frame"],
            "end_exclusive": shot["end_exclusive"],
            "scene_mother_approved": False,
            "visual_review_status": "pending_human_or_independent_visual_qa",
        })
    if (rows[3]["asset_path"] == rows[2]["asset_path"]
            or rows[3]["asset_kind"] != "reuse_archived_original_C07-P03"):
        raise ValueError("C07-P04 must reuse ORIGINAL C07-P03, distinct from C07-P03 V2")
    return {
        "schema_version": 1,
        "kind": "ep01_c07_c08_archived_image_contact_sheet",
        "source_manifest": MANIFEST.as_posix(),
        "shots": rows,
        "unique_source_images": len({x["sha256"] for x in rows}),
        "reused_shots": ["C07-P04"],
        "reuse_details": {"C07-P04": "archived ORIGINAL C07-P03; distinct from C07-P03 V2"},
        "contains_rendered_mp4_frames": False,
        "visual_qa_approved": False,
        "new_ai_requests": 0,
        "source_bytes_modified": 0,
        "youtube_publications": 0,
    }


def render_sheet(root: Path, output_dir: Path, inventory: dict) -> None:
    """Render labeled preview JPGs and a 3x3 sheet with Pillow, offline."""
    from PIL import Image, ImageDraw, ImageFont

    output_dir.mkdir(parents=True, exist_ok=True)
    width, height = DIMENSIONS
    label_height = 52
    tile_h = height + label_height
    board = Image.new("RGB", (width * 3, tile_h * 3), "#12161d")
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    for index, row in enumerate(inventory["shots"]):
        shot_id = row["shot_id"]
        label = shot_id + (" [REUSO ORIGINAL]" if shot_id == "C07-P04" else "")
        src = (root / row["asset_path"]).resolve(strict=True)
        tile = Image.new("RGB", (width, tile_h), "#12161d")
        with Image.open(src) as im:
            w, h = im.size
            row["source_dimensions"] = [w, h]
            row["aspect_ratio_mismatch_to_9_16"] = abs((w / h) - (9 / 16)) > 0.03
            image = im.convert("RGB")
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            x = (width - image.width) // 2
            y = label_height + (height - image.height) // 2
            tile.paste(image, (x, y))
        draw = ImageDraw.Draw(tile)
        draw.rectangle((0, 0, width, label_height - 1), fill="#17212d")
        draw.text((8, 14), label, fill="white", font=font)
        tile.save(output_dir / f"{shot_id}-preview.jpg", quality=90, optimize=True)
        board.paste(tile, ((index % 3) * width, (index // 3) * tile_h))
    board.save(output_dir / "c07-c08-9-shots-contact.jpg", quality=91, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    inventory = validate()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.render:
        render_sheet(ROOT, args.output_dir, inventory)
    (args.output_dir / "source-inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "shots": len(inventory["shots"]),
        "unique_images": inventory["unique_source_images"],
        "reused_shots": inventory["reused_shots"],
        "mp4_reviewed": False,
        "visual_qa_approved": False,
        "new_ai_requests": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
