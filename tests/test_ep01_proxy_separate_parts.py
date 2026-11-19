"""Zero-cost checks for fresh proxy-generated separate PNGs (not masks)."""
import hashlib
import unittest
from unittest.mock import patch

from videoforge import ep01_proxy_separate_parts as p
from videoforge.errors import VideoForgeError


class SeparatePartsTests(unittest.TestCase):
    def test_contact_revision_pins_actual_cart_and_never_sends_previous_kael(self):
        from unittest.mock import patch
        from videoforge import ep01_proxy_separate_parts as engine
        lookup=engine.existing_part
        def existing(shot,part,root):
            return None if part=="character-kael-v3" else lookup(shot,part,root)
        with patch.object(engine,"existing_part",side_effect=existing):
            spec=engine.prepare("C08-P02","character-kael-v3")
        self.assertEqual(spec["source_dimensions"],(1053,1493))
        self.assertEqual([p["asset_id"] for p in spec["ref_proofs"]],
                         ["biblia-kael-medieval-base-v1","c08-p02-object-carrinho-v2"])
        self.assertEqual(spec["ref_proofs"][-1]["sha256"],
                         "df5371baa402fb437e8671ffb6b11a21e640ec0ac5e589073d89850de1add65b")
        self.assertIn("x560-635",spec["prompt"])
        self.assertTrue(spec["transparent"])
    def test_crown_v2_uses_portrait_mother_canonical_bible_and_exact_failed_v1_fence(self):
        original=p.existing_part
        def only_missing_crown_v2(shot_id,part_id,root=p.ROOT):
            if (shot_id,part_id)==("C02-P01","object-coroa-aldric-v2"):
                return None
            return original(shot_id,part_id,root)
        with patch.object(p,"existing_part",side_effect=only_missing_crown_v2):
            with patch.object(p.proxy_images,"call_proxy") as charged:
                spec=p.prepare("C02-P01","object-coroa-aldric-v2")
                charged.assert_not_called()
        self.assertEqual(spec["source_dimensions"],(941,1672))
        self.assertEqual(spec["mother_proof"]["sha256"],
                         "0d1f8367c76cdf0c9b63f10071406a567b5a5a10cf799e1aa6c5d814019fa2a0")
        self.assertEqual([x["asset_id"] for x in spec["ref_proofs"]],
                         ["biblia-aldric-tribunal-v1"])
        self.assertIn("1774x887 landscape",spec["prompt"])
        self.assertIn("941x1672 portrait",spec["prompt"])
        self.assertIn("Do NOT attach, copy, resize, crop",spec["prompt"])
        self.assertIn("every other pixel is true alpha=0",spec["prompt"])

    def test_crown_v2_fails_closed_if_archived_v1_differs(self):
        original=p.existing_part
        def wrong_predecessor(shot_id,part_id,root=p.ROOT):
            if (shot_id,part_id)==("C02-P01","object-coroa-aldric-v2"):
                return None
            if (shot_id,part_id)==("C02-P01","object-coroa-aldric"):
                return {"sha256":"0"*64}
            return original(shot_id,part_id,root)
        with patch.object(p,"existing_part",side_effect=wrong_predecessor):
            with patch.object(p.proxy_images,"call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,
                        "EP01_CROWN_V2_REJECTED_PREDECESSOR_NOT_VERIFIED"):
                    p.prepare("C02-P01","object-coroa-aldric-v2")
                charged.assert_not_called()

    def test_crown_v2_replay_stops_when_its_own_version_is_archived(self):
        original=p.existing_part
        def v2_already_archived(shot_id,part_id,root=p.ROOT):
            if (shot_id,part_id)==("C02-P01","object-coroa-aldric-v2"):
                return {"sha256":"1"*64}
            return original(shot_id,part_id,root)
        with patch.object(p,"existing_part",side_effect=v2_already_archived):
            with patch.object(p.proxy_images,"call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,
                        "EP01_PROXY_PARTS_ALREADY_ARCHIVED_NO_REPEAT"):
                    p.prepare("C02-P01","object-coroa-aldric-v2")
                charged.assert_not_called()

    def test_guard_alignment_request_is_exact_no_ai_one_row_padding(self):
        from videoforge import ep01_align_proxy_part as align
        import json
        from pathlib import Path
        from videoforge.layered_shot_plan import REL
        request=json.loads((p.ROOT/REL/"PEDIDO-ALINHAMENTO-PROXY-EP01.json").read_text(encoding="utf-8"))
        self.assertEqual((request["shot_id"],request["part"]),
                         ("C01-P05","character-guarda_direito"))
        self.assertEqual(request["source_sha256"],
                         "7091af3214d3c04dc174d55941f525ab543f055b024632315195b97b4af24afd")
        self.assertTrue(request["no_provider_calls"])
        self.assertFalse(request["allow_crop_or_resize"])
        self.assertEqual(request["max_bottom_rows_to_add"],2)
        spec=align.prepare("C01-P05","character-guarda_direito")
        self.assertEqual(spec["padding"],1)
        self.assertEqual(spec["expected_canvas"],(941,1672))

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

    def test_c08_cart_uses_only_direct_canon_refs_no_unrelated_pursuers(self):
        with patch.object(p,"existing_part",return_value=None),patch.object(p.proxy_images,"call_proxy") as charged:
            spec=p.prepare("C08-P02","object-carrinho")
            charged.assert_not_called()
        self.assertEqual(len(spec["refs"]),2)
        self.assertEqual([x["asset_id"] for x in spec["ref_proofs"]],
                         ["biblia-carrinho-base-v1","biblia-kael-medieval-base-v1"])
        self.assertEqual(len(spec["refs"])+1,3)
        self.assertTrue(spec["transparent"])
        self.assertEqual(spec["source_dimensions"],(1053,1493))
        self.assertIn("SAME",spec["prompt"].upper())
        self.assertIn("ONLY movable object 'carrinho'",spec["prompt"])
        self.assertIn("NO pursuers",spec["prompt"])

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

    def test_v2_redraw_is_true_kael_only_with_single_identity_reference(self):
        from videoforge.ep01_proxy_separate_parts import right_side_prop_coverage
        from PIL import Image, ImageDraw
        original=p.existing_part
        def only_missing_v2(shot_id,part_id,root=p.ROOT):
            if part_id=="character-kael-v2":
                return None
            return original(shot_id,part_id,root)
        with patch.object(p,"existing_part",side_effect=only_missing_v2):
            with patch.object(p.proxy_images, "call_proxy") as charged:
                spec=p.prepare("C08-P02","character-kael-v2")
                charged.assert_not_called()
        self.assertEqual(spec["role"],"character")
        self.assertTrue(spec["transparent"])
        self.assertEqual(len(spec["refs"]),1)
        self.assertEqual([r["asset_id"] for r in spec["ref_proofs"]],
                         ["biblia-kael-medieval-base-v1"])
        self.assertIn("ZERO CART PIXELS",spec["prompt"])
        self.assertIn("NO wheels",spec["prompt"])
        self.assertIn("second is ONLY the canonical KAEL",spec["prompt"])
        self.assertEqual(spec["mother_proof"]["sha256"],
                         "3c21b7d82d69b1445b45cb1a23582e556c910530b568c26ae0d48b4873c38721")
        # Entirely independent left-hand sprite passes right-side cart gate.
        canvas=Image.new("RGBA",(1054,1493),(0,0,0,0))
        ImageDraw.Draw(canvas).ellipse((50,550,590,1300),fill=(100,50,80,255))
        self.assertEqual(right_side_prop_coverage(canvas),0.0)
        # Cart painted into the far right is not silently treated as a sprite.
        ImageDraw.Draw(canvas).rectangle((800,680,1053,1200),fill=(110,80,40,255))
        self.assertGreater(right_side_prop_coverage(canvas),0.2)

    def test_archived_v1_kael_has_cart_embedded_and_is_not_reused_for_rig(self):
        from PIL import Image
        old=p.existing_part("C08-P02","character-kael")
        self.assertEqual(old["sha256"],
                         "2579d5786f89957ea776c8c17b76371027fffd2ce43a4e3fba6505201db029d1")
        with Image.open(p.ROOT / old["file"]) as im:
            self.assertGreater(p.right_side_prop_coverage(im),0.3)
        # The original source must remain archived and SHA-verifiable.
        self.assertEqual(p.existing_part("C08-P02","character-kael")["sha256"],
                         old["sha256"])

    def test_successfully_archived_kael_v2_must_never_be_rebilled(self):
        archived=p.existing_part("C08-P02","character-kael-v2")
        self.assertIsNotNone(archived)
        self.assertEqual(archived["sha256"],
                         "cbf8dc00f81788dd26675f1a16df2c971b44e287665ccf4ecbc59d698a6bec4d")
        with patch.object(p.proxy_images,"call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,"ALREADY_ARCHIVED_NO_REPEAT"):
                p.prepare("C08-P02","character-kael-v2")
            charged.assert_not_called()

    def test_cart_v2_is_new_portrait_source_anchored_image_not_v1_landscape(self):
        original=p.existing_part
        def only_missing_cart_v2(shot_id,part_id,root=p.ROOT):
            if part_id=="object-carrinho-v2":
                return None
            return original(shot_id,part_id,root)
        with patch.object(p,"existing_part",side_effect=only_missing_cart_v2):
            with patch.object(p.proxy_images,"call_proxy") as charged:
                spec=p.prepare("C08-P02","object-carrinho-v2")
                charged.assert_not_called()
        self.assertEqual(spec["role"],"object")
        self.assertTrue(spec["transparent"])
        self.assertEqual(spec["source_dimensions"],(1053,1493))
        self.assertEqual(spec["mother_proof"]["sha256"],
                         "3c21b7d82d69b1445b45cb1a23582e556c910530b568c26ae0d48b4873c38721")
        self.assertEqual(len(spec["refs"]),1)
        self.assertEqual(spec["ref_proofs"][0]["asset_id"],"biblia-carrinho-base-v1")
        self.assertIn("VERTICAL portrait",spec["prompt"])
        self.assertIn("RIGHT side",spec["prompt"])
        self.assertIn("NEVER make a landscape",spec["prompt"])
        self.assertIn("NO Kael",spec["prompt"])
        self.assertIn("alpha=0",spec["prompt"])

    def test_successfully_archived_cart_v2_must_never_be_regenerated(self):
        archived=p.existing_part("C08-P02","object-carrinho-v2")
        self.assertEqual(archived["sha256"],
                         "df5371baa402fb437e8671ffb6b11a21e640ec0ac5e589073d89850de1add65b")
        with patch.object(p.proxy_images,"call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,"ALREADY_ARCHIVED_NO_REPEAT"):
                p.prepare("C08-P02","object-carrinho-v2")
            charged.assert_not_called()

    def test_cart_v2_requires_exact_archived_failed_predecessor(self):
        prior=p.existing_part("C08-P02","object-carrinho")
        self.assertEqual(prior["sha256"],
                         "bf78eae46f5d6836a7834fff8714c6e3072f23e523d6fbe73ac8b9b5accb47ab")
        original=p.existing_part
        def wrong(shot_id,part_id,root=p.ROOT):
            if part_id=="object-carrinho":
                return {"sha256":"0"*64}
            if part_id=="object-carrinho-v2":
                return None
            return original(shot_id,part_id,root)
        with patch.object(p,"existing_part",side_effect=wrong):
            with patch.object(p.proxy_images,"call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,"CART_V2_PREDECESSOR_NOT_VERIFIED"):
                    p.prepare("C08-P02","object-carrinho-v2")
                charged.assert_not_called()

    def test_kael_v2_denied_when_predecessor_provenance_does_not_match(self):
        original=p.existing_part
        def corrupted(shot_id,part_id,root=p.ROOT):
            if part_id=="character-kael":
                return {"sha256":"0"*64}
            if part_id=="character-kael-v2":
                return None
            return original(shot_id,part_id,root)
        with patch.object(p,"existing_part",side_effect=corrupted),patch.object(
                p.proxy_images,"call_proxy") as charged:
            with self.assertRaisesRegex(VideoForgeError,
                    "REJECTED_PREDECESSOR_NOT_VERIFIED"):
                p.prepare("C08-P02","character-kael-v2")
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
