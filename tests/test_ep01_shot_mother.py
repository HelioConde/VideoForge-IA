"""A cena-mãe usa bytes originais verificados e não exige poses isoladas."""
import unittest
from unittest.mock import patch

from videoforge.errors import VideoForgeError
from videoforge import ep01_shot_mother as mother


class MotherShotTests(unittest.TestCase):
    def test_shot_reference_plan_covers_40(self):
        rows = mother.read_refs()["shots"]
        self.assertEqual(len(rows), 40)
        self.assertEqual(len([x for x in rows if not x.get("black")]), 39)
        self.assertEqual(next(x for x in rows if x["id"] == "C01-P01")["reference_asset_ids"], [])

    def test_first_shot_attaches_three_real_sha_verified_masters(self):
        # C01-P02 has a real archived V1 mother; bypass only the archive guard
        # for this pure reference/prompt test (never for production).
        with patch.object(mother, "existing_mother", return_value=None):
            with patch.object(mother.proxy_images, "call_proxy") as pay:
                spec = mother.prepare("C01-P02")
                pay.assert_not_called()
        self.assertEqual([s["id"] for s in spec["references"]], [
            "biblia-carrasco-base-v2",
            "biblia-espada-carrasco-base-v1",
            "biblia-sala-do-trono-vazio-v1"])
        import hashlib
        self.assertEqual(len(spec["blobs"]), 3)
        for blob, ref in zip(spec["blobs"], spec["references"]):
            self.assertEqual(hashlib.sha256(blob).hexdigest(), ref["sha256"])
            self.assertTrue(ref["visual_approval_pending"])
        self.assertIn("FOCO PRINCIPAL espada", spec["prompt"])
        self.assertIn("NÃO pintar trilhas", spec["prompt"])
        self.assertLess(len(spec["prompt"]), 5000)

    def test_guards_reuse_corrected_portable_spear(self):
        for ident in ("C01-P04", "C01-P05"):
            with self.subTest(ident=ident):
                spec = mother.prepare(ident)
                refs = [x["id"] for x in spec["references"]]
                self.assertIn("biblia-lanca-guarda-completa-v2", refs)
                self.assertNotIn("biblia-lanca-guarda-completa-v1", refs)
                self.assertIn("TERÇO INFERIOR", spec["prompt"])

    def test_black_shot_cannot_generate(self):
        with self.assertRaisesRegex(VideoForgeError, "EP01_MOTHER_BLACK_FRAME_NO_PAID_IMAGE"):
            mother.prepare("C01-P01")

    def test_unarchived_source_fails_before_paid_call(self):
        real = mother.archived_reference
        def simulate_missing(channel, video, asset, root=mother.ROOT):
            if asset == "biblia-espada-carrasco-base-v1":
                return None
            return real(channel, video, asset, root)
        with patch.object(mother, "existing_mother", return_value=None):
            with patch.object(mother, "archived_reference", side_effect=simulate_missing):
                with patch.object(mother.proxy_images, "call_proxy") as paid:
                    with self.assertRaisesRegex(VideoForgeError, "EP01_MOTHER_REFERENCE_NOT_ARCHIVED"):
                        mother.prepare("C01-P02")
                    paid.assert_not_called()

    def test_archive_prevents_second_paid_attempt(self):
        with patch.object(mother, "existing_mother", return_value={"sha256": "a" * 64}):
            with self.assertRaisesRegex(VideoForgeError, "EP01_MOTHER_ALREADY_ARCHIVED_SHA_NO_REPEAT"):
                mother.prepare("C01-P02")

    def test_rejected_masters_are_not_reintroduced(self):
        doc = mother.read_refs()
        forbidden = {"biblia-carrasco-base-v1", "biblia-lanca-guarda-completa-v1",
                     "biblia-kael-casual-antes-v1", "biblia-mascarados-base-v1"}
        for entry in doc["shots"]:
            self.assertFalse(forbidden & set(entry["reference_asset_ids"]))


if __name__ == "__main__":
    unittest.main()
