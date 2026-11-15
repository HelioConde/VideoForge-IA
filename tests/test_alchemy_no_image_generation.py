"""Regressão: autorização permanente ativa e bloqueio de provedor revogado.

Todos os testes que verificam negativas simulam POLÍTICA NEGADA no processo,
sem alterar o arquivo real e sem usar rede, proxy ou imagens generativas.
"""
from __future__ import annotations
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch

from videoforge.errors import VideoForgeError
from videoforge.image_generation_policy import assert_image_generation_allowed
from videoforge.remake_autopilot import EPISODE
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
    def test_current_policy_allows_authorized_episode(self):
        self.assertIsNone(assert_image_generation_allowed(CHANNEL,VIDEO))

    def test_disabled_policy_still_blocks_in_an_isolated_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            base=root/EPISODE
            base.mkdir(parents=True)
            repo=Path(__file__).resolve().parents[1]/EPISODE
            for filename in ("estado-atual.json","autonomy-policy.json"):
                shutil.copyfile(repo/filename,base/filename)
            policy=json.loads((base/"autonomy-policy.json").read_text(encoding="utf-8"))
            policy["paid_provider_calls_approved"]=False
            policy["max_chargeable_calls_per_run"]=0
            (base/"autonomy-policy.json").write_text(json.dumps(policy),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"provider cost permission required"):
                assert_image_generation_allowed(CHANNEL,VIDEO,root)

    def test_other_channels_and_videos_are_not_affected(self):
        for channel,video in [
            ("otaku-multicena",VIDEO),
            (CHANNEL,"outro-episodio"),
            ("otaku-multicena","outro-episodio"),
        ]:
            with self.subTest(channel=channel,video=video):
                self.assertIsNone(assert_image_generation_allowed(channel,video))

    def test_direct_proxy_and_layer_generation_are_also_blocked(self):
        blocked=VideoForgeError("IMAGE_GENERATION_DENIED_ALCHEMY_EP01: synthetic denied-policy fixture")
        with patch("videoforge.image_generation_policy.assert_image_generation_allowed",side_effect=blocked), \
             patch.object(proxy_images,"call_proxy",side_effect=AssertionError("PROXY_MUST_NOT_RUN")) as proxy:
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
        blocked=VideoForgeError("IMAGE_GENERATION_DENIED_ALCHEMY_EP01: synthetic denied-policy fixture")
        with patch("videoforge.image_generation_policy.assert_image_generation_allowed",side_effect=blocked), \
             patch.object(proxy_images,"generate",side_effect=AssertionError("PROXY_MUST_NOT_RUN")) as g, \
             patch.object(proxy_images,"call_proxy",side_effect=AssertionError("PROXY_MUST_NOT_RUN")) as p:
            for i,action in enumerate(actions):
                with self.subTest(entrypoint=i):
                    with self.assertRaisesRegex(VideoForgeError,"IMAGE_GENERATION_DENIED_ALCHEMY_EP01"):
                        action()
            g.assert_not_called()
            p.assert_not_called()

if __name__=="__main__":
    unittest.main()
