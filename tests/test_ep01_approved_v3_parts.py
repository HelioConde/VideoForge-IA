"""Independent V3 parts use exact creator-approved mother & aligned technical copy."""
import unittest

from videoforge import ep01_approved_v3_parts as ep

class ApprovedV3PartsTests(unittest.TestCase):
    def test_fixed_scope_and_no_sword(self):
        self.assertEqual(len(ep.ROLE_CONFIG),7)
        self.assertIn("background-clean",ep.ROLE_CONFIG)
        self.assertIn("character-kael",ep.ROLE_CONFIG)
        self.assertIn("object-lanca-esquerda",ep.ROLE_CONFIG)
        self.assertIn("object-lanca-direita",ep.ROLE_CONFIG)
        self.assertNotIn("object-espada-carrasco",ep.ROLE_CONFIG)

    def test_approved_source_sha_and_full_canvas(self):
        source=ep.aligned_source()
        self.assertTrue(source["path"].endswith("c01-p04-scene-mother-facing-throne-v3-native-aligned.png"))
        self.assertEqual(len(source["sha256"]),64)
        self.assertNotEqual(source["sha256"],ep.SOURCE_SHA)
        self.assertTrue(len(source["blob"])>500_000)

    def test_generation_preflight_independent_not_cutout(self):
        for part in ep.ROLE_CONFIG:
            if ep.existing_part(part):
                continue
            spec=ep.prepare(part)
            self.assertEqual(spec["part"],part)
            self.assertEqual(spec["role"],ep.ROLE_CONFIG[part]["role"])
            self.assertGreaterEqual(len(spec["images"]),2)
            self.assertLessEqual(len(spec["images"]),8)
            self.assertIn("NOT a crop",spec["prompt"])
            self.assertIn("No automatic rig",spec["prompt"])
            self.assertIn("941x1672",spec["prompt"])

    def test_native_canvas_kept_without_cropping_or_resizing(self):
        from io import BytesIO
        from pathlib import Path
        import tempfile
        from PIL import Image
        frame=Image.new("RGBA",(1200,1310),(0,0,0,0))
        frame.putpixel((600,600),(10,20,30,255))
        payload=BytesIO()
        frame.save(payload,format="PNG")
        spec={"source":{"sha256":"a"*64,"path":"test-approved-frame.png"},"reference_proofs":[]}
        with tempfile.TemporaryDirectory() as tmp:
            report=ep.validate_and_save("character-guarda_esquerdo",
                                         payload.getvalue(),Path(tmp),spec)
            self.assertEqual((report["width"],report["height"]),(1200,1310))
            self.assertTrue(report["native_canvas_requires_spatial_registration"])
            self.assertEqual(report["technical_postprocess"],"none")
            self.assertEqual(report["technical_qa"],
                             "candidate_native_canvas_requires_spatial_registration")
            self.assertFalse(report["rig_ready"])

if __name__=="__main__":
    unittest.main()
