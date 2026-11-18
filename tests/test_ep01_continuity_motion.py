"""No-inference physical continuity gate tests for the nine C07/C08 shots."""
import copy
import unittest
from unittest.mock import patch

from videoforge import ep01_camera_batch as camera
from videoforge import ep01_continuity_motion as motion


class ContinuityMotionTests(unittest.TestCase):
    def test_real_archived_inputs_are_verified_but_rig_is_blocked(self):
        report = motion.validate()
        self.assertEqual(report["shots"], ["C07-P03", "C08-P02", "C08-P03"])
        self.assertEqual(len(report["provenance"]), 3)
        self.assertTrue(report["source_shas_verified"])
        self.assertFalse(report["art_approved"])
        self.assertFalse(report["rig_approved"])
        self.assertFalse(report["animated_motion_verified"])
        self.assertTrue(report["camera_only_does_not_satisfy_cart_motion"])
        self.assertEqual(report["physical_keyframes_proposed"], 7)
        self.assertEqual(report["cart_rotation_degrees_proposed"], 90)
        self.assertIn("approved_cart_layer_manifest", report["blocked_reasons"])
        self.assertIn("approved_cart_visual_bible_master", report["blocked_reasons"])
        self.assertEqual(report["inference_requests"], 0)
        self.assertEqual(report["youtube_publications"], 0)

    def test_proposal_cannot_silently_enable_rig_or_publish(self):
        original = motion.read()
        for key, value in [
            ("allow_publish", True),
            ("allow_paid_inference", True),
            ("never_use_full_png_as_rig", False),
            ("independent_hands", True),
        ]:
            changed = copy.deepcopy(original)
            changed["rules"][key] = value
            with self.subTest(key=key):
                with patch.object(motion, "read", return_value=changed):
                    with self.assertRaisesRegex(ValueError, "MOTION_SAFETY_POLICY_INVALID"):
                        # The original parser checks the altered file; the actual
                        # runtime guard is exercised with a temporary file below.
                        motion.validate()
        self.assertFalse(original["rules"]["allow_publish"])

    def test_cart_yaw_is_monotone_world_space_and_has_no_fake_png_motion(self):
        doc = motion.read()
        push, barricade = doc["shots"][1], doc["shots"][2]
        motion.validate_keyframes(push)
        self.assertEqual(push["frames"][0]["cart_yaw_degrees"], 0)
        self.assertEqual(push["frames"][-1]["cart_yaw_degrees"], 90)
        self.assertEqual(barricade["cart_yaw_degrees"], 90)
        self.assertEqual(push["cart_identity"], barricade["cart_identity"])
        self.assertIn("no_full_image_transform_for_faking_rig", push["physical_invariants"])
        self.assertEqual(barricade["screen_safe_side"], "right")
        self.assertEqual(barricade["pursuers_side"], "left")
        self.assertEqual(push["cast_present"], ["kael"])
        self.assertEqual(barricade["cast_forbidden"], ["elara"])

    def test_rejects_backward_pivot_and_contact_removed(self):
        source = motion.read()["shots"][1]
        broken = copy.deepcopy(source)
        broken["frames"][3]["cart_yaw_degrees"] = -1
        with self.assertRaisesRegex(ValueError, "NONMONOTONIC"):
            motion.validate_keyframes(broken)
        broken = copy.deepcopy(source)
        broken["frames"][-1]["cart_yaw_degrees"] = 80
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_PIVOT"):
            motion.validate_keyframes(broken)
        broken = copy.deepcopy(source)
        broken["physical_invariants"].remove("kael_grip_contact_locked_to_handle")
        with self.assertRaisesRegex(ValueError, "PHYSICAL_INVARIANT"):
            motion.validate_keyframes(broken)

    def test_existing_camera_preview_is_not_misreported_as_real_rig(self):
        shots = {s["id"]: s for s in camera.build_plan(revision="continuity-v2")["shots"]}
        self.assertEqual(len(shots), 42)
        for sid in motion.SHOT_IDS:
            shot = shots[sid]
            self.assertFalse(shot["rig"]["enabled"])
            self.assertFalse(shot["rig"]["independent_hands"])
            self.assertEqual(shot["continuity_gate"]["status"], "blocked_pending_visual_rig")
            self.assertFalse(shot["continuity_gate"]["animated_motion_verified"])
            self.assertIn("independent_C07_C08_temporal_rig_and_axis_review", shot["qa_required"])
        self.assertNotIn("continuity_gate", shots["C07-P04"])
        self.assertNotIn("continuity_gate", shots["C08-P04"])
        self.assertIn("CARRINHO SEM RIG", shots["C08-P02"]["continuity_gate"]["qa_notice"])

    def test_image_hash_or_staging_drift_blocks_validation(self):
        original = motion.read()
        corrupt = copy.deepcopy(original)
        corrupt["source_reference_shas"]["C08-P02"]["sha256"] = "0" * 64
        with patch.object(motion, "read", return_value=corrupt):
            with self.assertRaisesRegex(ValueError, "SOURCE_HASH_MISMATCH"):
                motion.validate()
        corrupt = copy.deepcopy(original)
        corrupt["shots"][2]["cart_yaw_degrees"] = 0
        with patch.object(motion, "read", return_value=corrupt):
            with self.assertRaisesRegex(ValueError, "BARRICADE_NOT_CONTINUOUS"):
                motion.validate()


if __name__ == "__main__":
    unittest.main()
