"""Regressões da espada: nunca acima dos dedos, nunca redimensionada."""
import hashlib
import unittest
from PIL import ImageChops
from videoforge.ep01_shot_layers import mother_source
from videoforge.ep01_contact_cutouts import make_source_cutouts
from videoforge.ep01_source_sword import candidate, sword_mask
from videoforge.errors import VideoForgeError


class SwordSourceTests(unittest.TestCase):
    def test_same_mother_pixels_and_size_without_redrawing(self):
        plan,raw,_=mother_source()
        first,qa=candidate(raw)
        _,ref=mother_source()
        self.assertEqual(first.size,(941,1672))
        self.assertTrue(qa["source_rgb_exact"])
        self.assertEqual(qa["source_coordinate_offset"],[0,0])
        self.assertEqual(qa["source_scale"],1)
        self.assertFalse(qa["original_pixels_resampled"])
        self.assertGreater(qa["visible_pixels"],1000)

    def test_sword_is_hidden_below_gloves(self):
        _,raw,_=mother_source()
        gloved,_=make_source_cutouts(raw)
        mask=sword_mask((941,1672),gloved)
        upper=gloved["hand-upper-contact-occlusion"].getchannel("A")
        lower=gloved["hand-lower-contact-occlusion"].getchannel("A")
        overlap=ImageChops.darker(mask,ImageChops.lighter(upper,lower))
        self.assertIsNone(overlap.getbbox())

    def test_unsafe_canvas_blocked(self):
        _,raw,_=mother_source()
        glove,_=make_source_cutouts(raw)
        with self.assertRaisesRegex(VideoForgeError,"EP01_SWORD_MOTHER_CANVAS_CHANGED"):
            sword_mask((981,1602),glove)


if __name__=="__main__":
    unittest.main()
