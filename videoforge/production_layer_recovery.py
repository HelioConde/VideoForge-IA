"""Retoma apenas uma camada faltante de um artifact parcial real do VideoForge.

Nunca recria o background aprovado tecnicamente. Confere SHA da
cena-mae, provenance, RGB e canal antes de consumir UMA edicao de IA.
Este modulo NAO aprova o rig nem gera MP4.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

from . import scene_layers, production_scene_layers, proxy_images
from .errors import VideoForgeError

def digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("LAYER_RECOVERY_SOURCE_MISSING_OR_SYMLINK")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def restore_partial(channel: str, video_id: str, number: int, incoming: Path,
                    original_dir: Path) -> Path:
    _plan, _story, entry = production_scene_layers.read_plan(channel, video_id, number)
    if number != 1:
        raise VideoForgeError("LAYER_RECOVERY_ONLY_FIRST_SCENE_CURRENTLY")
    manifest = scene_layers._read_manifest(incoming / "manifest.json")
    if any(manifest.get(k) != v for k, v in (
        ("channel", channel), ("video_id", video_id),
        ("scene", f"cena-{number:02d}"),
    )):
        raise VideoForgeError("LAYER_RECOVERY_MANIFEST_ORIGIN_INVALID")
    if set(manifest.get("layers", {})) != {"background"} or (
        manifest["layers"]["background"].get("technical_status") != "verified"
    ):
        raise VideoForgeError("LAYER_RECOVERY_EXPECTS_ONLY_VALID_BACKGROUND")
    filename = incoming / "cena-base.png"
    source_report = original_dir / f"cena-{number:02d}.production.json"
    original = original_dir / f"cena-{number:02d}.png"
    source_sha = production_scene_layers.validate_source(original, source_report, entry, channel, video_id)
    if digest(filename) != source_sha or manifest.get("source", {}).get("sha256") != source_sha:
        raise VideoForgeError("LAYER_RECOVERY_SOURCE_SHA_MISMATCH")
    background = incoming / "background.png"
    if digest(background) != manifest["layers"]["background"].get("sha256"):
        raise VideoForgeError("LAYER_RECOVERY_BACKGROUND_SHA_MISMATCH")
    dimensions = scene_layers.png_info(background.read_bytes(), require_alpha=False)
    if (dimensions["width"], dimensions["height"]) != (1024, 1536):
        raise VideoForgeError("LAYER_RECOVERY_CANVAS_INVALID")
    if (incoming / "character-main.png").exists():
        raise VideoForgeError("LAYER_RECOVERY_ALREADY_COMPLETE")
    folder = scene_layers.output_dir(channel, video_id, f"cena-{number:02d}")
    if folder.exists() or folder.is_symlink():
        raise VideoForgeError("LAYER_RECOVERY_WOULD_OVERWRITE")
    folder.mkdir(parents=True)
    for name in ("cena-base.png", "background.png", "manifest.json"):
        shutil.copyfile(incoming / name, folder / name)
    print("LAYER_RECOVERY_VERIFIED", source_sha, manifest["layers"]["background"]["sha256"])
    return folder

def recover(channel: str, video_id: str, number: int, incoming: Path,
            original_dir: Path, url: str, model: str="gpt-image-2") -> dict:
    plan, _story, entry = production_scene_layers.read_plan(channel, video_id, number)
    if model not in proxy_images.IMAGE_MODELS or plan.get("budget", {}).get("extra_images_this_test") != 2:
        raise VideoForgeError("LAYER_RECOVERY_MODEL_OR_BUDGET_INVALID")
    folder = restore_partial(channel, video_id, number, incoming, original_dir)
    instruction = plan["instruction_character"] + (
        f" Cena original {entry['scene']}: {entry['visual_direction']}. "
    )
    scene_layers.generate_layer(folder, "character-main", url,
                                os.getenv("CODEX_PROXY_API_KEY", ""), model,
                                instruction=instruction)
    manifest = scene_layers._read_manifest(folder/"manifest.json")
    if set(manifest["layers"]) != {"background","character-main"}:
        raise VideoForgeError("LAYER_RECOVERY_INCOMPLETE")
    result = {
        "schema":"videoforge/layer-recovery-result/v1",
        "channel":channel,"video_id":video_id,
        "scene":f"cena-{number:02d}",
        "source_sha256":manifest["source"]["sha256"],
        "background_reused":True,
        "background_sha256":manifest["layers"]["background"]["sha256"],
        "character_group_sha256":manifest["layers"]["character-main"]["sha256"],
        "individual_parts_created":False,
        "rig_animation_applied":False,
        "human_visual_approval":False,
        "video_official":False,
        "youtube_uploaded":False,
    }
    (folder/"recovery.qa.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8"
    )
    print("LAYER_RECOVERY_FINISHED", json.dumps(result,ensure_ascii=False))
    return result

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--channel",required=True)
    parser.add_argument("--video-id",required=True)
    parser.add_argument("--number",type=int,required=True)
    parser.add_argument("--partial",type=Path,required=True)
    parser.add_argument("--scene-original",type=Path,required=True)
    parser.add_argument("--url",required=True)
    parser.add_argument("--model",default="gpt-image-2")
    args=parser.parse_args()
    try:
        recover(args.channel,args.video_id,args.number,args.partial,args.scene_original,args.url,args.model)
        return 0
    except (VideoForgeError, scene_layers.LayerError, proxy_images.ProxyImageError,
            OSError, ValueError, KeyError) as err:
        print("LAYER_RECOVERY_BLOCKED",str(err),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
