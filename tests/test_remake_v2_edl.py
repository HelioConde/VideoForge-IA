"""V2 official EDL keeps 40-shot storyboard isolated from historical 37-shot EDL."""
import copy
import json
from pathlib import Path
import unittest

from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import EPISODE
from videoforge.remake_v2_edl import build,NAME,SCHEMA

ROOT=Path(__file__).resolve().parents[1]


class RemakeV2EdlTests(unittest.TestCase):
    def test_committed_40_shot_v2_edl_matches_both_current_sources(self):
        edl=build()
        committed=json.loads((ROOT/EPISODE/NAME).read_text(encoding="utf-8"))
        self.assertEqual(edl,committed)
        self.assertEqual(edl["schema"],SCHEMA)
        self.assertEqual(edl["shotCount"],40)
        self.assertEqual(edl["artRequiredShots"],39)
        self.assertEqual(edl["unapprovedShots"],39)
        self.assertEqual(edl["scenes"],14)
        self.assertEqual(edl["format"]["totalFrames"],4890)
        self.assertFalse(edl["renderOfficialAllowed"])
        self.assertFalse(edl["youtubeUploaded"])
        self.assertTrue(all(s["renderAllowed"] is False for s in edl["shots"][1:]))

    def test_new_inserts_have_real_40_shot_ranges_and_origin_contracts(self):
        edl=build()
        by_id={s["id"]:s for s in edl["shots"]}
        self.assertEqual(len(by_id),40)
        for sid,start,end in (
            ("C01-P05",310,360),
            ("C08-P04",2880,2940),
            ("C12-P04",4290,4350),
        ):
            s=by_id[sid]
            self.assertEqual((s["startFrame"],s["endFrameExclusive"]),(start,end))
            self.assertTrue(s["assetPaths"]["mother"].startswith("assets/remake-v2/"+sid))
            self.assertFalse(s["humanVisualApproved"])
            self.assertIsInstance(s["camera"]["description"],str)
            self.assertIsInstance(s["spokenOrSfx"],str)

    def test_37_shot_legacy_edl_remains_immutable_reference(self):
        old=json.loads((ROOT/EPISODE/"timeline-cinematografica.json").read_text(encoding="utf-8"))
        self.assertEqual(old["shotCount"],37)
        self.assertEqual(old["legacy_scope"],"pre_remake_cinematic_edl_immutable_reference")
        self.assertEqual(old["renderOfficialAllowed"],False)
        self.assertEqual(build()["legacy37ShotEdlUntouched"],"timeline-cinematografica.json")

    def test_original_sword_audio_is_audited_but_not_fake_approved(self):
        edl=build()
        opening=edl["shots"][0]
        qa=json.loads((ROOT/EPISODE/"QA-C01-P01-REMAKE-V2.json").read_text(encoding="utf-8"))
        self.assertEqual(opening["id"],"C01-P01")
        self.assertEqual(opening["audioSha256"],qa["audio_sha256"])
        self.assertEqual(opening["technicalPreviewArtifact"],qa["artifact_name"])
        self.assertFalse(opening["humanVisualApproved"])
        self.assertTrue(edl["audioRequiresShaVerifiedBytesBeforeOfficialRender"])

    def test_shot_coverage_is_continuous_and_retains_special_sword(self):
        shots=build()["shots"]
        cursor=0
        for shot in shots:
            self.assertEqual(shot["startFrame"],cursor)
            self.assertGreater(shot["endFrameExclusive"],cursor)
            cursor=shot["endFrameExclusive"]
        self.assertEqual(cursor,4890)
        self.assertEqual((shots[1]["id"],shots[1]["startFrame"],
                          shots[1]["endFrameExclusive"]),("C01-P02",60,150))


if __name__=="__main__":
    unittest.main()
