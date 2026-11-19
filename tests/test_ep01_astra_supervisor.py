"""Offline contract tests. Never instantiate the real proxy or make paid calls."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from orchestrator import ep01_astra_supervisor as s
from orchestrator import ep01_specialist_dispatch as tech
from orchestrator.agent_bus import fingerprint
from orchestrator.runtime_store import Store

def evidence_fixture():
    rows={}
    for role in tech.RUN_SEQUENCE:
        row={"role_id":role,"operation":tech.SPECS[role][0],
             "checkpoint_sha256":role * 32, "result_sha256":(role[::-1])*32,
             "output_hashes":{"proof.json":role*32},
             "observed_output":{"verified":True},
             "original_execution_run_id":"44453119485",
             "media_and_visual_approved":False}
        rows[role]={**row,"evidence_sha256":fingerprint(row)}
    return {"source_snapshot_sha256":fingerprint({"immutable":True}),
            "source_state_sha256":fingerprint({"checkpoint":True}),
            "specialist_evidence":rows,"verified_role_count":6,
            "model_calls_performed_for_this_verification":0,
            "approved_for_real_rig":False}

def response(agent,findings):
    body={"agent_id":agent,"mode":"codex_proxy","analysis":"Verificacao tecnica textual.",
          "findings":findings,"human_visual_approval":False}
    return {"agent_id":agent,"model":"gpt-6.2-astra",
            "response_id":"fake-deterministic-offline-only",
            "llm_executed":True,"simulated":False,
            "provider":"codex_proxy","reported_model":"gpt-6.2-astra",
            "response_sha256":fingerprint(body),"response":body}

class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.data=evidence_fixture()
        self.proposals=[{
            "role_id":r,"evidence_sha256":self.data["specialist_evidence"][r]["evidence_sha256"],
            "next_action":"Revisar evidencias de contato e coordenadas antes do rig.",
            "blockers":["Aprovacao visual humana pendente"],"production_ready":False}
            for r in tech.RUN_SEQUENCE]
        self.decisions=[{"role_id":r,
            "evidence_sha256":self.data["specialist_evidence"][r]["evidence_sha256"],
            "decision":"supported","reason":"Nao houve liberacao de publicacao ou arte."}
            for r in tech.RUN_SEQUENCE]
        self.end=[{"status":"needs_human_review",
                   "basis":"Apenas relatorios tecnicos; revisao visual pendente.",
                   "next_steps":["Conferir mao/carrinho e QA de continuidade C08-P03."]}]

    def test_real_six_technical_snapshots_remain_source_grounded(self):
        with tempfile.TemporaryDirectory() as name:
            database=Store(Path(name)/"technical.sqlite")
            try:
                technical=tech.run(database,Path(name)/"render")
                self.assertEqual(technical["specialist_dispatch"]["technical_completed"],6)
                proof=s.verified_technical_journal(database.export_snapshot())
                self.assertEqual(proof["verified_role_count"],6)
                self.assertEqual(set(proof["specialist_evidence"]),set(tech.RUN_SEQUENCE))
                self.assertEqual(proof["model_calls_performed_for_this_verification"],0)
                self.assertFalse(proof["approved_for_real_rig"])
                bad=deepcopy(database.export_snapshot())
                bad["tables"]["checkpoints"].pop()
                with self.assertRaises(Exception):
                    s.verified_technical_journal(bad)
            finally:
                database.close()

    def test_assignment_and_qa_fail_if_sha_or_visual_approval_forged(self):
        proposal={"findings":deepcopy(self.proposals)}
        s.validate_proposals(proposal,self.data)
        for field,new in (("evidence_sha256","0"*64),
                          ("production_ready",True),("blockers",[])):
            changed=deepcopy(proposal)
            changed["findings"][0][field]=new
            with self.subTest(field=field),self.assertRaises(Exception):
                s.validate_proposals(changed,self.data)
        self.assertTrue(s.validate_qa({"findings":self.decisions},self.data))
        changed=deepcopy(self.decisions)
        changed[3]["decision"]="insufficient_evidence"
        self.assertFalse(s.validate_qa({"findings":changed},self.data))
        changed[3]["evidence_sha256"]="x"*64
        with self.assertRaises(Exception):
            s.validate_qa({"findings":changed},self.data)
        s.validate_consolidation({"findings":self.end},True)
        with self.assertRaises(Exception):
            s.validate_consolidation({"findings":self.end},False)

    def test_full_three_stage_simulated_response_never_counts_as_real_usage(self):
        with tempfile.TemporaryDirectory() as name:
            store=Store(Path(name)/"test.sqlite")
            calls=[]
            def fake_model_step(db,task,root,role,payload,mode,limits):
                self.assertEqual(mode,"codex_proxy")
                self.assertEqual(limits["calls"],3)
                stage=payload["runtime_stage"]
                calls.append((role,stage))
                if stage.endswith("_assignment"):
                    return response("01",deepcopy(self.proposals))
                if stage.endswith("_qa"):
                    return response("12",deepcopy(self.decisions))
                return response("01",deepcopy(self.end))
            try:
                with patch.dict("os.environ",{
                    "VF_EP01_SUPERVISOR_AUTHORIZATION":"AUTHORIZE_THREE_ASTRA_HANDOFF_CALLS",
                    "GITHUB_RUN_ATTEMPT":"1","AI_MODEL":"gpt-6.2-astra"}):
                    with patch.object(s,"model_step",side_effect=fake_model_step):
                        result=s.run(store,self.data)
                self.assertEqual([x[0] for x in calls],["01","12","01"])
                self.assertEqual(result["tasks"][0]["status"],"completed")
                self.assertEqual(result["checkpoints"][0]["review"]["agent_id"],"12")
                self.assertIs(result["checkpoints"][0]["human_visual_approval"],False)
                self.assertEqual(result["astra_tool_supervision"]["actual_calls"],0)
                self.assertEqual(result["safety"]["youtube_publications"],0)
                with self.assertRaises(ValueError):
                    s.validate_real(result,"gpt-6.2-astra")
            finally:
                store.close()

    def test_no_authorization_no_call(self):
        with tempfile.TemporaryDirectory() as name:
            store=Store(Path(name)/"test.sqlite")
            try:
                with patch.dict("os.environ",{
                    "VF_EP01_SUPERVISOR_AUTHORIZATION":"",
                    "GITHUB_RUN_ATTEMPT":"1","AI_MODEL":"gpt-6.2-astra"}):
                    with patch.object(s,"model_step") as call:
                        with self.assertRaisesRegex(ValueError,"authorization"):
                            s.run(store,self.data)
                        call.assert_not_called()
            finally:
                store.close()

    def test_three_call_budget_and_prevention_of_fresh_unpaid_rerun(self):
        self.assertEqual(s.N_CALLS,3)
        self.assertEqual(s.EXPECTED,["01","12","01"])
        self.assertEqual(s.STATE,"runtime/ep01-astra-supervisor-v1.json")
        self.assertNotEqual(s.STATE,tech.STATE)


if __name__=="__main__":
    unittest.main()
