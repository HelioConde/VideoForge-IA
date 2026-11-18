"""Safe offline regression tests for the C01-P04 camera-only technical preview."""
from hashlib import sha256
import json
from pathlib import Path
import unittest
from videoforge import ep01_c01p04_camera_preview as preview
from videoforge.layered_shot_plan import ROOT,REL

class CameraPreviewTests(unittest.TestCase):
    def test_approved_original_technical_alignment_and_no_hand_parts(self):
        source=preview.preflight()
        self.assertEqual(source["original_sha256"],preview.MOTHER_SHA)
        self.assertEqual(source["aligned_sha256"],preview.ALIGNED_SHA)
        self.assertEqual(sha256(source["aligned_bytes"]).hexdigest(),preview.ALIGNED_SHA)
        contract=json.loads((ROOT/REL/"POLITICA-SEM-MAOS-INDEPENDENTES-C01-P04.json").read_text(encoding="utf-8"))
        self.assertTrue(contract["scope"]["skip_creation_of_independent_fingers"])
        self.assertTrue(contract["scope"]["skip_hand_grip_reconstruction"])
        self.assertEqual(contract["animation_approach"]["guards_in_c01_p04"],
                         "static_approved_integrated_character_and_weapon_visual")

    def test_mother_inventory_is_complete_but_not_automatically_approved(self):
        inventory=json.loads((ROOT/REL/"CHECKPOINT-IMAGENS-EP01-AUTO.json").read_text(encoding="utf-8"))
        self.assertEqual(inventory["visual_shots_with_original_mother"],39)
        self.assertEqual(inventory["visual_shots_missing_original_mother"],0)
        self.assertEqual(inventory["missing_original_mother_shot_ids"],[])
        self.assertTrue(inventory["counts_are_generated_not_approved"])
        self.assertFalse(inventory["rig_ready"])

    def test_c01_p04_camera_preview_is_not_official_episode(self):
        doc=json.loads((ROOT/preview.PLAN).read_text(encoding="utf-8"))
        self.assertEqual(doc["timeline"]["duration_frames"],70)
        self.assertEqual(doc["timeline"]["start_frame"],240)
        self.assertEqual(doc["timeline"]["end_frame_exclusive"],310)
        self.assertTrue(doc["render"]["preview_only"])
        self.assertFalse(doc["official_episode_render_authorized"])
        self.assertFalse(doc["hand_parts_required"])
        self.assertEqual(doc["camera"]["type"],"slow_dolly_out_single_layer_simulation")

if __name__=="__main__":
    unittest.main()
