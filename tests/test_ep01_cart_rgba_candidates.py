"""Source-bound tests for genuine but unapproved EP01 cart RGBA cutouts."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

from videoforge.ep01_cart_rgba_candidates import (
    ALL_LAYERS, PIECES, ROOT, build_candidates, make_masks,
    pinned_source, seed_mask, sha256,
)


class CartRGBAExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="vf-ep01-parts-")
        cls.dest = Path(cls.tmp.name) / "candidates"
        cls.original, cls.original_sha = pinned_source(ROOT)
        cls.report = build_candidates(ROOT, cls.dest)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_seven_real_full_size_rgba_pngs_with_transparent_pixels(self):
        self.assertEqual(self.report["layer_order"], list(ALL_LAYERS))
        self.assertEqual(len(self.report["layer_output_sha256"]), 7)
        for name in ALL_LAYERS:
            with self.subTest(name=name), Image.open(self.dest / (name + ".png")) as im:
                self.assertEqual(im.size, (1053, 1493))
                self.assertEqual(im.mode, "RGBA")
                alpha = np.array(im.getchannel("A"))
                self.assertEqual(int(alpha.max()), 255)
                if name != ALL_LAYERS[0]:
                    self.assertEqual(int(alpha.min()), 0)
                    self.assertGreater(int(np.count_nonzero(alpha)), 500)
                    self.assertTrue(np.all((alpha == 0) | (alpha == 255)))
                self.assertEqual(sha256(self.dest / (name + ".png")),
                                 self.report["layer_output_sha256"][name])

    def test_bit_exact_original_pose_recomposition_and_no_double_owned_pixels(self):
        raw = cv2.imread(str(self.original), cv2.IMREAD_COLOR)
        masks, detail = make_masks(raw)
        self.assertEqual(detail["mask_ownership_overlaps"], 0)
        seen = np.zeros(raw.shape[:2], dtype=np.bool_)
        for part in PIECES:
            self.assertFalse(np.any(seen & masks[part]))
            seen |= masks[part]
        composite = cv2.cvtColor(np.array(Image.open(
            self.dest / "source-pose-recomposed.png").convert("RGB")), cv2.COLOR_RGB2BGR)
        self.assertTrue(np.array_equal(raw, composite))
        self.assertEqual(self.report["source_pose_pixel_error"], 0)
        self.assertTrue(self.report["source_pose_recomposes_bit_exact"])
        self.assertEqual(self.report["source_sha256"], self.report["source_sha256_after"])

    def test_inpaint_and_semantic_edges_are_never_claimed_approved(self):
        status = self.report
        self.assertTrue(status["background_inpainted_artifact_created"])
        for flag in ("background_underlay_art_quality_verified",
                     "semantic_silhouettes_verified",
                     "visual_identity_verified",
                     "original_visual_bible_master_approved",
                     "production_ready", "rig_ready", "layer_split_verified",
                     "physical_animation_applied"):
            self.assertIs(status[flag], False, flag)
        self.assertEqual(status["independent_visual_qa"], "required_not_completed")
        self.assertEqual(status["new_generated_images"], 0)
        self.assertEqual(status["real_model_requests"], 0)
        self.assertEqual(status["youtube_publications"], 0)
        self.assertEqual(status["original_png_overwrites"], 0)
        self.assertTrue((self.dest / "semantic-mask-overlay.jpg").is_file())
        self.assertTrue((self.dest / "six-cutouts-contact.jpg").is_file())

    def test_source_sha_or_visual_bible_gate_drift_fails_closed(self):
        from videoforge.ep01_continuity_motion import read
        plan = read(ROOT)
        wrong = copy.deepcopy(plan)
        wrong["source_reference_shas"]["C08-P02"]["sha256"] = "0" * 64
        with patch("videoforge.ep01_cart_rgba_candidates.read_motion", return_value=wrong):
            with self.assertRaises(ValueError):
                pinned_source(ROOT)
        wrong = copy.deepcopy(plan)
        wrong["QA"]["rig_ready"] = True
        with patch("videoforge.ep01_cart_rgba_candidates.read_motion", return_value=wrong):
            with self.assertRaises(ValueError):
                pinned_source(ROOT)
        wrong = copy.deepcopy(plan)
        wrong["rules"]["allow_image_generation"] = True
        with patch("videoforge.ep01_cart_rgba_candidates.read_motion", return_value=wrong):
            with self.assertRaises(ValueError):
                pinned_source(ROOT)

    def test_output_cannot_overwrite_source_or_existing_files(self):
        with self.assertRaises(ValueError):
            build_candidates(ROOT, ROOT / "canal" / "alchemy-lab" / "videos")
        with self.assertRaises(ValueError):
            build_candidates(ROOT, self.dest)

    def test_seed_masks_are_nonempty_at_documented_resolution(self):
        for part in PIECES:
            with self.subTest(name=part):
                mask = seed_mask(part)
                self.assertEqual(mask.shape, (452, 320))
                self.assertGreater(int(np.count_nonzero(mask)), 300)
        with self.assertRaises(ValueError):
            seed_mask("independent_hand_rgba")


if __name__ == "__main__":
    unittest.main()
