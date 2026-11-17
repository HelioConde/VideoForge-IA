"""Arquiva camadas PNG realmente geradas por image edit, sem duplicar a mãe.

Produz arquivos PNG + .production.json compatíveis com o arquivador
compartilhado. O commit com registro na Bíblia ocorre depois, pelo workflow.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from .errors import VideoForgeError
from .paths import CHANNEL_IDS, IDENTIFIER
from .persist_generated_assets import _png_info
from .remake_autopilot import ROOT

COMPONENTS = ("background", "character-main")


def stage(channel: str, video_id: str, number: int, root: Path = ROOT):
    if (channel not in CHANNEL_IDS or not isinstance(video_id, str)
            or not IDENTIFIER.fullmatch(video_id)
            or not isinstance(number, int) or not 1 <= number <= 99):
        raise VideoForgeError("BIBLE_LAYER_STAGE_SCOPE_INVALID")
    root = Path(root)
    scene = f"cena-{number:02d}"
    src = root / "output" / channel / "videos" / video_id / "assets" / scene
    dst = root / "output" / channel / "videos" / video_id / "imagens"
    if not src.is_dir():
        return {"staged": 0, "reason": "source_scene_not_generated"}
    manifest = src / "manifest.json"
    if manifest.is_symlink() or not manifest.is_file():
        raise VideoForgeError("BIBLE_LAYER_SOURCE_MANIFEST_MISSING")
    obj = json.loads(manifest.read_text(encoding="utf-8"))
    if (obj.get("schema") != "videoforge/scene-layers/v1"
            or obj.get("channel") != channel
            or obj.get("video_id") != video_id
            or obj.get("scene") != scene
            or not isinstance(obj.get("layers"), dict)):
        raise VideoForgeError("BIBLE_LAYER_SOURCE_SCOPE_MISMATCH")
    source = obj.get("source") or {}
    source_path = src / "cena-base.png"
    if source_path.is_symlink() or not source_path.is_file():
        raise VideoForgeError("BIBLE_LAYER_MOTHER_MISSING")
    src_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if src_sha != source.get("sha256"):
        raise VideoForgeError("BIBLE_LAYER_MOTHER_SHA_MISMATCH")
    staged = []
    for part in COMPONENTS:
        original = src / (part + ".png")
        if not original.exists():
            continue
        if original.is_symlink() or not original.is_file():
            raise VideoForgeError("BIBLE_LAYER_IMAGE_UNSAFE")
        record = obj["layers"].get(part)
        if not isinstance(record, dict) or record.get("file") != original.name:
            raise VideoForgeError("BIBLE_LAYER_RECORD_MISSING")
        data = original.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        w, h = _png_info(data)
        if (record.get("sha256") != sha
                or record.get("width") != w or record.get("height") != h):
            raise VideoForgeError("BIBLE_LAYER_SHA_MISMATCH")
        name = scene + "-" + part
        metadata = {
            "schema": "videoforge/visual-bible-layer-archive/v1",
            "channel": channel, "video_id": video_id,
            "asset_id": name, "sha256": sha,
            "actual_width": w, "actual_height": h,
            "biblia_item_id": None, "biblia_categoria": None,
            "technical_status": record.get("technical_status", "unknown"),
            "source_originals_sha_verified": [{
                "id": scene + "-mother",
                "path": f"output/{channel}/videos/{video_id}/assets/{scene}/cena-base.png",
                "sha256": src_sha
            }],
            "human_visual_approval": False,
            "official_video_created": False,
            "youtube_uploaded": False
        }
        staged.append((dst / (name + ".png"), data))
        staged.append((dst / (name + ".production.json"),
                       (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode()))
    if not staged:
        return {"staged": 0, "reason": "no_generated_layers"}
    for target, data in staged:
        if target.is_symlink() or (target.exists() and target.read_bytes() != data):
            raise VideoForgeError("BIBLE_LAYER_WOULD_OVERWRITE")
    dst.mkdir(parents=True, exist_ok=True)
    for target, data in staged:
        if not target.exists():
            target.write_bytes(data)
    return {"staged": len(staged) // 2, "source_scene": scene, "image_dir": str(dst.relative_to(root))}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--channel", required=True)
    p.add_argument("--video-id", required=True)
    p.add_argument("--number", type=int, required=True)
    a = p.parse_args()
    print("BIBLE_LAYER_STAGE", json.dumps(stage(a.channel, a.video_id, a.number), ensure_ascii=False))


if __name__ == "__main__":
    main()
