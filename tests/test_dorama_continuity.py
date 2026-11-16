"""Regressões de referência visual APROVADA ao gerar próximos planos."""
import base64
import copy
import unittest
from pathlib import Path
from videoforge import production_art
from videoforge.dorama_continuity import reference,edit_payload,MODE
from videoforge.errors import VideoForgeError
ASSET="c01-p05-guardas-lancas-v1"
class ContinuityTests(unittest.TestCase):
    def test_approved_anchor_is_exact_permanent_png(self):
        anchor,source=reference()
        self.assertEqual(anchor["source_shot_id"],"C01-P04")
        self.assertEqual(anchor["sha256"],"605ccd361ad9a867eb8b92948010fdbb7d87a031d8b3601c663d815917b1b6cc")
        self.assertEqual(source[:8],bytes((137,80,78,71,13,10,26,10)))
        self.assertEqual((anchor["width"],anchor["height"]),(941,1672))
        self.assertTrue(anchor["approved_for_future_image_reference"])
    def test_next_real_shot_uses_image_edit_payload_not_text_only(self):
        plan,story=production_art.read_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
        asset=next(a for a in plan["assets"] if a["id"]==ASSET)
        self.assertEqual(asset["source_mode"],MODE)
        prompt,size=production_art.asset_prompt(plan,story,ASSET)
        payload,provenance=edit_payload(asset,prompt,"gpt-image-2",size)
        original=base64.b64decode(payload["images"][0]["image_url"].split(",",1)[1])
        anchor,known=reference()
        self.assertEqual(original,known)
        self.assertEqual(len(payload["images"]),1)
        self.assertEqual(provenance[0]["sha256"],anchor["sha256"])
        self.assertIn("C01-P05",prompt)
        self.assertIn("não",prompt.lower())
    def test_wrong_sha_refused_before_provider(self):
        plan,story=production_art.read_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
        asset=copy.deepcopy(next(a for a in plan["assets"] if a["id"]==ASSET))
        asset["required_source_sha256"]="0"*64
        prompt,size=production_art.asset_prompt(plan,story,ASSET)
        with self.assertRaisesRegex(VideoForgeError,"CONTINUITY_REQUEST_MISMATCH"):
            edit_payload(asset,prompt,"gpt-image-2",size)
    def test_wrong_cast_or_unknown_shot_blocked(self):
        plan,story=production_art.read_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
        asset=copy.deepcopy(next(a for a in plan["assets"] if a["id"]==ASSET))
        prompt,size=production_art.asset_prompt(plan,story,ASSET)
        asset["identity_cast"]=["elara"]
        with self.assertRaisesRegex(VideoForgeError,"CONTINUITY_REQUEST_CAST_MISMATCH"):
            edit_payload(asset,prompt,"gpt-image-2",size)
        asset["identity_cast"]=["guarda_esquerdo","guarda_direito"]
        asset["shot_id"]="C04-P99"
        with self.assertRaisesRegex(VideoForgeError,"CONTINUITY_SHOT_NOT_DISTINCT"):
            edit_payload(asset,prompt,"gpt-image-2",size)
    def test_original_rejected_reference_not_reapproved(self):
        anchor,_=reference()
        self.assertTrue(anchor["limitations"]["old_rejected_reference_is_not_resurrected"])
        self.assertTrue(anchor["limitations"]["not_an_approved_R2_or_MP4"])
if __name__=="__main__":
    unittest.main()
