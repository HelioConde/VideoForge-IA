"""A camada deve derivar da cena-mãe ORIGINAL, jamais de prompts legados."""
import json
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from videoforge import production_scene_layers as layers
from videoforge.errors import VideoForgeError


class SceneMotherLayerTests(TestCase):
    def test_all_scenes_covered_without_fixed_ceiling(self):
        plan,story,entry=layers.read_plan("otaku-br","spy-x-family-familia-de-mentira",1)
        self.assertEqual(len(plan["scenes"]),len(story["scenes"]))
        self.assertEqual(entry["scene"],story["scenes"][0]["id"])
        self.assertEqual(entry["required_layers"],["background","character-main"])
        self.assertFalse(plan["youtube_upload"])
        self.assertTrue(plan["no_fixed_scene_count"])

    def test_invalid_scene_number_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"NUMBER_INVALID"):
            layers.read_plan("otaku-br","spy-x-family-familia-de-mentira",999)

    def test_source_sha_and_scene_ledger_required(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"fake.png"
            report=Path(d)/"fake.production.json"
            source.write_bytes(b"not-real-png")
            report.write_text(json.dumps({"sha256":"a"*64}),encoding="utf-8")
            _,_,entry=layers.read_plan("otaku-br","spy-x-family-familia-de-mentira",1)
            with self.assertRaises((VideoForgeError,ValueError)):
                layers.validate_source(source,report,entry,
                                       "otaku-br","spy-x-family-familia-de-mentira")

    def test_legacy_character_prompt_is_never_default_in_production(self):
        import inspect
        src=inspect.getsource(layers.generate)
        self.assertIn("instruction=instruction+common",src)
        self.assertNotIn("aventureiro",src)
        self.assertNotIn("capa vermelha",src)


if __name__=="__main__":
    import unittest
    unittest.main()
