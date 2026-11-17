"""Regressões: encaixe da bainha/luvas vem do MESMO PNG, sem poses/IA."""
import hashlib
import io
import unittest
from unittest.mock import patch
from PIL import Image, ImageChops

from videoforge import ep01_contact_cutouts as m
from videoforge.ep01_shot_layers import mother_source
from videoforge.errors import VideoForgeError


class ContactSourceTests(unittest.TestCase):
    def test_mask_source_is_sha_verified_and_native(self):
        _,raw,info=mother_source()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),m.EXPECTED_MOTHER_SHA)
        self.assertEqual((info["width"],info["height"]),(941,1672))
        self.assertEqual(len(m.CONTACT_ORDER),3)

    def test_all_masked_pixels_keep_original_rgb_unmoved(self):
        _,raw,_=mother_source()
        source=Image.open(io.BytesIO(raw)).convert("RGBA")
        candidates,qa=m.make_source_cutouts(raw)
        self.assertEqual(set(candidates),set(m.CONTACT_ORDER))
        for name,cutout in candidates.items():
            with self.subTest(name=name):
                self.assertEqual(cutout.size,source.size)
                self.assertEqual(
                    ImageChops.difference(cutout.convert("RGB"),
                                          source.convert("RGB")).getbbox(),None)
                self.assertGreater(qa[name]["filled_pixels"],0)
                self.assertEqual(qa[name]["offset"],[0,0])
                self.assertEqual(qa[name]["scale"],1)
                self.assertTrue(qa[name]["draft_polygon_requires_visual_review"])

    def test_gloves_occlude_visible_sheath_not_reverse(self):
        _,raw,_=mother_source()
        candidates,_=m.make_source_cutouts(raw)
        sheath=candidates["object-bainha-source-visible"].getchannel("A")
        glove1=candidates["hand-upper-contact-occlusion"].getchannel("A")
        glove2=candidates["hand-lower-contact-occlusion"].getchannel("A")
        overlap=ImageChops.darker(sheath,ImageChops.lighter(glove1,glove2))
        self.assertIsNone(overlap.getbbox(),"Sheath must never cover gloves")

    def test_invalid_name_or_canvas_is_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"EP01_CONTACT_UNKNOWN_MASK"):
            m.polygon_mask((941,1672),"wrong-layer")
        with self.assertRaisesRegex(VideoForgeError,"EP01_CONTACT_MOTHER_CANVAS_CHANGED"):
            m.polygon_mask((981,1602),m.CONTACT_ORDER[0])

    def test_is_deterministic_and_has_no_paid_proxy_call(self):
        _,raw,_=mother_source()
        with patch("videoforge.proxy_images.call_proxy") as paid:
            first,_=m.make_source_cutouts(raw)
            second,_=m.make_source_cutouts(raw)
            paid.assert_not_called()
        for name in m.CONTACT_ORDER:
            self.assertEqual(first[name].tobytes(),second[name].tobytes())


if __name__=="__main__":
    unittest.main()
