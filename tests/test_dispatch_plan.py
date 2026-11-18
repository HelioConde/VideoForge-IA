import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from dispatch_plan import plan

class DispatchPlanTests(unittest.TestCase):
    def test_existing_queue_is_read_only(self):
        path = Path(__file__).resolve().parents[1] / "orchestrator/tasks.json"
        before = path.read_bytes()
        result = plan(path)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(result["worker_execution"])
        self.assertFalse(result["issue_creation"])
        self.assertEqual(result["ai_calls"], 0)
        self.assertTrue(all(not x["execute"] for x in result["candidates"]))

    def test_dependency_blocked(self):
        tasks = [
            {"task_id": "A", "owner": "diretor-cenas", "status": "ready",
             "reviewer": "supervisor-qa", "priority": "P0", "blocked_by": ["B"]},
            {"task_id": "B", "owner": "roteirista", "status": "needs_review",
             "reviewer": "supervisor-qa", "priority": "P0", "blocked_by": []},
        ]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "queue.json"
            p.write_text(json.dumps({"tasks": tasks}), encoding="utf-8")
            result = plan(p)
        self.assertEqual(result["candidate_count"], 0)
        self.assertEqual(result["dependency_blocked"][0]["task_id"], "A")

if __name__ == "__main__":
    unittest.main()
