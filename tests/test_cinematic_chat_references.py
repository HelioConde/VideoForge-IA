"""Style reference integrity tests, no generated pictures or network.

Only the user-approved original SHA values may be imported. A
successful archive match is still not approval for animation or upload.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from zipfile import ZipFile

from videoforge.cinematic_chat_references import (
    reference_status,check_png_source,MANIFEST,CHANNEL,VIDEO
)
from videoforge.import_cinematic_chat_references import validate_and_extract,UPLOAD_REL
from videoforge.errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]

class CinematicChatReferencesTests(unittest.TestCase):
    def test_verified_style_metadata_remains_not_renderable(self):
        r=reference_status()
        self.assertEqual(r["original_source_files_total"],2)
        self.assertEqual(len(r["samples"]),2)
        self.assertTrue(r["preferred_style_confirmed"])
        self.assertFalse(r["render_official_allowed"])
        self.assertFalse(r["official_character_bible_updated"])
        self.assertFalse(r["official_37_shots_approved"])
        self.assertEqual(r["new_image_generation_calls"],0)
        self.assertIn(r["status"],(
            "BOTH_SOURCE_FILES_PENDING_UPLOAD",
            "ONE_SOURCE_PENDING",
            "TWO_CHAT_STYLE_SOURCES_ARCHIVED",
        ))
        for s in r["samples"]:
            with self.subTest(s["id"]):
                self.assertEqual(len(s["expected_sha256"]),64)
                self.assertEqual(s["expected_dimensions_px"],[941,1672])
                self.assertFalse(s["approved_for_shot_mother"])

    def test_unsafe_image_and_hash_are_rejected(self):
        problems=check_png_source(b"not an image",941,1672,"0"*64,13)
        self.assertIn("NOT_PNG_IHDR",problems)
        self.assertIn("SHA256_MISMATCH",problems)
        self.assertIn("UNEXPECTED_FILE_SIZE",problems)

    def test_manifest_exact_original_names_and_user_praise(self):
        p=ROOT/"canal"/CHANNEL/"videos"/VIDEO/MANIFEST
        data=json.loads(p.read_text(encoding="utf8"))
        sample={x["id"]:x for x in data["approved_samples"]}
        self.assertEqual(
            sample["ref-kael-close-c12"]["original_sha256"],
            "edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f",
        )
        self.assertEqual(
            sample["ref-elara-close-c12"]["original_sha256"],
            "bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a",
        )
        self.assertFalse(data["quality_gates"]["mp4_official_rendered"])
        self.assertTrue(all(x["human_style_preference_confirmed"] for x in sample.values()))

    def test_new_bible_text_matches_user_liked_closes_without_unlocking_legacy_art(self):
        from videoforge.production_art import read_plan
        p,story=read_plan(CHANNEL,VIDEO)
        self.assertIn("capa/cachecol vinho-vermelho",p["character_bible"]["kael"])
        self.assertIn("ombreira",p["character_bible"]["kael"])
        self.assertIn("loiro-dourados",p["character_bible"]["elara"])
        self.assertIn("violeta",p["character_bible"]["elara"])
        self.assertIn("ametistas",p["character_bible"]["elara"])
        self.assertTrue(p["cinematic_direction"]["canonical_identity_migration_pending"])
        self.assertFalse(p["cinematic_direction"]["new_image_generation_allowed"])
        base=ROOT/"canal"/CHANNEL/"videos"/VIDEO
        self.assertTrue((base/"biblia-visual-v1-arquivada.md").is_file())
        current=(base/"biblia-visual.md").read_text(encoding="utf8")
        self.assertIn("Bíblia visual v2",current)
        self.assertIn("A identidade antiga continua",current)
        self.assertTrue((base/"SEM-GERACAO-NOVAS-IMAGENS.lock").is_file())

    def test_missing_zip_does_not_create_new_art_or_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(VideoForgeError,"ZIP_NOT_YET_UPLOADED"):
                validate_and_extract(root)
            self.assertEqual(list(root.iterdir()),[])

    def test_unexpected_zip_entries_cannot_be_extracted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            base=root/"canal"/CHANNEL/"videos"/VIDEO
            base.mkdir(parents=True)
            original=ROOT/"canal"/CHANNEL/"videos"/VIDEO/MANIFEST
            shutil.copyfile(original,base/MANIFEST)
            upload=root/UPLOAD_REL
            upload.parent.mkdir(parents=True)
            with ZipFile(upload,"w") as z:
                z.writestr("../../../malicious.txt","nope")
                z.writestr("another.txt","not original art")
            with self.assertRaisesRegex(VideoForgeError,"UNEXPECTED_ENTRIES"):
                validate_and_extract(root)
            self.assertFalse((base/"assets").exists())
            self.assertFalse((root/"malicious.txt").exists())

if __name__=="__main__":
    unittest.main()
