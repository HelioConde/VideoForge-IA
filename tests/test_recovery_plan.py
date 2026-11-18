import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"orchestrator"))
from recovery_plan import plan
from task_leases import claim
BASE={"task_id":"T1","owner":"diretor-cenas","status":"ready","blocked_by":[],"input_shas":{}}
class RecoveryPlanTests(unittest.TestCase):
    def snapshot(self, tasks):
        temp=tempfile.TemporaryDirectory()
        path=Path(temp.name)/"state.json"
        path.write_text(json.dumps({"tasks":tasks}),encoding="utf-8")
        return temp,path
    def test_expired_and_active(self):
        a=claim(BASE,"diretor-cenas",100,60)
        b=claim(dict(BASE,task_id="T2"),"diretor-cenas",180,60)
        tmp,path=self.snapshot([a,b])
        try:
            result=plan(path,200)
            self.assertEqual([d["decision"] for d in result["decisions"]],["retry_ready","still_running"])
            self.assertFalse(result["state_written"])
            self.assertEqual(json.loads(path.read_text())["tasks"][0]["status"],"running")
        finally:tmp.cleanup()
    def test_exhausted(self):
        t=claim(dict(BASE,attempts=2),"diretor-cenas",100,60)
        tmp,path=self.snapshot([t])
        try:self.assertEqual(plan(path,160)["decisions"][0]["decision"],"retry_exhausted")
        finally:tmp.cleanup()
    def test_corrupt_running_state(self):
        tmp,path=self.snapshot([dict(BASE,status="running")])
        try:self.assertEqual(plan(path,200)["decisions"][0]["decision"],"manual_review")
        finally:tmp.cleanup()
if __name__=="__main__":
    unittest.main()
