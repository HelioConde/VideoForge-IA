"""Production queue uses only current V2 data and reusable installed rig engine."""
import copy
import unittest

from videoforge.remake_starter import REUSE,work_queue


class RemakeStarterTests(unittest.TestCase):
    def test_exact_timeline_and_no_fake_asset_approval(self):
        out=work_queue()
        self.assertEqual(out["shot_count"],37)
        self.assertEqual(out["visual_shot_count"],36)
        self.assertEqual(out["format"]["total_frames"],4890)
        self.assertEqual(out["production_queue"][0]["start_frame"],0)
        self.assertEqual(out["production_queue"][-1]["end_frame_exclusive"],4890)
        self.assertFalse(out["created_images"])
        self.assertFalse(out["created_video"])
        self.assertFalse(out["youtube_uploaded"])
        self.assertTrue(all(not item["dispatch_permitted"] and not item["render_approved"]
                            for item in out["production_queue"]))

    def test_opening_has_no_image_and_sword_uses_real_prop_rig(self):
        first,second=work_queue()["production_queue"][:2]
        self.assertEqual(first["shot_id"],"C01-P01")
        self.assertEqual(first["status"],"audio_and_sfx_pending")
        self.assertIsNone(first["candidate_workflow"])
        self.assertEqual(second["shot_id"],"C01-P02")
        self.assertEqual(second["profile"],"prop-pivots-three")
        self.assertEqual(second["duration_frames"],90)
        self.assertIn("hand",second["required_parts"])
        self.assertIn("sheathe",second["required_parts"])
        self.assertIn("carrasco",second["direction"]["dramatic_direction"].lower())

    def test_sha_fingerprints_are_stable_and_restarts_do_not_duplicate(self):
        a=work_queue()
        b=work_queue()
        self.assertEqual(a,b)
        ids={i["task_fingerprint"] for i in a["production_queue"]}
        self.assertEqual(len(ids),37)

    def test_libraries_and_skills_are_explicitly_reused(self):
        out=work_queue()
        self.assertIn("ThreeCanvas",out["reuse"]["animation_engine"])
        self.assertIn("rig-three-scene",out["reuse"]["rig_component"])
        self.assertTrue(all(s.endswith("SKILL.md") for s in out["reuse"]["project_skills"]))

    def test_no_paid_calls_or_auto_dispatch_without_reference(self):
        out=work_queue()
        self.assertFalse(out["autopilot"]["dispatch_allowed"])
        self.assertEqual(out["autopilot"]["stage"],"generate_character_bible")
        self.assertEqual(out["autopilot"]["blocker"],"provider_cost_permission_required")
        for shot in out["production_queue"][1:]:
            self.assertEqual(shot["status"],"blocked_canonical_reference")
            self.assertEqual(shot["candidate_workflow"],"production-art-by-request.yml")


if __name__=="__main__":
    unittest.main()
