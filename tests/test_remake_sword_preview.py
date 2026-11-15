"""C01-P02 SHA/alpha/neutral QA, using only stdlib fixtures + FFmpeg.

Test-generated colored geometry is a TEST FIXTURE, never episode artwork.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zlib

from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import EPISODE
from videoforge.remake_sword_preview import (
    preflight,prepare,validate_package,SCHEMA,PARTS,CH,VID,SHOT,
)
ROOT=Path(__file__).resolve().parents[1]
W,H=1024,1536
FFMPEG_PRESENT=shutil.which("ffmpeg") is not None


def chunk(tag:bytes,blob:bytes)->bytes:
    return struct.pack(">I",len(blob))+tag+blob+struct.pack(">I",zlib.crc32(tag+blob)&0xffffffff)


def png_bytes(*,alpha:bool,base:tuple,rectangles:tuple=())->bytes:
    """Build canonical PNG scanlines with Python stdlib. NO Pillow installed."""
    channels=4 if alpha else 3
    kind=6 if alpha else 2
    encoder=zlib.compressobj(6)
    rows=[]
    for y in range(H):
        pixels=bytearray(bytes(base)*W)
        for x0,y0,x1,y1,color in rectangles:
            if y0<=y<y1:
                pixels[x0*channels:x1*channels]=bytes(color)*(x1-x0)
        rows.append(encoder.compress(b"\x00"+pixels))
    body=b"".join(rows)+encoder.flush()
    ihdr=struct.pack(">IIBBBBB",W,H,8,kind,0,0,0)
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",body)+chunk(b"IEND",b"")


RECTS={
    "sheath":(390,650,420,1090,(130,140,148)),
    "blade":(430,620,457,1020,(220,220,235)),
    "hand":(400,860,485,960,(137,89,76)),
}
COL=(12,13,14)


class SwordPreviewTests(unittest.TestCase):
    def test_current_preflight_fails_closed_without_any_image_generation(self):
        result=preflight()
        self.assertEqual(result["shot_id"],SHOT)
        self.assertEqual(result["global_frames"],[60,150])
        self.assertEqual(result["shot_duration_frames"],90)
        self.assertFalse(result["ready_for_render"])
        self.assertEqual(result["api_calls"],0)
        self.assertEqual(result["images_generated"],0)
        self.assertFalse(result["youtube_uploaded"])
        self.assertIn("ANCHOR",result["blocked_reason"])

    def test_missing_package_fails_before_proxy(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_ARTIFACT_REQUIRED"):
                validate_package(Path(temp)/"missing",12345)

    @unittest.skipUnless(FFMPEG_PRESENT,"FFmpeg required to decode PNG for positive test")
    def test_real_png_decode_qa_synthetic_fixture_and_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            package=self.fixture(root)
            stage=prepare(package,12345,root/"output",root/"public",root)
            self.assertEqual(stage["neutral_mae_rgb"],0)
            self.assertEqual(stage["qa_status"],"TECHNICAL_NEUTRAL_OK_HUMAN_REVIEW_PENDING")
            self.assertFalse(stage["human_visual_approved"])
            props=json.loads((root/"output/props.json").read_text(encoding="utf-8"))
            self.assertTrue(props["rig"]["technicalDraftOnly"])
            self.assertFalse(props["rig"]["humanVisualReview"])
            self.assertFalse(props["officialVideoApproved"])
            self.assertEqual(props["durationFrames"],90)
            self.assertEqual(set(props["rig"]["layers"]),set(PARTS))
            for part in PARTS:
                asset=root/"public"/(part+".png")
                self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),
                                 props["rig"]["layers"][part]["sha256"])
            with self.assertRaisesRegex(VideoForgeError,"PUBLIC_DIR_ALREADY_IN_USE"):
                prepare(package,12345,root/"output",root/"public",root)

    @unittest.skipUnless(FFMPEG_PRESENT,"FFmpeg required")
    def test_wrong_art_origin_or_tampered_layer_hash_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);package=self.fixture(root)
            with self.assertRaisesRegex(VideoForgeError,"BUNDLE_ORIGIN"):
                validate_package(package,99999,root)
            artifact=package/"scene-mother.production.json"
            saved=json.loads(artifact.read_text(encoding="utf-8"))
            artifact.write_text(json.dumps({**saved,"shot_id":"C01-P03"}),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"MOTHER_PROVENANCE_INVALID"):
                validate_package(package,12345,root)
            artifact.write_text(json.dumps(saved),encoding="utf-8")
            with (package/"hand.png").open("ab") as out:out.write(b"tamper")
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_SHA_MISMATCH:hand"):
                validate_package(package,12345,root)

    @unittest.skipUnless(FFMPEG_PRESENT,"FFmpeg required")
    def test_duplicate_layer_would_break_neutral_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);package=self.fixture(root)
            # Repaint a source-derived hand layer, rehash it, but leave mother
            # untouched. An attacker cannot fix inconsistency using only SHA.
            changed=png_bytes(alpha=True,base=(0,0,0,0),
                rectangles=((400,860,485,960,(255,1,1,255)),))
            (package/"hand.png").write_bytes(changed)
            bundle=package/"sword-bundle.json"
            data=json.loads(bundle.read_text())
            data["sha256"]["hand"]=hashlib.sha256(changed).hexdigest()
            bundle.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"NEUTRAL_RECOMPOSITION_FAILED"):
                validate_package(package,12345,root)

    def fixture(self,root:Path)->Path:
        """Only test fixture manipulates human_approved (in temp, never main)."""
        ep=root/EPISODE
        ep.mkdir(parents=True)
        for name in ("remake-ep01-planos.json","estado-atual.json","roteiro.json","autonomy-policy.json"):
            shutil.copyfile(ROOT/EPISODE/name,ep/name)
        anchor_dir=ep/"assets/geracoes/production-art-request/55555"
        anchor_dir.mkdir(parents=True)
        anchor_binary=png_bytes(alpha=False,base=COL)
        (anchor_dir/"character-bible.png").write_bytes(anchor_binary)
        anchor_sha=hashlib.sha256(anchor_binary).hexdigest()
        registry=ep/"remake-ep01-planos.json"
        data=json.loads(registry.read_text(encoding="utf-8"))
        data["identity_anchors"][0].update({
            "path":"assets/geracoes/production-art-request/55555/character-bible.png",
            "sha256":anchor_sha,"human_approved":True,"status":"approved"})
        registry.write_text(json.dumps(data),encoding="utf-8")
        package=root/"source"
        package.mkdir()
        (package/"underlay.png").write_bytes(png_bytes(alpha=False,base=COL))
        rectangles=[]
        for name in ("sheath","blade","hand"):
            x0,y0,x1,y1,rgb=RECTS[name]
            rectangles.append((x0,y0,x1,y1,rgb))
            binary=png_bytes(alpha=True,base=(0,0,0,0),
                rectangles=((x0,y0,x1,y1,rgb+(255,)),))
            (package/(name+".png")).write_bytes(binary)
        (package/"scene-mother.png").write_bytes(
            png_bytes(alpha=False,base=COL,rectangles=tuple(rectangles)))
        hashes={part:hashlib.sha256((package/(part+".png")).read_bytes()).hexdigest()
                for part in PARTS}
        hashes["scene-mother"]=hashlib.sha256((package/"scene-mother.png").read_bytes()).hexdigest()
        origin={
          "schema":"videoforge/production-scene/v1","channel":CH,"video_id":VID,
          "number":1,"scene":"C01","shot_id":SHOT,"shot_specific":True,
          "reference_sha256":anchor_sha,"sha256":hashes["scene-mother"],
          "technical_qa":"valid_png_opaque","youtube_uploaded":False,
        }
        (package/"scene-mother.production.json").write_text(json.dumps(origin),encoding="utf-8")
        bundle={
          "schema":SCHEMA,"channel":CH,"video_id":VID,"shot_id":SHOT,
          "source_run_id":12345,
          "source_artifact":"vf-remake-c01-p02-sword-source-12345",
          "anchor_sha256":anchor_sha,"sha256":hashes,
          "wristPivot":[427,930],
          "draw":{"beginFrame":7,"finishFrame":72,"travelPx":100,
                  "axisDeg":-10,"handFollow":.8,"handRotationDeg":2},
          "human_visual_approved":False,"official_video_approved":False,
          "youtube_uploaded":False,
        }
        (package/"sword-bundle.json").write_text(json.dumps(bundle),encoding="utf-8")
        return package


if __name__=="__main__":
    unittest.main()
