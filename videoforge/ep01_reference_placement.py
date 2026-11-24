"""Offline, versioned reference-canvas placement for EP01.

Never produces a sprite or authorizes a provider call. The original PNG bytes
are immutable. The padded PNG is a reference-only derivative, not production art.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json

from .errors import VideoForgeError
from .ep01_proxy_separate_parts import exact_canvas_size, mother_source

SCHEMA = "videoforge/ep01-reference-placement/v1"


def plan_placement(dimensions):
    """Minimum multiple-of-16 padding only; no scaling or orientation change.

    Do not enlarge tiny/oversized/extreme-ratio sources to force eligibility.
    """
    if (not isinstance(dimensions, (tuple, list)) or len(dimensions) != 2
            or any(type(edge) is not int or not 0 < edge <= 3840 for edge in dimensions)):
        raise VideoForgeError("EP01_REFERENCE_PLACEMENT_INVALID_SOURCE")
    w, h = dimensions
    pw, ph = ((w + 15) // 16 * 16, (h + 15) // 16 * 16)
    size = exact_canvas_size((pw, ph))
    if ((w > h) != (pw > ph) or (w < h) != (pw < ph)):
        raise VideoForgeError("EP01_REFERENCE_PLACEMENT_ORIENTATION_CHANGED")
    left, top = (pw - w) // 2, (ph - h) // 2
    return {
        "schema": SCHEMA,
        "source_canvas": [w, h],
        "reference_canvas": [pw, ph],
        "requested_size_candidate": size,
        "source_rect_xyxy": [left, top, left + w, top + h],
        "padding_ltrb": [left, top, pw - w - left, ph - h - top],
        "source_to_reference_offset_xy": [left, top],
        "reference_to_source_offset_xy": [-left, -top],
        "scale_xy": [1, 1],
        "reference_only": True,
        "provider_calls": 0,
        "generation_authorized": False,
        "placement_verified": False,
        "human_visual_approval": False,
        "rig_ready": False,
        "youtube_uploaded": False,
    }


def prepare_reference(raw: bytes, expected_sha256: str):
    """Return reference PNG + manifest after proving pixel identity in source rect."""
    from PIL import Image
    source_sha = hashlib.sha256(raw).hexdigest()
    if source_sha != expected_sha256:
        raise VideoForgeError("EP01_REFERENCE_PLACEMENT_SOURCE_SHA_MISMATCH")
    with Image.open(io.BytesIO(raw)) as source:
        if source.format != "PNG" or getattr(source, "n_frames", 1) != 1:
            raise VideoForgeError("EP01_REFERENCE_PLACEMENT_EXPECTED_STATIC_PNG")
        if source.mode not in ("RGB", "RGBA"):
            raise VideoForgeError("EP01_REFERENCE_PLACEMENT_UNSUPPORTED_PIXEL_MODE")
        plan = plan_placement(source.size)
        source.load()
        rgba = source.convert("RGBA")
        padded = Image.new("RGBA", tuple(plan["reference_canvas"]), (0, 0, 0, 0))
        # No alpha mask argument: copy even RGB values of fully transparent pixels.
        padded.paste(rgba, tuple(plan["source_to_reference_offset_xy"]))
        stream = io.BytesIO()
        padded.save(stream, format="PNG")
        reference = stream.getvalue()
        # QA-only crop, never used to construct generated art or sprites.
        with Image.open(io.BytesIO(reference)) as reopened:
            reopened.load()
            if reopened.crop(tuple(plan["source_rect_xyxy"])).tobytes() != rgba.tobytes():
                raise VideoForgeError("EP01_REFERENCE_PLACEMENT_PIXEL_MISMATCH")
    plan.update(source_sha256=source_sha,
                reference_sha256=hashlib.sha256(reference).hexdigest(),
                source_rect_pixels_verified=True,
                padding_fill_rgba=[0, 0, 0, 0])
    return reference, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shot-id", required=True)
    args = parser.parse_args()
    raw, proof = mother_source(args.shot_id)
    _, plan = prepare_reference(raw, proof["sha256"])
    plan["shot_id"] = args.shot_id
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
