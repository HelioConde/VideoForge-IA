"""VideoForge MVP: assemble genuine supplied images and narration into a review MP4.

No AI keys, no automatic image synthesis in production, no YouTube uploader.
The 'smoke' command creates unmistakably synthetic media solely to exercise
the same render path and technical QA in CI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

from .errors import VideoForgeError
from .paths import resolve_video_context

VIDEO_SIZE = (1080, 1920)
FPS = 24
MIN_SECONDS = 90
MAX_SECONDS = 180
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac"}


def _command(args: list[str], *, cwd: Path | None = None, timeout: int = 900) -> str:
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("MEDIA_COMMAND_UNAVAILABLE_OR_TIMEOUT") from exc
    if result.returncode != 0:
        # Never echo subprocess output; FFmpeg could disclose local media paths.
        raise VideoForgeError("MEDIA_COMMAND_FAILED")
    return result.stdout


def _require_tools() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise VideoForgeError("FFMPEG_AND_FFPROBE_REQUIRED")


def _media_info(path: Path) -> dict:
    raw = _command([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ], timeout=30)
    try:
        info = json.loads(raw)
        duration = float(info["format"]["duration"])
        if not 0 < duration < 3600:
            raise ValueError()
        return info
    except (KeyError, ValueError, TypeError) as exc:
        raise VideoForgeError("MEDIA_PROBE_INVALID") from exc


def _duration(info: dict) -> float:
    return float(info["format"]["duration"])


def _safe_asset(directory: Path, name: object, allowed: set[str]) -> Path:
    if not isinstance(name, str) or not name or len(name) > 180:
        raise VideoForgeError("ASSET_PATH_INVALID")
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or relative.suffix.lower() not in allowed:
        raise VideoForgeError("ASSET_PATH_INVALID")
    candidate = directory / relative
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(directory.resolve()):
        raise VideoForgeError("ASSET_OUTSIDE_PROJECT")
    if not candidate.is_file() or candidate.stat().st_size > 100_000_000:
        raise VideoForgeError("ASSET_MISSING_OR_TOO_LARGE")
    return candidate.resolve()


def _load_manifest(path: Path) -> tuple[dict, list[dict]]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 200_000:
        raise VideoForgeError("MANIFEST_MISSING_OR_UNSAFE")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise VideoForgeError("MANIFEST_JSON_INVALID") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != "videoforge/mvp/v1":
        raise VideoForgeError("MANIFEST_SCHEMA_INVALID")
    if manifest.get("channel") != "otaku-br":
        raise VideoForgeError("MVP_CHANNEL_NOT_SUPPORTED")
    if manifest.get("youtube_upload") is not False:
        raise VideoForgeError("YOUTUBE_UPLOAD_MUST_BE_DISABLED")
    scenes = manifest.get("scenes")
    # Nenhum teto artificial de quantidade de cenas: a narrativa determina os cortes.
    # Conservamos apenas ao menos uma cena; duracao/QA/seguranca seguem ativas.
    if not isinstance(scenes, list) or not scenes:
        raise VideoForgeError("SCENE_COUNT_INVALID")
    resolved = []
    for scene in scenes:
        if not isinstance(scene, dict):
            raise VideoForgeError("SCENE_INVALID")
        caption = scene.get("caption")
        if (not isinstance(caption, str) or not 1 <= len(caption.strip()) <= 180
                or any(ord(char) < 32 and char != "\n" for char in caption)):
            raise VideoForgeError("SCENE_CAPTION_INVALID")
        image = _safe_asset(path.parent, scene.get("image"), IMAGE_EXTENSIONS)
        audio = _safe_asset(path.parent, scene.get("audio"), AUDIO_EXTENSIONS)
        motion = scene.get("motion", "none")
        if motion not in ("none", "cinematic-pan"):
            raise VideoForgeError("SCENE_MOTION_INVALID")
        subtitle = scene.get("subtitles")
        if subtitle is not None:
            subtitle = _safe_asset(path.parent, subtitle, {".srt"})
            if subtitle.stat().st_size > 20_000:
                raise VideoForgeError("SCENE_SUBTITLES_TOO_LARGE")
        resolved.append({"image": image, "audio": audio, "caption": caption.strip(),
                         "motion": motion, "subtitles": subtitle})
    return manifest, resolved


def _drawtext_filter(caption_filename: str, *,
                     subtitle_filename: str | None = None,
                     motion: str = "none") -> str:
    """Preserve whole reference artwork; optional cinematic pan and real subtitles.

    Pan moves the FULL image ~8px over its blurred extension. This is camera
    motion, not articulated movement of faces/arms. No misleading rig claims.
    """
    fg_scale = ("scale=1024:1536:force_original_aspect_ratio=decrease"
                if motion == "cinematic-pan" else
                "scale=1080:1920:force_original_aspect_ratio=decrease")
    placement = ("overlay=x='(W-w)/2+8*sin(t*0.45)':"
                 "y='(H-h)/2+6*sin(t*0.27)':eval=frame"
                 if motion == "cinematic-pan" else
                 "overlay=(W-w)/2:(H-h)/2")
    chain = (
        "split=2[back_source][original_source];"
        "[back_source]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=28:2[soft_background];"
        "[original_source]" + fg_scale + "[original];"
        "[soft_background][original]" + placement + ","
    )
    if subtitle_filename:
        # Input path is a sanitized staging basename, not untrusted text.
        # Subtitles are short phrases, not fixed cards unrelated to narration.
        chain += (
            "subtitles=filename=" + subtitle_filename +
            ":force_style='FontName=DejaVu Sans,FontSize=11,"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H65000000,"
            "BorderStyle=3,BackColour=&H90000000,"
            "Alignment=2,MarginV=12',"
        )
    else:
        chain += (
            "drawtext=font=Sans:textfile=" + caption_filename +
            ":fontsize=44:fontcolor=white:line_spacing=12:"
            "box=1:boxcolor=black@0.68:boxborderw=18:"
            "x=(w-text_w)/2:y=h-350,"
        )
    return chain + "format=yuv420p"


def _render_scene(scene: dict, output: Path, *, workspace: Path, index: int) -> None:
    caption = workspace / ("caption-%03d.txt" % index)
    caption.write_text(textwrap.fill(scene["caption"], width=30), encoding="utf-8")
    subtitle_name = None
    if scene.get("subtitles") is not None:
        subtitle_name = "subtitle-%03d.srt" % index
        shutil.copyfile(scene["subtitles"], workspace / subtitle_name)
    _command([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-framerate", str(FPS), "-i", str(scene["image"]),
        "-i", str(scene["audio"]),
        "-vf", _drawtext_filter(
            caption.name, subtitle_filename=subtitle_name,
            motion=scene.get("motion", "none")),
        "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2",
        "-shortest", "-movflags", "+faststart", str(output),
    ], cwd=workspace)



def _verify_mp4(path: Path, *, expected: float, minimum: float, maximum: float) -> dict:
    info = _media_info(path)
    video = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    audio = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    duration = _duration(info)
    if (len(video) != 1 or not audio or video[0].get("codec_name") != "h264"
            or audio[0].get("codec_name") != "aac"
            or (video[0].get("width"), video[0].get("height")) != VIDEO_SIZE
            or not minimum <= duration <= maximum + 1.0
            or abs(expected - duration) > 3.0):
        raise VideoForgeError("MP4_QA_FAILED")
    return {
        "status": "technical_verified",
        "duration_seconds": round(duration, 3),
        "width": VIDEO_SIZE[0], "height": VIDEO_SIZE[1],
        "video_codec": "h264", "audio_codec": "aac",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "youtube_uploaded": False,
        "visual_quality_human_approved": False,
    }


def _compose(scenes: list[dict], output: Path, *, minimum: float, maximum: float,
             kind: str) -> dict:
    _require_tools()
    if output.exists():
        raise VideoForgeError("OUTPUT_ALREADY_EXISTS")
    # A quantidade e livre; o total de duracao do formato segue validado abaixo.
    if not scenes:
        raise VideoForgeError("SCENE_COUNT_INVALID")
    expected = 0.0
    for scene in scenes:
        sound = _media_info(scene["audio"])
        if not any(s.get("codec_type") == "audio" for s in sound.get("streams", [])):
            raise VideoForgeError("AUDIO_TRACK_MISSING")
        expected += _duration(sound)
    if not minimum <= expected <= maximum:
        raise VideoForgeError("TOTAL_DURATION_OUT_OF_RANGE")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="videoforge-") as folder:
        staging = Path(folder)
        concat_lines = []
        for number, scene in enumerate(scenes, 1):
            name = "scene-%03d.mp4" % number
            _render_scene(scene, staging / name, workspace=staging, index=number)
            concat_lines.append("file '%s'" % name)
        (staging / "clips.txt").write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
        temporary_output = staging / "combined.mp4"
        _command([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", "clips.txt",
            "-c", "copy", "-movflags", "+faststart", str(temporary_output),
        ], cwd=staging)
        qa = _verify_mp4(temporary_output, expected=expected,
                         minimum=minimum, maximum=maximum)
        shutil.copy2(temporary_output, output)
    qa["kind"] = kind
    qa["scenes"] = len(scenes)
    report_path = output.with_suffix(".qa.json")
    if report_path.exists():
        output.unlink(missing_ok=True)
        raise VideoForgeError("QA_REPORT_ALREADY_EXISTS")
    report_path.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    return qa


def render(manifest_path: Path, output: Path | None = None) -> dict:
    # Fail closed on channel identity, model and output location before FFmpeg.
    manifest, scenes = _load_manifest(manifest_path)
    context = resolve_video_context(
        manifest_path, manifest, requested_output=output
    )
    return _compose(scenes, context.output, minimum=MIN_SECONDS,
                    maximum=MAX_SECONDS, kind="real_supplied_media")


def smoke(output: Path) -> dict:
    """Create synthetic CI media, never to be represented as a channel video."""
    _require_tools()
    with tempfile.TemporaryDirectory(prefix="vf-fixture-") as folder:
        stage = Path(folder)
        scenes = []
        for index, (color, freq) in enumerate(
            (("navy", 320), ("darkred", 440), ("darkgreen", 560)), 1
        ):
            image, audio = stage / f"fixture-{index}.png", stage / f"fixture-{index}.wav"
            _command([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", f"color=c={color}:s=360x640",
                "-frames:v", "1", "-threads", "1", str(image),
            ])
            _command([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", f"sine=frequency={freq}:duration=1.8",
                "-c:a", "pcm_s16le", str(audio),
            ])
            scenes.append({
                "image": image, "audio": audio,
                "caption": f"TESTE TECNICO {index} - NAO PUBLICAR",
            })
        return _compose(scenes, output.resolve(), minimum=4, maximum=7,
                        kind="synthetic_smoke_not_production")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VideoForge MVP - no auto upload or AI spending")
    commands = parser.add_subparsers(dest="action", required=True)
    test = commands.add_parser("smoke", help="generate clearly synthetic technical MP4")
    test.add_argument("--output", type=Path, default=Path("dist/smoke.mp4"))
    production = commands.add_parser("render", help="render real supplied assets")
    production.add_argument("--video", "--manifest", dest="manifest", required=True, type=Path)
    production.add_argument("--output", type=Path,
                            help="optional; must match output/<channel>/videos/<id>/video.mp4")
    args = parser.parse_args(argv)
    try:
        result = smoke(args.output) if args.action == "smoke" else render(
            args.manifest, args.output
        )
    except VideoForgeError as exc:
        print(f"BLOCKED: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
