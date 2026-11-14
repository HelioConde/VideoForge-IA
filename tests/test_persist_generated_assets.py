"""Archiver tests use only tiny synthetic PNG bytes in temp directories.

No image generation, external APIs, GitHub writes or approvals.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from videoforge.persist_generated_assets import archive
from videoforge.errors import VideoForgeError

def png(rgb=(1,2,3))->bytes:
    def chunk(kind,data):
        return (struct.pack(">I",len(data))+kind+data+
                struct.pack(">I",zlib.crc32(kind+data)&0xffffffff))
    return (b"\x89PNG\r\n\x1a\n"+
            chunk(b"IHDR",struct.pack(">IIBBBBB",1,1,8,2,0,0,0))+
            chunk(b"tEXt",b"test-fixture\x00"+b"x"*82)+
            chunk(b"IDAT",zlib.compress(b"\x00"+bytes(rgb)))+
            chunk(b"IEND",b""))

class PermanentGeneratedImageArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.ch="alchemy-lab"
        self.vid="mmorpg-conquiste-a-princesa-ep01"
        self.inrel=f"output/{self.ch}/videos/{self.vid}/imagens"
        self.source=self.root/self.inrel
        self.source.mkdir(parents=True)
        self.png=png()
        (self.source/"quadro.png").write_bytes(self.png)
        self.dest=(self.root/"canal"/self.ch/"videos"/self.vid/"assets"/
                   "geracoes"/"production-art"/"1234")

    def run_archive(self):
        return archive(self.ch,self.vid,self.inrel,1234,"production-art",self.root)

    def test_first_archive_is_persistent_and_exact_sha(self):
        d=self.run_archive()
        self.assertEqual(d["archived_image_count"],1)
        self.assertFalse(d["production_approved"])
        self.assertFalse(d["generated_in_this_archiver"])
        self.assertFalse(d["youtube_uploaded"])
        self.assertEqual((self.dest/"quadro.png").read_bytes(),self.png)
        sha=hashlib.sha256(self.png).hexdigest()
        self.assertEqual(d["images"][0]["sha256"],sha)
        self.assertEqual(json.loads((self.dest/"manifesto-geracoes.json").read_text())
                         ["images"][0]["sha256"],sha)

    def test_rerun_is_idempotent_and_cannot_overwrite_original(self):
        a=self.run_archive()
        b=self.run_archive()
        self.assertEqual(a,b)
        first=(self.dest/"quadro.png").read_bytes()
        (self.source/"quadro.png").write_bytes(png((8,9,10)))
        with self.assertRaisesRegex(VideoForgeError,"WOULD_OVERWRITE_EXISTING"):
            self.run_archive()
        self.assertEqual((self.dest/"quadro.png").read_bytes(),first)

    def test_wrong_channel_or_path_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"WRONG_CHANNEL_OR_VIDEO"):
            archive("alchemy-lab","other-video",self.inrel,1234,
                    "production-art",self.root)
        with self.assertRaisesRegex(VideoForgeError,"SOURCE_PATH_UNSAFE"):
            archive(self.ch,self.vid,"../output/wrong",1234,
                    "production-art",self.root)

    def test_no_png_cannot_silently_report_success(self):
        (self.source/"quadro.png").unlink()
        with self.assertRaisesRegex(VideoForgeError,"NO_PNG_TO_PERSIST"):
            self.run_archive()
        self.assertFalse(self.dest.exists())

    def test_matching_production_sha_is_checked(self):
        p=self.source/"quadro.production.json"
        good={
            "schema":"videoforge/production-art-result/v1",
            "sha256":hashlib.sha256(self.png).hexdigest(),
            "human_visual_approval":False,
        }
        p.write_text(json.dumps(good),encoding="utf8")
        self.run_archive()
        self.assertEqual((self.dest/p.name).read_bytes(),p.read_bytes())

    def test_wrong_production_sha_blocks_without_writes(self):
        p=self.source/"quadro.production.json"
        p.write_text(json.dumps({"sha256":"0"*64}),encoding="utf8")
        with self.assertRaisesRegex(VideoForgeError,"PRODUCTION_SHA_MISMATCH"):
            self.run_archive()
        self.assertFalse(self.dest.exists())

    def test_secret_key_is_not_committed(self):
        (self.source/"quadro.meta.json").write_text(
            json.dumps({"api_key":"should-never-be-in-the-repo"}),encoding="utf8")
        with self.assertRaisesRegex(VideoForgeError,"SENSITIVE_METADATA_REFUSED"):
            self.run_archive()
        self.assertFalse(self.dest.exists())

    def test_reject_non_png_or_symlink(self):
        (self.source/"quadro.png").write_bytes(b"JPEG not PNG")
        with self.assertRaisesRegex(VideoForgeError,"PNG_INVALID"):
            self.run_archive()
        (self.source/"quadro.png").write_bytes(self.png)
        (self.source/"outside.png").symlink_to(self.source/"quadro.png")
        with self.assertRaisesRegex(VideoForgeError,"SOURCE_SYMLINK"):
            self.run_archive()
        self.assertFalse(self.dest.exists())

    def test_next_run_or_producer_will_not_change_earlier_files(self):
        self.run_archive()
        orig=(self.dest/"quadro.png").read_bytes()
        again=archive(self.ch,self.vid,self.inrel,5678,
                      "production-scenes",self.root)
        self.assertEqual(again["github_run_id"],5678)
        self.assertEqual((self.dest/"quadro.png").read_bytes(),orig)
        self.assertTrue((self.root/"canal"/self.ch/"videos"/self.vid/
                         "assets/geracoes/production-scenes/5678/quadro.png").is_file())

if __name__=="__main__":
    unittest.main()
