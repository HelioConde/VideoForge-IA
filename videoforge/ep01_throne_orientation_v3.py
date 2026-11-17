"""Corrigir eixo de Kael voltado ao trono nas cenas C01-P03 / C01-P04.

Versão V3 é gerada pelo proxy a partir das mães V2 arquivadas e das
referências SHA-verificadas da Bíblia. Não transporta imagens do chat,
não sobrescreve originais, não extrai sprites e não aprova rig/MP4.
Uma chamada de imagem por execução.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from . import image_generation_policy, proxy_images
from .errors import VideoForgeError
from .ep01_shot_mother import read_refs, MAX_REFERENCE_PNGS_PER_REQUEST
from .production_art import archived_reference
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO, validate as validate_plan
from .scene_layers import png_info

PRODUCER = "production-scene-mother-orientation-v3"
SCHEMA = "videoforge/ep01-throne-facing-mother-v3/v1"

SOURCE_SHOTS = {
    "C01-P03": {
        "shot": "C01-P03",
        "source": "assets/geracoes/production-scene-mother-repair-v2/44080234599/c01-p03-scene-mother-v2.png",
        "sha256": "bfc1249dc1f83b004b620c333f5aa81689b0ba0c23a3e7573d57c09dcf3539e3",
        "asset": "c01-p03-scene-mother-facing-throne-v3",
        "cast": "Kael and standing king Aldric only. No guards, spears, swords or executioner.",
        "direction": (
            "Low-angle dramatic kneeling audience: Aldric STANDING on throne steps, "
            "Kael KNEELING on one knee at foreground facing TOWARD Aldric and the "
            "throne in the UPPER CENTRAL PART OF THE IMAGE. Rotate Kael torso, "
            "hips, knees, head AND gaze to royal authority. Camera to his front-"
            "side enables legible THREE-QUARTER cheek/profile, but Kael must NEVER "
            "turn his back toward the throne or look off to the side. "
            "Do not move Aldric to the center foreground or place him sitting."
        ),
    },
    "C01-P04": {
        "shot": "C01-P04",
        "source": "assets/geracoes/production-scene-mother-v2-aligned/44080887693/c01-p04-scene-mother-v2-native-aligned-v1.png",
        "sha256": "2d11099a536999409a33dae2fc30c517e260c4ad640e41c6942c85b9db499ec5",
        "asset": "c01-p04-scene-mother-facing-throne-v3",
        "cast": "Kael kneeling, king Aldric SEATED, exactly two guards on either side with one spear each.",
        "direction": (
            "Wide full throne-room scene. Kael KNEELS in lower center foreground, "
            "whole torso and hips oriented UP THE STAIRS to the SEATED KING and throne. "
            "He looks at Aldric, not sideways away from him and never with his BACK "
            "to the king. Use a 3/4 camera angle, so some profile is visible. "
            "Two armored guards in mirror spacing EACH grasp their OWN long portable "
            "spear by the LOWER THIRD / BASE of the shaft: real fingers and thumbs "
            "wrapped around solid wood, hands connected to gauntlets/forearms, "
            "never hands floating or grip in middle of pole. Spear tips form an X "
            "HIGH ABOVE Kael, no impaling or overlapping Kael's head. "
            "King seated on same central red-gold throne."
        ),
    },
    "C01-P04-ALT": {
        "shot": "C01-P04",
        "source": "assets/geracoes/production-scene-mother-v2-aligned/44080887693/c01-p04-scene-mother-v2-native-aligned-v1.png",
        "sha256": "2d11099a536999409a33dae2fc30c517e260c4ad640e41c6942c85b9db499ec5",
        "asset": "c01-p04-scene-mother-facing-throne-v3-alt",
        "cast": "Kael kneeling; king Aldric seated; two guards, one on each side; exactly two spears.",
        "direction": (
            "ALTERNATE TAKE of the same wide royal hearing with camera slightly "
            "lower and offset to Kael's front-right. Kael still faces directly "
            "toward the king on central high throne, looks up from a realistic "
            "one-knee-down pose; 3/4 view reveals part of his face, never his back "
            "toward the throne. Preserve throne/stair geometry and all costumes. "
            "Both guards stand by stairs, hold ONE spear each at lower shaft/base "
            "with anatomically closed fingers, pole tips crossed in X high behind "
            "Kael. No floating poles, duplicated hands or extra weapons."
        ),
    },
}

def safe_png(relative: str, expected_sha: str, root: Path) -> bytes:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.suffix.lower() != ".png":
        raise VideoForgeError("THRONE_V3_SOURCE_PATH_REJECTED")
    p = root / REL / path
    if p.is_symlink() or not p.is_file() or p.stat().st_size > 35_000_000:
        raise VideoForgeError("THRONE_V3_REFERENCE_MISSING")
    blob = p.read_bytes()
    if hashlib.sha256(blob).hexdigest() != expected_sha:
        raise VideoForgeError("THRONE_V3_REFERENCE_SHA_MISMATCH")
    info = png_info(blob, require_alpha=False)
    if info["width"] < 512 or info["height"] < 512:
        raise VideoForgeError("THRONE_V3_REFERENCE_CANVAS_INVALID")
    return blob


def archived(target: str, root: Path = ROOT) -> dict | None:
    spec = SOURCE_SHOTS[target]
    dest = Path(root) / REL / "assets" / "geracoes" / PRODUCER
    if not dest.exists():
        return None
    matches = []
    filename = spec["asset"] + ".png"
    for folder in dest.iterdir():
        if folder.is_symlink():
            raise VideoForgeError("THRONE_V3_ARCHIVE_SYMLINK")
        if not folder.is_dir() or not folder.name.isdecimal():
            continue
        file = folder / filename
        if not file.exists():
            continue
        manifest = folder / "manifesto-geracoes.json"
        if file.is_symlink() or not manifest.is_file():
            raise VideoForgeError("THRONE_V3_ARCHIVE_INCOMPLETE")
        m = json.loads(manifest.read_text(encoding="utf-8"))
        sha = hashlib.sha256(file.read_bytes()).hexdigest()
        rows = [x for x in m.get("images", []) if x.get("file") == filename]
        if (m.get("producer") != PRODUCER or m.get("channel") != CHANNEL
                or m.get("video_id") != VIDEO or len(rows) != 1
                or rows[0].get("sha256") != sha):
            raise VideoForgeError("THRONE_V3_ARCHIVE_PROVENANCE_INVALID")
        matches.append({"run_id": int(folder.name), "sha256": sha})
    return max(matches, key=lambda x: x["run_id"]) if matches else None


def prepare(target: str, root: Path = ROOT) -> dict:
    root = Path(root)
    if target not in SOURCE_SHOTS:
        raise VideoForgeError("THRONE_V3_TARGET_INVALID")
    image_generation_policy.assert_image_generation_allowed(CHANNEL, VIDEO, root)
    validate_plan(root)
    if archived(target, root):
        raise VideoForgeError("THRONE_V3_ALREADY_ARCHIVED_NO_REPEAT")
    entry = SOURCE_SHOTS[target]
    old_source = safe_png(entry["source"], entry["sha256"], root)
    refdoc = read_refs(root)
    shot = next(x for x in refdoc["shots"] if x["id"] == entry["shot"])
    refs = []
    raws = []
    for asset in shot["reference_asset_ids"]:
        item = archived_reference(CHANNEL, VIDEO, asset, root)
        if not item:
            raise VideoForgeError("THRONE_V3_BIBLE_ASSET_MISSING " + asset)
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise VideoForgeError("THRONE_V3_BIBLE_PATH_REJECTED")
        raw = safe_png(relative.as_posix(), item["sha256"], root)
        refs.append({"asset_id": asset, "sha256": item["sha256"],
                     "path": (REL / relative).as_posix()})
        raws.append(raw)
    if not 1 <= len(refs) + 1 <= MAX_REFERENCE_PNGS_PER_REQUEST:
        raise VideoForgeError("THRONE_V3_REFERENCE_COUNT_INVALID")
    prompt = (
        "Make ONE corrected cinematic 9:16 FULL-FRAME anime/manhwa semi-realistic "
        "2D fantasy mother image by EDITING IMAGE ONE (V2) while comparing the "
        "attached SHA-verified Visual Bible reference images. Preserve the exact "
        "character design, outfits, crimson/gold and violet stained-glass palette, "
        "lighting, red carpet, throne architecture and reflections. "
        "The decisive correction is NARRATIVE SPATIAL ORIENTATION: a kneeling "
        "character should FACE the THRONE / KING as a person addressing authority, "
        "NOT face away or look in an unrelated direction. Three-quarter camera "
        "view must never change Kael's physical facing direction away from king. "
        + entry["direction"] + " CAST: " + entry["cast"] + " "
        "This is a SINGLE cinematic camera frame, NOT a poster or collage. "
        "Keep both knee/foot contacts physically grounded and costume consistent; "
        "no extra limbs, dislocated hands, floating spears, merged weapons, "
        "illogical cloth intersections, wrong grip, new characters or props. "
        "No words, no HUD, no bubbles, no watermark and no storyboard layout. "
        "Only the mother image is requested: transparent layers, rigs and animations "
        "are generated SEPARATELY by proxy after specific visual approval; "
        "NEVER use a local pixel crop as a final animation source. "
        "Candidate for human QA only. NO automatic approval."
    )
    if len(prompt) > 5000:
        raise VideoForgeError("THRONE_V3_PROMPT_TOO_LONG")
    return {"target": target, "asset": entry["asset"], "shot": entry["shot"],
            "source_sha": entry["sha256"], "source_path": entry["source"],
            "references": refs, "images": [old_source] + raws, "prompt": prompt}


def generate(target: str, url: str, model: str = "gpt-image-2",
             root: Path = ROOT) -> dict:
    if model != "gpt-image-2":
        raise VideoForgeError("THRONE_V3_MODEL_INVALID")
    spec = prepare(target, root)
    directory = Path(root) / "output" / CHANNEL / "videos" / VIDEO / "imagens"
    image = directory / (spec["asset"] + ".png")
    proof = directory / (spec["asset"] + ".production.json")
    if any(p.exists() or p.is_symlink() for p in (image, proof)):
        raise VideoForgeError("THRONE_V3_OUTPUT_EXISTS")
    payload = {
        "model": model, "n": 1, "size": "1024x1536",
        "background": "opaque", "output_format": "png",
        "response_format": "b64_json", "stream": False,
        "prompt": spec["prompt"],
        "images": [{"image_url": "data:image/png;base64," +
                    base64.b64encode(img).decode("ascii")} for img in spec["images"]],
    }
    reply = proxy_images.call_proxy(
        url, "/v1/images/edits", os.getenv("CODEX_PROXY_API_KEY", ""), payload)
    blob, ext = proxy_images.decode_image(reply)
    if ext != ".png":
        raise VideoForgeError("THRONE_V3_NON_PNG_OUTPUT")
    info = png_info(blob, require_alpha=False)
    if not 512 <= info["width"] <= 2048 or not 512 <= info["height"] <= 3072:
        raise VideoForgeError("THRONE_V3_CANVAS_INVALID")
    directory.mkdir(parents=True, exist_ok=True)
    image.write_bytes(blob)
    digest = hashlib.sha256(blob).hexdigest()
    qa = ("valid_png_provenance_visual_review_pending" if info["width"] == 941
          and info["height"] == 1672 else "canvas_mismatch_review_pending")
    result = {
        "schema": SCHEMA, "channel": CHANNEL, "video_id": VIDEO,
        "asset_id": spec["asset"], "candidate_scene_shot_id": spec["shot"],
        "target_variant": target,
        "source_image_sha256": spec["source_sha"],
        "source_path": str((REL / spec["source_path"]).as_posix()),
        "source_images_attached_to_request": len(spec["images"]),
        "source_originals_sha_verified": spec["references"],
        "file": str(image.relative_to(root).as_posix()),
        "sha256": digest, "width": info["width"], "height": info["height"],
        "technical_qa": qa, "generation_method": "proxy_edit_full_mother_with_bible",
        "human_visual_approval": False, "rig_ready": False,
        "mp4_generated": False, "youtube_uploaded": False,
        "provider_image_calls": 1,
    }
    proof.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n",
                     encoding="utf-8")
    print("EP01_THRONE_ORIENTATION_V3", json.dumps(
        {"target": target, "sha256": digest, "qa": qa,
         "images": len(spec["images"]), "approved": False}, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, choices=SOURCE_SHOTS.keys())
    parser.add_argument("--url", required=True)
    parser.add_argument("--model", default="gpt-image-2")
    args = parser.parse_args()
    try:
        generate(args.target, args.url, args.model)
    except (OSError, ValueError, VideoForgeError, proxy_images.ProxyImageError) as exc:
        print("EP01_THRONE_V3_STOPPED", str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
