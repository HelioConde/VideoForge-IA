"""The agent dashboard must not invent live inference or media approvals."""
import json
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
from unittest.mock import patch

from orchestrator import agent_activity, durable_dispatch, runtime
from orchestrator.runtime_store import Store


class AgentActivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue=json.loads((runtime.ROOT/"orchestrator/tasks.json").read_text())
        cls.temp=tempfile.TemporaryDirectory(prefix="agent-activity-test-")
        cls.store=Store(Path(cls.temp.name)/"status.sqlite")
        cls.dispatch=durable_dispatch.run(cls.store,max_tasks=4)

    @classmethod
    def tearDownClass(cls):
        cls.store.close()
        cls.temp.cleanup()

    def test_twelve_honest_role_rows_and_four_real_source_checkpoints(self):
        data=agent_activity.make_status(self.dispatch,self.queue,None,
                                        run_id=8888,now="2026-11-19T12:00:00+00:00")
        self.assertEqual(len(data["agents"]),12)
        self.assertEqual(data["technical_dispatch"]["source_audits_completed"],4)
        self.assertEqual({a["id"] for a in data["agents"]},set(agent_activity.NAMES))
        self.assertEqual({a["id"] for a in data["agents"]
                          if a["checkpoint_sha256"]}, {"03","04","07","10"})
        self.assertEqual(data["queue"]["statuses"]["ready"],6)
        self.assertEqual(data["queue"]["statuses"]["blocked"],3)
        self.assertEqual(data["queue"]["statuses"]["needs_review"],1)
        self.assertFalse(data["queue"]["dispatch_enabled"])
        self.assertEqual(data["technical_dispatch"]["new_model_calls"],0)
        self.assertFalse(data["human_visual_approval"])
        self.assertFalse(data["mp4_final_ready"])
        self.assertFalse(data["rig_ready"])
        self.assertEqual(data["youtube_publications"],0)
        self.assertFalse(data["historical_astra"]["validated"])
        self.assertIn("Revisou 4 resultados tecnicos",data["agents"][11]["current_activity"])
        self.assertEqual(data["agents"][4]["current_activity"],
                         "sem execucao recente comprovada")
        body=agent_activity.render_markdown(data)
        self.assertIn("Agente",body)
        self.assertIn("Historico Astra nao validado",body)
        self.assertIn("**0/6**",body)
        self.assertIn("nenhum MP4 final",body)
        self.assertIn("8888",body)
        self.assertIn("EP01-C07-C08-V2-CONTINUITY-AUDIT",body)
        self.assertEqual(body.count("| **"),12)

    def test_forged_independent_qa_is_rejected(self):
        for mutation in ("missing_checkpoint","false_approval","wrong_reviewer",
                         "result_sha_tampered","source_owner_mismatch",
                         "fake_model_call","fake_video"):
            d=deepcopy(self.dispatch)
            q=deepcopy(self.queue)
            if mutation=="missing_checkpoint":
                d["checkpoints"].pop()
            elif mutation=="false_approval":
                d["checkpoints"][0]["human_visual_approval"]=True
            elif mutation=="wrong_reviewer":
                d["checkpoints"][0]["review"]["agent_id"]="03"
            elif mutation=="result_sha_tampered":
                d["checkpoints"][0]["result_sha256"]="f"*64
            elif mutation=="source_owner_mismatch":
                q["tasks"][0]["owner"]="gerador-visual"
            elif mutation=="fake_model_call":
                d["dispatch"]["model_inference_requests"]=1
            elif mutation=="fake_video":
                d["safety"]["production_tools_enabled"]=True
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                agent_activity.make_status(d,q,None,run_id=1,now="test")

    def test_wrong_snapshot_and_queue_flags_reject_false_autonomy(self):
        d=deepcopy(self.dispatch)
        q=deepcopy(self.queue)
        q["dispatch_enabled"]=True
        with self.assertRaisesRegex(ValueError,"Unsafe"):
            agent_activity.make_status(d,q,None,run_id=1,now="test")
        q["dispatch_enabled"]=False
        q["mode"]="autonomous_image_production"
        with self.assertRaisesRegex(ValueError,"Unsafe"):
            agent_activity.make_status(d,q,None,run_id=1,now="test")

    def test_historical_real_astra_requires_proven_thirteen_roles(self):
        with self.assertRaisesRegex(ValueError,"Unverified"):
            agent_activity.historical_proof({
                "tasks":[{"model":"gpt-6.2-astra"}],
                "usage":[{"agent_id":"01","state":"settled"}]
            })
        self.assertEqual(agent_activity.historical_proof(None)["calls"],0)


if __name__=="__main__":
    unittest.main()
