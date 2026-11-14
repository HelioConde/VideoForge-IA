"""Regressão: não aprovar contaminação da cabeça por outros personagens."""
import unittest
from videoforge.rig_three_candidate_qa import foreign_character_pixel


class CandidateIsolationTests(unittest.TestCase):
    def test_detects_dark_foreign_area_repainted_as_pink(self):
        self.assertTrue(foreign_character_pixel(bytes((45,45,50)),bytes((250,153,143))))
        self.assertTrue(foreign_character_pixel(bytes((120,45,45)),bytes((250,153,143))))
    def test_does_not_reject_original_pink_hair_as_foreign(self):
        self.assertFalse(foreign_character_pixel(bytes((245,153,142)),bytes((251,154,147))))
    def test_does_not_reject_original_bright_skin(self):
        self.assertFalse(foreign_character_pixel(bytes((253,210,184)),bytes((253,208,187))))

if __name__=="__main__":
    unittest.main()
