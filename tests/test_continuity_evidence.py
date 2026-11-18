"""Zero-network tests for C07/C08 read-only documentary QA export."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from orchestrator.continuity_evidence import build_evidence, validated_shot_timeline
from orchestrator.runtime_store import Store


class ContinuityEvidenceTests(unittest.TestCase):
    def test_valid_timeline_is_preserved(self):
        shots = [
            {"id": "C07-P01", "beat": "Fuga", "start_frame": 2070, "end_exclusive": 2160},
            {"id": "C07-P02", "beat": "Perseguicao", "start_frame": 2160, "end_exclusive": 2250},
        ]
        result = validated_shot_timeline(shots)
        self.assertEqual(result, shots)
        self.assertEqual(result[-1]["end_exclusive"], 2250)

    def test_invalid_timeline_rejected(self):
        base = [
            {"id": "C07-P01", "beat": "Fuga", "start_frame": 2070, "end_exclusive": 2160},
            {"id": "C07-P02", "beat": "Perseguicao", "start_frame": 2160, "end_exclusive": 2250},
        ]
        cases = [
            [],
            [base[0], {**base[1], "start_frame": 2161}],
            [base[0], {**base[1], "start_frame": 2159}],
            [base[0], {**base[1], "id": "C07-P01"}],
            [base[0], {**base[1], "start_frame": True}],
            [base[0], {**base[1], "end_exclusive": 2160}],
            [base[0], {**base[1], "beat": ""}],
            [base[0], "not a shot"],
        ]
        for sample in cases:
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                validated_shot_timeline(sample)

    def test_empty_state_cannot_be_promoted_to_documentary_qa(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Store(Path(temp) / "state.sqlite")
            try:
                with patch("orchestrator.providers.urllib.request.build_opener") as network:
                    with self.assertRaises(ValueError):
                        build_evidence(store)
                network.assert_not_called()
                self.assertFalse(store.export_snapshot()["tables"]["checkpoints"])
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
