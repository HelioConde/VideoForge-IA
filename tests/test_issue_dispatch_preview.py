import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"orchestrator"))
from issue_dispatch_preview import run
from issue_proposals import proposals
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"orchestrator/tasks.json"
class IssueDispatchTests(unittest.TestCase):
    def test_no_open_issue_no_dispatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"issues.json"
            p.write_text("[]",encoding="utf-8")
            self.assertEqual(run(QUEUE,p,ROOT)["issue_dispatched"],[])
    def test_open_issue_dispatches_only_matching_task(self):
        proposal=next(x for x in proposals(QUEUE,10)["issues"] if x["task_id"]=="EP01-C07-C08-V2-CONTINUITY-AUDIT")
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"issues.json"
            p.write_text(json.dumps([{"number":100,"state":"open","body":"<!-- "+proposal["marker"]+" -->"}]),encoding="utf-8")
            result=run(QUEUE,p,ROOT)
            self.assertEqual([x["task_id"] for x in result["issue_dispatched"]],[proposal["task_id"]])
            self.assertEqual(result["github_writes"],0)
    def test_closed_issue_does_not_dispatch(self):
        proposal=proposals(QUEUE,1)["issues"][0]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"issues.json"
            p.write_text(json.dumps([{"number":100,"state":"closed","body":"<!-- "+proposal["marker"]+" -->"}]),encoding="utf-8")
            self.assertEqual(run(QUEUE,p,ROOT)["issue_dispatched"],[])
if __name__=="__main__":
    unittest.main()
