"""Pranchas de recortes candidatos em fontes existentes; NUNCA aprova ROI.

A anotação usa pixels da prancha de contato para propor polígonos. Mesmo com
SHA conferido, revisão humana dos recortes e das identidades ainda é obrigatória.
Não altera o contrato de QA, não gera imagens com IA, não libera R2.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import EPISODE, ROOT

MANIFEST = "ROI-POLIGONOS-CANDIDATOS-V2.json"
PREVIEW = "QA-ROI-RECORTES-CANDIDATOS-V2.jpg"
REPORT = "QA-ROI-RECORTES-CANDIDATOS-V2.json"
INVENTORY = "QA-ROI-FIGURINOS-V2.json"
REGIONS = [
    ("aldric", "barba"),
    ("aldric", "tecido_externo"),
    ("aldric", "painel_central"),
    ("elara", "corpete_roxo_palacio"),
]


def verified_file(ep: Path, relative: str, sha: str, *, image_only=False):
    from PIL import Image

    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise VideoForgeError("ROI_CANDIDATE_UNSAFE_PATH")
    path = ep / rel
    if path.is_symlink() or not path.is_file() or not 50 <= path.stat().st_size <= 16_000_000:
        raise VideoForgeError("ROI_CANDIDATE_SOURCE_MISSING")
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != sha:
        raise VideoForgeError("ROI_CANDIDATE_SOURCE_SHA_MISMATCH")
    if not image_only:
        return None
    with Image.open(io.BytesIO(blob)) as im:
        im.load()
        if im.format not in ("PNG", "JPEG"):
            raise VideoForgeError("ROI_CANDIDATE_IMAGE_FORMAT")
        if relative.endswith(".png") and im.format != "PNG":
            raise VideoForgeError("ROI_CANDIDATE_SOURCE_NOT_PNG")
        return im.convert("RGB")


def board_to_source(points, size, source_index):
    """Transforma coordenadas da prancha 2080x1060 para pixels da fonte.

    Replica a projeção do board() em wardrobe_roi_review.py, sem inventar
    contornos nem atribuir significado semântico ao polígono.
    """
    from PIL import Image, ImageOps

    width, height = size
    if not (0 <= source_index <= 2 and 50 <= width <= 8192 and 50 <= height <= 8192):
        raise VideoForgeError("ROI_CANDIDATE_DIMENSIONS")
    fitted = ImageOps.contain(Image.new("RGB", size), (655, 838), Image.Resampling.LANCZOS)
    left = 25 + 690 * source_index + (655 - fitted.width) // 2
    top = 100 + (838 - fitted.height) // 2
    vertices = []
    if not isinstance(points, list) or not 3 <= len(points) <= 50:
        raise VideoForgeError("ROI_CANDIDATE_POLYGON_INVALID")
    for point in points:
        if (not isinstance(point, list) or len(point) != 2 or
                any(type(n) is not int for n in point)):
            raise VideoForgeError("ROI_CANDIDATE_POLYGON_INVALID")
        x = round((point[0] - left) * width / fitted.width)
        y = round((point[1] - top) * height / fitted.height)
        if not 0 <= x < width or not 0 <= y < height:
            raise VideoForgeError("ROI_CANDIDATE_OUTSIDE_SOURCE")
        vertices.append((x, y))
    return vertices


def count_mask_pixels(size, vertices):
    from PIL import Image, ImageDraw
    mask = Image.new("1", size, 0)
    ImageDraw.Draw(mask).polygon(vertices, fill=1)
    count = sum(v != 0 for v in mask.getdata())
    if count < 128 or count / (size[0] * size[1]) > 0.35:
        raise VideoForgeError("ROI_CANDIDATE_MASK_INVALID")
    return count


def patch(im, vertices):
    from PIL import Image, ImageDraw, ImageOps
    x0 = min(p[0] for p in vertices)
    y0 = min(p[1] for p in vertices)
    x1 = max(p[0] for p in vertices)
    y1 = max(p[1] for p in vertices)
    margin = max(30, round(max(x1 - x0, y1 - y0) * 0.65))
    bound = (max(0, x0 - margin), max(0, y0 - margin),
             min(im.width, x1 + margin + 1), min(im.height, y1 + margin + 1))
    marked = im.copy()
    draw = ImageDraw.Draw(marked)
    draw.line(vertices + [vertices[0]], fill=(255, 221, 20), width=max(3, im.width // 310))
    crop = marked.crop(bound)
    return ImageOps.contain(crop, (520, 222), Image.Resampling.LANCZOS)


def run(root: Path = ROOT, sync=False):
    from PIL import Image, ImageDraw, ImageFont
    ep = Path(root) / EPISODE
    config = ep / MANIFEST
    inventory_file = ep / INVENTORY
    if any(p.is_symlink() for p in (config, inventory_file)):
        raise VideoForgeError("ROI_CANDIDATE_UNSAFE_METADATA")
    manifest = json.loads(config.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    pairs = manifest.get("pairs", [])
    if (manifest.get("schema") != "videoforge/roi-candidate-annotation/v1" or
            manifest.get("human_semantic_verification") is not False or
            manifest.get("can_change_canonical_status") is not False or
            [(x.get("actor"), x.get("semantic_region")) for x in pairs] != REGIONS or
            inventory.get("schema") != "videoforge/wardrobe-roi-review/v1"):
        raise VideoForgeError("ROI_CANDIDATE_MANIFEST_INVALID")
    for actor in ("aldric", "elara"):
        sheet = manifest["contact_sheets"][actor]
        verified_file(ep, sheet["path"], sheet["sha256"], image_only=True)
        if inventory["previews"][actor]["sha256"] != sheet["sha256"]:
            raise VideoForgeError("ROI_CANDIDATE_BOARD_NOT_MATCHED")
        if manifest["source_indices"][actor] != [0, 1]:
            raise VideoForgeError("ROI_CANDIDATE_EXPECTED_SOURCE_INDICES")
    canvas = Image.new("RGB", (1260, 1420), (20, 24, 32))
    pen = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=19)
    small = ImageFont.load_default(size=16)
    pen.text((25, 18), "EP01 V2 - RECORTES CANDIDATOS - SEM APROVACAO", font=font, fill="white")
    pen.text((25, 52), "A/B: pixels dos originais SHA conferidos; areas estimadas da prancha, nao mascaras validadas.", font=small, fill=(221, 199, 159))
    results = []
    for i, row in enumerate(pairs):
        actor = row["actor"]
        region = row["semantic_region"]
        y = 92 + i * 331
        pen.text((25, y), f"{actor.upper()} / {region} - CONFERIR LIMITES E CONTEUDO", font=font, fill="white")
        sources = []
        for col, name in enumerate(("a", "b")):
            idx = manifest["source_indices"][actor][col]
            source = inventory["previews"][actor]["sources"][idx]
            original = verified_file(ep, source["path"], source["sha256"], image_only=True)
            vertices = board_to_source(row["board_points_" + name], original.size, idx)
            pixels = count_mask_pixels(original.size, vertices)
            tile = patch(original, vertices)
            x = 25 + col * 615
            canvas.paste(tile, (x + (560 - tile.width)//2, y + 37))
            pen.text((x, y+268), f"{name.upper()} - {source['label'][:43]}", font=small, fill="white")
            pen.text((x, y+292), "SHA " + source["sha256"][:30], font=small, fill=(184, 203, 219))
            sources.append({
                "side": name, "path": source["path"], "sha256": source["sha256"],
                "dimensions": list(original.size),
                "candidate_polygon_native_px": [list(p) for p in vertices],
                "candidate_mask_pixels": pixels,
                "pose_semantically_verified": False,
                "mask_semantically_verified": False,
                "approved_for_color_comparison": False,
            })
        results.append({"actor": actor, "semantic_region": region,
                        "status": "CANDIDATO_NAO_VERIFICADO", "sources": sources,
                        "automatic_approved": False})
    pen.text((25, 1392), "QA SEM IA | R2 BLOQUEADA | 0 ROIs VERIFICADAS | REPROVACAO ANTERIOR MANTIDA", font=small, fill=(250, 206, 130))
    out = io.BytesIO()
    canvas.save(out, "JPEG", quality=87, optimize=True)
    report = {
        "schema": "videoforge/roi-candidate-preview/v1",
        "status": "EIGHT_CANDIDATE_MASKS_PENDING_SEMANTIC_REVIEW",
        "candidates": results,
        "candidate_count": 8, "validated_pair_count": 0,
        "automatic_approvals": 0, "r2_blocked": True,
        "original_images_modified": False, "paid_calls": 0,
        "mp4_created": False, "youtube_uploaded": False,
    }
    if sync:
        payloads = {
            ep / PREVIEW: out.getvalue(),
            ep / REPORT: (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode(),
        }
        for path, blob in payloads.items():
            if path.is_symlink():
                raise VideoForgeError("ROI_CANDIDATE_OUTPUT_SYMLINK")
            if not path.is_file() or path.read_bytes() != blob:
                path.write_bytes(blob)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    data = run(sync=args.sync)
    print("ROI_CANDIDATES", json.dumps({
        "candidates": data["candidate_count"],
        "verified": data["validated_pair_count"],
        "paid_calls": 0, "r2_blocked": True,
    }))


if __name__ == "__main__":
    main()
