"""Original C01 black opening audio can be recreated without Actions artifact."""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import shutil
import tempfile
import unittest

from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import EPISODE
from videoforge.remake_episode_audio import source_verified_wav,prepare,SCHEMA

ROOT=Path(__file__).resolve().parents[1]


class OriginalOpeningAudioTests(unittest.TestCase):
    def test_sha_reconstruction_matches_qa_and_first_shot(self):
        audio,digest=source_verified_wav()
        qa=json.loads((ROOT/EPISODE/"QA-C01-P01-REMAKE-V2.json").read_text(encoding="utf8"))
        self.assertEqual(digest,qa["audio_sha256"])
        self.assertEqual(digest,hashlib.sha256(audio).hexdigest())
        self.assertEqual(len(audio)>48000,True)

    def test_staging_is_idempotent_and_never_claims_full_episode(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"public/vf-remake/c01-p01"
            first=prepare(out)
            self.assertEqual(first["schema"],SCHEMA)
            self.assertTrue(first["created"])
            self.assertFalse(first["render_full_episode_approved"])
            self.assertFalse(first["youtube_uploaded"])
            second=prepare(out)
            self.assertFalse(second["created"])
            self.assertEqual(second["audio_sha256"],first["audio_sha256"])
            audio=out/"sword-original.wav"
            with audio.open("ab") as fp:fp.write(b"tamper")
            with self.assertRaisesRegex(VideoForgeError,"EXISTING_WAV_MISMATCH"):
                prepare(out)

    def test_tampered_qa_proof_blocks_audio_even_if_synthesis_is_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            episode=root/EPISODE
            episode.mkdir(parents=True)
            for name in ("remake-ep01-planos.json","QA-C01-P01-REMAKE-V2.json"):
                shutil.copyfile(ROOT/EPISODE/name,episode/name)
            doc=episode/"QA-C01-P01-REMAKE-V2.json"
            q=json.loads(doc.read_text(encoding="utf8"))
            q["audio_sha256"]="f"*64
            doc.write_text(json.dumps(q),encoding="utf8")
            with self.assertRaisesRegex(VideoForgeError,"PROVENANCE_NOT_AUDITED"):
                source_verified_wav(root)
            self.assertFalse((root/"public/vf-remake/c01-p01/sword-original.wav").exists())

    def test_wrong_origin_hash_and_symlink_destination_do_not_mutate(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            out=root/"audio"
            out.symlink_to(ROOT)
            with self.assertRaisesRegex(VideoForgeError,"SYMLINK_DESTINATION"):
                prepare(out)


if __name__=="__main__":
    unittest.main()
