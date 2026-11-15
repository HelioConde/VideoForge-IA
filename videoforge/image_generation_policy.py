"""Image generation permissions: later remake instruction overrides old EP01 ban.

Editorial authorization never silently approves paid provider calls or upload.
Existing per-run provider checks remain in effect.
"""
from __future__ import annotations
import json
from pathlib import Path
from .errors import VideoForgeError

ROOT = Path(__file__).resolve().parents[1]
CHANNEL, VIDEO = "alchemy-lab", "mmorpg-conquiste-a-princesa-ep01"


def assert_image_generation_allowed(channel: str, video_id: str, root: Path = ROOT) -> None:
    if (channel, video_id) != (CHANNEL, VIDEO):
        return
    episode = Path(root) / "canal" / channel / "videos" / video_id
    if (episode / "SEM-GERACAO-NOVAS-IMAGENS.lock").exists():
        raise VideoForgeError("IMAGE_GENERATION_DENIED_ALCHEMY_EP01: legacy lock still active")
    try:
        state = json.loads((episode / "estado-atual.json").read_text(encoding="utf-8"))
        policy = json.loads((episode / "autonomy-policy.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise VideoForgeError("IMAGE_GENERATION_DENIED_ALCHEMY_EP01: state not verifiable") from exc
    if (state.get("remake_v2", {}).get("generation_editorially_authorized") is not True
            or state.get("locks", {}).get("no_new_image_generation") is not False
            or policy.get("scope") != f"{channel}/{video_id}"):
        raise VideoForgeError("IMAGE_GENERATION_DENIED_ALCHEMY_EP01: remake not authorized")
    if (policy.get("paid_provider_calls_approved") is not True
            or type(policy.get("max_chargeable_calls_per_run")) is not int
            or policy["max_chargeable_calls_per_run"] < 1):
        raise VideoForgeError("IMAGE_GENERATION_DENIED_ALCHEMY_EP01: provider cost permission required")
