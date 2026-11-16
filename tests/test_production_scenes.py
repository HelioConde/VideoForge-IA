"""Scenarios for reference-anchored artwork requests without contacting IA."""
import unittest
import json
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from videoforge.production_scenes import reference_bytes
from tests.test_remake_reference import _valid_png

from videoforge.production_scenes import scene_prompt
from videoforge.errors import VideoForgeError


class ProductionScenesTests(unittest.TestCase):
    def test_all_16_scenes_use_the_same_character_bible(self):
        for number in range(1,17):
            prompt,scene=scene_prompt("otaku-br","spy-x-family-familia-de-mentira",number)
            self.assertLess(len(prompt),5001)
            self.assertIn("Anya",prompt)
            self.assertIn("Loid",prompt)
            self.assertIn("Yor",prompt)
            self.assertIn(scene["visual_direction"],prompt)
            self.assertEqual(scene["number"],number)

    def test_grounded_noncanonical_reference_requires_v2_approved_mode(self):
        from videoforge.grounded_identity import EXPECTED
        with TemporaryDirectory() as temp:
            base=Path(temp)
            source=base/"reference.png"
            raw=_valid_png(1199,1312)
            source.write_bytes(raw)
            metadata={"sha256":hashlib.sha256(raw).hexdigest(),
                      "asset_id":"character-bible-grounded",
                      "official_video_created":False,
                      "source_images_attached_to_request":2,
                      "source_originals_sha_verified":[
                          {"actor":actor,"id":sid,"path":path,"sha256":sha}
                          for actor,(sid,path,sha) in EXPECTED.items()],
            }
            report=base/"reference.production.json"
            report.write_text(json.dumps(metadata),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"REFERENCE_SHA_MISMATCH"):
                reference_bytes(source,report)
            saved,digest=reference_bytes(source,report,allow_grounded=True)
            self.assertEqual(saved,raw)
            self.assertEqual(digest,metadata["sha256"])
            metadata["source_images_attached_to_request"]=0
            report.write_text(json.dumps(metadata),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"GROUNDED_INPUT_PROOF_MISSING"):
                reference_bytes(source,report,allow_grounded=True)

    def test_scene_id_out_of_range_is_refused(self):
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_SCENE_NUMBER_INVALID"):
            scene_prompt("otaku-br","spy-x-family-familia-de-mentira",0)
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_SCENE_NUMBER_INVALID"):
            scene_prompt("otaku-br","spy-x-family-familia-de-mentira",17)

    def test_other_channel_does_not_get_spy_bible(self):
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_ART_PLAN_MISSING"):
            scene_prompt("gamer","spy-x-family-familia-de-mentira",1)


if __name__=="__main__":
    unittest.main()
