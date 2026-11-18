import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from videoforge import ep01_camera_batch as batch


class CameraBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = batch.build_plan()

    def test_real_inventory_and_editorial_timing(self):
        shots = self.plan['shots']
        self.assertEqual(len(shots), 40)
        self.assertEqual(sum(s['source'] is not None for s in shots), 39)
        self.assertEqual(sum(s['duration_frames'] for s in shots), 4890)
        self.assertEqual([s['duration_frames'] for s in shots[:4]], [60, 90, 90, 70])

    def test_approval_is_exact_and_rejected_contact_not_promoted(self):
        shots = {s['id']: s for s in self.plan['shots']}
        self.assertEqual(shots['C01-P02']['approval_status'], 'diagnostic_only_contact_rejected')
        self.assertEqual(shots['C01-P03']['approval_status'], 'pending_human_review')
        self.assertEqual(shots['C01-P04']['approval_status'], 'exact_sha_approval_record_exists')
        self.assertEqual(sum(s['approval_status'] == 'exact_sha_approval_record_exists' for s in shots.values()), 1)
        self.assertTrue(all(not s['rig']['enabled'] and not s['rig']['independent_hands'] for s in shots.values()))

    def test_source_tampering_and_escape_fail_closed(self):
        source = copy.deepcopy(self.plan['shots'][1]['source'])
        source['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'SHA mismatch'):
            batch.checked_source(batch.ROOT, source)
        source['file'] = '../escape.png'
        with self.assertRaisesRegex(ValueError, 'outside'):
            batch.checked_source(batch.ROOT, source)

    def test_cache_rejects_changed_video_or_changed_inputs(self):
        props = {'shots': self.plan['shots'][:4]}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder/'preview.mp4').write_bytes(b'previously-validated-test-placeholder')
            report = {'input_fingerprint': batch.fingerprint(batch.ROOT, props),
                      'mp4_sha256': batch.sha(folder/'preview.mp4'), 'technical_qa_passed': True, 'all_frames_decoded': True}
            batch.write(folder/'qa.json', report)
            self.assertTrue(batch.cache_valid(batch.ROOT, folder, props))
            changed = copy.deepcopy(props)
            changed['shots'][1]['duration_frames'] += 1
            self.assertFalse(batch.cache_valid(batch.ROOT, folder, changed))
            (folder/'preview.mp4').write_bytes(b'corrupted')
            self.assertFalse(batch.cache_valid(batch.ROOT, folder, props))

    def test_black_allowance_only_opening_and_sword_reveal(self):
        self.assertEqual(batch.black_ranges({'shots': self.plan['shots'][:4]}), [(0, 60), (60, 68)])

    def test_p05_preserves_integrated_grip_and_closes_c01_at_12_seconds(self):
        shot = self.plan['shots'][4]
        self.assertEqual(shot['id'], 'C01-P05')
        self.assertEqual(shot['start_frame'] + shot['duration_frames'], 360)
        self.assertEqual(sum(s['duration_frames'] for s in self.plan['shots'][:5]), 360)
        self.assertEqual(shot['camera']['end']['zoom'], 1.025)
        self.assertFalse(shot['rig']['enabled'])
        self.assertFalse(shot['rig']['independent_hands'])
        self.assertEqual(shot['approval_status'], 'pending_human_review')
        self.assertTrue(any('Empty throne' in warning for warning in shot['limitations']))

    def test_grown_historical_manifests_read_but_remain_bounded(self):
        from videoforge.cinematic_direction import load_active_remake_plan, _read
        from videoforge.production_art import read_plan
        from videoforge.errors import VideoForgeError
        self.assertIsNotNone(load_active_remake_plan('alchemy-lab', 'mmorpg-conquiste-a-princesa-ep01'))
        self.assertEqual(read_plan('alchemy-lab', 'mmorpg-conquiste-a-princesa-ep01')[0]['video_id'], 'mmorpg-conquiste-a-princesa-ep01')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'large.json'
            path.write_bytes(b' ' * 300001)
            with self.assertRaisesRegex(VideoForgeError, 'TOO_BIG'):
                _read(path)

    def test_decode_and_unexpected_black_fail(self):
        import json
        from types import SimpleNamespace
        metadata = {'streams': [{'codec_name':'h264', 'width':540, 'height':960,
                                'avg_frame_rate':'30/1', 'nb_frames':'2', 'duration':'0.066667'}]}
        with patch.object(batch.subprocess, 'check_output', return_value=json.dumps(metadata)), patch.object(batch.subprocess, 'run', return_value=SimpleNamespace(stdout=bytes(2048))):
            with self.assertRaisesRegex(ValueError, 'Unexpected black'):
                batch.verify_video(Path('unused'), 2)
        with patch.object(batch.subprocess, 'check_output', return_value=json.dumps(metadata)), patch.object(batch.subprocess, 'run', return_value=SimpleNamespace(stdout=bytes(1024))):
            with self.assertRaisesRegex(ValueError, 'Decoded frame count'):
                batch.verify_video(Path('unused'), 2)

    @unittest.skipUnless(batch.shutil.which('ffmpeg') and batch.shutil.which('ffprobe'), 'FFmpeg required')
    def test_real_encoded_black_is_detected_after_yuv_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'black.mp4'
            batch.subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=540x960:r=30', '-frames:v', '2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(path)], check=True)
            result = batch.verify_video(path, 2, [(0,2)])
            self.assertEqual(result['black_frames'], [0,1])
            with self.assertRaisesRegex(ValueError, 'Unexpected black'):
                batch.verify_video(path, 2)


if __name__ == '__main__':
    unittest.main()
