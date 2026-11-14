"""Spy Family — animacao vertical de personagem por camadas (preview vetorial).

Preparacao de voz no runner com espeak-ng; render exclusivamente no Remotion
GHCR pre-compilado; QA de video/audio/movimento sem publicar no YouTube.
Nao afirma arte final licenciada ou aprovacao visual humana.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

from . import mvp, spy_family_pilot as pilot
from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
VIDEO_ID=pilot.VIDEO_ID
CHANNEL="otaku-br"
BASE=ROOT/"output"/CHANNEL/"videos"/VIDEO_ID/"animated-preview"
STAGE=BASE/"stage"
SOUND_DIR=STAGE/"audio"
FPS=30


def _sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(*args:str)->None:
    try:
        process=subprocess.run(args,check=False,capture_output=True,timeout=600)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("SPY_ANIMATED_MEDIA_TOOL_FAILED") from exc
    if process.returncode:
        raise VideoForgeError("SPY_ANIMATED_MEDIA_COMMAND_FAILED")


def props_from_storyboard(story:dict,durations:list[float])->dict:
    scenes=story["scenes"]
    if len(scenes)!=len(durations) or not scenes:
        raise VideoForgeError("SPY_ANIMATED_DURATION_MISMATCH")
    items=[]
    for scene,seconds in zip(scenes,durations):
        if not 0 < seconds < 300 or not math.isfinite(seconds):
            raise VideoForgeError("SPY_ANIMATED_DURATION_INVALID")
        id=scene["id"]
        if any(x in id for x in ("..","/","\\")):
            raise VideoForgeError("SPY_ANIMATED_SCENE_ID_INVALID")
        if id in ("academia-eden","damian","adocao-anya"):
            setting="academy"
        elif id in ("operacao-strix","identidade-loid"):
            setting="office"
        else:
            setting="home"
        if "yor" in id:
            focus="yor"
        elif any(key in id for key in ("loid","operacao","academia","damian")):
            focus="loid"
        elif any(key in id for key in ("anya","telepatia","poder","adocao","escolha")):
            focus="anya"
        else:
            focus="family"
        items.append({
            "id":id,"card":scene["card"],"focus":focus,
            "setting":setting,"durationFrames":math.ceil(seconds*FPS),
            "audio":f"vf-spy/cena-{scene['number']:02d}.wav",
        })
    return {"channel":CHANNEL,"videoId":VIDEO_ID,
            "scenes":items,"totalFrames":sum(s["durationFrames"] for s in items),
            "draftPreview":True}


def prepare()->dict:
    story=pilot.load_storyboard()
    if not shutil.which("espeak-ng") or not shutil.which("ffprobe"):
        raise VideoForgeError("SPY_ANIMATED_VOICE_RUNTIME_MISSING")
    if STAGE.exists():
        raise VideoForgeError("SPY_ANIMATED_STAGE_EXISTS")
    SOUND_DIR.mkdir(parents=True)
    pilot_voice=pilot.FOLDER/"voz"
    pilot_voice.mkdir(exist_ok=True)
    durations=[]
    manifest=[]
    minimum=mvp.MIN_SECONDS/len(story["scenes"])
    for i,scene in enumerate(story["scenes"],1):
        vocal=pilot_voice/f"cena-{i:02d}.wav"
        if vocal.exists() or vocal.is_symlink():
            raise VideoForgeError("SPY_ANIMATED_VOICE_ALREADY_EXISTS")
        pilot.synthesize_ptbr(i,scene["narration"],vocal,
                               min_duration=minimum,speed=172)
        target=SOUND_DIR/vocal.name
        shutil.move(str(vocal),str(target))
        seconds=mvp._duration(mvp._media_info(target))
        durations.append(seconds)
        manifest.append({"scene":scene["id"],"audio":target.name,
                         "duration":round(seconds,4),"sha256":_sha(target)})
        print(f"SCENE {i}/{len(story['scenes'])}: audio gerado",flush=True)
    props=props_from_storyboard(story,durations)
    full=props["totalFrames"]/FPS
    if not mvp.MIN_SECONDS<=full<=mvp.MAX_SECONDS:
        raise VideoForgeError(f"SPY_ANIMATED_TOTAL_DURATION_OUT_OF_RANGE_{round(full,1)}s")
    (STAGE/"episode-props.json").write_text(
        json.dumps(props,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    qa={"schema":"videoforge/spy-family-animated-stage/v1",
        "channel":CHANNEL,"video_id":VIDEO_ID,"scenes":len(manifest),
        "duration_seconds":round(full,3),"storyboard_sha256":_sha(pilot.STORYBOARD),
        "audio":manifest,"rendered":False,"youtube_uploaded":False}
    (STAGE/"audio-stage.qa.json").write_text(
        json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return qa


def verify()->dict:
    propsfile=STAGE/"episode-props.json"
    if not propsfile.is_file():
        raise VideoForgeError("SPY_ANIMATED_PROPS_MISSING")
    props=json.loads(propsfile.read_text(encoding="utf-8"))
    video=BASE/"video.mp4"
    if not video.is_file() or video.stat().st_size<100_000:
        raise VideoForgeError("SPY_ANIMATED_VIDEO_MISSING")
    frames=props["totalFrames"]
    expected=frames/FPS
    qa=mvp._verify_mp4(video,expected=expected,minimum=90,maximum=180)
    samples=[]
    for t in (0.65,1.55,3.10):
        shot=BASE/f"motion-{int(t*100):03d}.png"
        _run("ffmpeg","-hide_banner","-nostdin","-loglevel","error",
             "-y","-ss",str(t),"-i",str(video),"-frames:v","1",str(shot))
        samples.append(_sha(shot))
    if len(set(samples))<2:
        raise VideoForgeError("SPY_ANIMATED_NO_VISIBLE_MOTION")
    result={
        "schema":"videoforge/spy-family-animated-qa/v1",
        "channel":CHANNEL,"video_id":VIDEO_ID,"scene_count":len(props["scenes"]),
        "status":"technical_verified","duration_seconds":qa["duration_seconds"],
        "resolution":"1080x1920","video_codec":"h264","audio_codec":"aac",
        "sha256":qa["sha256"],"frame_samples_changed":True,
        "animation_engine":"Remotion 4 SVG deterministic layered character rig",
        "rig_features":["opaque-head","blink-over-solid-face",
                        "layered-body-clothing","seam-underlay",
                        "pinned-shoulder-wind","hair-root-overlap",
                        "cinematic-motion","per-scene-audio"],
        "art_status":"procedural_vector_preview_not_final_character_art",
        "voice_status":"offline_synthetic_preview_not_final_narration",
        "visual_review":"pending_human_approval","publishable":False,
        "youtube_uploaded":False,"generative_image_calls":0,
        "storyboard_sha256":_sha(pilot.STORYBOARD)
    }
    (BASE/"animated-video.qa.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main()->int:
    arg=argparse.ArgumentParser(description="Spy x Family layered-animated draft only")
    arg.add_argument("command",choices=("prepare","verify"))
    args=arg.parse_args()
    try:
        result=prepare() if args.command=="prepare" else verify()
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (VideoForgeError,ValueError,OSError,KeyError,TypeError) as exc:
        print("SPY_ANIMATED_BLOCKED",str(exc))
        return 1

if __name__=="__main__":
    raise SystemExit(main())
