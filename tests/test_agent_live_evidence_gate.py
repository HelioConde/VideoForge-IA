"""Fail-closed proof that 13 calls alone cannot masquerade as a finished Astra audit."""
import copy
import unittest

from orchestrator.agent_bus import fingerprint
from orchestrator.agent_live_roundtrip import (
    FOCUS, SPECIALISTS, validate_live_roundtrip_result,
)
from orchestrator.providers import ProviderError
from orchestrator.runtime import MANIFEST, _stage_recipient


MODEL = "gpt-6.2-astra"
SOURCE = "a" * 64
RESULT = "b" * 64


def example(passed=True):
    roles = ["01", *SPECIALISTS, "12", "01"]
    stages = (["roundtrip_assignment"] + ["roundtrip_specialist"] * 10
              + ["roundtrip_independent_qa", "roundtrip_consolidation"])
    specialist_shas = {role: f"{int(role):064x}" for role in SPECIALISTS}
    journal = []
    usage = []
    for index, (role, stage) in enumerate(zip(roles, stages)):
        if stage == "roundtrip_assignment":
            findings = [
                {"recipient": specialist, "focus": FOCUS[specialist],
                 "source_sha256": SOURCE, "tools": ["read_only_text_analysis"]}
                for specialist in SPECIALISTS
            ]
        elif stage == "roundtrip_specialist":
            findings = [
                {"role_id": role, "focus": FOCUS[role],
                 "evidence_sha256": specialist_shas[role],
                 "production_ready": False,
                 "blockers": ["Aprovacao visual pendente"],
                 "recommendation": "Revisar as fontes e obter QA"}
            ]
        elif stage == "roundtrip_independent_qa":
            findings = [
                {"role_id": specialist,
                 "decision": ("supported" if passed or specialist != "07"
                              else "correction_requested"),
                 "evidence_sha256": specialist_shas[specialist],
                 "reason": "Evidencia textual examinada"}
                for specialist in SPECIALISTS
            ]
        else:
            findings = [{
                "status": "needs_human_review" if passed else "blocked",
                "basis": "Auditoria de texto somente, sem liberar producao",
                "next_steps": ["Exigir revisao humana e QA de midia"],
            }]
        response = {
            "agent_id": role, "mode": "codex_proxy",
            "analysis": "Somente auditoria textual de fontes pinadas",
            "findings": findings, "human_visual_approval": False,
        }
        call = f"call-{index:02}"
        response_id = f"response-{index:02}"
        content = {
            "call_id": call, "agent_id": role,
            "recipient": _stage_recipient(stage),
            "runtime_stage": stage, "model": MODEL,
            "response_id": response_id,
            "report_sha256": fingerprint(response),
            "validation_status": "accepted", "response": response,
        }
        usage.append({
            "call_id": call, "agent_id": role, "model": MODEL,
            "provider": "codex_proxy", "state": "settled",
            "response_id": response_id, "report_sha256": fingerprint(response),
        })
        journal.append({
            "task_id": "EP01-ALL-ROLES-TEXT-check", "type": "progress_update",
            "sender": role, "recipient": _stage_recipient(stage),
            "content": content,
        })
    review = {
        "agent_id": "12", "technical_passed": passed,
        "reviewed_result_sha256": RESULT, "human_visual_approval": False,
        "production_ready": False,
        "qa_response": {"response": journal[-2]["content"]["response"]},
        "coordinator": {"response": journal[-1]["content"]["response"]},
    }
    task = {
        "task_id": "EP01-ALL-ROLES-TEXT-check",
        "owner": "01", "reviewer": "12",
        "scope": "all-12-text-roundtrip-v1", "mode": "codex_proxy",
        "model": MODEL, "result_sha256": RESULT,
        "input_refs": {MANIFEST.as_posix(): SOURCE},
        "status": "completed" if passed else "blocked",
    }
    checkpoint = {
        "task_id": task["task_id"],
        "result_sha256": RESULT,
        "input_refs": task["input_refs"], "review": review,
        "human_visual_approval": False,
        "youtube_publication": False,
    }
    if not passed:
        task["blocked_reason"] = "independent_review_rejected"
        checkpoint["status"] = "blocked"
    return {
        "tasks": [task], "usage": usage, "events": journal,
        "checkpoints": [checkpoint],
        "safety": {"production_tools_enabled": False, "youtube_publications": 0},
    }


class EvidenceGateTests(unittest.TestCase):
    def test_thirteen_real_journals_and_passing_qa_only_reach_human_review(self):
        self.assertEqual(validate_live_roundtrip_result(example(), MODEL),
                         "needs_human_review")

    def test_qa_rejection_is_a_valid_blocked_audit_not_a_media_approval(self):
        self.assertEqual(validate_live_roundtrip_result(example(False), MODEL),
                         "blocked")

    def test_missing_duplicate_or_swapped_calls_fail(self):
        missing = example()
        missing["events"].pop(3)
        duplicate = example()
        duplicate["events"][2]["content"]["call_id"] = "call-01"
        swapped = example()
        swapped["usage"][5]["agent_id"] = "03"
        for data in (missing, duplicate, swapped):
            with self.subTest(change=data["usage"][5]["agent_id"]):
                with self.assertRaises((ProviderError, ValueError)):
                    validate_live_roundtrip_result(data, MODEL)

    def test_malformed_provenance_and_fake_approval_fail(self):
        mutations = [
            lambda x: x["usage"][4].update(model="mock"),
            lambda x: x["usage"][4].update(state="unknown"),
            lambda x: x["usage"][4].update(report_sha256="0" * 64),
            lambda x: x["events"][4]["content"].update(validation_status="rejected"),
            lambda x: x["events"][4].update(recipient="01"),
            lambda x: x["checkpoints"][0].update(youtube_publication=True),
            lambda x: x["tasks"][0].update(status="completed", blocked_reason="ProviderError"),
            lambda x: x["checkpoints"][0]["review"].update(technical_passed=False),
            lambda x: x["checkpoints"][0]["review"]["qa_response"].update(response={}),
            lambda x: x["checkpoints"][0]["review"]["coordinator"].update(response={}),
            lambda x: x["events"][0]["content"]["response"].update(human_visual_approval=True),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                tampered = copy.deepcopy(example())
                mutate(tampered)
                with self.assertRaises((ProviderError, ValueError)):
                    validate_live_roundtrip_result(tampered, MODEL)

    def test_specialist_journals_target_independent_reviewer(self):
        self.assertEqual(_stage_recipient("roundtrip_specialist"), "12")
        self.assertEqual(_stage_recipient("roundtrip_independent_qa"), "01")


if __name__ == "__main__":
    unittest.main()
