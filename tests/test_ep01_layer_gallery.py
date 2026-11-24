import hashlib
import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from scripts import ep01_action_production_queue as q
from scripts.ep01_layer_gallery import gallery, feedback_state, feedback_snapshot


class GalleryTests(unittest.TestCase):
    def test_preview_requires_the_archived_bytes_and_preserves_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = q.EP / "assets" / "layer.png"
            (root/path).parent.mkdir(parents=True)
            Image.new("RGBA", (4, 4), (50, 40, 20, 120)).save(root/path)
            task = dict(task_id="one", kind="image", shot_id="C01-P05", owner="05",
                        part="guarda", status="ready_for_preflight")
            receipt = dict(status="rejected_archived", child_run_id=123, source_file=path.as_posix(),
                           technical_qa="rejected_canvas_mismatch_no_pixel_resizing",
                           sha256=q.digest(root/path))
            result = gallery([task], {"one":receipt}, root)
            self.assertIn("data:image/png;base64,", result)
            self.assertIn("rejected_canvas_mismatch", result)
            self.assertIn("/runs/123", result)
            receipt["sha256"] = "0"*64
            self.assertNotIn("data:image/png", gallery([task], {"one":receipt}, root))

    def test_public_dashboard_replaces_previous_active_child(self):
        body="<!-- videoforge-ep01-production-queue:v1 -->\n# EP01\n<!-- ep01-active-child -->old"
        observed=[]
        def fake_gh(*args, **kwargs):
            if args[0]=="api":
                return {"body":body,"state":"open"}
            observed.append(Path(args[-1]).read_text(encoding="utf8"))
        with patch.dict("os.environ", EP01_SHOW_ACTIVE_CHILD="true"), patch.object(q,"gh",side_effect=fake_gh):
            q.publish_active_child({"owner":"05","shot_id":"C01-P05","part":"guard"},123)
        self.assertEqual(observed[0].count("<!-- ep01-active-child -->"),1)
        self.assertIn("Agente 05",observed[0])
        self.assertIn("/actions/runs/123",observed[0])

    def test_success_cannot_credit_another_child_or_mother(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "123" / "layer.png"
            path.parent.mkdir()
            path.write_bytes(b"archived fixture")
            meta = dict(technical_qa="candidate_minor_edge_delta_requires_alignment_qa",
                        source_mother_sha256="a"*64)
            path.with_suffix(".production.json").write_text(json.dumps(meta))
            item = dict(file="123/layer.png", sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            task = dict(kind="image", shot_id="C01-P05", part="guard", source_sha256="a"*64)
            with patch.object(q, "ROOT", root), patch.object(q, "reload_main"), patch.object(q.parts, "existing_part", return_value=item):
                self.assertEqual(q.verify_child(task, 123)["status"], "archived")
                with self.assertRaises(ValueError):
                    q.verify_child(task, 124)
                with self.assertRaises(ValueError):
                    q.verify_child(dict(task,source_sha256="b"*64), 123)


    def test_current_restrictions_survive_old_success_receipts(self):
        for status in ("blocked_reference_revision", "blocked_repeated_canvas_mismatch",
                       "archived_version_check_needed", "archived_rejected_needs_review",
                       "blocked_waiting_for_verified_rgba_and_rig"):
            with self.subTest(status=status):
                task = dict(status=status, reason="Current mother requires review")
                state = feedback_state(task, dict(status="archived", technical_qa="old_candidate"))
                self.assertEqual(state, dict(status=status, reason=task["reason"]))

    def test_receipt_must_match_current_source_before_claiming_completion(self):
        task = dict(status="ready_for_preflight", reason="", source_sha256="a"*64)
        for source in (None, "b"*64):
            with self.subTest(source=source):
                state = feedback_state(task, dict(status="archived", source_sha256=source))
                self.assertEqual(state["status"], "blocked_receipt_source_mismatch")
        self.assertEqual(feedback_state(task, dict(status="archived", source_sha256="a"*64))["status"],
                         "archived")
        self.assertEqual(feedback_state(task, {})["status"], "ready_for_preflight")

    def test_unresolved_receipt_is_not_promoted_to_ready(self):
        task = dict(status="ready_for_preflight", source_sha256="a"*64)
        for status in ("reserved", "dispatched", "blocked_uncertain", "blocked_failed"):
            with self.subTest(status=status):
                self.assertEqual(feedback_state(task, dict(status=status, source_sha256="a"*64))["status"],
                                 status)

    def test_gallery_shows_current_block_and_historical_archive_separately(self):
        task = dict(task_id="one", kind="image", shot_id="C01-P03", owner="05",
                    status="archived_version_check_needed", reason="V3 replaced the mother")
        receipt = dict(status="archived", technical_qa="candidate_old_V2", child_run_id=123)
        result = gallery([task], {"one": receipt})
        self.assertIn("archived_version_check_needed", result)
        self.assertIn("V3 replaced the mother", result)
        self.assertIn("Registro histórico: archived", result)
        self.assertIn("/runs/123", result)
        self.assertEqual(receipt["status"], "archived")

    def test_snapshot_does_not_modify_ledger_or_accept_duplicate_tasks(self):
        tasks = [dict(task_id="one", status="blocked_reference_revision", reason="V3")]
        attempts = {"one": dict(status="archived")}
        before = deepcopy((tasks, attempts))
        self.assertEqual(feedback_snapshot(tasks, attempts)["states"]["one"]["status"],
                         "blocked_reference_revision")
        self.assertEqual((tasks, attempts), before)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            feedback_snapshot(tasks*2, attempts)

    def run_dashboard(self, completed_batch, unsafe=False):
        """Execute the actual workflow JS with local fixture files and fake GitHub."""
        workflow = (q.ROOT / ".github/workflows/ep01-image-animation-action-queue.yml").read_text()
        raw = workflow.rsplit("          script: |", 1)[1].split("\n      - name:", 1)[0]
        source = "\n".join(line[12:] if line.startswith("            ") else line
                           for line in raw.splitlines())
        tasks = [
            dict(task_id="mother", kind="mother", shot_id="C11-P01", part=None,
                 owner="05", status="not_required", reason="", source_sha256="a"*64),
            dict(task_id="next", kind="image", shot_id="C11-P01", part="character-kael",
                 owner="05", status="ready_for_preflight", reason="", source_sha256="a"*64),
            dict(task_id="done", kind="image", shot_id="C11-P01", part="object-broche",
                 owner="05", status="ready_for_preflight", reason="", source_sha256="a"*64),
        ]
        plan = {"queue": dict(schema=q.SCHEMA, shots=42, original_image_requests=146,
                             total_tasks=276, per_child_paid_image_cap=1,
                             youtube_publication=False, rig_approval_automatic=False, tasks=tasks)}
        ledger = dict(schema=q.STATE_SCHEMA, schema_version=1, attempts={
            "done": dict(status="archived", source_sha256="a"*64, child_run_id=321)})
        encoded = json.dumps(ledger)
        harness = """
const ledger=LEDGER;
let published=null;
const context={repo:{owner:'HelioConde',repo:'VideoForge-IA'},runId:999,job:'offline'};
const github={rest:{
  repos:{getContent:async()=>({data:{content:Buffer.from(JSON.stringify(ledger)).toString('base64')}})},
  actions:{listWorkflowRuns:async()=>({data:{workflow_runs:[]}})},
  issues:{
    get:async()=>({data:{state:'open',body:'<!-- videoforge-ep01-production-queue:v1 -->'}}),
    update:async(args)=>{published=args.body;}
  }
}};
const core={warning:()=>{},summary:{addRaw:()=>({write:async()=>{}})}};
(async()=>{
SOURCE
process.stdout.write(JSON.stringify(published));
})().catch(error=>{process.stderr.write(error.message);process.exitCode=1;});
""".replace("LEDGER", encoded).replace("SOURCE", source)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            initial = root/"plan.json"
            execution = root/"run.json"
            initial.write_text(json.dumps(plan))
            if completed_batch:
                final = deepcopy(plan)
                final["queue"]["tasks"][1].update(
                    status="blocked_repeated_canvas_mismatch", reason="Two canvas failures in this batch")
                final["execution"] = dict(processed_images=1, processed_camera_previews=0,
                                          youtube_publications=0, human_visual_approval=unsafe,
                                          rig_ready=False)
                execution.write_text(json.dumps(final))
            result = subprocess.run(["node", "-e", harness], cwd=q.ROOT,
                env={**os.environ, "PLAN_FILE":str(initial), "RUN_FILE":str(execution),
                     "RUNNER_TEMP":tmp}, text=True, capture_output=True, timeout=45)
            html = (root/"ep01-camadas.html").read_text() if (root/"ep01-camadas.html").exists() else ""
        return result, html

    def test_dashboard_and_gallery_use_final_batch_block_and_same_counts(self):
        result, html = self.run_dashboard(True)
        self.assertEqual(result.returncode, 0, result.stderr)
        body = json.loads(result.stdout)
        self.assertIn("2 solicitacoes, 0 candidatas a preflight, 1 bloqueadas", body)
        self.assertIn("0 prontas para pré-verificação; 1 bloqueadas", body)
        self.assertIn("Two canvas failures in this batch", body)
        self.assertIn("blocked_repeated_canvas_mismatch", html)

    def test_dashboard_plan_only_keeps_ledger_progress_in_both_counts(self):
        result, html = self.run_dashboard(False)
        self.assertEqual(result.returncode, 0, result.stderr)
        body = json.loads(result.stdout)
        self.assertIn("2 solicitacoes, 1 candidatas a preflight, 0 bloqueadas", body)
        self.assertIn("1 prontas para pré-verificação; 0 bloqueadas", body)
        self.assertNotIn("blocked_repeated_canvas_mismatch", html)

    def test_dashboard_rejects_fabricated_approval_before_writing_feedback(self):
        result, html = self.run_dashboard(True, unsafe=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unexpected approval or publishing", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(html, "")
