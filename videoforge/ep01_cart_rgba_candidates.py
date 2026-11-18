"""Source-faithful, UNAPPROVED RGBA segmentation candidates for EP01 C08-P02.

Uses only the pinned archive PNG, OpenCV seeded GrabCut and Telea underlay.
Outputs seven actual full-canvas RGBA images, QA and visual overlays to a
separate artifact directory. The pixels at the original pose recompose
losslessly by design, but the newly revealed underlay and semantic edges
are NOT guaranteed correct, so this cannot approve a rig or final scene.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .ep01_continuity_motion import ROOT, EP, read as read_motion

SOURCE = EP / "assets/geracoes/production-continuity-v2-mother/44265114014/c08-p02-continuity-v2-scene-mother.png"
BIBLE_STATUS = ROOT / "canal/alchemy-lab/biblia-visual/objetos/carrinho/status.json"
TEMPLATE = (320, 452)  # coordinate system is the uncropped C08-P02 photo
PIECES = (
    "kael_connected_body_rgba",
    "cart_chassis_rgba",
    "wheel_left_rgba",
    "wheel_right_rgba",
    "kael_grip_integrated_rgba",
    "cart_front_occlusion_rgba",
)
ALL_LAYERS = ("alley_reconstructed_rgba", *PIECES)
# Loose artist-facing seed regions, NOT approved silhouettes/semantic masks.
POLYGONS = {
    "kael_connected_body_rgba": (
        (0, 174), (35, 200), (84, 188), (118, 170), (147, 168),
        (169, 190), (173, 224), (147, 246), (165, 285),
        (146, 336), (125, 394), (96, 399), (76, 379),
        (54, 345), (23, 319), (0, 295),
    ),
    "cart_chassis_rgba": (
        (175, 183), (319, 180), (319, 309), (277, 322),
        (235, 302), (214, 286), (185, 267),
    ),
    "kael_grip_integrated_rgba": (
        (151, 192), (184, 191), (205, 204), (213, 249),
        (186, 268), (160, 252), (147, 225),
    ),
    "cart_front_occlusion_rgba": (
        (241, 279), (319, 294), (319, 445), (286, 388),
        (262, 330),
    ),
}
ELLIPSES = {
    "wheel_left_rgba": ((188, 319), (34, 82)),
    "wheel_right_rgba": ((291, 325), (27, 50)),
}
# Disjoint pixel ownership; the body can never overwrite the connected grip.
PRIORITY = (
    "wheel_left_rgba", "wheel_right_rgba", "kael_grip_integrated_rgba",
    "cart_front_occlusion_rgba", "cart_chassis_rgba",
    "kael_connected_body_rgba",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pinned_source(root: Path = ROOT) -> tuple[Path, str]:
    root = root.resolve()
    path = root / SOURCE
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to((root / EP).resolve()):
        raise ValueError("Original art is missing, is a symlink, or escaped the episode")
    plan = read_motion(root)
    expected = plan["source_reference_shas"]["C08-P02"]
    if (plan["rules"]["allow_image_generation"] is not False
            or plan["rules"]["never_modify_original_png"] is not True
            or plan["QA"]["art_approval"] is not False
            or plan["QA"]["rig_ready"] is not False
            or expected["asset"] != SOURCE.relative_to(EP).as_posix()
            or sha256(path) != expected["sha256"]):
        raise ValueError("C08-P02 source art changed or was unexpectedly approved")
    bible = root / "canal/alchemy-lab/biblia-visual/objetos/carrinho/status.json"
    if (bible.is_symlink() or not bible.is_file()
            or json.loads(bible.read_text(encoding="utf-8")).get("aprovacao_mestra") is not False):
        raise ValueError("Visual-bible master approval changed: independent review is mandatory")
    return path, expected["sha256"]


def seed_mask(name: str) -> np.ndarray:
    canvas = np.zeros((TEMPLATE[1], TEMPLATE[0]), dtype=np.uint8)
    if name in POLYGONS:
        cv2.fillPoly(canvas, [np.array(POLYGONS[name], dtype=np.int32)], 255)
    elif name in ELLIPSES:
        center, axes = ELLIPSES[name]
        cv2.ellipse(canvas, center, axes, 0, 0, 360, 255, -1)
    else:
        raise ValueError("Unknown cart part")
    if np.count_nonzero(canvas) < 300:
        raise ValueError("Seed region is empty")
    return canvas


def refine_candidate(small_bgr: np.ndarray, seed: np.ndarray) -> tuple[np.ndarray, str]:
    """Refine contours; if OpenCV rejects seed topology retain explicit seed.

    A fallback is always reported for review, never silently approved.
    """
    fg_core = cv2.erode(seed, np.ones((9, 9), np.uint8), iterations=1)
    near = cv2.dilate(seed, np.ones((23, 23), np.uint8), iterations=1)
    mask = np.full(seed.shape, cv2.GC_BGD, dtype=np.uint8)
    mask[near != 0] = cv2.GC_PR_BGD
    mask[seed != 0] = cv2.GC_PR_FGD
    mask[fg_core != 0] = cv2.GC_FGD
    bg_model, fg_model = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(small_bgr, mask, None, bg_model, fg_model, 3, cv2.GC_INIT_WITH_MASK)
        refined = np.isin(mask, [cv2.GC_FGD, cv2.GC_PR_FGD]).astype(np.uint8) * 255
        if np.count_nonzero(refined) >= 250:
            return refined, "grabcut_seed_refinement_unreviewed"
    except cv2.error:
        pass
    return seed.copy(), "polygon_fallback_needs_contour_review"


def make_masks(src_bgr: np.ndarray) -> tuple[dict[str, np.ndarray], dict]:
    if src_bgr.dtype != np.uint8 or src_bgr.ndim != 3 or src_bgr.shape[2] != 3:
        raise ValueError("Only three-channel source photos are supported")
    h, w = src_bgr.shape[:2]
    if (w, h) != (1053, 1493):
        raise ValueError("C08-P02 native PNG dimensions changed")
    small = cv2.resize(src_bgr, TEMPLATE, interpolation=cv2.INTER_AREA)
    owned = np.zeros((h, w), dtype=np.bool_)
    masks = {}
    statuses = {}
    for part in PRIORITY:
        mask, statuses[part] = refine_candidate(small, seed_mask(part))
        native = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST) > 0
        native &= ~owned
        count = int(np.count_nonzero(native))
        if count < w * h * 0.0005 or count > w * h * 0.24:
            raise ValueError(f"Unreasonable unreviewed area for {part}: {count} pixels")
        masks[part] = native
        owned |= native
    total = int(np.count_nonzero(owned))
    if total < w * h * 0.07 or total > w * h * 0.60:
        raise ValueError("Candidate segmentation has implausible total coverage")
    return masks, {
        "mask_methods": statuses,
        "candidate_coverage_fraction": round(total / (w * h), 6),
        "mask_ownership_overlaps": 0,
        "native_dimensions": [w, h],
        "seed_template_dimensions": list(TEMPLATE),
    }


def build_candidates(root: Path, output_dir: Path) -> dict:
    src_path, pinned_sha = pinned_source(root)
    if (output_dir.is_symlink() or output_dir.resolve().is_relative_to(root.resolve())
            or output_dir.exists() and any(output_dir.iterdir())):
        raise ValueError("Output must be an empty external directory, never a project source")
    img = cv2.imread(str(src_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Cannot decode archived mother PNG")
    if img.ndim != 3 or img.shape[2] not in (3, 4):
        raise ValueError("Unrecognized original PNG channel count")
    if img.shape[2] == 4:
        if np.any(img[:, :, 3] != 255):
            raise ValueError("Source image unexpectedly contains alpha")
        img = img[:, :, :3].copy()
    masks, info = make_masks(img)
    output_dir.mkdir(parents=True, exist_ok=True)
    total_mask = np.zeros(img.shape[:2], np.uint8)
    for part in PIECES:
        total_mask[masks[part]] = 255
    bg = cv2.inpaint(img, total_mask, 7, cv2.INPAINT_TELEA)
    if not np.array_equal(bg[total_mask == 0], img[total_mask == 0]):
        raise ValueError("Inpainting unexpectedly modified unmasked original background")
    bg_rgba = cv2.cvtColor(bg, cv2.COLOR_BGR2RGBA)
    rgb_original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    layers = {ALL_LAYERS[0]: bg_rgba}
    for part in PIECES:
        mask = masks[part].astype(np.uint8) * 255
        rgba = np.dstack([rgb_original, mask])
        rgba[mask == 0, :3] = 0
        layers[part] = rgba
    reconstructed = bg.copy()
    for part in PIECES:
        reconstructed[masks[part]] = img[masks[part]]
    if not np.array_equal(img, reconstructed):
        raise ValueError("Candidate parts fail bit-exact original-pose recomposition")
    for layer, rgba in layers.items():
        Image.fromarray(rgba, mode="RGBA").save(output_dir / (layer + ".png"))
    # Pixel-verified 1:1 origin view and visual masks for independent review.
    Image.fromarray(cv2.cvtColor(reconstructed, cv2.COLOR_BGR2RGB)).save(
        output_dir / "source-pose-recomposed.png")
    palette = [(243, 88, 96), (65, 169, 254), (252, 198, 81),
               (153, 112, 224), (72, 222, 146), (249, 126, 226)]
    overlay = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
    for index, part in enumerate(PIECES):
        mask = masks[part]
        shade = np.array(palette[index], dtype=np.float32)
        overlay[mask] = overlay[mask] * .65 + shade * .35
    Image.fromarray(np.uint8(np.clip(overlay, 0, 255))).save(
        output_dir / "semantic-mask-overlay.jpg", quality=94)
    board = Image.new("RGB", (960, 3 * 505), (28, 31, 40))
    draw = ImageDraw.Draw(board)
    for i, part in enumerate(PIECES):
        rgba = Image.fromarray(layers[part], mode="RGBA")
        rgba.thumbnail((300, 450))
        tile = Image.new("RGBA", (320, 505), (40, 44, 55, 255))
        tile.alpha_composite(rgba, ((320 - rgba.width) // 2, 45))
        board.paste(tile.convert("RGB"), ((i % 3) * 320, (i // 3) * 505))
        draw.text(((i % 3) * 320 + 6, (i // 3) * 505 + 8),
                  part.replace("_rgba", ""), fill="white")
    board.crop((0, 0, 960, 1010)).save(output_dir / "six-cutouts-contact.jpg", quality=93)
    evidence = {
        "schema": "videoforge/ep01-cart-rgba-candidates/v1",
        "shot_id": "C08-P02",
        "source_path": SOURCE.as_posix(),
        "source_sha256": pinned_sha,
        "source_sha256_after": sha256(src_path),
        "layer_order": list(ALL_LAYERS),
        "layer_output_sha256": {
            part: sha256(output_dir / (part + ".png")) for part in ALL_LAYERS
        },
        "layer_nontransparent_pixels": {
            part: int(np.count_nonzero(layers[part][:, :, 3])) for part in ALL_LAYERS
        },
        "source_pose_recomposes_bit_exact": True,
        "source_pose_pixel_error": 0,
        "background_inpainted_artifact_created": True,
        "background_underlay_art_quality_verified": False,
        "semantic_silhouettes_verified": False,
        "visual_identity_verified": False,
        "original_visual_bible_master_approved": False,
        "independent_visual_qa": "required_not_completed",
        "production_ready": False,
        "rig_ready": False,
        "layer_split_verified": False,
        "physical_animation_applied": False,
        "real_model_requests": 0,
        "new_generated_images": 0,
        "original_png_overwrites": 0,
        "youtube_publications": 0,
        "technical_details": info,
        "limitations": [
            "Native image was segmented with tentative manually seeded OpenCV regions.",
            "Masks may contain incorrect subject edges or wheel interiors.",
            "Underlay is algorithmic inpainting, not validated hidden geometry.",
            "Bit-exact static compositing does not prove independent pose animation.",
            "Kael grip is an integrated region and NOT an independent hand.",
            "C08-P03 requires a separate continuity-and-identity alignment QA.",
        ],
    }
    (output_dir / "qa.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return evidence


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    evidence = build_candidates(ROOT, args.output_dir)
    print(json.dumps({
        "part_candidates": len(evidence["layer_order"]),
        "source_pose_recomposes_bit_exact": evidence["source_pose_recomposes_bit_exact"],
        "native_canvas": evidence["technical_details"]["native_dimensions"],
        "visual_qa_passed": False,
        "rig_approved": False,
        "original_png_overwrites": 0,
        "youtube_publications": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
