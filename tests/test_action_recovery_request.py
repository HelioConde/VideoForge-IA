"""Safe, offline regression tests for artifact recovery request validation."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from videoforge.action_recovery_request import validate, verify_download

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "docs/requests/recuperar-imagens-do-actions.json"

class ActionRecoveryRequestTests(unittest.TestCase):
    def setUp(self):
        self.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_exact_existing_paid_artifact_and_no_provider_calls(self):
        info = validate(self.request)
        self.assertEqual(info["run"], 44740269740)
        self.assertEqual(info["producer"], "production-proxy-separate-part-v1")
        self.assertEqual(info["expected_png_name"], "c10-p01-background-clean.png")
        self.assertEqual(info["expected_png_sha256"],
                         "ff290bddb995f049fb2a95def7fcb0babe3f8195781f1340284225f2ae00f460")
        self.assertIs(self.request["generate_new_image"], False)
        self.assertIs(self.request["render_mp4"], False)
        self.assertIs(self.request["youtube_upload"], False)

    def test_safety_flags_wrong_identity_or_producer_are_rejected(self):
        changes = [
            ("generate_new_image", True),
            ("youtube_upload", True),
            ("render_mp4", True),
            ("source_run_id", 1),
            ("artifact_name", "vf-ep01-part-C11-P01-background-clean-44740269740"),
            ("archive_producer", "production-art"),
            ("channel", "otaku-br"),
            ("expected_png_sha256", "0" * 64),
        ]
        for key, value in changes:
            with self.subTest(key=key):
                invalid = dict(self.request, **{key:value})
                if key == "expected_png_sha256":
                    # A different well-formed hash is rejected after download.
                    with tempfile.TemporaryDirectory() as tmp:
                        folder = Path(tmp)
                        (folder/"c10-p01-background-clean.png").write_bytes(b"fixture")
                        with self.assertRaisesRegex(ValueError, "SHA_MISMATCH"):
                            verify_download(folder, validate(invalid))
                else:
                    with self.assertRaises(ValueError):
                        validate(invalid)

    def test_download_checks_exact_filename_and_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            expected = dict(self.request)
            expected["expected_png_sha256"] = hashlib.sha256(b"test-bytes").hexdigest()
            pinned = validate(expected)
            (folder/"c10-p01-background-clean.png").write_bytes(b"test-bytes")
            self.assertEqual(verify_download(folder, pinned)["images"], 1)
            (folder/"c10-p01-background-clean.png").write_bytes(b"other-bytes")
            with self.assertRaisesRegex(ValueError, "SHA_MISMATCH"):
                verify_download(folder, pinned)
            (folder/"c10-p01-background-clean.png").unlink()
            (folder/"other.png").write_bytes(b"test-bytes")
            with self.assertRaisesRegex(ValueError, "NAME_OR_COUNT_MISMATCH"):
                verify_download(folder, pinned)

    def test_recovery_workflow_indexes_png_into_canonical_visual_bible(self):
        workflow=(ROOT/".github/workflows/recuperar-imagens-antigas-actions.yml"
                  ).read_text(encoding="utf-8")
        self.assertIn("python -m videoforge.visual_bible --channel",workflow)
        self.assertIn("python -m videoforge.ep01_image_inventory --write",workflow)
        self.assertIn('git add -A -- "canal/$CH/biblia-visual"',workflow)
        self.assertIn("CHECKPOINT-IMAGENS-EP01-AUTO.json",workflow)
        self.assertIn("- '.github/workflows/recuperar-imagens-antigas-actions.yml'",workflow)
        self.assertIn("if github.event_name != 'pull_request'",workflow)

    def test_legacy_request_is_still_compatible_but_never_publishes(self):
        legacy = dict(self.request,
                      archive_producer="legacy-action-import",
                      channel="otaku-br",
                      video_id="spy-x-family-familia-de-mentira",
                      artifact_name="vf-cena-mae-spy-family-cena-01-43560159589",
                      source_run_id=43560159589)
        legacy.pop("expected_png_name")
        legacy.pop("expected_png_sha256")
        self.assertEqual(validate(legacy)["producer"], "legacy-action-import")
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            (folder/"candidate.png").write_bytes(b"fixture")
            self.assertEqual(verify_download(folder,validate(legacy))["images"],1)

if __name__ == "__main__":
    unittest.main()
