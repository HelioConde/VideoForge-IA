"""Regression tests: the director cannot override independent QA or human approval."""
import unittest
from orchestrator.providers import ProviderError
from orchestrator.runtime import _validate_chain_stage


class DirectorConsolidationGateTests(unittest.TestCase):
    def check(self, technical_passed, status, basis="Verificacao concluida", next_steps=None):
        data = {"findings": [{"status": status, "basis": basis,
                              "next_steps": ["Solicitar revisao humana"] if next_steps is None else next_steps}]}
        return _validate_chain_stage(None, {}, {"review": {"technical_passed": technical_passed}},
                                     "01", "director_consolidation", data)

    def test_qa_pass_still_requires_human_review(self):
        self.check(True, "needs_human_review")

    def test_failed_qa_must_block(self):
        self.check(False, "blocked")
        self.check(None, "blocked")

    def test_director_cannot_claim_completion_without_human_approval(self):
        for qa in (True, False, None):
            with self.subTest(qa=qa), self.assertRaises(ProviderError):
                self.check(qa, "completed")

    def test_director_cannot_override_qa_status(self):
        with self.assertRaises(ProviderError):
            self.check(False, "needs_human_review")
        with self.assertRaises(ProviderError):
            self.check(True, "blocked")

    def test_empty_or_unstructured_next_steps_are_rejected(self):
        for steps in ([], [""], [None], [12]):
            with self.subTest(steps=steps), self.assertRaises(ProviderError):
                self.check(True, "needs_human_review", next_steps=steps)
        with self.assertRaises(ProviderError):
            self.check(True, "needs_human_review", basis="  ")


if __name__ == "__main__":
    unittest.main()
