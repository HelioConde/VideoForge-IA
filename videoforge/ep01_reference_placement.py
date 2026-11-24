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


def inspect_candidate(raw: bytes, source_raw: bytes, expected_source_sha256: str,
                      reference_manifest: dict, *, role: str) -> dict:
    """Read-only QA of a candidate in the versioned reference coordinate space.

    Rebuild the reference from independently pinned source bytes. Never trust
    offsets, dimensions or approval flags supplied by a candidate's manifest.
    This checks geometry/alpha only, not provider provenance or visual placement.
    """
    from PIL import Image
    if role not in ("background", "character", "object"):
        raise VideoForgeError("EP01_REFERENCE_CANDIDATE_INVALID_ROLE")
    _, verified = prepare_reference(source_raw, expected_source_sha256)
    if (not isinstance(reference_manifest, dict)
            or json.dumps({key: reference_manifest.get(key) for key in verified},
                          sort_keys=True) != json.dumps(verified, sort_keys=True)):
        raise VideoForgeError("EP01_REFERENCE_CANDIDATE_MANIFEST_MISMATCH")
    candidate_sha = hashlib.sha256(raw).hexdigest()
    report = {
        "schema": "videoforge/ep01-reference-candidate-qa/v1",
        "candidate_sha256": candidate_sha,
        "source_sha256": verified["source_sha256"],
        "reference_sha256": verified["reference_sha256"],
        "source_canvas": verified["source_canvas"],
        "expected_canvas": verified["reference_canvas"],
        "candidate_canvas": None,
        "source_rect_xyxy": verified["source_rect_xyxy"],
        "reference_to_source_offset_xy": verified["reference_to_source_offset_xy"],
        "scale_xy": [1, 1],
        "role": role,
        "alpha_bbox_source_xyxy": None,
        "pixels_modified": False,
        "provider_calls": 0,
        "provider_provenance_verified": False,
        "generation_authorized": False,
        "placement_verified": False,
        "human_visual_approval": False,
        "rig_ready": False,
        "youtube_uploaded": False,
    }

    def result(status):
        report["technical_qa"] = status
        report["canvas_alpha_candidate"] = status == "candidate_canvas_alpha_visual_review_required"
        return report

    if candidate_sha in (verified["source_sha256"], verified["reference_sha256"]):
        return result("rejected_source_or_reference_reused")
    try:
        with Image.open(io.BytesIO(raw)) as candidate:
            report["candidate_canvas"] = list(candidate.size)
            if candidate.format != "PNG" or getattr(candidate, "n_frames", 1) != 1:
                return result("rejected_expected_static_png")
            if list(candidate.size) != verified["reference_canvas"]:
                return result("rejected_reference_canvas_mismatch")
            if candidate.mode != "RGBA":
                return result("rejected_no_rgba_channel")
            candidate.load()
            alpha = candidate.getchannel("A")
            left, top, right, bottom = verified["source_rect_xyxy"]
            width, height = candidate.size
            # These crops inspect alpha only; no pixel output or sprite is made.
            margins = ((0, 0, width, top), (0, bottom, width, height),
                       (0, top, left, bottom), (right, top, width, bottom))
            if any(alpha.crop(box).getextrema()[1] != 0 for box in margins
                   if box[0] < box[2] and box[1] < box[3]):
                return result("rejected_nontransparent_reference_padding")
            interior = alpha.crop((left, top, right, bottom))
            low, high = interior.getextrema()
            if high < 128:
                return result("rejected_empty_or_insufficient_alpha")
            if role == "background" and low != 255:
                return result("rejected_background_has_transparent_holes")
            if role != "background" and low != 0:
                return result("rejected_no_transparency_inside_source_rect")
            bbox = interior.getbbox()
            report["alpha_bbox_source_xyxy"] = list(bbox) if bbox else None
    except (OSError, ValueError, Image.DecompressionBombError):
        return result("rejected_unreadable_image")
    return result("candidate_canvas_alpha_visual_review_required")



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--candidate-part", help="Inspect a SHA-verified archived component; no generation")
    args = parser.parse_args()
    raw, proof = mother_source(args.shot_id)
    _, plan = prepare_reference(raw, proof["sha256"])
    plan["shot_id"] = args.shot_id
    plan["source_proof"] = proof
    if args.candidate_part:
        from .ep01_proxy_separate_parts import ROOT, existing_part, read_shot
        item = existing_part(args.shot_id, args.candidate_part)
        if not item:
            raise VideoForgeError("EP01_REFERENCE_CANDIDATE_NOT_ARCHIVED")
        path = ROOT / item["file"]
        meta_path = path.with_suffix(".production.json")
        if meta_path.is_symlink() or meta_path.stat().st_size > 2_000_000:
            raise VideoForgeError("EP01_REFERENCE_CANDIDATE_UNSAFE_METADATA")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if (meta.get("source_mother_sha256") != proof["sha256"]
                or meta.get("sha256") != item["sha256"]
                or meta.get("asset_id") != item["asset_id"]):
            raise VideoForgeError("EP01_REFERENCE_CANDIDATE_ARCHIVE_SOURCE_MISMATCH")
        _, request = read_shot(args.shot_id, args.candidate_part)
        qa = inspect_candidate(path.read_bytes(), raw, proof["sha256"], plan,
                               role=request["role"])
        qa["archived_candidate_proof"] = item
        print(json.dumps({"reference": plan, "candidate_qa": qa}, indent=2))
    else:
        print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
