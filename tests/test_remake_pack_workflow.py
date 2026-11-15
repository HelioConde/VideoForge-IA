"""Require the automatic C01-P02 producer to remain fail-closed and cost-free."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class RemakePackWorkflowTests(unittest.TestCase):
    def test_source_scanner_does_not_charge_ai_or_publish(self):
        src=(ROOT/".github/workflows/remake-sword-pack.yml").read_text(encoding="utf-8")
        self.assertIn("videoforge.remake_sword_pack scan",src)
        self.assertIn("needs.scan_real_source_archives.outputs.ready == 'true'",src)
        self.assertIn("videoforge.remake_sword_pack pack",src)
        self.assertIn("vf-remake-c01-p02-sword-source-",src)
        self.assertIn("actions/upload-artifact@v4",src)
        self.assertIn("retention-days: 90",src)
        self.assertNotIn("CODEX_PROXY_API_KEY",src)
        self.assertNotIn("images/edits",src)
        self.assertNotIn("gh workflow run",src)
        self.assertNotIn("git push",src)

    def test_preview_consumes_only_real_bundle_and_skips_blocked_runs(self):
        src=(ROOT/".github/workflows/remake-sword-preview.yml").read_text(encoding="utf-8")
        self.assertIn('workflows: ["VideoForge - C01-P02 pacote da arte real por SHA"]',src)
        self.assertIn("listWorkflowRunArtifacts",src)
        self.assertIn("head_repository.full_name == github.repository",src)
        self.assertIn("needs.locate-source-artifact.outputs.available == 'true'",src)
        self.assertIn("actions/download-artifact@v4",src)
        self.assertIn("videoforge.remake_sword_preview prepare",src)
        self.assertIn("videoforge.remake_sword_preview_qa",src)
        self.assertIn("needs: render-three-draft",src)
        self.assertNotIn("CODEX_PROXY_API_KEY",src)
        render=src.split("\n  render-three-draft:",1)[1].split("\n  checkpoint-in-git-host:",1)[0]
        self.assertNotIn("git push",render)
        self.assertIn("git push origin HEAD:main",src.split("\n  checkpoint-in-git-host:",1)[1])

    def test_archive_pack_uses_known_producer_schemas_and_refuses_legacy_gates(self):
        src=(ROOT/"videoforge/remake_sword_pack.py").read_text(encoding="utf-8")
        self.assertIn("production-scene-request",src)
        self.assertIn("production-rgba-request",src)
        self.assertIn("production-sword-underlay-request",src)
        self.assertIn("production-scene/v1",src)
        self.assertIn('doc.get("scene")=="c01"',src)
        self.assertIn("SAME_SOURCE_ALREADY_RENDERED_TECHNICALLY",src)
        self.assertIn("human_motion_review_required",src)
        self.assertIn("validate_package(output,source_run_id,root)",src)
        self.assertNotIn("call_proxy(",src)
        self.assertNotIn("Image.open",src)


if __name__=="__main__":
    unittest.main()
