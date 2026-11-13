"""Validacao fail-closed dos sprites para rig 2D Remotion (sem inferencia IA).

O manifesto e entregue junto de 5 PNGs RGBA de tamanho integral.
Hashes e alpha nao substituem a revisao visual de sobreposicao/oclusao.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from . import scene_layers
from .errors import VideoForgeError

SCHEMA = "videoforge/mesh-rig-assets/v1"
RIG_SCHEMA = "videoforge/mesh-rig/v1"
ASSET_NAMES = {
    "body": "body-no-head-no-cape.png",
    "head": "head-no-eyes.png",
    "eyesOpen": "eyes-open.png",
    "eyesClosed": "eyes-closed.png",
    "cape": "cape.png",
}


class RigAssetError(VideoForgeError):
    pass


def _number(value: object, minimum: float, maximum: float) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or
            not math.isfinite(value) or not minimum <= value <= maximum):
        raise RigAssetError("RIG_NUMERIC_PARAMETER_INVALID")
    return float(value)


def _integer(value: object, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise RigAssetError("RIG_INTEGER_PARAMETER_INVALID")
    return value


def _sha(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise RigAssetError("RIG_HASH_INVALID")
    return value


def validate_rig_dir(directory: Path, *, channel: str, video_id: str,
                     scene: str, source_sha: str, width: int, height: int,
                     duration_frames: int) -> dict:
    """Retorna props seguros e caminhos fixos; nunca interpreta paths do JSON."""
    if directory.is_symlink() or not directory.is_dir():
        raise RigAssetError("RIG_DIRECTORY_MISSING_OR_SYMLINK")
    path = directory / "rig.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 20_000:
        raise RigAssetError("RIG_MANIFEST_MISSING_OR_UNSAFE")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise RigAssetError("RIG_MANIFEST_INVALID_JSON") from exc
    if not isinstance(raw, dict) or raw.get("schema") != SCHEMA:
        raise RigAssetError("RIG_SCHEMA_INVALID")
    if (raw.get("channel"), raw.get("video_id"), raw.get("scene")) != (channel, video_id, scene):
        raise RigAssetError("RIG_CROSS_CHANNEL_OR_SCENE")
    if _sha(raw.get("source_sha256")) != source_sha:
        raise RigAssetError("RIG_SOURCE_HASH_MISMATCH")
    if raw.get("canvas") != {"width": width, "height": height}:
        raise RigAssetError("RIG_CANVAS_MISMATCH")
    review = raw.get("human_review")
    if not isinstance(review, dict) or any(
        review.get(k) is not True for k in
        ("no_duplicate_parts", "pixel_alignment", "occlusion_order")
    ):
        raise RigAssetError("RIG_HUMAN_ASSET_REVIEW_REQUIRED")
    hashes = raw.get("assets")
    optional_assets = {"cape-front.png": "capeFront", "head-open.png": "headOpen", "head-closed-ai.png": "headClosed"}
    expected_names = set(ASSET_NAMES.values())
    if isinstance(hashes, dict):
        expected_names.update(name for name in optional_assets if name in hashes)
    if not isinstance(hashes, dict) or set(hashes) != expected_names:
        raise RigAssetError("RIG_ASSET_LIST_INVALID")
    verified_hashes = {}
    for name in sorted(expected_names):
        expected = _sha(hashes[name])
        asset = directory / name
        data = scene_layers._read_png(asset)
        if hashlib.sha256(data).hexdigest() != expected:
            raise RigAssetError("RIG_ASSET_HASH_MISMATCH")
        info = scene_layers.png_info(
            data, require_alpha=True,
            min_visible_fraction=.00001 if name.startswith('eyes-') else .005,
        )
        if (info["width"], info["height"]) != (width, height):
            raise RigAssetError("RIG_ASSET_CANVAS_MISMATCH")
        verified_hashes[name] = expected
    if len(set(verified_hashes.values())) != len(verified_hashes):
        raise RigAssetError("RIG_DUPLICATE_ASSET_FILE")

    pivot = raw.get("neck_pivot")
    if not isinstance(pivot, dict):
        raise RigAssetError("RIG_NECK_PIVOT_REQUIRED")
    neck = {"x": _number(pivot.get("x"), 0, width),
            "y": _number(pivot.get("y"), 0, height)}
    angle = _number(raw.get("head_max_deg"), .05, 2.0)
    blinks = raw.get("blink_frames")
    if not isinstance(blinks, list) or not 1 <= len(blinks) <= 10:
        raise RigAssetError("RIG_BLINK_FRAMES_REQUIRED")
    blink_frames = [_integer(f, 4, duration_frames - 5) for f in blinks]
    if any(b - a < 12 for a, b in zip(blink_frames, blink_frames[1:])):
        raise RigAssetError("RIG_BLINK_FRAMES_TOO_CLOSE_OR_UNSORTED")

    mesh = raw.get("cape_mesh")
    if not isinstance(mesh, dict) or not isinstance(mesh.get("bounds"), dict):
        raise RigAssetError("RIG_CAPE_BOUNDS_REQUIRED")
    b = mesh["bounds"]
    bounds = {
        "x": _number(b.get("x"), 0, width - 10),
        "y": _number(b.get("y"), 0, height - 10),
        "width": _number(b.get("width"), 10, width),
        "height": _number(b.get("height"), 10, height),
    }
    if bounds["x"] + bounds["width"] > width or bounds["y"] + bounds["height"] > height:
        raise RigAssetError("RIG_CAPE_BOUNDS_OUT_OF_CANVAS")
    columns = _integer(mesh.get("columns"), 2, 6)
    rows = _integer(mesh.get("rows"), 2, 8)
    amplitude = _number(mesh.get("amplitude_px"), .1, 12)
    layers = {key: "vf-scene/rig/" + filename for key, filename in ASSET_NAMES.items()}
    for filename, key in optional_assets.items():
        if filename in expected_names:
            layers[key] = "vf-scene/rig/" + filename
    return {
        "schema": RIG_SCHEMA,
        "canvas": {"width": width, "height": height},
        "layers": layers,
        "neckPivot": neck,
        "headMaxDeg": angle,
        "blinkFrames": blink_frames,
        "capeMesh": {"bounds": bounds, "columns": columns, "rows": rows,
                     "amplitudePx": amplitude},
    }
