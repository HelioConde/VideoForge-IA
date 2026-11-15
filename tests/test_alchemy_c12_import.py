"""Technical PNG archival must fail closed without original bytes."""
import unittest
from videoforge.c12_technical_preview import PART_SHAS, SOURCES, bbox, plan
from videoforge.import_c12_technical_zip import targets

class C12TechnicalArchiveTest(unittest.TestCase):
    def test_exact_seven_known_png_sha_targets(self):
        mapping=targets()
        self.assertEqual(len(mapping),7)
        self.assertEqual(set(PART_SHAS.values()).issubset(mapping),True)
        self.assertEqual({s[2] for s in SOURCES.values()}.issubset(mapping),True)

    def test_source_sprite_crop_sizes_are_grounded(self):
        mapping=targets()
        for part in plan()["meshParts"]:
            _,_,w,h=bbox(part["polygon"])
            self.assertEqual(mapping[PART_SHAS[part["id"]]][1],(w,h))

if __name__=="__main__":
    unittest.main()
