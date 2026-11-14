"""Synthetic fixtures only: never constitute an approved channel rig."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from videoforge.rig_three_contract import validate_rig_folder,ThreeRigError


def test_png(color:int)->bytes:
    def chunk(tag:bytes,payload:bytes)->bytes:
        return struct.pack(">I",len(payload))+tag+payload+struct.pack(">I",zlib.crc32(tag+payload)&0xffffffff)
    w=h=64
    rows=[]
    for y in range(h):
        row=bytearray()
        for x in range(w):
            a=255 if 8<=x<56 and 8<=y<56 else 0
            row.extend((color,30,40,a))
        rows.append(b"\0"+row)
    return (b"\x89PNG\r\n\x1a\n"+
        chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+
        chunk(b"IDAT",zlib.compress(b"".join(rows)))+chunk(b"IEND",b""))


def make_fixture(folder:Path):
    names=["body-no-head","head-open","head-closed","hair-front"]
    layers=[]
    for i,name in enumerate(names):
        raw=test_png(55+i*35)
        file=name+".png"
        (folder/file).write_bytes(raw)
        layer={"id":name,"file":file,"sha256":hashlib.sha256(raw).hexdigest(),
               "bbox":[0,0,64,64],"z":i+1}
        if name=="hair-front":
            layer["mesh"]={"columns":7,"rows":9,"pinnedRows":[0],"amplitudePx":4}
        layers.append(layer)
    result={
        "schema":"videoforge/rig-three/v1","channel":"otaku-br","video_id":"fixture",
        "scene":"cena-01","sceneMotherSha256":"a"*64,
        "canvas":{"width":64,"height":64},"neckPivot":[32,32],
        "headMaxRotationDeg":2,"blinkFrames":[30,90],
        "eyeEditQa":{"nonEyePixelsChanged":0,"alphaPixelsChanged":0},
        "humanReview":{"partsReconstructed":True,"noDuplicatedPixels":True,
          "roundTripComposition":True,"hairAndFaceOcclusion":True,
          "seamsAndPivot":True},
        "layers":layers,
    }
    (folder/"rig.json").write_text(json.dumps(result),encoding="utf-8")
    return result


class ThreeRigContractTests(unittest.TestCase):
    def check(self,folder:Path):
        return validate_rig_folder(folder,channel="otaku-br",video_id="fixture",
             scene="cena-01",scene_mother_sha256="a"*64,frames=120)

    def test_fixture_only_verified_asset_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            make_fixture(folder)
            result=self.check(folder)
            self.assertEqual(result["rigType"],"independent-parts-and-deformable-mesh")
            self.assertEqual(result["layers"][-1]["mesh"]["pinnedRows"],[0])
            self.assertEqual(result["neckPivot"],[32.,32.])
            self.assertFalse(result["youtubeUploaded"])

    def test_no_automatic_human_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            doc=make_fixture(folder)
            doc["humanReview"]["noDuplicatedPixels"]=False
            (folder/"rig.json").write_text(json.dumps(doc),encoding="utf-8")
            with self.assertRaisesRegex(ThreeRigError,"HUMAN_REVIEW_REQUIRED"):
                self.check(folder)

    def test_no_fake_character_png_or_duplicate_body_head(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            doc=make_fixture(folder)
            doc["layers"][1]["file"]=doc["layers"][0]["file"]
            (folder/"rig.json").write_text(json.dumps(doc),encoding="utf-8")
            with self.assertRaisesRegex(ThreeRigError,"FILE_UNSAFE_OR_DUPLICATED"):
                self.check(folder)

    def test_rejects_wrong_provenance_and_missing_sprite(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            doc=make_fixture(folder)
            with self.assertRaisesRegex(ThreeRigError,"PROVENANCE_INVALID"):
                validate_rig_folder(folder,channel="gamer",video_id="fixture",
                  scene="cena-01",scene_mother_sha256="a"*64,frames=120)
            (folder/"head-closed.png").unlink()
            with self.assertRaisesRegex(ThreeRigError,"ASSET_MISSING"):
                self.check(folder)

    def test_two_independent_hair_meshes_accepted_but_review_gate_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            doc=make_fixture(folder)
            doc["layers"][-1]["id"]="hair-front-left"
            raw=test_png(124)
            (folder/"hair-front-right.png").write_bytes(raw)
            doc["layers"].append({
                "id":"hair-front-right","file":"hair-front-right.png",
                "sha256":hashlib.sha256(raw).hexdigest(),
                "bbox":[0,0,64,64],"z":5,
                "mesh":{"columns":7,"rows":9,"pinnedRows":[0],"amplitudePx":4}
            })
            (folder/"rig.json").write_text(json.dumps(doc),encoding="utf-8")
            result=self.check(folder)
            self.assertEqual({x["id"] for x in result["layers"] if x.get("mesh")},
                             {"hair-front-left","hair-front-right"})
            doc["humanReview"]["hairAndFaceOcclusion"]=False
            (folder/"rig.json").write_text(json.dumps(doc),encoding="utf-8")
            with self.assertRaisesRegex(ThreeRigError,"HUMAN_REVIEW_REQUIRED"):
                self.check(folder)

    def test_mesh_pinned_and_source_hash_required(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            doc=make_fixture(folder)
            doc["layers"][-1]["mesh"]["pinnedRows"]=[1]
            (folder/"rig.json").write_text(json.dumps(doc),encoding="utf-8")
            with self.assertRaisesRegex(ThreeRigError,"MESH_MUST_PIN_ROOT"):
                self.check(folder)
            doc["layers"][-1]["mesh"]["pinnedRows"]=[0]
            (folder/"rig.json").write_text(json.dumps(doc),encoding="utf-8")
            with self.assertRaisesRegex(ThreeRigError,"PROVENANCE_INVALID"):
                validate_rig_folder(folder,channel="otaku-br",video_id="fixture",
                  scene="cena-01",scene_mother_sha256="b"*64,frames=120)


if __name__=="__main__":
    unittest.main()
