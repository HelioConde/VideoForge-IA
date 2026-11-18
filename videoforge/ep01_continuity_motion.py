"""C07/C08 physical continuity readiness: hard gates, no image/model/render calls.

Plans a real articulated cart/Kael interaction. It MUST NOT promote a
painted, integrated scene image into an approved rig or claim a fixed shot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
PROPOSAL = EP / "PROPOSTA-MOVIMENTO-C07-C08-V1.json"
SHOT_IDS = ("C07-P03", "C08-P02", "C08-P03")
REQUIRED_LAYERS = (
    "alley_reconstructed_rgba",
    "kael_connected_body_rgba",
    "cart_chassis_rgba",
    "wheel_left_rgba",
    "wheel_right_rgba",
    "kael_grip_integrated_rgba",
    "cart_front_occlusion_rgba",
)
PREVIEW_NOTICES = {
    "C07-P03": "EIXO ELARA→KAEL PENDENTE — CAMERA NAO CORRIGE POSE",
    "C08-P02": "CARRINHO SEM RIG — GIRO AINDA NAO ANIMADO",
    "C08-P03": "BARRICADA ESTATICA — TRANSICAO AINDA SEM GIRO",
}


def read(root=ROOT) -> dict:
    document = json.loads((Path(root) / PROPOSAL).read_text(encoding="utf-8"))
    if (document.get("schema") != "videoforge/ep01-c07c08-motion-readiness/v1"
            or document.get("video_id") != EP.name
            or document.get("status") != "proposal_only_not_rig_approved"
            or not isinstance(document.get("rules"), dict)):
        raise ValueError("C07C08_MOTION_SCHEMA_INVALID")
    rules = document["rules"]
    required_true = ("never_use_full_png_as_rig", "never_modify_original_png",
                     "require_art_approval_before_rig",
                     "require_human_visual_approval_before_release")
    required_false = ("independent_hands", "allow_paid_inference",
                      "allow_publish", "allow_image_generation")
    if (any(rules.get(name) is not True for name in required_true)
            or any(rules.get(name) is not False for name in required_false)
            or tuple(document.get("required_layer_ids", [])) != REQUIRED_LAYERS):
        raise ValueError("C07C08_MOTION_SAFETY_POLICY_INVALID")
    shots = document.get("shots", [])
    if not isinstance(shots, list) or tuple(x.get("id") for x in shots if isinstance(x, dict)) != SHOT_IDS:
        raise ValueError("C07C08_MOTION_SHOTS_INVALID")
    qa = document.get("QA")
    if (not isinstance(qa, dict) or any(qa.get(key) is not False for key in
            ("visual_review_passed", "layer_split_verified", "rig_ready",
             "art_approval", "animation_qa_passed"))):
        raise ValueError("C07C08_MOTION_FALSE_APPROVAL")
    return document


def validate_keyframes(shot: dict) -> None:
    """A 90° world-space pivot with contact has a proposed monotone timeline."""
    keys = shot.get("frames")
    if not isinstance(keys, list) or len(keys) < 4:
        raise ValueError("C08_P02_KEYFRAMES_MISSING")
    last_frame = -1
    last_angle = -1.0
    last_progress = -1.0
    required_last_frame = shot["end_exclusive"] - shot["start_frame"] - 1
    for key in keys:
        if not isinstance(key, dict):
            raise ValueError("C08_P02_BAD_KEYFRAME")
        frame = key.get("frame")
        angle = key.get("cart_yaw_degrees")
        progress = key.get("push_progress")
        if (type(frame) is not int or not isinstance(angle, (int, float))
                or type(angle) is bool or not isinstance(progress, (float, int))
                or type(progress) is bool or not 0 <= angle <= 90
                or not 0 <= progress <= 1 or frame <= last_frame
                or angle < last_angle or progress < last_progress):
            raise ValueError("C08_P02_NONMONOTONIC_KEYFRAMES")
        last_frame, last_angle, last_progress = frame, angle, progress
    if (keys[0]["frame"] != 0 or keys[0]["cart_yaw_degrees"] != 0
            or keys[0]["push_progress"] != 0 or last_frame != required_last_frame
            or last_angle != 90 or last_progress != 1):
        raise ValueError("C08_P02_INCOMPLETE_PIVOT")
    if (shot.get("coord_space") != "proposed_world_space_not_screen_plane_pixels"
            or shot.get("target_yaw_degrees") != 90
            or shot.get("cart_identity") != "biblia-carrinho-base-v1"
            or shot.get("cast_present") != ["kael"]
            or shot.get("cast_forbidden") != ["elara", "pursuer_1", "pursuer_2"]):
        raise ValueError("C08_P02_PHYSICAL_CONSTRAINT_INVALID")
    required = {
        "kael_grip_contact_locked_to_handle",
        "both_wheels_ground_contact",
        "cart_chassis_is_one_rigid_object",
        "no_wheel_sliding_without_rotation",
        "no_soldiers_touch_cart",
        "no_character_or_cart_teleport",
        "no_full_image_transform_for_faking_rig",
    }
    if set(shot.get("physical_invariants", [])) != required:
        raise ValueError("C08_P02_PHYSICAL_INVARIANT_INVALID")


def validate(root=ROOT, *, verify_bytes: bool = True) -> dict:
    root = Path(root)
    proposal = read(root)
    from .ep01_continuity_v2 import read_plan
    continuity = read_plan(root)
    selected = {shot["id"]: shot for shot in continuity["shots"]}
    refs = proposal["source_reference_shas"]
    if set(refs) != set(SHOT_IDS):
        raise ValueError("C07C08_MOTION_PINNED_SOURCES_INVALID")
    report_sources = []
    for shot in proposal["shots"]:
        sid = shot["id"]
        baseline = selected[sid]
        if (shot["start_frame"] != baseline["start_frame"]
                or shot["end_exclusive"] != baseline["end_exclusive"]
                or baseline["rig_approved"] is not False
                or baseline["scene_mother_approved"] is not False):
            raise ValueError("C07C08_MOTION_BASELINE_DRIFT")
        ref = refs[sid]
        image = (root / EP / ref["asset"]).resolve()
        if (not image.is_relative_to((root / EP).resolve())
                or not image.is_file() or image.is_symlink()):
            raise ValueError("C07C08_MOTION_SOURCE_MISSING")
        sha = hashlib.sha256(image.read_bytes()).hexdigest() if verify_bytes else ref["sha256"]
        if sha != ref["sha256"]:
            raise ValueError("C07C08_MOTION_SOURCE_HASH_MISMATCH")
        # The archive's formal image manifest must pin exactly these bytes.
        metadata = image.with_suffix(".production.json")
        record = json.loads(metadata.read_text(encoding="utf-8"))
        if (record.get("sha256") != ref["sha256"]
                or record.get("shot_id") != sid
                or record.get("human_visual_approval") is not False
                or record.get("rig_ready") is not False):
            raise ValueError("C07C08_MOTION_IMAGE_PROVENANCE_INVALID")
        report_sources.append({"shot_id": sid, "sha256": sha, "file": str(ref["asset"])})

    p03, p02, p03_barricade = proposal["shots"]
    if (p03.get("mode") != "spatial_axis_and_blocking_review"
            or p03.get("desired_screen_direction") != "left_to_right"
            or p03.get("requires_updated_art_or_approved_alternative_for_true_motion") is not True):
        raise ValueError("C07_P03_AXIS_REVIEW_MISSING")
    validate_keyframes(p02)
    if (p03_barricade.get("cart_identity") != p02.get("cart_identity")
            or p03_barricade.get("cart_yaw_degrees") != 90
            or p03_barricade.get("cart_start_state") != p02.get("final_cart_state")
            or p03_barricade.get("screen_safe_side") != "right"
            or p03_barricade.get("pursuers_side") != "left"
            or p03_barricade.get("cast_present") != ["kael", "pursuer_1", "pursuer_2"]
            or p03_barricade.get("cast_forbidden") != ["elara"]
            or p03_barricade.get("frame_hold") != {
                "start_frame": 0,
                "end_inclusive": p03_barricade["end_exclusive"]-p03_barricade["start_frame"]-1,
                "yaw_degrees": 90,
            }):
        raise ValueError("C08_P03_BARRICADE_NOT_CONTINUOUS")

    cart = proposal["cart_bible"]
    master = json.loads((root / "canal/alchemy-lab/biblia-visual/objetos/carrinho/status.json").read_text(encoding="utf-8"))
    master_meta = json.loads((root / EP / cart["asset"]).with_suffix(".production.json").read_text(encoding="utf-8"))
    if (cart["master_approved"] is not False
            or master.get("aprovacao_mestra") is not False
            or master_meta.get("sha256") != cart["sha256"]
            or master_meta.get("human_visual_approval") is not False):
        raise ValueError("C08_CART_MASTER_APPROVAL_UNVERIFIED")
    layer_manifest = (root / EP / proposal["missing_layer_manifest"]).resolve()
    if (not layer_manifest.is_relative_to((root / EP).resolve())
            or layer_manifest.is_symlink()):
        raise ValueError("C08_CART_LAYER_MANIFEST_PATH_INVALID")
    missing = []
    if not layer_manifest.exists():
        missing.append("approved_cart_layer_manifest")
    else:
        # A file alone must never bypass art/QA approvals. Do not parse an
        # arbitrary unapproved rig manifest as evidence of readiness.
        missing.append("layer_art_approval_and_independent_recomposition_qa")
    missing.extend(["approved_cart_visual_bible_master",
                    "articulated_hand_cart_contact_QA",
                    "C07_P03_screen_axis_resolution",
                    "C08_P02_to_P03_temporal_rig_validation"])
    return {
        "schema_version": 1,
        "mode": "c07c08_physical_animation_plan_readiness",
        "source_shas_verified": verify_bytes,
        "provenance": report_sources,
        "cart_bible_sha256": cart["sha256"],
        "blocked_reasons": missing,
        "shots": list(SHOT_IDS),
        "staging": "candidate_only_not_rig",
        "physical_keyframes_proposed": len(p02["frames"]),
        "cart_rotation_degrees_proposed": 90,
        "art_approved": False,
        "rig_approved": False,
        "animated_motion_verified": False,
        "camera_only_does_not_satisfy_cart_motion": True,
        "independent_hands": False,
        "next_agent": "06 prepare approved layers; 07 rig; 08 animate; 12 independent temporal QA",
        "inference_requests": 0,
        "images_generated": 0,
        "youtube_publications": 0,
    }


def preview_gate(shot_id: str, root=ROOT) -> dict | None:
    """Pure annotation for camera-only preview; not the full readiness check."""
    if shot_id not in PREVIEW_NOTICES:
        return None
    read(root)  # Reject changed approval/safety policies before showing labels.
    return {"status": "blocked_pending_visual_rig", "qa_notice": PREVIEW_NOTICES[shot_id],
            "not_an_art_approval": True, "animated_motion_verified": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    report = validate()
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"shots": report["shots"], "blocked_reasons": report["blocked_reasons"],
                      "inference_requests": 0, "rig_approved": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
