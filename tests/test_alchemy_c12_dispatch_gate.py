"""C12 archive-dispatch tests: no real or generated images used."""
import copy
import unittest
from videoforge.c12_dispatch_gate import C12DispatchError, classify_preflight


def base():
    return {
        "schema": "videoforge/c12-technical-three-preflight/v1",
        "status": "ASSETS_PENDING",
        "technical_preview_only": True,
        "official_video_approved": False,
        "human_visual_approved": False,
        "image_generation_calls": 0,
        "verified": [],
        "errors": ["MISSING_OR_SYMLINK:some/source.png"],
    }


class DispatchAfterArchiveTest(unittest.TestCase):
    def test_wait_for_missing_original_pngs_not_a_false_success(self):
        self.assertEqual(classify_preflight(base()),
                         "WAIT_FOR_EXISTING_SOURCE_BYTES")

    def test_ready_only_for_nine_distinct_sha_verified_origins(self):
        p = base()
        p["status"] = "READY_FOR_TECHNICAL_THREECANVAS_RENDER"
        p["errors"] = []
        p["verified"] = [{"id": f"part-{i}", "sha256": f"{i:064x}"}
                         for i in range(1, 10)]
        self.assertEqual(classify_preflight(p), "READY")
        p["verified"].pop()
        with self.assertRaises(C12DispatchError):
            classify_preflight(p)

    def test_reject_duplicate_verified_image(self):
        p = base()
        p["status"] = "READY_FOR_TECHNICAL_THREECANVAS_RENDER"
        p["errors"] = []
        p["verified"] = [{"id": f"part-{i}", "sha256": f"{i:064x}"}
                         for i in range(1, 10)]
        p["verified"][8] = copy.deepcopy(p["verified"][7])
        with self.assertRaises(C12DispatchError):
            classify_preflight(p)

    def test_reject_unexpected_missing_or_altered_art(self):
        p = base()
        p["errors"] = ["SHA_MISMATCH:some/source.png"]
        with self.assertRaises(C12DispatchError):
            classify_preflight(p)
        p["errors"] = ["PNG_DIMENSIONS_OR_RGBA_INVALID:file.png"]
        with self.assertRaises(C12DispatchError):
            classify_preflight(p)

    def test_does_not_dispatch_if_any_image_generation_was_used(self):
        p = base()
        p["image_generation_calls"] = 1
        with self.assertRaises(C12DispatchError):
            classify_preflight(p)

    def test_does_not_dispatch_an_official_or_human_approved_fake_report(self):
        for key in ("official_video_approved", "human_visual_approved"):
            p = base()
            p[key] = True
            with self.assertRaises(C12DispatchError):
                classify_preflight(p)


if __name__ == "__main__":
    unittest.main()
