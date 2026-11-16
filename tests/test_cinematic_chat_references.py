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
        self.assertTrue(r["import_read_only"])
        self.assertTrue(r["legacy_image_generation_lock_archived"])
        self.assertEqual(r["active_remake_version"],"remake-v2-20261115")
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
        self.assertTrue(p["cinematic_direction"]["new_image_generation_allowed"])
        self.assertTrue(p["remake_v2_20261115"]["new_image_generation_editorially_authorized"])
        base=ROOT/"canal"/CHANNEL/"videos"/VIDEO
        self.assertTrue((base/"biblia-visual-v1-arquivada.md").is_file())
        current=(base/"biblia-visual.md").read_text(encoding="utf8")
        self.assertIn("Bíblia visual v2",current)
        self.assertIn("A identidade antiga continua",current)
        self.assertFalse((base/"SEM-GERACAO-NOVAS-IMAGENS.lock").exists())
        self.assertTrue((base/"REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md").is_file())
        state=json.loads((base/"estado-atual.json").read_text(encoding="utf8"))
        self.assertEqual(state["active_production_version"],"remake-v2-20261115")
        self.assertFalse(state["locks"]["no_new_image_generation"])
        self.assertTrue(state["locks"]["no_youtube_upload"])

    def test_third_camera_candidate_is_recorded_but_never_implicitly_approved(self):
        r=reference_status()
        camera=r["camera_candidate_C12_P02"]
        self.assertEqual(camera["shot_id"],"C12-P02")
        self.assertEqual(
            camera["expected_sha256"],
            "01eb7c127b0699d2e502d29dacec0bb39c0e1e23bf8205fdcf6fb70976e70535",
        )
        self.assertIn(camera["status"],("UPLOAD_PENDING","EXACT_SOURCE_ARCHIVED"))
        self.assertFalse(camera["human_shot_approval"])
        self.assertFalse(camera["shot_mother_approval"])
        self.assertFalse(camera["rig_approved"])

    def test_three_originals_zip_rejects_unexpected_or_incorrect_bytes(self):
        from videoforge.import_cinematic_chat_references import UPLOAD_THREE_REL
        manifest_path=ROOT/"canal"/CHANNEL/"videos"/VIDEO/MANIFEST
        camera_path=ROOT/"canal"/CHANNEL/"videos"/VIDEO/"candidato-camera-c12-p02.json"
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            base=root/"canal"/CHANNEL/"videos"/VIDEO
            base.mkdir(parents=True)
            shutil.copyfile(manifest_path,base/MANIFEST)
            shutil.copyfile(camera_path,base/"candidato-camera-c12-p02.json")
            upload=root/UPLOAD_THREE_REL
            upload.parent.mkdir(parents=True)
            with ZipFile(upload,"w") as z:
                for filename in ("kael-close-salao.png","elara-close-trono.png",
                                 "confronto-trono-c12-p02.png"):
                    z.writestr(filename,b"wrong bytes"*200)
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_MISMATCH"):
                validate_and_extract(root)
            self.assertFalse((base/"assets").exists())
            with ZipFile(upload,"w") as z:
                for filename in ("kael-close-salao.png","elara-close-trono.png",
                                 "unexpected-camera.png"):
                    z.writestr(filename,b"wrong bytes"*200)
            with self.assertRaisesRegex(VideoForgeError,"UNEXPECTED_ENTRIES"):
                validate_and_extract(root)
            self.assertFalse((base/"assets").exists())

    def test_three_originals_positive_import_with_tiny_synthetic_png_fixtures(self):
        """Test only temporary 1x1 fixtures; never upload test images as artwork."""
        import hashlib
        import struct
        import zlib
        from unittest.mock import patch
        from videoforge.import_cinematic_chat_references import UPLOAD_THREE_REL

        def chunk(kind,data):
            return (struct.pack(">I",len(data))+kind+data+
                    struct.pack(">I",zlib.crc32(kind+data)&0xffffffff))

        def tiny_fixture(rgb):
            return (b"\x89PNG\r\n\x1a\n"+
                    chunk(b"IHDR",struct.pack(">IIBBBBB",1,1,8,2,0,0,0))+
                    chunk(b"tEXt",b"fixture\x00"+b"X"*1400)+
                    chunk(b"IDAT",zlib.compress(b"\x00"+bytes(rgb)))+
                    chunk(b"IEND",b""))

        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            base=root/"canal"/CHANNEL/"videos"/VIDEO
            base.mkdir(parents=True)
            actual_base=ROOT/"canal"/CHANNEL/"videos"/VIDEO
            manifest=json.loads((actual_base/MANIFEST).read_text(encoding="utf8"))
            candidate=json.loads(
                (actual_base/"candidato-camera-c12-p02.json").read_text(encoding="utf8")
            )
            files={
                "kael-close-salao.png":tiny_fixture([1,2,3]),
                "elara-close-trono.png":tiny_fixture([5,6,7]),
                "confronto-trono-c12-p02.png":tiny_fixture([9,10,11]),
            }
            for sample in manifest["approved_samples"]:
                raw=files[Path(sample["expected_repo_path"]).name]
                sample["dimensions_px"]=[1,1]
                sample["original_sha256"]=hashlib.sha256(raw).hexdigest()
                sample["expected_bytes"]=len(raw)
            raw=files["confronto-trono-c12-p02.png"]
            candidate.update({
                "original_width_px":1,"original_height_px":1,
                "source_sha256":hashlib.sha256(raw).hexdigest(),
                "original_bytes":len(raw),
            })
            (base/MANIFEST).write_text(json.dumps(manifest),encoding="utf8")
            (base/"candidato-camera-c12-p02.json").write_text(
                json.dumps(candidate),encoding="utf8"
            )
            (base/"SEM-GERACAO-NOVAS-IMAGENS.lock").write_text(
                "PROHIBIT AI IMAGE GENERATION",encoding="utf8"
            )
            bundle=root/UPLOAD_THREE_REL
            bundle.parent.mkdir(parents=True)
            with ZipFile(bundle,"w") as z:
                for name,raw in files.items(): z.writestr(name,raw)
            fake_status={
                "original_source_files_sha_verified":2,
                "camera_candidate_C12_P02":{"source_verified":True},
            }
            with patch(
                "videoforge.import_cinematic_chat_references.reference_status",
                return_value=fake_status,
            ):
                out=validate_and_extract(root)
            self.assertEqual(out["original_source_files_sha_verified"],2)
            for sample in manifest["approved_samples"]:
                name=Path(sample["expected_repo_path"]).name
                self.assertEqual((base/sample["expected_repo_path"]).read_bytes(),files[name])
            self.assertEqual(
                (base/candidate["expected_repo_path"]).read_bytes(),
                files["confronto-trono-c12-p02.png"],
            )
            # No final scene-mother, motion rigs or MP4 can be generated.
            self.assertFalse((base/"assets/planos").exists())
            self.assertFalse((base/"video.mp4").exists())

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
