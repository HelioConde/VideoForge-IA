"""Deterministic packaging and coverage for unapproved, directed rig diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
from collections.abc import Sequence

from . import rig_candidate, scene_layers


class DirectedRigError(ValueError):
    pass


def _mask_uncovered(pixels: bytes | bytearray,
                    referenced_pixels: Sequence[bytes | bytearray]) -> tuple[bytearray, int]:
    """Keep a source RGBA pixel only where every reference is transparent.

    Inputs are full-canvas RGBA buffers. Returns a new full-canvas buffer and
    the number of nontransparent source pixels retained. Source bytes are
    preserved exactly outside covered pixels; covered pixels become RGBA 0.
    Neither input buffer is mutated.
    """
    if len(pixels) == 0 or len(pixels) % 4:
        raise DirectedRigError("UNCOVERED_RGBA_INVALID")
    if not referenced_pixels or any(len(ref) != len(pixels) for ref in referenced_pixels):
        raise DirectedRigError("UNCOVERED_REFERENCE_CANVAS_MISMATCH")
    covered = bytearray(len(pixels) // 4)
    for reference in referenced_pixels:
        for alpha_offset in range(3, len(reference), 4):
            if reference[alpha_offset]:
                covered[alpha_offset // 4] = 1
    result = bytearray(pixels)
    uncovered = 0
    for pixel_index, is_covered in enumerate(covered):
        offset = pixel_index * 4
        if is_covered:
            result[offset:offset + 4] = b"\0\0\0\0"
        elif pixels[offset + 3]:
            uncovered += 1
    return result, uncovered


def _require(condition, message):
    if not condition:
        raise DirectedRigError(message)


def _load(path):
    path = Path(path)
    _require(not any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())
                     for p in [path, *path.parents]), "JSON_SYMLINK")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            _require(k not in result, "DUPLICATE_JSON_KEY")
            result[k] = v
        return result
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (OSError, ValueError) as exc:
        raise DirectedRigError("INVALID_JSON: " + str(exc)) from exc
    _require(isinstance(data, dict), "JSON_OBJECT_REQUIRED")
    _finite_tree(data)
    return data


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _integer(value, minimum=0):
    return type(value) is int and value >= minimum


def _finite_tree(value):
    if isinstance(value, float):
        _require(math.isfinite(value), "NON_FINITE_JSON_VALUE")
    elif isinstance(value, dict):
        for item in value.values():
            _finite_tree(item)
    elif isinstance(value, list):
        for item in value:
            _finite_tree(item)


def _safe_output(path):
    _require(not any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())
                     for p in [path, *path.parents]), "OUTPUT_SYMLINK")


def _source(root, spec, canvas, alpha=False):
    _require(isinstance(spec, dict), "SOURCE_OBJECT_REQUIRED")
    name = spec.get("file")
    _require(isinstance(name, str) and name and "\\" not in name and ":" not in name,
             "SOURCE_PATH_INVALID")
    rel = Path(name)
    _require(not rel.is_absolute() and all(x not in ("..", ".", "") for x in name.split("/")),
             "SOURCE_PATH_ESCAPE")
    path = root / rel
    _require(not any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())
                     for p in [path, *path.parents]), "SOURCE_SYMLINK")
    _require(path.resolve().is_relative_to(root.resolve()) and path.is_file(), "SOURCE_MISSING_OR_ESCAPE")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    _require(spec.get("sha256") == digest, "SOURCE_SHA_MISMATCH")
    info = scene_layers.png_info(data)
    _require((info["width"], info["height"]) == (canvas["width"], canvas["height"]),
             "SOURCE_CANVAS_MISMATCH")
    if alpha:
        _require(info.get("color_type") == 6 or data[25] == 6, "SPRITE_RGBA_REQUIRED")
    return path, digest


def _direction(data):
    _require(data.get("schema") == "videoforge/direcao-rig-remotion/v1", "DIRECTION_SCHEMA_INVALID")
    _require(isinstance(data.get("scenes"), list) and data["scenes"], "SCENES_REQUIRED")
    fmt = data.get("format", {})
    for key in ("width", "height", "fps"):
        _require(_integer(fmt.get(key), 1), "FORMAT_INVALID")
    result, ids, scenes = [], set(), set()
    previous_end = 0
    for scene in data["scenes"]:
        _require(isinstance(scene, dict) and isinstance(scene.get("id"), str)
                 and scene["id"] not in scenes, "SCENE_ID_INVALID")
        scenes.add(scene["id"])
        _require(isinstance(scene.get("shots"), list) and scene["shots"], "SHOTS_REQUIRED")
        _require(scene.get("startFrame", previous_end) == previous_end, "SCENE_TIMELINE_INVALID")
        for shot in scene["shots"]:
            _require(isinstance(shot, dict) and isinstance(shot.get("id"), str)
                     and shot["id"] not in ids, "SHOT_ID_INVALID")
            ids.add(shot["id"])
            start, end = shot.get("startFrame"), shot.get("endFrameExclusive")
            _require(_integer(start) and _integer(end, 1) and start == previous_end
                     and end > start and shot.get("durationFrames", end-start) == end-start,
                     "SHOT_TIMELINE_INVALID")
            previous_end = end
            _require(isinstance(shot.get("rigKeyframes"), list), "TRACKS_REQUIRED")
            _require(shot.get("scene", scene["id"]) == scene["id"], "SHOT_SCENE_MISMATCH")
            camera = shot.get("camera", {})
            _require(isinstance(camera, dict), "CAMERA_INVALID")
            if camera:
                _require(camera.get("type") in ("none", "perspective_3d"), "CAMERA_TYPE_INVALID")
                camera_frames = camera.get("keyframes", [])
                _require(isinstance(camera_frames, list), "CAMERA_KEYFRAMES_INVALID")
                if camera["type"] == "perspective_3d":
                    _require(len(camera_frames) >= 2, "CAMERA_KEYS_REQUIRED")
                last_camera_frame = -1
                for key in camera_frames:
                    _require(isinstance(key, dict) and _integer(key.get("frame"))
                             and start <= key["frame"] < end and key["frame"] > last_camera_frame,
                             "CAMERA_KEYFRAME_INVALID")
                    last_camera_frame = key["frame"]
                    if camera["type"] == "perspective_3d":
                        _require(_number(key.get("z")) and key["z"] > 0
                                 and _number(key.get("fovDeg")) and 0 < key["fovDeg"] < 180
                                 and isinstance(key.get("lookAt"), list) and len(key["lookAt"]) == 3
                                 and all(_number(v) for v in key["lookAt"]), "CAMERA_GEOMETRY_INVALID")
            for track in shot["rigKeyframes"]:
                _require(isinstance(track, dict) and isinstance(track.get("target"), str)
                         and track["target"], "TRACK_TARGET_INVALID")
                _require(track.get("transform") in ("rotationZ", "translateX", "translateY", "scaleX", "scaleY"),
                         "TRACK_TRANSFORM_INVALID")
                unit = ("degrees" if track["transform"] == "rotationZ" else
                        "ratio" if track["transform"].startswith("scale") else "pixels_source_canvas")
                _require(track.get("unit") == unit, "TRACK_UNIT_INVALID")
                _require(track.get("easing", "easeInOutCubic") in ("linear", "easeInOutCubic"), "TRACK_EASING_INVALID")
                frames = track.get("keyframes")
                _require(isinstance(frames, list) and len(frames) >= 2, "KEYFRAMES_REQUIRED")
                last = -1
                for key in frames:
                    _require(isinstance(key, dict) and _integer(key.get("frame"))
                             and start <= key["frame"] < end and key["frame"] > last
                             and _number(key.get("value")), "KEYFRAME_INVALID")
                    last = key["frame"]
                    if track["transform"].startswith("scale"):
                        _require(key["value"] >= 0, "NEGATIVE_SCALE")
            _require(len({(t["target"], t["transform"]) for t in shot["rigKeyframes"]})
                     == len(shot["rigKeyframes"]), "DUPLICATE_TRACK")
            result.append(shot)
        _require(scene.get("endFrameExclusive", previous_end) == previous_end, "SCENE_TIMELINE_INVALID")
    _require(fmt.get("durationInFrames", previous_end) == previous_end, "DURATION_MISMATCH")
    return result


def _bindings(direction, bindings, root):
    _require(bindings.get("schema") == "videoforge/direction-bindings/v1", "BINDINGS_SCHEMA_INVALID")
    for key in ("channel", "video_id"):
        val = bindings.get(key)
        _require(isinstance(val, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", val)
                 and val == direction.get(key), "BINDINGS_ID_MISMATCH")
    _require(isinstance(bindings.get("shots"), dict), "BINDING_SHOTS_REQUIRED")
    shots = _direction(direction)
    _require(set(bindings["shots"]) <= {s["id"] for s in shots}, "UNKNOWN_BOUND_SHOT")
    validated = {}
    for shot in shots:
        spec = bindings["shots"].get(shot["id"])
        if spec is None:
            continue
        _require(isinstance(spec, dict), "SHOT_BINDING_INVALID")
        canvas = spec.get("canvas", {})
        _require(all(_integer(canvas.get(k), 1) for k in ("width", "height")), "CANVAS_INVALID")
        _require(isinstance(spec.get("warnings"), list)
                 and all(isinstance(w, str) for w in spec["warnings"]), "WARNINGS_REQUIRED")
        sources = {"sourceMother": _source(root, spec.get("sourceMother"), canvas),
                   "background": _source(root, spec.get("background"), canvas)}
        nodes = spec.get("nodes")
        _require(isinstance(nodes, list), "NODES_REQUIRED")
        by_id = {}
        for node in nodes:
            _require(isinstance(node, dict) and isinstance(node.get("id"), str)
                     and re.fullmatch(r"[a-zA-Z0-9_.-]+", node["id"])
                     and node["id"] not in by_id and node["id"] not in ("background", "sourceMother"), "NODE_ID_INVALID")
            by_id[node["id"]] = node
            _require(isinstance(node.get("role"), str) and _integer(node.get("z"), -100000), "NODE_METADATA_INVALID")
            pivot = node.get("pivot")
            _require(isinstance(pivot, list) and len(pivot) == 2 and all(_number(v) for v in pivot)
                     and 0 <= pivot[0] <= canvas["width"] and 0 <= pivot[1] <= canvas["height"], "PIVOT_INVALID")
            if "file" in node:
                bbox = node.get("bbox")
                _require(isinstance(bbox, list) and len(bbox) == 4
                         and all(_integer(v) for v in bbox) and bbox[2] > 0 and bbox[3] > 0
                         and bbox[0]+bbox[2] <= canvas["width"]
                         and bbox[1]+bbox[3] <= canvas["height"], "BBOX_INVALID")
                sources[node["id"]] = _source(root, node, canvas, alpha=True)
            else:
                _require(not any(k in node for k in ("sha256", "bbox", "mesh")), "GROUP_HAS_SPRITE_METADATA")
            if "mesh" in node:
                mesh = node["mesh"]
                _require(isinstance(mesh, dict) and mesh.get("kind") in
                         ("cloth", "hair-back", "hair-front", "hair-front-left", "hair-front-right", "cape")
                         and _integer(mesh.get("columns"), 2) and mesh["columns"] <= 16
                         and _integer(mesh.get("rows"), 2) and mesh["rows"] <= 20
                         and mesh.get("pinnedRows") == [0] and _number(mesh.get("amplitudePx"))
                         and 0 <= mesh["amplitudePx"] <= 12, "MESH_INVALID")
                pin = mesh.get("sourcePin")
                if pin is not None:
                    _require(isinstance(pin, dict) and set(pin) == {"startY", "endY"}
                             and all(_number(pin[k]) for k in ("startY", "endY"))
                             and 0 <= pin["startY"] < pin["endY"] <= canvas["height"],
                             "SOURCE_PIN_INVALID")
        for node in nodes:
            visited, parent = {node["id"]}, node.get("parent")
            _require("parent" in node, "PARENT_REQUIRED")
            while parent is not None:
                _require(isinstance(parent, str) and parent in by_id and parent not in visited, "NODE_DAG_INVALID")
                visited.add(parent)
                parent = by_id[parent].get("parent")
            if node.get("mesh", {}).get("sourcePin"):
                ancestors, current = set(), node
                while current is not None:
                    ancestors.add(current["id"])
                    current = by_id.get(current["parent"])
                _require(not any(t["target"] in ancestors and t["transform"].startswith("scale")
                                 and any(k["value"] <= 1e-6 for k in t["keyframes"])
                                 for t in shot["rigKeyframes"]), "SOURCE_PIN_SCALE_NOT_INVERTIBLE")
        for node in nodes:
            if "onlyUncoveredBy" not in node:
                continue
            _require("file" in node, "UNCOVERED_OWNER_SPRITE_REQUIRED")
            references = node["onlyUncoveredBy"]
            _require(isinstance(references, list) and references, "UNCOVERED_REFERENCES_REQUIRED")
            _require(all(isinstance(ref, str) for ref in references)
                     and len(set(references)) == len(references)
                     and node["id"] not in references, "UNCOVERED_REFERENCES_INVALID")
            for ref in references:
                _require(ref in by_id and "file" in by_id[ref], "UNCOVERED_REFERENCE_SPRITE_REQUIRED")
                _require("onlyUncoveredBy" not in by_id[ref], "UNCOVERED_REFERENCE_NESTING_FORBIDDEN")
        missing = sorted({t["target"] for t in shot["rigKeyframes"]} - set(by_id))
        validated[shot["id"]] = (spec, sources, missing)
    return shots, validated


def inspect(direction_path, bindings_path, output=None):
    direction, bindings = _load(direction_path), _load(bindings_path)
    shots, validated = _bindings(direction, bindings, Path(bindings_path).parent)
    rows = []
    for shot in shots:
        bound = validated.get(shot["id"])
        blockers = ["unapproved_art_and_provisional_pivots"]
        if bound is None:
            blockers.append("missing_shot_binding")
        elif bound[2]:
            blockers.extend("missing_target:"+x for x in bound[2])
        rows.append({"id": shot["id"], "trackCount": len(shot["rigKeyframes"]),
                     "targets": sorted({t["target"] for t in shot["rigKeyframes"]}),
                     "bound": bound is not None, "missingTargets": bound[2] if bound else sorted({t["target"] for t in shot["rigKeyframes"]}),
                     "warnings": bound[0]["warnings"] if bound else [], "blockers": blockers})
    result = {"schema": "videoforge/direction-coverage/v1", "channel": bindings["channel"],
              "videoId": bindings["video_id"], "sceneCount": len(direction["scenes"]), "shotCount": len(shots),
              "trackCount": sum(r["trackCount"] for r in rows), "shots": rows,
              "humanVisualReview": False, "publishable": False, "approval": False}
    if output:
        _safe_output(Path(output))
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    return result


def prepare(direction_path, bindings_path, shot_id, output_dir, public_dir):
    direction, bindings = _load(direction_path), _load(bindings_path)
    shots, validated = _bindings(direction, bindings, Path(bindings_path).parent)
    _require(shot_id in validated, "SHOT_MAPPING_REQUIRED")
    spec, sources, missing = validated[shot_id]
    _require(not missing, "MISSING_TARGETS: " + ",".join(missing))
    shot = next(s for s in shots if s["id"] == shot_id)
    _require(re.fullmatch(r"[a-zA-Z0-9_-]+", shot_id), "SHOT_PATH_INVALID")
    relative = Path("vf-directed") / bindings["channel"] / bindings["video_id"] / shot_id
    dest, output = Path(public_dir) / relative, Path(output_dir)
    for path in (dest, output):
        _safe_output(path)
    _require(not dest.exists(), "PUBLIC_ASSETS_EXIST")
    _require(not output.exists() or output.is_dir(), "OUTPUT_NOT_DIRECTORY")
    _require(not any((output/name).exists() for name in ("props.json", "source-hashes.json")), "OUTPUT_EXISTS")
    # Decode all crops before writing any output. Original pixels are preserved.
    full_pixels = {}
    crops = {}
    recovered = []
    for node in spec["nodes"]:
        if "file" in node:
            full_pixels[node["id"]] = rig_candidate._image(
                sources[node["id"]][0], **spec["canvas"])
    for node in spec["nodes"]:
        if "file" in node:
            x, y, w, h = node["bbox"]
            pixels = full_pixels[node["id"]]
            if "onlyUncoveredBy" in node:
                pixels, _ = _mask_uncovered(
                    pixels, [full_pixels[ref] for ref in node["onlyUncoveredBy"]])
                stride = spec["canvas"]["width"] * 4
                recovered_count = sum(
                    pixels[row * stride + col * 4 + 3] != 0
                    for row in range(y, y + h) for col in range(x, x + w))
                recovered.append({
                    "nodeId": node["id"],
                    "sourceFile": str(Path(sources[node["id"]][0]).relative_to(Path(bindings_path).parent)),
                    "sourceSha256": sources[node["id"]][1],
                    "onlyUncoveredBy": node["onlyUncoveredBy"],
                    "uncoveredAlphaPixelsInBbox": recovered_count,
                })
            stride = spec["canvas"]["width"] * 4
            crops[node["id"]] = bytearray().join(pixels[(y+r)*stride+x*4:(y+r)*stride+(x+w)*4] for r in range(h))
    dest.mkdir(parents=True)
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sources["background"][0], dest / "background.png")
    packaged = []
    for index, node in enumerate(spec["nodes"]):
        obj = {k: v for k, v in node.items()
               if k not in ("sha256", "file", "onlyUncoveredBy")}
        if "file" in node:
            filename = f"node-{index}.png"
            rig_candidate._write_png(dest / filename, crops[node["id"]], node["bbox"][2], node["bbox"][3])
            obj["file"] = (relative / filename).as_posix()
        packaged.append(obj)
    warnings = ["TECHNICAL DRAFT: unapproved candidate art; provisional pivots; hidden anatomy and narrative coverage pending."] + spec["warnings"]
    props = {"schema": "videoforge/directed-rig-preview/v1", "mode": "technical_draft",
             "channel": bindings["channel"], "videoId": bindings["video_id"], "id": shot_id,
             **{k: direction["format"][k] for k in ("width", "height", "fps")},
             "startFrame": shot["startFrame"], "durationFrames": shot["endFrameExclusive"]-shot["startFrame"],
             "pixelRecovery": recovered,
             "shots": [{"id": shot_id, "startFrame": shot["startFrame"], "endFrameExclusive": shot["endFrameExclusive"],
                        "canvas": spec["canvas"], "background": (relative / "background.png").as_posix(),
                        "nodes": packaged, "tracks": shot["rigKeyframes"], "camera": shot.get("camera", {})}],
             "warnings": warnings, "humanVisualReview": False, "publishable": False}
    (output / "props.json").write_text(json.dumps(props, indent=2)+"\n", encoding="utf-8")
    hashes = {k: {"file": str(v[0].relative_to(Path(bindings_path).parent)), "sha256": v[1]} for k, v in sources.items()}
    manifests = {name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                 for name, path in (("direction", direction_path), ("bindings", bindings_path))}
    (output / "source-hashes.json").write_text(json.dumps({"channel": bindings["channel"], "videoId": bindings["video_id"], "directionSha256": manifests["direction"], "bindingsSha256": manifests["bindings"], "manifests": manifests, "sources": hashes, "humanVisualReview": False, "publishable": False}, indent=2)+"\n", encoding="utf-8")
    return output / "props.json"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "prepare"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--direction", required=True, type=Path)
        cmd.add_argument("--bindings", required=True, type=Path)
        if name == "inspect":
            cmd.add_argument("--output", required=True, type=Path)
        else:
            cmd.add_argument("--shot", required=True)
            cmd.add_argument("--output-dir", required=True, type=Path)
            cmd.add_argument("--public-dir", type=Path, default=Path("motion-remotion/public"))
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            inspect(args.direction, args.bindings, args.output)
        else:
            prepare(args.direction, args.bindings, args.shot, args.output_dir, args.public_dir)
    except (DirectedRigError, OSError, ValueError) as exc:
        parser.exit(2, str(exc)+"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
