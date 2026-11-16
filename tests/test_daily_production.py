import unittest
from videoforge.daily_production import inspect
from videoforge.errors import VideoForgeError
class DailyProductionTests(unittest.TestCase):
    def test_five_channels_and_no_phantom_uploads(self):
        o=inspect(day="2026-11-16")
        self.assertEqual(o["target_videos_per_day"],5)
        self.assertEqual(len(o["channels"]),5)
        self.assertEqual(o["uploads"],0)
        self.assertEqual(o["generated_videos"],0)
        self.assertTrue(o["alchemy_ep01_r2_blocked"])
    def test_technical_render_is_not_publication(self):
        o=inspect(day="2026-11-16")
        br=next(x for x in o["channels"] if x["channel"]=="otaku-br")
        self.assertEqual(br["local_post_records"],0)
        self.assertTrue(br["history_incomplete"])
        self.assertFalse(br["youtube_upload_claimed"])
    def test_bad_date(self):
        with self.assertRaisesRegex(VideoForgeError,"DAILY_DATE_INVALID"):
            inspect(day="nonsense")
if __name__=="__main__":unittest.main()
