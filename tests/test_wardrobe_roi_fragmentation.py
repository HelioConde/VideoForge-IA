"""QA de fragmentacao: diagnostico em pixels nativos, nunca aprovacao."""
import unittest
from PIL import Image
from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_fragmentation import component_stats, run

class FragmentationTests(unittest.TestCase):
    def test_diagonal_neighbors_are_connected(self):
        m=Image.new("L",(10,10),0)
        m.putpixel((1,1),255)
        m.putpixel((2,2),255)
        m.putpixel((8,8),255)
        x=component_stats(m)
        self.assertEqual(x["connected_components"],2)
        self.assertEqual(x["largest_component_pixels"],2)
        self.assertEqual(x["single_pixel_islands"],1)
        self.assertEqual(x["selected_pixels"],3)
    def test_empty_mask_is_never_approved(self):
        x=component_stats(Image.new("L",(7,7)))
        self.assertEqual(x["connected_components"],0)
        self.assertEqual(x["largest_component_share_percent"],0)
    def test_native_mask_cannot_be_non_l(self):
        with self.assertRaisesRegex(VideoForgeError,"MASK_INVALID"):
            component_stats(Image.new("RGBA",(4,4)))
    def test_real_eight_archived_masks_still_blocked(self):
        output=run()
        self.assertEqual(output["masks_analyzed"],8)
        self.assertEqual(output["semantic_masks_approved"],0)
        self.assertEqual(output["canonical_pairs_ready"],0)
        self.assertTrue(output["r2_blocked"])
        self.assertTrue(output["no_pixels_modified"])
        for row in output["rows"]:
            self.assertGreater(row["pixel_fragmentation"]["selected_pixels"],127)
            self.assertFalse(row["semantic_verification"])
            self.assertFalse(row["official_art_usable"])

if __name__=="__main__":
    unittest.main()
