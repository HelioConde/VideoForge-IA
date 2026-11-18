import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"orchestrator"))
from issue_checkpoints import prepare
class CheckpointTests(unittest.TestCase):
    def test_deterministic_proposals(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d)
            dispatch={"mode":"read_only_issue_gated_preview","github_writes":0,
              "issue_dispatched":[{"task_id":"TASK-1","agent_id":"03","qa_passed":True,
                 "result":{"qa_12":{"human_review_required":True},"technical":42}}]}
            issues=[{"number":4,"state":"open","body":"<!-- videoforge-task:TASK-1 -->"}]
            (d/"dispatch.json").write_text(json.dumps(dispatch))
            (d/"issues.json").write_text(json.dumps(issues))
            a=prepare(d/"dispatch.json",d/"issues.json")
            b=prepare(d/"dispatch.json",d/"issues.json")
            self.assertEqual(a,b)
            self.assertEqual(len(a["comments"]),1)
            self.assertIn("não é aprovação visual",a["comments"][0]["body"])
    def test_no_qa_no_comment(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d)
            (d/"dispatch.json").write_text(json.dumps({"mode":"read_only_issue_gated_preview","github_writes":0,
                "issue_dispatched":[{"task_id":"TASK-1","qa_passed":False,"result":{}}]}))
            (d/"issues.json").write_text("[]")
            self.assertEqual(prepare(d/"dispatch.json",d/"issues.json")["comments"],[])
if __name__=="__main__":
    unittest.main()
