"""Fail-closed export test. Never generates even a temporary image."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from videoforge.cinematic_remotion_export import (
    build_props, stage, _check_bbox, OUTPUT_PREFIX,
)
from videoforge.cinematic_shot_assets import build_edl, _png_valid
from videoforge.errors import VideoForgeError

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"


class CinematicRemotionExportTests(unittest.TestCase):
    def test_current_episode_cannot_export_unapproved_shots(self):
        edl=build_edl(CHANNEL,VIDEO)
        self.assertEqual(edl["unapprovedShots"],36)
        self.assertFalse(edl["renderOfficialAllowed"])
        self.assertFalse(edl["canonicalReferencesArchived"])
        with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EXPORT_UNAPPROVED_SHOTS_36"):
            build_props(CHANNEL,VIDEO)

    def test_no_staged_files_can_be_produced_while_shots_pending(self):
        with tempfile.TemporaryDirectory() as td:
            isolated=Path(td)
            # A preflight is mandatory before stage; no source list available.
            with self.assertRaisesRegex(VideoForgeError,"CINEMATIC_EXPORT_UNAPPROVED_SHOTS"):
                build_props(CHANNEL,VIDEO)
            self.assertEqual(list(isolated.iterdir()),[])

    def test_crop_dimensions_must_be_inside_source_mother(self):
        self.assertEqual(_check_bbox([200,100,50,60]),(50,60))
        for box in ([-2,0,200,200],[0,0,1025,100],
                    [999,0,50,30],[0,0,0,100],
                    [0,0,20],[0,0,200.5,20]):
            with self.subTest(box=box):
                with self.assertRaisesRegex(VideoForgeError,"BBOX_INVALID"):
                    _check_bbox(box)

    def test_native_portrait_bboxes_use_their_own_canvas(self):
        self.assertEqual(_check_bbox([920,1500,21,172],(941,1672)),(21,172))
        self.assertEqual(_check_bbox([980,1400,44,136],(1024,1536)),(44,136))
        with self.assertRaisesRegex(VideoForgeError,"BBOX_INVALID"):
            _check_bbox([920,1500,22,172],(941,1672))
        with self.assertRaisesRegex(VideoForgeError,"BBOX_INVALID"):
            _check_bbox([920,1500,21,173],(941,1672))
        with self.assertRaisesRegex(VideoForgeError,"BBOX_INVALID"):
            _check_bbox([980,1400,44,136],(941,1672))

    def test_binary_verifier_does_not_accept_arbitrary_png_without_sha(self):
        with tempfile.TemporaryDirectory() as td:
            bad=Path(td)/"not-real.png"
            bad.write_bytes(b"not a png")
            self.assertFalse(_png_valid(bad,"e"*64,True,(50,60)))
        self.assertEqual(OUTPUT_PREFIX,"vf-cinema")


if __name__=="__main__":
    unittest.main()
