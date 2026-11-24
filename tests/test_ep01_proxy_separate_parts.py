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
        # The one-row alignment candidate is already archived. The contract
        # must refuse a second attempt, not fail unrelated queue preflights.
        with self.assertRaisesRegex(VideoForgeError,
                                    "EP01_ALIGN_ALREADY_ARCHIVED_NO_REPEAT"):
            align.prepare("C01-P05","character-guarda_direito")

    def test_native_canvas_contract_prevents_silent_orientation_guess(self):
        # Explicit native dimensions are part of the provider prompt; no paid calls.
        with patch.object(p, "existing_part", return_value=None), patch.object(
                p.proxy_images, "call_proxy") as charged:
            for shot, part, expected in (
                    ("C10-P02", "object-broche-flor", (941, 1672)),
                    ("C08-P02", "object-carrinho", (1053, 1493))):
                spec = p.prepare(shot, part)
                w, h = spec["source_dimensions"]
                self.assertEqual((w, h), expected)
                self.assertIn(f"image one is {w}x{h} pixels", spec["prompt"])
                self.assertIn(f"WIDTH={w}, HEIGHT={h}, VERTICAL portrait", spec["prompt"])
                self.assertIn(f"NEVER transpose to {h}x{w}", spec["prompt"])
                self.assertLessEqual(len(spec["prompt"]), 5000)
            charged.assert_not_called()

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


class NativeCanvasContractTests(unittest.TestCase):
    def test_supported_sizes_keep_width_height_and_custom_dimensions(self):
        for dims in ((1024,1536),(1536,1024),(1536,864),(1024,1024),
                     (640,1024),(3840,2160),(2160,3840),(1536,512)):
            with self.subTest(dims=dims):
                self.assertEqual(p.exact_canvas_size(dims),f"{dims[0]}x{dims[1]}")

    def test_unsupported_native_sizes_never_round_or_fall_back(self):
        for dims in ((941,1672),(1053,1493),(0,1024),(-16,1024),
                     (True,1024),(1024.0,1024),("1024",1024),
                     (512,512),(4096,2048),(3840,3840),(2048,512),
                     (1024,),None):
            with self.subTest(dims=dims):
                with self.assertRaisesRegex(VideoForgeError,"UNSUPPORTED_NATIVE_CANVAS"):
                    p.exact_canvas_size(dims)

    def test_inspection_remains_available_but_production_preflight_blocks(self):
        with patch.object(p,"existing_part",return_value=None), patch.object(
                p.proxy_images,"call_proxy") as charged:
            spec=p.prepare("C11-P03","background-clean")
            self.assertEqual(spec["source_dimensions"],(941,1672))
            with self.assertRaisesRegex(VideoForgeError,"UNSUPPORTED_NATIVE_CANVAS"):
                p.prepare("C11-P03","background-clean",require_supported_canvas=True)
            charged.assert_not_called()

    def test_generate_checks_canvas_before_provider_or_output(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                p,"prepare",return_value={"source_dimensions":(941,1672)}) as prepare:
            with patch.object(p.proxy_images,"call_proxy") as charged:
                with self.assertRaisesRegex(VideoForgeError,"UNSUPPORTED_NATIVE_CANVAS"):
                    p.generate("C11-P03","background-clean","http://unused",root=Path(tmp))
                charged.assert_not_called()
                prepare.assert_called_once_with("C11-P03","background-clean",Path(tmp),
                                                require_supported_canvas=True)
                self.assertEqual(list(Path(tmp).iterdir()),[])

    @staticmethod
    def png(size):
        import io
        from PIL import Image
        stream=io.BytesIO()
        # Synthetic QA fixture only; never stored as production art in Git.
        Image.new("RGB",size,(12,34,56)).save(stream,format="PNG")
        return stream.getvalue()

    def run_generation(self,root,output_size):
        import base64
        source=self.png((1536,864))
        reference=self.png((1024,1024))
        output=self.png(output_size)
        spec={"source_dimensions":(1536,864),"mother":source,"refs":[reference],
              "mother_proof":{"sha256":hashlib.sha256(source).hexdigest()},
              "ref_proofs":[{"sha256":hashlib.sha256(reference).hexdigest()}],
              "role":"background","transparent":False,"prompt":"test"}
        with patch.object(p,"prepare",return_value=spec), patch.object(
                p.proxy_images,"call_proxy",
                return_value={"data":[{"b64_json":base64.b64encode(output).decode()}]}) as charged:
            if output_size==(1536,864):
                report=p.generate("C11-P03","background-clean","http://unused",root=root)
                self.assertEqual(report["requested_size"],"1536x864")
                self.assertFalse(report["human_visual_approval"])
                self.assertFalse(report["rig_ready"])
            else:
                with self.assertRaisesRegex(VideoForgeError,"GENERATED_REJECTED_BUT_ARCHIVED"):
                    p.generate("C11-P03","background-clean","http://unused",root=root)
            self.assertEqual(charged.call_count,1)
            payload=charged.call_args.args[3]
            self.assertEqual(payload["size"],"1536x864")
            self.assertEqual(payload["n"],1)
            self.assertEqual([base64.b64decode(x["image_url"].split(",",1)[1])
                              for x in payload["images"]],[source,reference])
        image=root/"output"/p.CHANNEL/"videos"/p.VIDEO/"imagens"/"c11-p03-background-clean.png"
        self.assertEqual(image.read_bytes(),output)
        return image

    def test_request_uses_exact_landscape_size_and_original_reference_bytes(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            self.run_generation(Path(tmp),(1536,864))

    def test_wrong_provider_canvas_is_archived_unmodified_without_retry(self):
        import json
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            image=self.run_generation(Path(tmp),(981,1602))
            report=json.loads(image.with_suffix(".production.json").read_text())
            self.assertEqual(report["technical_qa"],"rejected_canvas_mismatch_no_pixel_resizing")
            self.assertEqual(report["provider_canvas"],[981,1602])
            self.assertEqual(report["requested_size"],"1536x864")
            self.assertEqual(report["sha256"],hashlib.sha256(image.read_bytes()).hexdigest())
            self.assertFalse(report["human_visual_approval"])
            self.assertFalse(report["rig_ready"])


class ReferencePlacementTests(unittest.TestCase):
    def test_known_incompatible_mothers_have_reversible_integer_offsets(self):
        from videoforge.ep01_reference_placement import plan_placement
        for dims, canvas, rect in (
                ((941,1672),[944,1680],[1,4,942,1676]),
                ((1053,1493),[1056,1504],[1,5,1054,1498])):
            with self.subTest(dims=dims):
                plan=plan_placement(dims)
                self.assertEqual(plan["reference_canvas"],canvas)
                self.assertEqual(plan["source_rect_xyxy"],rect)
                self.assertEqual(plan["scale_xy"],[1,1])
                self.assertEqual(plan["reference_to_source_offset_xy"],
                                 [-rect[0],-rect[1]])
                self.assertFalse(plan["generation_authorized"])
                self.assertFalse(plan["rig_ready"])
                self.assertEqual(plan["provider_calls"],0)

    def test_native_compatible_canvas_has_no_padding(self):
        from videoforge.ep01_reference_placement import plan_placement
        plan=plan_placement((1536,864))
        self.assertEqual(plan["source_rect_xyxy"],[0,0,1536,864])
        self.assertEqual(plan["padding_ltrb"],[0,0,0,0])
        self.assertEqual(plan["requested_size_candidate"],"1536x864")

    def test_invalid_or_orientation_changing_sources_fail_closed(self):
        from videoforge.ep01_reference_placement import plan_placement
        for dims in ((0,1024),(True,1024),(4096,2048),(100,100),
                     (2048,512),(1000,1001),(3840,3840)):
            with self.subTest(dims=dims), self.assertRaises(VideoForgeError):
                plan_placement(dims)

    def test_reference_pixels_and_transparent_margins_preserved(self):
        import io
        from PIL import Image
        from videoforge.ep01_reference_placement import prepare_reference
        for mode in ("RGB","RGBA"):
            with self.subTest(mode=mode):
                image=Image.new(mode,(941,1672),
                                (12,34,56) if mode=="RGB" else (12,34,56,0))
                image.putpixel((940,1671),(255,0,0) if mode=="RGB" else (255,0,0,192))
                stream=io.BytesIO()
                image.save(stream,format="PNG")
                raw=stream.getvalue()
                digest=hashlib.sha256(raw).hexdigest()
                with patch.object(p.proxy_images,"call_proxy") as charged:
                    reference, manifest=prepare_reference(raw,digest)
                    charged.assert_not_called()
                self.assertEqual(manifest["source_sha256"],digest)
                self.assertEqual(manifest["reference_sha256"],hashlib.sha256(reference).hexdigest())
                self.assertTrue(manifest["source_rect_pixels_verified"])
                self.assertFalse(manifest["placement_verified"])
                with Image.open(io.BytesIO(reference)) as padded:
                    self.assertEqual(padded.size,(944,1680))
                    self.assertEqual(padded.getpixel((0,0)),(0,0,0,0))
                    self.assertEqual(padded.crop((1,4,942,1676)).tobytes(),
                                     image.convert("RGBA").tobytes())


    def test_cli_inspects_real_archived_mother_with_proof_without_mutation(self):
        import io
        import json
        from videoforge import ep01_reference_placement as placement
        raw, proof=p.mother_source("C11-P03")
        output=io.StringIO()
        with patch("sys.argv",["placement","--shot-id","C11-P03"]), patch(
                "sys.stdout",output), patch.object(p.proxy_images,"call_proxy") as charged:
            placement.main()
            charged.assert_not_called()
        manifest=json.loads(output.getvalue())
        self.assertEqual(manifest["shot_id"],"C11-P03")
        self.assertEqual(manifest["source_proof"],proof)
        self.assertEqual(manifest["source_sha256"],hashlib.sha256(raw).hexdigest())
        self.assertEqual(manifest["source_canvas"],[941,1672])
        self.assertEqual(manifest["reference_canvas"],[944,1680])
        self.assertTrue(manifest["source_rect_pixels_verified"])
        self.assertTrue(manifest["reference_only"])
        self.assertFalse(manifest["generation_authorized"])
        self.assertFalse(manifest["placement_verified"])
        self.assertEqual(p.mother_source("C11-P03"),(raw,proof))

    def test_wrong_sha_rejected_before_reference_decode(self):
        from videoforge.ep01_reference_placement import prepare_reference
        with self.assertRaisesRegex(VideoForgeError,"SOURCE_SHA_MISMATCH"):
            prepare_reference(b"not an image","0"*64)

    def test_non_png_and_unsupported_mode_rejected(self):
        import io
        from PIL import Image
        from videoforge.ep01_reference_placement import prepare_reference
        for mode,fmt,error in (("RGB","JPEG","EXPECTED_STATIC_PNG"),
                               ("L","PNG","UNSUPPORTED_PIXEL_MODE")):
            with self.subTest(mode=mode,fmt=fmt):
                stream=io.BytesIO()
                Image.new(mode,(944,1680)).save(stream,format=fmt)
                raw=stream.getvalue()
                with self.assertRaisesRegex(VideoForgeError,error):
                    prepare_reference(raw,hashlib.sha256(raw).hexdigest())


class ReferenceCandidateQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from videoforge import ep01_reference_placement as placement
        from PIL import Image
        cls.placement=placement
        cls.source=cls.encode(Image.new("RGB",(941,1672),(12,34,56)))
        cls.source_sha=hashlib.sha256(cls.source).hexdigest()
        cls.reference,cls.manifest=placement.prepare_reference(cls.source,cls.source_sha)

    @staticmethod
    def encode(image,fmt="PNG",**options):
        import io
        stream=io.BytesIO()
        image.save(stream,format=fmt,**options)
        return stream.getvalue()

    def candidate(self):
        from PIL import Image, ImageDraw
        image=Image.new("RGBA",(944,1680),(0,0,0,0))
        ImageDraw.Draw(image).rectangle((11,24,40,63),fill=(90,80,70,255))
        return image

    def audit(self,image,role="character"):
        return self.placement.inspect_candidate(self.encode(image),self.source,
                    self.source_sha,self.manifest,role=role)

    def test_valid_candidate_maps_alpha_bounds_without_approving_or_modifying(self):
        from copy import deepcopy
        before=deepcopy(self.manifest)
        raw=self.encode(self.candidate())
        with patch.object(p.proxy_images,"call_proxy") as charged:
            qa=self.placement.inspect_candidate(raw,self.source,self.source_sha,
                                                 self.manifest,role="character")
            charged.assert_not_called()
        self.assertTrue(qa["canvas_alpha_candidate"])
        self.assertEqual(qa["alpha_bbox_source_xyxy"],[10,20,40,60])
        self.assertEqual(qa["candidate_sha256"],hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.manifest,before)
        for field in ("pixels_modified","placement_verified","human_visual_approval",
                      "rig_ready","generation_authorized","provider_provenance_verified",
                      "youtube_uploaded"):
            self.assertIs(qa[field],False)
        self.assertEqual(qa["provider_calls"],0)

    def test_each_padding_edge_rejects_even_one_visible_alpha_pixel(self):
        for point in ((0,20),(943,20),(20,0),(20,1679)):
            with self.subTest(point=point):
                image=self.candidate()
                image.putpixel(point,(255,255,255,1))
                self.assertEqual(self.audit(image)["technical_qa"],
                                 "rejected_nontransparent_reference_padding")
        image=self.candidate()
        image.putpixel((0,20),(255,0,0,0))
        self.assertTrue(self.audit(image)["canvas_alpha_candidate"])

    def test_wrong_canvas_including_one_pixel_delta_never_auto_aligns(self):
        from PIL import Image
        for dims in ((944,1679),(1680,944),(941,1672)):
            with self.subTest(dims=dims):
                qa=self.audit(Image.new("RGBA",dims,(20,20,20,255)))
                self.assertEqual(qa["technical_qa"],"rejected_reference_canvas_mismatch")
                self.assertEqual(qa["candidate_canvas"],list(dims))
                self.assertFalse(qa["pixels_modified"])

    def test_missing_empty_and_fully_opaque_character_alpha_are_rejected(self):
        from PIL import Image, ImageDraw
        self.assertEqual(self.audit(self.candidate().convert("RGB"))["technical_qa"],
                         "rejected_no_rgba_channel")
        for opacity in (0,127):
            image=Image.new("RGBA",(944,1680),(0,0,0,0))
            image.putpixel((10,20),(70,80,90,opacity))
            self.assertEqual(self.audit(image)["technical_qa"],
                             "rejected_empty_or_insufficient_alpha")
        image=self.candidate()
        ImageDraw.Draw(image).rectangle((1,4,941,1675),fill=(90,80,70,255))
        self.assertEqual(self.audit(image)["technical_qa"],
                         "rejected_no_transparency_inside_source_rect")

    def test_background_is_opaque_only_inside_original_rectangle(self):
        from PIL import ImageDraw
        image=self.candidate()
        ImageDraw.Draw(image).rectangle((1,4,941,1675),fill=(90,80,70,255))
        qa=self.audit(image,role="background")
        self.assertTrue(qa["canvas_alpha_candidate"])
        self.assertEqual(qa["alpha_bbox_source_xyxy"],[0,0,941,1672])
        image.putpixel((20,30),(90,80,70,254))
        self.assertEqual(self.audit(image,role="background")["technical_qa"],
                         "rejected_background_has_transparent_holes")

    def test_original_or_reference_bytes_cannot_be_claimed_as_new_candidate(self):
        for raw in (self.source,self.reference):
            with self.subTest(sha=hashlib.sha256(raw).hexdigest()):
                qa=self.placement.inspect_candidate(raw,self.source,self.source_sha,
                                                      self.manifest,role="background")
                self.assertEqual(qa["technical_qa"],"rejected_source_or_reference_reused")

    def test_manifest_and_source_tampering_fail_before_candidate_decode(self):
        from copy import deepcopy
        changes={"source_rect_xyxy":[0,0,941,1672],
                 "reference_to_source_offset_xy":[0,0],
                 "reference_canvas":[1024,1536],
                 "scale_xy":[True,True],"source_sha256":"0"*64,
                 "reference_sha256":"0"*64,"generation_authorized":True}
        for field,value in changes.items():
            manifest=deepcopy(self.manifest)
            manifest[field]=value
            with self.subTest(field=field), self.assertRaisesRegex(
                    VideoForgeError,"MANIFEST_MISMATCH"):
                self.placement.inspect_candidate(b"not decoded",self.source,
                    self.source_sha,manifest,role="character")
        with self.assertRaisesRegex(VideoForgeError,"SOURCE_SHA_MISMATCH"):
            self.placement.inspect_candidate(b"",self.source,"0"*64,
                                                self.manifest,role="character")
        with self.assertRaisesRegex(VideoForgeError,"INVALID_ROLE"):
            self.audit(self.candidate(),role="approved_rig")

    def test_unreadable_non_png_and_animated_png_do_not_pass(self):
        image=self.candidate()
        second=image.copy()
        second.putpixel((20,30),(255,0,0,255))
        cases=[(b"not an image","rejected_unreadable_image"),
               (self.encode(image.convert("RGB"),fmt="JPEG"),"rejected_expected_static_png"),
               (self.encode(image,save_all=True,append_images=[second],duration=100),
                "rejected_expected_static_png")]
        for raw,expected in cases:
            with self.subTest(expected=expected):
                qa=self.placement.inspect_candidate(raw,self.source,self.source_sha,
                                                     self.manifest,role="character")
                self.assertEqual(qa["technical_qa"],expected)

    def test_cli_rechecks_real_rejected_archive_without_rewriting_or_rebilling(self):
        import io
        import json
        archived=p.existing_part("C11-P03","character-guarda_direito")
        file=p.ROOT/archived["file"]
        before=file.read_bytes()
        output=io.StringIO()
        with patch("sys.argv",["qa","--shot-id","C11-P03","--candidate-part",
                              "character-guarda_direito"]),patch("sys.stdout",output):
            with patch.object(p.proxy_images,"call_proxy") as charged:
                self.placement.main()
                charged.assert_not_called()
        qa=json.loads(output.getvalue())["candidate_qa"]
        self.assertEqual(qa["candidate_canvas"],[981,1602])
        self.assertEqual(qa["expected_canvas"],[944,1680])
        self.assertEqual(qa["technical_qa"],"rejected_reference_canvas_mismatch")
        self.assertEqual(qa["candidate_sha256"],archived["sha256"])
        self.assertEqual(file.read_bytes(),before)
        self.assertFalse(qa["canvas_alpha_candidate"])


if __name__=="__main__":
    unittest.main()
