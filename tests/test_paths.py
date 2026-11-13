"""Channel-isolated folder contracts reused from the previous VideoForge."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from videoforge.errors import VideoForgeError
from videoforge.paths import CHANNEL_IDS, resolve_video_context

ROOT = Path(__file__).resolve().parents[1]


class ChannelFolderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        directory = self.root / "canal" / "otaku-br"
        directory.mkdir(parents=True)
        (directory / "canal.json").write_text(json.dumps({
            "id": "otaku-br",
            "modelo_padrao": "imagem-estatica",
            "youtube": {"conectado": False, "upload_habilitado": False},
        }), encoding="utf-8")
        model_dir = self.root / "modelos" / "imagem-estatica"
        model_dir.mkdir(parents=True)
        (model_dir / "modelo.json").write_text(json.dumps({
            "id": "imagem-estatica", "operacional": True,
        }), encoding="utf-8")
        video_dir = directory / "videos" / "episodio-001"
        video_dir.mkdir(parents=True)
        self.video = video_dir / "video.json"
        self.manifest = {"channel": "otaku-br"}
        self.video.write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_old_project_channel_tree_exists_in_new_repo(self):
        self.assertEqual(len(CHANNEL_IDS), 5)
        for channel in CHANNEL_IDS:
            with self.subTest(channel=channel):
                base = ROOT / "canal" / channel
                cfg = json.loads((base / "canal.json").read_text(encoding="utf-8"))
                self.assertEqual(cfg["id"], channel)
                self.assertFalse(cfg["youtube"]["conectado"])
                self.assertFalse(cfg["youtube"]["upload_habilitado"])
                self.assertTrue((base / "README.md").is_file())
                self.assertTrue((base / "videos" / "README.md").is_file())
                index = json.loads((base / "conteudos" / "indice.json").read_text())
                self.assertEqual(index["canal_id"], channel)
                candidates = json.loads((base / "editorial" / "candidatos.json").read_text())
                self.assertEqual(candidates["candidates"], [])
                ledger = json.loads((base / "editorial" / "reservas.json").read_text())
                self.assertEqual(ledger["channel"], channel)
                self.assertEqual(ledger["entries"], [])
        self.assertTrue((ROOT / "modelos" / "imagem-estatica" / "modelo.json").is_file())
        self.assertTrue((ROOT / "modelos" / "camadas-animadas" / "modelo.json").is_file())

    def test_default_video_and_output_use_same_channel(self):
        context = resolve_video_context(self.video, self.manifest)
        self.assertEqual(context.channel, "otaku-br")
        self.assertEqual(context.video_id, "episodio-001")
        self.assertEqual(context.model, "imagem-estatica")
        self.assertEqual(
            context.output,
            self.root / "output" / "otaku-br" / "videos" / "episodio-001" / "video.mp4",
        )
        self.assertFalse(context.output.parent.exists())

    def test_cross_channel_manifest_is_rejected(self):
        with self.assertRaisesRegex(VideoForgeError, "VIDEO_CHANNEL_MISMATCH"):
            resolve_video_context(self.video, {"channel": "gamer"})

    def test_wrong_manifest_directory_is_rejected(self):
        outside = self.root / "projects" / "otaku-br" / "video.json"
        with self.assertRaisesRegex(VideoForgeError, "VIDEO_MANIFEST_LOCATION_INVALID"):
            resolve_video_context(outside, self.manifest)

    def test_unscoped_output_is_rejected(self):
        for target in (
            self.root / "dist" / "video.mp4",
            self.root / "output" / "gamer" / "videos" / "episodio-001" / "video.mp4",
        ):
            with self.subTest(output=str(target)), self.assertRaisesRegex(
                VideoForgeError, "VIDEO_OUTPUT_NOT_CHANNEL_SCOPED"
            ):
                resolve_video_context(self.video, self.manifest, requested_output=target)

    def test_override_model_is_checked_not_implicitly_available(self):
        extra_dir = self.root / "modelos" / "camadas-animadas"
        extra_dir.mkdir(parents=True)
        (extra_dir / "modelo.json").write_text(json.dumps({
            "id": "camadas-animadas", "operacional": False,
        }))
        with self.assertRaisesRegex(VideoForgeError, "VIDEO_MODEL_NOT_IMPLEMENTED"):
            resolve_video_context(self.video, {"channel": "otaku-br", "modelo": "camadas-animadas"})

    def test_channel_identity_config_must_match(self):
        config = self.root / "canal" / "otaku-br" / "canal.json"
        obj = json.loads(config.read_text())
        obj["id"] = "gamer"
        config.write_text(json.dumps(obj))
        with self.assertRaisesRegex(VideoForgeError, "CHANNEL_CONFIG_ID_MISMATCH"):
            resolve_video_context(self.video, self.manifest)

    def test_output_symlink_cannot_redirect_to_other_channel(self):
        (self.root / "output").symlink_to(self.root / "outside", target_is_directory=True)
        with self.assertRaisesRegex(VideoForgeError, "CHANNEL_PATH_SYMLINK_NOT_ALLOWED"):
            resolve_video_context(self.video, self.manifest)


if __name__ == "__main__":
    unittest.main()
