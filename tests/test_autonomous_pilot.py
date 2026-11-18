import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"orchestrator"))
from autonomous_pilot import run

ROOT=Path(__file__).resolve().parents[1]
class PilotTests(unittest.TestCase):
    def test_real_manifest_audit_without_mutation(self):
        path=ROOT/"orchestrator/tasks.json"
        original=path.read_bytes()
        result=run(path,ROOT)
        self.assertEqual(path.read_bytes(),original)
        self.assertEqual(result["agents_executed"],["01","03","12"])
        self.assertEqual(result["llm_agents_executed"],[])
        self.assertEqual(len(result["messages"]),3)
        self.assertFalse(result["qa_12"]["visual_quality_approved"])
        self.assertEqual(result["safety"]["proxy_calls"],0)

    def test_rejects_unready_task(self):
        data=json.loads((ROOT/"orchestrator/tasks.json").read_text(encoding="utf-8"))
        task=next(x for x in data["tasks"] if x["task_id"]=="EP01-C07-C08-V2-CONTINUITY-AUDIT")
        task["status"]="blocked"
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"tasks.json"
            p.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaises(ValueError):
                run(p,ROOT)
if __name__=="__main__":
    unittest.main()
