import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"orchestrator"))
from multi_task_pilot import run, ART_ID, CONTINUITY_ID
ROOT=Path(__file__).resolve().parents[1]
class MultiTaskTests(unittest.TestCase):
    def test_dispatch_two_supported_tasks(self):
        q=ROOT/"orchestrator/tasks.json"
        before=q.read_bytes()
        result=run(q, ROOT)
        self.assertEqual(before,q.read_bytes())
        self.assertEqual({x["task_id"] for x in result["completed"]}, {ART_ID, CONTINUITY_ID})
        self.assertTrue(all(x["qa_passed"] for x in result["completed"]))
        self.assertFalse(result["queue_persisted"])
        self.assertEqual(result["proxy_calls"],0)
        self.assertFalse(result["ep01_visual_approval"])
    def test_unsupported_not_executed(self):
        q=ROOT/"orchestrator/tasks.json"
        result=run(q, ROOT, 1)
        self.assertEqual(len(result["completed"]),1)
        self.assertTrue(all(x["reason"]=="no_deterministic_worker_registered" for x in result["unsupported"]))
    def test_rejects_limit(self):
        with self.assertRaises(ValueError):
            run(ROOT/"orchestrator/tasks.json",ROOT,0)
if __name__=="__main__":
    unittest.main()
