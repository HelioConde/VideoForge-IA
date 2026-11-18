"""Local-only integration tests for durable safe multi-agent dispatch."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from orchestrator import durable_dispatch, runtime
from orchestrator.runtime_store import Store


class DurableDispatchTests(unittest.TestCase):
    def test_four_specialists_independent_review_persist_and_idempotency(self):
        source = runtime.ROOT / runtime.MANIFEST
        before = runtime.file_sha(source)
        queue = runtime.ROOT / "orchestrator/tasks.json"
        queue_before = queue.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            first_db = Path(tmp) / "dispatch.sqlite"
            store = Store(first_db)
            try:
                with patch("orchestrator.providers.urllib.request.build_opener") as transport:
                    result = durable_dispatch.run(store, max_tasks=4)
                    transport.assert_not_called()
                self.assertEqual(len(result["dispatch"]["new_task_ids"]), 4)
                self.assertEqual(result["dispatch"]["technical_completed"], 4)
                self.assertEqual(len(result["dispatch"]["steps"]), 8)
                self.assertEqual(result["dispatch"]["model_inference_requests"], 0)
                self.assertEqual(result["dispatch"]["image_requests"], 0)
                self.assertEqual(result["dispatch"]["youtube_publications"], 0)
                self.assertFalse(result["dispatch"]["visual_quality_approved"])
                self.assertEqual(len(result["checkpoints"]), 4)
                self.assertEqual(result["usage"], [])
                self.assertTrue(all(t["status"] == "completed" for t in result["tasks"]))
                self.assertEqual({t["owner"] for t in result["tasks"]},
                                 {"03", "04", "07", "10"})
                self.assertTrue(all(c["review"]["agent_id"] == "12"
                                    and c["review"]["technical_passed"]
                                    and c["human_visual_approval"] is False
                                    for c in result["checkpoints"]))
                self.assertTrue(all(c["scope"] == "read_only_technical_audit"
                                    for c in result["checkpoints"]))
                self.assertEqual(result["state_sha256"],
                                 durable_dispatch.run(store)["state_sha256"])
                snapshot = store.export_snapshot()
                reopened = Store(Path(tmp) / "reopened.sqlite")
                try:
                    reopened.import_snapshot(snapshot)
                    once_more = durable_dispatch.run(reopened)
                    self.assertEqual(once_more["dispatch"]["new_task_ids"], [])
                    self.assertEqual(once_more["dispatch"]["steps"], [])
                    self.assertEqual(once_more["state_sha256"], result["state_sha256"])
                    self.assertEqual(len(once_more["checkpoints"]), 4)
                finally:
                    reopened.close()
            finally:
                store.close()
        self.assertEqual(queue_before, queue.read_bytes())
        self.assertEqual(before, runtime.file_sha(source))

    def test_only_four_allowlisted_tasks_even_when_queue_has_other_ready_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "x.sqlite")
            try:
                added = durable_dispatch.select_and_seed(store)
                self.assertEqual(len(added), 4)
                self.assertTrue(all("-DURABLE-" in t for t in added))
                self.assertTrue(all(not any(denied in t for denied in [
                    "TARGETED-VISUAL-FIXES", "CREATOR-DECISION", "FINAL-MP4",
                    "FIVE-CHANNEL", "ROI-SEMANTICS"]) for t in added))
            finally:
                store.close()

    def test_mismatched_role_or_approval_is_rejected_before_enqueuing(self):
        source = json.loads((runtime.ROOT / "orchestrator/tasks.json").read_text())
        for change in [
            {"owner": "gerador-visual"},
            {"requires_human_approval": True},
            {"reviewer": "diretor-cenas"},
        ]:
            altered = json.loads(json.dumps(source))
            row = next(t for t in altered["tasks"] if t["task_id"] ==
                       "EP01-C07-C08-V2-CONTINUITY-AUDIT")
            row.update(change)
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "queue.json"
                path.write_text(json.dumps(altered))
                store = Store(Path(tmp) / "data.sqlite")
                try:
                    with self.assertRaisesRegex(ValueError, "Unsafe specialist assignment"):
                        durable_dispatch.select_and_seed(store, queue_path=path)
                    self.assertEqual(store.export_snapshot()["tables"]["usage"], [])
                finally:
                    store.close()

    def test_disabling_safety_contract_fails_closed(self):
        source = json.loads((runtime.ROOT / "orchestrator/tasks.json").read_text())
        source["dispatch_enabled"] = True
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "unsafe-queue.json"
            queue.write_text(json.dumps(source))
            store = Store(Path(tmp) / "data.sqlite")
            try:
                with self.assertRaisesRegex(ValueError, "Unsafe or malformed"):
                    durable_dispatch.select_and_seed(store, queue_path=queue)
            finally:
                store.close()

    def test_max_tasks_cannot_be_unbounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "data.sqlite")
            try:
                for invalid in (0, 5, -1, 200):
                    with self.subTest(max_tasks=invalid), self.assertRaises(ValueError):
                        durable_dispatch.run(store, max_tasks=invalid)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
