"""Regressão: nunca assistir a um run antigo com mesmo título."""
import unittest

from videoforge.github_dispatch_id import extract_run_id


class GitHubDispatchIDTests(unittest.TestCase):
    def test_extract_exact_new_run(self):
        text = "https://github.com/HelioConde/VideoForge-IA/actions/runs/44015635823"
        self.assertEqual(extract_run_id(text, "HelioConde/VideoForge-IA"), 44015635823)

    def test_no_match_for_other_repository(self):
        text = "https://github.com/Other/VideoForge-IA/actions/runs/44015635823"
        self.assertIsNone(extract_run_id(text, "HelioConde/VideoForge-IA"))

    def test_ambiguous_new_run_is_rejected(self):
        text = ("https://github.com/HelioConde/VideoForge-IA/actions/runs/44015635823\n"
                "https://github.com/HelioConde/VideoForge-IA/actions/runs/44012198030")
        self.assertIsNone(extract_run_id(text, "HelioConde/VideoForge-IA"))

    def test_missing_and_invalid_url_fail_closed(self):
        self.assertIsNone(extract_run_id("Run workflow submitted", "HelioConde/VideoForge-IA"))
        self.assertIsNone(extract_run_id("https://github.com/HelioConde/VideoForge-IA/actions/runs/123",
                                         "../../unsafe"))
        self.assertIsNone(extract_run_id("https://github.com/HelioConde/VideoForge-IA/actions/runs/0",
                                         "HelioConde/VideoForge-IA"))

    def test_valid_query_or_suffix(self):
        text = "https://github.com/HelioConde/VideoForge-IA/actions/runs/44015635823?check_suite_focus=true"
        self.assertEqual(extract_run_id(text, "HelioConde/VideoForge-IA"), 44015635823)


if __name__ == "__main__":
    unittest.main()
