"""Guard tests for archived mother art vs 36 independent cinematic shots.

Reads existing files and hashes only. No network, no generated images.
"""
from __future__ import annotations

import copy
import unittest

from videoforge.cinematic_asset_inventory import audit
from videoforge.errors import VideoForgeError

class CinematicReferenceInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=audit()

    def test_fourteen_existing_mothers_cannot_auto_authorize_shot_art(self):
        d=self.data
        self.assertEqual(d["legacySceneMotherCount"],14)
        self.assertEqual(d["shotsTotal"],37)
        self.assertEqual(d["visualShots"],36)
        self.assertEqual(d["visualShotsPendingApproval"],36)
        self.assertEqual(d["faceCloseups"],12)
        self.assertFalse(d["officialMP4Allowed"])
        self.assertFalse(d["newImageGenerationAllowed"])
        self.assertFalse(d["approvedChatImagesAvailableInRepo"])

    def test_every_visible_shot_maps_to_archived_reference_only(self):
        d=self.data
        visuals=[s for s in d["shots"] if s["type"]!="black"]
        self.assertEqual(len(visuals),36)
        self.assertEqual(len(set(s["id"] for s in visuals)),36)
        for s in visuals:
            with self.subTest(s["id"]):
                self.assertFalse(s["renderApproved"])
                self.assertFalse(s["ownMotherPresent"])
                self.assertTrue(s["sourceLegacyReferenceIsNotApprovedShotArt"])
                self.assertIn(s["id"],s["requiredMother"])
                self.assertIn(s["id"],s["requiredQA"])
                self.assertEqual(len(s["sourceReferenceSha256"]),64)
                self.assertIn("SHOT_MOTHER_MISSING",s["blockers"])
                self.assertIn("NO_NEW_IMAGE_GENERATION_LOCK_ACTIVE",s["blockers"])

    def test_black_shot_has_no_art_dependency(self):
        s=self.data["shots"][0]
        self.assertEqual(s["id"],"C01-P01")
        self.assertTrue(s["renderableWithoutArt"])
        self.assertIsNone(s["priority"])

    def test_c01_legacy_guards_are_not_actual_36_shot_rigs(self):
        d=self.data
        self.assertGreaterEqual(d["legacyScene01DraftPNGs"],20)
        self.assertTrue(d["legacyScene01DraftsNotApproved"])
        shots=[s for s in d["shots"] if s.get("scene")=="C01"]
        self.assertTrue(all(
            s["sourceReferenceOnly"]=="assets/cenas-mae/cena-01.png"
            for s in shots
        ))
        self.assertTrue(all(s["renderApproved"] is False for s in shots))

if __name__=="__main__":
    unittest.main()
