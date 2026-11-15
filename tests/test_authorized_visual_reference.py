import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from videoforge.authorized_visual_reference import load_reference, CHANNEL, VIDEO, CONTRACT
from videoforge.production_scenes import ROOT, scene_prompt, reference_bytes
from videoforge.cinematic_direction import load_plan
from videoforge.errors import VideoForgeError

class AuthorizedReferenceTests(unittest.TestCase):
    def test_png_preserves_all_decoded_original_pixels(self):
        import io
        from PIL import Image
        canonical=load_reference(ROOT,CHANNEL,VIDEO)
        original=ROOT/'canal'/CHANNEL/'videos'/VIDEO/'assets/referencias/user-20261115/reference-original.jpg'
        with Image.open(original) as a, Image.open(io.BytesIO(canonical['source'])) as b:
            self.assertEqual(a.size,b.size)
            self.assertEqual(a.convert('RGB').tobytes(),b.convert('RGB').tobytes())

    def test_every_visual_shot_includes_exact_user_prompt(self):
        data=load_reference(ROOT,CHANNEL,VIDEO)
        for shot in load_plan(CHANNEL,VIDEO)['shots']:
            if shot['shot_type']=='black':
                continue
            prompt,_=scene_prompt(CHANNEL,VIDEO,int(shot['scene'][1:]),shot['id'])
            self.assertIn(data['prompt'],prompt)
            self.assertLessEqual(len(prompt),5000)

    def test_native_reference_is_accepted_without_resizing(self):
        data=load_reference(ROOT,CHANNEL,VIDEO)
        base=ROOT/'canal'/CHANNEL/'videos'/VIDEO
        raw,sha=reference_bytes(base/data['contract']['reference_file'],base/CONTRACT)
        self.assertEqual(raw,data['source'])
        self.assertEqual(data['contract']['reference_size'],[720,1280])
        self.assertFalse(data['contract']['rig_approved'])
        self.assertEqual(sha,data['contract']['reference_sha256'])

    def test_wrong_reference_bytes_cannot_use_canonical_report(self):
        with TemporaryDirectory() as folder:
            image=Path(folder)/'wrong.png'
            image.write_bytes(b'not the user reference')
            with self.assertRaisesRegex(VideoForgeError,'CANONICAL_REFERENCE_MISMATCH'):
                reference_bytes(image,ROOT/'canal'/CHANNEL/'videos'/VIDEO/CONTRACT)

    def test_other_channels_are_unchanged(self):
        self.assertIsNone(load_reference(ROOT,'otaku-br','another-video'))
