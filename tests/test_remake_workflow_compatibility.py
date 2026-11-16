"""Remake read-only workflows must not require the archived V1 image ban."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
EP="canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
READONLY=["align-alchemy-kael-existing.yml","directed-rig-preview.yml","qa-alchemy-chat-cinematic-references.yml","qa-alchemy-cinematic-continuity.yml","qa-alchemy-eye-pixels.yml","qa-alchemy-guard-arms.yml","qa-alchemy-guard-motion-holes.yml","qa-alchemy-scene1-composition.yml","qa-alchemy-scene1-reconciled.yml","qa-cinematic-edl.yml","qa-cinematic-remotion-renderer.yml","qa-cinematic-shots.yml","qa-permanent-image-archive.yml","reconcile-alchemy-background-c01.yml","refine-alchemy-aldric-existing.yml","refine-alchemy-guards-existing.yml","remap-alchemy-kael-existing.yml","split-alchemy-aldric-existing.yml","split-alchemy-guard-arms-existing.yml","import-alchemy-c12-technical-zip.yml"]

class RemakeWorkflowCompatibilityTests(unittest.TestCase):
    def test_legacy_qa_workflows_no_longer_require_old_live_lock(self):
        for name in READONLY:
            with self.subTest(name=name):
                data=(ROOT/".github/workflows"/name).read_text(encoding="utf-8")
                self.assertNotIn("SEM-GERACAO-NOVAS-IMAGENS.lock",data)
                self.assertIn("REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md",data)

    def test_cinematic_legacy_edl_cannot_erase_historical_metadata(self):
        data=(ROOT/".github/workflows/qa-cinematic-edl.yml").read_text(encoding="utf-8")
        self.assertIn('data["legacy_scope"]="pre_remake_cinematic_edl_immutable_reference"',data)
        self.assertIn('data["active_remake_manifest"]="remake-ep01-planos.json"',data)
        self.assertIn('assert d["noImageGenerationLock"] is True',data)

    def test_scene_workflow_uses_v2_sha_approved_reference_and_legacy_fallback(self):
        data=(ROOT/".github/workflows/production-scene-by-request.yml").read_text(encoding="utf-8")
        self.assertIn("REMAKE_V2_REQUIRES_EXPLICIT_SHOT_ID",data)
        self.assertIn("videoforge.remake_reference",data)
        self.assertIn("steps.request.outputs.is_remake == 'true'",data)
        self.assertIn("steps.request.outputs.is_remake != 'true'",data)
        self.assertIn("scripts/arquivar-pngs-se-existirem.sh",data)

    def test_qa_archive_checks_new_policy_without_allowing_paid_work(self):
        data=(ROOT/".github/workflows/qa-permanent-image-archive.yml").read_text(encoding="utf-8")
        self.assertIn("state['active_production_version']=='remake-v2-20261115'",data)
        # Persist-only QA never calls the provider; it must not contradict
        # the separate, standing V2 editorial authorization.
        self.assertIn("policy['paid_provider_calls_approved'] is True",data)
        self.assertIn("d['generate_images'] is False",data)
        self.assertIn("d['render_mp4'] is False",data)
        self.assertIn("d['youtube_upload'] is False",data)
        self.assertIn("tests.test_art_request_gate",data)


if __name__=="__main__":
    unittest.main()
