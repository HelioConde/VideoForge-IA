"""Contato mão/bainha V3: não transformar erro antigo em imagem canônica."""
import hashlib
import unittest
from unittest.mock import patch

from videoforge import ep01_contact_repair as repair
from videoforge.errors import VideoForgeError


class ContactRepairTests(unittest.TestCase):
    def test_panels_2_and_4_are_rejected_before_paid_call(self):
        with patch.object(repair.proxy_images,"call_proxy") as paid:
            spec=repair.prepare()
            paid.assert_not_called()
        self.assertEqual(spec["review"]["owner_review"]["rejected_panels"],[2,4])
        self.assertEqual(hashlib.sha256(spec["original"]).hexdigest(),repair.EXPECTED_MOTHER_SHA)
        self.assertEqual((spec["width"],spec["height"]),(941,1672))
        self.assertIn("bainha deve ficar claramente",spec["prompt"])
        self.assertIn("ATRÁS dos dedos",spec["prompt"])
        self.assertIn("NÃO redesenhe todo",spec["prompt"])
        self.assertTrue(spec["roi"][0]<spec["roi"][2])

    def test_existing_archived_v3_cannot_be_regenerated(self):
        with patch.object(repair,"archived_candidate",return_value={"sha256":"a"*64}):
            with patch.object(repair.proxy_images,"call_proxy") as paid:
                with self.assertRaisesRegex(VideoForgeError,"EP01_REPAIR_CANDIDATE_ALREADY_ARCHIVED"):
                    repair.prepare()
                paid.assert_not_called()

    def test_non_gpt_image_2_rejected_before_provider(self):
        with patch.object(repair.proxy_images,"call_proxy") as paid:
            with self.assertRaisesRegex(VideoForgeError,"EP01_REPAIR_MODEL_NOT_ALLOWED"):
                repair.generate("http://127.0.0.1:18080",model="unknown")
            paid.assert_not_called()

    def test_repair_does_not_use_old_displaced_scabbard(self):
        spec=repair.prepare()
        self.assertNotIn("QA-C01-P02-REGISTRO-BAINHA.jpg",spec["prompt"])
        self.assertNotIn("object-bainha.png",spec["prompt"])
        self.assertEqual(repair.PATCH_ASSET,"c01-p02-contact-local-patch-v3")


if __name__=="__main__":
    unittest.main()
