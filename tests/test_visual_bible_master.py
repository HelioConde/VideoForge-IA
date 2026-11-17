"""Base limpa do palácio tem fonte real e não aprova lanças defeituosas."""
import base64
import unittest
from videoforge.production_art import read_plan, asset_prompt
from videoforge.visual_bible_master import edit_payload, MODE, STYLE_SHA
from videoforge.dorama_continuity import reference
from videoforge.errors import VideoForgeError


class VisualBibleMasterTests(unittest.TestCase):
    def test_throne_room_empty_master_preserves_only_style_source(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = next(x for x in plan["assets"] if x["id"] == "biblia-sala-do-trono-vazio-v1")
        prompt, size = asset_prompt(plan, story, asset["id"])
        payload, provenance = edit_payload(asset, prompt, "gpt-image-2", size)
        anchor, raw = reference()
        self.assertEqual(base64.b64decode(payload["images"][0]["image_url"].split(",", 1)[1]), raw)
        self.assertEqual(len(payload["images"]), 1)
        self.assertEqual(provenance[0]["sha256"], STYLE_SHA)
        self.assertTrue(provenance[0]["source_spear_pose_rejected"])
        self.assertEqual(asset["biblia_item_id"], "sala-do-trono")
        self.assertEqual(asset["biblia_categoria"], "cenarios")
        self.assertIn("SEM PESSOAS", prompt.upper())
        self.assertIn("SEM LANÇAS", prompt.upper())
        self.assertFalse(asset["youtube_upload"])
    def test_fake_reference_blocks_before_provider(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = dict(next(x for x in plan["assets"] if x["id"] == "biblia-sala-do-trono-vazio-v1"))
        asset["required_source_sha256"] = "0" * 64
        prompt, size = asset_prompt(plan, story, asset["id"])
        with self.assertRaisesRegex(VideoForgeError, "STYLE_SHA_MISMATCH"):
            edit_payload(asset, prompt, "gpt-image-2", size)


if __name__ == "__main__":
    unittest.main()
