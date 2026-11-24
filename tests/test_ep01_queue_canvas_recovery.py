"""Do not rebill a rejected archived image. Tiny PNG edges are QA candidates."""
import base64
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw
from scripts import ep01_action_production_queue as queue
from videoforge import ep01_proxy_separate_parts as producer


class TinyCanvasAndRecovery(unittest.TestCase):
    def make_image(self, size):
        frame=Image.new("RGBA",size,(0,0,0,0))
        ImageDraw.Draw(frame).rectangle((50,50,90,140),fill=(150,60,50,255))
        b=BytesIO()
        frame.save(b,format="PNG")
        return b.getvalue()

    def fake_source(self):
        # Valid request canvas; these tests exercise provider output QA.
        return {
            "mother":b"mother-reference","refs":[],
            "mother_proof":{"sha256":"a"*64},
            "ref_proofs":[],"source_dimensions":(1024,1536),
            "transparent":True,"role":"character",
            "prompt":"source-aligned full-canvas real RGBA character asset",
        }

    def test_one_pixel_height_delta_is_archived_as_unapproved_alignment_candidate(self):
        with tempfile.TemporaryDirectory() as folder:
            raw=self.make_image((1024,1535))
            with patch.object(producer,"prepare",return_value=self.fake_source()):
                with patch.object(producer.proxy_images,"call_proxy",return_value={"fake":"response"}):
                    with patch.object(producer.proxy_images,"decode_image",return_value=(raw,".png")):
                        info=producer.generate("C01-P05","character-guarda_direito",
                                               "http://not-used",root=Path(folder))
            self.assertEqual(info["technical_qa"],
                             "candidate_minor_edge_delta_requires_alignment_qa")
            self.assertEqual([info["width"],info["height"]],[1024,1535])
            self.assertEqual(info["source_canvas"],[1024,1536])
            self.assertTrue(info["coordinate_alignment_required"])
            self.assertFalse(info["placement_verified"])
            self.assertFalse(info["rig_ready"])
            self.assertFalse(info["human_visual_approval"])
            self.assertFalse(info["youtube_uploaded"])
            original=Path(folder)/"output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/imagens/c01-p05-character-guarda_direito.png"
            self.assertEqual(original.read_bytes(),raw)

    def test_large_canvas_mismatch_still_rejected_and_archived(self):
        with tempfile.TemporaryDirectory() as folder:
            raw=self.make_image((930,1630))
            with patch.object(producer,"prepare",return_value=self.fake_source()):
                with patch.object(producer.proxy_images,"call_proxy",return_value={"fake":"response"}):
                    with patch.object(producer.proxy_images,"decode_image",return_value=(raw,".png")):
                        with self.assertRaisesRegex(Exception,"GENERATED_REJECTED_BUT_ARCHIVED"):
                            producer.generate("C01-P05","character-guarda_direito",
                                              "http://not-used",root=Path(folder))
            meta=Path(folder)/"output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/imagens/c01-p05-character-guarda_direito.production.json"
            self.assertEqual(json.loads(meta.read_text())["technical_qa"],
                             "rejected_canvas_mismatch_no_pixel_resizing")

    def test_failed_paid_child_with_verified_rejected_png_is_terminal_never_replayed(self):
        task={
            "task_id":"image:C01-P05:character-guarda_direito:6a599ab681994790b3e9",
            "kind":"image","shot_id":"C01-P05","part":"character-guarda_direito",
            "source_sha256":"6a599ab681994790b3e9b07bf573817781a448bcf9f77081bc03764448028553",
        }
        plan={"tasks":[task]}
        ledger={"schema_version":1,"schema":queue.STATE_SCHEMA,
                "attempts":{task["task_id"]:{
                    "status":"blocked_failed","workflow":queue.IMAGE_WORKFLOW,
                    "source_sha256":task["source_sha256"],
                    "child_run_id":44524006117}}}
        saved=[]
        class Remote:
            def save(self,data):
                queue.QueueRemote._validate_snapshot(data)
                saved.append(deepcopy(data))
        prior={"file":"canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-proxy-separate-part-v1/44524006117/c01-p05-character-guarda_direito.png",
               "sha256":"7"*64}
        info={"sha256":"7"*64,"source_mother_sha256":task["source_sha256"],
              "asset_id":"c01-p05-character-guarda_direito",
              "technical_qa":"rejected_canvas_mismatch_no_pixel_resizing",
              "human_visual_approval":False,"rig_ready":False,
              "youtube_uploaded":False}
        with patch.object(queue.parts,"existing_part",return_value=prior):
            with patch.object(queue,"load_json",return_value=info):
                with patch.object(queue,"gh",return_value={
                    "conclusion":"failure","event":"workflow_dispatch","head_branch":"main"}):
                    fixed=queue.reconcile_rejected_archives(plan,Remote(),ledger)
        self.assertEqual(fixed,[task["task_id"]])
        self.assertEqual(ledger["attempts"][task["task_id"]]["status"],
                         "rejected_archived")
        self.assertEqual(ledger["attempts"][task["task_id"]]["sha256"],"7"*64)
        self.assertTrue(ledger["attempts"][task["task_id"]]["needs_human_visual_review"])
        self.assertFalse(ledger["attempts"][task["task_id"]]["cannot_be_used_as_approved_rig"] is False)
        self.assertEqual(len(saved),1)

    def test_failed_paid_child_with_restored_candidate_is_archived_no_replay(self):
        # The real C10-P01 source completed one paid proxy call, but the archive
        # push conflicted. Restore the original ZIP bytes first; only then may
        # this deterministic ledger reconciliation mark the attempt terminal.
        task={
            "task_id":"image:C10-P01:background-clean:bf4bcf0210528b26bd8a",
            "kind":"image","shot_id":"C10-P01","part":"background-clean",
            "source_sha256":"bf4bcf0210528b26bd8a97b5ed9d953322e4b0edbe2ec5283c82470dd18a0c82",
        }
        prior={
            "file":"canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-proxy-separate-part-v1/44740269740/c10-p01-background-clean.png",
            "sha256":"ff290bddb995f049fb2a95def7fcb0babe3f8195781f1340284225f2ae00f460",
        }
        info={
            "sha256":prior["sha256"],
            "source_mother_sha256":task["source_sha256"],
            "asset_id":"c10-p01-background-clean",
            "technical_qa":"candidate_minor_edge_delta_requires_alignment_qa",
            "human_visual_approval":False,"rig_ready":False,
            "youtube_uploaded":False,
        }
        saved=[]
        class Remote:
            def save(self, data):
                queue.QueueRemote._validate_snapshot(data)
                saved.append(deepcopy(data))
        for mutation in ("valid","wrong_file_sha","wrong_origin","not_final_child",
                         "not_main_child","untrusted_quality","wrong_source_run"):
            record={"status":"blocked_failed","workflow":queue.IMAGE_WORKFLOW,
                    "source_sha256":task["source_sha256"],
                    "child_run_id":44740269740}
            ledger={"schema_version":1,"schema":queue.STATE_SCHEMA,
                    "attempts":{task["task_id"]:record}}
            source=dict(prior)
            metadata=dict(info)
            child={"conclusion":"failure","event":"workflow_dispatch","head_branch":"main"}
            if mutation=="wrong_file_sha":
                metadata["sha256"]="0"*64
            elif mutation=="wrong_origin":
                metadata["source_mother_sha256"]="1"*64
            elif mutation=="not_final_child":
                child["conclusion"]="success"
            elif mutation=="not_main_child":
                child["head_branch"]="feature"
            elif mutation=="untrusted_quality":
                metadata["technical_qa"]="approved_no_qa"
            elif mutation=="wrong_source_run":
                source["file"]=source["file"].replace("44740269740","999999999")
            with self.subTest(mutation=mutation):
                with patch.object(queue.parts,"existing_part",return_value=source):
                    with patch.object(queue,"load_json",return_value=metadata):
                        with patch.object(queue,"gh",return_value=child):
                            fixed=queue.reconcile_rejected_archives({"tasks":[task]},Remote(),ledger)
                if mutation=="valid":
                    self.assertEqual(fixed,[task["task_id"]])
                    self.assertEqual(record["status"],"archived")
                    self.assertTrue(record["needs_human_visual_review"])
                    self.assertFalse(record["youtube_publication"])
                    self.assertEqual(record["sha256"],prior["sha256"])
                    self.assertEqual(record["technical_qa"],info["technical_qa"])
                else:
                    self.assertEqual(fixed,[])
                    self.assertEqual(record["status"],"blocked_failed")
        self.assertEqual(len(saved),1)

    def test_unrelated_or_unverified_failure_remains_blocked_and_unresolved(self):
        task={"task_id":"image:C01-P05:character-guarda_direito:6a599ab681994790b3e9",
              "kind":"image","shot_id":"C01-P05","part":"character-guarda_direito",
              "source_sha256":"6a599ab681994790b3e9b07bf573817781a448bcf9f77081bc03764448028553"}
        attempts={task["task_id"]:{"status":"blocked_failed",
                  "workflow":queue.IMAGE_WORKFLOW,
                  "child_run_id":44524006117,
                  "source_sha256":task["source_sha256"]}}
        ledger={"schema_version":1,"schema":queue.STATE_SCHEMA,"attempts":attempts}
        class Remote:
            def save(self,data):
                raise AssertionError("No unverified reconciliation allowed")
        with patch.object(queue.parts,"existing_part",return_value=None):
            self.assertEqual(queue.reconcile_rejected_archives(
                {"tasks":[task]},Remote(),ledger),[])
        self.assertEqual(attempts[task["task_id"]]["status"],"blocked_failed")


if __name__=="__main__":
    unittest.main()
