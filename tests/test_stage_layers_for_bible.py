"""Separação RGBA: imagens geradas devem ter SHA e marcador antes de arquivar."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from videoforge.stage_layers_for_bible import stage
from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import ROOT


class StageLayersForBibleTests(unittest.TestCase):
    def test_real_png_stage_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            parent = root / "output/otaku-br/videos/sample-video/assets/cena-01"
            parent.mkdir(parents=True)
            original = (ROOT / "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/"
                        "assets/geracoes/production-art-request/43965460068/"
                        "c01-p04-imagem-inicial-v3.png")
            shutil.copyfile(original, parent / "cena-base.png")
            shutil.copyfile(original, parent / "background.png")
            data = original.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            from videoforge.persist_generated_assets import _png_info
            w, h = _png_info(data)
            obj = {
                "schema": "videoforge/scene-layers/v1",
                "channel": "otaku-br", "video_id": "sample-video", "scene": "cena-01",
                "source": {"file": "cena-base.png", "sha256": sha, "width": w, "height": h},
                "layers": {"background": {"file": "background.png", "sha256": sha,
                                          "width": w, "height": h, "technical_status": "verified"}}
            }
            (parent / "manifest.json").write_text(json.dumps(obj))
            first = stage("otaku-br", "sample-video", 1, root)
            self.assertEqual(first["staged"], 1)
            self.assertEqual(stage("otaku-br", "sample-video", 1, root)["staged"], 1)
            generated = root / "output/otaku-br/videos/sample-video/imagens/cena-01-background.png"
            self.assertEqual(hashlib.sha256(generated.read_bytes()).hexdigest(), sha)
            meta = json.loads(generated.with_suffix(".production.json").read_text())
            self.assertFalse(meta["human_visual_approval"])
            self.assertEqual(meta["source_originals_sha_verified"][0]["sha256"], sha)
            obj["layers"]["background"]["sha256"] = "0" * 64
            (parent / "manifest.json").write_text(json.dumps(obj))
            with self.assertRaisesRegex(VideoForgeError, "SHA_MISMATCH"):
                stage("otaku-br", "sample-video", 1, root)


if __name__ == "__main__":
    unittest.main()
