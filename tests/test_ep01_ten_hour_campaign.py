"""Offline guards for the 10-slot EP01 campaign. No GitHub calls or media generated."""
import re
import unittest
from unittest.mock import patch

from scripts import ep01_ten_hour_campaign as campaign


class TenHourCampaignTests(unittest.TestCase):
    def test_plan_600_minutes_and_dispatch_caps(self):
        plan = campaign.load_plan()
        self.assertEqual(len(plan["stages"]), 10)
        self.assertEqual(sum(s["planned_minutes"] for s in plan["stages"]), 600)
        self.assertEqual([s["slot"] for s in plan["stages"]], list(range(1, 11)))
        self.assertEqual(plan["safe_dispatch"]["max_paid_image_requests_if_all_stages_run"], 20)
        self.assertEqual(plan["safe_dispatch"]["max_camera_preview_dispatches_if_all_stages_run"], 40)
        self.assertTrue(plan["safe_dispatch"]["reuse_remote_CAS_ledger"])
        self.assertFalse(plan["safe_dispatch"]["never_publish_youtube"] is False)

    def test_github_environment_is_main_only(self):
        with patch.dict("os.environ", {
            "GITHUB_REPOSITORY": "HelioConde/VideoForge-IA",
            "GITHUB_REF": "refs/heads/not-main",
            "GH_TOKEN": "fake-local-test",
            "GITHUB_RUN_ID": "123",
        }):
            with self.assertRaisesRegex(ValueError, "MAIN_ONLY"):
                campaign.require_main()

    def test_workflow_has_ten_sequential_stages_and_stop_gate(self):
        source = (campaign.ROOT / ".github/workflows/ep01-10h-campaign.yml").read_text(encoding="utf-8")
        stages = re.findall(r"^  slot_(\d\d):$", source, re.M)
        self.assertEqual(stages, [f"{i:02d}" for i in range(1, 11)])
        for i in range(2, 11):
            before = f"{i - 1:02d}"
            now = f"{i:02d}"
            self.assertIn(f"slot_{now}:\n    needs: slot_{before}", source)
            self.assertIn(f"needs.slot_{before}.outputs.has_more == 'true'", source)
        self.assertNotIn("youtube-upload", source.lower())
        self.assertNotIn("sleep 3600", source.lower())

    def test_reusable_step_calls_existing_queue_only(self):
        source = (campaign.ROOT / ".github/workflows/ep01-10h-step.yml").read_text(encoding="utf-8")
        self.assertIn("scripts.ep01_ten_hour_campaign", source)
        self.assertIn("timeout-minutes: 55", source)
        self.assertNotIn("proxy_images", source)
        self.assertNotIn("auto_publish", source)
        self.assertIn("uses: actions/upload-artifact@v4", source)

    def test_invalid_or_missing_github_ref_aborts_before_dispatch(self):
        with patch.dict("os.environ", {"GITHUB_REPOSITORY": "HelioConde/VideoForge-IA",
                                        "GITHUB_REF": "refs/heads/main",
                                        "GITHUB_RUN_ID": "123"}, clear=True):
            with self.assertRaisesRegex(ValueError, "MAIN_ONLY"):
                campaign.require_main()


if __name__ == "__main__":
    unittest.main()
