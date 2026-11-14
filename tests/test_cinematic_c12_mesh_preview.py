"""QA of the first *technical* C12 mesh preview metadata.

Does not claim that unimported PNGs/rigs are approved or render official.
"""
from __future__ import annotations
import json
from pathlib import Path
import unittest

FILE=(Path(__file__).resolve().parents[1]/
      "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"/
      "qa-c12-rig-malha-v2.json")

class C12TechnicalMeshPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads(FILE.read_text(encoding="utf8"))

    def test_real_triangles_are_declared_per_independent_piece(self):
        m=self.m
        parts=m["meshParts"]
        self.assertEqual(m["schema"],"videoforge/c12-mesh-rig-technical-draft/v2")
        self.assertEqual(len(parts),5)
        self.assertEqual(sum(x["triangles"] for x in parts),512)
        self.assertEqual(len({x["id"] for x in parts}),5)
        self.assertTrue(all(x["columns"]>=4 and x["rows"]>=8 for x in parts))
        self.assertTrue(all(x["triangles"]==2*x["columns"]*x["rows"] for x in parts))
        self.assertTrue(all(x["meshKind"] in
                            ("cape","hair-front-left","hair-back","cloth","earring")
                            for x in parts))
        self.assertTrue(all(x["polygon"] and len(x["pivot"])==2
                            for x in parts))

    def test_source_coordinates_and_shot_timing_are_constrained(self):
        m=self.m
        self.assertEqual(m["sourceCanvas"],[941,1672])
        self.assertEqual(m["previewCanvas"],[720,1280])
        self.assertEqual(m["fps"],30)
        self.assertEqual(m["frames"],360)
        self.assertEqual([x["id"] for x in m["shot_timing"]],
                         ["C12-P01","C12-P02","C12-P03"])
        self.assertTrue(all(x["endFrameExclusive"]-x["startFrame"]==120
                            for x in m["shot_timing"]))
        for part in m["meshParts"]:
            self.assertIn(part["shot"],("C12-P02","C12-P03"))
            self.assertTrue(0<part["amplitudePx"]<=12)
            self.assertTrue(all(
                0<=x<941 and 0<=y<1672 for x,y in part["polygon"]
            ))
            self.assertTrue(0<=part["pivot"][0]<941)
            self.assertTrue(0<=part["pivot"][1]<1672)

    def test_locked_face_close_has_no_hair_or_cloth_drift(self):
        m=self.m
        self.assertFalse(any(x["shot"]=="C12-P01" for x in m["meshParts"]))
        self.assertEqual(m["shot_timing"][0]["motion"],"pupils_only_locked_head")
        self.assertTrue(m["per_part_motion"])
        self.assertFalse(m["global_png_position_animation"])

    def test_preview_is_not_production_or_false_human_approval(self):
        m=self.m
        self.assertTrue(m["technical_mesh_proof"])
        self.assertFalse(m["three_js_remotion_full_rig_ready"])
        self.assertFalse(m["technical_layers_human_approved"])
        self.assertFalse(m["official_render_allowed"])
        self.assertFalse(m["neutral_recomposition_qa_pending"] is False)
        self.assertFalse(m["artifacts_uploaded_to_github"])
        self.assertFalse(m["youtube_uploaded"])
        self.assertFalse(m["original_pngs_modified"])
        self.assertEqual(m["external_image_generation_calls"],0)
        self.assertEqual(len(m["preview"]["local_sha256"]),64)

if __name__=="__main__":
    unittest.main()
