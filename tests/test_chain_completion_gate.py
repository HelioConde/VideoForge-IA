"""Four successful calls are not a completed audit without durable QA evidence."""
import copy
import unittest
from orchestrator.runtime import validate_chain_audit_result


def completed(approved=True):
    status = "needs_human_review" if approved else "blocked"
    task = {"task_id": "audit", "result_sha256": "a" * 64,
            "status": "completed" if approved else "blocked"}
    if not approved:
        task["blocked_reason"] = "independent_review_rejected"
    review = {"agent_id": "12", "technical_passed": approved,
              "reviewed_result_sha256": task["result_sha256"],
              "coordinator": {"agent_id": "01",
                              "response": {"findings": [{"status": status}]}}}
    checkpoint = {"task_id": "audit", "result_sha256": task["result_sha256"],
                  "human_visual_approval": False, "youtube_publication": False,
                  "review": review}
    if not approved:
        checkpoint["status"] = "blocked"
    ledger = [{"agent_id": agent, "state": "settled",
               "model": "gpt-6.2-astra", "report_sha256": "b" * 64}
              for agent in ("01", "03", "12", "01")]
    return {"tasks": [task], "checkpoints": [checkpoint], "usage": ledger}


class CompletionGateTests(unittest.TestCase):
    def test_passed_qa_is_technical_only(self):
        self.assertEqual(validate_chain_audit_result(completed(), "gpt-6.2-astra"),
                         "needs_human_review")

    def test_qa_rejection_has_valid_blocked_audit_checkpoint(self):
        self.assertEqual(validate_chain_audit_result(completed(False), "gpt-6.2-astra"),
                         "blocked")

    def test_provider_block_cannot_pass_with_four_calls(self):
        evidence = completed(False)
        evidence["tasks"][0]["blocked_reason"] = "ProviderError"
        with self.assertRaises(ValueError):
            validate_chain_audit_result(evidence, "gpt-6.2-astra")

    def test_four_calls_without_qa_checkpoint_must_fail(self):
        evidence = completed()
        evidence["checkpoints"] = []
        with self.assertRaises(ValueError):
            validate_chain_audit_result(evidence, "gpt-6.2-astra")

    def test_director_override_must_fail(self):
        evidence = completed(False)
        evidence["checkpoints"][0]["review"]["coordinator"]["response"]["findings"][0]["status"] = "completed"
        with self.assertRaises(ValueError):
            validate_chain_audit_result(evidence, "gpt-6.2-astra")

    def test_missing_final_response_or_wrong_model_must_fail(self):
        evidence = completed()
        evidence["usage"][-1]["report_sha256"] = None
        with self.assertRaises(ValueError):
            validate_chain_audit_result(evidence, "gpt-6.2-astra")
        evidence = completed()
        with self.assertRaises(ValueError):
            validate_chain_audit_result(evidence, "gpt-6-astra")


if __name__ == "__main__":
    unittest.main()
