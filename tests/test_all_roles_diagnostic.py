"""Real EP01 source reads; diagnostic completion never implies media production."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestrator.all_roles_diagnostic import SPECIALISTS, diagnostic, run, seed, worker_step
from orchestrator.agent_bus import ROLES
from orchestrator.runtime import ROOT
from orchestrator.runtime_store import Store


class AllRolesDiagnosticTests(unittest.TestCase):
    def test_ten_specialists_coordinate_with_01_and_independent_12(self):
        original = (ROOT / "orchestrator/tasks.json").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "roles.sqlite")
            try:
                first = run(store)
                info = first["role_diagnostic"]
                self.assertEqual(info["diagnostic_completed_count"], 10)
                self.assertEqual(info["blocked_task_ids"], [])
                self.assertEqual(set(info["roles_covered"]), set(ROLES))
                self.assertEqual(len(info["steps"]), 20)
                self.assertEqual(len(first["checkpoints"]), 10)
                self.assertTrue(all(t["status"] == "completed" for t in first["tasks"]))
                self.assertFalse(info["production_ready"])
                self.assertEqual(info["media_created"], 0)
                self.assertEqual(info["model_calls"], 0)
                self.assertEqual(info["youtube_publications"], 0)
                reports = [store.result(t["task_id"]) for t in first["tasks"]]
                self.assertEqual({r["agent_id"] for r in reports}, set(SPECIALISTS))
                self.assertEqual(len({r["evidence"]["focus"] for r in reports}), 10)
                self.assertTrue(all(r["evidence"]["diagnostic_completed"] for r in reports))
                self.assertTrue(all(not r["evidence"]["production_ready"] for r in reports))
                self.assertTrue(all(r["evidence"]["production_blockers"] for r in reports))
                self.assertTrue(all(cp["review"]["agent_id"] == "12"
                                    and cp["review"]["technical_passed"] is True
                                    and cp["human_visual_approval"] is False
                                    for cp in first["checkpoints"]))
                later = run(store)
                self.assertEqual(later["role_diagnostic"]["created"], [])
                self.assertEqual(later["role_diagnostic"]["steps"], [])
                self.assertEqual(first["state_sha256"], later["state_sha256"])
            finally:
                store.close()
        self.assertEqual(original, (ROOT / "orchestrator/tasks.json").read_bytes())

    def test_producer_result_mismatch_is_blocked_by_independent_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "roles.sqlite")
            try:
                self.assertEqual(len(seed(store)), 10)
                produced = worker_step(store)
                self.assertEqual(produced["status"], "needs_review")
                original = diagnostic
                def mutated(task, root=ROOT):
                    evidence = original(task, root)
                    evidence["facts"]["tampered"] = True
                    return evidence
                with patch("orchestrator.all_roles_diagnostic.diagnostic", side_effect=mutated):
                    review = worker_step(store)
                self.assertEqual(review["status"], "blocked")
                self.assertEqual(review["blocked_reason"], "independent_review_rejected")
                self.assertFalse(store.checkpoint(review["task_id"])["review"]["technical_passed"])
            finally:
                store.close()

    def test_no_production_claims_for_missing_layers_and_rig(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "roles.sqlite")
            try:
                seed(store)
                tasks = {row["owner"]: row for row in
                         (store.get(row[0]) for row in
                          store.db.execute("SELECT task_id FROM tasks"))}
                for role in ("05", "06", "07", "08", "11"):
                    result = diagnostic(tasks[role])
                    self.assertTrue(result["production_blockers"])
                    self.assertFalse(result["production_ready"])
                    self.assertEqual(result["media_actions"], 0)
                    self.assertEqual(result["model_calls"], 0)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
