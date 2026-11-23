"""Offline regression: distinguish a billed rejected PNG from proxy errors."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.ep01_proxy_qa_feedback import inspect


class Ep01QaFeedbackTests(unittest.TestCase):
    SHOT = "C10-P02"
    PART = "object-broche-flor"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.png = self.folder / "c10-p02-object-broche-flor.png"
        self.meta = self.png.with_suffix(".production.json")

    def record(self, qa="rejected_canvas_mismatch_no_pixel_resizing", **changes):
        # The feedback tool intentionally uses stdlib and never decodes images.
        raw = b"\x89PNG\r\n\x1a\nexample-offline-sha-fixture"
        self.png.write_bytes(raw)
        info = {
            "schema": "videoforge/ep01-proxy-separate-part/v1",
            "channel": "alchemy-lab",
            "video_id": "mmorpg-conquiste-a-princesa-ep01",
            "candidate_scene_shot_id": self.SHOT,
            "component": self.PART,
            "asset_id": "c10-p02-object-broche-flor",
            "generation_method": "proxy_generated_separate_image",
            "provider_image_calls": 1,
            "human_visual_approval": False, "rig_ready": False,
            "youtube_uploaded": False,
            "source_canvas": [941, 1672],
            "provider_canvas": [1672, 941],
            "technical_qa": qa,
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        info.update(changes)
        self.meta.write_text(json.dumps(info), encoding="utf-8")

    def test_rejected_rotated_canvas_is_not_mislabeled_as_proxy_outage(self):
        self.record()
        report, valid = inspect(self.folder, self.SHOT, self.PART)
        self.assertTrue(valid)
        self.assertIn("Reprovada no QA técnico", report)
        self.assertIn("orientação trocada", report)
        self.assertIn("Chamadas informadas pelo gerador | 1", report)
        self.assertIn("não / não / não", report)
        self.assertNotIn("aprovada para rig", report)

    def test_candidate_still_needs_review(self):
        self.record("candidate_minor_edge_delta_requires_alignment_qa",
                    provider_canvas=[941, 1671])
        report, valid = inspect(self.folder, self.SHOT, self.PART)
        self.assertTrue(valid)
        self.assertIn("Candidata para revisão", report)
        self.assertIn("alinhamento", report)

    def test_no_png_does_not_falsely_claim_generation(self):
        report, valid = inspect(self.folder, self.SHOT, self.PART)
        self.assertTrue(valid)
        self.assertIn("Sem PNG/relatório", report)
        self.assertNotIn("Chamadas informadas", report)

    def test_png_without_provenance_is_error(self):
        self.png.write_bytes(b"fake")
        report, valid = inspect(self.folder, self.SHOT, self.PART)
        self.assertFalse(valid)
        self.assertIn("Erro de integridade", report)

    def test_sha_mismatch_is_fail_closed(self):
        self.record()
        self.png.write_bytes(b"changed")
        report, valid = inspect(self.folder, self.SHOT, self.PART)
        self.assertFalse(valid)
        self.assertIn("SHA-256 mismatch", report)

    def test_approval_metadata_forgery_is_fail_closed(self):
        self.record(human_visual_approval=True)
        report, valid = inspect(self.folder, self.SHOT, self.PART)
        self.assertFalse(valid)
        self.assertIn("integridade", report)

    def test_wrong_shot_metadata_is_fail_closed(self):
        self.record(candidate_scene_shot_id="C11-P01")
        _, valid = inspect(self.folder, self.SHOT, self.PART)
        self.assertFalse(valid)

    def test_input_path_segments_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid shot or part"):
            inspect(self.folder, self.SHOT, "../bad")


if __name__ == "__main__":
    unittest.main()
