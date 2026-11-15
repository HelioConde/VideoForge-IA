"""Real-source packer regressions, using ONLY isolated synthetic temp fixtures.

The default checkout is always blocked until approved anchor + real shot art.
No PNG files from these tests go into the user channel or Github history.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import EPISODE
from videoforge.remake_sword_pack import (
    scan,assemble,MOTHER_PRODUCER,PART_PRODUCER,UNDERLAY_PRODUCER,
)
from tests.test_remake_sword_preview import SwordPreviewTests,FFMPEG_PRESENT

ROOT=Path(__file__).resolve().parents[1]


def archived(ep:Path,producer:str,run:int,file:str,raw:bytes,qa_file:str,qa:dict)->Path:
    dest=ep/"assets"/"geracoes"/producer/str(run)
    dest.mkdir(parents=True)
    (dest/file).write_bytes(raw)
    (dest/qa_file).write_text(json.dumps(qa),encoding="utf-8")
    manifest={
        "schema":"videoforge/permanent-generated-image-archive/v1",
        "channel":"alchemy-lab",
        "video_id":"mmorpg-conquiste-a-princesa-ep01",
        "producer":producer,"github_run_id":run,
        "production_approved":False,"youtube_uploaded":False,
        "images":[{"file":file,"sha256":hashlib.sha256(raw).hexdigest(),
                   "width":1024,"height":1536,
                   "human_visual_approval":False}],
    }
    (dest/"manifesto-geracoes.json").write_text(json.dumps(manifest),encoding="utf-8")
    return dest


class RemakeSwordPackTests(unittest.TestCase):
    def test_actual_repository_cannot_claim_a_complete_package(self):
        status=scan()
        self.assertIsInstance(status["ready"],bool)
        if status["ready"]:
            self.assertIsNone(status["blocker"])
        else:
            self.assertIsInstance(status["blocker"],str)
        self.assertEqual(status["new_image_generation_calls"],0)
        self.assertFalse(status["official_video_approved"])
        self.assertFalse(status["youtube_uploaded"])
        # A repository with a newly approved real anchor may legitimately
        # transition to ready; a QA test must never freeze production.

    def test_no_paid_call_and_no_synthetic_output_in_empty_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            ep=root/EPISODE
            ep.mkdir(parents=True)
            for file in ("remake-ep01-planos.json","estado-atual.json",
                         "roteiro.json","autonomy-policy.json"):
                shutil.copyfile(ROOT/EPISODE/file,ep/file)
            with self.assertRaisesRegex(VideoForgeError,"V2_ANCHOR_NOT_APPROVED"):
                assemble(333,root/"result",root)
            self.assertFalse((root/"result/sword-bundle.json").exists())

    @unittest.skipUnless(FFMPEG_PRESENT,"FFmpeg required")
    def test_prevent_endless_repacking_of_already_qad_same_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            sources=self.create_test_archive(root)
            ep=sources["ep"]
            mother_sha=hashlib.sha256((sources["source"]/"scene-mother.png").read_bytes()).hexdigest()
            anchor_sha=json.loads((ep/"remake-ep01-planos.json").read_text())["identity_anchors"][0]["sha256"]
            proof={"schema":"videoforge/remake-sword-preview-qa/v1",
                   "source_mother_sha256":mother_sha,
                   "anchor_sha256":anchor_sha,
                   "technical_preview_only":True,
                   "official_video_approved":False,
                   "youtube_uploaded":False}
            (ep/"QA-C01-P02-REMAKE-V2.json").write_text(json.dumps(proof),encoding="utf-8")
            status=scan(root)
            self.assertFalse(status["ready"])
            self.assertEqual(status["blocker"],
                             "REMAKE_PACK_SAME_SOURCE_ALREADY_RENDERED_TECHNICALLY")
            with self.assertRaisesRegex(VideoForgeError,"SAME_SOURCE_ALREADY_RENDERED"):
                assemble(888,root/"second",root)

    def create_test_archive(self,root:Path)->dict:
        original=SwordPreviewTests().fixture(root)
        ep=root/EPISODE
        mother=(original/"scene-mother.png").read_bytes()
        momsha=hashlib.sha256(mother).hexdigest()
        origin=json.loads((original/"scene-mother.production.json").read_text(encoding="utf-8"))
        mom=archived(ep,MOTHER_PRODUCER,501,
                     "cena-01-c01-p02.png",mother,
                     "cena-01-c01-p02.production.json",origin)
        component_archives={}
        for i,part in enumerate(("underlay","sheath","blade","hand")):
            raw=(original/(part+".png")).read_bytes()
            prov={
                "schema":("videoforge/remake-underlay-candidate/v1" if part=="underlay"
                          else "videoforge/rgba-part-candidate/v1"),
                "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
                "scene_mother_sha256":momsha,"output_sha256":hashlib.sha256(raw).hexdigest(),
                "technical_status":("candidate_opaque_verified" if part=="underlay"
                                    else "candidate_rgba_verified"),
                "human_visual_approval":False,"youtube_uploaded":False,
            }
            if part=="underlay":prov["shot_id"]="C01-P02"
            else:prov.update({"scene_number":1,"part_id":part})
            component_archives[part]=archived(
                ep,UNDERLAY_PRODUCER if part=="underlay" else PART_PRODUCER,
                502+i,part+".png",raw,part+".qa.json",prov)
        return {"ep":ep,"source":original,"mother":mom,"parts":component_archives}

    @unittest.skipUnless(FFMPEG_PRESENT,"container FFmpeg required for positive recomposition")
    def test_real_archive_selection_and_auto_pack_with_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            self.create_test_archive(root)
            preview=scan(root)
            self.assertTrue(preview["ready"],preview["blocker"])
            self.assertEqual(set(preview["archived_sources_found"]),
                             {"underlay","sheath","blade","hand"})
            out=root/"bundle"
            report=assemble(77777,out,root)
            self.assertEqual(report["neutral_mae_rgb"],0)
            self.assertTrue(report["human_motion_review_required"])
            self.assertFalse(report["official_video_approved"])
            self.assertEqual(report["new_image_generation_calls"],0)
            self.assertEqual(report["artifact_name"],
                             "vf-remake-c01-p02-sword-source-77777")
            bundle=json.loads((out/"sword-bundle.json").read_text(encoding="utf-8"))
            self.assertEqual(bundle["source_archives"]["scene-mother"]["source_run_id"],501)
            self.assertEqual(bundle["source_archives"]["blade"]["source_run_id"],504)
            self.assertTrue(bundle["draft_motion_heuristic_only"])
            self.assertEqual(set(bundle["sha256"]),
                             {"scene-mother","underlay","sheath","blade","hand"})
            self.assertFalse(bundle["human_visual_approved"])
            with self.assertRaisesRegex(VideoForgeError,"DESTINATION_NOT_EMPTY"):
                assemble(77777,out,root)

    @unittest.skipUnless(FFMPEG_PRESENT,"container FFmpeg required for selected archives")
    def test_refuse_cross_mother_layer_even_with_valid_per_file_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            sources=self.create_test_archive(root)
            hand=sources["parts"]["hand"]/"hand.qa.json"
            report=json.loads(hand.read_text(encoding="utf-8"))
            report["scene_mother_sha256"]="f"*64
            hand.write_text(json.dumps(report),encoding="utf-8")
            status=scan(root)
            self.assertFalse(status["ready"])
            self.assertIn("hand",status["blocker"])
            with self.assertRaisesRegex(VideoForgeError,"MISSING_SAME_MOTHER_PARTS"):
                assemble(77777,root/"bundle",root)

    @unittest.skipUnless(FFMPEG_PRESENT,"container FFmpeg required")
    def test_reject_wrong_video_metadata_and_corrupt_source_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            sources=self.create_test_archive(root)
            mom=sources["mother"]/"manifesto-geracoes.json"
            j=json.loads(mom.read_text(encoding="utf-8"))
            j["video_id"]="other-episode"
            mom.write_text(json.dumps(j),encoding="utf-8")
            status=scan(root)
            self.assertFalse(status["ready"])
            self.assertIn("MOTHER_NOT_ARCHIVED",status["blocker"])
            j["video_id"]="mmorpg-conquiste-a-princesa-ep01"
            mom.write_text(json.dumps(j),encoding="utf-8")
            with (sources["mother"]/"cena-01-c01-p02.png").open("ab") as fp:
                fp.write(b"extra")
            status=scan(root)
            self.assertFalse(status["ready"])
            self.assertIn("MOTHER_NOT_ARCHIVED",status["blocker"])


if __name__=="__main__":
    unittest.main()
