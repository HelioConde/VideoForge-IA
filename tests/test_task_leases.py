import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from task_leases import claim, recover, checkpoint

class TaskLeaseTests(unittest.TestCase):
    def setUp(self):
        self.task = {"task_id": "DEMO", "owner": "diretor-cenas", "status": "ready",
                     "blocked_by": [], "input_shas": {"a": "abc"}}

    def test_claim_is_idempotent(self):
        leased = claim(self.task, "diretor-cenas", 100)
        self.assertEqual(claim(leased, "diretor-cenas", 101), leased)
        self.assertEqual(leased["attempts"], 1)
        self.assertEqual(self.task["status"], "ready")

    def test_no_wrong_owner(self):
        with self.assertRaises(ValueError):
            claim(self.task, "supervisor-qa", 100)

    def test_expiry_and_retry(self):
        task = claim(self.task, "diretor-cenas", 100, 60)
        self.assertEqual(recover(task, 160)["status"], "ready")
        task = claim(recover(task, 160), "diretor-cenas", 161, 60)
        task = claim(recover(task, 221), "diretor-cenas", 222, 60)
        self.assertEqual(recover(task, 282)["status"], "failed")

    def test_checkpoint_requires_evidence(self):
        task = claim(self.task, "diretor-cenas", 100)
        with self.assertRaises(ValueError):
            checkpoint(task, "diretor-cenas", "wrong", {"artifact_sha256": "abc"})
        with self.assertRaises(ValueError):
            checkpoint(task, "diretor-cenas", task["lease"]["lease_key"], {})
        done = checkpoint(task, "diretor-cenas", task["lease"]["lease_key"], {"artifact_sha256": "abc"})
        self.assertEqual(done["status"], "needs_review")
        self.assertFalse(done["checkpoint"]["approval"])

if __name__ == "__main__":
    unittest.main()
