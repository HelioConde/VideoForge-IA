"""Base limpa do palácio tem fonte real e não aprova lanças defeituosas."""
import base64
import unittest
from videoforge.production_art import read_plan, asset_prompt
from videoforge.visual_bible_master import edit_payload, MODE, STYLE_SHA
from videoforge.dorama_continuity import reference
from videoforge.errors import VideoForgeError


class VisualBibleMasterTests(unittest.TestCase):
    def test_throne_room_empty_master_preserves_only_style_source(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = next(x for x in plan["assets"] if x["id"] == "biblia-sala-do-trono-vazio-v1")
        prompt, size = asset_prompt(plan, story, asset["id"])
        payload, provenance = edit_payload(asset, prompt, "gpt-image-2", size)
        anchor, raw = reference()
        self.assertEqual(base64.b64decode(payload["images"][0]["image_url"].split(",", 1)[1]), raw)
        self.assertEqual(len(payload["images"]), 1)
        self.assertEqual(provenance[0]["sha256"], STYLE_SHA)
        self.assertTrue(provenance[0]["source_spear_pose_rejected"])
        self.assertEqual(asset["biblia_item_id"], "sala-do-trono")
        self.assertEqual(asset["biblia_categoria"], "cenarios")
        self.assertIn("SEM PESSOAS", prompt.upper())
        self.assertIn("SEM LANÇAS", prompt.upper())
        self.assertFalse(asset["youtube_upload"])
    def test_kael_and_elara_use_two_original_images(self):
        from videoforge.grounded_identity import inputs
        sources={x["actor"]:x for x in inputs()}
        plan,story=read_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
        for asset_id,actor in (("biblia-kael-medieval-base-v1","kael"),
                               ("biblia-elara-palacio-base-v1","elara")):
            with self.subTest(actor=actor):
                asset=next(x for x in plan["assets"] if x["id"]==asset_id)
                prompt,size=asset_prompt(plan,story,asset_id)
                payload,provenance=edit_payload(asset,prompt,"gpt-image-2",size)
                self.assertEqual(len(payload["images"]),2)
                source=base64.b64decode(payload["images"][1]["image_url"].split(",",1)[1])
                self.assertEqual(source,sources[actor]["bytes"])
                self.assertEqual(provenance[1]["sha256"],sources[actor]["sha256"])
                self.assertEqual(asset["biblia_item_id"],actor)
                self.assertEqual(asset["biblia_categoria"],"personagens")
                self.assertIn("FUNDO NEUTRO",prompt.upper())
                self.assertFalse(asset["youtube_upload"])

    def test_character_variant_attaches_sha_verified_character_master(self):
        import hashlib
        from videoforge.production_art import archived_reference
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = next(x for x in plan["assets"] if x["id"] == "biblia-kael-casual-antes-v1")
        self.assertEqual(asset["additional_master_asset_ids"], ["biblia-kael-medieval-base-v1"])
        prompt, size = asset_prompt(plan, story, asset["id"])
        payload, provenance = edit_payload(asset, prompt, "gpt-image-2", size)
        self.assertEqual(len(payload["images"]), 3)
        archived = archived_reference("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", "biblia-kael-medieval-base-v1")
        self.assertIsNotNone(archived)
        self.assertEqual(provenance[-1]["sha256"], archived["sha256"])
        self.assertEqual(provenance[-1]["id"], "biblia-kael-medieval-base-v1")
        raw = base64.b64decode(payload["images"][-1]["image_url"].split(",", 1)[1])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), archived["sha256"])

    def test_character_variant_missing_master_fails_before_paid_call(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = dict(next(x for x in plan["assets"] if x["id"] == "biblia-kael-casual-antes-v1"))
        asset["additional_master_asset_ids"] = ["biblia-master-not-archived-v1"]
        prompt, size = asset_prompt(plan, story, asset["id"])
        with self.assertRaisesRegex(VideoForgeError, "EXTRA_SOURCE_NOT_ARCHIVED"):
            edit_payload(asset, prompt, "gpt-image-2", size)

    def test_modern_kael_v2_uses_original_face_only_not_medieval_clothes(self):
        import hashlib
        from videoforge.grounded_identity import inputs
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = next(x for x in plan["assets"] if x["id"] == "biblia-kael-casual-antes-v2")
        self.assertEqual(asset["reference_mode"], "identity_face_only_kael")
        self.assertFalse(asset.get("additional_master_asset_ids"))
        prompt, size = asset_prompt(plan, story, asset["id"])
        payload, provenance = edit_payload(asset, prompt, "gpt-image-2", size)
        self.assertEqual(len(payload["images"]), 1)
        kael = next(x for x in inputs() if x["actor"] == "kael")
        original = base64.b64decode(payload["images"][0]["image_url"].split(",", 1)[1])
        self.assertEqual(hashlib.sha256(original).hexdigest(), kael["sha256"])
        self.assertEqual(provenance[0]["sha256"], kael["sha256"])
        self.assertNotIn("estilo_do_palacio", [x.get("actor") for x in provenance])
        self.assertIn("NÃO usar o mestre de corpo inteiro medieval", prompt)

    def test_spear_base_v2_uses_only_corrected_complete_spear(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = next(x for x in plan["assets"] if x["id"] == "biblia-lanca-guarda-base-v2")
        self.assertEqual(asset["reference_mode"], "master_only")
        self.assertEqual(asset["additional_master_asset_ids"],
                         ["biblia-lanca-guarda-completa-v2"])
        from videoforge.production_art import archived_reference
        ref = archived_reference(
            "alchemy-lab", "mmorpg-conquiste-a-princesa-ep01",
            "biblia-lanca-guarda-completa-v2")
        self.assertIsNotNone(ref, "A lança V2 deve estar arquivada para gerar seus detalhes")
        prompt, size = asset_prompt(plan, story, asset["id"])
        payload, provenance = edit_payload(asset, prompt, "gpt-image-2", size)
        self.assertEqual(len(payload["images"]), 1)
        self.assertEqual(len(provenance), 1)
        self.assertEqual(provenance[0]["id"], "biblia-lanca-guarda-completa-v2")
        self.assertEqual(provenance[0]["sha256"], ref["sha256"])
        self.assertFalse(any(r.get("source_spear_pose_rejected") for r in provenance))
        import hashlib
        raw = base64.b64decode(payload["images"][0]["image_url"].split(",", 1)[1])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), ref["sha256"])

    def test_face_only_refuses_accidental_medieval_body_attachment(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = dict(next(x for x in plan["assets"] if x["id"] == "biblia-kael-casual-antes-v2"))
        asset["additional_master_asset_ids"] = ["biblia-kael-medieval-base-v1"]
        prompt, size = asset_prompt(plan, story, asset["id"])
        with self.assertRaisesRegex(VideoForgeError, "BIBLE_FACE_ONLY_CANNOT_ATTACH_MEDIEVAL_BODY"):
            edit_payload(asset, prompt, "gpt-image-2", size)

    def test_new_masked_actors_use_empty_palace_style_not_kael(self):
        import hashlib
        from videoforge.production_art import archived_reference
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        source = archived_reference(
            "alchemy-lab", "mmorpg-conquiste-a-princesa-ep01",
            "biblia-sala-do-trono-vazio-v1")
        self.assertIsNotNone(source)
        for asset_id in ("biblia-carrasco-base-v2", "biblia-figurantes-base-v2",
                         "biblia-mascarado-1-base-v2", "biblia-mascarado-2-base-v2"):
            with self.subTest(asset_id=asset_id):
                asset = next(x for x in plan["assets"] if x["id"] == asset_id)
                self.assertEqual(asset["reference_mode"], "style_environment_only")
                prompt, size = asset_prompt(plan, story, asset_id)
                payload, provenance = edit_payload(asset, prompt, "gpt-image-2", size)
                self.assertEqual(len(payload["images"]), 1)
                self.assertEqual(provenance[0]["sha256"], source["sha256"])
                self.assertTrue(provenance[0]["source_character_identity_forbidden"])
                self.assertNotEqual(provenance[0]["sha256"], STYLE_SHA)
                raw = base64.b64decode(payload["images"][0]["image_url"].split(",",1)[1])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), source["sha256"])

    def test_group_of_masked_actors_requires_two_v2_references(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = next(x for x in plan["assets"] if x["id"] == "biblia-mascarados-base-v2")
        self.assertEqual(asset["reference_mode"], "master_only")
        self.assertEqual(asset["additional_master_asset_ids"], [
            "biblia-mascarado-1-base-v2", "biblia-mascarado-2-base-v2"])
        from videoforge.production_art import archived_reference
        deps = asset["additional_master_asset_ids"]
        archived = [archived_reference(
            "alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", dep)
            for dep in deps]
        prompt, size = asset_prompt(plan, story, asset["id"])
        if all(archived):
            payload, provenance = edit_payload(asset, prompt, "gpt-image-2", size)
            self.assertEqual(len(payload["images"]), 2)
            self.assertEqual([r["id"] for r in provenance], deps)
            self.assertEqual([r["sha256"] for r in provenance],
                             [r["sha256"] for r in archived])
        else:
            with self.assertRaisesRegex(VideoForgeError, "BIBLE_MASTER_EXTRA_SOURCE_NOT_ARCHIVED"):
                edit_payload(asset, prompt, "gpt-image-2", size)

    def test_wrong_environment_sha_is_rejected_before_provider(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = dict(next(x for x in plan["assets"] if x["id"] == "biblia-mascarado-1-base-v2"))
        asset["environment_style_sha256"] = "0" * 64
        prompt, size = asset_prompt(plan, story, asset["id"])
        with self.assertRaisesRegex(VideoForgeError, "BIBLE_ENVIRONMENT_STYLE_SHA_INVALID"):
            edit_payload(asset, prompt, "gpt-image-2", size)

    def test_missing_master_only_source_never_triggers_image_provider(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = dict(next(x for x in plan["assets"] if x["id"] == "biblia-lanca-guarda-base-v2"))
        asset["additional_master_asset_ids"] = ["biblia-nunca-criada-v9"]
        prompt, size = asset_prompt(plan, story, asset["id"])
        with self.assertRaisesRegex(VideoForgeError, "BIBLE_MASTER_EXTRA_SOURCE_NOT_ARCHIVED"):
            edit_payload(asset, prompt, "gpt-image-2", size)

    def test_spear_interaction_requires_human_approved_masters(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = next(x for x in plan["assets"] if x["id"] == "biblia-guardas-cruzando-lancas-base-v1")
        self.assertEqual(asset["reference_mode"], "approved_masters_only")
        self.assertEqual(len(asset["additional_master_asset_ids"]), 3)
        self.assertIn("TERÇO INFERIOR", asset["prompt"])
        self.assertIn("NÃO anexar nem copiar C01-P04 V3 ou V4", asset["prompt"])
        prompt, size = asset_prompt(plan, story, asset["id"])
        with self.assertRaisesRegex(VideoForgeError, "BIBLE_MASTER_EXTRA_SOURCE_NOT_ARCHIVED|BIBLE_INTERACTION_SOURCE_NOT_HUMAN_APPROVED"):
            edit_payload(asset, prompt, "gpt-image-2", size)

    def test_fake_reference_blocks_before_provider(self):
        plan, story = read_plan("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01")
        asset = dict(next(x for x in plan["assets"] if x["id"] == "biblia-sala-do-trono-vazio-v1"))
        asset["required_source_sha256"] = "0" * 64
        prompt, size = asset_prompt(plan, story, asset["id"])
        with self.assertRaisesRegex(VideoForgeError, "STYLE_SHA_MISMATCH"):
            edit_payload(asset, prompt, "gpt-image-2", size)


if __name__ == "__main__":
    unittest.main()
