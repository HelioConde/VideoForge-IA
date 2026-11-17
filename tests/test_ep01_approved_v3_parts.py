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
        self.assertTrue(source["file"].endswith("c01-p04-scene-mother-facing-throne-v3-native-aligned.png"))
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

if __name__=="__main__":
    unittest.main()
