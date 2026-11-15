"""C12 technical-only neutral recomposition and LOCAL mesh motion QA.

Consumes only pre-existing, SHA-verified RGB/RGBA PNGs and the real Remotion
MP4. Does not generate or modify art, approve rig, or publish to YouTube.
Neutral QA uses source pixels, not renders/synthetic stand-ins. Video QA
decodes the H.264 itself and rejects a static video or whole-frame camera move.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from . import c12_technical_preview as source

WIDTH, HEIGHT = 720, 1280
SOURCE_WIDTH, SOURCE_HEIGHT = 941, 1672
FPS, FRAMES = 30, 240
SELECTED = (0, 73, 120, 180)
STILLS = (0, 73, 120, 180, 239)
REPEAT = (73, 180)
OUTPUT = source.ROOT / "output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/c12-mesh-technical"


class C12QAError(ValueError):
    """Fail-closed gate for the unapproved technical preview."""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def neutral_difference(mother, reconstructed) -> tuple[float, int]:
    """Exact per-channel MAE and number of pixels with a channel delta >16.

    Pillow images are passed directly in tests; no temporary image is
    generated or stored. Both frames must match in size.
    """
    from PIL import ImageChops
    if mother.size != reconstructed.size or mother.mode != "RGB" or reconstructed.mode != "RGB":
        raise C12QAError("NEUTRAL_RGB_DIMENSIONS_MISMATCH")
    difference = ImageChops.difference(mother, reconstructed)
    samples = 0
    pixels_over_16 = 0
    for color in difference.getdata():
        samples += sum(color)
        pixels_over_16 += int(max(color) > 16)
    return samples / (mother.width * mother.height * 3), pixels_over_16


def neutral(out: Path) -> dict:
    """Recompose original mother in native coordinates; require very low diff.

    This numerical gate does NOT mean the underlays, masks or hidden anatomy
    have been approved by a human.
    """
    from PIL import Image
    out.mkdir(parents=True, exist_ok=True)
    plan = source.plan()
    source.policy()
    entries = source.required_files(plan)
    verified = []
    for path, expected, dims, alpha, role in entries:
        source.validate_png(path, expected, dims, alpha)
        verified.append({"role": role, "sha256": expected})
    parts = {mesh["id"]: mesh for mesh in plan["meshParts"]}
    result = {
        "schema": "videoforge/c12-technical-neutral-recomposition/v1",
        "status": "REJECTED", "source_sha_verified": True,
        "new_image_generation_calls": 0, "human_visual_approved": False,
        "official_video_approved": False, "shots": [], "verified_count": len(verified),
    }
    for shot, (relative_mother, _, _) in source.SOURCES.items():
        with Image.open(source.EP / relative_mother) as im:
            mother = im.convert("RGB")
        with Image.open(source.EP / "assets/planos" / shot / "background-inpaint-technical.png") as im:
            composite = im.convert("RGBA")
        if mother.size != (SOURCE_WIDTH, SOURCE_HEIGHT) or composite.size != mother.size:
            raise C12QAError("NEUTRAL_SOURCE_CANVAS_MISMATCH:" + shot)
        for name in source.SHOT_PARTS[shot]:
            part = parts[name]
            x, y, w, h = source.bbox(part["polygon"])
            path = source.EP / "assets/planos" / shot / (name + ".png")
            with Image.open(path) as im:
                sprite = im.convert("RGBA")
            if sprite.size != (w, h):
                raise C12QAError("NEUTRAL_LAYER_BBOX_MISMATCH:" + name)
            composite.alpha_composite(sprite, dest=(x, y))
        mae, over16 = neutral_difference(mother, composite.convert("RGB"))
        # Conservative automated fidelity thresholds. The previous local
        # technical QA recorded ~0.0009/10 and ~0.0069/77 respectively.
        # Passing these bounds still cannot certify skin, hair or seams.
        shot_result = {
            "shot": shot, "mean_absolute_rgb_error": round(mae, 8),
            "pixels_any_channel_delta_gt16": over16,
            "max_automatic_mae": 0.15, "max_automatic_bad_pixels": 500,
            "passed_automatic_neutral_gate": mae <= 0.15 and over16 <= 500,
            "human_mask_qa_passed": False, "hidden_region_qa_passed": False,
        }
        result["shots"].append(shot_result)
    result["status"] = ("TECHNICAL_NEUTRAL_OK_NOT_HUMAN_APPROVED"
                        if all(x["passed_automatic_neutral_gate"] for x in result["shots"])
                        else "REJECTED_NEUTRAL_RECOMPOSITION")
    (out / "neutral.qa.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    if result["status"].startswith("REJECTED"):
        raise C12QAError("C12_NEUTRAL_RECOMPOSITION_REJECTED")
    return result


def project_boxes(native_boxes: list[list[int]], *,
                  output_width: int = WIDTH, output_height: int = HEIGHT,
                  source_width: int = SOURCE_WIDTH, source_height: int = SOURCE_HEIGHT,
                  padding: int = 24) -> list[tuple[int, int, int, int]]:
    """Project original PNG bbox to Remotion object-fit:cover/ThreeCanvas view."""
    if min(output_width, output_height, source_width, source_height) <= 0:
        raise C12QAError("PROJECT_INVALID_CANVAS")
    scale = max(output_width / source_width, output_height / source_height)
    dx = (output_width - source_width * scale) / 2
    dy = (output_height - source_height * scale) / 2
    projected = []
    for item in native_boxes:
        if len(item) != 4 or item[2] < 1 or item[3] < 1:
            raise C12QAError("PROJECT_INVALID_BOX")
        x, y, w, h = item
        projected.append((
            max(0, math.floor(dx + x * scale) - padding),
            max(0, math.floor(dy + y * scale) - padding),
            min(output_width, math.ceil(dx + (x + w) * scale) + padding),
            min(output_height, math.ceil(dy + (y + h) * scale) + padding),
        ))
    return projected


def measure_local_motion(frame_a: bytes, frame_b: bytes,
                         width: int, height: int,
                         boxes: list[tuple[int, int, int, int]],
                         *, min_channel_delta: int = 16) -> dict:
    """Count changed RGB pixels, independently within and outside moving parts.

    Treating the whole image as one moving sprite will produce substantial
    changes outside sprite boxes and must be rejected.
    """
    expected = width * height * 3
    if len(frame_a) != expected or len(frame_b) != expected or not boxes:
        raise C12QAError("MOTION_FRAME_OR_ROI_INVALID")
    inside = outside = 0
    for y in range(height):
        for x in range(width):
            i = 3 * (y * width + x)
            if (abs(frame_a[i] - frame_b[i]) <= min_channel_delta and
                abs(frame_a[i + 1] - frame_b[i + 1]) <= min_channel_delta and
                abs(frame_a[i + 2] - frame_b[i + 2]) <= min_channel_delta):
                continue
            in_region = any(x0 <= x < x1 and y0 <= y < y1 for x0, y0, x1, y1 in boxes)
            if in_region:
                inside += 1
            else:
                outside += 1
    # At least 30 visibly changed pixels in real decoded MP4; reject global
    # motion outside the moving RGBA meshes, allowing codec-block variation.
    allowed_outside = max(128, int(inside * 0.35))
    return {
        "changed_pixels_inside_original_sprite_rois": inside,
        "changed_pixels_outside_original_sprite_rois": outside,
        "max_allowed_outside": allowed_outside,
        "passed_localized_motion": inside >= 30 and outside <= allowed_outside,
    }


def _run(command: list[str], *, binary=False):
    try:
        finished = subprocess.run(command, capture_output=True,
                                  text=not binary, timeout=120, check=True)
    except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        raise C12QAError("FFMPEG_OR_FFPROBE_FAILED:" + str(exc)) from exc
    return finished.stdout


def _decode(mp4: Path) -> dict[int, bytes]:
    selected = "+".join("eq(n\\," + str(frame) + ")" for frame in SELECTED)
    raw = _run([
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-i", str(mp4), "-an", "-vf", "select=" + selected,
        "-fps_mode", "vfr", "-frames:v", str(len(SELECTED)),
        "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1",
    ], binary=True)
    stride = WIDTH * HEIGHT * 3
    if len(raw) != stride * len(SELECTED):
        raise C12QAError("C12_MP4_SELECTED_FRAMES_MISSING")
    return {frame: raw[i*stride:(i+1)*stride] for i, frame in enumerate(SELECTED)}


def verify_mp4(out: Path) -> dict:
    """Validate codec AND visible localized motion decoded from output MP4."""
    out.mkdir(parents=True, exist_ok=True)
    mp4 = out / "c12-three-mesh-8s.mp4"
    props_path = out / "props.json"
    neutral_path = out / "neutral.qa.json"
    preflight_path = out / "preflight.qa.json"
    if not mp4.is_file() or not props_path.is_file() or not neutral_path.is_file() or not preflight_path.is_file():
        raise C12QAError("MP4_QA_MISSING_REQUIRED_REAL_PREVIEW_OR_PROVENANCE")
    preflight = json.loads(preflight_path.read_text(encoding="utf8"))
    neutral_report = json.loads(neutral_path.read_text(encoding="utf8"))
    props = json.loads(props_path.read_text(encoding="utf8"))
    if (preflight.get("status") != "READY_FOR_TECHNICAL_THREECANVAS_RENDER"
        or neutral_report.get("status") != "TECHNICAL_NEUTRAL_OK_NOT_HUMAN_APPROVED"
        or neutral_report.get("verified_count") != 9
        or props.get("sourceOriginalsArchived") is not True
        or props.get("officialVideoApproved") is not False
        or props.get("expectedMeshTriangles") != 512
        or len(props.get("shots", [])) != 2):
        raise C12QAError("MP4_QA_SOURCE_OR_NEUTRAL_GATE_NOT_PASSED")
    if mp4.stat().st_size < 30000:
        raise C12QAError("MP4_QA_EMPTY_MP4")
    details = json.loads(_run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_name,codec_type,pix_fmt,width,height,r_frame_rate,nb_frames",
        "-of", "json", str(mp4),
    ]))
    videos = [stream for stream in details.get("streams", []) if stream.get("codec_type") == "video"]
    if len(videos) != 1 or any(stream.get("codec_type") == "audio" for stream in details.get("streams", [])):
        raise C12QAError("MP4_QA_VIDEO_ONLY_REQUIRED")
    stream = videos[0]
    if (stream.get("codec_name") != "h264" or stream.get("pix_fmt") != "yuv420p"
        or (stream.get("width"), stream.get("height")) != (WIDTH, HEIGHT)
        or stream.get("r_frame_rate") != "30/1"
        or stream.get("nb_frames") not in ("240", 240)
        or not 7.95 <= float(details.get("format", {}).get("duration", 0)) <= 8.12):
        raise C12QAError("MP4_QA_CODEC_FPS_FRAMES_OR_DURATION_INVALID")
    for n in STILLS:
        path = out / ("frame-" + str(n) + ".png")
        if not path.is_file() or path.stat().st_size < 1000:
            raise C12QAError("MP4_QA_MISSING_STILL_FRAME:" + str(n))
    repeat_shas = {}
    for n in REPEAT:
        main = out / ("frame-" + str(n) + ".png")
        repeat = out / ("frame-" + str(n) + "-repeat.png")
        if not repeat.is_file() or _sha(main) != _sha(repeat):
            raise C12QAError("MP4_QA_NONDETERMINISTIC_REMOTION_FRAME:" + str(n))
        repeat_shas[str(n)] = _sha(main)
    frames = _decode(mp4)
    mesh_info = source.plan()["meshParts"]
    motion = []
    for shot, start, end in (("C12-P02", 0, 73), ("C12-P03", 120, 180)):
        rectangles = [source.bbox(part["polygon"]) for part in mesh_info if part["shot"] == shot]
        boxes = project_boxes(rectangles)
        report = measure_local_motion(frames[start], frames[end], WIDTH, HEIGHT, boxes)
        report.update({"shot": shot, "frame_start": start, "frame_end": end,
                       "moving_rgba_mesh_count": len(rectangles)})
        motion.append(report)
    result = {
        "schema": "videoforge/c12-threecanvas-localized-motion-mp4-qa/v2",
        "status": "TECHNICAL_ONLY_LOCAL_MOTION_OK" if all(x["passed_localized_motion"] for x in motion)
                  else "REJECTED_STATIC_OR_GLOBAL_ANIMATION",
        "file": mp4.name, "sha256": _sha(mp4),
        "frames": FRAMES, "fps": FPS, "resolution": [WIDTH, HEIGHT],
        "codec": "h264", "pixel_format": "yuv420p",
        "mesh_triangles": 512, "independent_rgba_parts": 5,
        "source_sha_verified": True,
        "neutral_recomposition_automated_passed": True,
        "localized_motion_decoded_from_mp4": motion,
        "deterministic_frame_sha256": repeat_shas,
        "image_generation_calls": 0,
        "human_visual_approved": False, "video_oficial_do_programa": False,
        "youtube_uploaded": False, "preview_tecnico_nao_oficial": True,
    }
    (out / "mp4.qa.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    if result["status"].startswith("REJECTED"):
        raise C12QAError("MP4_QA_STATIC_OR_GLOBAL_ANIMATION_REJECTED")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("neutral", "mp4"))
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        result = neutral(args.output.resolve()) if args.mode == "neutral" else verify_mp4(args.output.resolve())
    except (C12QAError, source.AssetGateError, OSError, ValueError) as exc:
        print("C12_TECHNICAL_QA_BLOCKED", str(exc))
        return 2
    print("C12_TECHNICAL_QA_OK", json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
