import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.ep01_review_cut import validate_clip
from videoforge.ep01_camera_batch import sha


class ReviewCutTests(unittest.TestCase):
    def test_only_reuse_exact_editorial_shot_and_video(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shot = {"id":"C01-P01", "source":None,"duration_frames":30}
            video = folder/"preview.mp4"
            video.write_bytes(b"fixture")
            (folder/"props.json").write_text(json.dumps({"shots":[shot],"durationFrames":30}))
            (folder/"qa.json").write_text(json.dumps(dict(technical_qa_passed=True, all_frames_decoded=True,
                technical_preview_only=True, official_episode_approved=False, character_rig_approved=False,
                audio_status="not_included", mp4_sha256=sha(video))))
            self.assertEqual(validate_clip(folder,shot), sha(video))
            with self.assertRaises(ValueError):
                validate_clip(folder,dict(shot,duration_frames=31))
            video.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                validate_clip(folder,shot)
