"""Preflight sem chamadas pagas para V3 do eixo Kael -> Trono."""
import unittest
from pathlib import Path
from videoforge import ep01_throne_orientation_v3 as engine

class ThroneFacingV3Test(unittest.TestCase):
    def test_three_unique_versioned_outputs(self):
        self.assertEqual(set(engine.SOURCE_SHOTS),
                         {"C01-P03","C01-P04","C01-P04-ALT"})
        names=[x["asset"] for x in engine.SOURCE_SHOTS.values()]
        self.assertEqual(len(names),len(set(names)))
        self.assertTrue(all("-v3" in name for name in names))
        self.assertEqual(engine.PRODUCER,"production-scene-mother-orientation-v3")

    def test_canonical_cast_framing(self):
        p03=engine.SOURCE_SHOTS["C01-P03"]
        p04=engine.SOURCE_SHOTS["C01-P04"]
        self.assertEqual(p03["shot"],"C01-P03")
        self.assertEqual(p04["shot"],"C01-P04")
        self.assertIn("No guards",p03["cast"])
        self.assertIn("SEATED",p04["cast"])
        for target,entry in engine.SOURCE_SHOTS.items():
            self.assertIn("throne",entry["direction"].lower())
            self.assertIn("Kael",entry["direction"])
            self.assertEqual(len(entry["sha256"]),64)
            self.assertTrue(entry["source"].startswith("assets/geracoes/"))

    def test_all_inputs_sha_checked_and_provably_not_approved(self):
        for target in engine.SOURCE_SHOTS:
            if engine.archived(target):
                # Idempotent after a real generation.
                continue
            spec=engine.prepare(target)
            self.assertEqual(spec["target"],target)
            self.assertGreaterEqual(len(spec["images"]),4)
            self.assertLessEqual(len(spec["images"]),8)
            self.assertIn("NO automatic approval",spec["prompt"])
            self.assertIn("FACE the THRONE",spec["prompt"])
            self.assertTrue(spec["source_sha"])

if __name__ == "__main__":
    unittest.main()
