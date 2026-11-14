"""Regressão: nenhum fluxo de IA pode gerar imagem para Alchemy Lab EP01.

Os testes não chamam rede, proxy, imagem generativa, nem criam PNG.
"""
from __future__ import annotations
from pathlib import Path
import unittest
from unittest.mock import patch

from videoforge.errors import VideoForgeError
from videoforge.image_generation_policy import assert_image_generation_allowed
from videoforge import (
    production_art,
    production_scenes,
    production_scene_layers,
    production_layer_recovery,
    production_rgba_parts,
    proxy_images,
    scene_layers,
)

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"
MISSING=Path("/does-not-exist/do-not-open.png")

class ImageGenerationBanTests(unittest.TestCase):
    def test_direct_policy_blocks_exact_episode(self):
        with self.assertRaisesRegex(VideoForgeError,"IMAGE_GENERATION_DENIED_ALCHEMY_EP01"):
            assert_image_generation_allowed(CHANNEL,VIDEO)

    def test_other_channels_and_videos_are_not_affected(self):
        for channel,video in [
            ("otaku-multicena",VIDEO),
            (CHANNEL,"outro-episodio"),
            ("otaku-multicena","outro-episodio"),
        ]:
            with self.subTest(channel=channel,video=video):
                self.assertIsNone(assert_image_generation_allowed(channel,video))

    def test_direct_proxy_and_layer_generation_are_also_blocked(self):
        with patch.object(proxy_images,"call_proxy",side_effect=AssertionError("PROXY_MUST_NOT_RUN")) as proxy:
            with self.assertRaisesRegex(proxy_images.ProxyImageError,"IMAGE_GENERATION_DENIED_ALCHEMY_EP01"):
                proxy_images.generate(
                    "https://invalid.invalid","no-secret",CHANNEL,VIDEO,
                    "cena-01","gpt-image-2","1024x1536","never send this")
            with patch.object(scene_layers,"_read_manifest",
                              return_value={"channel":CHANNEL,"video_id":VIDEO,"layers":{}}):
                with self.assertRaisesRegex(scene_layers.LayerError,"IMAGE_GENERATION_DENIED_ALCHEMY_EP01"):
                    scene_layers.generate_layer(
                        MISSING.parent,"background","https://invalid.invalid",
                        "no-secret","gpt-image-2")
            proxy.assert_not_called()

    def test_every_generation_entrypoint_blocks_before_any_input_or_proxy(self):
        actions=[
            lambda: production_art.create_image(CHANNEL,VIDEO,"character-bible","https://invalid.invalid"),
            lambda: production_scenes.generate_scene(CHANNEL,VIDEO,1,MISSING,MISSING,"https://invalid.invalid"),
            lambda: production_scene_layers.generate(CHANNEL,VIDEO,1,MISSING,MISSING,"https://invalid.invalid","gpt-image-2"),
            lambda: production_layer_recovery.recover(CHANNEL,VIDEO,1,MISSING,MISSING,"https://invalid.invalid"),
            lambda: production_rgba_parts.make_part(CHANNEL,VIDEO,1,"kael",MISSING,MISSING,"https://invalid.invalid"),
        ]
        with patch.object(proxy_images,"generate",side_effect=AssertionError("PROXY_MUST_NOT_RUN")) as g, \
             patch.object(proxy_images,"call_proxy",side_effect=AssertionError("PROXY_MUST_NOT_RUN")) as p:
            for i,action in enumerate(actions):
                with self.subTest(entrypoint=i):
                    with self.assertRaisesRegex(VideoForgeError,"IMAGE_GENERATION_DENIED_ALCHEMY_EP01"):
                        action()
            g.assert_not_called()
            p.assert_not_called()

if __name__=="__main__":
    unittest.main()
