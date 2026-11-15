"""Avoid committing with git inside the Remotion GHCR image (no git installed)."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class OpeningWorkflowTests(unittest.TestCase):
    def test_render_image_never_commits_and_git_host_job_persists(self):
        yaml=(ROOT/".github/workflows/remake-opening-preview.yml").read_text(encoding="utf-8")
        pre,post=yaml.split("\n  checkpoint-in-git-host:",1)
        self.assertIn("original-sfx-remotion-preview:",pre)
        self.assertNotIn("git push",pre)
        self.assertNotIn("git add",pre)
        self.assertIn("needs: original-sfx-remotion-preview",post)
        self.assertIn("actions/download-artifact@v4",post)
        self.assertIn("python -m videoforge.remake_opening verify",post)
        self.assertIn("git push origin HEAD:main",post)
        self.assertIn("QA-C01-P01-REMAKE-V2.json",post)
        self.assertIn("retention-days: 90",pre)
        self.assertIn("--codec=h264",pre)
        self.assertIn("--audio-codec=aac",pre)
        self.assertNotIn("git add -f",post)


if __name__=="__main__":
    unittest.main()
