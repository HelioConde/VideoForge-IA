"""Regressões: novas lanças precisam tocar as mãos em edição ancorada."""
import base64
import copy
import unittest
from videoforge.production_art import read_plan,asset_prompt
from videoforge.dorama_grip_correction import ASSET,edit_payload,batch_hold,block_batch
from videoforge.dorama_continuity import reference
from videoforge.errors import VideoForgeError

class PhysicalGripTests(unittest.TestCase):
    def setUp(self):
        self.plan,self.story=read_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
        self.asset=next(x for x in self.plan["assets"] if x["id"]==ASSET)
        self.prompt,self.size=asset_prompt(self.plan,self.story,ASSET)
    def test_old_pose_is_explicitly_held(self):
        hold=batch_hold()
        self.assertTrue(hold["active"])
        self.assertFalse(hold["corrected_anchor_promoted"])
        with self.assertRaisesRegex(VideoForgeError,"NEW_SHOTS_PAUSED"):
            block_batch()
    def test_edit_uses_original_sha_exactly(self):
        anchor,raw=reference()
        payload,provenance=edit_payload(self.asset,self.prompt,"gpt-image-2",self.size)
        supplied=base64.b64decode(payload["images"][0]["image_url"].split(",",1)[1])
        self.assertEqual(supplied,raw)
        self.assertEqual(provenance[0]["sha256"],anchor["sha256"])
        self.assertFalse(provenance[0]["source_spear_grip_approved"])
        self.assertIn("SEGURAM",self.prompt)
        self.assertIn("MÃOS",self.prompt.upper())
    def test_reference_tampering_fails_before_generation(self):
        mod=copy.deepcopy(self.asset)
        mod["required_source_sha256"]="0"*64
        with self.assertRaisesRegex(VideoForgeError,"SOURCE_SHA_OR_MODEL_MISMATCH"):
            edit_payload(mod,self.prompt,"gpt-image-2",self.size)
    def test_no_automatic_approval(self):
        mod=copy.deepcopy(self.asset)
        mod["visual_approval"]=True
        with self.assertRaisesRegex(VideoForgeError,"CONTRACT_INVALID"):
            edit_payload(mod,self.prompt,"gpt-image-2",self.size)

if __name__=="__main__":
    unittest.main()
