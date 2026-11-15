"""EP01 Remake V2: real production prompt uses active manifesto, not V1 gate."""
from __future__ import annotations

import copy
import unittest

from videoforge.cinematic_direction import (
    load_plan,load_active_remake_plan,validate_active_remake_plan,
    resolve_shot,assert_shot_generation_ready,
    assert_scene_reference_matches_anchor,validate_visual_reference_gate,
)
from videoforge.production_scenes import scene_prompt
from videoforge.errors import VideoForgeError

CH="alchemy-lab"
VID="mmorpg-conquiste-a-princesa-ep01"


class RemakeCinematicIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=load_active_remake_plan(CH,VID)

    def test_source_of_active_plan_is_remake_v2(self):
        self.assertIsNotNone(self.plan)
        summary=validate_active_remake_plan(CH,VID,self.plan)
        self.assertEqual(summary["shot_count"],37)
        self.assertEqual(summary["art_required"],36)
        self.assertEqual(summary["duration_frames"],4890)
        self.assertTrue(summary["editorial_images_unlimited"])

    def test_legacy_plan_remains_readable_but_not_selected(self):
        old=load_plan(CH,VID)
        self.assertEqual(old["legacy_scope"],"pre_remake_cinematic_shot_description")
        self.assertEqual(old["production_gate"]["new_generation_allowed"],False)
        shot=resolve_shot(CH,VID,1,"C01-P02")
        self.assertEqual(shot["remake_source"],"remake-ep01-planos.json")
        self.assertEqual(shot["dramatic_direction"],
                         "Espada pertence ao carrasco; mão, bainha e lâmina separadas")

    def test_37_cinematic_prompts_are_distinct_and_new_style(self):
        prompts=set()
        for original in self.plan["shots"]:
            sid=original["shot_id"]
            if sid=="C01-P01":
                continue
            scene=int(sid[1:3])
            prompt,_=scene_prompt(CH,VID,scene,sid)
            with self.subTest(sid=sid):
                self.assertIn(sid,prompt)
                self.assertIn("Cinematic Semi-Realistic Fantasy Anime",prompt)
                self.assertIn("Direcao dramatica do remake V2",prompt)
                self.assertLessEqual(len(prompt),5000)
                self.assertIn("foco",prompt.lower())
                self.assertIn("Sem qualquer texto",prompt)
            prompts.add(prompt)
        self.assertEqual(len(prompts),36)

    def test_critical_story_and_black_frame_preserved(self):
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_BLACK_FRAME_NEVER_GENERATE_IMAGE"):
            scene_prompt(CH,VID,1,"C01-P01")
        opening,_=scene_prompt(CH,VID,1,"C01-P02")
        self.assertIn("Espada pertence ao carrasco",opening)
        self.assertNotIn("Elara:",opening)
        reveal,_=scene_prompt(CH,VID,12,"C12-P02")
        self.assertIn("Elara:",reveal)
        self.assertIn("Aldric:",reveal)
        self.assertIn("Kael:",reveal)
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_SHOT_NOT_IN_SCENE"):
            scene_prompt(CH,VID,1,"C12-P02")

    def test_tampering_with_timeline_or_princess_fails(self):
        for mutation,error in (
            (lambda p: p["shots"][1].update(frame_start=61),"REMAKE_SHOT_TIMELINE_MISMATCH"),
            (lambda p: p["shots"][2].update(cast=["elara"]),"REMAKE_SHOT_VISUAL_CONTRACT_INVALID"),
            (lambda p: p.update(version="v1"),"REMAKE_SHOT_MANIFEST_ORIGIN_INVALID"),
            (lambda p: p["shots"][1].update(publishable=True),"REMAKE_SHOT_FALSE_PUBLICATION_APPROVAL"),
        ):
            modified=copy.deepcopy(self.plan)
            mutation(modified)
            with self.subTest(error=error):
                with self.assertRaisesRegex(VideoForgeError,error):
                    validate_active_remake_plan(CH,VID,modified)

    def test_real_anchor_and_paid_provider_not_claimed(self):
        gate=validate_visual_reference_gate(CH,VID)
        self.assertEqual(gate["active_manifest"],"remake-ep01-planos.json")
        self.assertTrue(gate["editorial_generation_authorized"])
        self.assertFalse(gate["source_image_files_verified"])
        self.assertFalse(gate["new_image_generation_allowed"])
        self.assertFalse(gate["paid_provider_calls_approved"])
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_CANONICAL_REFERENCE_NOT_APPROVED"):
            assert_shot_generation_ready(CH,VID)
        with self.assertRaisesRegex(VideoForgeError,"REMAKE_SCENE_REFERENCE_ANCHOR_SHA_MISMATCH"):
            assert_scene_reference_matches_anchor(CH,VID,"0"*64)

    def test_other_channel_still_uses_legacy_behavior(self):
        self.assertIsNone(load_active_remake_plan("otaku-br","spy-x-family-familia-de-mentira"))
        prompt,scene=scene_prompt("otaku-br","spy-x-family-familia-de-mentira",1)
        self.assertIn(scene["visual_direction"],prompt)
        self.assertNotIn("Direcao dramatica do remake V2",prompt)


if __name__=="__main__":
    unittest.main()
