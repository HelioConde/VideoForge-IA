"""Reference QA must be immutable, truthful and free of new inference."""
from pathlib import Path
import json
import unittest
from videoforge.reference_art_qa import inspect_reference, sync_reference_report,QA_NAME,EP_CHANNEL,EP_ID
from videoforge.remake_autopilot import EPISODE


class ArchivedIdentityReferenceQATests(unittest.TestCase):
    def test_existing_reference_sha_and_no_automatic_approval(self):
        record=inspect_reference()
        self.assertEqual(record["status"],"technical_valid_human_identity_review_pending")
        self.assertEqual(record["source"]["sha256"],"47b7b0cd83689a72a44e7e44dd61c5ba6beabcfc1e411f0e3850fc78f0e8b5c4")
        self.assertEqual((record["source"]["width"],record["source"]["height"]),(1199,1312))
        self.assertFalse(record["requested_format"]["source_dimensions_match_requested"])
        self.assertFalse(record["human_review"]["approved"])
        self.assertFalse(record["downstream"]["approved_canonical_anchor"])
        self.assertFalse(record["generation_provenance_limits"]["approved_originals_attached_to_generation"])
        self.assertFalse(record["generation_provenance_limits"]["claim_exact_original_identity_match"])
        audit=record["source_originals_current_audit"]
        self.assertEqual(audit["kael_elara_sources_total"],2)
        self.assertEqual(audit["kael_elara_sources_verified"],2)
        self.assertTrue(audit["c12_camera_source_verified"])
        self.assertTrue(record["generation_provenance_limits"]["approved_reference_images_sha_imported_in_repo"])
        self.assertFalse(record["generation_provenance_limits"]["approved_originals_attached_to_generation"])
        self.assertEqual(len(audit["expected_originals"]),3)
        self.assertEqual(
            record["generation_provenance_limits"]["approved_reference_images_sha_imported_in_repo"],
            audit["kael_elara_sources_verified"]==2)
        self.assertFalse(audit["aldric_individually_approved_original_sha_available"])
        self.assertFalse(audit["can_approve_identity_automatically"])
        self.assertIn("cabelo",record["identity_review_criteria"]["kael"])
        self.assertIn("violeta",record["identity_review_criteria"]["elara"])
        self.assertIn("barba",record["identity_review_criteria"]["aldric"])
        self.assertFalse(record["downstream"]["can_generate_shot_specific_mothers"])
        self.assertEqual(record["provider_calls"],0)

    def test_aspect_fit_keeps_whole_original_and_does_not_render_fake_preview(self):
        data=inspect_reference()
        fit=data["requested_format"]["preview_only_contain_fit"]
        self.assertEqual(fit["fit_width"]+fit["padding_left"]+fit["padding_right"],1024)
        self.assertEqual(fit["fit_height"]+fit["padding_top"]+fit["padding_bottom"],1536)
        self.assertFalse(fit["rendered"])
        self.assertFalse(fit["pixels_resampled"])
        self.assertTrue(data["source"]["source_pixels_unmodified"])


if __name__=="__main__":
    unittest.main()
