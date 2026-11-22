"""E2E: six actual technical executors, persistent checkpoints and truthful QA."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from orchestrator import ep01_specialist_dispatch as d
from orchestrator.runtime_store import Store


class SixSpecialistsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="vf-six-specialists-")
        cls.db=Path(cls.tmp.name)/"six.sqlite"
        cls.outputs=Path(cls.tmp.name)/"output"
        cls.store=Store(cls.db)
        cls.first=d.run(cls.store,cls.outputs)
        cls.snapshot=cls.store.export_snapshot()

    @classmethod
    def tearDownClass(cls):
        cls.store.close()
        cls.tmp.cleanup()

    def test_six_independent_specialists_execute_real_files(self):
        report=self.first
        self.assertEqual(len(report["tasks"]),6)
        self.assertEqual(report["specialist_dispatch"]["technical_completed"],6)
        self.assertEqual(report["specialist_dispatch"]["completed_roles"],
                         list(sorted(d.RUN_SEQUENCE)))
        self.assertEqual(report["specialist_dispatch"]["model_calls"],0)
        self.assertEqual(report["specialist_dispatch"]["new_images"],0)
        self.assertEqual(report["specialist_dispatch"]["youtube_publications"],0)
        self.assertEqual(report["usage"],[])
        self.assertEqual(len(report["checkpoints"]),6)
        for task in report["tasks"]:
            cp=next(x for x in report["checkpoints"] if x["task_id"]==task["task_id"])
            with self.subTest(agent=task["owner"]):
                self.assertEqual(task["status"],"completed")
                self.assertEqual(cp["result_sha256"],task["result_sha256"])
                self.assertEqual(cp["review"]["agent_id"],"12")
                self.assertTrue(cp["review"]["technical_passed"])
                self.assertFalse(cp["human_visual_approval"])
                real=self.store.result(task["task_id"])
                self.assertFalse(real["human_visual_approval"])
                self.assertFalse(real["youtube_publication"])
                self.assertTrue(d.independent_qa(
                    real["evidence"],self.outputs/task["task_id"],task["owner"]))

    def test_all_six_outputs_are_archived_and_11_is_real_90_frame_tech_mp4(self):
        for role in d.RUN_SEQUENCE:
            task=next(x for x in self.first["tasks"] if x["owner"]==role)
            result=self.store.result(task["task_id"])["evidence"]
            self.assertGreater(len(result["outputs_sha256"]),0)
            for filename,digest in result["outputs_sha256"].items():
                p=self.outputs/task["task_id"]/filename
                self.assertTrue(p.is_file())
                self.assertEqual(d.sha(p),digest)
        role11=next(t for t in self.first["tasks"] if t["owner"]=="11")
        root=self.outputs/role11["task_id"]
        qa=json.loads((root/"11-media-technical-preview-QA.json").read_text())
        self.assertEqual(qa["frames"],90)
        self.assertFalse(qa["rig_animation"])
        self.assertFalse(qa["audio_included"])
        self.assertFalse(qa["final_episode"])
        self.assertFalse(qa["youtube_published"])
        self.assertGreater((root/"11-c08-p02-tech-preview-NOT-FINAL.mp4").stat().st_size,10000)

    def test_historical_versions_do_not_inflate_current_six_or_get_claimed(self):
        # Reproduce the live CAS ledger: older completed versions plus a stale
        # ready one must never count as current work or be executed again.
        from orchestrator.agent_bus import fingerprint
        with tempfile.TemporaryDirectory(prefix="vf-historic-versions-") as tmp:
            store=Store(Path(tmp)/"history.sqlite")
            try:
                store.import_snapshot(self.snapshot)
                for role,status in (("08","completed"),("09","completed"),("11","ready")):
                    task=next(t for t in self.first["tasks"] if t["owner"]==role)
                    source=store.db.execute(
                        "SELECT payload,revision FROM tasks WHERE task_id=?",
                        (task["task_id"],)).fetchone()
                    old=json.loads(source["payload"])
                    old["task_id"]=f"EP01-REAL-TECH-AG{role}-historical"
                    old["status"]=status
                    old.pop("lease",None)
                    old.pop("attempt_id",None)
                    old.pop("phase",None)
                    store.db.execute("INSERT INTO tasks(task_id,payload,revision) VALUES (?,?,?)",
                                     (old["task_id"],json.dumps(old),source["revision"]))
                    if status=="completed":
                        cp_row=store.db.execute(
                            "SELECT content FROM checkpoints WHERE task_id=?",
                            (task["task_id"],)).fetchone()
                        cp=json.loads(cp_row["content"])
                        cp["task_id"]=old["task_id"]
                        store.db.execute(
                            "INSERT INTO checkpoints(task_id,content,sha256) VALUES (?,?,?)",
                            (old["task_id"],json.dumps(cp),fingerprint(cp)))
                outcome=d.run(store,Path(tmp)/"output")
                summary=outcome["specialist_dispatch"]
                self.assertEqual(summary["historical_task_versions"],3)
                self.assertEqual(summary["historical_completed"],2)
                self.assertEqual(summary["technical_completed"],6)
                self.assertEqual(summary["new_task_ids"],[])
                self.assertEqual(summary["steps"],[])
                self.assertEqual(len(outcome["tasks"]),6)
                self.assertEqual(len(outcome["checkpoints"]),6)
                self.assertEqual(store.get("EP01-REAL-TECH-AG11-historical")["status"],"ready")
                from orchestrator import agent_activity, durable_dispatch, runtime
                with tempfile.TemporaryDirectory() as td:
                    audit=Store(Path(td)/"audit.sqlite")
                    try:
                        base=durable_dispatch.run(audit,max_tasks=4)
                    finally:
                        audit.close()
                queue=json.loads((runtime.ROOT/"orchestrator/tasks.json").read_text())
                dashboard=agent_activity.make_status(
                    base,queue,None,run_id=1234,now="2026-11-22T10:00:00+00:00",
                    specialists=outcome)
                self.assertEqual(dashboard["six_role_technical_execution"]["technical_completed"],6)
            finally:
                store.close()

    def test_reopen_is_idempotent_no_new_task_no_new_renders(self):
        again=d.run(self.store,self.outputs)
        self.assertEqual(again["specialist_dispatch"]["new_task_ids"],[])
        self.assertEqual(again["specialist_dispatch"]["steps"],[])
        self.assertEqual(again["state_sha256"],self.first["state_sha256"])
        reopened=Store(Path(self.tmp.name)/"reopened.sqlite")
        try:
            reopened.import_snapshot(self.snapshot)
            retry=d.run(reopened,self.outputs)
            self.assertEqual(retry["specialist_dispatch"]["new_task_ids"],[])
            self.assertEqual(retry["specialist_dispatch"]["steps"],[])
            self.assertEqual(retry["state_sha256"],self.first["state_sha256"])
        finally:
            reopened.close()

    def test_independent_QA_rejects_fake_approval_or_missing_output(self):
        task=next(t for t in self.first["tasks"] if t["owner"]=="06")
        evidence=self.store.result(task["task_id"])["evidence"]
        root=self.outputs/task["task_id"]
        for bad in ["fake_visual_approval","falsified_sha","pretend_image_generation",
                    "pretend_youtube"]:
            mutated=deepcopy(evidence)
            if bad=="fake_visual_approval":
                mutated["human_visual_approval"]=True
            if bad=="falsified_sha":
                p=next(iter(mutated["outputs_sha256"]))
                mutated["outputs_sha256"][p]="0"*64
            if bad=="pretend_image_generation":
                mutated["new_generated_image_calls"]=1
            if bad=="pretend_youtube":
                mutated["youtube_publication"]=True
            with self.subTest(case=bad):
                self.assertFalse(d.independent_qa(mutated,root,"06"))

    def test_sources_are_version_pinned_and_refuse_mutation(self):
        ref=next(iter(self.first["tasks"][0]["input_refs"]))
        original=self.first["tasks"][0]["input_refs"][ref]
        with self.assertRaises(Exception):
            d.pinned_file(d.ROOT,ref,expected="0"*64)
        self.assertEqual(d.pinned_file(d.ROOT,ref),original)

    def test_six_verified_roles_appear_on_public_twelve_agent_dashboard(self):
        from orchestrator import agent_activity, durable_dispatch, runtime
        with tempfile.TemporaryDirectory(prefix="vf-old-four-") as tmp:
            earlier=Store(Path(tmp)/"four.sqlite")
            try:
                old=durable_dispatch.run(earlier,max_tasks=4)
            finally:
                earlier.close()
        queue=json.loads((runtime.ROOT/"orchestrator/tasks.json").read_text())
        status=agent_activity.make_status(
            old,queue,None,run_id=9999,now="2026-11-19T12:00:00+00:00",
            specialists=self.first)
        self.assertEqual(len(status["agents"]),12)
        self.assertEqual(status["six_role_technical_execution"]["technical_completed"],6)
        self.assertEqual(status["technical_dispatch"]["source_audits_completed"],4)
        self.assertTrue(status["agents"][10]["technical_preview_created"])
        self.assertFalse(status["mp4_final_ready"])
        self.assertEqual(status["youtube_publications"],0)
        self.assertTrue(all(status["agents"][int(role)-1]["checkpoint_sha256"]
                            for role in d.RUN_SEQUENCE))
        body=agent_activity.render_markdown(status)
        self.assertIn("**6/6**",body)
        self.assertIn("MP4 TECNICO",body)
        self.assertIn("nao equivalem a novos pedidos Astra",body)
        forged=deepcopy(self.first)
        item=next(t for t in forged["tasks"] if t["owner"]=="11")
        item["status"]="completed"
        cp=next(c for c in forged["checkpoints"] if c["task_id"]==item["task_id"])
        cp["review"]["technical_passed"]=False
        with self.assertRaises(ValueError):
            agent_activity.make_status(old,queue,None,run_id=9999,now="test",
                                       specialists=forged)

    def test_run_only_claims_allowed_roles_and_stores_no_credentials(self):
        all_roles={x["owner"] for x in self.first["tasks"]}
        self.assertEqual(all_roles,set(d.RUN_SEQUENCE))
        self.assertEqual({x["reviewer"] for x in self.first["tasks"]},{"12"})
        data=json.dumps(self.snapshot)
        self.assertNotIn("github_pat_",data)
        self.assertNotIn("sk-proj-",data)
        self.assertNotIn("Bearer ",data)
        self.assertNotIn("github_token",data.lower())


if __name__=="__main__":
    unittest.main()
