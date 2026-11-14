"""Source-pixel Anya side hair splitting must not fake an approved rig."""
import unittest
import numpy as np

from videoforge.errors import VideoForgeError
from videoforge.rig_three_hair_draft import _hair_partition, H, W


class AnyaHairDraftTests(unittest.TestCase):
    def fixture(self):
        head=np.zeros((H,W,4),dtype=np.uint8)
        head[1280:1450,215:390]=[230,130,120,255]
        head[1280:1450,655:770]=[231,130,120,255]
        head[1095:1130,490:520]=[250,220,198,255]
        closed=head.copy()
        closed[1105:1114,500:510,:3]=[170,80,60]
        seed=head.copy()
        return head,closed,seed

    def test_separate_disjoint_locks_preserve_approved_eye_delta(self):
        head,closed,seed=self.fixture()
        base,base_closed,locks,counts=_hair_partition(
            head,closed,seed,np)
        self.assertGreater(counts[0],18000)
        self.assertGreater(counts[1],18000)
        self.assertFalse(np.any(base[:,:,3] & locks[0][:,:,3]))
        self.assertFalse(np.any(base[:,:,3] & locks[1][:,:,3]))
        self.assertTrue(np.any(base[1105:1114,500:510,:3] !=
                               base_closed[1105:1114,500:510,:3]))
        self.assertFalse(np.any(locks[0][1105:1114,500:510,3]))
        self.assertFalse(np.any(locks[1][1105:1114,500:510,3]))

    def test_cannot_cut_a_closed_eye_inside_moving_hair(self):
        head,closed,seed=self.fixture()
        closed[1350,300,0]=0
        with self.assertRaisesRegex(VideoForgeError,"CUT_APPROVED_BLINK"):
            _hair_partition(head,closed,seed,np)

    def test_wrong_canvas_is_blocked(self):
        head,closed,seed=self.fixture()
        with self.assertRaisesRegex(VideoForgeError,"CANVAS_MISMATCH"):
            _hair_partition(head[:-1],closed,seed,np)


if __name__=="__main__":
    unittest.main()
