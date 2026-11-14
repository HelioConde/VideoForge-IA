"""The three originals have SHA identities and optional visual stats.

No new artwork is generated; in-memory sampling never writes a PNG.
The repository cannot claim completion until it contains the actual bytes.
"""
from __future__ import annotations

import copy
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest

from videoforge.cinematic_reference_fingerprint import (
    get_manifest,audit,dhash_rgb,EPISODE,BASELINE,
)
from videoforge.errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]

class VisualReferenceFingerprintTests(unittest.TestCase):
    def test_exact_three_baselines_are_distinct_and_never_approved_rigs(self):
        b=get_manifest()
        self.assertEqual(len(b["originals"]),3)
        self.assertEqual({x["id"] for x in b["originals"]},
                         {"kael","elara","c12-p02"})
        self.assertEqual(len({x["sha256"] for x in b["originals"]}),3)
        self.assertTrue(all(x["dimensions"]==[941,1672] for x in b["originals"]))
        self.assertFalse(b["art_generated"])
        self.assertFalse(b["rig_or_shot_approved"])
        self.assertFalse(b["pngs_saved_to_github"])
        self.assertTrue(all(x["renderStatus"] in
                            ("style_reference_only","candidate_camera_only")
                            for x in b["originals"]))

    def test_current_art_is_pending_and_fingerprint_does_not_approve_rig(self):
        d=audit()
        self.assertEqual(d["originalCount"],3)
        self.assertEqual(d["imageGenerationCalls"],0)
        self.assertEqual(d["newImageFilesCreated"],0)
        self.assertFalse(d["originalPixelsModified"])
        self.assertFalse(d["officialRenderAllowed"])
        self.assertFalse(d["rigOrShotHumanApproved"])
        self.assertEqual(d["status"],"AWAITING_ORIGINAL_BINARY_TRANSFER")
        self.assertEqual(d["exactShaVerifiedCount"],0)

    def test_corrupt_source_is_not_imported_as_valid_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            base=root/EPISODE
            base.mkdir(parents=True)
            shutil.copyfile(ROOT/EPISODE/BASELINE,base/BASELINE)
            first=get_manifest(root)["originals"][0]
            candidate=base/first["file"]
            candidate.parent.mkdir(parents=True)
            candidate.write_bytes(b"invalid input")
            with self.assertRaisesRegex(VideoForgeError,"ORIGINAL_SHA_INVALID"):
                audit(root)

    def test_sha_and_dhash_are_distinct_roles(self):
        b=get_manifest()
        for item in b["originals"]:
            self.assertEqual(len(item["sha256"]),64)
            self.assertEqual(len(item["dhash64"]),16)
            self.assertTrue(item["topColors"])
            self.assertFalse(item["renderStatus"]=="ready_for_render")

if __name__=="__main__":
    unittest.main()
