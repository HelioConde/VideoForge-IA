"""No-network contract tests for a real-Astra-to-media handoff that stays blocked."""
import copy
import unittest

from test_agent_live_evidence_gate import example, SOURCE
from orchestrator.ep01_production_handoff import (
    BLOCKED, EXPECTED_ROLES, REQUIRED_SHOTS, build_handoff, layer_brief
)
from orchestrator.runtime import MANIFEST


def images():
    return {
        "source_manifest": MANIFEST.as_posix(),
        "visual_qa_approved": False,
        "new_ai_requests": 0,
        "source_bytes_modified": 0,
        "unique_source_images": 9,
        "reuse_details": {
            "C07-P04": "archived ORIGINAL C07-P03; distinct from C07-P03 V2"
        },
        "shots": [
            {"shot_id": shot, "sha256": f"{i+1:064x}",
             "asset_path": f"archived/{shot}.png",
             "scene_mother_approved": False,
             "visual_review_status": "pending_human_or_independent_visual_qa"}
            for i, shot in enumerate(REQUIRED_SHOTS)
        ]
    }


def physical():
    return {
        "art_approved": False, "rig_approved": False,
        "animated_motion_verified": False, "source_shas_verified": True,
        "cart_rotation_degrees_proposed": 90, "physical_keyframes_proposed": 7,
        "shots": ["C07-P03", "C08-P02", "C08-P03"],
        "blocked_reasons": [
            "approved_cart_layer_manifest", "C07_P03_screen_axis_resolution"
        ],
    }


def layer_plan():
    return {
        "required_layer_ids": [
            "alley_reconstructed_rgba", "kael_connected_body_rgba",
            "cart_chassis_rgba", "wheel_left_rgba", "wheel_right_rgba",
            "kael_grip_integrated_rgba", "cart_front_occlusion_rgba"
        ],
        "missing_layer_manifest": "assets/rig/c07-c08-cart-v1/layers-manifest.json",
        "cart_bible": {"asset": "archived/biblia-carrinho.png",
                       "sha256": "0" * 64, "master_approved": False},
        "rules": {"allow_image_generation": False},
        "shots": [{
            "id": "C08-P02", "physical_invariants": [
                "kael_grip_contact_locked_to_handle",
                "both_wheels_ground_contact", "cart_chassis_is_one_rigid_object",
                "no_full_image_transform_for_faking_rig",
            ]
        }],
    }


class RealAstraMediaHandoffTests(unittest.TestCase):
    def test_verified_role_journals_create_twelve_blocked_workorders(self):
        result = build_handoff(example(), images(), physical(),
                               expected_source_sha=SOURCE)
        self.assertEqual(result["astra_model"], "gpt-6.2-astra")
        self.assertEqual(result["real_llm_calls_verified"], 13)
        self.assertEqual(result["real_roles_verified"], EXPECTED_ROLES)
        self.assertEqual(result["source_mother_hashes_verified"], 9)
        self.assertEqual([x["agent_id"] for x in result["work_orders"]], EXPECTED_ROLES)
        self.assertEqual(len({x["id"] for x in result["work_orders"]}), 12)
        self.assertTrue(all(not x["production_completed"]
                            and not x["youtube_publication"]
                            for x in result["work_orders"]))
        self.assertEqual(result["work_orders"][4]["status"],
                         "source_sha_verified_not_visual_approved")
        self.assertEqual(result["work_orders"][5]["status"], BLOCKED)
        self.assertFalse(result["production_gate"]["human_visual_approval"])
        self.assertFalse(result["production_gate"]["rig_approved"])
        self.assertFalse(result["production_gate"]["final_mp4_approved"])
        self.assertEqual(result["new_model_calls"], 0)
        self.assertEqual(result["new_image_generations"], 0)

    def test_propose_seven_layers_but_never_claim_rgba_or_rig_creation(self):
        handoff = build_handoff(example(), images(), physical(),
                                expected_source_sha=SOURCE)
        brief = layer_brief(handoff, layer_plan())
        self.assertEqual(len(brief["required_layers"]), 7)
        self.assertFalse(brief["rig_created"])
        self.assertFalse(brief["qa_approved"])
        self.assertTrue(brief["do_not_overwrite_sources"])
        self.assertFalse(brief["independent_hands"])
        self.assertEqual(brief["requested_yaw_degrees"], 90)
        self.assertEqual(brief["mother_source"]["shot_id"], "C08-P02")
        self.assertEqual(brief["continuity_source"]["shot_id"], "C08-P03")
        self.assertTrue(all(x["status"] == "not_generated_or_verified"
                            for x in brief["required_layers"]))

    def test_real_QA_rejection_and_source_drift_block_handoff(self):
        with self.assertRaises(ValueError):
            build_handoff(example(False), images(), physical(),
                          expected_source_sha=SOURCE)
        with self.assertRaises(ValueError):
            build_handoff(example(), images(), physical(),
                          expected_source_sha="d" * 64)

    def test_forged_approvals_and_missing_images_cannot_unlock_media(self):
        for kind in ("image_approval", "missing_mother", "unexpected_regeneration",
                     "rig_approved", "missing_layer_blocker", "wrong_direction"):
            inventory, motion = images(), physical()
            if kind == "image_approval":
                inventory["shots"][5]["scene_mother_approved"] = True
            elif kind == "missing_mother":
                inventory["shots"].pop()
            elif kind == "unexpected_regeneration":
                inventory["new_ai_requests"] = 1
            elif kind == "rig_approved":
                motion["rig_approved"] = True
            elif kind == "missing_layer_blocker":
                motion["blocked_reasons"].remove("approved_cart_layer_manifest")
            elif kind == "wrong_direction":
                motion["cart_rotation_degrees_proposed"] = 0
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                build_handoff(example(), inventory, motion,
                              expected_source_sha=SOURCE)

    def test_image_generation_policy_drift_rejects_layer_brief(self):
        handoff = build_handoff(example(), images(), physical(),
                                expected_source_sha=SOURCE)
        proposal = layer_plan()
        proposal["rules"]["allow_image_generation"] = True
        with self.assertRaises(ValueError):
            layer_brief(handoff, proposal)


if __name__ == "__main__":
    unittest.main()
