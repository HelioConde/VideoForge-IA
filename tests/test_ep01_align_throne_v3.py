"""Approved V3 image: exact SHA and metadata before technical alignment."""
import unittest
from videoforge import ep01_align_throne_v3 as align

class AlignThroneV3Test(unittest.TestCase):
    def test_source_identity_immutable(self):
        self.assertEqual(align.SHOT,"C01-P04")
        self.assertEqual(align.SOURCE_RUN,44152300579)
        self.assertEqual(len(align.SOURCE_SHA),64)
        self.assertIn("-v3-aligned",align.PRODUCER)
        self.assertNotEqual(align.ASSET,align.SOURCE_ASSET)

    def test_preflight_creator_approval_provenance(self):
        proven=align.approved_original()
        self.assertTrue(proven["file"].endswith("c01-p04-scene-mother-facing-throne-v3.png"))
        self.assertIn("APROVACOES-VISUAIS-C01-V3.json",proven["approval_file"])
        self.assertIsInstance(proven["blob"],bytes)
        self.assertTrue(len(proven["blob"])>500_000)

if __name__=="__main__":
    unittest.main()
