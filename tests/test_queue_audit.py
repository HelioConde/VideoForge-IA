import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from queue_audit import audit

class QueueAuditTests(unittest.TestCase):
    def test_existing_queue_read_only(self):
        path = Path(__file__).resolve().parents[1] / "orchestrator/tasks.json"
        before = path.read_bytes()
        result = audit(path)
        self.assertEqual(path.read_bytes(), before)
        self.assertGreater(result["task_count"], 0)
        self.assertEqual(result["proxy_calls"], 0)
        self.assertFalse(result["dispatch_enabled"])

    def test_duplicate_and_self_review(self):
        task = {"task_id":"X", "owner":"diretor-cenas", "reviewer":"diretor-cenas", "status":"ready"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.json"
            path.write_text(json.dumps({"tasks":[task,task]}), encoding="utf-8")
            errors = audit(path)["errors"]
        self.assertTrue(any("Duplicate" in x for x in errors))
        self.assertTrue(any("self-review" in x for x in errors))

if __name__ == "__main__":
    unittest.main()
