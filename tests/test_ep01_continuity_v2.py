import unittest
from videoforge.ep01_continuity_v2 import read_plan, revised_camera_plan
from videoforge.ep01_camera_batch import build_plan


class ContinuityTests(unittest.TestCase):
    def test_seven_generation_candidates_and_two_reuses(self):
        doc = read_plan()
        rows = doc["shots"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(sum(x["source_policy"] == "generate" for x in rows), 7)
        self.assertEqual([x["id"] for x in rows if x["source_policy"].startswith("reuse:")],
                         ["C07-P01", "C07-P04"])
        self.assertFalse(doc["rules"]["auto_youtube_upload"])
        self.assertFalse(doc["rules"]["independent_hands"])

    def test_screen_direction_and_blockage(self):
        plan = read_plan()
        rows = {s["id"]: s for s in plan["shots"]}
        self.assertIn("DIREITA", rows["C07-P01"]["visual_prompt"].upper())
        self.assertIn("NÃO incluir Elara", rows["C07-P02"]["visual_prompt"])
        self.assertIn("Kael SOZINHO", rows["C08-P02"]["visual_prompt"])
        self.assertIn("Em hipótese alguma", rows["C08-P03"]["visual_prompt"])
        self.assertIn("Kael a alcança", rows["C08-P05"]["visual_prompt"])
        self.assertTrue(all(not x["scene_mother_approved"] for x in rows.values()))
        self.assertTrue(all(not x["rig_approved"] for x in rows.values()))

    def test_revised_42_shot_timeline_and_honest_missing_assets(self):
        old = build_plan()
        plan = revised_camera_plan(old, require_generated=False)
        shots = plan["shots"]
        self.assertEqual(len(shots), 42)
        self.assertEqual(sum(s["duration_frames"] for s in shots), 4890)
        self.assertEqual([s["id"] for s in shots if s["id"].startswith("C07-")],
                         ["C07-P01", "C07-P02", "C07-P03", "C07-P04"])
        self.assertEqual([s["id"] for s in shots if s["id"].startswith("C08-")],
                         ["C08-P01", "C08-P02", "C08-P03", "C08-P04", "C08-P05"])
        self.assertEqual(shots[-1]["start_frame"] + shots[-1]["duration_frames"], 4890)
        self.assertIsNone(next(s for s in shots if s["id"] == "C07-P02")["source"])
        self.assertFalse(any(s["rig"]["enabled"] for s in shots if s["id"].startswith(("C07-", "C08-"))))
        with self.assertRaisesRegex(ValueError, "CONTINUITY_V2_MOTHER_PENDING"):
            revised_camera_plan(old, require_generated=True)


if __name__ == "__main__":
    unittest.main()
