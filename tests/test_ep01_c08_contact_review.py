"""A review board is useful evidence, never an authorization for a rig."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw
from videoforge import ep01_c08_contact_review as q


class C08ContactReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="ep01-c08-contact-test-")
        cls.destination=Path(cls.temp.name)/"review"
        cls.report=q.produce(q.ROOT,cls.destination)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_grounded_upper_hand_gap_lower_overlay_with_no_false_grip_approval(self):
        r=self.report
        self.assertEqual(r["schema"],q.SCHEMA)
        self.assertEqual(r["new_paid_proxy_calls"],0)
        self.assertEqual(r["new_generated_images"],0)
        self.assertEqual(r["original_pngs_overwritten"],0)
        self.assertFalse(r["human_visual_approval"])
        self.assertFalse(r["upper_hand_contact_approved"])
        self.assertFalse(r["lower_hand_contact_approved"])
        self.assertFalse(r["rig_ready"])
        self.assertFalse(r["animated_episode_ready"])
        self.assertFalse(r["youtube_published"])
        self.assertEqual(r["geometry_alpha"]["upper_hand"]["opaque_intersection_px"],0)
        self.assertGreaterEqual(
            r["geometry_alpha"]["upper_hand"]["chebyshev_proximity_radius_px"],1)
        self.assertGreater(r["geometry_alpha"]["lower_hand"]["opaque_intersection_px"],100)
        self.assertFalse(r["geometry_alpha"]["lower_hand"]["can_prove_correct_grip"])

    def test_exact_three_archived_images_and_review_files_are_byte_verified(self):
        r=self.report
        self.assertEqual(len(r["separate_source_png_sha256"]),3)
        self.assertEqual(set(r["separate_source_png_sha256"]),set(q.SOURCE_PARTS))
        proof=q.verify_report(q.ROOT,self.destination)
        self.assertEqual(proof["rechecked_source_images"],3)
        self.assertEqual(proof["contact_regions"],2)
        self.assertTrue(proof["qa_technical_verified"])
        self.assertFalse(proof["art_visual_approved"])
        self.assertFalse(proof["rig_ready"])
        with Image.open(self.destination/q.PREVIEW) as im:
            self.assertEqual(im.size,(1560,415))
        self.assertEqual(q.sha(self.destination/q.PREVIEW),r["preview_board_sha256"])

    def test_exact_nine_shot_timeline_and_240_source_poses_match(self):
        row=self.report["narrative_42_shot_handoff"]
        self.assertEqual(row["total_shots"],42)
        self.assertEqual(row["regional_shots_matched"],9)
        self.assertEqual(row["c08p02_frame_range"],[2550,2680])
        self.assertEqual(row["c08p03_frame_range"],[2680,2790])
        self.assertEqual(row["kinematic_frames"],240)
        self.assertEqual(row["at_cut_yaw_degrees"],[90.0,90])
        self.assertTrue(row["kinematic_continuity"])
        self.assertFalse(row["artistic_axis_and_visual_contact_approved"])
        self.assertFalse(row["real_wheel_rgba_parts_present"])

    def test_modified_review_png_and_false_approval_cannot_pass_independent_qa(self):
        report_file=self.destination/"c08-p02-contact-review.json"
        original=report_file.read_text(encoding="utf-8")
        try:
            for field,val in (
                ("human_visual_approval",True),
                ("rig_ready",True),
                ("upper_hand_contact_approved",True),
                ("wheel_sprites_independently_generated",True),
                ("new_paid_proxy_calls",1),
            ):
                d=json.loads(original)
                d[field]=val
                report_file.write_text(json.dumps(d),encoding="utf-8")
                with self.subTest(field=field),self.assertRaises(ValueError):
                    q.verify_report(q.ROOT,self.destination)
        finally:
            report_file.write_text(original,encoding="utf-8")

    def test_missing_or_mutated_original_sha_cannot_masquerade_as_independent_art(self):
        with patch.dict(q.source_comp.RECORDS["kael"],{"sha256":"0"*64}):
            with self.assertRaises(ValueError):
                q.source_comp.verified_sources(q.ROOT)

    def test_cannot_overwrite_original_or_earlier_review(self):
        with self.assertRaises(ValueError):
            q.produce(q.ROOT,q.ROOT/"canal"/"alchemy-lab"/"videos")
        with self.assertRaises(ValueError):
            q.produce(q.ROOT,self.destination)

    def test_only_source_alphas_not_anatomical_classification(self):
        k=Image.new("RGBA",q.source_comp.CANVAS,(0,0,0,0))
        c=Image.new("RGBA",q.source_comp.CANVAS,(0,0,0,0))
        ImageDraw.Draw(k).rectangle((565,620,572,637),fill=(100,100,100,255))
        ImageDraw.Draw(c).rectangle((578,620,585,637),fill=(100,100,100,255))
        row=q.mask_stats(k,c,q.ROIS["upper_hand"])
        self.assertEqual(row["opaque_intersection_px"],0)
        self.assertGreaterEqual(row["chebyshev_proximity_radius_px"],1)
        self.assertFalse(row["can_prove_correct_grip"])
        ImageDraw.Draw(c).rectangle((570,620,578,637),fill=(100,100,100,255))
        row=q.mask_stats(k,c,q.ROIS["upper_hand"])
        self.assertGreater(row["opaque_intersection_px"],0)
        self.assertFalse(row["can_prove_correct_grip"])


if __name__=="__main__":
    unittest.main()
