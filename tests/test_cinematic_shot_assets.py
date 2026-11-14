"""QA da EDL cinematográfica e dos próprios assets de cada tomada.

Nenhuma geração de imagens, chamadas a rede ou escrita no GitHub.
Os testes preservam fail-closed e conferem 4890 quadros de 37 planos.
"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videoforge.cinematic_shot_assets import (
    build_edl, validate_edl, expected_shot_paths, validate_shot_art,
    _png_valid, _file_from_rel, CANVAS, QA_SCHEMA, RIG_SCHEMA,
)
from videoforge.errors import VideoForgeError

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"

class CinematicShotAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=build_edl(CHANNEL,VIDEO)

    def test_37_cuts_use_absolute_continuous_frames(self):
        d=self.doc
        validate_edl(d)
        self.assertEqual(d["shotCount"],37)
        self.assertEqual(d["format"]["totalFrames"],4890)
        self.assertEqual(d["format"]["durationSeconds"],163)
        self.assertEqual(d["format"]["fps"],30)
        self.assertEqual(d["shots"][0]["startFrame"],0)
        self.assertEqual(d["shots"][-1]["endFrameExclusive"],4890)
        self.assertTrue(all(s["transition"]=="hard_cut" for s in d["shots"]))
        self.assertTrue(all(
            a["endFrameExclusive"]==b["startFrame"]
            for a,b in zip(d["shots"],d["shots"][1:])
        ))

    def test_black_opening_is_renderable_without_mother(self):
        d=self.doc
        self.assertEqual(d["shots"][0]["id"],"C01-P01")
        self.assertEqual(d["shots"][0]["type"],"black")
        self.assertIsNone(d["shots"][0]["assetPaths"])
        self.assertTrue(d["shots"][0]["renderAllowed"])
        self.assertFalse(d["shots"][0]["rigApproved"])

    def test_36_visual_shots_require_their_own_mother_and_rig(self):
        d=self.doc
        visual=d["shots"][1:]
        self.assertEqual(len(visual),36)
        for s in visual:
            with self.subTest(id=s["id"]):
                self.assertFalse(s["renderAllowed"])
                self.assertFalse(s["rigApproved"])
                self.assertEqual(s["status"],"shot_art_or_rig_pending")
                self.assertIn(s["id"],s["assetPaths"]["mother"])
                self.assertIn(s["id"],s["assetPaths"]["background"])
                self.assertIn(s["id"],s["assetPaths"]["rig"])
                self.assertIn("SHOT_MOTHER_MISSING",s["blockers"])
                self.assertIn("SHOT_RIG_MISSING",s["blockers"])
                self.assertIn("NO_NEW_IMAGE_GENERATION_LOCK_ACTIVE",s["blockers"])

    def test_closeups_have_unique_media_paths_and_focus(self):
        d=self.doc
        closeups=[s for s in d["shots"] if s["type"] in ("close_up","extreme_close_up")]
        self.assertEqual(len(closeups),12)
        self.assertEqual(len({s["assetPaths"]["mother"] for s in closeups}),12)
        self.assertEqual(next(s for s in closeups if s["id"]=="C12-P01")["focus"],"kael.olhos")
        self.assertFalse(d["renderOfficialAllowed"])
        self.assertEqual(d["status"],"pipeline_pendente")
        self.assertEqual(d["unapprovedShots"],36)
        self.assertEqual(d["artAndRigApprovedShots"],0)
        self.assertTrue(d["visualReferenceConflict"])
        self.assertTrue(d["noImageGenerationLock"])
        self.assertEqual(d["pixelFilesCreated"],0)

    def test_legacy_pan_assembler_cannot_replace_cinematic_rig(self):
        from videoforge.production_assemble import prepare
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(
                VideoForgeError,"CINEMATIC_36_SHOTS_REQUIRE_OWN_MOTHERS_RIGS_AND_QA"
            ):
                prepare(CHANNEL,VIDEO,Path(temp)/"missing-images",
                        Path(temp)/"missing-audio",Path(temp)/"missing-report")

    def test_unsafe_paths_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            for s in ("../../x.png","/etc/passwd","foo.png",r"assets\windows.png"):
                with self.subTest(path=s):
                    with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_ASSET_PATH_INVALID"):
                        _file_from_rel(base,s)

    def test_missing_art_never_counts_as_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            shot={"id":"C02-P01","scene":"C02"}
            valid,failures,evidence=validate_shot_art(Path(tmp),shot,expected_shot_paths("C02-P01"))
            self.assertFalse(valid)
            self.assertEqual(evidence,{})
            self.assertIn("SHOT_MOTHER_MISSING",failures)

    def test_require_png_sha_and_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"bad.png"
            p.write_bytes(b"not a PNG")
            self.assertFalse(_png_valid(p,"0"*64,False))
            self.assertEqual(CANVAS,(1024,1536))
            self.assertEqual(len(QA_SCHEMA)>10,True)
            self.assertEqual(len(RIG_SCHEMA)>10,True)

    def test_modified_cut_disallowed(self):
        doc=copy.deepcopy(self.doc)
        doc["shots"][2]["startFrame"]+=1
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EDL_SHOTS_GAP_OVERLAP_DUPLICATE"):
            validate_edl(doc)

    def test_cannot_mark_render_ready_without_all_shots(self):
        doc=copy.deepcopy(self.doc)
        doc["renderOfficialAllowed"]=True
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EDL_GATES_INCONSISTENT"):
            validate_edl(doc)
        doc=copy.deepcopy(self.doc)
        doc["shots"][1]["renderAllowed"]=True
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EDL_UNAPPROVED_RIG_EXPOSED"):
            validate_edl(doc)

if __name__=="__main__":
    unittest.main()
