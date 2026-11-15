"""Generate and verify C01-P01: ORIGINAL synthesized sword SFX + black Remotion.

No image generation, reused music, proxy, fake rig, or YouTube upload.
FFmpeg is used ONLY for audiovisual QA of a Remotion-rendered MP4.
"""
from __future__ import annotations

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import wave

from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE

SAMPLE_RATE=48000
DURATION=2
FRAMES=60
EP_DIR=EPISODE/"assets"/"remake-v2"/"C01-P01"
WAVE_NAME="sword-original.wav"
VIDEO_NAME="black-opening-technical.mp4"
QA_NAME="black-opening.qa.json"
SCHEMA="videoforge/remake-black-opening/v1"
BEGIN="<!-- REMAKE-C01-P01-START -->"
END="<!-- REMAKE-C01-P01-END -->"


def original_sword_pcm() -> bytes:
    """Procedural metallic scrape/draw; generated from equations, not samples."""
    samples=array("h")
    seed=20261115
    for n in range(SAMPLE_RATE*DURATION):
        t=n/SAMPLE_RATE
        seed=(1664525*seed+1013904223)&0xffffffff
        noise=(seed/0xffffffff)*2-1
        # Scabbard contact starts in darkness: irregular steel friction.
        local=t-.16
        scrape=0.0
        if 0<=local<.92:
            env=min(1,local/.075)*min(1,(.92-local)/.17)
            chirp=math.sin(2*math.pi*(410*local+940*local*local))
            scrape=env*(.097*chirp+.065*noise
                        +.033*math.sin(2*math.pi*(1490*local+370*local*local)))
        # Blade clears sheath; an original bright metal impulse rings down.
        ring_t=t-.78
        ringing=0.0
        if ring_t>=0:
            env=(1-math.exp(-ring_t*95))*math.exp(-ring_t*3.9)
            ringing=env*(.29*math.sin(2*math.pi*1063*ring_t)
                         +.18*math.sin(2*math.pi*1607*ring_t)
                         +.11*math.sin(2*math.pi*2639*ring_t)
                         +.055*math.sin(2*math.pi*3449*ring_t))
        # Smoothly tame last samples to avoid terminal clicks.
        tail=min(1,(DURATION-t)/.09)
        signal=(scrape+ringing)*max(0,tail)
        samples.append(max(-32767,min(32767,round(signal*32767))))
    if sys.byteorder!="little":
        samples.byteswap()
    return samples.tobytes()


def _wav_bytes() -> bytes:
    from io import BytesIO
    memory=BytesIO()
    with wave.open(memory,"wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(original_sword_pcm())
    return memory.getvalue()


def _sha(binary:bytes)->str:
    return hashlib.sha256(binary).hexdigest()


def _write_consistent(path:Path,binary:bytes)->bool:
    if path.is_symlink():
        raise VideoForgeError("REMAKE_OPENING_SYMLINK_FORBIDDEN")
    if path.exists():
        if not path.is_file() or path.read_bytes()!=binary:
            raise VideoForgeError("REMAKE_OPENING_EXISTING_FILE_MISMATCH")
        return False
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(binary)
    return True


def prepare(output:Path,public:Path)->dict:
    source=_wav_bytes()
    with wave.open(__import__("io").BytesIO(source),"rb") as wav:
        if (wav.getframerate(),wav.getnchannels(),wav.getnframes(),wav.getsampwidth())!=(
            SAMPLE_RATE,1,SAMPLE_RATE*DURATION,2):
            raise VideoForgeError("REMAKE_OPENING_WAV_FORMAT_INVALID")
    output.mkdir(parents=True,exist_ok=True)
    public.mkdir(parents=True,exist_ok=True)
    _write_consistent(output/WAVE_NAME,source)
    _write_consistent(public/WAVE_NAME,source)
    raw=original_sword_pcm()
    values=array("h")
    values.frombytes(raw)
    if sys.byteorder!="little":values.byteswap()
    peak=max(abs(x) for x in values)/32768
    rms=math.sqrt(sum(x*x for x in values)/len(values))/32768
    if not (.025<rms<.42 and .08<peak<.95):
        raise VideoForgeError("REMAKE_OPENING_SOUND_INVALID_OR_CLIPPED")
    report={"schema":SCHEMA,"shot":"C01-P01","channel":"alchemy-lab",
      "video_id":"mmorpg-conquiste-a-princesa-ep01","audio_original_procedural":True,
      "file":WAVE_NAME,"sha256":_sha(source),"sample_rate":SAMPLE_RATE,
      "samples":len(values),"peak":round(peak,6),"rms":round(rms,6),
      "media_generated":True,"images_generated":0,"real_actor_rig_present":False,
      "official_video_approved":False,"youtube_uploaded":False}
    props={"schema":SCHEMA,"shotId":"C01-P01","audioSha256":_sha(source),
           "durationFrames":FRAMES,"renderOfficialApproved":False,"youtubeUploaded":False}
    _write_consistent(output/"audio.qa.json",(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())
    _write_consistent(output/"props.json",(json.dumps(props,ensure_ascii=False,indent=2)+"\n").encode())
    return report


def _command(*args:str,timeout:int=90)->bytes:
    try:
        p=subprocess.run(list(args),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=timeout,check=True)
    except (subprocess.CalledProcessError,OSError,subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("REMAKE_OPENING_MEDIA_QA_COMMAND_FAILED") from exc
    return p.stdout


def verify_mp4(output:Path)->dict:
    audio=output/WAVE_NAME
    video=output/VIDEO_NAME
    existing=output/"audio.qa.json"
    if any(x.is_symlink() or not x.is_file() for x in (audio,video,existing)):
        raise VideoForgeError("REMAKE_OPENING_REQUIRED_BYTES_MISSING")
    aud=json.loads(existing.read_text(encoding="utf-8"))
    if aud.get("schema")!=SCHEMA or aud.get("sha256")!=_sha(audio.read_bytes()):
        raise VideoForgeError("REMAKE_OPENING_AUDIO_HASH_MISMATCH")
    meta=json.loads(_command("ffprobe","-v","error","-count_frames",
        "-show_streams","-show_format","-of","json",str(video)))
    streams=meta.get("streams",[])
    picture=[s for s in streams if s.get("codec_type")=="video"]
    sounds=[s for s in streams if s.get("codec_type")=="audio"]
    if len(picture)!=1 or len(sounds)!=1:
        raise VideoForgeError("REMAKE_OPENING_AV_STREAMS_MISSING")
    pic=picture[0];sound=sounds[0]
    frame_count=int(pic.get("nb_read_frames") or pic.get("nb_frames") or -1)
    duration=float(meta.get("format",{}).get("duration",0))
    if (pic.get("codec_name")!="h264"
        or pic.get("width")!=1080 or pic.get("height")!=1920
        or pic.get("avg_frame_rate")!="30/1" or frame_count!=FRAMES
        or sound.get("codec_name")!="aac"
        or sound.get("sample_rate")!=str(SAMPLE_RATE)
        or not 1.98<=duration<=2.1):
        raise VideoForgeError("REMAKE_OPENING_MP4_PARAMETERS_INVALID")
    # Decoder sees 60 monochrome frames. This confirms no character/poster
    # was accidentally composited into a scene that must be BLACK.
    gray=_command("ffmpeg","-nostdin","-v","error","-i",str(video),
        "-map","0:v:0","-vf","scale=16:16,format=gray",
        "-f","rawvideo","-pix_fmt","gray","-an","pipe:1")
    if len(gray)!=FRAMES*16*16 or max(gray)>2:
        raise VideoForgeError("REMAKE_OPENING_NOT_FULLY_BLACK")
    rendered_sound=_command("ffmpeg","-nostdin","-v","error","-i",str(video),
        "-map","0:a:0","-ac","1","-ar",str(SAMPLE_RATE),
        "-f","s16le","pipe:1")
    values=array("h")
    values.frombytes(rendered_sound)
    if sys.byteorder!="little":values.byteswap()
    if not values or max(abs(v) for v in values)<150:
        raise VideoForgeError("REMAKE_OPENING_RENDERED_AUDIO_SILENT")
    return {"schema":"videoforge/remake-opening-technical-qa/v1","shot":"C01-P01",
      "technical_preview_only":True,"renderer":"remotion@4",
      "black_pixels_verified":True,"audio_original_sfx_verified":True,
      "frames":frame_count,"fps":30,"width":1080,"height":1920,
      "duration_seconds":duration,"video_codec":"h264","audio_codec":"aac",
      "audio_sha256":aud["sha256"],"mp4_sha256":_sha(video.read_bytes()),
      "human_visual_approved":False,"official_video_approved":False,
      "full_episode_rendered":False,"youtube_uploaded":False}


def audit_media(output:Path)->dict:
    """Run heavy FFprobe and decoded-frame QA ONLY in the Remotion container."""
    report=verify_mp4(output)
    binary=(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    _write_consistent(output/"black-opening.media.qa.json",binary)
    return report


def read_audited_qa(output:Path)->dict:
    """Host checks bytes and an in-artifact report already produced by FFmpeg QA.

    The GitHub Ubuntu host need not ship ffmpeg, only Git/Python stdlib.
    The report is created by the controlled render job in the SAME workflow.
    """
    report_file=output/"black-opening.media.qa.json"
    props_file=output/"props.json"
    audio_file=output/WAVE_NAME
    video_file=output/VIDEO_NAME
    audio_report=output/"audio.qa.json"
    if any(x.is_symlink() or not x.is_file() for x in
           (report_file,props_file,audio_file,video_file,audio_report)):
        raise VideoForgeError("REMAKE_OPENING_AUDITED_ARTIFACT_INCOMPLETE")
    try:
        report=json.loads(report_file.read_text(encoding="utf-8"))
        props=json.loads(props_file.read_text(encoding="utf-8"))
        sound_meta=json.loads(audio_report.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError) as exc:
        raise VideoForgeError("REMAKE_OPENING_AUDITED_ARTIFACT_JSON_INVALID") from exc
    if (report.get("schema")!="videoforge/remake-opening-technical-qa/v1"
            or report.get("shot")!="C01-P01" or report.get("renderer")!="remotion@4"
            or report.get("technical_preview_only") is not True
            or report.get("black_pixels_verified") is not True
            or report.get("audio_original_sfx_verified") is not True
            or report.get("frames")!=FRAMES or report.get("fps")!=30
            or report.get("width")!=1080 or report.get("height")!=1920
            or not 1.98<=report.get("duration_seconds",0)<=2.1
            or report.get("video_codec")!="h264" or report.get("audio_codec")!="aac"
            or report.get("official_video_approved") is not False
            or report.get("youtube_uploaded") is not False
            or report.get("human_visual_approved") is not False
            or report.get("full_episode_rendered") is not False
            or props.get("schema")!=SCHEMA or props.get("shotId")!="C01-P01"
            or props.get("durationFrames")!=FRAMES
            or props.get("renderOfficialApproved") is not False
            or props.get("youtubeUploaded") is not False
            or sound_meta.get("schema")!=SCHEMA
            or sound_meta.get("audio_original_procedural") is not True
            or sound_meta.get("sample_rate")!=SAMPLE_RATE):
        raise VideoForgeError("REMAKE_OPENING_AUDIT_CONTRACT_MISMATCH")
    raw_audio=audio_file.read_bytes()
    raw_video=video_file.read_bytes()
    if (raw_audio!=_wav_bytes()
            or props.get("audioSha256")!=_sha(raw_audio)
            or sound_meta.get("sha256")!=_sha(raw_audio)
            or report.get("audio_sha256")!=_sha(raw_audio)
            or report.get("mp4_sha256")!=_sha(raw_video)
            or len(raw_video)<2048):
        raise VideoForgeError("REMAKE_OPENING_ARTIFACT_BYTES_SHA_INVALID")
    return report


def persist(output:Path,repo_root:Path=ROOT)->dict:
    """Archive hashes/QA in git; keep binary media in GitHub Actions artifact.

    The repo explicitly ignores *.mp4, *.wav and canal/.../assets.
    Never bypass that policy with force-add or a fake repo asset path.
    """
    qa=read_audited_qa(output)
    episode=Path(repo_root)/EPISODE
    plan_file=episode/"remake-ep01-planos.json"
    state_file=episode/"estado-atual.json"
    history_file=episode/"HISTORICO-DESENVOLVIMENTO.md"
    checkpoint=episode/"ESTADO-ATUAL.md"
    plan=json.loads(plan_file.read_text(encoding="utf-8"))
    first=plan["shots"][0]
    if first["shot_id"]!="C01-P01" or first["frame_end_exclusive"]!=FRAMES:
        raise VideoForgeError("REMAKE_OPENING_TIMELINE_WRONG")
    import os
    run_id=os.environ.get("GITHUB_RUN_ID")
    if not run_id or not run_id.isdigit():
        raise VideoForgeError("REMAKE_OPENING_GITHUB_RUN_ID_REQUIRED")
    artifact="vf-remake-c01-p01-opening-"+run_id
    report_path=episode/"QA-C01-P01-REMAKE-V2.json"
    qa.update({
      "github_run_id":int(run_id),"artifact_name":artifact,
      "artifact_retention_days":90,
      "audio_file_in_repository":False,
      "mp4_file_in_repository":False,
      "archive_kind":"github_actions_artifact_not_git_binary",
      "sfx_filename":WAVE_NAME,"preview_filename":VIDEO_NAME,
    })
    if report_path.exists():
        existing=json.loads(report_path.read_text(encoding="utf-8"))
        if existing==qa: return qa
        raise VideoForgeError("REMAKE_OPENING_EXISTING_QA_VERSIONED_NO_OVERWRITE")
    first["original_audio_sha256"]=qa["audio_sha256"]
    first["technical_preview_sha256"]=qa["mp4_sha256"]
    first["technical_preview_qa_path"]="QA-C01-P01-REMAKE-V2.json"
    first["technical_preview_artifact"]=artifact
    first["asset_status"]="black_original_audio_preview_archived_in_actions"
    first["next_stage"]="review_original_sfx_and_protect_technical_artifact"
    first["mp4_created"]=True
    first["human_visual_approved"]=False
    first["publishable"]=False
    new={
      "status":"technical_preview_in_github_actions_only_not_full_episode",
      "run_id":int(run_id),"artifact_name":artifact,"retention_days":90,
      "audio_sha256":qa["audio_sha256"],
      "video_sha256":qa["mp4_sha256"],
      "qa":"QA-C01-P01-REMAKE-V2.json",
      "frames":FRAMES,"seconds":DURATION,"black_frames_verified":True,
      "original_sfx":True,"remotion_renderer":True,
      "media_in_repo":False,"human_visual_approved":False,
      "new_full_episode_mp4":False,"youtube_uploaded":False,
    }
    state=json.loads(state_file.read_text(encoding="utf-8"))
    if state.get("c01_p01_black_opening_v2") not in (None,new):
        raise VideoForgeError("REMAKE_OPENING_PREVIOUS_PROOF_REQUIRES_HUMAN_RECONCILIATION")
    state["c01_p01_black_opening_v2"]=new
    notice=(BEGIN+"\n### C01-P01 — abertura preta com SFX original (QA técnico)\n"
      f"- **MP4 técnico real:** artifact \`{artifact}\` do GitHub run \`{run_id}\`; "
      f"SHA256 \`{qa['mp4_sha256']}\`; 2 s, 60 quadros pretos "
      "1080×1920/30fps H264/AAC por Remotion.\n"
      f"- **Áudio original:** \`{WAVE_NAME}\`, SHA256 \`{qa['audio_sha256']}\`; "
      "efeito procedural inédito, QA de áudio e preto passou.\n"
      "- **Armazenamento:** MP4/WAV no artifact de GitHub Actions por 90 dias; "
      "o repositório ignora *.mp4, *.wav e assets/ para evitar mídia versionada. "
      "QA e hashes persistidos em \`QA-C01-P01-REMAKE-V2.json\`.\n"
      "- **Limites:** não é o episódio completo, não há rig de personagem, "
      "imagem nova, aprovação humana, gasto de API ou YouTube. "
      "Próxima tomada: C01-P02 depende da âncora V2 aprovada.\n"+END)
    current=checkpoint.read_text(encoding="utf-8")
    if (BEGIN in current)!=(END in current):
        raise VideoForgeError("REMAKE_OPENING_CHECKPOINT_MARKERS_INVALID")
    if BEGIN in current:
        a=current.index(BEGIN);b=current.index(END,a)+len(END)
        current=current[:a]+notice+current[b:]
    else:
        current=current.replace("\n","\n\n"+notice+"\n\n",1)
    stamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    plan_file.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    state_file.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    checkpoint.write_text(current,encoding="utf-8")
    with history_file.open("a",encoding="utf-8") as h:
        h.write(f"\n## {stamp} — C01-P01 Remotion 60 frames pretos + SFX próprio\n\n"
                f"- GitHub Actions run \`{run_id}\`, artifact \`{artifact}\` (90 dias); "
                f"MP4 SHA \`{qa['mp4_sha256']}\`, áudio SHA \`{qa['audio_sha256']}\`.\n"
                "- Render Remotion real de 2 segundos somente; QA salvo no repositório, "
                "mídia guardada em artifact, sem aprovação humana ou upload YouTube. "
                "Próximo: âncora V2 e C01-P02.\n")
    return qa


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["prepare","audit","checkpoint"])
    ap.add_argument("--output-dir",required=True,type=Path)
    ap.add_argument("--public-dir",type=Path)
    args=ap.parse_args()
    if args.action=="prepare":
        if args.public_dir is None: raise VideoForgeError("REMAKE_OPENING_PUBLIC_DIR_REQUIRED")
        print("REMAKE_OPENING_AUDIO",json.dumps(prepare(args.output_dir,args.public_dir),ensure_ascii=False))
    elif args.action=="audit":
        print("REMAKE_OPENING_MEDIA_AUDITED",json.dumps(audit_media(args.output_dir),ensure_ascii=False))
    else:
        print("REMAKE_OPENING_CHECKPOINT",json.dumps(persist(args.output_dir),ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
