"""Use approved V2 character-bible directly from permanent GitHub image archives.

No download of V1 artifacts; no image-generation calls. Validate archive
provenance + PNG hash + human approval before giving a source to the editor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from .cinematic_direction import assert_shot_generation_ready,load_active_remake_plan
from .errors import VideoForgeError
from .remake_autopilot import verified_asset
from .scene_layers import png_info

ROOT=Path(__file__).resolve().parents[1]


def prepare_remake_reference(channel:str,video_id:str,destination:Path,
                             root:Path=ROOT)->dict:
    manifest=load_active_remake_plan(channel,video_id,root)
    if manifest is None:
        raise VideoForgeError("REMAKE_REFERENCE_ONLY_FOR_ACTIVE_V2")
    assert_shot_generation_ready(channel,video_id,root)
    anchor=manifest["identity_anchors"][0]
    relative=anchor["path"]
    sha=anchor["sha256"]
    parts=Path(relative).parts
    if (len(parts)!=5 or parts[:3]!=("assets","geracoes","production-art-request")
            or not parts[3].isdigit() or parts[4]!="character-bible.png"):
        raise VideoForgeError("REMAKE_REFERENCE_ARCHIVE_PATH_INVALID")
    run_id=int(parts[3])
    episode=Path(root)/"canal"/channel/"videos"/video_id
    if not verified_asset(episode,relative,sha):
        raise VideoForgeError("REMAKE_REFERENCE_SHA_NOT_VERIFIED")
    archive=episode.joinpath(*parts[:-1])
    manifest_file=archive/"manifesto-geracoes.json"
    production_file=archive/"character-bible.production.json"
    if any(f.is_symlink() or not f.is_file() for f in (manifest_file,production_file)):
        raise VideoForgeError("REMAKE_REFERENCE_PROVENANCE_MISSING")
    try:
        archive_manifest=json.loads(manifest_file.read_text(encoding="utf-8"))
        result=json.loads(production_file.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError) as exc:
        raise VideoForgeError("REMAKE_REFERENCE_PROVENANCE_INVALID") from exc
    if (archive_manifest.get("schema")!="videoforge/permanent-generated-image-archive/v1"
            or archive_manifest.get("producer")!="production-art-request"
            or archive_manifest.get("github_run_id")!=run_id
            or archive_manifest.get("channel")!=channel
            or archive_manifest.get("video_id")!=video_id
            or not any(isinstance(item,dict)
                       and item.get("file")=="character-bible.png"
                       and item.get("sha256")==sha
                       for item in archive_manifest.get("images",[]))
            or result.get("schema")!="videoforge/production-art-result/v1"
            or result.get("channel")!=channel or result.get("video_id")!=video_id
            or result.get("asset_id")!="character-bible"
            or result.get("sha256")!=sha
            or result.get("official_video_created") is not False):
        raise VideoForgeError("REMAKE_REFERENCE_PROVENANCE_MISMATCH")
    raw=(archive/"character-bible.png").read_bytes()
    info=png_info(raw,require_alpha=False)
    if (info["width"],info["height"])!=(1024,1536):
        raise VideoForgeError("REMAKE_REFERENCE_DIMENSIONS_INVALID")
    target=Path(destination)
    if (target.is_symlink() or any(parent.is_symlink() for parent in target.parents)):
        raise VideoForgeError("REMAKE_REFERENCE_DESTINATION_SYMLINK")
    target.mkdir(parents=True,exist_ok=True)
    payloads=(("character-bible.png",raw),
              ("character-bible.production.json",production_file.read_bytes()))
    for filename,blob in payloads:
        out=target/filename
        if out.is_symlink() or (out.exists() and out.read_bytes()!=blob):
            raise VideoForgeError("REMAKE_REFERENCE_WOULD_OVERWRITE_OTHER_SOURCE")
    for filename,blob in payloads:
        out=target/filename
        out.write_bytes(blob)
    if hashlib.sha256((target/"character-bible.png").read_bytes()).hexdigest()!=sha:
        raise VideoForgeError("REMAKE_REFERENCE_POST_COPY_SHA_MISMATCH")
    return {"source":"approved_immutable_github_archive","channel":channel,
            "video_id":video_id,"sha256":sha,"run_id":run_id,
            "source_path":relative,"human_approved":True,
            "image_generation_calls":0,"youtube_uploaded":False}


def main()->int:
    p=argparse.ArgumentParser(description="Stage EP01 V2 approved anchor from GitHub, no proxy")
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        report=prepare_remake_reference(args.channel,args.video_id,args.output)
        print("REMAKE_APPROVED_REFERENCE_STAGED",json.dumps(report,ensure_ascii=False))
        return 0
    except (OSError,ValueError,VideoForgeError) as exc:
        print("REMAKE_REFERENCE_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
