"""C01-P01 original SFX production: deterministic, no API, no fake art."""
import hashlib
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
import wave

from videoforge.remake_opening import (
    DURATION,SAMPLE_RATE,FRAMES,_wav_bytes,original_sword_pcm,
    prepare,verify_mp4,
)
from videoforge.errors import VideoForgeError


class OpeningAudioTests(unittest.TestCase):
    def test_original_sfx_is_repeatable_and_has_exact_length(self):
        first=original_sword_pcm()
        self.assertEqual(first,original_sword_pcm())
        self.assertEqual(len(first),DURATION*SAMPLE_RATE*2)
        self.assertEqual(DURATION*30,FRAMES)

    def test_wav_is_real_audio_and_not_silent_or_clipped(self):
        wav=_wav_bytes()
        with wave.open(BytesIO(wav),"rb") as r:
            self.assertEqual(r.getnframes(),96000)
            self.assertEqual(r.getframerate(),SAMPLE_RATE)
            self.assertEqual(r.getnchannels(),1)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            a=prepare(root/"output",root/"public")
            b=prepare(root/"output",root/"public")
            self.assertEqual(a,b)
            self.assertEqual(a["sha256"],hashlib.sha256(wav).hexdigest())
            self.assertGreater(a["rms"],.025)
            self.assertLess(a["peak"],.95)
            self.assertEqual((root/"output/sword-original.wav").read_bytes(),wav)
            self.assertEqual((root/"public/sword-original.wav").read_bytes(),wav)
            self.assertFalse(a["official_video_approved"])

    def test_no_mp4_claim_if_remotion_did_not_render(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            prepare(root/"output",root/"public")
            with self.assertRaisesRegex(VideoForgeError,"REQUIRED_BYTES_MISSING"):
                verify_mp4(root/"output")


if __name__=="__main__":
    unittest.main()
