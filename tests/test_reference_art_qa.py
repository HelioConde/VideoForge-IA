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
