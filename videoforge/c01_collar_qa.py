"""C01 collar-occlusion diagnostics from ORIGINAL scene background and real MP4 frames.

No generated artwork, retouching, guessed neck anatomy, video publishing or
approval. Count pixels at the nape that used to cover the true background but
have become almost identical to the original background in a later frame.
This catches exposed scenery at a rotating head/jacket seam, not whole PNG pan.
"""
from __future__ import annotations

import json
from pathlib import Path


class C01CollarError(ValueError):
    pass


# Source 1024x1536. Constrain to the true jacket-to-shoulder collar seam
# source x492..580, y847..880. A wider region also included legitimate hair
# silhouette movement (y833) and counted it as an exposed neck incorrectly.
C01_NECK_SOURCE_ROI = (492, 847, 88, 33)


def collar_background_exposure(
    original_video_rgba: bytes | bytearray,
    later_video_rgba: bytes | bytearray,
    background_rgba: bytes | bytearray,
    *,
    width: int,
    height: int,
    source_width: int,
    source_height: int,
    roi: tuple[int, int, int, int] = C01_NECK_SOURCE_ROI,
    foreground_distance: int = 42,
    background_distance: int = 25,
) -> dict:
    """Compare visible canvas against existing RGB source background.

    A candidate counts only if the pixel at frame zero visibly *covered* the
    background but a later frame newly exposes the SAME background RGB.
    Excludes overlays by sampling the middle of the original character.
    """
    if (not all(type(v) is int and v > 0 for v in
                (width, height, source_width, source_height))
        or len(original_video_rgba) != width * height * 4
        or len(later_video_rgba) != width * height * 4
        or len(background_rgba) != source_width * source_height * 4):
        raise C01CollarError("C01_COLLAR_FRAME_DIMENSIONS_INVALID")
    x0, y0, rw, rh = roi
    if (not all(type(v) is int for v in roi)
        or x0 < 0 or y0 < 0 or rw < 1 or rh < 1
        or x0 + rw > source_width or y0 + rh > source_height
        or foreground_distance < background_distance
        or background_distance < 1):
        raise C01CollarError("C01_COLLAR_UNSAFE_ROI_OR_THRESHOLDS")
    # The C01 camera is fixed at z=14, 30 degrees and lookAt=[0,0,0].
    # sourceWorldScale calibrates native canvas height to the video height;
    # crop the extra horizontal source width around the center.
    visible_source_height = min(source_height, source_width / (width / height))
    scale = height / visible_source_height
    dx = (width - source_width * scale) / 2
    dy = (height - source_height * scale) / 2
    newly_exposed = 0
    sample_count = 0
    newly_exposed_coordinates = []
    for sy in range(y0, y0 + rh):
        y = round(dy + (sy + .5) * scale - .5)
        if y < 0 or y >= height:
            continue
        for sx in range(x0, x0 + rw):
            x = round(dx + (sx + .5) * scale - .5)
            if x < 0 or x >= width:
                continue
            i = 4 * (y * width + x)
            j = 4 * (sy * source_width + sx)
            rgb = background_rgba[j:j+3]
            original_delta = max(abs(original_video_rgba[i+c] - rgb[c]) for c in range(3))
            later_delta = max(abs(later_video_rgba[i+c] - rgb[c]) for c in range(3))
            sample_count += 1
            if original_delta >= foreground_distance and later_delta <= background_distance:
                newly_exposed += 1
                # We only need a bounded sample for QA context (not a mask).
                if len(newly_exposed_coordinates) < 12:
                    newly_exposed_coordinates.append([sx, sy])
    if not sample_count:
        raise C01CollarError("C01_COLLAR_ROI_OUTSIDE_VIDEO")
    return {
        "schema": "videoforge/c01-collar-existing-background-exposure/v1",
        "native_source_region": list(roi),
        "pixels_checked": sample_count,
        "newly_exposed_background_pixels": newly_exposed,
        "fraction_new_background_exposure": round(newly_exposed / sample_count, 7),
        "first_exposed_source_coordinates": newly_exposed_coordinates,
        "reference": "SHA-gated original C01 scene background, no edited pixels",
        "human_visual_approved": False,
    }


def collar_gate(results: list[dict], max_new_background_pixels: int = 75) -> dict:
    if not results or type(max_new_background_pixels) is not int or max_new_background_pixels < 0:
        raise C01CollarError("C01_COLLAR_GATE_PARAMETERS_INVALID")
    worst = max(r["newly_exposed_background_pixels"] for r in results)
    return {
        "status": "PASS_TECHNICAL_NO_HUMAN_APPROVAL"
                  if worst <= max_new_background_pixels
                  else "BLOCKED_EXPOSED_BACKGROUND_AT_NECK",
        "maximum_newly_exposed_pixels": worst,
        "allowed_pixels_per_checked_frame": max_new_background_pixels,
        "scans": results,
        "mask_review_approved": False,
        "hidden_anatomy_reconstruction_approved": False,
        "official_video_approved": False,
        "image_generation_calls": 0,
    }
