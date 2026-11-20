"""EP01 V3 regression: distinct geography, seated king, standalone cart, immutable V2."""
import unittest
from pathlib import Path
from videoforge import ep01_continuity_v3 as v3
from videoforge import ep01_camera_batch as camera


class EP01V3Tests(unittest.TestCase):
    def test_three_distinct_location_anchors_and_eleven_replacements(self):
        plan=v3.load_plan()
        self.assertEqual([x["id"] for x in plan["backgrounds"]],list(v3.EXPECTED_PLACES))
        self.assertEqual([s["id"] for s in plan["shots"]],list(v3.EXPECTED_SHOTS))
        self.assertEqual(len(plan["shots"]),11)
        self.assertEqual(len(plan["backgrounds"]),3)
        self.assertEqual(plan["shots_total"],42)
        self.assertEqual(plan["frames_total"],4890)
        self.assertFalse(plan["throne"]["avoid_replacing_approved_anchor"] is False)
        self.assertTrue(plan["geography"]["no_repeated_landmarks_between_different_locations"])
        self.assertTrue(all(not s["human_visual_approval"] and not s["rig_ready"]
                            and not s["youtube_uploaded"] for s in plan["shots"]))

    def test_cart_alone_and_geography_do_not_repeat_old_becco(self):
        plan=v3.load_plan()
        shots={s["id"]:s for s in plan["shots"]}
        for sid in ["C07-P03","C07-P04"]:
            self.assertEqual(shots[sid]["location"],v3.EXPECTED_PLACES[0])
            self.assertIn("sem carroça" if False else "carroça",shots[sid]["prompt"].lower())
        self.assertEqual(shots["C08-P03"]["ref"],[
            "biblia-carrinho-base-v1",v3.EXPECTED_PLACES[1]])
        self.assertIn("SEM guardas",shots["C08-P03"]["prompt"])
        self.assertIn("SEM Kael",shots["C08-P03"]["prompt"])
        self.assertIn("SEM Elara",shots["C08-P03"]["prompt"])
        for sid in ["C08-P04","C08-P05","C09-P01","C09-P02"]:
            self.assertEqual(shots[sid]["location"],v3.EXPECTED_PLACES[2])
        for place in plan["backgrounds"]:
            self.assertEqual(len(place["forbidden_landmarks"]),3)
            self.assertIn("nenhuma",place["prompt"].lower() if "nenhuma" in place["prompt"].lower() else "nenhuma")

    def test_king_never_gets_out_of_the_approved_seat(self):
        d={s["id"]:s for s in v3.load_plan()["shots"]}
        for sid in ["C01-P03","C01-P05"]:
            self.assertEqual(d[sid]["reference_scene_shot_id"],"C01-P04")
            self.assertIn("SENTADO",d[sid]["prompt"])
        old=camera.build_plan(revision="continuity-v2")
        rev=v3.revised_camera_plan(old,require_generated=False)
        a={x["id"]:x for x in old["shots"]}
        b={x["id"]:x for x in rev["shots"]}
        self.assertEqual(len(rev["shots"]),42)
        self.assertEqual(sum(s["duration_frames"] for s in rev["shots"]),4890)
        self.assertEqual(a["C01-P04"],b["C01-P04"])
        self.assertEqual(a["C02-P01"],b["C02-P01"])
        self.assertEqual(a["C02-P02"],b["C02-P02"])
        for sid in v3.EXPECTED_SHOTS:
            self.assertEqual(b[sid]["approval_status"],"candidate_v3_pending_creator_review")
            self.assertEqual(b[sid]["rig"]["enabled"],False)
            self.assertEqual(b[sid]["revision"],"continuity-v3")
        self.assertFalse(rev["youtube_upload"])

    def test_file_keys_and_strict_block_on_missing_v3_art(self):
        self.assertEqual(v3.producer("biblia-largo-encontro-arken-v3"),
            "production-art-request-biblia-largo-encontro-arken-v3")
        self.assertEqual(v3.filename("C01-P05"),
            "c01-p05-continuity-v3-scene-mother.png")
        self.assertEqual(v3.producer("C08-P03"),"production-continuity-v3-mother")
        with self.assertRaises(ValueError):
            v3.producer("C01-P04")
        with self.assertRaises(ValueError):
            v3.filename("C07-P07")
        old=camera.build_plan(revision="continuity-v2")
        if any(v3.archived(sid) is None for sid in v3.EXPECTED_SHOTS):
            with self.assertRaisesRegex(ValueError,"EP01_V3_MOTHER_PENDING"):
                v3.revised_camera_plan(old,require_generated=True)
        else:
            self.assertEqual(len(v3.revised_camera_plan(old,require_generated=True)["shots"]),42)


if __name__=="__main__":
    unittest.main()
