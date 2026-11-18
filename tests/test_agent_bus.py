import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from agent_bus import ROLES, make_message, append_message, transition, safe_checkpoint, load_queue

class AgentBusTests(unittest.TestCase):
    def test_all_roles(self):
        self.assertEqual(len(ROLES), 12)
        self.assertEqual(len(set(ROLES.values())), 12)

    def test_idempotent_ordered_messages(self):
        state = {}
        msg = make_message("DEMO", "01", "03", "task_assigned", "Audit", 1)
        self.assertTrue(append_message(state, msg))
        self.assertFalse(append_message(state, msg))
        with self.assertRaises(ValueError):
            append_message(state, make_message("DEMO", "03", "12", "review", "Ready", 3))
        self.assertTrue(append_message(state, make_message("DEMO", "03", "12", "review", "Ready", 2)))
        self.assertEqual(safe_checkpoint(state["events"])["proxy_calls"], 0)

    def test_no_self_approval(self):
        task = {"owner": "diretor-cenas", "status": "needs_review"}
        with self.assertRaises(ValueError):
            transition(task, "approved", "03")
        transition(task, "approved", "12")
        self.assertEqual(task["status"], "approved")

    def test_human_gate(self):
        task = {"owner": "diretor-cenas", "status": "needs_review", "requires_human_approval": True}
        with self.assertRaises(ValueError):
            transition(task, "approved", "12")

    def test_dependency_gate(self):
        task = {"owner": "diretor-cenas", "status": "ready", "blocked_by": ["x"]}
        with self.assertRaises(ValueError):
            transition(task, "running", "03")

    def test_existing_queue(self):
        path = Path(__file__).resolve().parents[1] / "orchestrator" / "tasks.json"
        self.assertGreater(len(load_queue(path)["tasks"]), 0)

if __name__ == "__main__":
    unittest.main()
