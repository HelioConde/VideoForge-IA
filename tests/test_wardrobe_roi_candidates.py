"""Propostas visuais NÃO substituem aprovação de barba e figurino."""
import unittest

from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_candidates import board_to_source, count_mask_pixels, run


class ROICandidateTests(unittest.TestCase):
    def test_coordinate_projection_on_both_source_sizes(self):
        a = board_to_source([[350, 275], [357, 272], [367, 276]], (1024, 1536), 0)
        self.assertEqual(len(a), 3)
        self.assertTrue(all(0 <= x < 1024 and 0 <= y < 1536 for x,y in a))
        b = board_to_source([[1166, 277], [1180, 274], [1192, 294]], (941, 1672), 1)
        self.assertEqual(len(b), 3)
        self.assertTrue(all(0 <= x < 941 and 0 <= y < 1672 for x,y in b))
    def test_outside_and_tiny_masks_rejected(self):
        with self.assertRaisesRegex(VideoForgeError, "OUTSIDE_SOURCE"):
            board_to_source([[5, 5], [9, 6], [9, 15]], (1024, 1536), 0)
        with self.assertRaisesRegex(VideoForgeError, "MASK_INVALID"):
            count_mask_pixels((100, 100), [(2,2),(3,2),(2,3)])
    def test_real_assets_produce_eight_unverified_patches(self):
        r = run()
        self.assertEqual(r["candidate_count"], 8)
        self.assertEqual(r["validated_pair_count"], 0)
        self.assertTrue(r["r2_blocked"])
        self.assertEqual(r["paid_calls"], 0)
        self.assertFalse(r["original_images_modified"])
        self.assertEqual(len(r["candidates"]), 4)
        for pair in r["candidates"]:
            self.assertEqual(pair["status"], "CANDIDATO_NAO_VERIFICADO")
            self.assertEqual(len(pair["sources"]), 2)
            for source in pair["sources"]:
                self.assertGreaterEqual(source["candidate_mask_pixels"], 128)
                self.assertFalse(source["mask_semantically_verified"])
                self.assertFalse(source["approved_for_color_comparison"])


if __name__ == "__main__":
    unittest.main()
