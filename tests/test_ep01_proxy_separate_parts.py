"""Zero-cost checks for fresh proxy-generated separate PNGs (not masks)."""
import hashlib
import unittest
from unittest.mock import patch

from videoforge import ep01_proxy_separate_parts as p
from videoforge.errors import VideoForgeError


class SeparatePartsTests(unittest.TestCase):
    def test_new_shot_background_has_sha_verified_mother_and_reference(self):
        # The real background may already be archived by subsequent runs.
        # These prompt/provenance tests never bypass the production no-repeat gate.
        with patch.object(p, "existing_part", return_value=None), patch.object(p,"enforce_source_qa",return_value=None):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                spec=p.prepare("C01-P03","background-clean")
                charged.assert_not_called()
        self.assertEqual(spec["role"],"background")
        self.assertFalse(spec["transparent"])
        self.assertEqual(spec["source_dimensions"],(941,1672))
        self.assertEqual(hashlib.sha256(spec["mother"]).hexdigest(),
                         spec["mother_proof"]["sha256"])
        self.assertTrue(spec["ref_proofs"])
        self.assertIn("NEW INDEPENDENT image",spec["prompt"])
        self.assertIn("NO",spec["prompt"])
        self.assertLessEqual(len(spec["refs"])+1,p.MAX_REFERENCE_PNGS_PER_REQUEST)

    def test_character_is_requested_as_new_png_not_cutout(self):
        with patch.object(p, "existing_part", return_value=None), patch.object(p,"enforce_source_qa",return_value=None):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                spec=p.prepare("C01-P03","character-kael")
                charged.assert_not_called()
        self.assertEqual(spec["role"],"character")
        self.assertTrue(spec["transparent"])
        self.assertIn("REAL transparent RGBA",spec["prompt"])
        self.assertIn("no cropping/segmentation",spec["prompt"])

    def test_rejected_p03_mother_is_fail_closed_until_versioned_source(self):
        shot, _ = p.read_shot("C01-P03","background-clean")
        self.assertTrue(shot["qa"]["require_versioned_mother_v2_before_more_proxy_parts"])
        with self.assertRaisesRegex(VideoForgeError,
                                   "EP01_PROXY_PARTS_MOTHER_REJECTED_NEW_VERSION_REQUIRED"):
            p.enforce_source_qa(shot)

    def test_rejected_p04_standing_kael_mother_is_blocked_for_rig(self):
        shot, _ = p.read_shot("C01-P04","background-clean")
        self.assertEqual(shot["qa"]["required_character_pose"],"kael_kneeling_not_standing")
        with self.assertRaisesRegex(VideoForgeError,
                                   "EP01_PROXY_PARTS_MOTHER_REJECTED_NEW_VERSION_REQUIRED"):
            p.enforce_source_qa(shot)

    def test_unapproved_c01_p02_v1_cannot_be_used_for_rig(self):
        with patch.object(p.proxy_images, "call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,
                 "EP01_PROXY_PARTS_C01_P02_MOTHER_NOT_CANONICAL"):
                p.prepare("C01-P02","background-clean")
            charged.assert_not_called()

    def test_earlier_archive_never_rebilled(self):
        with patch.object(p,"existing_part",return_value={"sha256":"a"*64}):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,
                     "EP01_PROXY_PARTS_ALREADY_ARCHIVED_NO_REPEAT"):
                    p.prepare("C01-P03","background-clean")
                charged.assert_not_called()

    def test_c08_p02_uses_exact_archived_continuity_v2_image_not_old_mother(self):
        import json
        from videoforge.ep01_continuity_motion import EP as episode, read as motion
        from videoforge.layered_shot_plan import ROOT
        source = motion(ROOT)["source_reference_shas"]["C08-P02"]
        raw, proof = p.mother_source("C08-P02")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), source["sha256"])
        self.assertEqual(proof["sha256"], source["sha256"])
        self.assertEqual(proof["path"], (episode / source["asset"]).as_posix())
        self.assertIn("unapproved", proof["status"])
        self.assertTrue(proof["path"].endswith("c08-p02-continuity-v2-scene-mother.png"))

    def test_c08_p02_proxy_contract_attaches_original_mother_and_cart_bible(self):
        with patch.object(p, "existing_part", return_value=None):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                character = p.prepare("C08-P02", "character-kael")
                cart = p.prepare("C08-P02", "object-carrinho")
                background = p.prepare("C08-P02", "background-clean")
                charged.assert_not_called()
        self.assertEqual(character["mother_proof"]["sha256"],
                         "3c21b7d82d69b1445b45cb1a23582e556c910530b568c26ae0d48b4873c38721")
        for spec in (character, cart, background):
            self.assertEqual(spec["source_dimensions"], (1053, 1493))
            self.assertEqual(hashlib.sha256(spec["mother"]).hexdigest(),
                             spec["mother_proof"]["sha256"])
            self.assertGreaterEqual(len(spec["refs"]), 1)
            self.assertIn("NEW INDEPENDENT image", spec["prompt"])
            self.assertIn("NO pursuers", spec["prompt"])
            self.assertIn("continuity V2", spec["prompt"])
        self.assertIn("character 'kael'", character["prompt"])
        self.assertIn("object 'carrinho'", cart["prompt"])
        self.assertIn("EMPTY CLEAN BACKGROUND", background["prompt"])
        self.assertTrue(cart["transparent"])
        self.assertFalse(background["transparent"])

    def test_c08_p02_mother_sha_drift_denies_before_any_provider_call(self):
        from copy import deepcopy
        from videoforge.ep01_continuity_motion import read as motion
        document = deepcopy(motion())
        document["source_reference_shas"]["C08-P02"]["sha256"] = "f" * 64
        with patch("videoforge.ep01_continuity_motion.read", return_value=document):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,
                    "V2_MOTHER_SHA_OR_POLICY_CHANGED"):
                    p.mother_source("C08-P02")
                charged.assert_not_called()

    def test_wrong_asset_or_model_fail_before_proxy(self):
        with patch.object(p.proxy_images, "call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,"NOT_IN_SHOT_PLAN"):
                p.prepare("C01-P03","character-elara")
            with self.assertRaisesRegex(VideoForgeError,"MODEL_NOT_ALLOWED"):
                p.generate("C01-P03","background-clean","http://127.0.0.1:18080",
                           model="invalid")
            with self.assertRaisesRegex(VideoForgeError,"INVALID_SHOT"):
                p.prepare("C01-P01","background-clean")
            charged.assert_not_called()


if __name__=="__main__":
    unittest.main()
