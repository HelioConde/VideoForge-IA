"""Real 42-shot queue coverage, anti-duplicate and fail-closed paid dispatch."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import ep01_action_production_queue as q

REAL_REMOTE_CLASS=q.QueueRemote


class FakeRemote:
    shared=None
    writes=[]
    def __init__(self,**kwargs):
        self.path=kwargs.get("path")
    def load(self):
        return deepcopy(FakeRemote.shared)
    def save(self,data):
        REAL_REMOTE_CLASS._validate_snapshot(data)
        FakeRemote.shared=deepcopy(data)
        FakeRemote.writes.append(deepcopy(data))
        return "remote-test-sha"


class ActionQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=q.build()

    def setUp(self):
        FakeRemote.shared=None
        FakeRemote.writes=[]

    def test_all_42_edited_shots_and_146_original_part_requests_have_tasks(self):
        p=self.plan
        self.assertEqual(p["schema"],q.SCHEMA)
        self.assertEqual(p["shots"],42)
        self.assertEqual(p["original_image_requests"],146)
        self.assertEqual(len(p["tasks"]),p["total_tasks"])
        self.assertEqual(len({t["task_id"] for t in p["tasks"]}),len(p["tasks"]))
        self.assertEqual(len([x for x in p["tasks"] if x["kind"]=="mother"]),42)
        self.assertEqual(len([x for x in p["tasks"] if x["kind"]=="image"]),146)
        self.assertEqual(len([x for x in p["tasks"] if x["kind"]=="image_correction"]),4)
        self.assertEqual(len([x for x in p["tasks"] if x["kind"]=="camera_preview"]),42)
        self.assertEqual(len([x for x in p["tasks"] if x["kind"]=="rig_animation"]),42)
        self.assertEqual(p["per_child_paid_image_cap"],1)
        self.assertFalse(p["image_approval_automatic"])
        self.assertFalse(p["rig_approval_automatic"])
        self.assertFalse(p["youtube_publication"])

    def test_existing_generated_parts_reused_and_rejected_originals_never_generated(self):
        items=self.plan["tasks"]
        # C01-P03 V1 generated PNGs exist, but their mother was rejected.
        # They are not canonical: the queue MUST block reusing this version.
        self.assertTrue(any(x["kind"]=="image" and
                            x["status"] in {"blocked_reference_revision","archived_version_check_needed"}
                            for x in items if x["shot_id"]=="C01-P03"))
        for item in items:
            if item["kind"]!="image":
                continue
            if item["shot_id"] in q.SHOTS_BLOCKED_FROM_LEGACY_PARTS:
                self.assertNotEqual(item["status"],"ready_for_preflight")
            if item["shot_id"]=="C01-P04" and "hand" in (item.get("part") or ""):
                self.assertNotEqual(item["status"],"ready_for_preflight")
        must=[t for t in items if t["kind"]=="image_correction"]
        self.assertTrue(any(t["part"]=="character-kael-v3" for t in must))
        self.assertTrue(all(t["status"]=="blocked_needs_shot_specific_prompt_and_art_qa"
                            for t in must if t["part"]!="character-kael-v3"))
        kael=next(t for t in must if t["part"]=="character-kael-v3")
        self.assertIn(kael["status"], {"ready_for_preflight","archived","archived_rejected_needs_review"})

    def test_all_42_actual_rig_animations_blocked_and_camera_previews_separate(self):
        tasks=self.plan["tasks"]
        rigs=[x for x in tasks if x["kind"]=="rig_animation"]
        cameras=[x for x in tasks if x["kind"]=="camera_preview"]
        self.assertEqual(len(rigs),len(cameras))
        self.assertEqual({x["shot_id"] for x in rigs},
                         {x["shot_id"] for x in cameras})
        self.assertTrue(all(x["status"]=="blocked_waiting_for_verified_rgba_and_rig"
                            for x in rigs))
        self.assertTrue(all(x["status"]=="ready_for_preflight" for x in cameras))
        self.assertEqual({t["paid_image_requests_per_child"] for t in cameras},{0})
        self.assertEqual({t["paid_image_requests_per_child"] for t in rigs},{0})

    def test_v3_replacements_fence_old_paid_parts_and_old_camera_runs(self):
        plan=self.plan
        self.assertEqual(len(q.V3_REPLACED_SHOTS),11)
        old_parts=[t for t in plan["tasks"] if t["kind"]=="image"
                   and t["shot_id"] in q.V3_REPLACED_SHOTS]
        self.assertTrue(old_parts)
        self.assertTrue(all(t["status"]!="ready_for_preflight" for t in old_parts))
        self.assertTrue(any("V3" in t["reason"] for t in old_parts))
        candidate=next(t for t in plan["tasks"]
            if t["kind"]=="camera_preview" and t["shot_id"]=="C08-P03")
        env={"GH_TOKEN":"offline-test","GITHUB_TOKEN":"offline-test",
             "GITHUB_REPOSITORY":"HelioConde/VideoForge-IA",
             "GITHUB_REF":"refs/heads/main","GITHUB_RUN_ID":"999"}
        with patch.dict("os.environ",env), patch.object(q,"QueueRemote",FakeRemote):
            with patch.object(q,"dispatch_child",side_effect=AssertionError("old V2 preview must never run")):
                result=q.run_remote({"tasks":[candidate]},0,1)
        self.assertEqual(result["processed_camera_previews"],0)
        self.assertEqual(result["external_workflow_dispatch_calls"],0)

    def test_branch_state_schema_does_not_accept_fake_completed_or_publishing(self):
        q.QueueRemote._validate_snapshot({
            "schema_version":1,"schema":q.STATE_SCHEMA,"attempts":{}})
        for state in ("success_fake","youtube_published","approved_rig","completed_by_planning"):
            with self.subTest(state=state),self.assertRaises(ValueError):
                q.QueueRemote._validate_snapshot({
                    "schema_version":1,"schema":q.STATE_SCHEMA,
                    "attempts":{"bad":{"status":state,"workflow":q.IMAGE_WORKFLOW}}})

    def test_verified_one_image_then_camera_dispatch_are_reserved_before_external_calls(self):
        image=next(t for t in self.plan["tasks"]
                   if t["kind"]=="image" and t["status"]=="ready_for_preflight")
        preview=next(t for t in self.plan["tasks"]
                     if t["kind"]=="camera_preview")
        portion={"tasks":[image,preview]}
        order=[]
        def dispatch(t):
            order.append(("dispatch",t["task_id"]))
            self.assertEqual(FakeRemote.writes[-1]["attempts"][t["task_id"]]["status"],
                             "reserved")
            return 8231 if t["kind"]=="image" else 8232
        def after(t,run):
            order.append(("verify",t["task_id"]))
            if t["kind"]=="image":
                return {"status":"archived","sha256":"a"*64,
                        "source_file":"archived-real-file.png"}
            return {"status":"preview_complete","artifact_id":12345,
                    "technical_camera_only":True,"animation_rig_approved":False}
        env={"GH_TOKEN":"offline-test","GITHUB_TOKEN":"offline-test",
             "GITHUB_REPOSITORY":"HelioConde/VideoForge-IA",
             "GITHUB_REF":"refs/heads/main","GITHUB_RUN_ID":"999"}
        with patch.dict("os.environ",env):
            with patch.object(q,"QueueRemote",FakeRemote):
                with patch.object(q.parts,"existing_part",return_value=None):
                    with patch.object(q.parts,"prepare",return_value={
                        "mother_proof":{"sha256":image["source_sha256"]}}):
                        with patch.object(q,"dispatch_child",side_effect=dispatch):
                            with patch.object(q,"verify_child",side_effect=after):
                                with patch.object(q,"gh",return_value=""):
                                    result=q.run_remote(portion,1,1)
                                    self.assertEqual(result["processed_images"],1)
                                    self.assertEqual(result["processed_camera_previews"],1)
                                    self.assertEqual(result["external_workflow_dispatch_calls"],2)
                                    self.assertEqual([v["status"] for v in result["executed"]],
                                                     ["archived","preview_complete"])
                                    self.assertFalse(result["human_visual_approval"])
                                    self.assertEqual(result["youtube_publications"],0)
                                    self.assertEqual(
                                        [t[0] for t in order],
                                        ["dispatch","verify","dispatch","verify"])
                                    before=len(FakeRemote.writes)
                                    again=q.run_remote(portion,1,1)
                                    self.assertEqual(again["executed"],[])
                                    self.assertEqual(len(FakeRemote.writes),before)

    def test_uncertain_external_call_is_permanently_fenced_without_replay(self):
        image=next(t for t in self.plan["tasks"]
                   if t["kind"]=="image" and t["status"]=="ready_for_preflight")
        portion={"tasks":[image]}
        env={"GH_TOKEN":"offline-test","GITHUB_TOKEN":"offline-test",
             "GITHUB_REPOSITORY":"HelioConde/VideoForge-IA",
             "GITHUB_REF":"refs/heads/main","GITHUB_RUN_ID":"999"}
        with patch.dict("os.environ",env),patch.object(q,"QueueRemote",FakeRemote):
            with patch.object(q.parts,"existing_part",return_value=None):
                with patch.object(q.parts,"prepare",return_value={
                    "mother_proof":{"sha256":image["source_sha256"]}}):
                    with patch.object(q,"dispatch_child",side_effect=RuntimeError("uncertain")) as send:
                        with self.assertRaisesRegex(RuntimeError,"NO_RETRY"):
                            q.run_remote(portion,1,0)
                        self.assertEqual(send.call_count,1)
                        self.assertEqual(FakeRemote.shared["attempts"][image["task_id"]]["status"],
                                         "blocked_uncertain")
                        with self.assertRaisesRegex(RuntimeError,"UNRESOLVED_EXTERNAL_ATTEMPT"):
                            q.run_remote(portion,1,0)
                        self.assertEqual(send.call_count,1)

    def test_verified_rejected_child_is_not_retried_and_does_not_stop_next_task(self):
        images=[t for t in self.plan["tasks"]
                if t["kind"]=="image" and t["status"]=="ready_for_preflight"][:2]
        self.assertEqual(len(images),2)
        env={"GH_TOKEN":"offline-test","GITHUB_TOKEN":"offline-test",
             "GITHUB_REPOSITORY":"HelioConde/VideoForge-IA",
             "GITHUB_REF":"refs/heads/main","GITHUB_RUN_ID":"999"}
        called=[]
        def send(task):
            called.append(task["task_id"])
            return 2001 if len(called)==1 else 2002
        def fake_reconcile(plan,remote,ledger):
            task=images[0]["task_id"]
            if ledger["attempts"].get(task,{}).get("status")=="blocked_failed":
                ledger["attempts"][task].update(
                    status="rejected_archived",
                    technical_qa="rejected_canvas_mismatch_no_pixel_resizing")
                remote.save(ledger)
                return [task]
            return []
        def watcher(*args,**kwargs):
            if args[:2]==("run","watch") and args[2]=="2001":
                raise RuntimeError("verified rejected PNG child")
            return ""
        with patch.dict("os.environ",env),patch.object(q,"QueueRemote",FakeRemote):
            with patch.object(q.parts,"existing_part",return_value=None):
                with patch.object(q.parts,"prepare",side_effect=lambda shot,part:{
                    "mother_proof":{"sha256":next(t["source_sha256"] for t in images
                        if t["shot_id"]==shot and t["part"]==part)}}):
                    with patch.object(q,"dispatch_child",side_effect=send):
                        with patch.object(q,"reconcile_rejected_archives",side_effect=fake_reconcile):
                            with patch.object(q,"reload_main"):
                                with patch.object(q,"gh",side_effect=watcher):
                                    with patch.object(q,"verify_child",return_value={
                                        "status":"archived","sha256":"a"*64,
                                        "source_file":"verified.png"}):
                                        result=q.run_remote({"tasks":images},2,0)
        self.assertEqual(len(called),2)
        self.assertEqual(result["processed_images"],2)
        self.assertEqual([x["status"] for x in result["executed"]],
                         ["rejected_archived","archived"])
        self.assertEqual(FakeRemote.shared["attempts"][images[0]["task_id"]]["status"],
                         "rejected_archived")

    def test_proven_preflight_failure_is_terminal_block_without_provider_replay(self):
        task=next(t for t in self.plan["tasks"]
                  if t["kind"]=="image" and t["status"]=="ready_for_preflight")
        key=task["task_id"]
        record={"status":"blocked_failed","workflow":q.IMAGE_WORKFLOW,
                "source_sha256":task["source_sha256"],"child_run_id":44535994724}
        ledger={"schema_version":1,"schema":q.STATE_SCHEMA,
                "attempts":{key:record}}
        class Remote:
            def save(self, data):
                q.QueueRemote._validate_snapshot(data)
        steps=[
            {"name":"Validar 39 planos, PNG-mãe e componente sem pagar proxy",
             "conclusion":"failure"},
            {"name":"Gerar uma imagem NOVA pelo proxy sem recortar a mae",
             "conclusion":"skipped"},
        ]
        def api(*args,**kwargs):
            route=args[1]
            if route.endswith("/jobs"):
                return {"jobs":[{"name":"gerar-imagem-separada","steps":steps}]}
            if route.endswith("/artifacts"):
                return {"total_count":0,"artifacts":[]}
            return {"conclusion":"failure","event":"workflow_dispatch",
                    "head_branch":"main",
                    "path":".github/workflows/"+q.IMAGE_WORKFLOW}
        with patch.object(q.parts,"existing_part",return_value=None):
            with patch.object(q,"gh",side_effect=api) as http:
                changed=q.reconcile_failed_preflight(
                    {"tasks":[task]},Remote(),ledger)
        self.assertEqual(changed,[key])
        self.assertEqual(record["status"],"blocked_preflight")
        self.assertEqual(record["provider_calls_confirmed"],0)
        self.assertFalse(record["retry_original_task"])
        self.assertEqual(http.call_count,3)

    def test_uncertain_failed_child_cannot_be_marked_preflight(self):
        task=next(t for t in self.plan["tasks"]
                  if t["kind"]=="image" and t["status"]=="ready_for_preflight")
        entry={"status":"blocked_failed","workflow":q.IMAGE_WORKFLOW,
               "source_sha256":task["source_sha256"],"child_run_id":44535994724}
        ledger={"schema_version":1,"schema":q.STATE_SCHEMA,
                "attempts":{task["task_id"]:entry}}
        class Remote:
            def save(self, data):
                raise AssertionError("Uncertain failure must not be reconciled")
        def api(*args,**kwargs):
            route=args[1]
            if route.endswith("/jobs"):
                return {"jobs":[{"name":"gerar-imagem-separada","steps":[
                    {"name":"Validar 39 planos, PNG-mãe e componente sem pagar proxy",
                     "conclusion":"success"},
                    {"name":"Gerar uma imagem NOVA pelo proxy sem recortar a mae",
                     "conclusion":"failure"}]}]}
            return {"conclusion":"failure","event":"workflow_dispatch",
                    "head_branch":"main","path":".github/workflows/"+q.IMAGE_WORKFLOW}
        with patch.object(q.parts,"existing_part",return_value=None),patch.object(q,"gh",side_effect=api):
            self.assertEqual(q.reconcile_failed_preflight(
                {"tasks":[task]},Remote(),ledger),[])
        self.assertEqual(entry["status"],"blocked_failed")

    def test_fail_closed_policy_and_invalid_ref(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(Exception):
                q.policy_guard(Path(p))
        with self.assertRaises(ValueError):
            q.id_for("image","C08-P02","object bad","a"*64)

    def test_child_dispatch_ignores_concurrent_unrelated_run(self):
        task=next(t for t in self.plan["tasks"]
                  if t["kind"]=="image" and t["status"]=="ready_for_preflight")
        sent=[]
        def fake_gh(*args,**kwargs):
            self.assertEqual(args[:2],("workflow","run"))
            sent.append(next(v.split("=",1)[1] for v in args
                             if v.startswith("dispatch_token=")))
            return ""
        def runs(_workflow):
            previous={"databaseId":100,"displayTitle":"earlier manual run"}
            if not sent:
                return [previous]
            return [previous,
                    {"databaseId":101,"displayTitle":"EP01 PNG separado C01-P01 / manual"},
                    {"databaseId":102,"displayTitle":"EP01 PNG separado "+task["shot_id"]+" / "+sent[0]}]
        with patch.dict("os.environ",{"GITHUB_RUN_ID":"999"},clear=False):
            with patch.object(q,"gh",side_effect=fake_gh),patch.object(q,"child_runs",side_effect=runs):
                result=q.dispatch_child(task)
        self.assertEqual(result,102)
        self.assertEqual(len(sent),1)
        self.assertRegex(sent[0],r"^vfq-[0-9a-f]{20}$")

    def test_child_dispatch_camera_uses_correlated_token(self):
        task=next(t for t in self.plan["tasks"] if t["kind"]=="camera_preview")
        sent=[]
        def fake_gh(*args,**kwargs):
            sent.append(next(v.split("=",1)[1] for v in args
                             if v.startswith("dispatch_token=")))
            self.assertIn("revision=continuity-v2",args)
            return ""
        def runs(_workflow):
            if not sent:
                return []
            return [{"databaseId":201,"displayTitle":"EP01 camera preview C01-P01 / manual"},
                    {"databaseId":202,"displayTitle":"EP01 camera preview "+task["shot_id"]+
                     " / continuity-v2 / "+sent[0]}]
        with patch.dict("os.environ",{"GITHUB_RUN_ID":"999"},clear=False):
            with patch.object(q,"gh",side_effect=fake_gh),patch.object(q,"child_runs",side_effect=runs):
                self.assertEqual(q.dispatch_child(task),202)

    def test_ambiguous_correlated_child_runs_fail_closed(self):
        task=next(t for t in self.plan["tasks"]
                  if t["kind"]=="image" and t["status"]=="ready_for_preflight")
        token=[]
        def fake_gh(*args,**kwargs):
            token.append(next(v.split("=",1)[1] for v in args
                              if v.startswith("dispatch_token=")))
            return ""
        def runs(_workflow):
            if not token:
                return []
            return [{"databaseId":301,"displayTitle":"A / "+token[0]},
                    {"databaseId":302,"displayTitle":"B / "+token[0]}]
        with patch.dict("os.environ",{"GITHUB_RUN_ID":"999"},clear=False):
            with patch.object(q,"gh",side_effect=fake_gh),patch.object(q,"child_runs",side_effect=runs):
                with self.assertRaisesRegex(RuntimeError,"Ambiguous correlated"):
                    q.dispatch_child(task)

    def test_child_run_listing_requires_display_title(self):
        with patch.object(q,"gh",return_value=[{"databaseId":1}]):
            with self.assertRaisesRegex(ValueError,"untraceable"):
                q.child_runs(q.IMAGE_WORKFLOW)
        with patch.object(q,"gh",return_value=[{"databaseId":1,"displayTitle":"run"}]) as api:
            self.assertEqual(q.child_runs(q.IMAGE_WORKFLOW)[0]["databaseId"],1)
            self.assertIn("databaseId,displayTitle,status,conclusion,createdAt",api.call_args.args)


if __name__=="__main__":
    unittest.main()
