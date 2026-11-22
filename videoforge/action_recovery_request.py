"""Validate an existing Actions artifact recovery without invoking providers.

A non-legacy recovery is pinned to a producer, expected PNG filename and SHA
so a failed git push can be repaired without silently charging for a new image.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from .paths import CHANNEL_IDS, IDENTIFIER

SCHEMA = "videoforge/restore-existing-action-artifact/v1"
PRODUCERS = {"legacy-action-import", "production-proxy-separate-part-v1"}
PART = re.compile(r"(c[0-9]{2}-p[0-9]{2})-(background-clean|character-[a-z0-9_-]+|object-[a-z0-9_-]+)\.png")
SHA = re.compile(r"[0-9a-f]{64}")


def validate(request: dict) -> dict:
    if (not isinstance(request, dict) or request.get("schema") != SCHEMA
            or request.get("generate_new_image") is not False
            or request.get("render_mp4") is not False
            or request.get("youtube_upload") is not False
            or request.get("source_folder") != "imagens"):
        raise ValueError("RECOVERY_SOURCE_ONLY_GATES_INVALID")
    ch, vid = request.get("channel"), request.get("video_id")
    run, name = request.get("source_run_id"), request.get("artifact_name")
    producer = request.get("archive_producer", "legacy-action-import")
    if (ch not in CHANNEL_IDS or not isinstance(vid, str)
            or not IDENTIFIER.fullmatch(vid)
            or type(run) is not int or run <= 0
            or not isinstance(name, str)
            or not re.fullmatch(r"[a-zA-Z0-9_.-]{8,180}", name)
            or str(run) not in name
            or producer not in PRODUCERS):
        raise ValueError("RECOVERY_ARTIFACT_IDENTIFIER_INVALID")
    filename = request.get("expected_png_name")
    expected_sha = request.get("expected_png_sha256")
    if (filename is None) != (expected_sha is None):
        raise ValueError("RECOVERY_PNG_PIN_INCOMPLETE")
    if filename is not None:
        if (not isinstance(filename, str)
                or not re.fullmatch(r"[a-zA-Z0-9_.-]{5,180}\.png", filename)
                or not isinstance(expected_sha, str) or not SHA.fullmatch(expected_sha)):
            raise ValueError("RECOVERY_PNG_PIN_INVALID")
    if producer != "legacy-action-import":
        part = PART.fullmatch(filename or "")
        if (ch != "alchemy-lab" or vid != "mmorpg-conquiste-a-princesa-ep01"
                or not part
                or name != f"vf-ep01-part-{part.group(1).upper()}-{part.group(2)}-{run}"):
            raise ValueError("RECOVERY_PRODUCTION_ARTIFACT_MISMATCH")
    return {"ch": ch, "vid": vid, "run": run, "name": name,
            "producer": producer, "expected_png_name": filename,
            "expected_png_sha256": expected_sha}


def verify_download(folder: Path, config: dict) -> dict:
    folder = Path(folder)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("RECOVERY_INPUT_FOLDER_INVALID")
    images = sorted(folder.rglob("*.png"))
    if not images or any(p.is_symlink() or not p.is_file() for p in images):
        raise ValueError("RECOVERY_PNG_MISSING_OR_UNSAFE")
    if config["expected_png_name"] is not None:
        if len(images) != 1 or images[0].name != config["expected_png_name"]:
            raise ValueError("RECOVERY_PINNED_PNG_NAME_OR_COUNT_MISMATCH")
        digest = hashlib.sha256(images[0].read_bytes()).hexdigest()
        if digest != config["expected_png_sha256"]:
            raise ValueError("RECOVERY_PINNED_PNG_SHA_MISMATCH")
    return {"images": len(images), "producer": config["producer"],
            "source_run_id": config["run"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--request", type=Path, required=True)
    p.add_argument("--github-output", type=Path)
    p.add_argument("--verify-input", type=Path)
    args = p.parse_args()
    config = validate(json.loads(args.request.read_text(encoding="utf-8")))
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as fd:
            for key in ("ch", "vid", "run", "name", "producer"):
                fd.write(f"{key}={config[key]}\n")
    if args.verify_input:
        print("RECOVERY_PINNED_EXISTING_PNG_VERIFIED",
              json.dumps(verify_download(args.verify_input, config)))
    else:
        print("RECOVERY_ONLY_EXISTING_ACTIONS_ARTIFACT",
              config["ch"], config["vid"], config["run"], config["producer"])


if __name__ == "__main__":
    main()
