"""Independent C01-P02 PNG layers, original mother, anchor and QA invariants.

Synthetic fixtures are TEST-ONLY; no visual approval or production PNG emitted.
"""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import EPISODE
from videoforge.remake_sword_preview import (
    preflight,prepare,validate_package,SCHEMA,PARTS,CH,VID,SHOT,
)
ROOT=Path(__file__).resolve().parents[1]

try:
    from PIL import Image,ImageDraw
except ImportError:
    Image=None


class SwordPreviewTests(unittest.TestCase):
    def test_first_current_preflight_stops_before_any_image_generation(self):
        result=preflight()
        self.assertEqual(result["shot_id"],SHOT)
        self.assertEqual(result["global_frames"],[60,150])
        self.assertEqual(result["shot_duration_frames"],90)
        self.assertFalse(result["ready_for_render"])
        self.assertEqual(result["api_calls"],0)
        self.assertEqual(result["images_generated"],0)
        self.assertFalse(result["youtube_uploaded"])
        self.assertIn("ANCHOR",result["blocked_reason"])

    def test_missing_package_fails_closed_without_workflow_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_ARTIFACT_REQUIRED"):
                validate_package(Path(tmp)/"none",100)

    @unittest.skipUnless(Image is not None,"Pillow required only for real-image recomposition smoke")
    def test_independent_parts_stage_real_png_bytes_in_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            package=self._fixture(root)
            out=root/"output"
            public=root/"public"
            result=prepare(package,12345,out,public,root)
            self.assertEqual(result["neutral_mae_rgb"],0)
            self.assertFalse(result["human_visual_approved"])
            self.assertFalse(result["official_video_approved"])
            props=json.loads((out/"props.json").read_text(encoding="utf-8"))
            self.assertTrue(props["rig"]["technicalDraftOnly"])
            self.assertFalse(props["rig"]["humanVisualReview"])
            self.assertEqual(props["durationFrames"],90)
            self.assertEqual(set(props["rig"]["layers"]),set(PARTS))
            for part in PARTS:
                self.assertEqual(
                    hashlib.sha256((public/(part+".png")).read_bytes()).hexdigest(),
                    props["rig"]["layers"][part]["sha256"])
            with self.assertRaisesRegex(VideoForgeError,"PUBLIC_DIR_ALREADY_IN_USE"):
                prepare(package,12345,out,public,root)

    @unittest.skipUnless(Image is not None,"Pillow required")
    def test_wrong_source_origin_or_alpha_cannot_be_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            package=self._fixture(root)
            source=package/"scene-mother.production.json"
            data=json.loads(source.read_text())
            data["shot_id"]="C01-P03"
            source.write_text(json.dumps(data))
            with self.assertRaisesRegex(VideoForgeError,"MOTHER_PROVENANCE_INVALID"):
                validate_package(package,12345,root)

    @unittest.skipUnless(Image is not None,"Pillow required")
    def test_artifact_run_and_layer_sha_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            package=self._fixture(root)
            with self.assertRaisesRegex(VideoForgeError,"BUNDLE_ORIGIN"):
                validate_package(package,99999,root)
            with (package/"hand.png").open("ab") as f:f.write(b"tampered")
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_SHA_MISMATCH:hand"):
                validate_package(package,12345,root)

    def _fixture(self,root:Path)->Path:
        # Deliberately synthetic TEST fixtures; never write to real repo.
        if Image is None:raise AssertionError("PIL missing")
        ep=root/EPISODE
        ep.mkdir(parents=True)
        for filename in ("remake-ep01-planos.json","estado-atual.json","roteiro.json","autonomy-policy.json"):
            shutil.copyfile(ROOT/EPISODE/filename,ep/filename)
        work=ep/"assets/geracoes/production-art-request/55555"
        work.mkdir(parents=True)
        anchor=Image.new("RGB",(1024,1536),(12,13,14))
        anchor.save(work/"character-bible.png")
        anchor_sha=hashlib.sha256((work/"character-bible.png").read_bytes()).hexdigest()
        plan_path=ep/"remake-ep01-planos.json"
        plan=json.loads(plan_path.read_text(encoding="utf-8"))
        plan["identity_anchors"][0].update({
            "path":"assets/geracoes/production-art-request/55555/character-bible.png",
            "sha256":anchor_sha,"human_approved":True,"status":"approved"})
        plan_path.write_text(json.dumps(plan),encoding="utf-8")
        package=root/"source"
        package.mkdir()
        underlay=Image.new("RGB",(1024,1536),(12,13,14))
        layers={}
        for name,color,rect in (
            ("sheath",(130,140,148,255),(390,650,420,1090)),
            ("blade",(220,220,235,255),(430,620,457,1020)),
            ("hand",(137,89,76,255),(400,860,485,960)),
        ):
            img=Image.new("RGBA",(1024,1536),(0,0,0,0))
            ImageDraw.Draw(img).rectangle(rect,fill=color)
            layers[name]=img
            img.save(package/(name+".png"))
        underlay.save(package/"underlay.png")
        comp=underlay.convert("RGBA")
        for name in ("sheath","blade","hand"):comp.alpha_composite(layers[name])
        comp.convert("RGB").save(package/"scene-mother.png")
        hashes={name:hashlib.sha256((package/(name+".png")).read_bytes()).hexdigest()
                for name in ("underlay","sheath","blade","hand")}
        hashes["scene-mother"]=hashlib.sha256((package/"scene-mother.png").read_bytes()).hexdigest()
        original={"schema":"videoforge/production-scene/v1",
            "channel":CH,"video_id":VID,"number":1,"scene":"C01",
            "shot_id":SHOT,"shot_specific":True,"reference_sha256":anchor_sha,
            "sha256":hashes["scene-mother"],"technical_qa":"valid_png_opaque",
            "youtube_uploaded":False}
        (package/"scene-mother.production.json").write_text(json.dumps(original),encoding="utf-8")
        bundle={"schema":SCHEMA,"channel":CH,"video_id":VID,
            "shot_id":SHOT,"source_run_id":12345,
            "source_artifact":"vf-remake-c01-p02-sword-source-12345",
            "anchor_sha256":anchor_sha,"sha256":hashes,
            "wristPivot":[427,930],
            "draw":{"beginFrame":7,"finishFrame":72,"travelPx":100,"axisDeg":-10,
                "handFollow":.8,"handRotationDeg":2},
            "human_visual_approved":False,"official_video_approved":False,
            "youtube_uploaded":False}
        (package/"sword-bundle.json").write_text(json.dumps(bundle),encoding="utf-8")
        return package


if __name__=="__main__":
    unittest.main()
