"""Import existing C12 PNG bytes and stage the isolated Three.js draft. No AI."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import zipfile

from .errors import VideoForgeError
from .persist_generated_assets import archive
from .scene_layers import png_info

ROOT = Path(__file__).resolve().parents[1]
CHANNEL = "alchemy-lab"
VIDEO = "mmorpg-conquiste-a-princesa-ep01"
EPISODE = Path("canal") / CHANNEL / "videos" / VIDEO
OUT = Path("output") / CHANNEL / "videos" / VIDEO / "c12-technical"
ARCHIVE = EPISODE / "assets" / "geracoes" / "c12-technical-import"
MAX_FILE = 35_000_000
MAX_TOTAL = 160_000_000
MAX_ENTRIES = 256
REVIEW_FRAMES = (0, 30, 74, 76, 119, 120, 150, 173, 175, 239)


def require(condition, code):
    if not condition:
        raise VideoForgeError(code)


def safe_path(path: Path):
    require(not any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())
                    for p in (path, *path.parents)), "C12_SYMLINK_OR_JUNCTION")


def manifest(root=ROOT):
    return json.loads((root / EPISODE / "c12-technical-assets.json").read_text(encoding="utf-8"))


def candidates(sources):
    """Yield bounded bytes; ZIP entries are never extracted to filesystem paths."""
    count, total = 0, 0
    for source in sources:
        source = Path(source)
        safe_path(source)
        if not source.exists():
            continue
        if source.suffix.lower() == ".zip":
            with zipfile.ZipFile(source) as bundle:
                entries = bundle.infolist()
                require(len(entries) <= MAX_ENTRIES, "C12_ZIP_TOO_MANY_ENTRIES")
                names = set()
                for entry in entries:
                    name = entry.filename
                    path = PurePosixPath(name)
                    require(name and not path.is_absolute() and ".." not in path.parts
                            and "\\" not in name and ":" not in name
                            and name.casefold() not in names
                            and not stat.S_ISLNK(entry.external_attr >> 16), "C12_ZIP_UNSAFE_ENTRY")
                    names.add(name.casefold())
                    require(not entry.flag_bits & 1 and entry.file_size <= MAX_FILE, "C12_ZIP_ENCRYPTED_OR_OVERSIZED")
                    total += entry.file_size
                    require(total <= MAX_TOTAL, "C12_INPUT_TOO_LARGE")
                    if entry.is_dir() or path.suffix.lower() != ".png":
                        continue
                    count += 1
                    require(count <= MAX_ENTRIES, "C12_TOO_MANY_FILES")
                    yield name, bundle.read(entry), None
        else:
            paths = source.rglob("*") if source.is_dir() else [source]
            for path in paths:
                safe_path(path)
                if not path.is_file() or path.suffix.lower() != ".png":
                    continue
                count += 1
                size = path.stat().st_size
                total += size
                require(count <= MAX_ENTRIES and size <= MAX_FILE and total <= MAX_TOTAL,
                        "C12_INPUT_TOO_LARGE")
                yield path.name, path.read_bytes(), path


def scan(sources, specification):
    assets = specification["assets"]
    canvas = specification["sourceCanvas"]
    require(len(canvas) == 2 and all(type(n) is int and 0 < n <= 4096 for n in canvas),
            "C12_MANIFEST_CANVAS_INVALID")
    ids = set()
    for asset in assets:
        require(isinstance(asset["id"], str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,80}", asset["id"])
                and asset["id"] not in ids, "C12_MANIFEST_ID_INVALID")
        ids.add(asset["id"])
        require(asset["role"] in ("mother", "background", "sprite")
                and asset["shot"] in ("C12-P02", "C12-P03")
                and re.fullmatch(r"[0-9a-f]{64}", asset["sha256"]), "C12_MANIFEST_ASSET_INVALID")
        dims = asset["dimensions"]
        require(len(dims) == 2 and all(type(n) is int and 0 < n <= 4096 for n in dims),
                "C12_MANIFEST_DIMENSIONS_INVALID")
        if asset["role"] == "sprite":
            bbox = asset.get("bbox", [])
            require(len(bbox) == 4 and all(type(n) is int for n in bbox)
                    and bbox[0] >= 0 and bbox[1] >= 0
                    and bbox[2:] == dims and bbox[0] + bbox[2] <= canvas[0]
                    and bbox[1] + bbox[3] <= canvas[1], "C12_MANIFEST_BBOX_DIMENSIONS_MISMATCH")
        else:
            require(dims == canvas, "C12_MANIFEST_CANVAS_DIMENSIONS_MISMATCH")
    expected = {a["sha256"]: a for a in assets}
    require(len(expected) == len(assets), "C12_MANIFEST_DUPLICATE_HASH")
    found, invalid, ignored = {}, [], 0
    for name, data, path in candidates(sources):
        digest = hashlib.sha256(data).hexdigest()
        asset = expected.get(digest)
        if asset is None:
            ignored += 1
            continue
        info = png_info(data, require_alpha=asset["role"] == "sprite")
        if [info["width"], info["height"]] != asset["dimensions"]:
            invalid.append({"id": asset["id"], "reason": "native_dimensions_or_crop_alignment_mismatch",
                            "actual": [info["width"], info["height"]], "expected": asset["dimensions"]})
            continue
        found[asset["id"]] = (data, path)
    missing = [{"id": a["id"], "role": a["role"], "shot": a["shot"], "sha256": a["sha256"]}
               for a in assets if a["id"] not in found]
    report = {"schema": "videoforge/c12-import-preflight/v1", "channel": CHANNEL,
              "video_id": VIDEO, "ready": not missing and not invalid,
              "foundCount": len(found), "requiredCount": len(assets), "missing": missing,
              "invalid": invalid, "ignoredUnrecognizedPngs": ignored,
              "officialVideoApproved": False, "humanVisualReview": False, "imageGenerationCalls": 0}
    return report, found


def write_json(path: Path, data):
    safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_assets(sources, import_id: int, root=ROOT):
    require(type(import_id) is int and import_id > 0, "C12_IMPORT_ID_INVALID")
    spec = manifest(root)
    report, found = scan(sources, spec)
    require(report["ready"], "C12_REQUIRED_EXISTING_ASSETS_MISSING_OR_INVALID")
    staging_rel = OUT / "incoming" / str(import_id)
    staging = root / staging_rel
    safe_path(staging)
    safe_path(root / ARCHIVE / str(import_id))
    require(not staging.exists(), "C12_IMPORT_STAGING_EXISTS")
    staging.mkdir(parents=True)
    for asset in spec["assets"]:
        (staging / (asset["id"] + ".png")).write_bytes(found[asset["id"]][0])
    write_json(staging / "manifest.json", {"schema": "videoforge/c12-existing-pixel-import/v1",
               "channel": CHANNEL, "video_id": VIDEO, "sourceManifest": spec,
               "generatedImages": 0, "humanVisualReview": False,
               "importId": import_id, "idOrigin": "local-import-not-github-actions"})
    receipt = archive(CHANNEL, VIDEO, staging_rel.as_posix(), import_id,
                      "c12-technical-import", root=root)
    receipt["gitCommitAndPushRequired"] = True
    receipt["archivePath"] = (ARCHIVE / str(import_id)).as_posix()
    write_json(root / OUT / "import-receipt.json", receipt)
    return receipt


def require_committed(path: Path, data: bytes, root: Path):
    """No archive flag based only on a filename or a JSON assertion."""
    safe_path(path)
    require(path.resolve().is_relative_to((root / ARCHIVE).resolve()), "C12_ASSET_OUTSIDE_ARCHIVE")
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    result = subprocess.run(["git", "show", "HEAD:" + rel], cwd=root,
                            capture_output=True, timeout=30)
    require(result.returncode == 0 and result.stdout == data, "C12_ORIGINALS_NOT_COMMITTED_EXACTLY")


def prepare(root=ROOT):
    spec = manifest(root)
    report, found = scan([root / ARCHIVE], spec)
    write_json(root / OUT / "preflight.json", report)
    require(report["ready"], "C12_REQUIRED_EXISTING_ASSETS_MISSING_OR_INVALID")
    for data, path in found.values():
        require(path is not None, "C12_ARCHIVED_SOURCE_REQUIRED")
        require_committed(path, data, root)
    prefix = f"vf-cinema/{CHANNEL}/{VIDEO}/assets/planos/"
    files, shots = [], []
    for shot_id in ("C12-P02", "C12-P03"):
        records = [a for a in spec["assets"] if a["shot"] == shot_id]
        mother = next(a for a in records if a["role"] == "mother")
        background = next(a for a in records if a["role"] == "background")
        bg_file = prefix + shot_id + "/background-inpaint-technical.png"
        files.append((bg_file, found[background["id"]][0]))
        layers = []
        for asset in records:
            if asset["role"] != "sprite":
                continue
            file = prefix + shot_id + "/" + asset["id"] + ".png"
            layers.append({k: asset[k] for k in ("id", "bbox", "sha256", "z", "mesh")} | {"file": file})
            files.append((file, found[asset["id"]][0]))
        shots.append({"id": shot_id, "sourceOriginalSha256": mother["sha256"],
                      "backgroundSha256": background["sha256"], "backgroundFile": bg_file, "layers": layers})
    props = {"schema": "videoforge/c12-technical-three-mesh-preview/v1", "fps": 30,
             "sourceCanvas": {"width": 941, "height": 1672}, "width": 720, "height": 1280,
             "totalFrames": 240, "expectedMeshTriangles": 512, "status": "TECHNICAL_NO_HUMAN_APPROVAL",
             "sourceOriginalsArchived": True, "officialVideoApproved": False,
             "imageGenerationCalls": 0, "shots": shots}
    target = root / OUT / "props.json"
    require(not target.exists(), "C12_PROPS_ALREADY_EXIST")
    for file, _ in files:
        dest = root / "motion-remotion/public" / file
        safe_path(dest)
        require(not dest.exists(), "C12_STAGED_ASSET_ALREADY_EXISTS")
    for file, data in files:
        dest = root / "motion-remotion/public" / file
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    write_json(target, props)
    return target


def verify(video: Path, output: Path):
    safe_path(video)
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(video)],
                                     capture_output=True, text=True, check=True, timeout=30).stdout)
    streams = [s for s in info["streams"] if s["codec_type"] == "video"]
    require(len(streams) == 1, "C12_VIDEO_STREAM_REQUIRED")
    stream = streams[0]
    require(stream["codec_name"] == "h264" and stream["pix_fmt"] == "yuv420p"
            and (stream["width"], stream["height"]) == (720, 1280)
            and stream["r_frame_rate"] == "30/1" and int(stream["nb_frames"]) == 240,
            "C12_VIDEO_FORMAT_MISMATCH")
    require(not any(s["codec_type"] == "audio" for s in info["streams"]), "C12_DRAFT_MUST_BE_SILENT")
    stills = video.parent / "review-frames"
    frame_hashes = {}
    for frame in REVIEW_FRAMES:
        original = stills / f"frame-{frame}.png"
        repeat = stills / f"frame-{frame}-repeat.png"
        safe_path(original)
        safe_path(repeat)
        a, b = original.read_bytes(), repeat.read_bytes()
        require(png_info(a)["width"] == 720 and png_info(a)["height"] == 1280,
                "C12_REVIEW_FRAME_SIZE")
        require(a == b, "C12_NONDETERMINISTIC_FRAME_" + str(frame))
        frame_hashes[str(frame)] = hashlib.sha256(a).hexdigest()
    # Same shot and same static watermark: a static plate fails this check.
    # This is only visible-change evidence; seam/occlusion QA still needs review.
    require(frame_hashes["0"] != frame_hashes["30"] and frame_hashes["120"] != frame_hashes["150"],
            "C12_SHOT_HAS_NO_VISIBLE_CHANGE")
    report = {"schema": "videoforge/c12-technical-render-evidence/v1",
              "runId": os.getenv("GITHUB_RUN_ID"), "commit": os.getenv("GITHUB_SHA"),
              "sha256": hashlib.sha256(video.read_bytes()).hexdigest(), "frames": 240,
              "seconds": 8, "shots": ["C12-P02", "C12-P03"], "codec": "h264",
              "audioPresent": any(s["codec_type"] == "audio" for s in info["streams"]),
              "humanVisualReview": False, "officialVideoApproved": False,
              "imageGenerationCalls": 0, "fullRigReady": False}
    report.update({"repeatedFrameHashes": frame_hashes, "repeatFramesIdentical": True,
                   "neutralRecompositionApproved": False, "seamAndOcclusionReview": "pending",
                   "renderer": "Remotion ThreeCanvas SWANGLE"})
    props_file = video.parent / "props.json"
    safe_path(props_file)
    report["inputPropsSha256"] = hashlib.sha256(props_file.read_bytes()).hexdigest()
    write_json(output, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "import", "prepare", "verify"))
    parser.add_argument("--source", type=Path, action="append")
    parser.add_argument("--import-id", type=int)
    parser.add_argument("--output", type=Path, default=ROOT / OUT / "preflight.json")
    parser.add_argument("--video", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "preflight":
            report, _ = scan(args.source or [ROOT / ARCHIVE], manifest())
            write_json(args.output, report)
            print(json.dumps(report))
            return 0 if report["ready"] else 2
        if args.command == "import":
            require(args.source and args.import_id, "C12_IMPORT_SOURCE_AND_ID_REQUIRED")
            print(json.dumps(import_assets(args.source, args.import_id)))
        elif args.command == "prepare":
            print(prepare())
        else:
            require(args.video is not None, "C12_VIDEO_PATH_REQUIRED")
            print(json.dumps(verify(args.video, args.output)))
        return 0
    except (VideoForgeError, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, subprocess.SubprocessError) as exc:
        write_json(args.output, {"ready": False, "error": str(exc), "officialVideoApproved": False})
        print("C12_TECHNICAL_BLOCKED", str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
