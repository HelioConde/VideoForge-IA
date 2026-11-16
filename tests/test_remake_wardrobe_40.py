"""Current V2 continuity must have 40 shots; legacy 37 is history."""
import unittest
from videoforge.remake_wardrobe_40 import derive

class RemakeWardrobe40Tests(unittest.TestCase):
    def test_all_current_shots_and_variants_are_consistent(self):
        report=derive()
        self.assertEqual(report["total_shots"],40)
        self.assertEqual(report["total_frames"],4890)
        self.assertEqual(len(report["shots"]),40)
        by={x["shot_id"]:x for x in report["shots"]}
        self.assertEqual(by["C01-P05"]["cast"],["guarda_esquerdo","guarda_direito"])
        self.assertEqual(by["C08-P04"]["costumes"]["elara"]["variant"],"street_disguise")
        self.assertEqual(by["C12-P04"]["costumes"]["elara"]["variant"],
                         "royal_white_violet_purple_bodice")
        self.assertTrue(by["C12-P04"]["costumes"]["elara"]["royal_purple_bodice_required"])
        self.assertEqual(by["C14-P02"]["costumes"]["aldric"]["variant"],"royal_burgundy_gold")
        self.assertFalse(by["C01-P02"]["requires_verified_royal_costume"])
        self.assertTrue(by["C02-P01"]["requires_verified_royal_costume"])
        self.assertEqual(report["verified_owner_approved_full_royal_outfits"],0)
        self.assertFalse(report["human_approved"])
        self.assertFalse(report["cannot_auto_generate_character_art_before_full_outfit_approval"] is False)
        self.assertTrue(all(not row["official_shot_render_allowed"] for row in report["shots"]))
        self.assertTrue(all(not row["characters_or_costumes_auto_approved"] for row in report["shots"]))
    def test_same_report_without_modifying_art(self):
        self.assertEqual(derive(sync=False),derive(sync=False))
        self.assertEqual(derive(sync=False)["image_provider_calls"],0)
if __name__=="__main__":
    unittest.main()
