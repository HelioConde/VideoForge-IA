"""Verifica arquivos arquivados V3 sem alterar identidade ou figurino."""
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from videoforge.errors import VideoForgeError
from videoforge.wardrobe_roi_archive import audit, check_archive_bytes, secure_rel


class ROIV3ArchiveTests(unittest.TestCase):
    def test_real_archive_eight_masks_and_no_approval(self):
        result = audit()
        self.assertEqual(result["checked_masks"], 8)
        self.assertTrue(result["context_board_sha_verified"])
        self.assertEqual(result["approved_semantic_masks"], 0)
        self.assertEqual(result["approved_pairs"], 0)
        self.assertTrue(result["r2_blocked"])
        self.assertEqual(result["provider_calls"], 0)
        self.assertTrue(all(row["archived_png_verified"] for row in result["rows"]))

    def test_hash_and_rgb_tampering_fail_closed(self):
        src = Image.new("RGB", (20, 20), (35, 75, 105))
        before = Image.new("L", src.size, 255)
        after = before.copy()
        after.putpixel((2, 2), 0)
        def encode(im):
            data = io.BytesIO()
            im.save(data, format="PNG")
            return data.getvalue()
        good = src.convert("RGBA")
        good.putalpha(after)
        blob = encode(good)
        sha = hashlib.sha256(blob).hexdigest()
        self.assertTrue(check_archive_bytes(blob, sha, src, before, after,
                                            [0, 0, 20, 20], 1)["rgb_matches_source_crop"])
        with self.assertRaisesRegex(VideoForgeError, "SHA_MISMATCH"):
            check_archive_bytes(blob, "0" * 64, src, before, after,
                                [0, 0, 20, 20], 1)
        bad = good.copy()
        bad.putpixel((4, 4), (200, 75, 105, 255))
        blob_bad = encode(bad)
        with self.assertRaisesRegex(VideoForgeError, "RGB_CHANGED"):
            check_archive_bytes(blob_bad, hashlib.sha256(blob_bad).hexdigest(),
                                src, before, after, [0, 0, 20, 20], 1)

    def test_archive_path_cannot_escape_episode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "assets/qa-roi-exclusions-v3/test.png"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"test")
            self.assertEqual(secure_rel(root, "assets/qa-roi-exclusions-v3/test.png",
                                        "assets/qa-roi-exclusions-v3/"), target)
            for path in ("../secret.png", "/etc/passwd",
                         "assets/qa-roi-exclusions-v3/../../secret.png",
                         "assets/qa-roi-exclusions-v2/test.png"):
                with self.assertRaisesRegex(VideoForgeError, "UNSAFE_PATH"):
                    secure_rel(root, path, "assets/qa-roi-exclusions-v3/")


if __name__ == "__main__":
    unittest.main()
