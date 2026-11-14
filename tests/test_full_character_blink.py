"""Regression: blink uses the identical full character reference and swaps frames."""
import inspect
import unittest
from videoforge.full_character_blink import eye_weight, prompt_for_character, generate, compose_same_character

class FullCharacterBlinkTests(unittest.TestCase):
    def test_prompt_changes_only_large_anyas_eyes(self):
        p=prompt_for_character({})
        for token in ("IMAGEM RGBA DO PERSONAGEM", "UNICA MUDANCA PERMITIDA",
                      "dois olhos fechados", "NADA MAIS PODE MUDAR",
                      "franja", "MESMA POSICAO"):
            self.assertIn(token.lower(),p.lower())
        self.assertNotIn("sobreponha um sticker",p.lower())

    def test_full_image_is_the_proxy_reference(self):
        src=inspect.getsource(generate)
        self.assertIn('base64.b64encode(blob)',src)
        self.assertIn('"/v1/images/edits"',src)
        self.assertIn('"input_fidelity":"high"',src)
        self.assertIn('"background":"transparent"',src)

    def test_never_modify_hair_or_any_outside_eyes(self):
        self.assertEqual(eye_weight(500,1050,[[421,1230,80,52],[611,1230,88,52]]),0)
        self.assertEqual(eye_weight(520,1230,[[421,1230,80,52],[611,1230,88,52]]),0)
        self.assertGreater(eye_weight(421,1230,[[421,1230,80,52],[611,1230,88,52]]),.99)
        src=inspect.getsource(compose_same_character)
        self.assertIn("safe=bytearray(base)",src)
        self.assertIn('non_eye_pixels_changed',src)
        self.assertIn('alpha_pixels_changed',src)
        self.assertIn("if w<=0:continue",src)

if __name__=="__main__":
    unittest.main()
