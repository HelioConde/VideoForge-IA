"""Os pixels selecionados não viram máscaras canônicas automaticamente."""
import tempfile
import unittest

from PIL import Image

from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_refine import color_candidate, refine_mask, run


class ROIMaskRefinementTests(unittest.TestCase):
    def test_color_filter_excludes_skin_and_gold_from_beard(self):
        self.assertTrue(color_candidate("barba",(155,157,158)))
        self.assertFalse(color_candidate("barba",(211,147,100)))
        self.assertFalse(color_candidate("barba",(220,171,61)))
        self.assertTrue(color_candidate("corpete_roxo_palacio",(94,48,150)))
        self.assertFalse(color_candidate("corpete_roxo_palacio",(240,183,87)))
        self.assertTrue(color_candidate("painel_central",(126,30,45)))
        self.assertFalse(color_candidate("painel_central",(32,31,33)))
    def test_pixel_output_removes_foreign_color_inside_same_polygon(self):
        im=Image.new("RGB",(160,160),(220,160,90))
        for y in range(40,100):
            for x in range(35,100):
                im.putpixel((x,y),(105,47,158))
        mask, before, after, viable=refine_mask(
            im,[(20,20),(125,20),(125,125),(20,125)],"corpete_roxo_palacio")
        self.assertTrue(viable)
        self.assertGreater(before,after)
        self.assertEqual(mask.getpixel((50,60)),255)
        self.assertEqual(mask.getpixel((25,60)),0)
    def test_four_real_pairs_remain_unapproved(self):
        result=run()
        self.assertEqual(result["candidate_masks"],8)
        self.assertEqual(result["verified_semantic_masks"],0)
        self.assertEqual(result["verified_semantic_pairs"],0)
        self.assertTrue(result["r2_blocked"])
        self.assertEqual(result["provider_calls"],0)
        for pair in result["regions"]:
            self.assertFalse(pair["automatic_approval"])
            self.assertFalse(pair["automatic_rejection"])
            for side in pair["sources"]:
                self.assertGreater(side["seed_polygon_pixels"],128)
                self.assertFalse(side["semantic_mask_verified"])
                self.assertFalse(side["official_color_comparison_eligible"])


if __name__ == "__main__":
    unittest.main()
