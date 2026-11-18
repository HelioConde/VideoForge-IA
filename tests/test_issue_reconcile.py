import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"orchestrator"))
from issue_reconcile import reconcile
from issue_proposals import proposals
QUEUE=Path(__file__).resolve().parents[1]/"orchestrator/tasks.json"
class ReconcileTests(unittest.TestCase):
    def test_existing_and_new(self):
        p=proposals(QUEUE,2)["issues"]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"snapshot.json"
            path.write_text(json.dumps([{"number":72,"body":"<!-- "+p[0]["marker"]+" -->","state":"open"}]),encoding="utf-8")
            result=reconcile(QUEUE,path,2)
            self.assertEqual(len(result["already_present"]),1)
            self.assertEqual(len(result["new_proposals"]),1)
    def test_conflict_detected(self):
        p=proposals(QUEUE,1)["issues"][0]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"snapshot.json"
            path.write_text(json.dumps([{"number":2,"body":"<!-- "+p["marker"]+" -->"},
                                        {"number":3,"body":"<!-- "+p["marker"]+" -->"}]),encoding="utf-8")
            self.assertEqual(len(reconcile(QUEUE,path,1)["duplicate_conflicts"]),1)
if __name__=="__main__":
    unittest.main()
