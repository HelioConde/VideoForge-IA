"""Shell behavior for permanent backup of successful and rejected visuals.

No network, no GitHub push; the *inner* commit script is stubbed in tmp dir.
All test payloads are synthetically generated local bytes, not episode art.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/"scripts/arquivar-pngs-se-existirem.sh"

class ArchiveEvenIfQaFailedTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        (self.root/"scripts").mkdir()
        (self.root/"output/channel/videos/video/imagens").mkdir(parents=True)
        inner=self.root/"scripts/persistir-imagens-gh.sh"
        inner.write_text("#!/usr/bin/env bash\nprintf '%s' \"$*\" > archive-called.txt\n",encoding="utf8")
        self.folder="output/channel/videos/video/imagens"

    def run_wrapper(self,status:str,channel:str="channel"):
        return subprocess.run(
            ["bash",str(SOURCE),channel,"video",self.folder,"1234",
             "production-art",status],
            cwd=self.root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,
        )

    def test_failed_generator_with_no_png_does_not_claim_archive(self):
        r=self.run_wrapper("failure")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("No PNG generated",r.stdout)
        self.assertFalse((self.root/"archive-called.txt").exists())

    def test_successful_generator_without_png_is_hard_failure(self):
        r=self.run_wrapper("success")
        self.assertEqual(r.returncode,2,r.stderr)
        self.assertIn("no original PNG was found",r.stderr)

    def test_failed_quality_gate_after_png_is_archived(self):
        (self.root/self.folder/"candidate.png").write_bytes(b"fixture-png-present")
        r=self.run_wrapper("failure")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("PNG_ORIGINAL_PRESERVED_EVEN_IF_VISUAL_QA_FAILED",r.stdout)
        self.assertIn("production-art",
                      (self.root/"archive-called.txt").read_text())

    def test_success_with_png_is_archived(self):
        (self.root/self.folder/"candidate.png").write_bytes(b"fixture-png-present")
        r=self.run_wrapper("success")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("channel video", (self.root/"archive-called.txt").read_text())

    def test_orphan_png_missing_channel_is_rejected(self):
        (self.root/self.folder/"candidate.png").write_bytes(b"fixture-png-present")
        r=self.run_wrapper("failure",channel="")
        self.assertNotEqual(r.returncode,0)
        self.assertIn("provenance missing",r.stderr)

    def test_unexpected_job_status_rejected(self):
        r=self.run_wrapper("unknown")
        self.assertEqual(r.returncode,2)
        self.assertIn("Invalid status",r.stderr)

if __name__=="__main__":
    unittest.main()
