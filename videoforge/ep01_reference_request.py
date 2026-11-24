"""Prepare a versioned EP01 image-edit request and inspect its response offline.

No provider transport, reservations, files or approvals are created here.
The returned payload remains an unsigned draft until an authorized transport
binds its exact fingerprint to a durable no-replay reservation.
"""
from __future__ import annotations

import argparse
import base64
from copy import deepcopy
import hashlib
import json
import re

from . import ep01_proxy_separate_parts as parts
from .ep01_reference_placement import prepare_reference, inspect_candidate
from .errors import VideoForgeError

SCHEMA = "videoforge/ep01-reference-request/v1"
REVISION = "reference-canvas-v1"


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()


def reference_prompt(spec, placement):
    """Replace only the generic native-canvas preamble, fail on prompt drift."""
    marker = "Use the ATTACHED first image"
    prompt = spec["prompt"]
    if not prompt.startswith("CANVAS CONTRACT:") or prompt.count(marker) != 1:
        raise VideoForgeError("EP01_REFERENCE_REQUEST_PROMPT_CONTRACT_CHANGED")
    body = prompt[prompt.index(marker):]
    if spec["role"] == "background":
        opaque = "same shot, OPAQUE RGB/RGBA."
        holes = "No person/object silhouettes or transparent holes."
        if body.count(opaque) != 1 or body.count(holes) != 1:
            raise VideoForgeError("EP01_REFERENCE_REQUEST_BACKGROUND_CONTRACT_CHANGED")
        body = body.replace(opaque, "same shot, fully opaque ONLY inside the source rectangle.")
        body = body.replace(holes, "No silhouettes or transparent holes INSIDE the source rectangle.")
    width, height = placement["reference_canvas"]
    left, top, right, bottom = placement["source_rect_xyxy"]
    source_w, source_h = placement["source_canvas"]
    prompt = (
        f"CANVAS CONTRACT {REVISION}: image one is a {width}x{height} RGBA "
        f"reference canvas. Output WIDTH={width}, HEIGHT={height}, in that order. "
        f"The original {source_w}x{source_h} scene occupies x=[{left},{right}), "
        f"y=[{top},{bottom}); upper limits are exclusive. "
        f"Source coordinates map to reference coordinates by x+{left}, y+{top}, "
        "with scale exactly 1:1. Preserve placement relative to IMAGE ONE. "
        "ALL pixels outside that source rectangle MUST have alpha=0, including "
        "background requests. Draw no content into these added margins. "
        "Do not rotate, stretch, crop, enlarge or recenter. Generate a NEW "
        "independent component; never return the reference image itself. "
    ) + body
    if len(prompt) > 5000:
        raise VideoForgeError("EP01_REFERENCE_REQUEST_PROMPT_TOO_LONG")
    return prompt


def prepare_request(shot_id, part_id, expected_source_sha256, root=parts.ROOT):
    # Reuse the current source revision fence; do not reopen V2/V3 or approved art.
    from scripts.ep01_action_production_queue import SHOTS_BLOCKED_FROM_LEGACY_PARTS
    if shot_id in SHOTS_BLOCKED_FROM_LEGACY_PARTS:
        raise VideoForgeError("EP01_REFERENCE_REQUEST_SOURCE_REVISION_BLOCKED")
    if not isinstance(expected_source_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_source_sha256):
        raise VideoForgeError("EP01_REFERENCE_REQUEST_SOURCE_SHA_REQUIRED")
    _, request = parts.read_shot(shot_id, part_id, root)
    # Special revisions have shot-specific pixel coordinates and need their own
    # prompt migration. This adapter handles only the original generic requests.
    if request["id"] != part_id:
        raise VideoForgeError("EP01_REFERENCE_REQUEST_SPECIAL_PROMPT_NOT_MIGRATED")
    versioned_part = part_id + "-" + REVISION
    if parts.existing_part(shot_id, versioned_part, root):
        raise VideoForgeError("EP01_REFERENCE_REQUEST_ALREADY_ARCHIVED_NO_REPEAT")
    # Also retains the base component's existing no-repeat and source QA rules.
    spec = parts.prepare(shot_id, part_id, root)
    if spec["mother_proof"]["sha256"] != expected_source_sha256:
        raise VideoForgeError("EP01_REFERENCE_REQUEST_SOURCE_CHANGED")
    reference, placement = prepare_reference(spec["mother"], expected_source_sha256)
    if list(spec["source_dimensions"]) != placement["source_canvas"]:
        raise VideoForgeError("EP01_REFERENCE_REQUEST_SOURCE_DIMENSIONS_CHANGED")
    if (len(spec["refs"]) != len(spec["ref_proofs"])
            or len(spec["refs"]) + 1 > parts.MAX_REFERENCE_PNGS_PER_REQUEST
            or any(hashlib.sha256(raw).hexdigest() != proof["sha256"]
                   for raw, proof in zip(spec["refs"], spec["ref_proofs"]))):
        raise VideoForgeError("EP01_REFERENCE_REQUEST_IDENTITY_REFERENCES_CHANGED")
    payload = {
        "model": "gpt-image-2", "n": 1,
        "prompt": reference_prompt(spec, placement),
        "size": placement["requested_size_candidate"],
        "background": "transparent", "output_format": "png",
        "response_format": "b64_json", "stream": False,
        "images": [{"image_url": "data:image/png;base64," +
                    base64.b64encode(raw).decode("ascii")}
                   for raw in [reference, *spec["refs"]]],
    }
    bundle = {
        "schema": SCHEMA, "revision": REVISION,
        "request_id": shot_id.lower() + "-" + versioned_part,
        "shot_id": shot_id, "base_component": part_id,
        "versioned_component": versioned_part, "role": spec["role"],
        "source_sha256": expected_source_sha256,
        "source_proof": deepcopy(spec["mother_proof"]),
        "reference_manifest": placement,
        "identity_reference_proofs": deepcopy(spec["ref_proofs"]),
        "endpoint": "/v1/images/edits", "payload": payload,
        "provider_calls": 0, "generation_authorized": False,
        "human_visual_approval": False, "rig_ready": False,
        "youtube_uploaded": False,
    }
    bundle["request_sha256"] = fingerprint(bundle)
    return bundle


def inspect_response(bundle, raw, expected_request_sha256, root=parts.ROOT):
    """Bind QA to an independently pinned request, then recheck original bytes."""
    unsigned = dict(bundle)
    claimed = unsigned.pop("request_sha256", None)
    if (claimed != expected_request_sha256 or fingerprint(unsigned) != claimed
            or bundle.get("schema") != SCHEMA or bundle.get("revision") != REVISION
            or bundle.get("generation_authorized") is not False):
        raise VideoForgeError("EP01_REFERENCE_REQUEST_FINGERPRINT_MISMATCH")
    source, proof = parts.mother_source(bundle["shot_id"], root)
    if (proof != bundle["source_proof"]
            or proof["sha256"] != bundle["source_sha256"]):
        raise VideoForgeError("EP01_REFERENCE_REQUEST_SOURCE_CHANGED")
    report = inspect_candidate(raw, source, bundle["source_sha256"],
                               bundle["reference_manifest"], role=bundle["role"])
    report.update(request_id=bundle["request_id"], request_sha256=claimed,
                  versioned_component=bundle["versioned_component"])
    return report


def summary(bundle):
    """Printable review copy, deliberately not an executable/fingerprint-valid payload."""
    result = deepcopy(bundle)
    images = result["payload"].pop("images")
    result["attached_image_count"] = len(images)
    result["summary_only"] = True
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--part", required=True)
    parser.add_argument("--source-sha256", required=True)
    args = parser.parse_args()
    bundle = prepare_request(args.shot_id, args.part, args.source_sha256)
    print(json.dumps(summary(bundle), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
