"""Real archived three-image proxy composition: fail-closed source and visual gates."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

from videoforge import ep01_c08_proxy_composite as m


class IndependentProxyC08QA(unittest.TestCase):
    def test_real_archived_pngs_have_three_distinct_sha_and_same_v2_mother(self):
        sources=m.verified_sources()
        self.assertEqual(set(sources),{"background","cart","kael"})
        self.assertEqual(len({m.RECORDS[key]["sha256"] for key in sources}),3)
        for role,item in sources.items():
            self.assertEqual(item["proof"]["source_mother_sha256"],m.MOTHER_SHA)
            self.assertEqual(item["proof"]["generation_method"],
                             "proxy_generated_separate_image")
            self.assertTrue(item["proof"]["not_a_pixel_cutout"])
            self.assertIs(item["proof"]["human_visual_approval"],False)

    def test_three_real_pngs_make_unapproved_sha_grounded_composite(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"review"
            result=m.build(m.ROOT,target)
            self.assertEqual(result["source_pngs_SHA_verified"],3)
            self.assertEqual(result["new_image_generations"],0)
            self.assertEqual(result["new_proxy_calls"],0)
            self.assertEqual(result["original_images_overwritten"],0)
            self.assertFalse(result["image_scaling"])
            self.assertFalse(result["human_visual_approval"])
            self.assertFalse(result["kael_upper_hand_to_cart_contact_approved"])
            self.assertFalse(result["recomposition_approved_against_mother"])
            self.assertFalse(result["cart_independent_wheel_layers_generated"])
            self.assertFalse(result["rig_ready"])
            self.assertFalse(result["animation_complete"])
            self.assertEqual(result["youtube_publications"],0)
            self.assertLess(result["qa_cart_zone_opacity_kael"],0.02)
            for role in ("background","cart","kael"):
                with self.subTest(role=role):
                    row=result["native_source_QA"][role]
                    self.assertFalse(row["pixel_resampling"])
                    self.assertFalse(row["pixel_shift"])
                    self.assertFalse(row["original_png_modified"])
                    self.assertFalse(row["rig_ready"])
                    self.assertTrue((target/row["aligned_artifact"]).is_file())
                    with Image.open(target/row["aligned_artifact"]) as im:
                        self.assertEqual(im.size,m.CANVAS)
            self.assertEqual(result["native_source_QA"]["cart"]["pad_right_px"],14)
            self.assertEqual(result["native_source_QA"]["cart"]["crop_bottom_px"],21)
            self.assertEqual(result["native_source_QA"]["kael"]["crop_right_px"],1)
            self.assertEqual(result["native_source_QA"]["kael"]["pad_bottom_px"],1)
            self.assertTrue((target/result["composite_preview"]).is_file())
            with self.assertRaises(ValueError):
                m.build(m.ROOT,target)

    def test_tampered_source_sha_blocks_qa(self):
        with patch.dict(m.RECORDS["cart"],{"sha256":"0"*64}):
            with self.assertRaises(ValueError):
                m.verified_sources()

    def test_nontransparent_crop_must_never_remove_object_pixels(self):
        kael=Image.new("RGBA",(1054,1492),(0,0,0,0))
        ImageDraw.Draw(kael).rectangle((1053,600,1053,690),
                                      fill=(255,130,80,255))
        with self.assertRaisesRegex(ValueError,"right"):
            m.alignment("kael",kael)
        cart=Image.new("RGBA",(1039,1514),(0,0,0,0))
        ImageDraw.Draw(cart).rectangle((410,1498,550,1513),
                                      fill=(110,50,20,255))
        with self.assertRaisesRegex(ValueError,"bottom"):
            m.alignment("cart",cart)

    def test_cannot_write_new_qa_over_source_files(self):
        with self.assertRaises(ValueError):
            m.build(m.ROOT,m.ROOT/"canal"/"alchemy-lab"/"videos")


if __name__=="__main__":
    unittest.main()
