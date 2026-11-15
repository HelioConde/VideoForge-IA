"""C01-P02 paid image producer workflows must remain manual and fail-closed."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class SwordProducerWorkflowTests(unittest.TestCase):
    def test_paid_generation_cannot_start_automatically(self):
        yaml=(ROOT/".github/workflows/remake-sword-component.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:",yaml)
        self.assertIn("github.event_name == 'workflow_dispatch'",yaml)
        self.assertIn("github.event_name == 'push'",yaml)
        jobs=yaml.split("\njobs:",1)[1]
        pay=jobs.split("\n  one-real-image-only-manual:",1)[1]
        free=jobs.split("\n  validate-code-no-cost:",1)[1].split(
            "\n  one-real-image-only-manual:",1)[0]
        self.assertNotIn("CODEX_PROXY_API_KEY",free)
        self.assertNotIn("gh workflow run",yaml)
        self.assertIn('if: github.event_name == ',pay)
        self.assertIn("image_generation_allowed",(
            ROOT/"videoforge/remake_sword_source.py").read_text(encoding="utf-8"))
        self.assertIn("REMAKE_SWORD_PAID_OR_ORIGIN_BLOCKED",pay)
        self.assertLess(pay.index("BARRAR geracao"),pay.index("Validar proxy configurado"))
        self.assertLess(pay.index("Validar proxy configurado"),
                        pay.index("Gerar UMA imagem candidata"))
        self.assertIn("production-sword-underlay-request",yaml)
        self.assertIn("production-rgba-request",yaml)
        self.assertIn("arquivar-pngs-se-existirem.sh",yaml)
        self.assertIn("actions/upload-artifact@v4",yaml)
        self.assertNotIn("youtube_upload: true",yaml)
        self.assertNotIn("retry_429",yaml)

    def test_real_source_producer_reuses_existing_archive_and_never_auto_approves(self):
        src=(ROOT/"videoforge/remake_sword_source.py").read_text(encoding="utf-8")
        self.assertIn("from .remake_sword_pack import _find_mother",src)
        self.assertIn('mother["run_id"]!=source_run_id',src)
        self.assertIn("scene_mother_sha256",src)
        self.assertIn("C01-P02",src)
        self.assertIn("human_visual_approval",src)
        self.assertIn("rejected_png_or_alpha_invalid",src)
        self.assertIn("call_proxy",src)
        self.assertNotIn("retry",src.split("def produce(",1)[1].split("def main(",1)[0])
        self.assertNotIn("youtube_upload=True",src)
        self.assertNotIn("human_visual_approval=True",src)

if __name__=="__main__":
    unittest.main()
