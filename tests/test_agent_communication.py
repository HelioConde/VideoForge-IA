import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from agent_communication import simulate

class CommunicationTest(unittest.TestCase):
    def test_handoff_and_safety(self):
        result = simulate()
        self.assertEqual(result["status"], "protocol_test_passed")
        self.assertEqual(len(result["events"]), 3)
        self.assertEqual([e["to"] for e in result["events"]], ["03", "12", "01"])
        self.assertFalse(result["ep01_human_visual_approval"])
        self.assertTrue(result["no_proxy_calls"])
        self.assertTrue(result["no_publication"])
        self.assertEqual(len({e["event_id"] for e in result["events"]}), 3)

if __name__ == "__main__":
    unittest.main()
