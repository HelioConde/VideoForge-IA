"""Deterministic QA for Anya's source-pixel body and head/hand roundtrip."""
import unittest
try:
    import numpy as np
except ImportError:  # runner do MVP não usa NumPy; rig especializado deve executar este teste
    np = None

from videoforge.errors import VideoForgeError
from videoforge.rig_three_hand_split import (
    repair_body_and_partition, rgba_over, roundtrip_metrics
)


@unittest.skipUnless(np is not None, 'NumPy não instalado no runner MVP; testar no runner de rig')
class RigThreeHandRoundtripTests(unittest.TestCase):
    def fixtures(self):
        source = np.zeros((8, 8, 4), dtype=np.uint8)
        source[1:3, 2:6] = [232, 149, 130, 255]  # head
        source[3:7, 2:6] = [60, 34, 33, 255]    # uniform
        source[3, 3] = [247, 182, 153, 255]    # hand over collar
        iso = np.zeros_like(source)
        iso[1:4, 2:6] = source[1:4, 2:6]       # old mask omitted torso
        head = np.zeros_like(source)
        head[1:3, 2:6] = source[1:3, 2:6]
        hand = np.zeros_like(source)
        hand[3, 3] = source[3, 3]
        body = np.zeros_like(source)
        body[3:7, 2:6] = [90, 80, 40, 255]     # edited, must be restored
        body[7, 4] = [90, 80, 40, 255]         # spill into transparent area
        return source, iso, head, hand, body

    def test_restores_original_uniform_and_strips_stray_pixels(self):
        source, iso, head, hand, body = self.fixtures()
        fixed, anya, others, restored, recovered = repair_body_and_partition(
            source, iso, head, hand, body, np)
        self.assertEqual(tuple(fixed[5, 3]), tuple(source[5, 3]))
        self.assertEqual(fixed[7, 4, 3], 0)
        self.assertGreater(restored, 0)
        self.assertGreater(recovered, 0)
        np.testing.assert_array_equal(
            anya[:, :, 3].astype(int) + others[:, :, 3].astype(int),
            source[:, :, 3].astype(int))
        neutral = rgba_over(rgba_over(fixed, head, np), hand, np)
        stats = roundtrip_metrics(neutral, anya, source, np)
        self.assertEqual(stats["missing_opaque_pixels"], 0)
        self.assertEqual(stats["stray_alpha_pixels"], 0)
        self.assertEqual(stats["large_rgb_error_pixels_gt20"], 0)

    def test_never_accept_foreign_head_outside_anya_mask(self):
        source, iso, head, hand, body = self.fixtures()
        head[0, 0] = [255, 1, 1, 255]
        with self.assertRaisesRegex(VideoForgeError, "FOREIGN_PIXELS_IN_HEAD"):
            repair_body_and_partition(source, iso, head, hand, body, np)

    def test_visible_body_restored_but_hidden_underlay_retained(self):
        source, iso, head, hand, body = self.fixtures()
        body[2, 3] = [10, 10, 10, 255]  # reconstruction hidden by head
        fixed, *_ = repair_body_and_partition(
            source, iso, head, hand, body, np)
        self.assertEqual(tuple(fixed[2, 3]), (10, 10, 10, 255))
        self.assertEqual(tuple(fixed[5, 3]), tuple(source[5, 3]))


if __name__ == "__main__":
    unittest.main()
