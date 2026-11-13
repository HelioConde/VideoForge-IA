"""Regressao de preparo de sprite candidato (apenas stdlib + FFmpeg do runner)."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videoforge import mesh_rig, proxy_images, rig_candidate as r, rig_hair_repair, rig_eye_ai, scene_layers


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

    def test_alpha_over_keeps_fractional_pixels_in_valid_byte_range(self):
        base=bytearray((248,255,250,3))
        top=bytearray((252,252,252,2))
        r._composite(base,top)
        self.assertEqual(len(base),4)
        self.assertTrue(all(0<=value<=255 for value in base))
        self.assertGreater(base[3],0)

    def test_natural_eyes_are_generated_and_remain_unapproved(self):
        self.plan["eyelid_beziers"] = [
            {"points": [[30,23],[32,26],[35,27],[37,26]],
             "width":1.4,"color":[66,30,25]},
        ]
        self.write_plan()
        report=r.prepare(self.source,self.plan_path,self.output)
        detail=report["natural_eyelids_preview"]
        self.assertIn("antialiased",detail["technique"])
        self.assertEqual(detail["external_model_calls"],0)
        self.assertFalse(report["rig_ready_for_remotion"])
        eyelid=r._image(self.output/"eyes-closed.png",64,96)
        self.assertTrue(any(0 < eyelid[i] < 255 for i in range(3,len(eyelid),4)))
        self.assertGreater(detail["closed_lid_visible_pixels"],0)
        self.assertTrue(report["head_open_original_pixels_preserved"])
        self.assertIn("head-open.png", report["asset_sha256"])
        open_head=r._image(self.output/"head-open.png",64,96)
        fixed_head=r._image(self.output/"head-no-eyes.png",64,96)
        eye_pixel=(25*64+32)*4
        original_head=r._image(self.source/"character-main.png",64,96)
        self.assertEqual(open_head[eye_pixel:eye_pixel+4],original_head[eye_pixel:eye_pixel+4])
        self.assertEqual(open_head[eye_pixel:eye_pixel+4],bytes((95,55,90,255)))
        self.assertEqual(
            report["asset_sha256"]["eyes-closed.png"],
            hashlib.sha256((self.output/"eyes-closed.png").read_bytes()).hexdigest(),
        )

    def test_complete_hair_mask_guards_every_original_visible_strand(self):
        self.plan["head_full_polygon"]=[
            [19,8],[44,8],[46,43],[21,46],[19,40]]
        self.plan["hair_guard_bbox"]=[25,12,40,33]
        self.write_plan()
        report=r.prepare(self.source,self.plan_path,self.output)
        self.assertEqual(report["head_mask_variant"],"head_full_polygon")
        self.assertEqual(report["head_full_hair_guard_alpha_coverage"],1.0)
        source=r._image(self.source/"character-main.png",64,96)
        head=r._image(self.output/"head-open.png",64,96)
        for y in range(12,33):
            for x in range(25,40):
                off=4*(y*64+x)
                self.assertEqual(head[off:off+4],source[off:off+4])

    def test_clipped_hair_is_rejected_even_when_eye_polygon_fits(self):
        self.plan["head_full_polygon"]=[[27,15],[43,15],[43,40],[27,40]]
        self.plan["hair_guard_bbox"]=[25,12,40,33]
        self.write_plan()
        with self.assertRaisesRegex(r.CandidateError,"RIG_HAIR_CLIPPED_BY_HEAD_MASK"):
            r.prepare(self.source,self.plan_path,self.output)
        self.assertFalse(self.output.exists())

    def test_reuse_existing_ai_eye_pixels_on_complete_original_hair(self):
        self.plan["head_full_polygon"]=[[19,8],[44,8],[46,43],[21,46],[19,40]]
        self.plan["hair_guard_bbox"]=[25,12,40,33]
        self.write_plan()
        r.prepare(self.source,self.plan_path,self.output)
        old=self.root/"archived-eye"
        old.mkdir()
        data=r._image(self.output/"head-open.png",64,96)
        old_open=bytearray(data)
        # Previous head lost a hair strand; keep it missing in both old sprites.
        for x in range(31,39):
            p=4*(17*64+x)
            old_open[p:p+4]=b"\\0\\0\\0\\0"
        old_closed=bytearray(old_open)
        for y in range(21,31):
            for x in range(28,41):
                off=4*(y*64+x)
                old_closed[off:off+3]=bytes((25,35,46))
        r._write_png(old/"head-open.png",old_open,64,96)
        r._write_png(old/"head-closed-ai.png",old_closed,64,96)
        r._write_png(old/"face-closed-ai-reference.png",old_closed,64,96)
        filenames=("head-open.png","head-closed-ai.png","face-closed-ai-reference.png")
        (old/"manifest.json").write_text(json.dumps({
            "schema":"videoforge/original-eye-ai-archive/v1",
            "channel":"otaku-br","video_id":"teste-001","scene":"cena-01",
            "source_run_id":12345678,"source_sha256":self.source_sha,
            "files_sha256":{
                name:hashlib.sha256((old/name).read_bytes()).hexdigest()
                for name in filenames},
            "human_review":False,"publishable":False,"model_calls_for_eye":1
        }))
        def weight(x,y,areas):
            return 1 if 28<=x-.5<41 and 21<=y-.5<31 else 0
        with patch.object(rig_eye_ai,"_eye_regions",return_value=[(34,25,10,10)]), \
             patch.object(rig_eye_ai,"_weight",side_effect=weight):
            report=rig_hair_repair.restore(
                self.output,old,self.plan_path,self.source)
        self.assertEqual(report["model_calls_in_this_repair"],0)
        self.assertEqual(report["eye_edited_pixels_reused"],130)
        repaired=r._image(self.output/"head-closed-ai.png",64,96)
        head=r._image(self.output/"head-open.png",64,96)
        # New strand is sourced from ORIGINAL, not the old clipped AI sprite.
        self.assertEqual(repaired[4*(17*64+34):4*(17*64+34)+4],
                         head[4*(17*64+34):4*(17*64+34)+4])
        self.assertNotEqual(repaired[4*(25*64+34):4*(25*64+34)+3],
                            head[4*(25*64+34):4*(25*64+34)+3])
        qa=json.loads((self.output/"candidate.qa.json").read_text())
        prov=json.loads((self.output/"asset-provenance.json").read_text())
        self.assertFalse(qa["human_visual_approval"])
        self.assertFalse(qa["rig_ready_for_remotion"])
        self.assertEqual(prov["model_calls"],1)
        self.assertEqual(prov["eye_ai_edit"]["model_calls_in_this_repair"],0)
        with self.assertRaisesRegex(rig_hair_repair.HairRepairError,"NO_OVERWRITE"):
            with patch.object(rig_eye_ai,"_eye_regions",return_value=[(34,25,10,10)]), \
                 patch.object(rig_eye_ai,"_weight",side_effect=weight):
                rig_hair_repair.restore(self.output,old,self.plan_path,self.source)

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
