"""Guard against contradictory active dorama rules and stale permissions."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"


class RemakePolicyConsistencyTests(unittest.TestCase):
    def test_active_remake_flags_do_not_disagree(self):
        state = json.loads((EP / "estado-atual.json").read_text(encoding="utf-8"))
        style = json.loads((EP / "estilo-visual-oficial-dorama.json").read_text(encoding="utf-8"))
        policy = json.loads((EP / "autonomy-policy.json").read_text(encoding="utf-8"))
        self.assertEqual(state["active_production_version"], "remake-v2-20261115")
        self.assertFalse(state["locks"]["no_new_image_generation"])
        self.assertTrue(state["remake_v2"]["generation_editorially_authorized"])
        self.assertTrue(style["generation_authorization"]["current_episode_new_image_calls_allowed"])
        self.assertFalse(style["production_policy"]["current_episode_generation_locked"])
        self.assertFalse(style["production_policy"]["current_episode_lock_still_active"])
        self.assertFalse(policy["paid_provider_calls_approved"])
        self.assertFalse(state["locks"]["official_video_allowed"])
        self.assertFalse(state["locks"]["no_youtube_upload"] is False)

    def test_legacy_lock_is_archived_not_active(self):
        self.assertFalse((EP / "SEM-GERACAO-NOVAS-IMAGENS.lock").exists())
        self.assertTrue((EP / "REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md").is_file())

    def test_current_sources_and_legacy_are_labeled(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        cp = (EP / "ESTADO-ATUAL.md").read_text(encoding="utf-8")
        legacy = (EP / "PLANO-ARTE-RIG-EP01.md").read_text(encoding="utf-8")
        self.assertIn("PRECEDÊNCIA DAS REGRAS", agents)
        self.assertIn("REGRAS ATIVAS DO REMAKE", cp)
        self.assertIn("DOCUMENTO HISTÓRICO", legacy)
        self.assertIn("REMAKE-EP01-PLANO-OFICIAL.md", cp)
        self.assertIn("manual principal", agents.lower())

    def test_v1_manifests_are_explicitly_historical(self):
        for name in ("direcao-cinematografica-planos.json", "timeline-cinematografica.json"):
            with self.subTest(name=name):
                obj=json.loads((EP / name).read_text(encoding="utf-8"))
                self.assertTrue(obj["legacy_scope"].startswith("pre_remake"))
                self.assertEqual(obj["active_remake_manifest"], "remake-ep01-planos.json")


if __name__ == "__main__":
    unittest.main()
