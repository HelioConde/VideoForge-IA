"""No EP01, as quatro camadas derivam da mesma cena-mãe SHA."""
import hashlib
import unittest
from unittest.mock import patch

from videoforge import ep01_shot_layers as layer
from videoforge.errors import VideoForgeError


class EP01ShotLayerTests(unittest.TestCase):
    def test_four_components_stay_in_original_frame(self):
        cfg=layer.read_plan()
        self.assertEqual(len(cfg["parts"]),4)
        self.assertEqual({x["id"] for x in cfg["parts"]},layer.VALID_PARTS)
        self.assertEqual([x["id"] for x in cfg["parts"] if x["mode"]=="opaque"],
                         ["background-clean"])
        self.assertEqual(cfg["mother_sha256"],
                         "b055b93e2174625adb4b7f5eb4f5a40f88f9353bce0fe50e0ac193d6eb002a5e")

    def test_real_sha_source_is_reused_for_every_component(self):
        # Inspecionar cada preflight mesmo depois que a primeira camada for
        # arquivada; o guard anti-duplicação é testado separadamente.
        with patch.object(layer,"archived_layer",return_value=None):
            with patch.object(layer.proxy_images,"call_proxy") as paid:
                for ident in sorted(layer.VALID_PARTS):
                    with self.subTest(component=ident):
                        spec=layer.prepare(ident)
                        self.assertEqual(hashlib.sha256(spec["source"]).hexdigest(),
                                         spec["source_sha256"])
                        self.assertEqual(spec["dimensions"],(941,1672))
                        self.assertIn("imagem-mãe original",spec["prompt"].lower())
                        self.assertLess(len(spec["prompt"]),4400)
                paid.assert_not_called()

    def test_black_or_unknown_component_not_allowed(self):
        with self.assertRaisesRegex(VideoForgeError,"EP01_LAYER_UNKNOWN_COMPONENT"):
            layer.prepare("pose-ajoelhado")

    def test_existing_archive_skips_paid_generation(self):
        with patch.object(layer,"archived_layer",return_value={"sha256":"x"}):
            with patch.object(layer.proxy_images,"call_proxy") as paid:
                with self.assertRaisesRegex(VideoForgeError,"EP01_LAYER_ALREADY_ARCHIVED"):
                    layer.prepare("object-espada")
                paid.assert_not_called()

    def test_invalid_model_rejected_before_provider(self):
        with patch.object(layer.proxy_images,"call_proxy") as paid:
            with self.assertRaisesRegex(VideoForgeError,"EP01_LAYER_MODEL_NOT_ALLOWED"):
                layer.generate("object-bainha","http://127.0.0.1:18080","gpt-image-1.5")
            paid.assert_not_called()


if __name__=="__main__":
    unittest.main()
