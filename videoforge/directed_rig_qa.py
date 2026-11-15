"""Review artifacts for directed rigs. Pixel diagnostics never approve artwork."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from .rig_candidate import _image, _write_png
from .directed_rig import _mask_uncovered


def neutral_review(bindings_path: Path, shot_id: str, output: Path) -> dict:
    """Compare existing sprites at their original coordinates with their mother."""
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    shot = bindings["shots"][shot_id]
    base = bindings_path.parent
    width, height = shot["canvas"]["width"], shot["canvas"]["height"]
    mother = _image(base / shot["sourceMother"]["file"], width, height)
    composite = _image(base / shot["background"]["file"], width, height)
    decoded = {node["id"]: _image(base / node["file"], width, height)
               for node in shot["nodes"] if "file" in node}
    for node in sorted(shot["nodes"], key=lambda item: item["z"]):
        if "file" not in node:
            continue
        pixels = decoded[node["id"]]
        if "onlyUncoveredBy" in node:
            pixels, _ = _mask_uncovered(pixels, [decoded[ref] for ref in node["onlyUncoveredBy"]])
        x, y, w, h = node["bbox"]
        for row in range(y, y + h):
            for col in range(x, x + w):
                offset = 4 * (row * width + col)
                alpha = pixels[offset + 3]
                if not alpha:
                    continue
                for channel in range(3):
                    composite[offset + channel] = (
                        pixels[offset + channel] * alpha
                        + composite[offset + channel] * (255 - alpha) + 127
                    ) // 255
                composite[offset + 3] = 255
    diff = bytearray(width * height * 4)
    changed, error = 0, 0
    for offset in range(0, len(mother), 4):
        delta = [abs(mother[offset + c] - composite[offset + c]) for c in range(3)]
        changed += any(delta)
        error += sum(delta)
        diff[offset:offset + 4] = bytes([min(255, d * 3) for d in delta] + [255])
    output.mkdir(parents=True, exist_ok=True)
    _write_png(output / "neutral-composite.png", composite, width, height)
    _write_png(output / "neutral-difference-x3.png", diff, width, height)
    # Three columns: original / neutral assembly / amplified difference.
    thumb_w, thumb_h = 256, round(height * 256 / width)
    sheet = bytearray(thumb_w * 3 * thumb_h * 4)
    for column, source in enumerate((mother, composite, diff)):
        for row in range(thumb_h):
            for x in range(thumb_w):
                src = 4 * ((row * height // thumb_h) * width + x * width // thumb_w)
                dst = 4 * (row * thumb_w * 3 + column * thumb_w + x)
                sheet[dst:dst + 4] = source[src:src + 4]
    _write_png(output / "neutral-contact-sheet.png", sheet, thumb_w * 3, thumb_h)
    report = {
        "schema": "videoforge/directed-rig-neutral-qa/v1", "shot": shot_id,
        "changedPixels": changed, "totalPixels": width * height,
        "meanAbsoluteRgbError": error / (width * height * 3),
        "pixelExactRecomposition": changed == 0,
        "comparison": "original mother / candidate neutral assembly / abs diff x3",
        "humanVisualReview": False, "publishable": False,
        "note": "Metrics do not validate anatomy, masks, pivots or narrative framing.",
    }
    (output / "neutral-qa.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def _video_frame(video: Path, frame: int, width: int, height: int) -> bytearray:
    raw = subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(video),
        "-vf", f"select=eq(n\\,{frame})", "-frames:v", "1", "-f", "rawvideo",
        "-pix_fmt", "rgba", "-",
    ], capture_output=True, check=True, timeout=60).stdout
    if len(raw) != width * height * 4:
        raise ValueError("DIRECTED_QA_DECODED_FRAME_MISMATCH")
    return bytearray(raw)


def c01_actor_motion_pixels(before: bytes | bytearray, after: bytes | bytearray,
                            shot: dict, width: int, height: int,
                            *, threshold: int = 24) -> dict:
    """Check actual H.264 movement around the articulated actor, not the UI.

    C01-P03 uses a locked z=14 / fov=30 camera. Source-to-video projection
    matches the calibrated renderer; no camera motion can count as rig motion.
    This is a technical signal, never visual/art approval.
    """
    if (len(before) != width*height*4 or len(after) != len(before)
            or width <= 0 or height <= 0):
        raise ValueError("C01_ACTING_RGBA_VIDEO_DIMENSIONS_INVALID")
    camera = shot.get("camera", {})
    keys = camera.get("keyframes", [])
    if (camera.get("move") != "locked"
        or camera.get("type") != "perspective_3d"
        or not keys
        or any(k.get("z") != 14 or k.get("fovDeg") != 30
               or k.get("lookAt") != [0,0,0] for k in keys)):
        raise ValueError("C01_ACTING_REQUIRES_LOCKED_CAMERA_AND_REAL_RIG")
    source = shot["canvas"]
    source_w, source_h = source["width"], source["height"]
    # This mapping is valid for the fixed C01 camera (z=14, fov 30,
    # lookAt origin) and the sourceWorldScale calibration in directed-rig-math.
    scale = height / min(source_h, source_w / (width/height))
    offset_x = (width-source_w*scale)/2
    offset_y = (height-source_h*scale)/2
    nodes = [n for n in shot["nodes"]
             if n["id"].startswith("kael.") and "bbox" in n]
    if len(nodes) < 8:
        raise ValueError("C01_ACTING_INDEPENDENT_KAEL_SPRITES_REQUIRED")
    minx = min(n["bbox"][0] for n in nodes)
    miny = min(n["bbox"][1] for n in nodes)
    maxx = max(n["bbox"][0]+n["bbox"][2] for n in nodes)
    maxy = max(n["bbox"][1]+n["bbox"][3] for n in nodes)
    x0 = max(0, int(minx*scale + offset_x)-18)
    x1 = min(width, int(maxx*scale + offset_x)+19)
    y0 = max(height//8, int(miny*scale + offset_y)-18)
    y1 = min(height - min(240, height//8), int(maxy*scale+offset_y)+19)
    if x1 <= x0 or y1 <= y0:
        raise ValueError("C01_ACTING_EMPTY_CHARACTER_ROI")
    changed = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            i = (y*width + x)*4
            if max(abs(before[i+j] - after[i+j]) for j in range(3)) >= threshold:
                changed += 1
    return {
        "source": "decoded_real_h264_frames",
        "scope": "Kael character source rectangles only, no UI or camera movement",
        "source_frame_baseline": 0,
        "roi_output_px": [x0,y0,x1,y1],
        "changed_pixels_min_rgb_delta": threshold,
        "changed_pixels": changed,
        "human_visual_review": False,
    }


def verify_render(props_path: Path, output: Path) -> dict:
    props = json.loads(props_path.read_text(encoding="utf-8"))
    if (props.get("schema") != "videoforge/directed-rig-preview/v1"
            or props.get("mode") != "technical_draft"
            or props.get("publishable") is not False
            or props.get("humanVisualReview") is not False):
        raise ValueError("DIRECTED_QA_DRAFT_FLAGS_REQUIRED")
    video = output / "directed-rig-preview.mp4"
    probe = json.loads(subprocess.run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)
    ], check=True, capture_output=True, text=True, timeout=60).stdout)
    videos = [s for s in probe["streams"] if s["codec_type"] == "video"]
    if len(videos) != 1:
        raise ValueError("DIRECTED_QA_VIDEO_STREAM_REQUIRED")
    stream = videos[0]
    numerator, denominator = map(int, stream["r_frame_rate"].split("/"))
    if (stream["codec_name"] != "h264" or stream["pix_fmt"] != "yuv420p"
            or stream["width"] != props["width"] or stream["height"] != props["height"]
            or numerator / denominator != props["fps"]
            or int(stream["nb_frames"]) != props["durationFrames"]):
        raise ValueError("DIRECTED_QA_VIDEO_FORMAT_MISMATCH")
    frame_mid = min(30, props["durationFrames"] - 1)
    first = output / "frame-0.png"
    middle = output / f"frame-{frame_mid}.png"
    repeated = output / "frame-repeat.png"
    if middle.read_bytes() != repeated.read_bytes():
        raise ValueError("DIRECTED_QA_NONDETERMINISTIC_FRAME")
    width, height = props["width"], props["height"]
    before, after = _image(first, width, height), _image(middle, width, height)
    # Exclude the fixed banner and changing frame label. UI must not count as rig motion.
    margin = min(240, height // 4)
    changed = sum(before[i:i + 3] != after[i:i + 3]
                  for i in range(margin * width * 4, (height - margin) * width * 4, 4))
    if changed <= 50:
        raise ValueError("DIRECTED_QA_NO_ART_MOTION")
    video_before = _video_frame(video, 0, width, height)
    video_after = _video_frame(video, frame_mid, width, height)
    changed_video = sum(
        max(abs(video_before[i + c] - video_after[i + c]) for c in range(3)) >= 8
        for i in range(margin * width * 4, (height - margin) * width * 4, 4)
    )
    if changed_video <= 50:
        raise ValueError("DIRECTED_QA_NO_MP4_ART_MOTION")
    c01_actor = None
    if props.get("id") == "C01-P03" and props.get("channel") == "alchemy-lab":
        # Unlike the old 50-pixel check, this detects whether the acting
        # remains imperceptible in the actual encoded video at the second beat.
        frame_lift = min(75, props["durationFrames"]-1)
        c01_actor = c01_actor_motion_pixels(
            video_before, _video_frame(video, frame_lift, width, height),
            props["shots"][0], width, height, threshold=24)
        c01_actor["source_frame_performance"] = frame_lift
        c01_actor["min_changed_pixels"] = 16000
        c01_actor["technical_perceptible_motion"] = c01_actor["changed_pixels"] >= 16000
        if not c01_actor["technical_perceptible_motion"]:
            raise ValueError("C01_ACTING_STILL_TOO_SUBTLE_IN_REAL_MP4")
    audio = any(s["codec_type"] == "audio" for s in probe["streams"])
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(output.iterdir()) if p.is_file() and p.suffix in (".png", ".mp4")}
    report = {
        "schema": "videoforge/directed-rig-render-qa/v1",
        "channel": props["channel"], "video_id": props["videoId"],
        "run_id": os.environ.get("GITHUB_RUN_ID"), "commit": os.environ.get("GITHUB_SHA"),
        "format": {k: stream[k] for k in ("codec_name", "pix_fmt", "width", "height", "r_frame_rate", "nb_frames")},
        "audioPresent": audio, "deterministicRepeatedFrame": frame_mid,
        "changedArtPixelsAtFrame": {"frame": frame_mid, "pixels": changed},
        "changedMp4ArtPixelsAtFrame": {"frame": frame_mid, "pixels": changed_video, "minRgbDelta": 8},
        "c01ArticulatedActorMotion": c01_actor,
        "sha256": hashes, "warnings": props["warnings"],
        "pixelRecovery": props.get("pixelRecovery", []),
        "imageGenerationCalls": 0, "previewTecnicoNaoOficial": True,
        "rigProductionReady": False, "humanVisualReview": False,
        "publishable": False, "videoOficialDoPrograma": False, "youtubeUploaded": False,
    }
    (output / "render-qa.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("neutral", "verify"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--shot")
    parser.add_argument("--props", type=Path)
    args = parser.parse_args()
    if args.command == "neutral":
        if not args.bindings or not args.shot:
            parser.error("neutral requires --bindings and --shot after directed_rig prepare")
        result = neutral_review(args.bindings, args.shot, args.output_dir)
    else:
        if not args.props:
            parser.error("verify requires --props")
        result = verify_render(args.props, args.output_dir)
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
