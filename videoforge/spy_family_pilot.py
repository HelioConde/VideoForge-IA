"""Piloto vertical editorial de Spy x Family.

Objetivo: testar a montagem de um Short completo do roteiro legado,
com voz sintetizada offline e storyboard GRAFICO (sem arte de personagens).
Nao representa uma animacao/voz final, nem chama IA ou publica YouTube.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from . import mvp
from .errors import VideoForgeError

ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID = "spy-x-family-familia-de-mentira"
FOLDER = ROOT / "canal" / "otaku-br" / "videos" / VIDEO_ID
STORYBOARD = FOLDER / "roteiro.json"
MANIFEST = FOLDER / "video.json"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MIN_SCENE_SECONDS = 10.0


def load_storyboard() -> dict:
    data = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    if (data.get("schema") != "videoforge/spy-family-pilot/v1"
            or data.get("channel") != "otaku-br"
            or data.get("video_id") != VIDEO_ID
            or data.get("youtube_upload") is not False
            or data.get("mode") != "technical_animatic_previsualization"):
        raise VideoForgeError("SPY_PILOT_WRONG_PROJECT_OR_SCHEMA")
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or len(scenes) != 10:
        raise VideoForgeError("SPY_PILOT_SCENE_COUNT")
    if not all(isinstance(scene, dict) and
               scene.get("number") == index and
               isinstance(scene.get("narration"), str) and
               30 <= len(scene["narration"]) <= 450 and
               isinstance(scene.get("card"), str) and
               5 <= len(scene["card"]) <= 60
               for index, scene in enumerate(scenes, 1)):
        raise VideoForgeError("SPY_PILOT_STORYBOARD_INVALID")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (manifest.get("schema") != "videoforge/mvp/v1"
            or manifest.get("channel") != "otaku-br"
            or manifest.get("youtube_upload") is not False
            or len(manifest.get("scenes", [])) != len(scenes)):
        raise VideoForgeError("SPY_PILOT_MANIFEST_INVALID")
    for source, target in zip(scenes, manifest["scenes"]):
        if any(source[field] != target[field]
               for field in ("image", "audio", "caption")):
            raise VideoForgeError("SPY_PILOT_MANIFEST_SCENE_MISMATCH")
    return data


def run(*args: str, timeout: int = 100) -> None:
    try:
        result = subprocess.run(
            list(args), cwd=FOLDER, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("SPY_PILOT_TOOL_UNAVAILABLE") from exc
    if result.returncode:
        raise VideoForgeError("SPY_PILOT_MEDIA_COMMAND_FAILED")


def write_once(path: Path, text: str) -> str:
    if path.exists() or path.is_symlink():
        raise VideoForgeError("SPY_PILOT_WOULD_OVERWRITE_ASSET")
    path.write_text(text, encoding="utf-8")
    return path.name


def draw_card(number: int, scene: dict, output: Path) -> None:
    """Tipografia propria: nenhum frame/arte/OST de terceiros."""
    from textwrap import fill
    tmp = FOLDER / "_preview_text"
    tmp.mkdir(exist_ok=True)
    card = write_once(tmp / f"titulo-{number:02d}.txt",
                      fill(scene["card"], width=18))
    number_file = write_once(tmp / f"numero-{number:02d}.txt",
                             f"CENA {number:02d} / 10")
    title_file = write_once(tmp / f"serie-{number:02d}.txt", "SPY x FAMILY")
    warning_file = write_once(tmp / f"aviso-{number:02d}.txt",
                              "ANIMATICO TECNICO - NAO PUBLICAR")
    # Textfile paths relative to FOLDER (same cwd as FFmpeg).
    def t(file: str, y: int, size: int, color: str = "white") -> str:
        return ("drawtext=fontfile=" + FONT + ":textfile=_preview_text/" + file
                + f":fontsize={size}:fontcolor={color}:line_spacing=12:"
                + f"x=(w-text_w)/2:y={y}")
    focus = scene["id"]
    names = [("LOID", "0x75b9a2", 115),
             ("YOR", "0xef8581", 250),
             ("ANYA", "0xf5b3cf", 385)]
    filters = [
        "drawbox=x=0:y=0:w=540:h=960:color=0x0c1a31:t=fill",
        "drawbox=x=0:y=50:w=540:h=11:color=0xe8b56c:t=fill",
        "drawbox=x=50:y=206:w=440:h=240:color=0x132847:t=fill",
        "drawbox=x=0:y=740:w=540:h=15:color=0xe8b56c:t=fill",
        t(title_file, 88, 46, "0xfce3a9"),
        t(number_file, 177, 22, "0xc5d3e7"),
    ]
    # Tres placas de cor coerentes como MARCADORES EDITORIAIS, nunca
    # retratos finais ou tentativa de imitar personagens licenciados.
    for name, color, x in names:
        selected = focus.lower() == name.lower()
        filters.append(f"drawbox=x={x}:y={275 if selected else 289}:"
                       f"w=44:h={90 if selected else 63}:color={color}:t=fill")
    filters += [
        t(card, 489, 34),
        t(warning_file, 862, 16, "0xf2b4b4"),
    ]
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=0x0c1a31:s=540x960:r=1:d=1",
        "-vf", ",".join(filters), "-frames:v", "1", "-threads", "1",
        str(output.relative_to(FOLDER)), timeout=40)


def synthesize_ptbr(number: int, narration: str, output: Path) -> None:
    if not shutil.which("espeak-ng"):
        raise VideoForgeError("SPY_PILOT_ESPEAK_NOT_PREBUILT")
    raw = output.with_name(f"raw-voz-{number:02d}.wav")
    run("espeak-ng", "-v", "pt-br", "-s", "142", "-a", "170",
        "-p", "47", "-w", str(raw.relative_to(FOLDER)), narration)
    # Pequena pausa de leitura: audio curto não gera cena sub-90 segundos.
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(raw.relative_to(FOLDER)), "-af",
        f"apad=whole_dur={MIN_SCENE_SECONDS:.1f}",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(output.relative_to(FOLDER)), timeout=60)
    raw.unlink()


def main() -> int:
    try:
        storyboard = load_storyboard()
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise VideoForgeError("SPY_PILOT_FFMPEG_MISSING")
        (FOLDER / "imagens").mkdir(exist_ok=True)
        (FOLDER / "voz").mkdir(exist_ok=True)
        for i, scene in enumerate(storyboard["scenes"], 1):
            visual = FOLDER / scene["image"]
            voice = FOLDER / scene["audio"]
            if visual.exists() or voice.exists():
                raise VideoForgeError("SPY_PILOT_ASSET_ALREADY_EXISTS")
            draw_card(i, scene, visual)
            synthesize_ptbr(i, scene["narration"], voice)
        report = mvp.render(MANIFEST)
        qa = {
            "schema": "videoforge/spy-family-pilot-qa/v1",
            "video_id": VIDEO_ID, "channel": "otaku-br",
            "technical_mp4_verified": report["status"] == "technical_verified",
            "duration_seconds": report["duration_seconds"],
            "sha256": report["sha256"],
            "actual_art": False, "actual_character_animation": False,
            "voice_quality": "offline_synthetic_robotic_preview",
            "visual_review": "pending",
            "editorial_review": "pending",
            "publishable": False, "youtube_uploaded": False,
            "external_ai_calls": 0,
            "source": storyboard["source"],
        }
        dst = ROOT / "output" / "otaku-br" / "videos" / VIDEO_ID
        (dst / "pilot.qa.json").write_text(
            json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(json.dumps(qa, ensure_ascii=False))
        return 0
    except (VideoForgeError, ValueError, OSError, KeyError) as exc:
        print("SPY_PILOT_BLOCKED:", str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
