"""Restore original, deterministic C01-P01 sword SFX for future full V2 render.

Pure local sound synthesis from the ALREADY QA'd source equations. No paid API,
stock audio, speech model, image calls, FFmpeg animation or YouTube.
The official video remains blocked until all 39 visual shots pass QA.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys
import wave

from .errors import VideoForgeError
from .remake_autopilot import ROOT,EPISODE
from .remake_opening import _wav_bytes,SAMPLE_RATE,DURATION,FRAMES,WAVE_NAME

QA_NAME="QA-C01-P01-REMAKE-V2.json"
SCHEMA="videoforge/remake-original-opening-audio-staging/v1"
SHA64=__import__("re").compile(r"^[0-9a-f]{64}$")


def source_verified_wav(root:Path=ROOT)->tuple[bytes,str]:
    episode=Path(root)/EPISODE
    qa_path=episode/QA_NAME
    plan_path=episode/"remake-ep01-planos.json"
    if (not qa_path.is_file() or qa_path.is_symlink() or
        not plan_path.is_file() or plan_path.is_symlink()):
        raise VideoForgeError("REMAKE_EPISODE_AUDIO_SOURCE_PROOF_MISSING")
    try:
        qa=json.loads(qa_path.read_text(encoding="utf-8"))
        plan=json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise VideoForgeError("REMAKE_EPISODE_AUDIO_PROOF_JSON_INVALID") from exc
    opening=plan.get("shots",[None])[0]
    expected=qa.get("audio_sha256")
    if (not isinstance(opening,dict)
        or opening.get("shot_id")!="C01-P01"
        or opening.get("frame_start")!=0
        or opening.get("frame_end_exclusive")!=FRAMES
        or qa.get("schema")!="videoforge/remake-opening-technical-qa/v1"
        or qa.get("shot")!="C01-P01"
        or qa.get("technical_preview_only") is not True
        or qa.get("audio_original_sfx_verified") is not True
        or qa.get("youtube_uploaded") is not False
        or qa.get("official_video_approved") is not False
        or not isinstance(expected,str) or not SHA64.fullmatch(expected)
        or expected!=opening.get("original_audio_sha256")):
        raise VideoForgeError("REMAKE_EPISODE_AUDIO_PROVENANCE_NOT_AUDITED")
    audio=_wav_bytes()
    digest=hashlib.sha256(audio).hexdigest()
    if digest!=expected:
        raise VideoForgeError("REMAKE_EPISODE_AUDIO_REGENERATED_SHA_MISMATCH")
    with wave.open(BytesIO(audio),"rb") as wav:
        if (wav.getframerate(),wav.getnchannels(),wav.getsampwidth(),
                wav.getnframes())!=(SAMPLE_RATE,1,2,SAMPLE_RATE*DURATION):
            raise VideoForgeError("REMAKE_EPISODE_AUDIO_WAV_FORMAT_INVALID")
    return audio,digest


def prepare(destination:Path,root:Path=ROOT)->dict:
    audio,digest=source_verified_wav(root)
    destination=Path(destination)
    if destination.is_symlink() or destination.parent.is_symlink():
        raise VideoForgeError("REMAKE_EPISODE_AUDIO_SYMLINK_DESTINATION")
    output=destination/WAVE_NAME
    if output.is_symlink():
        raise VideoForgeError("REMAKE_EPISODE_AUDIO_SYMLINK_FILE")
    if output.exists():
        if not output.is_file() or hashlib.sha256(output.read_bytes()).hexdigest()!=digest:
            raise VideoForgeError("REMAKE_EPISODE_AUDIO_EXISTING_WAV_MISMATCH")
        created=False
    else:
        destination.mkdir(parents=True,exist_ok=True)
        output.write_bytes(audio)
        created=True
    return {
        "schema":SCHEMA,
        "shot":"C01-P01",
        "output":str(output),
        "audio_sha256":digest,
        "frames":FRAMES,
        "fps":30,
        "sample_rate":SAMPLE_RATE,
        "created":created,
        "qa_verification":"matches_SHA_and_PCM_of_original_opening",
        "render_full_episode_approved":False,
        "youtube_uploaded":False,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify-only",action="store_true")
    mode.add_argument("--prepare",action="store_true")
    ap.add_argument("--destination",type=Path,
                    default=ROOT/"motion-remotion/public/vf-remake/c01-p01")
    args=ap.parse_args()
    try:
        if args.verify_only:
            _,digest=source_verified_wav()
            print("REMAKE_EPISODE_ORIGINAL_AUDIO_VERIFIED",digest,
                  "no_file_written,no_video_rendered")
        else:
            print("REMAKE_EPISODE_ORIGINAL_AUDIO_STAGED",
                  json.dumps(prepare(args.destination),ensure_ascii=False))
        return 0
    except (OSError,ValueError,KeyError,VideoForgeError) as exc:
        print("REMAKE_EPISODE_AUDIO_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
