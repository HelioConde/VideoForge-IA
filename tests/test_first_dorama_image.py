"""Primeira imagem do julgamento é gerada no GitHub, ancorada em Kael.

Este módulo nunca chama provedor; apenas valida contrato e payload SHA.
"""
import unittest
import json
from pathlib import Path
from unittest.mock import patch
from videoforge import production_art
from videoforge.errors import VideoForgeError
ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
ASSET="c01-p04-imagem-inicial-v3"
class FirstDoramaImageTests(unittest.TestCase):
    def test_candidate_has_exact_shot_and_style(self):
        plan,story=production_art.read_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
        prompt,size=production_art.asset_prompt(plan,story,ASSET)
        self.assertEqual(size,"1024x1536")
        self.assertIn("C01-P04",prompt)
        self.assertIn("ANEXADA",prompt)
        self.assertIn("ELARA NÃO APARECE",prompt)
        self.assertIn("SEMIRREALISTA",prompt)
        self.assertIn("Sem texto",prompt)
    def test_unique_request_preserves_publication_and_human_gates(self):
        request=json.loads((EP/"pedido-geracao-arte.json").read_text(encoding="utf-8"))
        plan, story = production_art.read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        self.assertIn(request["asset"], [item["id"] for item in plan["assets"]])
        self.assertEqual(request["max_calls_per_run"],1)
        self.assertFalse(request["youtube_upload"])
        self.assertTrue(request["human_visual_review_required"])
        self.assertTrue(request["previous_rejected_reference_must_not_be_used"])
    def test_reference_kael_is_real_sha_verified(self):
        from videoforge.grounded_identity import inputs
        sources=inputs()
        kael=next(r for r in sources if r["actor"]=="kael")
        self.assertEqual(kael["sha256"],
                         "edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f")
        self.assertEqual(kael["bytes"][:4], bytes((137, 80, 78, 71)))
    def test_duplicate_is_not_accepted_for_different_asset(self):
        from videoforge.art_request_gate import decide
        old=decide("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",ASSET,
                   "push","requested_new_unique_shot_candidate")
        self.assertEqual(old["reason"],"already_archived_sha_no_repeat")
        self.assertFalse(old["ready"])
        next_shot=decide("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                         "c01-p05-guardas-lancas-v1","push","requested_next_shot")
        self.assertEqual(next_shot["reason"],"ready_unarchived_request")
        self.assertTrue(next_shot["ready"])
if __name__=="__main__":
    unittest.main()
