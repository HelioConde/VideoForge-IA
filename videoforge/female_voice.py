"""Narração FEMININA pt-BR e legendas por trechos de fala, no VideoForge-IA.

Usa espeak-ng pt-br+f3 que já está no runner GHCR, sem API paga,
clonagem de voz ou restrições de licença de modelo neural.
Os tempos das legendas vêm da DURAÇÃO REAL de cada fragmento narrado.
O resultado é uma voz feminina SINTÉTICA; não chamar de voz neural natural.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import wave

from . import mvp, production_art
from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
VOICE="pt-br+f3"
SPEED=155


def _run(args:list[str],timeout:int=120)->None:
    try:
        p=subprocess.run(args,capture_output=True,timeout=timeout,check=False)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("FEMALE_VOICE_COMMAND_UNAVAILABLE") from exc
    if p.returncode:
        raise VideoForgeError("FEMALE_VOICE_COMMAND_FAILED")


def phrases(text:str, max_words:int=9)->list[str]:
    """Keep punctuation and naturally sized narration fragments."""
    if not isinstance(text,str) or not text.strip() or not 2<=max_words<=16:
        raise VideoForgeError("FEMALE_VOICE_TEXT_INVALID")
    words=text.split()
    groups=[]
    queue=[]
    for word in words:
        queue.append(word)
        if len(queue)>=max_words or (len(queue)>=4 and word[-1:] in (",",".","!","?",";",":")):
            groups.append(" ".join(queue))
            queue=[]
    if queue:
        groups.append(" ".join(queue))
    if not groups or " ".join(groups)!=" ".join(words):
        raise VideoForgeError("FEMALE_VOICE_PHRASE_SPLIT_INVALID")
    return groups


def stamp(seconds:float)->str:
    millis=round(seconds*1000)
    h,remaining=divmod(millis,3600_000)
    m,remaining=divmod(remaining,60_000)
    s,ms=divmod(remaining,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def synthesize_scene(text:str,index:int,audio:Path,subtitle:Path,
                     *,min_seconds:float)->dict:
    if not shutil.which("espeak-ng") or not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise VideoForgeError("FEMALE_VOICE_RUNTIME_MISSING")
    if audio.exists() or subtitle.exists() or audio.is_symlink() or subtitle.is_symlink():
        raise VideoForgeError("FEMALE_VOICE_ASSET_ALREADY_EXISTS")
    if not 0 < min_seconds < 40:
        raise VideoForgeError("FEMALE_VOICE_MIN_DURATION_INVALID")
    audio.parent.mkdir(parents=True,exist_ok=True)
    subtitle.parent.mkdir(parents=True,exist_ok=True)
    cues=[]
    chunks=phrases(text)
    with tempfile.TemporaryDirectory(prefix="vf-female-voice-") as temp:
        root=Path(temp)
        pcm=b""
        sample=None
        rate=None
        channel_count=None
        frames_so_far=0
        for n,line in enumerate(chunks,1):
            fragment=root/f"piece-{n:04d}.wav"
            # Fala sintetizada feminina: text é argumento, não shell.
            _run(["espeak-ng","-v",VOICE,"-s",str(SPEED),"-a","185",
                  "-p","45","-w",str(fragment),line])
            with wave.open(str(fragment),"rb") as wav:
                fmt=(wav.getnchannels(),wav.getsampwidth(),
                     wav.getframerate(),wav.getcomptype())
                if fmt[1]!=2 or fmt[3]!="NONE" or fmt[0]!=1:
                    raise VideoForgeError("FEMALE_VOICE_PCM_INVALID")
                if sample is None:
                    sample=fmt
                    rate=fmt[2]
                    channel_count=fmt[0]
                if sample!=fmt:
                    raise VideoForgeError("FEMALE_VOICE_PCM_MISMATCH")
                frames=wav.getnframes()
                if frames<=0:
                    raise VideoForgeError("FEMALE_VOICE_EMPTY_SEGMENT")
                raw=wav.readframes(frames)
            begin=frames_so_far/rate
            pcm+=raw
            frames_so_far+=frames
            end=frames_so_far/rate
            cues.append((begin,end,line))
            # Short deliberate silent break for readable subtitle transitions.
            pause=round(rate*0.10)
            pcm+=b"\x00"*(pause*2)
            frames_so_far+=pause
        if not cues or not rate:
            raise VideoForgeError("FEMALE_VOICE_EMPTY_NARRATION")
        raw_path=root/"joined.wav"
        with wave.open(str(raw_path),"wb") as out:
            out.setnchannels(channel_count)
            out.setsampwidth(2)
            out.setframerate(rate)
            out.writeframes(pcm)
        # Prevent shorter-than-Short output; otherwise preserve voice timing.
        _run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
              "-i",str(raw_path),"-af",
              f"apad=whole_dur={min_seconds:.3f},loudnorm=I=-16:TP=-1.5:LRA=11",
              "-ar","48000","-ac","2","-c:a","pcm_s16le",str(audio)],180)
    total=mvp._duration(mvp._media_info(audio))
    if cues[-1][1]>total+0.1:
        raise VideoForgeError("FEMALE_VOICE_SUBTITLE_TIME_EXCEEDS_AUDIO")
    subtitle.write_text("\n\n".join(
        f"{i}\n{stamp(start)} --> {stamp(end)}\n{line}"
        for i,(start,end,line) in enumerate(cues,1))+"\n",
        encoding="utf-8")
    return {"scene":index,"audio":audio.name,"audio_sha256":hashlib.sha256(audio.read_bytes()).hexdigest(),
            "subtitles":subtitle.name,"subtitle_sha256":hashlib.sha256(subtitle.read_bytes()).hexdigest(),
            "segments":len(cues),"duration_seconds":round(total,3),
            "spoken_text":" ".join(x[2] for x in cues)}


def produce(channel:str,video_id:str)->dict:
    plan,story=production_art.read_plan(channel,video_id)
    scenes=story["scenes"]
    directory=ROOT/"output"/channel/"videos"/video_id/"female-voice-stage"
    if directory.exists() or directory.is_symlink():
        raise VideoForgeError("FEMALE_VOICE_STAGE_ALREADY_EXISTS")
    voice_dir=directory/"audio"
    subs_dir=directory/"subtitles"
    rows=[]
    floor=mvp.MIN_SECONDS/len(scenes)
    for i,scene in enumerate(scenes,1):
        if scene.get("number")!=i or not isinstance(scene.get("narration"),str):
            raise VideoForgeError("FEMALE_VOICE_STORYBOARD_INVALID")
        result=synthesize_scene(scene["narration"],i,
                               voice_dir/f"cena-{i:02d}.wav",
                               subs_dir/f"cena-{i:02d}.srt",
                               min_seconds=floor)
        result["scene"]=scene["id"]
        rows.append(result)
        print(f"VOICE_FEMALE_SCENE_OK {i}/{len(scenes)}",flush=True)
    duration=sum(x["duration_seconds"] for x in rows)
    if not mvp.MIN_SECONDS<=duration<=mvp.MAX_SECONDS:
        raise VideoForgeError(f"FEMALE_VOICE_TOTAL_DURATION_INVALID_{duration:.1f}")
    result={"schema":"videoforge/female-voice-stage/v1",
            "channel":channel,"video_id":video_id,"scene_count":len(rows),
            "voice":VOICE,"voice_gender":"feminine_variant",
            "voice_quality":"synthetic_espeak_ng_not_neural",
            "language":"pt-BR",
            "subtitle_timing":"speech_fragment_boundaries_actual_wav_duration",
            "audio":rows,"duration_seconds":round(duration,3),
            "youtube_uploaded":False,"human_audio_approval":False}
    (directory/"audio-stage.qa.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    args=p.parse_args()
    try:
        result=produce(args.channel,args.video_id)
        print("VOICE_FEMALE_DONE",json.dumps(
            {k:v for k,v in result.items() if k!="audio"},ensure_ascii=False))
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError) as exc:
        print("VOICE_FEMALE_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
