"""Regression: every main VideoForge image workflow persists originals.

Workflow archives are durable Git files; Actions artifacts are temporary.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOWS=[
 "production-art.yml",
 "production-art-by-request.yml",
 "production-scene.yml",
 "production-scene-by-request.yml",
 "production-scenes-batch-by-request.yml",
 "production-rgba-part-by-request.yml",
 "production-rig-three-art-candidate.yml",
 "production-scene-mother-layers.yml",
 "proxy-images.yml",
]

class MainImageGenerationPersistenceWiringTests(unittest.TestCase):
    def test_main_generation_workflows_persist_origin_and_backup_artifacts(self):
        for name in WORKFLOWS:
            with self.subTest(workflow=name):
                s=(ROOT/".github"/"workflows"/name).read_text()
                self.assertIn("contents: write",s)
                self.assertIn("persist-credentials: true",s)
                self.assertIn("scripts/arquivar-pngs-se-existirem.sh",s)
                self.assertIn("actions/upload-artifact@v4",s)
                self.assertIn("always()",s)
                self.assertLess(s.index("scripts/arquivar-pngs-se-existirem.sh"),
                                s.rindex("actions/upload-artifact@v4"))

    def test_image_generation_lock_still_applies_to_alchemy(self):
        s=(ROOT/".github"/"workflows"/"proxy-images.yml").read_text()
        self.assertIn("assert_image_generation_allowed",s)
        policy=(ROOT/"videoforge"/"image_generation_policy.py").read_text()
        self.assertIn("mmorpg-conquiste-a-princesa-ep01",policy)

    def test_archive_script_never_force_pushes_or_swaps_channel(self):
        script=(ROOT/"scripts"/"persistir-imagens-gh.sh").read_text()
        self.assertIn("python -m videoforge.persist_generated_assets",script)
        self.assertIn('git add -f -- "$DEST"',script)
        self.assertIn("git push origin HEAD:main",script)
        self.assertNotIn("git push --force",script)
        self.assertNotIn("git reset --hard",script)

    def test_archive_wrapper_includes_failed_visual_qa_protection(self):
        script=(ROOT/"scripts"/"arquivar-pngs-se-existirem.sh").read_text()
        self.assertIn("PRIOR_STATUS",script)
        self.assertIn("persistir-imagens-gh.sh",script)
        self.assertIn("PNG_ORIGINAL_PRESERVED_EVEN_IF_VISUAL_QA_FAILED",script)
        self.assertIn("if [[ \"$PRIOR_STATUS\" == success ]]",script)
        self.assertIn("No PNG generated",script)

    def test_matrix_jobs_get_independent_per_run_producer_paths(self):
        batch=(ROOT/".github"/"workflows"/"production-scenes-batch-by-request.yml").read_text()
        rig=(ROOT/".github"/"workflows"/"production-rig-three-art-candidate.yml").read_text()
        self.assertIn("scene-batch-"+"$"+"{{ matrix.scene }}",batch)
        self.assertIn("rig-three-"+"$"+"{{ matrix.part }}",rig)

if __name__=="__main__":
    unittest.main()
