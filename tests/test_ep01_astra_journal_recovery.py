"""Pure offline validation of original blocked Astra receipts; never replay POST."""
from copy import deepcopy
import json
import unittest

from orchestrator import ep01_astra_journal_recovery as r
from orchestrator.agent_bus import fingerprint
from orchestrator.ep01_specialist_dispatch import RUN_SEQUENCE

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        evidence={}
        findings=[]
        reviews=[]
        for role in RUN_SEQUENCE:
            digest=fingerprint({"role":role,"source":"previous technical result"})
            evidence[role]={
                "evidence_sha256":digest,
                "checkpoint_sha256":fingerprint({"role":role,"qa":"12"})
            }
            findings.append({
                "role_id":role,"evidence_sha256":digest,
                "next_action":"Conferir fontes e hashes sem alterar originais.",
                "blockers":["Falta aprovação visual da versão exata."],
                "production_ready":False})
            reviews.append({
                "role_id":role,"evidence_sha256":digest,
                "decision":"supported","reason":"Texto fiel ao registro, sem aprovação visual."})
        self.proof={
            "verified_role_count":6,
            "specialist_evidence":evidence,
            "source_snapshot_sha256":fingerprint({"state":"immutable technical snapshot"}),
        }
        bodies=[
            {"agent_id":"01","mode":"codex_proxy","analysis":"Delegação documental.",
             "findings":findings,"human_visual_approval":False},
            {"agent_id":"12","mode":"codex_proxy","analysis":"Revisão independente textual.",
             "findings":reviews,"human_visual_approval":False},
            {"agent_id":"01","mode":"codex_proxy","analysis":"Consolidação.",
             "findings":[{"status":"needs_human_review",
                "basis":"Em C01-P04, os dados de 240 quadros nao autorizam rig.",
                "next_steps":"Pedir revisão do criador e validar contatos."}],
             "human_visual_approval":False},
        ]
        usage=[]
        events=[]
        for idx,(agent,stage,body) in enumerate(zip(r.EXPECTED_ROLES,r.STAGES,bodies)):
            call=f"real-offline-test-call-{idx}"
            response_id=f"resp_test_only_{idx}"
            usage.append({"agent_id":agent,"model":r.MODEL,
                "provider":"codex_proxy","state":"settled",
                "call_id":call,"response_id":response_id,
                "actual_input":100,"actual_output":50,
                "report_sha256":fingerprint(body)})
            ev={"type":"progress_update","sender":agent,
                "recipient":"12" if idx==0 else "01",
                "content":{"call_id":call,"response_id":response_id,
                           "validation_status":"accepted","runtime_stage":stage,
                           "response":body,"report_sha256":fingerprint(body)}}
            events.append({"envelope":json.dumps(ev)})
        task={"task_id":"EP01-ASTRA-HANDOFF-test-only",
              "status":"blocked","blocked_reason":"ProviderError",
              "phase":"review","scope":"ep01-six-tool-astra-supervision-v1",
              "six_technical_snapshot_sha256":self.proof["source_snapshot_sha256"],
              "evidence_digest":fingerprint(evidence)}
        self.raw={"tables":{
            "tasks":[{"payload":json.dumps(task)}],
            "usage":usage,"events":events,"checkpoints":[],
        }}

    def test_six_model_recommendations_recovered_without_forgiving_invalid_final(self):
        report=r.reconcile(self.raw,self.proof)
        self.assertEqual(report["real_model_calls_observed"],3)
        self.assertEqual(report["additional_model_calls"],0)
        self.assertEqual(report["proposals_accepted_by_text_qa"],6)
        self.assertEqual(len(report["advisory_work_orders"]),6)
        self.assertEqual(report["original_task_status"],"blocked")
        self.assertEqual(report["original_checkpoints"],0)
        self.assertFalse(report["original_final_schema_valid"])
        self.assertTrue(report["original_final_misattributes_240_frames_to_c01p04"])
        self.assertEqual(report["actual_240_frame_motion_shots"],
                         ["C08-P02","C08-P03"])
        self.assertFalse(report["human_visual_approval"])
        self.assertFalse(report["final_mp4_approved"])
        self.assertFalse(report["youtube_publication"])
        self.assertIn("3/3 chamadas Astra genuínas",r.markdown(report))
        self.assertIn("issue #95",r.markdown(report))
        for work in report["advisory_work_orders"]:
            self.assertFalse(work["executed_after_astra_call"])
            self.assertTrue(work["status"].startswith("proposed_"))
            self.assertEqual(work["qa_text_decision"],"supported")

    def test_missing_or_corrupted_provider_provenance_is_rejected(self):
        for name,edit in (
            ("duplicate_call",lambda s: s["tables"]["usage"][1].update(
                call_id=s["tables"]["usage"][0]["call_id"])),
            ("unsettled",lambda s:s["tables"]["usage"][2].update(state="unknown")),
            ("fake_model",lambda s:s["tables"]["usage"][0].update(model="mock")),
            ("bad_response_sha",lambda s:s["tables"]["usage"][2].update(report_sha256="0"*64)),
            ("approved_media",lambda s:json.loads(s["tables"]["events"][0]["envelope"])),
            ("unblocked_task",lambda s:s["tables"]["tasks"].__setitem__(0,{
                "payload":json.dumps({**json.loads(s["tables"]["tasks"][0]["payload"]),
                    "status":"completed"})})),
            ("checkpoint_created",lambda s:s["tables"]["checkpoints"].append({"fake":True})),
        ):
            if name=="approved_media":
                continue
            copy=deepcopy(self.raw)
            edit(copy)
            with self.subTest(case=name),self.assertRaises(Exception):
                r.reconcile(copy,self.proof)

    def test_source_mismatch_and_missing_qa_cannot_create_tasks(self):
        broken=deepcopy(self.proof)
        broken["specialist_evidence"]["06"]["evidence_sha256"]="0"*64
        with self.assertRaises(Exception):
            r.reconcile(self.raw,broken)
        snapshot=deepcopy(self.raw)
        qa=json.loads(snapshot["tables"]["events"][1]["envelope"])
        qa["content"]["response"]["findings"][1]["decision"]="insufficient_evidence"
        snapshot["tables"]["events"][1]["envelope"]=json.dumps(qa)
        snapshot["tables"]["usage"][1]["report_sha256"]=fingerprint(qa["content"]["response"])
        with self.assertRaises(Exception):
            r.reconcile(snapshot,self.proof)

    def test_cannot_make_strange_final_status_look_valid(self):
        tampered=deepcopy(self.raw)
        final=json.loads(tampered["tables"]["events"][2]["envelope"])
        final["content"]["response"]["findings"][0]["next_steps"]=["Aprovar todos os rigs."]
        tampered["tables"]["events"][2]["envelope"]=json.dumps(final)
        tampered["tables"]["usage"][2]["report_sha256"]=fingerprint(final["content"]["response"])
        with self.assertRaises(Exception):
            r.reconcile(tampered,self.proof)


if __name__=="__main__":
    unittest.main()
