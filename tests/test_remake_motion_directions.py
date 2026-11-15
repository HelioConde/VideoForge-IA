"""40 distinct 4-beat cinematic motion instructions, all source-bound and unapproved."""
import copy
import unittest
from videoforge.remake_motion_directions import (
    load_motion_directions,validate_motion_directions,
)
from videoforge.errors import VideoForgeError
from videoforge.remake_starter import work_queue


class RemakeMotionDirectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=load_motion_directions()

    def test_40_shots_with_160_keyed_actions_and_no_real_image_claim(self):
        result=validate_motion_directions(self.doc)
        self.assertEqual(result["shots"],40)
        self.assertEqual(result["stages"],160)
        self.assertFalse(result["rig_geometry_calibrated"])
        self.assertFalse(result["full_video_render_approved"])
        self.assertFalse(self.doc["paid_provider_calls_authorized"])
        self.assertFalse(self.doc["official_video_approved"])
        for s in self.doc["shots"]:
            self.assertFalse(s["source_contract"]["human_visual_approved"])
            self.assertFalse(s["approved_for_final_render"])
            self.assertEqual([x["stage"] for x in s["stages"]],
                             ["establish","anticipate","articulate","resolve"])

    def test_special_sword_and_reveal_frames_unchanged(self):
        by={s["shot_id"]:s for s in self.doc["shots"]}
        self.assertEqual([x["local_frame"] for x in by["C01-P02"]["stages"]],
                         [0,7,72,89])
        self.assertEqual(by["C01-P02"]["independent_rgba_parts"],
                         ["underlay","sheath","blade","hand"])
        self.assertEqual([x["local_frame"] for x in by["C12-P01"]["stages"]],
                         [0,4,86,119])
        self.assertNotIn("elara",by["C01-P05"]["cast"])
        self.assertEqual(by["C12-P04"]["focus"],"broche.prateado")
        self.assertTrue("roda" in by["C08-P04"]["stages"][1]["direction"].lower())

    def test_task_queue_includes_explicit_motion_beat_instructions(self):
        tasks=work_queue()["production_queue"]
        self.assertEqual(len(tasks),40)
        for t in tasks:
            self.assertEqual(t["motion_cues_source"],"remake-v2-motion-directions.json")
            self.assertEqual(len(t["motion_phases"]),4)
            self.assertEqual(t["motion_phases"][0]["local_frame"],0)
            self.assertFalse(t["dispatch_permitted"])
            self.assertFalse(t["render_approved"])

    def test_moved_cut_or_fake_approval_blocks_the_plan(self):
        fake=copy.deepcopy(self.doc)
        fake["shots"][1]["frames"]["global_start"]=61
        with self.assertRaisesRegex(VideoForgeError,"SHOT_MISMATCH"):
            validate_motion_directions(fake)
        fake=copy.deepcopy(self.doc)
        fake["shots"][1]["source_contract"]["human_visual_approved"]=True
        with self.assertRaisesRegex(VideoForgeError,"FAKE_ASSET_APPROVAL"):
            validate_motion_directions(fake)

    def test_missing_action_or_fake_pivot_calibration_blocks(self):
        fake=copy.deepcopy(self.doc)
        fake["shots"][1]["stages"].pop()
        with self.assertRaisesRegex(VideoForgeError,"FOUR_PHASES"):
            validate_motion_directions(fake)
        fake=copy.deepcopy(self.doc)
        fake["shots"][1]["source_contract"]["pivots_measured_from_real_art"]=True
        with self.assertRaisesRegex(VideoForgeError,"FAKE_ASSET_APPROVAL"):
            validate_motion_directions(fake)


if __name__=="__main__":
    unittest.main()
