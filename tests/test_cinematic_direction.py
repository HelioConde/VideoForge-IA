"""Planejamento cinematográfico do dorama: sem chamada a IA e sem PNG novo."""
from __future__ import annotations
from pathlib import Path
import unittest

from videoforge.cinematic_direction import (
    CLOSE_TYPES,load_plan,validate_plan,resolve_shot,prompt_direction,
    validate_visual_reference_gate,
)
from videoforge.errors import VideoForgeError
from videoforge.production_scenes import scene_prompt

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"

class CinematicDirectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=load_plan(CHANNEL,VIDEO)
        cls.shots=cls.plan["shots"]

    def test_37_shots_have_variety_and_exact_frames(self):
        r=validate_plan(CHANNEL,VIDEO,self.plan)
        self.assertEqual(r["shot_count"],37)
        self.assertEqual(r["face_closeups"],12)
        self.assertGreaterEqual(r["types"]["over_shoulder"],4)
        self.assertGreaterEqual(r["types"]["wide"],3)
        self.assertEqual(sum(s["end_frame_exclusive"]-s["start_frame"] for s in self.shots),4890)

    def test_first_shot_is_black_and_not_art_generation(self):
        shot=resolve_shot(CHANNEL,VIDEO,1,"C01-P01")
        self.assertEqual(shot["shot_type"],"black")
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_BLACK_FRAME_NEVER_GENERATE_IMAGE"):
            scene_prompt(CHANNEL,VIDEO,1,"C01-P01")

    def test_closeup_eyes_is_not_generic_ensemble(self):
        text,scene=scene_prompt(CHANNEL,VIDEO,12,"C12-P01")
        self.assertIn("C12-P01",text)
        self.assertIn("close",text.lower())
        self.assertIn("olhos",text.lower())
        self.assertIn("Kael",text)
        self.assertNotIn("Elara:",text)
        self.assertNotIn("Aldric:",text)
        self.assertIn("Remotion",text)
        self.assertLessEqual(len(text),5000)

    def test_princess_is_hidden_in_tribunal_until_reveal(self):
        intro,_=scene_prompt(CHANNEL,VIDEO,1,"C01-P04")
        self.assertNotIn("Elara:",intro)
        self.assertIn("PROIBIDOS",intro)
        reveal,_=scene_prompt(CHANNEL,VIDEO,12,"C12-P02")
        self.assertIn("Elara:",reveal)
        self.assertIn("Aldric:",reveal)
        self.assertIn("Kael:",reveal)

    def test_all_non_black_shots_generate_valid_distinct_prompts_without_proxy(self):
        prompts=set()
        for shot in self.shots:
            if shot["shot_type"]=="black":
                continue
            number=int(shot["id"][1:3])
            prompt,scene=scene_prompt(CHANNEL,VIDEO,number,shot["id"])
            self.assertLessEqual(len(prompt),5000,shot["id"])
            self.assertIn(shot["id"],prompt)
            self.assertIn("foco",prompt.lower())
            self.assertIn("Sem qualquer texto",prompt)
            self.assertNotIn("Sem texto da missão SOMENTE NO PÔSTER",prompt)
            self.assertEqual(scene["number"],number)
            prompts.add(prompt)
        self.assertEqual(len(prompts),36)

    def test_specific_shot_must_belong_to_scene(self):
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_SHOT_NOT_IN_SCENE"):
            scene_prompt(CHANNEL,VIDEO,1,"C02-P01")

    def test_reference_conflict_and_generation_gate_not_silently_approved(self):
        gate=validate_visual_reference_gate(CHANNEL,VIDEO)
        self.assertFalse(gate["new_image_generation_allowed"])
        self.assertFalse(gate["source_image_files_verified"])
        self.assertTrue(gate["canonical_identity_conflict"])

    def test_other_project_preserves_original_prompt_contract(self):
        text,scene=scene_prompt("otaku-br","spy-x-family-familia-de-mentira",1)
        self.assertIn(scene["visual_direction"],text)
        self.assertIn("Loid",text)

if __name__=="__main__":
    unittest.main()
