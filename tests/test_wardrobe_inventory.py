"""Existing V1 outfit snapshots are NOT approved canonical references."""
import unittest
from videoforge.wardrobe_inventory import inventory
class ExistingWardrobeInventoryTests(unittest.TestCase):
    def test_catalog_contains_real_art_never_canonical(self):
        result=inventory()
        self.assertEqual(result["candidate_count"],6)
        self.assertEqual(result["verified_owner_approved_complete_outfits"],0)
        self.assertFalse(result["r2_ready"])
        self.assertFalse(result["visual_approval"])
        self.assertEqual(result["image_provider_calls"],0)
        self.assertTrue(all(len(x["sha256"])==64 and not x["owner_approved_full_outfit"]
                            and not x["usable_as_grounded_r2_without_new_review"]
                            for x in result["candidates"]))
    def test_review_inventory_deterministic(self):
        self.assertEqual(inventory(),inventory())
if __name__=="__main__":
    unittest.main()
