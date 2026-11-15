"""No-cost regression tests for C01-P02 one-image, source-aware producer.

Every source image used here is a temporary *synthetic test fixture*; mock
network before positive calls. Never write fake assets into canal/.../main.
"""
from __future__ import annotations
import base64
import hashlib
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videoforge.errors import VideoForgeError
from videoforge.image_generation_policy import assert_image_generation_allowed
from videoforge.remake_autopilot import EPISODE
from videoforge.remake_sword_source import (
    preflight,produce,source_info,PROMPTS,CH,VID,SHOT,
)
from videoforge.persist_generated_assets import archive
from videoforge.remake_sword_pack import _find_part
from tests import test_remake_sword_pack as pack_fixtures

class SwordSourceTests(unittest.TestCase):
    def test_policy_denies_paid_calls_without_proxy_in_isolated_fixture(self):
        # Never assume the real main checkout will remain cost-blocked forever.
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            self.setup_approved_temp_source(root)
            ep=root/EPISODE
            path=ep/"autonomy-policy.json"
            policy=json.loads(path.read_text(encoding="utf-8"))
            policy["paid_provider_calls_approved"]=False
            policy["max_chargeable_calls_per_run"]=0
            path.write_text(json.dumps(policy),encoding="utf-8")
            with patch("videoforge.remake_sword_source.proxy_images.call_proxy") as call:
                checked=preflight("blade",501,root)
                self.assertFalse(checked["ready"])
                self.assertIn("provider cost permission required",
                              checked["blocked_reason"])
                with self.assertRaisesRegex(VideoForgeError,"provider cost permission required"):
                    produce("blade",501,"https://proxy.example",root=root)
                call.assert_not_called()

    def test_strict_one_image_prompts_by_source_part(self):
        self.assertEqual(set(PROMPTS),{"underlay","sheath","blade","hand"})
        for part,prompt in PROMPTS.items():
            self.assertIn("C01-P02",prompt)
            self.assertGreaterEqual(len(prompt),150)
            self.assertLess(len(prompt),2800)
        self.assertIn("CARRASCO",PROMPTS["hand"])
        self.assertIn("OPACO",PROMPTS["underlay"])

    def setup_approved_temp_source(self,root:Path,*,keep_components:bool=False)->dict:
        sources=pack_fixtures.RemakeSwordPackTests().create_test_archive(root)
        # For edit tests the mother exists but none of its parts were generated.
        # Only the duplication test keeps archived, valid components.
        if not keep_components:
            for folder in sources["parts"].values():
                shutil.rmtree(folder)
        ep=root/EPISODE
        policy_path=ep/"autonomy-policy.json"
        policy=json.loads(policy_path.read_text(encoding="utf-8"))
        policy["paid_provider_calls_approved"]=True
        policy["max_chargeable_calls_per_run"]=1
        policy_path.write_text(json.dumps(policy),encoding="utf-8")
        assert_image_generation_allowed(CH,VID,root)
        return sources

    def test_source_context_rejects_wrong_scene_run_after_cost_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.setup_approved_temp_source(root)
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_RUN_ID_NOT_CURRENT"):
                source_info(root,502)
            with patch("videoforge.remake_sword_source.proxy_images.call_proxy") as call:
                with self.assertRaisesRegex(VideoForgeError,"SOURCE_RUN_ID_NOT_CURRENT"):
                    produce("blade",502,"https://proxy.example",root=root)
                call.assert_not_called()

    def test_hand_real_rgba_data_one_call_and_permanent_archive_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            sources=self.setup_approved_temp_source(root)
            image=(sources["source"]/"hand.png").read_bytes()
            mock_response={"data":[{"b64_json":base64.b64encode(image).decode("ascii")}]}
            with patch("videoforge.remake_sword_source.proxy_images.call_proxy",
                       return_value=mock_response) as call:
                result=produce("hand",501,"https://proxy.example",root=root)
            call.assert_called_once()
            kwargs=call.call_args.args[3]
            self.assertEqual(kwargs["background"],"transparent")
            self.assertEqual(len(kwargs["images"]),1)
            self.assertEqual(result["shot_id"],SHOT)
            self.assertEqual(result["source_archive_run_id"],501)
            self.assertEqual(result["technical_status"],"candidate_rgba_verified")
            self.assertFalse(result["human_visual_approval"])
            self.assertFalse(result["youtube_uploaded"])
            self.assertEqual(result["api_edit_calls_executed"],1)
            folder="output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/sword-components/c01-p02/hand"
            archived=archive(CH,VID,folder,777,"production-rgba-request",root)
            self.assertEqual(archived["archived_image_count"],1)
            self.assertEqual(archived["producer"],"production-rgba-request")
            entry=_find_part(root/EPISODE,"hand",result["scene_mother_sha256"])
            self.assertIsNotNone(entry)
            self.assertEqual(entry["run_id"],777)
            with patch("videoforge.remake_sword_source.proxy_images.call_proxy") as second:
                with self.assertRaisesRegex(VideoForgeError,"ALREADY_ARCHIVED_SAME_MOTHER"):
                    produce("hand",501,"https://proxy.example",root=root)
                second.assert_not_called()

    def test_deny_paid_duplicate_from_a_fresh_runner_with_valid_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.setup_approved_temp_source(root,keep_components=True)
            checked=preflight("hand",501,root)
            self.assertFalse(checked["ready"])
            self.assertIn("REMAKE_SWORD_COMPONENT_ALREADY_ARCHIVED_SAME_MOTHER",
                          checked["blocked_reason"])
            with patch("videoforge.remake_sword_source.proxy_images.call_proxy") as call:
                with self.assertRaisesRegex(VideoForgeError,
                                           "REMAKE_SWORD_COMPONENT_ALREADY_ARCHIVED_SAME_MOTHER"):
                    produce("hand",501,"https://proxy.example",root=root)
                call.assert_not_called()

    def test_underlay_opaque_png_producer_metadata_and_shas(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            sources=self.setup_approved_temp_source(root)
            image=(sources["source"]/"underlay.png").read_bytes()
            with patch("videoforge.remake_sword_source.proxy_images.call_proxy",
                       return_value={"data":[{"b64_json":base64.b64encode(image).decode()}]}) as call:
                result=produce("underlay",501,"https://proxy.example",root=root)
            self.assertEqual(call.call_count,1)
            self.assertEqual(call.call_args.args[3]["background"],"opaque")
            self.assertEqual(result["technical_status"],"candidate_opaque_verified")
            self.assertEqual(result["schema"],"videoforge/remake-underlay-candidate/v1")
            folder="output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/sword-components/c01-p02/underlay"
            ar=archive(CH,VID,folder,778,"production-sword-underlay-request",root)
            self.assertEqual(ar["archived_image_count"],1)
            src=_find_part(root/EPISODE,"underlay",result["scene_mother_sha256"])
            self.assertIsNotNone(src)
            self.assertEqual(src["run_id"],778)

    def test_invalid_alpha_is_preserved_for_review_but_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            sources=self.setup_approved_temp_source(root)
            rgb=(sources["source"]/"underlay.png").read_bytes()
            with patch("videoforge.remake_sword_source.proxy_images.call_proxy",
                       return_value={"data":[{"b64_json":base64.b64encode(rgb).decode()}]}):
                result=produce("hand",501,"https://proxy.example",root=root)
            self.assertEqual(result["technical_status"],"rejected_png_or_alpha_invalid")
            self.assertFalse(result["human_visual_approval"])
            target=root/"output"/CH/"videos"/VID/"sword-components/c01-p02/hand/hand.png"
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                             result["output_sha256"])

if __name__=="__main__":
    unittest.main()
