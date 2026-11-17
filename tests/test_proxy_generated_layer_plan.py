"""Política: peças animáveis são imagens separadas pelo proxy, não recortes locais."""
import json
import unittest
from pathlib import Path

from videoforge.layered_shot_plan import REL, ROOT, validate
from videoforge.ep01_contact_gate import audit


class ProxyGeneratedLayerPolicyTests(unittest.TestCase):
    def test_all_39_visual_shots_require_proxy_generated_assets(self):
        summary=validate()
        self.assertEqual(summary["shot_mothers_to_generate"],39)
        self.assertTrue(summary["separated_assets_from_proxy"])
        self.assertFalse(summary["local_cutout_for_rig_allowed"])
        plan=json.loads((ROOT / REL / "PLANO-CAMADAS-CAMERA-EP01.json").read_text())
        self.assertFalse(plan["pose_images_as_prerequisite"])
        shots=[s for s in plan["shots"] if s["id"]!="C01-P01"]
        self.assertEqual(len(shots),39)
        for sh in shots:
            with self.subTest(shot=sh["id"]):
                imgs=sh["images"]
                self.assertTrue(imgs["mother_figure_is_visual_reference_not_cutout_source"])
                self.assertEqual(imgs["local_segmentation_policy"],"QA_only_never_final_source")
                self.assertEqual(imgs["asset_source_method"],"proxy_generated_separate_image")
                self.assertTrue(imgs["proxy_generation_requests"])
                self.assertEqual(len({r["id"] for r in imgs["proxy_generation_requests"]}),
                                 len(imgs["proxy_generation_requests"]))
                for req in imgs["proxy_generation_requests"]:
                    self.assertEqual(req["method"],"proxy_generated_separate_image")

    def test_legacy_mask_sources_still_block_rig(self):
        qa=audit()
        self.assertFalse(qa["render_ready"])
        self.assertIn("legacy_v1_pixel_masks_not_proxy_generated_rig_assets",
                      qa["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()
