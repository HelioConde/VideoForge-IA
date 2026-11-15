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


def _valid_png()->bytes:
    raw=(b"\x00"+b"\x55\x33\x22"*1024)*1536
    ihdr=struct.pack(">IIBBBBB",1024,1536,8,2,0,0,0)
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
