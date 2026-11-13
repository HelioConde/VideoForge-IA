"""Regressao de preparo de sprite candidato (apenas stdlib + FFmpeg do runner)."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videoforge import mesh_rig, proxy_images, rig_candidate as r, scene_layers


class CandidateRigTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        cfg=self.root/"canal/otaku-br/canal.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text('{"id":"otaku-br"}')
        patched=patch.object(proxy_images,"ROOT",self.root)
        patched.start()
        self.addCleanup(patched.stop)
        self.source=self.root/"source"
        self.source.mkdir()
        self.width,self.height=64,96
        self.video_id="teste-001"
        self.scene="cena-01"
        source_hashes={}
        for name in r.REQUIRED:
            img=bytearray(self.width*self.height*4)
            for y in range(self.height):
                for x in range(self.width):
                    idx=4*(y*self.width+x)
                    is_bg=name in ("background.png","cena-base.png")
                    if is_bg:
                        alpha=255
                    elif name=="character-main.png":
                        alpha=255 if 8<x<54 and 7<y<89 else 0
                    elif name=="cape.png":
                        alpha=255 if 8<x<35 and 28<y<80 else 0
                    else:
                        alpha=255 if y>82 else 0
                    img[idx:idx+4]=bytes((180 if name=="cape.png" else 95,55,90,alpha))
            path=self.source/name
            r._write_png(path,img,self.width,self.height)
            source_hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        self.source_sha=source_hashes["cena-base.png"]
        records={name[:-4]:{"sha256":source_hashes[name],
                            "technical_status":"verified"}
                 for name in r.REQUIRED if name!="cena-base.png"}
        source={"sha256":self.source_sha,"width":self.width,"height":self.height}
        (self.source/"manifest.json").write_text(json.dumps({
            "schema":scene_layers.SCHEMA,
            "channel":"otaku-br","video_id":self.video_id,"scene":self.scene,
            "source":source,"layers":records,
        }))
        self.plan={
            "schema":r.PLAN_SCHEMA,
            "channel":"otaku-br","video_id":self.video_id,"scene":self.scene,
            "source_sha256":self.source_sha,
            "canvas":{"width":self.width,"height":self.height},
            "head_polygon":[[20,9],[44,9],[45,43],[21,45]],
            "eye_polygons":[[[30,21],[37,21],[38,28],[30,29]]],
            "skin_samples":[[32,33]],
            "eyelid_lines":[{"points":[[30,25],[38,25]],"radius":1,"color":[32,14,18]}],
            "cape_front_polygon":[[18,35],[48,35],[45,60],[18,60]],
            "neck_pivot":[32,42],
            "head_max_deg":1.5,
            "blink_frames":[15,60],
            "cape_mesh":{"bounds":{"x":8,"y":27,"width":29,"height":55},
                         "columns":3,"rows":4,"amplitude_px":3},
            "approved":False
        }
        self.plan_path=self.root/"plan.json"
        self.output=self.root/"output/otaku-br/videos/teste-001/rig-candidates/cena-01"
        self.write_plan()

    def write_plan(self):
        self.plan_path.write_text(json.dumps(self.plan))

    def test_candidate_prepares_real_pngs_but_keeps_approval_false(self):
        report=r.prepare(self.source,self.plan_path,self.output)
        self.assertEqual(report["status"],"draft_unapproved")
        self.assertEqual(report["eyes_extracted_from_original"],1)
        self.assertFalse(report["rig_ready_for_remotion"])
        self.assertTrue(report["needs_manual_reconstruction"])
        self.assertGreater(report["body_pixels_erased_without_inpainting"],0)
        self.assertTrue((self.output/"contact-sheet.png").is_file())
        c=scene_layers.png_info((self.output/"contact-sheet.png").read_bytes())
        self.assertEqual((c["width"],c["height"]),(128,48))
        rig=json.loads((self.output/"rig.json").read_text())
        self.assertFalse(any(rig["human_review"].values()))
        self.assertIn("cape-front.png",rig["assets"])
        for name,sha in rig["assets"].items():
            data=(self.output/name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),sha)
            info=scene_layers.png_info(
                data,require_alpha=True,
                min_visible_fraction=.00001 if name.startswith("eyes-") else .005)
            self.assertEqual((info["width"],info["height"]),(64,96))
        with self.assertRaisesRegex(mesh_rig.RigAssetError,"RIG_HUMAN_ASSET_REVIEW_REQUIRED"):
            mesh_rig.validate_rig_dir(
                self.output,channel="otaku-br",video_id=self.video_id,
                scene=self.scene,source_sha=self.source_sha,
                width=self.width,height=self.height,duration_frames=240)
        with self.assertRaisesRegex(r.CandidateError,"OUTPUT_ALREADY_EXISTS"):
            r.prepare(self.source,self.plan_path,self.output)

    def test_fail_closed_on_bad_scene_hash_and_mask_geometry(self):
        for key,value in (("video_id","outro-video"),("source_sha256","x"*64)):
            with self.subTest(key=key):
                original=self.plan[key]
                self.plan[key]=value
                self.write_plan()
                with self.assertRaises(r.CandidateError):
                    r.prepare(self.source,self.plan_path,self.output)
                self.assertFalse(self.output.exists())
                self.plan[key]=original
        self.plan["eye_polygons"]=[[[50,70],[57,70],[57,77],[50,77]]]
        self.write_plan()
        with self.assertRaisesRegex(r.CandidateError,"RIG_EYE_NOT_INSIDE_HEAD"):
            r.prepare(self.source,self.plan_path,self.output)

    def test_png_round_trip_and_masks(self):
        mask=r._mask([[[3,3],[10,3],[10,12],[3,12]]],16,16)
        self.assertGreater(mask.count(255),20)
        self.assertEqual(mask[0],0)
        data=bytearray(16*16*4)
        for i in range(16*16):
            data[4*i:4*i+4]=bytes((99,123,234,255))
        path=self.root/"test.png"
        r._write_png(path,data,16,16)
        raw=r._image(path,16,16)
        self.assertEqual(raw,data)


if __name__=="__main__":
    unittest.main()
