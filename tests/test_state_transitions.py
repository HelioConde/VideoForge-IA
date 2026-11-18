import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"orchestrator"))
from state_transitions import digest,transition
BASE={"tasks":[{"task_id":"T1","owner":"diretor-cenas","status":"ready","blocked_by":[],"input_shas":{}}]}
class StateTransitionTests(unittest.TestCase):
    def test_claim_checkpoint_and_conflict(self):
        rev=digest(BASE)
        a=transition(BASE,"T1","claim",rev,100,"diretor-cenas")
        self.assertFalse(a["persisted"])
        self.assertEqual(BASE["tasks"][0]["status"],"ready")
        with self.assertRaises(ValueError):
            transition(a["next_state"],"T1","claim",rev,101,"diretor-cenas")
        task=a["next_state"]["tasks"][0]
        b=transition(a["next_state"],"T1","checkpoint",a["next_revision"],110,
                     "diretor-cenas",task["lease"]["lease_key"],{"artifact_sha256":"abc"})
        self.assertEqual(b["next_state"]["tasks"][0]["status"],"needs_review")
        self.assertFalse(b["next_state"]["tasks"][0]["checkpoint"]["approval"])
    def test_recovery(self):
        a=transition(BASE,"T1","claim",digest(BASE),100,"diretor-cenas")
        b=transition(a["next_state"],"T1","recover",a["next_revision"],1000)
        self.assertEqual(b["next_state"]["tasks"][0]["status"],"ready")
    def test_reject_duplicate_id(self):
        state={"tasks":[BASE["tasks"][0],BASE["tasks"][0]]}
        with self.assertRaises(ValueError):
            transition(state,"T1","claim",digest(state),100,"diretor-cenas")
if __name__=="__main__":
    unittest.main()
