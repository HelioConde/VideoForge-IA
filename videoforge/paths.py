"""Strict channel/video/model directory resolution, no file writes.

Layout follows the original VideoForge contract:
canal/<id>/videos/<video-id>/video.json
modelos/<modelo>/modelo.json
output/<id>/videos/<video-id>/video.mp4

No channel-to-channel path escape, secret loading or YouTube calls.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

from .errors import VideoForgeError

CHANNEL_IDS = frozenset({
    "otaku-br", "otaku-en", "gamer", "manu-kids", "alchemy-lab",
})
SUPPORTED_RENDER_MODELS = frozenset({"imagem-estatica"})
IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class VideoContext:
    root: Path
    channel: str
    video_id: str
    model: str
    output: Path


def _valid_id(value: object) -> bool:
    return (isinstance(value, str) and 1 <= len(value) <= 64
            and IDENTIFIER.fullmatch(value) is not None)


def _read_json_config(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 128_000:
        raise VideoForgeError("CHANNEL_OR_MODEL_CONFIG_MISSING")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError) as exc:
        raise VideoForgeError("CHANNEL_OR_MODEL_CONFIG_INVALID") from exc
    if not isinstance(value, dict):
        raise VideoForgeError("CHANNEL_OR_MODEL_CONFIG_INVALID")
    return value


def _check_symlinks(path: Path, *, stop_at: Path) -> None:
    """Check all path components down to an already selected repository root."""
    cursor = path
    while cursor != stop_at:
        if cursor.is_symlink():
            raise VideoForgeError("CHANNEL_PATH_SYMLINK_NOT_ALLOWED")
        if cursor == cursor.parent:
            raise VideoForgeError("CHANNEL_PATH_OUTSIDE_REPOSITORY")
        cursor = cursor.parent


def resolve_video_context(
    manifest_path: Path, manifest: dict, *, requested_output: Path | None = None
) -> VideoContext:
    """Validate all channel boundaries before contacting any media provider."""
    raw = Path(manifest_path)
    if ".." in raw.parts or not isinstance(manifest, dict):
        raise VideoForgeError("VIDEO_MANIFEST_LOCATION_INVALID")
    source = raw.absolute()
    # /repo/canal/<channel>/videos/<video-id>/video.json
    if (source.name != "video.json" or len(source.parents) < 5
            or source.parents[1].name != "videos"
            or source.parents[3].name != "canal"):
        raise VideoForgeError("VIDEO_MANIFEST_LOCATION_INVALID")
    video_id = source.parents[0].name
    channel_id = source.parents[2].name
    root = source.parents[4]
    if channel_id not in CHANNEL_IDS or not _valid_id(video_id):
        raise VideoForgeError("VIDEO_CHANNEL_OR_ID_INVALID")
    _check_symlinks(source, stop_at=root)
    if not source.is_file():
        raise VideoForgeError("VIDEO_MANIFEST_MISSING")
    if manifest.get("channel") != channel_id:
        raise VideoForgeError("VIDEO_CHANNEL_MISMATCH")
    channel_cfg = _read_json_config(root / "canal" / channel_id / "canal.json")
    if channel_cfg.get("id") != channel_id:
        raise VideoForgeError("CHANNEL_CONFIG_ID_MISMATCH")
    youtube = channel_cfg.get("youtube")
    if (not isinstance(youtube, dict) or youtube.get("conectado") is not False
            or youtube.get("upload_habilitado") is not False):
        raise VideoForgeError("CHANNEL_YOUTUBE_CONNECTION_NOT_ALLOWED")
    requested_model = manifest.get("modelo")
    model_id = channel_cfg.get("modelo_padrao") if requested_model is None else requested_model
    if not _valid_id(model_id):
        raise VideoForgeError("VIDEO_MODEL_ID_INVALID")
    model_file = root / "modelos" / model_id / "modelo.json"
    _check_symlinks(model_file, stop_at=root)
    model_cfg = _read_json_config(model_file)
    if model_cfg.get("id") != model_id:
        raise VideoForgeError("VIDEO_MODEL_CONFIG_ID_MISMATCH")
    if model_id not in SUPPORTED_RENDER_MODELS or model_cfg.get("operacional") is not True:
        raise VideoForgeError("VIDEO_MODEL_NOT_IMPLEMENTED")
    target = root / "output" / channel_id / "videos" / video_id / "video.mp4"
    _check_symlinks(target, stop_at=root)
    if requested_output is not None:
        candidate = Path(requested_output)
        if ".." in candidate.parts or candidate.absolute() != target:
            raise VideoForgeError("VIDEO_OUTPUT_NOT_CHANNEL_SCOPED")
    return VideoContext(
        root=root, channel=channel_id, video_id=video_id,
        model=model_id, output=target,
    )
