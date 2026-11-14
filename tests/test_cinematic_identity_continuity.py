"""Identity/wardrobe anti-drift tests on 37 planned cinematic shots.

Fixtures below are metadata ONLY and do not claim visual/rig approval.
"""
from __future__ import annotations

import copy
import unittest

from videoforge.cinematic_identity_continuity import (
    build_continuity,validate_actor_wardrobe,verify_shot_continuity
)
from videoforge.errors import VideoForgeError

class CharacterContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=build_continuity()
        cls.shots={s["shot_id"]:s for s in cls.report["shots"]}

    @staticmethod
    def fake_approved_metadata(shot):
        actors=[]
        review={}
        for character,rule in shot["main_character_requirements"].items():
            fields={k:rule[k] for k in (
                "style_reference_sha256","wardrobe_version","hair_identity"
            )}
            actors.append({"id":character,"continuity":fields})
            review[character]={
                "approved":True,
                **fields,
                **({"princess_identity_revealed":rule["is_princess_identity_revealed"]}
                   if character=="elara" else {}),
            }
        return {"actors":actors},{"character_continuity_review":review}

    def test_all_37_shots_have_expected_preference_rules_without_art_approval(self):
        d=self.report
        self.assertEqual(d["total_shots"],37)
        self.assertEqual(d["black_openings"],1)
        self.assertFalse(d["canonical_references_imported"])
        self.assertFalse(d["production_render_allowed"])
        self.assertTrue(d["generator_locked"])
        self.assertEqual(d["image_generation_calls"],0)
        self.assertEqual(len(self.shots),37)
        self.assertTrue(all(s["art_and_rig_approved"] is False
                            for s in self.shots.values()))

    def test_kael_clothing_changes_only_when_narrative_changes_world(self):
        k=lambda name:self.shots[name]["main_character_requirements"]["kael"]["wardrobe_version"]
        self.assertEqual(k("C01-P03"),"palace_trial_red_cloak")
        self.assertEqual(k("C02-P02"),"palace_trial_red_cloak")
        self.assertEqual(k("C04-P01"),"modern_world")
        self.assertEqual(k("C04-P03"),"modern_world")
        self.assertEqual(k("C05-P01"),"arken_red_cloak")
        self.assertEqual(k("C12-P01"),"arken_red_cloak")

    def test_elara_is_disguised_until_royal_reveal_C12(self):
        for sid,shot in self.shots.items():
            elara=shot["main_character_requirements"].get("elara")
            if elara is None:
                continue
            scene=int(sid[1:3])
            if scene<12:
                self.assertEqual(elara["wardrobe_version"],"street_disguise")
                self.assertFalse(elara["is_princess_identity_revealed"])
            else:
                self.assertEqual(elara["wardrobe_version"],"royal_white_violet")
                self.assertTrue(elara["is_princess_identity_revealed"])
        self.assertNotIn("elara",self.shots["C01-P04"]["main_character_requirements"])
        self.assertNotIn("elara",self.shots["C02-P01"]["main_character_requirements"])

    def test_original_refs_must_be_imported_and_sha_validated_first(self):
        shot=self.shots["C12-P02"]
        rig,qa=self.fake_approved_metadata(shot)
        with self.assertRaisesRegex(VideoForgeError,"EXACT_STYLE_SOURCE_NOT_IMPORTED"):
            validate_actor_wardrobe(shot,rig,qa,False)
        # This is a structural fixture, not actual source artwork.
        self.assertIsNone(validate_actor_wardrobe(shot,rig,qa,True))

    def test_royal_costume_in_street_and_wrong_face_are_blocked(self):
        shot=self.shots["C08-P01"]
        rig,qa=self.fake_approved_metadata(shot)
        rig["actors"][1]["continuity"]["wardrobe_version"]="royal_white_violet"
        with self.assertRaisesRegex(VideoForgeError,"WRONG_FACE_HAIR_OR_COSTUME"):
            validate_actor_wardrobe(shot,rig,qa,True)
        rig,qa=self.fake_approved_metadata(shot)
        rig["actors"][0]["continuity"]["style_reference_sha256"]="0"*64
        with self.assertRaisesRegex(VideoForgeError,"WRONG_FACE_HAIR_OR_COSTUME"):
            validate_actor_wardrobe(shot,rig,qa,True)
        rig,qa=self.fake_approved_metadata(shot)
        qa["character_continuity_review"]["elara"]["approved"]=False
        with self.assertRaisesRegex(VideoForgeError,"HUMAN_QA_REQUIRED"):
            validate_actor_wardrobe(shot,rig,qa,True)

    def test_disguise_cannot_be_marked_as_royal_reveal(self):
        shot=self.shots["C07-P03"]
        rig,qa=self.fake_approved_metadata(shot)
        qa["character_continuity_review"]["elara"]["princess_identity_revealed"]=True
        with self.assertRaisesRegex(VideoForgeError,"SPOILER_OR_REVEAL_WRONG"):
            validate_actor_wardrobe(shot,rig,qa,True)

    def test_early_palace_princess_must_not_be_identifiable_even_in_background(self):
        shot=self.shots["C01-P02"]
        plan_cast={"id":shot["shot_id"],"scene":shot["scene"],
                   "characters":shot["planned_cast"]}
        rig={"actors":[]}
        qa={}
        with self.assertRaisesRegex(VideoForgeError,"PRINCESS_SPOILER_VISUAL_QA"):
            verify_shot_continuity(plan_cast,rig,qa)
        qa={"visual_spoiler_review":{
            "approved":True,"elara_identifiable":False,"royal_elara_visible":False
        }}
        self.assertIsNone(verify_shot_continuity(plan_cast,rig,qa))
        qa["visual_spoiler_review"]["royal_elara_visible"]=True
        with self.assertRaisesRegex(VideoForgeError,"PRINCESS_SPOILER_VISUAL_QA"):
            verify_shot_continuity(plan_cast,rig,qa)

    def test_real_current_episode_cannot_claim_continuity_is_approved(self):
        shot=self.shots["C12-P02"]
        plan_cast={
            "id":shot["shot_id"],
            "characters":shot["planned_cast"],
        }
        rig,qa=self.fake_approved_metadata(shot)
        with self.assertRaisesRegex(VideoForgeError,"EXACT_STYLE_SOURCE_NOT_IMPORTED"):
            verify_shot_continuity(plan_cast,rig,qa)

if __name__=="__main__":
    unittest.main()
