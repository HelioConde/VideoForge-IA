"""Ensure the canonical assembler never creates substitute media."""
from pathlib import Path
import tempfile
import unittest

from videoforge.production_assemble import prepare
from videoforge.errors import VideoForgeError


class ProductionAssemblyTests(unittest.TestCase):
    def test_missing_real_reference_or_scenes_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises((VideoForgeError,FileNotFoundError)):
                prepare("otaku-br","spy-x-family-familia-de-mentira",
                        root/"images",root/"voice",
                        root/"missing-reference.json")

    def test_only_real_production_assets_expected(self):
        import inspect
        from videoforge import production_assemble
        source=inspect.getsource(production_assemble.render)
        self.assertIn("mvp.render(manifest)",source)
        self.assertNotIn("spy_family_pilot",source)
        self.assertNotIn("draw_card",source)
        self.assertNotIn("smoke(",source)


if __name__=="__main__":
    unittest.main()
