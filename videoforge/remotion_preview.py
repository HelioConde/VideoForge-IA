"""Renderizacao Remotion de camadas que vieram do nosso Codex Proxy.

O CLI do Remotion 4 e responsavel pelas animacoes. FFmpeg so gera silencio
e e utilizado para o QA tecnico apos a renderizacao, nao para movimento.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from . import animate_layers, mesh_rig, mvp, proxy_images, scene_layers
from .errors import VideoForgeError
from .paths import _check_symlinks

FPS = 30
MIN_SECONDS = 4
MAX_SECONDS = 12
RENDERER = "remotion"
PRESETS = ("ultrassutil", "equilibrado", "vivo")
COMPOSITION = "VideoForgeLayerScene"
PROPS_SCHEMA = "videoforge/remotion-preview-props/v1"
QA_SCHEMA = "videoforge/remotion-technical-qa/v1"
FILES = ("background.png", "character-main.png", "foreground-roof.png")


class RemotionPreviewError(VideoForgeError):
    pass


def target_dir(channel: str, video_id: str, scene: str) -> Path:
    scene_layers.output_dir(channel, video_id, scene)
    folder = (proxy_images.ROOT / "output" / channel / "videos" / video_id
              / "animacoes" / scene)
    _check_symlinks(folder, stop_at=proxy_images.ROOT)
    return folder


def make_props(*, channel: str, video_id: str, scene: str,
               duration: int, preset: str, source_sha: str,
               rig: dict | None = None) -> dict:
    if preset not in PRESETS or not MIN_SECONDS <= duration <= MAX_SECONDS:
        raise RemotionPreviewError("REMOTION_PREVIEW_PARAMETERS_INVALID")
    if not isinstance(source_sha, str) or len(source_sha) != 64 or any(
        c not in "0123456789abcdef" for c in source_sha
    ):
        raise RemotionPreviewError("REMOTION_REFERENCE_HASH_INVALID")
    scene_layers.output_dir(channel, video_id, scene)
    props = {
        "schema": PROPS_SCHEMA, "id": video_id, "scene": scene,
        "channel": channel, "durationFrames": duration * FPS,
        "preset": preset,
        "background": "vf-scene/background.png",
        "character": "vf-scene/character-main.png",
        "foreground": "vf-scene/foreground-roof.png",
        "silence": "vf-scene/silence.wav",
        "layerSourceHash": source_sha,
        "youtubeUpload": False, "capeOverlayEnabled": rig is not None,
        "bodyPartRiggingImplemented": rig is not None,
        "animationEngine": RENDERER,
        "motionAuthors": [
            "AutoEditorVideo/motion-remotion/src/character-idle.ts",
            "AutoEditorVideo/motion-remotion/src/cinematic-motion.ts",
            "video-forge-ia2/videoforge/motion/videoforge-motion.ts",
        ],
    }
    if rig is not None:
        props["rig"] = rig
    return props


def prepare(input_dir: Path, channel: str, video_id: str, scene: str,
            duration: int, preset: str, rig_dir: Path | None = None) -> Path:
    if not MIN_SECONDS <= duration <= MAX_SECONDS or preset not in PRESETS:
        raise RemotionPreviewError("REMOTION_PREVIEW_PARAMETERS_INVALID")
    destination = target_dir(channel, video_id, scene)
    public_dir = proxy_images.ROOT / "motion-remotion" / "public" / "vf-scene"
    _check_symlinks(public_dir, stop_at=proxy_images.ROOT)
    if destination.exists() or public_dir.exists():
        raise RemotionPreviewError("REMOTION_OUTPUT_ALREADY_EXISTS")
    # Valida SHA-256, canais, tipo PNG, RGBA e tamanho de todas as camadas.
    folder, manifest = animate_layers._trusted_assets(
        input_dir, channel, video_id, scene
    )
    rig = None
    if rig_dir is not None:
        source = manifest["source"]
        rig = mesh_rig.validate_rig_dir(
            rig_dir, channel=channel, video_id=video_id, scene=scene,
            source_sha=source["sha256"], width=source["width"],
            height=source["height"], duration_frames=duration * FPS,
        )
    props = make_props(channel=channel, video_id=video_id, scene=scene,
                       duration=duration, preset=preset,
                       source_sha=manifest["source"]["sha256"], rig=rig)
    destination.mkdir(parents=True)
    public_dir.mkdir(parents=True)
    # Sempre manter o fallback intacto, sem sobrepor a capa duplicada.
    for name in FILES:
        shutil.copyfile(folder / name, public_dir / name)
    if rig_dir is not None:
        rig_public = public_dir / "rig"
        rig_public.mkdir()
        for name in mesh_rig.ASSET_NAMES.values():
            shutil.copyfile(rig_dir / name, rig_public / name)
    mvp._command([
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", str(duration), "-c:a", "pcm_s16le",
        str(public_dir / "silence.wav"),
    ], timeout=60)
    if not (public_dir / "silence.wav").is_file():
        raise RemotionPreviewError("REMOTION_SILENT_AUDIO_NOT_PREPARED")
    (destination / "remotion-props.json").write_text(
        json.dumps(props, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def verify(channel: str, video_id: str, scene: str) -> dict:
    destination = target_dir(channel, video_id, scene)
    props_path = destination / "remotion-props.json"
    output = destination / "remotion-teste.mp4"
    if props_path.is_symlink() or not props_path.is_file():
        raise RemotionPreviewError("REMOTION_PROPS_MISSING")
    try:
        props = json.loads(props_path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError, OSError) as exc:
        raise RemotionPreviewError("REMOTION_PROPS_INVALID") from exc
    if (not isinstance(props, dict) or props.get("schema") != PROPS_SCHEMA or
        props.get("channel") != channel or props.get("id") != video_id or
        props.get("scene") != scene or
        props.get("capeOverlayEnabled") is not (props.get("rig") is not None) or
        props.get("bodyPartRiggingImplemented") is not (props.get("rig") is not None) or
        props.get("youtubeUpload") is not False or
        props.get("animationEngine") != RENDERER):
        raise RemotionPreviewError("REMOTION_PROPS_MISMATCH")
    if not output.is_file() or output.is_symlink() or output.stat().st_size < 20_000:
        raise RemotionPreviewError("REMOTION_MP4_NOT_RENDERED")
    duration = props["durationFrames"] / FPS
    report = mvp._verify_mp4(
        output, expected=duration, minimum=duration - .4, maximum=duration + .4
    )
    frame1 = animate_layers._frame_md5(output, duration*.17)
    frame2 = animate_layers._frame_md5(output, duration*.68)
    if not frame1.startswith("MD5=") or frame1 == frame2:
        raise RemotionPreviewError("REMOTION_FRAME_MOTION_NOT_DETECTED")
    has_rig = props.get("rig") is not None
    if has_rig and (
        not isinstance(props["rig"], dict) or
        props["rig"].get("schema") != mesh_rig.RIG_SCHEMA
    ):
        raise RemotionPreviewError("REMOTION_RIG_PROPS_INVALID")
    report.update({
        "schema": QA_SCHEMA, "renderer": RENDERER,
        "composition": COMPOSITION, "duration_frames": props["durationFrames"],
        "fps_expected": FPS, "channel": channel, "video_id": video_id,
        "scene": scene, "source_sha256": props["layerSourceHash"],
        "motion_authors": props["motionAuthors"],
        "motion_detected": True,
        "motion_method": "FFmpeg decoded-frame MD5 comparison (QA only)",
        "motion_layers": (
            ["background: legacy Remotion cinematic motion",
             "body/head/eyes: SVG 2D neck pivot and frame-based blink",
             "cape: SVG affine triangle mesh warp",
             "foreground-roof: legacy VideoForge motion cue"]
            if has_rig else
            ["background: legacy Remotion cinematic motion",
             "character-main: legacy Remotion character-idle",
             "foreground-roof: legacy VideoForge motion cue"]
        ),
        "cape_overlay_enabled": has_rig,
        "body_part_rigging_implemented": has_rig,
        "rig_assets_review_declared": has_rig,
        "narration_present": False, "audio_is_silent": True,
        "visual_review": "pending", "pixel_alignment_verified": False,
        "youtube_uploaded": False, "publishable": False,
    })
    qa = destination / "remotion-teste.qa.json"
    if qa.exists():
        raise RemotionPreviewError("REMOTION_QA_ALREADY_EXISTS")
    qa.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n",
                  encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Animar camadas com Remotion legado")
    parser.add_argument("action", choices=("prepare", "verify"))
    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--rig-dir", type=Path, help="Artifact com rig.json e sprites RGBA")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--duration", type=int, default=8)
    parser.add_argument("--preset", default="equilibrado")
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            if args.input_dir is None:
                raise RemotionPreviewError("REMOTION_ARTIFACT_REQUIRED")
            result = prepare(args.input_dir, args.channel, args.video_id,
                             args.scene, args.duration, args.preset, args.rig_dir)
            print("Remotion preparado:", result.relative_to(proxy_images.ROOT))
        else:
            result = verify(args.channel, args.video_id, args.scene)
            print(json.dumps(result, ensure_ascii=False))
        return 0
    except (RemotionPreviewError, VideoForgeError,
            scene_layers.LayerError, proxy_images.ProxyImageError) as exc:
        print("REMOTION_BLOCKED:", str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
