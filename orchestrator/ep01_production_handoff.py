"""Read-only handoff from REAL 12-role Astra QA to verifiable EP01 production tasks.

Reads the persisted GitHub CAS snapshot and archived assets, revalidates
13 provider journals and 12 independent role responses, then creates concrete
source-pinned work orders and a nine-image contact sheet. NEVER generates or
edits images, enables rig, renders a final MP4 or publishes videos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from .agent_bus import fingerprint
from .agent_live_roundtrip import validate_live_roundtrip_result
from .runtime import EP, MANIFEST, ROOT, report, source
from .runtime_store import Store
from .shot_contact_sheet import render_sheet, validate as validate_archived_images
from videoforge.ep01_continuity_motion import validate as validate_cart_motion, read as read_cart_motion

STATE_PATH = "runtime/agent-12-text-roundtrip-v1.json"
EXPECTED_ROLES = [f"{i:02}" for i in range(1, 13)]
REQUIRED_SHOTS = ["C07-P01", "C07-P02", "C07-P03", "C07-P04", "C08-P01",
                  "C08-P02", "C08-P03", "C08-P04", "C08-P05"]
BLOCKED = "blocked_pending_art_or_physical_qa"
NEVER_PRODUCTION = {
    "human_visual_approval": False, "rig_approved": False,
    "animation_qa_passed": False, "final_mp4_approved": False,
    "youtube_publication": False,
}


def _task(role, operation, shots, prerequisites, status=BLOCKED, notes=""):
    return {
        "id": f"EP01-C07C08-AG{role}-{operation}",
        "agent_id": role, "operation": operation,
        "shots": shots, "requires": prerequisites,
        "status": status, "reviewer": "12" if role != "12" else "creator",
        "notes": notes,
        "production_completed": False,
        "human_visual_approval": False,
        "youtube_publication": False,
    }


def build_handoff(data: dict, images: dict, motion: dict, *, expected_source_sha: str) -> dict:
    """Convert authentic role evidence into blocked/actionable task definitions.

    The role QA only approves source-bound text. Independently verify image SHA,
    no rig readiness, no visual approvals and all dependencies before any work
    could be delegated to actual media production tools.
    """
    if not isinstance(data, dict) or len(data.get("tasks", [])) != 1:
        raise ValueError("Exactly one real Astra EP01 roundtrip is required")
    task = data["tasks"][0]
    model = task.get("model")
    if model not in ("gpt-6.2-astra", "gpt-6-astra"):
        raise ValueError("Astra model identity was not verified")
    result = validate_live_roundtrip_result(data, model)
    if result != "needs_human_review" or task.get("status") != "completed":
        raise ValueError("The real independent text QA must pass before handoff")
    if task.get("input_refs", {}).get(MANIFEST.as_posix()) != expected_source_sha:
        raise ValueError("Source manifest changed since the thirteen real calls")
    reviews = data["checkpoints"][0]["review"]
    if reviews.get("technical_passed") is not True or reviews.get("production_ready") is not False:
        raise ValueError("Independent QA failed or falsely approved production")
    qa = reviews["qa_response"]["response"]["findings"]
    if ([x.get("role_id") for x in qa] != [f"{i:02}" for i in range(2, 12)]
            or any(x.get("decision") != "supported" for x in qa)):
        raise ValueError("All ten source-only specialist reports must be supported")
    if (images.get("visual_qa_approved") is not False
            or images.get("new_ai_requests") != 0
            or images.get("source_bytes_modified") != 0
            or images.get("unique_source_images") != 9
            or [r.get("shot_id") for r in images.get("shots", [])] != REQUIRED_SHOTS
            or images.get("source_manifest") != MANIFEST.as_posix()):
        raise ValueError("Archived image QA inventory is incomplete or unsafe")
    if (motion.get("art_approved") is not False
            or motion.get("rig_approved") is not False
            or motion.get("animated_motion_verified") is not False
            or motion.get("source_shas_verified") is not True
            or motion.get("cart_rotation_degrees_proposed") != 90
            or motion.get("physical_keyframes_proposed") != 7
            or motion.get("shots") != ["C07-P03", "C08-P02", "C08-P03"]
            or "approved_cart_layer_manifest" not in motion.get("blocked_reasons", [])):
        raise ValueError("Physical animation gates were unexpectedly relaxed")
    by_shot = {r["shot_id"]: r for r in images["shots"]}
    for row in by_shot.values():
        if row.get("scene_mother_approved") is not False or row.get("visual_review_status") != "pending_human_or_independent_visual_qa":
            raise ValueError("Scene mothers must remain candidates")
    if images["reuse_details"].get("C07-P04") != "archived ORIGINAL C07-P03; distinct from C07-P03 V2":
        raise ValueError("The separate dialogue shot must retain its original archived mother")

    c03 = "EP01-C07C08-AG03-resolve_screen_axis"
    c04 = "EP01-C07C08-AG04-approve_cart_and_bible"
    c05 = "EP01-C07C08-AG05-verify_original_mothers"
    c06 = "EP01-C07C08-AG06-prepare_real_rgba_layers"
    c07 = "EP01-C07C08-AG07-build_and_validate_cart_rig"
    c08 = "EP01-C07C08-AG08-animate_physical_cart"
    c09 = "EP01-C07C08-AG09-check_camera_axis"
    c10 = "EP01-C07C08-AG10-produce_audio_and_sync"
    c11 = "EP01-C07C08-AG11-assemble_and_verify_mp4"
    work = [
        _task("01", "coordinate_approved_production", REQUIRED_SHOTS,
              ["independent_media_QA", "creator_approval"],
              notes="The proven Astra roundtrip coordinated TEXT ONLY; no media work was performed."),
        _task("02", "review_nine_beats_and_dialogue", REQUIRED_SHOTS,
              ["creator_creative_review"],
              notes="The dialogue C07-P04 follows the encounter C07-P03; no dialogue inside the chase shot."),
        _task("03", "resolve_screen_axis", ["C07-P01", "C07-P02", "C07-P03", "C07-P04"],
              ["visual_axis_inspection"],
              notes="Elara flees left-to-right; two pursuers remain behind, never help with cart."),
        _task("04", "approve_cart_and_bible", ["C08-P02", "C08-P03"],
              ["independent_original_visual_qa", "cart_master_approval"],
              notes="Keep same archived cart identity; do not silently change visual bible."),
        _task("05", "verify_original_mothers", REQUIRED_SHOTS, [],
              status="source_sha_verified_not_visual_approved",
              notes="Nine distinct archived candidates verified byte-for-byte; do not regenerate."),
        _task("06", "prepare_real_rgba_layers", ["C08-P02", "C08-P03"],
              [c04, c05, "approved_transparency_and_recomposition"],
              notes="Seven transparent components; keep Kael grip integrated, with no independent hands."),
        _task("07", "build_and_validate_cart_rig", ["C08-P02", "C08-P03"],
              [c06, c03, "physical_grip_and_ground_contact_QA"],
              notes="Rigid cart chassis, two rolling wheels, locked hand contact, no flattened-PNG transforms."),
        _task("08", "animate_physical_cart", ["C08-P02", "C08-P03"],
              [c07, "intermediate_frame_independent_QA"],
              notes="130-frame proposed 0-90-degree pivot; 110-frame same-cart barricade hold."),
        _task("09", "check_camera_axis", ["C07-P03", "C08-P02", "C08-P03"],
              [c03, c08],
              notes="Camera-only previews are not proof of articulated rig or spatial continuity."),
        _task("10", "produce_audio_and_sync", REQUIRED_SHOTS,
              ["approved_dialogue", "licensed_sound", "sound_sync_QA"],
              notes="No audio is proven by the camera-only technical MP4."),
        _task("11", "assemble_and_verify_mp4", REQUIRED_SHOTS,
              [c08, c09, c10, "independent_full_media_QA"],
              notes="42-shot / 4890-frame plan is not proof that a finished audiovisual MP4 exists."),
        _task("12", "independent_media_QA", REQUIRED_SHOTS,
              [c03, c04, c06, c07, c08, c09, c10, c11],
              notes="Source-text QA passed; all visual, temporal and sound QA remain separate."),
    ]
    expected_ids = set(x["id"] for x in work)
    if len(expected_ids) != len(EXPECTED_ROLES):
        raise ValueError("Duplicate or missing specialist work order")
    director = reviews["coordinator"]["response"]["findings"][0]
    if (director.get("status") != "needs_human_review"
            or not isinstance(director.get("next_steps"), list)
            or not director["next_steps"]):
        raise ValueError("Director did not preserve its real source-only handoff")
    return {
        "schema_version": 1,
        "kind": "ep01_real_astra_to_production_handoff",
        "episode": EP.as_posix(),
        "stage": "real_source_audit_passed_media_still_blocked",
        "astra_model": model,
        "source_manifest": MANIFEST.as_posix(),
        "source_sha256": expected_source_sha,
        "real_llm_calls_verified": 13, "real_roles_verified": EXPECTED_ROLES,
        "independent_source_text_QA": True,
        "source_mother_hashes_verified": 9,
        "archived_mothers": [
            {"shot_id": row["shot_id"], "sha256": row["sha256"],
             "asset_path": row["asset_path"]}
            for row in images["shots"]
        ],
        "director_advisory_next_steps": director["next_steps"],
        "blocked_reasons": sorted(set(motion["blocked_reasons"]
                                      + ["all_nine_shots_visual_QA_pending",
                                         "final_audio_not_verified",
                                         "finished_animation_and_mp4_not_verified"])),
        "work_orders": work,
        "production_gate": NEVER_PRODUCTION.copy(),
        "new_model_calls": 0, "new_image_generations": 0,
        "new_youtube_publications": 0,
    }


def layer_brief(handoff: dict, motion_plan: dict) -> dict:
    """A concrete source-pinned seven-piece brief, NOT fabricated PNG assets."""
    shots = {s["shot_id"]: s for s in handoff["archived_mothers"]}
    if len(motion_plan["required_layer_ids"]) != 7:
        raise ValueError("Approved physical plan changed its seven-layer contract")
    if motion_plan["rules"].get("allow_image_generation") is not False:
        raise ValueError("Image-generation permission changed without review")
    return {
        "schema_version": 1, "kind": "source_pinned_rgba_separation_work_order",
        "producer": "06", "independent_qa": "12",
        "status": "blocked_pending_visual_and_cart_master_approval",
        "mother_shot": "C08-P02", "continuity_shot": "C08-P03",
        "mother_source": shots["C08-P02"], "continuity_source": shots["C08-P03"],
        "cart_reference": motion_plan["cart_bible"],
        "required_layers": [{"id": n, "status": "not_generated_or_verified"}
                            for n in motion_plan["required_layer_ids"]],
        "manifest_target": motion_plan["missing_layer_manifest"],
        "independent_hands": False,
        "do_not_overwrite_sources": True,
        "create_rig_only_after_layer_QA": True,
        "no_full_png_rig": True,
        "requested_yaw_degrees": 90,
        "physical_invariants": next(s for s in motion_plan["shots"]
                                    if s["id"] == "C08-P02")["physical_invariants"],
        "image_calls_made": 0, "rig_created": False, "qa_approved": False,
        "youtube_publication": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    from .github_state import GitHubState
    remote = GitHubState(path=STATE_PATH, initialize=False)
    snapshot = remote.load()
    if snapshot is None:
        parser.error("No durable real Astra role evidence exists")
    with tempfile.TemporaryDirectory(prefix="vf-ep01-handoff-") as tmp:
        store = Store(Path(tmp) / "state.sqlite")
        try:
            store.import_snapshot(snapshot)
            data = report(store)
        finally:
            store.close()
    task = data["tasks"][0]
    _, source_sha = source(ROOT, MANIFEST.as_posix(),
                           task["input_refs"][MANIFEST.as_posix()])
    inventory = validate_archived_images(ROOT)
    motion = validate_cart_motion(ROOT)
    result = build_handoff(data, inventory, motion, expected_source_sha=source_sha)
    brief = layer_brief(result, read_cart_motion(ROOT))
    dest = args.output_dir
    if dest.is_symlink() or dest.resolve().is_relative_to((ROOT / EP).resolve()):
        parser.error("Reports must never overwrite production sources")
    dest.mkdir(parents=True, exist_ok=True)
    render_sheet(ROOT, dest / "contact-sheet", inventory)
    for name, value in {
        "handoff.json": result,
        "agent-06-layer-brief.json": brief,
        "nine-mother-source-inventory.json": inventory,
        "physical-cart-readiness.json": motion,
    }.items():
        (dest / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    print(json.dumps({"real_roles_verified": 12, "real_calls_verified": 13,
                      "work_orders": len(result["work_orders"]),
                      "archived_images_sha_verified": 9,
                      "layer_assets_created": 0,
                      "physical_rig_approved": False,
                      "media_approved": False, "youtube_publications": 0},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
