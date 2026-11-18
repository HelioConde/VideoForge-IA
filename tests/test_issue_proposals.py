import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from issue_proposals import proposals

class IssueProposalTests(unittest.TestCase):
    def test_safe_deduplicable_proposals(self):
        path = Path(__file__).resolve().parents[1] / "orchestrator/tasks.json"
        before = path.read_bytes()
        first = proposals(path)
        self.assertEqual(first, proposals(path))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(first["github_writes"], 0)
        self.assertTrue(all(not item["execute"] for item in first["issues"]))
        self.assertEqual(len({item["marker"] for item in first["issues"]}), first["issue_count"])

    def test_limits(self):
        path = Path(__file__).resolve().parents[1] / "orchestrator/tasks.json"
        with self.assertRaises(ValueError):
            proposals(path, 0)
        self.assertLessEqual(proposals(path, 2)["issue_count"], 2)

if __name__ == "__main__":
    unittest.main()
