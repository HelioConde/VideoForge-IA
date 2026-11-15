"""Production queue uses only current V2 data and reusable installed rig engine."""
import copy
import unittest

from videoforge.remake_starter import REUSE,work_queue


class RemakeStarterTests(unittest.TestCase):
    def test_exact_timeline_and_no_fake_asset_approval(self):
        out=work_queue()
        self.assertEqual(out["shot_count"],40)
        self.assertEqual(out["visual_shot_count"],39)
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
        self.assertIn(first["status"],("audio_and_sfx_pending","opening_technical_preview_in_actions_pending_review"))
        self.assertIn(first["candidate_workflow"],(None,"remake-opening-preview.yml"))
        self.assertEqual(second["shot_id"],"C01-P02")
        self.assertEqual(second["profile"],"sword-draw-three")
        self.assertEqual(second["duration_frames"],90)
        self.assertIn("hand",second["required_parts"])
        self.assertEqual(second["required_parts"],["underlay","sheath","blade","hand"])
        self.assertIn("carrasco",second["direction"]["dramatic_direction"].lower())

    def test_sha_fingerprints_are_stable_and_restarts_do_not_duplicate(self):
        a=work_queue()
        b=work_queue()
        self.assertEqual(a,b)
        ids={i["task_fingerprint"] for i in a["production_queue"]}
        self.assertEqual(len(ids),40)

    def test_40_shots_add_drama_without_moving_opening_or_epilogue(self):
        data=work_queue()
        ids=[x["shot_id"] for x in data["production_queue"]]
        self.assertEqual(len(ids),40)
        self.assertEqual(len(set(ids)),40)
        self.assertEqual(
            [x for x in ids if x in {"C01-P05","C08-P04","C12-P04"}],
            ["C01-P05","C08-P04","C12-P04"])
        by_id={x["shot_id"]:x for x in data["production_queue"]}
        self.assertEqual((by_id["C01-P02"]["start_frame"],
                          by_id["C01-P02"]["end_frame_exclusive"]),(60,150))
        for sid,span in {"C01-P05":(310,360),"C08-P04":(2880,2940),
                         "C12-P04":(4290,4350)}.items():
            self.assertEqual((by_id[sid]["start_frame"],
                              by_id[sid]["end_frame_exclusive"]),span)
            self.assertFalse(by_id[sid]["render_approved"])
        self.assertEqual(data["format"]["total_frames"],4890)

    def test_every_queue_task_includes_four_motion_phases(self):
        queue=work_queue()["production_queue"]
        self.assertEqual(len(queue),40)
        self.assertEqual(sum(len(t["motion_phases"]) for t in queue),160)
        for task in queue:
            self.assertEqual(task["motion_cues_source"],"remake-v2-motion-directions.json")
            self.assertEqual(task["motion_phases"][0]["local_frame"],0)
            self.assertFalse(task["render_approved"])
            self.assertFalse(task["dispatch_permitted"])

    def test_39_visual_tasks_require_source_mask_geometry(self):
        queue=work_queue()["production_queue"]
        self.assertEqual(len(queue),40)
        self.assertEqual(sum(t["geometry_qa_required"] for t in queue),39)
        by_id={t["shot_id"]:t for t in queue}
        self.assertEqual(by_id["C01-P02"]["geometry_qa_candidate"],
                         "mask-geometry.qa.json")
        self.assertFalse(by_id["C01-P02"]["geometry_pixels_measured"])
        self.assertFalse(by_id["C01-P02"]["geometry_human_anatomy_approved"])
        self.assertFalse(by_id["C01-P01"]["geometry_qa_required"])

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
