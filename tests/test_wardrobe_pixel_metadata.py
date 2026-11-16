"""QA pixel audit is evidence, never a canonical approval."""
import json
import unittest
from videoforge.remake_autopilot import ROOT, EPISODE

class PixelAuditMetadataTests(unittest.TestCase):
    def test_real_sha_report_cannot_be_interpreted_as_approved_outfit(self):
        base=ROOT/EPISODE
        report=json.loads((base/"QA-CORES-PIXELS-FIGURINO-V2.json").read_text(encoding="utf-8"))
        state=json.loads((base/"estado-atual.json").read_text(encoding="utf-8"))
        self.assertEqual(report["schema"],"videoforge/wardrobe-pixel-audit/v1")
        self.assertEqual(len(report["rows"]),6)
        self.assertEqual(report["measured_rgba_sources"],4)
        self.assertEqual(report["approved_full_outfits"],0)
        self.assertFalse(report["beard_color_exactly_measured"])
        self.assertFalse(report["purple_bodice_exactly_measured"])
        self.assertFalse(report["red_outer_vs_black_center_measured"])
        self.assertFalse(report["canonical_identity_approved"])
        self.assertEqual(report["provider_calls"],0)
        self.assertTrue(all(x["percent"] is None for x in report["rows"]
                            if x["actor"]=="elara"))
        self.assertFalse(state["wardrobe_real_pixel_audit_20261116"]["automatic_approval"])
        self.assertFalse(state["autopilot_checkpoint"]["dispatch_allowed"])
    def test_output_cannot_mask_owner_rejection(self):
        base=ROOT/EPISODE
        state=json.loads((base/"estado-atual.json").read_text(encoding="utf-8"))
        report=json.loads((base/"RELATORIO-FILTRO-FIGURINO-V2.json").read_text(encoding="utf-8"))
        self.assertEqual(report["decision"]["aldric"],"REPROVADO")
        self.assertEqual(report["decision"]["elara_palace"],"REPROVADO")
        self.assertEqual(state["autopilot_checkpoint"]["blocker"],
                         "wardrobe_identity_rejected_reference_missing")

if __name__=="__main__":
    unittest.main()
