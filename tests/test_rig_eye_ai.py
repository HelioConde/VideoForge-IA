"""Contrato de edicao real com imagem ORIGINAL + mascara; zero chamadas em CI."""
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videoforge import rig_candidate as c, rig_eye_ai as e, proxy_images as p


class EyeAIContract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.plan=json.loads(Path(
            "canal/otaku-br/videos/teste-proxy-20261113/rig-plan.json"
        ).read_text())

    def test_only_eyes_are_editable(self):
        regions=e._eye_regions(self.plan)
        self.assertEqual(len(regions),2)
        self.assertEqual(e._weight(10,10,regions),0)
        self.assertEqual(e._weight(447,339,regions),1)
        self.assertGreater(e._weight(489,350,regions),.2)
        self.assertEqual(e._weight(445,395,regions),0)

    def test_edit_uses_images_edits_route_with_actual_reference_and_mask(self):
        work=self.root/"work"
        work.mkdir()
        blank=bytearray(1024*1024*4)
        for i in range(3,len(blank),4): blank[i]=255
        p1=work/"reference-face.png"
        p2=work/"edit-mask.png"
        c._write_png(p1,blank,1024,1024)
        for i in range(0,len(blank),4):blank[i:i+4]=bytes((255,255,255,255))
        for y in range(450,480):
            for x in range(430,480):
                blank[4*(y*1024+x)+3]=0
        c._write_png(p2,blank,1024,1024)
        ref_sha=hashlib.sha256(p1.read_bytes()).hexdigest()
        mask_sha=hashlib.sha256(p2.read_bytes()).hexdigest()
        (work/"eye-ai.json").write_text(json.dumps({
            "schema":e.SCHEMA,"status":"prepared_not_generated",
            "reference_sha256":ref_sha,"mask_sha256":mask_sha,
            "model_calls":0,"human_visual_approval":False,
        }))
        fake={"data":[{"b64_json":base64.b64encode(p1.read_bytes()).decode()}]}
        with patch.object(p,"call_proxy",return_value=fake) as request:
            meta=e.edit("https://proxy.example","s"*32,work,"gpt-image-1.5")
        self.assertEqual(request.call_count,1)
        args,kwargs=request.call_args
        self.assertEqual(args[1],"/v1/images/edits")
        payload=args[3]
        self.assertIn("images",payload)
        self.assertIn("mask",payload)
        self.assertTrue(payload["images"][0]["image_url"].startswith("data:image/png;base64,"))
        self.assertEqual(payload["input_fidelity"],"high")
        self.assertIn("both visible eyes",payload["prompt"])
        self.assertEqual(meta["model_calls"],1)
        self.assertFalse(meta["human_visual_approval"])
        self.assertEqual((work/"face-closed-ai.png").read_bytes(),p1.read_bytes())
        with self.assertRaisesRegex(e.EyeAIError,"NOT_GENERATED|PREPARATION_INVALID"):
            e.edit("https://proxy.example","s"*32,work,"gpt-image-1.5")

    def test_portrait_output_from_proxy_is_saved_for_alignment(self):
        work=self.root/"portrait"
        work.mkdir()
        original=bytearray(1024*1024*4)
        for i in range(3,len(original),4):original[i]=255
        c._write_png(work/"reference-face.png",original,1024,1024)
        for y in range(440,490):
            for x in range(440,490):
                original[4*(y*1024+x)+3]=0
        c._write_png(work/"edit-mask.png",original,1024,1024)
        portrait=bytearray(1024*1536*4)
        for i in range(3,len(portrait),4):portrait[i]=255
        c._write_png(work/"response.png",portrait,1024,1536)
        meta={
            "schema":e.SCHEMA,"status":"prepared_not_generated","model_calls":0,
            "reference_sha256":hashlib.sha256((work/"reference-face.png").read_bytes()).hexdigest(),
            "mask_sha256":hashlib.sha256((work/"edit-mask.png").read_bytes()).hexdigest(),
            "human_visual_approval":False,
        }
        (work/"eye-ai.json").write_text(json.dumps(meta))
        fake={"data":[{"b64_json":base64.b64encode((work/"response.png").read_bytes()).decode()}]}
        with patch.object(p,"call_proxy",return_value=fake) as request:
            result=e.edit("https://proxy.example","x"*32,work,"gpt-image-1.5")
        self.assertEqual(request.call_count,1)
        self.assertEqual(result["actual_size"],{"width":1024,"height":1536})
        self.assertTrue((work/e.EDITED_NAME).is_file())
        self.assertFalse(result["human_visual_approval"])

    def test_edited_eyes_only_change_original_head_under_mask(self):
        source=self.root/"src"
        source.mkdir()
        work=self.root/"edit"
        work.mkdir()
        candidate=self.root/"candidate"
        candidate.mkdir()
        plan_path=self.root/"plan.json"
        plan_path.write_text(json.dumps(self.plan))
        w,h=1024,1536
        original=bytearray(w*h*4)
        # Original character pixels, only in face region. Other pixels transparent.
        for y in range(220,515):
            for x in range(270,565):
                q=4*(y*w+x)
                original[q:q+4]=bytes((184,103,77,255))
        head=candidate/"head-open.png"
        c._write_png(head,original,w,h)
        head_hash=hashlib.sha256(head.read_bytes()).hexdigest()
        source_base=self.root/"base.png"
        c._write_png(source_base,original,w,h)
        source_hash=hashlib.sha256(source_base.read_bytes()).hexdigest()
        self.plan["source_sha256"]=source_hash
        plan_path.write_text(json.dumps(self.plan))
        (source/"cena-base.png").write_bytes(source_base.read_bytes())
        (source/"manifest.json").write_text(json.dumps({
            "schema":"videoforge/scene-layers/v1",
            "channel":"otaku-br","video_id":"teste-proxy-20261113","scene":"cena-01",
            "source":{"sha256":source_hash,"width":w,"height":h}
        }))
        (candidate/"rig.json").write_text(json.dumps({
            "schema":"videoforge/mesh-rig-assets/v1",
            "channel":"otaku-br","video_id":"teste-proxy-20261113","scene":"cena-01",
            "source_sha256":source_hash,"assets":{"head-open.png":head_hash},
            "candidate_only":True,
        }))
        (candidate/"candidate.qa.json").write_text(json.dumps({
            "status":"draft_unapproved","human_visual_approval":False,
            "rig_ready_for_remotion":False
        }))
        (candidate/"asset-provenance.json").write_text(json.dumps({
            "model_calls":0,"human_review":False
        }))
        face=bytearray(1024*1024*4)
        for i in range(0,len(face),4):face[i:i+4]=bytes((77,42,32,255))
        c._write_png(work/e.EDITED_NAME,face,1024,1024)
        edit_hash=hashlib.sha256((work/e.EDITED_NAME).read_bytes()).hexdigest()
        (work/"eye-ai.json").write_text(json.dumps({
            "schema":e.SCHEMA,"status":"generated_pending_review","model_calls":1,
            "source_sha256":source_hash,
            "plan_sha256":hashlib.sha256(plan_path.read_bytes()).hexdigest(),
            "face_closed_sha256":edit_hash,
            "reference_sha256":"a"*64,"mask_sha256":"b"*64,"model":"gpt-image-1.5",
        }))
        qa=e.apply(source,plan_path,work,candidate)
        closed=c._image(candidate/e.FINAL_NAME,w,h)
        self.assertNotEqual(original[4*(338*w+440):4*(338*w+440)+3],
                            closed[4*(338*w+440):4*(338*w+440)+3])
        for x,y in [(310,300),(440,400),(200,340),(800,900)]:
            pos=4*(y*w+x)
            self.assertEqual(original[pos:pos+4],closed[pos:pos+4])
        self.assertFalse(qa["human_visual_approval"])
        self.assertFalse(qa["publishable"])
        self.assertEqual(qa["model_calls_for_eye"],1)
        self.assertEqual(qa["eye_close_technique"],"image_edit_original_reference_masked")
        prov=json.loads((candidate/"asset-provenance.json").read_text())
        self.assertEqual(prov["model_calls"],1)


if __name__=="__main__":
    unittest.main()
