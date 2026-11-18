import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"orchestrator"))
from task_leases import claim,recover,checkpoint
TASK={"task_id":"T-1","owner":"diretor-cenas","status":"ready","blocked_by":[],"input_shas":{"a":"b"}}
class LeaseFencingTests(unittest.TestCase):
    def test_stale_token_cannot_complete_retry(self):
        first=claim(TASK,"diretor-cenas",100,60)
        self.assertEqual(claim(first,"diretor-cenas",110),first)
        with self.assertRaises(ValueError):
            claim(first,"diretor-cenas",160)
        recovered=recover(first,160)
        self.assertEqual(recovered["status"],"ready")
        second=claim(recovered,"diretor-cenas",161,60)
        self.assertNotEqual(first["lease"]["lease_key"],second["lease"]["lease_key"])
        with self.assertRaises(ValueError):
            checkpoint(second,"diretor-cenas",first["lease"]["lease_key"],{"artifact_sha256":"abc"},170)
        with self.assertRaises(ValueError):
            checkpoint(second,"diretor-cenas",second["lease"]["lease_key"],{"artifact_sha256":"abc"},221)
        done=checkpoint(second,"diretor-cenas",second["lease"]["lease_key"],{"artifact_sha256":"abc"},220)
        self.assertEqual(done["status"],"needs_review")
        self.assertFalse(done["checkpoint"]["approval"])
    def test_retry_budget(self):
        t=dict(TASK)
        for i in range(3):
            t=claim(t,"diretor-cenas",100+i*100,60)
            t=recover(t,160+i*100)
        self.assertEqual(t["status"],"failed")
        with self.assertRaises(ValueError):
            claim(t,"diretor-cenas",500)
if __name__=="__main__":
    unittest.main()
