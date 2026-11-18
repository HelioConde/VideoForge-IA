import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))
from dashboard import render


class RuntimeDashboardTests(unittest.TestCase):
    def test_render_has_all_roles_and_lease_derived_state(self):
        report = {
            "agents": [{"id": "01", "role": "Director", "status": "running", "execution_mode": "mock"}],
            "tasks": [
                {"task_id": "live", "owner_id": "01", "status": "running", "lease": {"expires_at": 200}},
                {"task_id": "stale", "owner_id": "03", "status": "running", "lease": {"expires_at": 100}},
                {"task_id": "blocked", "owner_id": "04", "status": "blocked"},
                {"task_id": "review", "owner_id": "03", "status": "reviewing", "lease": {"worker": "supervisor-qa", "expires_at": 200}},
            ],
            "events": [], "attempts": [], "checkpoints": [], "usage": [], "safety": {"human_approval": False},
        }
        page = render(report, now=150)
        self.assertIn("Director", page)
        self.assertIn("Executando", page)
        self.assertIn("Lease expirada", page)
        self.assertIn("Bloqueado", page)
        self.assertEqual(page.count('class="status '), 12)
        self.assertIn("<td>12</td><td>Supervisor de qualidade</td><td><span class=\"status running\">", page)

    def test_escapes_untrusted_report_values(self):
        report = {"agents": [], "tasks": [{"task_id": "<script>alert(1)</script>", "title": "<img src=x onerror=alert(1)>", "status": "ready"}],
                  "events": [{"content": "</pre><script>evil()</script>"}], "attempts": [],
                  "checkpoints": [], "usage": [], "safety": {"note": "<svg/onload=alert(1)>"}}
        page = render(report, now=0)
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img src=x", page)
        self.assertNotIn("<svg/onload", page)
        self.assertIn("&lt;script&gt;", page)

    def test_rejects_invalid_report_collections(self):
        with self.assertRaises(ValueError):
            render({"tasks": "not-an-array"})


if __name__ == "__main__":
    unittest.main()
