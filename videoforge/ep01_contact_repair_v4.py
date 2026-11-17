"""V4 contact-only candidate from SHA-verified V3 patch. Never approves render."""
from __future__ import annotations
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys

from . import image_generation_policy, proxy_images
from .errors import VideoForgeError
from .ep01_contact_repair import read_owner_review, EXPECTED_MOTHER_SHA, ROI
from .layered_shot_plan import CHANNEL, VIDEO, REL, ROOT
from .scene_layers import png_info

V3_ASSET = "c01-p02-contact-local-patch-v3"
V3_SHA = "17da28fcf733727a11d2d67a38a84611bd1192cff0e97d45d7db10169de9089d"
ASSET = "c01-p02-contact-detail-v4"
PATCH_ASSET = "c01-p02-contact-local-patch-v4"
PRODUCER = "production-contact-repair-v4"
SCHEMA = "videoforge/ep01-contact-repair-candidate/v2"
MAX_BYTES = 32_000_000


def _registered_v3(root: Path) -> tuple[bytes, str]:
    index = root / "canal" / CHANNEL / "biblia-visual" / "REGISTRO-GERACOES.json"
    registry = json.loads(index.read_text(encoding="utf-8"))
    entries = [r for r in registry.get("geracoes", []) if r.get("asset") == V3_ASSET]
    if len(entries) != 1:
        raise VideoForgeError("EP01_V4_V3_REFERENCE_MISSING_OR_AMBIGUOUS")
    row = entries[0]
    rel = Path(row["arquivo"])
    folder = REL / "assets" / "geracoes" / "production-contact-repair-v3"
    if (rel.is_absolute() or ".." in rel.parts or
            not rel.is_relative_to(folder) or
            (row.get("sha256"), row.get("width"), row.get("height")) != (V3_SHA, 941, 1672)):
        raise VideoForgeError("EP01_V4_V3_REGISTRY_INVALID")
    file = root / rel
    proof_file = file.with_suffix(".production.json")
    if (file.is_symlink() or proof_file.is_symlink() or
            not file.is_file() or not proof_file.is_file()):
        raise VideoForgeError("EP01_V4_V3_FILE_MISSING")
    raw = file.read_bytes()
    proof = json.loads(proof_file.read_text(encoding="utf-8"))
    if (hashlib.sha256(raw).hexdigest() != V3_SHA or
            png_info(raw, require_alpha=False)["width"] != 941 or
            png_info(raw, require_alpha=False)["height"] != 1672 or
            proof.get("sha256") != V3_SHA or
            proof.get("source_mother_sha256") != EXPECTED_MOTHER_SHA or
            proof.get("human_visual_approval") is not False):
        raise VideoForgeError("EP01_V4_V3_REFERENCE_TAMPERED")
    return raw, rel.as_posix()


def archived_candidate(root: Path = ROOT) -> dict | None:
    folder = Path(root) / REL / "assets" / "geracoes" / PRODUCER
    if folder.is_symlink():
        raise VideoForgeError("EP01_V4_ARCHIVE_SYMLINK")
    if not folder.exists():
        return None
    found = []
    for run in folder.iterdir():
        if run.is_symlink():
            raise VideoForgeError("EP01_V4_ARCHIVE_RUN_SYMLINK")
        if not run.is_dir() or not run.name.isdecimal():
            continue
        file = run / (ASSET + ".png")
        manifest = run / "manifesto-geracoes.json"
        if file.exists():
            if (file.is_symlink() or manifest.is_symlink() or not manifest.is_file()):
                raise VideoForgeError("EP01_V4_ARCHIVE_INVALID")
            data = json.loads(manifest.read_text(encoding="utf-8"))
            matches = [x for x in data.get("images", []) if x.get("file") == file.name]
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            if (len(matches) != 1 or matches[0].get("sha256") != digest or
                    data.get("producer") != PRODUCER or
                    data.get("github_run_id") != int(run.name)):
                raise VideoForgeError("EP01_V4_ARCHIVE_HASH_MISMATCH")
            found.append({"run_id": int(run.name), "sha256": digest})
    return max(found, key=lambda x: x["run_id"]) if found else None


def prepare(root: Path = ROOT) -> dict:
    root = Path(root)
    read_owner_review(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL, VIDEO, root)
    raw, source_path = _registered_v3(root)
    if archived_candidate(root):
        raise VideoForgeError("EP01_V4_ALREADY_ARCHIVED")
    prompt = (
        "Edit the ATTACHED EXISTING image only: cinematic semi-realistic medieval "
        "fantasy anime. Output one frame, identical vertical composition, no layout "
        "or reference sheet. This is a precise anatomical repair, not a redesign. "
        "Keep face, hands count, costume, lighting, stairs, throne, camera, "
        "upper glove and sword hilt, original sword guard, gold decorations, "
        "body size, and background IDENTICAL to input. "
        "Focus ONLY on the lower gloved hand gripping the wine-red leather "
        "scabbard, the ornate scabbard mouth and the lower section of the exposed "
        "blade. The BLADE MUST PHYSICALLY ENTER the actual open mouth of the "
        "scabbard along ONE continuous straight axis. No solid decorative plate "
        "between blade and entry slot, no blade crossing leather or gold rim, "
        "no blade resting alongside the sheath, no extra or disconnected tip. "
        "The scabbard is entirely OUTSIDE and IN FRONT of the coat and its folds. "
        "The lower gloved fingers curl naturally AROUND the visible scabbard, "
        "with plausible knuckles and continuous contact: fingertips on its near "
        "surface and palm behind it, wrist connected to the arm. The upper hand "
        "stays firmly on the sword's grip. No extra fingers, hands, scabbards, "
        "weapons, floating components or doubled edges. Preserve matching "
        "perspective, blade width and metallic reflections, no perspective change. "
        "Change as few pixels as possible. Do not move objects as whole cutouts "
        "or stretch them. Keep everything outside lower-right contact region "
        "unchanged. No text, logo or captions. This is candidate V4 only, never "
        "a human-approved animation source."
    )
    return {"source_sha256": V3_SHA, "source_path": source_path,
            "original": raw, "width": 941, "height": 1672,
            "prompt": prompt, "roi": ROI}


def generate(url: str, model: str = "gpt-image-2", root: Path = ROOT) -> dict:
    root = Path(root)
    if model != "gpt-image-2":
        raise VideoForgeError("EP01_V4_MODEL_NOT_ALLOWED")
    spec = prepare(root)
    folder = root / "output" / CHANNEL / "videos" / VIDEO / "imagens"
    if folder.is_symlink() or (folder.exists() and any(folder.iterdir())):
        raise VideoForgeError("EP01_V4_OUTPUT_NOT_EMPTY")
    response = proxy_images.call_proxy(
        url, "/v1/images/edits", os.getenv("CODEX_PROXY_API_KEY", ""),
        {"model": model, "prompt": spec["prompt"], "n": 1,
         "size": "1024x1536", "background": "opaque",
         "output_format": "png", "response_format": "b64_json",
         "stream": False, "images": [{"image_url": "data:image/png;base64," +
                           base64.b64encode(spec["original"]).decode("ascii")}]})
    raw, ext = proxy_images.decode_image(response)
    if ext != ".png" or not 64 <= len(raw) <= MAX_BYTES:
        raise VideoForgeError("EP01_V4_RETURNED_INVALID_PNG")
    dim = png_info(raw, require_alpha=False)
    native = (dim["width"], dim["height"]) == (941, 1672)
    folder.mkdir(parents=True, exist_ok=True)
    edit_path = folder / (ASSET + ".png")
    edit_path.write_bytes(raw)
    edit_sha = hashlib.sha256(raw).hexdigest()
    entries = [{
        "schema": SCHEMA, "channel": CHANNEL, "video_id": VIDEO,
        "asset_id": ASSET, "candidate_scene_shot_id": "C01-P02",
        "sha256": edit_sha, "source_image_sha256": V3_SHA,
        "source_originals_sha_verified": [
            {"id": V3_ASSET, "path": spec["source_path"], "sha256": V3_SHA}],
        "source_ancestor_v1_sha256": EXPECTED_MOTHER_SHA,
        "source_canvas": [941, 1672],
        "new_canvas": [dim["width"], dim["height"]],
        "same_canvas": native, "source_unchanged": True,
        "human_visual_approval": False, "rig_authorized": False,
        "mp4_generated": False, "youtube_uploaded": False,
        "provider_image_calls": 1,
        "technical_qa": "candidate_requires_visual_review"
    }]
    if native:
        from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat
        with Image.open(io.BytesIO(spec["original"])) as im:
            before = im.convert("RGB")
        with Image.open(io.BytesIO(raw)) as im:
            after = im.convert("RGB")
        opacity = Image.new("L", before.size, 0)
        l, t, r, b = ROI
        ImageDraw.Draw(opacity).rectangle((l+18, t+18, r-18, b-18), fill=255)
        opacity = opacity.filter(ImageFilter.GaussianBlur(radius=17))
        fence = Image.new("L", before.size, 0)
        ImageDraw.Draw(fence).rectangle(ROI, fill=255)
        opacity = ImageChops.multiply(opacity, fence)
        patched = Image.composite(after, before, opacity)
        exclusion = Image.new("L", before.size, 255)
        ImageDraw.Draw(exclusion).rectangle(ROI, fill=0)
        diff = ImageChops.difference(before, patched)
        if ImageChops.multiply(diff.convert("L"), exclusion).getbbox():
            raise VideoForgeError("EP01_V4_PIXELS_CHANGED_OUTSIDE_ROI")
        patch_path = folder / (PATCH_ASSET + ".png")
        patched.save(patch_path, "PNG", optimize=True)
        patch_sha = hashlib.sha256(patch_path.read_bytes()).hexdigest()
        entries.append({
            "schema": SCHEMA, "channel": CHANNEL, "video_id": VIDEO,
            "asset_id": PATCH_ASSET, "candidate_scene_shot_id": "C01-P02",
            "sha256": patch_sha, "source_image_sha256": V3_SHA,
            "source_originals_sha_verified": [
                {"id": V3_ASSET, "path": spec["source_path"], "sha256": V3_SHA},
                {"id": ASSET, "path": edit_path.relative_to(root).as_posix(),
                 "sha256": edit_sha}],
            "source_ancestor_v1_sha256": EXPECTED_MOTHER_SHA,
            "crop_roi": list(ROI), "source_unrelated_pixels_retained": True,
            "mean_rgb_difference_from_v3_patch": round(
                sum(ImageStat.Stat(diff).mean)/3, 4),
            "no_spatial_resampling": True,
            "human_visual_approval": False, "rig_authorized": False,
            "mp4_generated": False, "youtube_uploaded": False,
            "provider_image_calls": 0,
            "technical_qa": "local_edit_candidate_not_approved"
        })
    for entry in entries:
        (folder / (entry["asset_id"] + ".production.json")).write_text(
            json.dumps(entry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    print("EP01_V4_CONTACT_CANDIDATE", json.dumps({
        "source": V3_SHA, "candidate": edit_sha, "same_canvas": native,
        "assets": [x["asset_id"] for x in entries],
        "human_approved": False, "provider_calls": 1}))
    return entries[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    try:
        generate(args.url)
    except (OSError, ValueError, VideoForgeError, proxy_images.ProxyImageError) as exc:
        print("EP01_V4_CONTACT_REPAIR_STOPPED", str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
