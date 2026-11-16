"""Prove the official V2 image workflow uses only approved SHA-backed archives."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zlib

from videoforge.remake_reference import prepare_remake_reference
from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import EPISODE

SOURCE=Path(__file__).resolve().parents[1]


def _chunk(tag:bytes,data:bytes)->bytes:
    return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)


def _valid_png(width:int=1024,height:int=1536)->bytes:
    raw=(b"\x00"+b"\x55\x33\x22"*width)*height
    ihdr=struct.pack(">IIBBBBB",width,height,8,2,0,0,0)
    return b"\x89PNG\r\n\x1a\n"+_chunk(b"IHDR",ihdr)+_chunk(b"IDAT",zlib.compress(raw,3))+_chunk(b"IEND",b"")


class RemakeReferenceTests(unittest.TestCase):
    def test_missing_or_unapproved_reference_blocks_without_proxy(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_CANONICAL_REFERENCE_NOT_APPROVED"):
                prepare_remake_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",Path(temp)/"input")

    def _fixture(self,root:Path)->tuple[Path,Path,str]:
        episode=root/EPISODE
        episode.mkdir(parents=True,exist_ok=True)
        for name in ("estado-atual.json","remake-ep01-planos.json","roteiro.json","autonomy-policy.json"):
            shutil.copyfile(SOURCE/EPISODE/name,episode/name)
        archive=episode/"assets/geracoes/production-art-request/67890"
        archive.mkdir(parents=True)
        binary=_valid_png()
        sha=hashlib.sha256(binary).hexdigest()
        (archive/"character-bible.png").write_bytes(binary)
        origin={"schema":"videoforge/production-art-result/v1","asset_id":"character-bible",
                "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
                "sha256":sha,"official_video_created":False}
        (archive/"character-bible.production.json").write_text(json.dumps(origin),encoding="utf-8")
        origin_manifest={
            "schema":"videoforge/permanent-generated-image-archive/v1",
            "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
            "producer":"production-art-request","github_run_id":67890,
            "images":[{"file":"character-bible.png","sha256":sha,"width":1024,"height":1536}]
        }
        (archive/"manifesto-geracoes.json").write_text(json.dumps(origin_manifest),encoding="utf-8")
        plan=json.loads((episode/"remake-ep01-planos.json").read_text(encoding="utf-8"))
        plan["identity_anchors"][0].update({
            "path":"assets/geracoes/production-art-request/67890/character-bible.png",
            "sha256":sha,"status":"approved","human_approved":True
        })
        (episode/"remake-ep01-planos.json").write_text(json.dumps(plan),encoding="utf-8")
        return episode,archive,sha

    def test_sha_verified_reference_and_provenance_are_copied(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            episode,archive,sha=self._fixture(root)
            destination=root/"input"
            result=prepare_remake_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                                            destination,root)
            self.assertEqual(result["sha256"],sha)
            self.assertTrue(result["human_approved"])
            self.assertEqual(result["image_generation_calls"],0)
            self.assertEqual(hashlib.sha256((destination/"character-bible.png").read_bytes()).hexdigest(),sha)

    def test_approved_grounded_reference_is_staged_without_resizing(self):
        from videoforge.grounded_identity import EXPECTED
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            episode,archive,_=self._fixture(root)
            name="character-bible-grounded"
            binary=_valid_png(1199,1312)
            digest=hashlib.sha256(binary).hexdigest()
            original=(archive/"character-bible.png")
            original.unlink()
            (archive/(name+".png")).write_bytes(binary)
            proof=[{"actor":actor,"id":sid,"path":rel,"sha256":sha}
                   for actor,(sid,rel,sha) in EXPECTED.items()]
            production={"schema":"videoforge/production-art-result/v1",
                        "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
                        "asset_id":name,"sha256":digest,"model":"gpt-image-2",
                        "source_images_attached_to_request":2,
                        "source_originals_sha_verified":proof,
                        "human_visual_approval":False,"official_video_created":False,
                        "youtube_uploaded":False}
            (archive/"character-bible.production.json").unlink()
            (archive/(name+".production.json")).write_text(json.dumps(production),encoding="utf-8")
            manifest=json.loads((archive/"manifesto-geracoes.json").read_text(encoding="utf-8"))
            manifest["images"]=[{"file":name+".png","sha256":digest,"width":1199,"height":1312}]
            (archive/"manifesto-geracoes.json").write_text(json.dumps(manifest),encoding="utf-8")
            plan_path=episode/"remake-ep01-planos.json"
            plan=json.loads(plan_path.read_text(encoding="utf-8"))
            plan["identity_anchors"][0].update({
                "path":"assets/geracoes/production-art-request/67890/"+name+".png",
                "sha256":digest,"status":"approved","human_approved":True,
            })
            plan_path.write_text(json.dumps(plan),encoding="utf-8")
            result=prepare_remake_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",root/"input",root)
            self.assertEqual(result["sha256"],digest)
            self.assertEqual(result["original_asset_id"],name)
            self.assertEqual(result["reference_source_dimensions"],[1199,1312])
            self.assertFalse(result["reference_pixels_resampled"])
            self.assertEqual((root/"input/character-bible.png").read_bytes(),binary)
            # Tampering with the original input provenance must block.
            production["source_originals_sha_verified"]=[]
            (archive/(name+".production.json")).write_text(json.dumps(production),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"GROUNDED_REVIEW_ORIGINAL_PROVENANCE_INVALID"):
                prepare_remake_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",root/"other",root)

    def test_missing_or_corrupt_origin_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            episode,archive,sha=self._fixture(root)
            path=archive/"manifesto-geracoes.json"
            path.unlink()
            with self.assertRaisesRegex(VideoForgeError,"REMAKE_REFERENCE_PROVENANCE_MISSING"):
                prepare_remake_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                                          root/"input",root)

    def test_wrong_origin_sha_fails_even_with_correct_png(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            episode,archive,sha=self._fixture(root)
            path=archive/"character-bible.production.json"
            result=json.loads(path.read_text(encoding="utf-8"))
            result["sha256"]="0"*64
            path.write_text(json.dumps(result),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"REMAKE_REFERENCE_PROVENANCE_MISMATCH"):
                prepare_remake_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                                          root/"input",root)


if __name__=="__main__":
    unittest.main()
