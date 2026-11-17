"""Bíblia Visual: histórico real SHA, não-aprovação e idempotência."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import ROOT
from videoforge.visual_bible import build, sync, _markdown


class VisualBibleTests(unittest.TestCase):
    def test_ep01_bible_grows_without_limiting_40_story_shots(self):
        bible = ROOT / "canal/alchemy-lab/biblia-visual"
        index = json.loads((bible / "INDEX-BIBLIA.json").read_text(encoding="utf-8"))
        count = sum(len(v) for v in index["categorias"].values())
        self.assertGreaterEqual(count, 39)\n        self.assertEqual(len({(cat,x['id']) for cat,items in index['categorias'].items() for x in items}),count)\n        self.assertIn('arken-muralhas',[x['id'] for x in index['categorias']['cenarios']])\n        self.assertFalse(next(x['aprovacao_mestra'] for x in index['categorias']['cenarios'] if x['id']=='arken-muralhas'))
        plan = json.loads((bible / "FILA-EP01.json").read_text(encoding="utf-8"))
        self.assertEqual(len(plan["tomadas"]), 40)
        self.assertNotIn("rainha", [actor for s in plan["tomadas"] for actor in s["personagens"]])
        self.assertTrue(plan["hold"])

    def test_archived_sha_and_known_rejections_are_not_approved(self):
        index, registry = build("alchemy-lab")
        self.assertGreaterEqual(registry["total_arquivadas"], 6)
        records = {x["sha256"]: x for x in registry["geracoes"]}
        v3 = records["605ccd361ad9a867eb8b92948010fdbb7d87a031d8b3601c663d815917b1b6cc"]
        v4 = records["0bb72ea525d81b6e935af49eb873d308a88ce8230a4a2b7d89c62d5d0e88a8dc"]
        self.assertEqual(v3["status"], "em_revisao")
        self.assertIn("pose", v3["escopo_proibido"])
        self.assertEqual(v4["status"], "rejeitado")
        self.assertEqual(v4["github_run_id"], 43990928355)
        self.assertFalse(v4["aprovacao_automatica"])
        self.assertNotIn("rainha", [x["asset"] for x in registry["geracoes"]])

    def test_legacy_channel_images_have_provenance(self):
        _, registry = build("otaku-br")
        self.assertGreaterEqual(registry["total_arquivadas"], 5)
        self.assertTrue(all(x["status"] == "gerado" for x in registry["geracoes"]))
        self.assertTrue(all(x["sha256"] for x in registry["geracoes"]))

    def test_sync_repeat_and_fail_closed_on_corrupt_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = ROOT / ("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/"
                             "assets/geracoes/production-art-request/43990928355")
            dest = root / ("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/"
                           "assets/geracoes/production-art-request/43990928355")
            dest.mkdir(parents=True)
            for item in source.iterdir():
                if item.is_file():
                    shutil.copyfile(item, dest / item.name)
            first = sync("alchemy-lab", root)
            self.assertEqual(first["images"], 1)
            second = sync("alchemy-lab", root)
            self.assertEqual(second["changed_files"], 0)
            registry_path = root / "canal/alchemy-lab/biblia-visual/REGISTRO-GERACOES.json"
            rows = json.loads(registry_path.read_text())["geracoes"]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "gerado")
            manifest = dest / "manifesto-geracoes.json"
            obj = json.loads(manifest.read_text())
            obj["images"][0]["sha256"] = "0" * 64
            manifest.write_text(json.dumps(obj))
            with self.assertRaisesRegex(VideoForgeError, "SHA_OR_SIZE_MISMATCH"):
                build("alchemy-lab", root)

    def test_permanent_archiver_commits_png_and_bible_together(self):
        script = (ROOT / "scripts/persistir-imagens-gh.sh").read_text(encoding="utf-8")
        self.assertIn('python -m videoforge.visual_bible --channel "$CHANNEL"', script)
        self.assertIn('git add -f -- "$DEST"', script)
        self.assertIn('git add -A -- "$BIBLE_DIR"', script)
        self.assertLess(script.index("python -m videoforge.visual_bible"),
                        script.index("git commit"))
        self.assertLess(script.index('git add -A -- "$BIBLE_DIR"'),
                        script.index("git commit"))

    def test_no_approval_without_review_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bible = root / "canal/alchemy-lab/biblia-visual"
            bible.mkdir(parents=True)
            review = {"schema": "videoforge/visual-bible-reviews/v1",
                      "channel": "alchemy-lab",
                      "by_sha256": {"a" * 64: {"status": "aprovado"}}}
            (bible / "REVISOES-MANUAIS.json").write_text(json.dumps(review))
            with self.assertRaisesRegex(VideoForgeError, "APPROVAL_REQUIRES_HUMAN_EVIDENCE"):
                build("alchemy-lab", root)


if __name__ == "__main__":
    unittest.main()
