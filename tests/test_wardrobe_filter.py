"""Owner-observed costume defects must reject; unknown shots may never pass."""
import copy
import unittest
from unittest.mock import patch

from videoforge.wardrobe_filter import evaluate,_facts
from videoforge.errors import VideoForgeError

class WardrobeFilterTests(unittest.TestCase):
    def test_red_black_inversion_beard_and_purple_bodice_are_rejected(self):
        result=evaluate()
        self.assertEqual(result["shot_count"],40)
        self.assertEqual(result["total_frames"],4890)
        self.assertEqual(result["decision"]["aldric"],"REPROVADO")
        self.assertEqual(result["decision"]["elara_palace"],"REPROVADO")
        self.assertEqual(result["decision"]["kael"],"REVISAO_PENDENTE")
        self.assertEqual(result["decision"]["elara_street"],"REVISAO_PENDENTE")
        self.assertEqual(
            {x["code"] for x in result["findings"]},
            {"aldric_red_black_inversion","aldric_beard_color_changed","elara_purple_bodice_missing"})
        self.assertEqual(len(result["shot_impact"]["aldric"]),7)
        self.assertEqual(len(result["shot_impact"]["elara_royal"]),6)
        self.assertEqual(len(result["shot_impact"]["elara_street"]),9)
        self.assertFalse(result["approved_for_canonical_use"])
        self.assertFalse(result["pixel_color_statistics_claimed"])
        self.assertFalse(result["pixel_level_outfit_or_beard_segmentation_available"])
        self.assertEqual(result["provider_calls"],0)
    def test_royal_purple_not_required_on_street_disguise(self):
        r=evaluate()
        by={s["shot_id"]:s for s in r["shot_risk_register"]}
        self.assertEqual(by["C08-P04"]["verdict"],"REVISAO_VISUAL_PENDENTE")
        self.assertNotIn("elara_purple_bodice_missing",by["C08-P04"]["blocking_known_reference_defects"])
        self.assertIn("elara_purple_bodice_missing",by["C12-P04"]["blocking_known_reference_defects"])
        self.assertIn("aldric_red_black_inversion",by["C01-P03"]["blocking_known_reference_defects"])
        self.assertTrue(all(not s["official_render_allowed"] for s in r["shot_risk_register"]))
        self.assertTrue(all(not s["individual_shot_pixels_visually_checked"] for s in r["shot_risk_register"]))
    def test_swapped_colors_or_missing_beard_observation_is_not_accepted(self):
        from videoforge.wardrobe_filter import _read_json,NAMES
        from videoforge.remake_autopilot import ROOT,EPISODE
        data={name:_read_json(ROOT/EPISODE/file) for name,file in NAMES.items()}
        corrupted=copy.deepcopy(data)
        corrupted["aldric"]["known_defects"][0]["scene_b"]["center_panel_color"]="preto"
        with self.assertRaisesRegex(VideoForgeError,"RED_BLACK_INVERSION_UNVERIFIED"):
            _facts(corrupted)
        corrupted=copy.deepcopy(data)
        corrupted["aldric"]["known_defects"][1]["beard_color_difference_confirmed_by_user"]=False
        with self.assertRaisesRegex(VideoForgeError,"BEARD_CHANGE_NOT_RECORDED"):
            _facts(corrupted)
    def test_deterministic_without_provider_calls(self):
        self.assertEqual(evaluate(),evaluate())
        self.assertFalse(evaluate()["new_images_generated"])

if __name__=="__main__":
    unittest.main()
