"""Pixel-derived C01-P02 geometry: only synthetic temporary fixtures in CI.

The test source marks an anchor approved ONLY under TemporaryDirectory; no
private image art, paid provider, or actual episode asset is ever created.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import EPISODE
from videoforge.remake_rig_geometry import analyze,persist,verify_report,FILE_NAME,SCHEMA
from tests.test_remake_sword_preview import SwordPreviewTests,FFMPEG_PRESENT

ROOT=Path(__file__).resolve().parents[1]


class RemakeRigGeometryTests(unittest.TestCase):
    def fixture(self,root:Path)->Path:
        package=SwordPreviewTests().fixture(root)
        shutil.copyfile(ROOT/EPISODE/"remake-v2-motion-directions.json",
                        root/EPISODE/"remake-v2-motion-directions.json")
        return package

    def test_missing_real_package_does_not_create_fake_geometry(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            package=root/"source"
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_ARTIFACT_REQUIRED"):
                analyze(package,12345,root)
            self.assertFalse((package/FILE_NAME).exists())

    @unittest.skipUnless(FFMPEG_PRESENT,"FFmpeg container required for real PNG masks")
    def test_real_png_alpha_boxes_measured_by_pixels_without_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            package=self.fixture(root)
            report=persist(package,12345,root)
            self.assertEqual(report["schema"],SCHEMA)
            self.assertTrue(report["candidate_only"])
            self.assertTrue(report["pivots_measured_from_actual_rgba"])
            self.assertFalse(report["human_visual_approved"])
            self.assertFalse(report["official_video_approved"])
            self.assertEqual(report["paid_provider_calls"],0)
            self.assertEqual(report["neutral_roundtrip_mae_rgb"],0)
            self.assertEqual(report["parts"]["sheath"]["bbox_xyxy"],
                             [390,650,420,1090])
            self.assertEqual(report["parts"]["blade"]["bbox_xyxy"],
                             [430,620,457,1020])
            self.assertEqual(report["parts"]["hand"]["bbox_xyxy"],
                             [400,860,485,960])
            self.assertTrue(report["parts"]["underlay"]["opaque_rgb_verified"])
            self.assertEqual(report["draft_wrist_pivot_px"],[427,930])
            self.assertEqual([x["local_frame"] for x in report["directed_frame_poses"]],
                             [0,7,72,89])
            self.assertEqual(report["directed_frame_poses"][0]["progress"],0)
            self.assertEqual(report["directed_frame_poses"][2]["progress"],1)
            self.assertGreater(report["directed_frame_poses"][2]["blade_offset_px"][0],90)
            self.assertEqual(len(report["motion_direction_sha256"]),64)
            self.assertTrue((package/FILE_NAME).is_file())
            self.assertEqual(verify_report(package,12345,root),report)
            self.assertEqual(persist(package,12345,root),report) # idempotent
            path=package/FILE_NAME
            path.write_text('{"fake":true}',encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"ATTESTATION_CHANGED"):
                verify_report(package,12345,root)
            with self.assertRaisesRegex(VideoForgeError,"ALREADY_EXISTS_DIFFERENT"):
                persist(package,12345,root)

    @unittest.skipUnless(FFMPEG_PRESENT,"FFmpeg container required")
    def test_cross_origin_or_changed_cue_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            package=self.fixture(root)
            manifest_path=package/"sword-bundle.json"
            doc=json.loads(manifest_path.read_text(encoding="utf-8"))
            doc["anchor_sha256"]="f"*64
            manifest_path.write_text(json.dumps(doc),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"BUNDLE_ORIGIN"):
                analyze(package,12345,root)
            doc["anchor_sha256"]=json.loads(
                (root/EPISODE/"remake-ep01-planos.json").read_text(encoding="utf-8")
            )["identity_anchors"][0]["sha256"]
            manifest_path.write_text(json.dumps(doc),encoding="utf-8")
            motion=root/EPISODE/"remake-v2-motion-directions.json"
            cues=json.loads(motion.read_text(encoding="utf-8"))
            target=next(x for x in cues["shots"] if x["shot_id"]=="C01-P02")
            target["stages"][2]["local_frame"]=70
            target["stages"][2]["global_frame"]=130
            motion.write_text(json.dumps(cues),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"SWORD_TIMING_CHANGED"):
                analyze(package,12345,root)

    @unittest.skipUnless(FFMPEG_PRESENT,"FFmpeg container required")
    def test_alpha_color_type_mismatch_is_rejected_even_with_sha_rehash(self):
        from tests.test_remake_sword_preview import png_bytes,COL
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            package=self.fixture(root)
            source=png_bytes(alpha=True,base=COL+(255,))
            underlay=package/"underlay.png"
            underlay.write_bytes(source)
            manifest=package/"sword-bundle.json"
            j=json.loads(manifest.read_text(encoding="utf-8"))
            j["sha256"]["underlay"]=hashlib.sha256(source).hexdigest()
            manifest.write_text(json.dumps(j),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"UNDERLAY_NOT_OPAQUE"):
                analyze(package,12345,root)


if __name__=="__main__":
    unittest.main()
