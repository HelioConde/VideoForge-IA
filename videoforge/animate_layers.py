"""VideoForge - animar PNGs separados em MP4 demonstrativo via FFmpeg.

Entrada: artifact do Teste 2 com cena-base + background + personagem +
foreground, cada arquivo com hash e QA tecnico do manifesto original.
Camada de capa propositalmente NAO aplicada: personagem ainda a contem.
O resultado e um clipe tecnico com trilha silenciosa, NAO video publicavel.
Nenhuma inferencia de IA e feita neste modulo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

from . import mvp, proxy_images, scene_layers
from .errors import VideoForgeError
from .paths import _check_symlinks

FPS = 24
OUTPUT_SIZE = (1080, 1920)
MIN_DURATION = 4
MAX_DURATION = 12
PRESETS = {
    "cinematic": {
        "background_pan_x": 8,
        "background_pan_y": 10,
        "character_bob_x": 3,
        "character_bob_y": 5,
        "foreground_shift_x": 3,
        "foreground_shift_y": 2,
    },
    "subtle": {
        "background_pan_x": 4,
        "background_pan_y": 5,
        "character_bob_x": 1,
        "character_bob_y": 2,
        "foreground_shift_x": 1,
        "foreground_shift_y": 1,
    },
}

class AnimationError(VideoForgeError):
    pass


def _trusted_assets(input_dir: Path, channel: str, video_id: str, scene: str) -> tuple[Path, dict]:
    """Importa artifact existente, verificando hashes por cena e canal."""
    folder = scene_layers.resume(channel, video_id, scene, input_dir)
    manifest = scene_layers._read_manifest(folder / "manifest.json")
    ref = manifest["source"]
    for name in ("background", "character-main", "foreground-roof"):
        record = manifest["layers"].get(name)
        if not isinstance(record, dict) or record.get("technical_status") != "verified":
            raise AnimationError("ANIMATION_LAYER_NOT_VERIFIED")
        asset = folder / (name + ".png")
        data = scene_layers._read_png(asset)
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise AnimationError("ANIMATION_LAYER_HASH_MISMATCH")
        image_info = scene_layers.png_info(data, require_alpha=(name != "background"))
        if (image_info["width"], image_info["height"]) != (ref["width"], ref["height"]):
            raise AnimationError("ANIMATION_LAYER_RESOLUTION_MISMATCH")
    return folder, manifest


def filter_graph(width: int, height: int, duration: int, preset: str) -> str:
    """Somente presets auditados, sem expressao externa de FFmpeg injetavel."""
    if preset not in PRESETS or not (16 <= width <= 4096 and 16 <= height <= 4096):
        raise AnimationError("ANIMATION_PRESET_OR_RESOLUTION_INVALID")
    if not MIN_DURATION <= duration <= MAX_DURATION:
        raise AnimationError("ANIMATION_DURATION_INVALID")
    motions = PRESETS[preset]
    # Overscan preserva a cobertura do fundo enquanto a camera deriva.
    extra_x = max(32, ((width * 3 // 100) // 2) * 2)
    extra_y = max(48, ((height * 3 // 100) // 2) * 2)
    margin_x, margin_y = extra_x // 2, extra_y // 2
    bgx, bgy = motions["background_pan_x"], motions["background_pan_y"]
    charx, chary = motions["character_bob_x"], motions["character_bob_y"]
    fgx, fgy = motions["foreground_shift_x"], motions["foreground_shift_y"]
    if bgx >= margin_x or bgy >= margin_y:
        raise AnimationError("ANIMATION_OVERSCAN_TOO_SMALL")
    return (
        f"[0:v]format=rgba,scale={width + extra_x}:{height + extra_y}:flags=bicubic,"
        f"crop={width}:{height}:x='{margin_x}+{bgx}*sin(n/29)':"
        f"y='{margin_y}+{bgy}*sin(n/41)'[background];"
        "[1:v]format=rgba[character];"
        "[2:v]format=rgba[foreground];"
        f"[background][character]overlay=x='{charx}*sin(t*1.15)':"
        f"y='{chary}*sin(t*1.75)':eval=frame:format=auto[scene];"
        f"[scene][foreground]overlay=x='{fgx}*sin(t*.75)':"
        f"y='{fgy}*sin(t*1.15)':eval=frame:format=auto,"
        "scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,"
        f"crop=1080:1920,fade=t=in:st=0:d=0.25,"
        f"fade=t=out:st={duration - 0.4}:d=0.4,format=yuv420p[v]"
    )


def _frame_md5(path: Path, at: float) -> str:
    return mvp._command([
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-i", str(path), "-ss", f"{at:.3f}", "-frames:v", "1",
        "-f", "md5", "-",
    ], timeout=90).strip()


def render_preview(
    input_dir: Path, channel: str, video_id: str, scene: str, *,
    duration: int = 8, preset: str = "cinematic"
) -> dict:
    if preset not in PRESETS or not MIN_DURATION <= duration <= MAX_DURATION:
        raise AnimationError("ANIMATION_PARAMETERS_INVALID")
    mvp._require_tools()
    folder, manifest = _trusted_assets(input_dir, channel, video_id, scene)
    source = manifest["source"]
    width, height = source["width"], source["height"]
    graph = filter_graph(width, height, duration, preset)
    dest = proxy_images.ROOT / "output" / channel / "videos" / video_id / "animacoes" / scene
    _check_symlinks(dest, stop_at=proxy_images.ROOT)
    video = dest / "teste-parallax.mp4"
    qa_path = dest / "teste-parallax.qa.json"
    motion_path = dest / "movimentos.json"
    if any(path.exists() or path.is_symlink() for path in (video, qa_path, motion_path)):
        raise AnimationError("ANIMATION_PREVIEW_ALREADY_EXISTS")
    dest.mkdir(parents=True, exist_ok=True)
    tracks = {
        "background": "slow camera pan with overscan",
        "character-main": "independent breathing/bobbing",
        "foreground-roof": "independent parallax drift",
        "cape": "disabled: cape already included in character-main",
    }
    with tempfile.TemporaryDirectory(prefix="vf-animation-") as tmp:
        temp = Path(tmp) / "scene.mp4"
        mvp._command([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-framerate", str(FPS), "-i", str(folder / "background.png"),
            "-loop", "1", "-framerate", str(FPS), "-i", str(folder / "character-main.png"),
            "-loop", "1", "-framerate", str(FPS), "-i", str(folder / "foreground-roof.png"),
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex", graph,
            "-map", "[v]", "-map", "3:a:0", "-t", str(duration),
            "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "23", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(temp),
        ], timeout=600)
        qa = mvp._verify_mp4(
            temp, expected=float(duration),
            minimum=float(duration) - 0.6,
            maximum=float(duration) + 0.6,
        )
        frame_a = _frame_md5(temp, max(0.5, duration * 0.2))
        frame_b = _frame_md5(temp, duration * 0.75)
        if not frame_a.startswith("MD5=") or not frame_b.startswith("MD5=") or frame_a == frame_b:
            raise AnimationError("ANIMATION_MOTION_NOT_DETECTED")
        shutil.copy2(temp, video)
    qa.update({
        "schema": "videoforge/animation-preview/v1",
        "kind": "layer_animation_preview_not_publishable",
        "channel": channel, "video_id": video_id, "scene": scene,
        "preset": preset, "fps": FPS,
        "motion_detected": True,
        "motion_method": "different decoded frame checksums",
        "source_sha256": source["sha256"],
        "tracks": tracks,
        "rendered_from": ["background", "character-main", "foreground-roof"],
        "cape_overlay_enabled": False,
        "audio_track_is_silence": True,
        "narration_present": False,
        "pixel_alignment_verified": False,
        "visual_approval": "pending",
        "youtube_uploaded": False,
    })
    qa_path.write_text(json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    motion_path.write_text(json.dumps({
        "schema": "videoforge/animation-tracks/v1",
        "source_scene_hash": source["sha256"],
        "fps": FPS, "duration_seconds": duration,
        "preset": preset, "tracks": tracks,
        "parameters": PRESETS[preset],
        "cape_independent_animation": "requires character body without cape",
        "youtube_upload": False,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return qa


def main() -> int:
    parser = argparse.ArgumentParser(description="Renderizar animacao de camadas reais com FFmpeg")
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--duration", type=int, choices=range(MIN_DURATION, MAX_DURATION + 1), default=8)
    parser.add_argument("--preset", choices=tuple(PRESETS), default="cinematic")
    args = parser.parse_args()
    try:
        result = render_preview(
            args.input_dir, args.channel, args.video_id, args.scene,
            duration=args.duration, preset=args.preset,
        )
    except (AnimationError, VideoForgeError, scene_layers.LayerError) as exc:
        print("ANIMATION_BLOCKED:", str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
