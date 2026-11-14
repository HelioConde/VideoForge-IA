"""Female speech and fragment-aligned subtitle contract."""
import unittest

from videoforge.female_voice import phrases,stamp
from videoforge.errors import VideoForgeError


class FemaleVoiceTests(unittest.TestCase):
    def test_fragments_retain_exact_words_and_punctuation(self):
        source="Anya sabe que Loid é espião e que Yor é assassina. Mas ninguém sabe disso!"
        groups=phrases(source,max_words=8)
        self.assertEqual(" ".join(groups),source)
        self.assertGreater(len(groups),1)
        self.assertTrue(all(1<=len(g.split())<=8 for g in groups))

    def test_precise_srt_timestamp_with_milliseconds(self):
        self.assertEqual(stamp(0),"00:00:00,000")
        self.assertEqual(stamp(8.314),"00:00:08,314")
        self.assertEqual(stamp(61.5),"00:01:01,500")

    def test_invalid_text_rejected(self):
        with self.assertRaisesRegex(VideoForgeError,"FEMALE_VOICE_TEXT_INVALID"):
            phrases("")
        with self.assertRaisesRegex(VideoForgeError,"FEMALE_VOICE_TEXT_INVALID"):
            phrases("hello",max_words=1)

if __name__ == "__main__":
    unittest.main()
