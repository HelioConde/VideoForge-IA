"""EP01 C01-P04 V3: generate NEW independent artwork from creator-approved mother.

No pixel segmentation, no crop of mother, no sprite tracing. Each provider
call creates exactly one opaque background or RGBA full-canvas part.
Original V3 and one-row-aligned reference are immutable and SHA-verified.
New artwork requires individual human QA before rig/rendering.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import sys

from . import image_generation_policy, proxy_images
from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO, validate as validate_plan
from .ep01_align_throne_v3 import approved_original, already_archived, SOURCE_SHA
from .ep01_proxy_separate_parts import _reference_bible
from .scene_layers import png_info

PRODUCER = "production-c01p04-approved-v3-independent-parts"
SCHEMA = "videoforge/ep01-c01p04-approved-v3-independent-part/v1"
SHOT = "C01-P04"
ROLE_CONFIG = {
    "background-clean": {
        "role":"background",
        "prompt":(
            "Generate the completely EMPTY THRONE ROOM of this same cinematic "
            "frame. Keep architecture, staircase, royal upholstered throne, "
            "banners, gold decoration, stained glass, light shafts, shiny floor "
            "and all background locations EXACTLY framed as in the reference. "
            "Remove Kael, king Aldric, both guards and both spears entirely; "
            "fully invent plausible hidden parts of steps, carpet and throne "
            "upholstery, with no ghost silhouettes, characters, floating items "
            "or cutout holes. Image must be opaque and full-canvas."),
    },
    "character-kael": {
        "role":"character",
        "prompt":(
            "ONLY Kael kneeling in the lower center foreground, physically "
            "facing UP the stairs TOWARD king/throne, three-quarter body/profile "
            "visible. Preserve exactly the same red cloak, armor, limb "
            "positions, knees and ground contact as the approved mother, with "
            "fully rendered missing cloth/back hidden behind his body. "
            "NO king, guards, spears, throne or background. Preserve the "
            "large transparent space around the small lower-central actor."),
    },
    "character-aldric": {
        "role":"character",
        "prompt":(
            "ONLY seated king Aldric at top of the central staircase, "
            "small and distant, with exact approved grey hair/beard, crown, "
            "red-and-gold royal clothing, fur mantle, arms and seated pose. "
            "He must retain his original small scale, XY coordinates, seat "
            "contact and silhouette. Do not render throne, stairs, guards, "
            "other characters or background. No enlarged royal portrait."),
    },
    "character-guarda_esquerdo": {
        "role":"character",
        "prompt":(
            "ONLY LEFT royal guard viewed in this exact shot, full matching "
            "plate armor, red plume and cape, on same left side/XY location, "
            "with the ORIGINAL arm and finger poses that grip shaft near "
            "base, but WITHOUT drawing the actual spear (it is generated "
            "separately). Fill hidden hand/gauntlet/anatomy coherently "
            "without adding extra fingers. Keep scale and feet unchanged. "
            "No throne, Kael, king, right guard or scene background."),
    },
    "character-guarda_direito": {
        "role":"character",
        "prompt":(
            "ONLY RIGHT royal guard, same armor, red plume and cape, in "
            "the EXACT right-side location, pose and original scale. Hands "
            "keep natural wrapped-grip position at lower spear shaft/base, "
            "but do NOT draw the spear: it is an independent layer. "
            "Reconstruct hidden hand geometry without disconnected limbs. "
            "No Kael, king, left guard or background."),
    },
    "object-lanca-esquerda": {
        "role":"object",
        "prompt":(
            "ONLY the LEFT guard's single long spear as one independent "
            "rigid straight object, at the EXACT same diagonal XY coordinates "
            "and length as the left-side guard's spear in approved image. "
            "Handle/shaft EXTENDS to the lower-third held in left guard's "
            "gauntlets; upper sharp tip creates one half of a high X above "
            "Kael, not an X by itself. Draw no hand, guard, or other spear. "
            "Preserve original metal tip and wood material. No background."),
    },
    "object-lanca-direita": {
        "role":"object",
        "prompt":(
            "ONLY the RIGHT guard's single spear, in the exact approved "
            "diagonal XY position, canon wood shaft and gold metal blade "
            "with same length/angle as original. Lower third/base aligns to "
            "right guard's closed fingers, spearhead crosses left spear's "
            "imaginary location HIGH above Kael. No second spear, hands, "
            "characters or background. The whole spear must be rigid "
            "and connected, with true alpha outside."),
    },
}

def path_of_part(part: str) -> str:
    return "c01-p04-v3-" + part

def aligned_source(root: Path = ROOT) -> dict:
    root = Path(root)
    approved_original(root)
    existing = already_archived(root)
    if existing is None:
        raise VideoForgeError("EP01_APPROVED_V3_PARTS_MOTHER_ALIGNMENT_NOT_ARCHIVED")
    path = root / existing["file"]
    proof = path.with_suffix(".production.json")
    if any(p.is_symlink() or not p.is_file() for p in (path, proof)):
        raise VideoForgeError("EP01_APPROVED_V3_PARTS_ALIGNED_PROOF_MISSING")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    meta = json.loads(proof.read_text(encoding="utf-8"))
    if (digest != existing["sha256"]
            or meta.get("sha256") != digest
            or meta.get("source_image_sha256") != SOURCE_SHA
            or meta.get("source_pixels_unchanged") is not True
            or meta.get("pixel_qa") != "full_source_region_exact_and_bottom_row_identical"
            or meta.get("output_canvas") != [941,1672]
            or meta.get("human_visual_approval") is not False):
        raise VideoForgeError("EP01_APPROVED_V3_PARTS_ALIGNED_SHA_MISMATCH")
    details = png_info(raw, require_alpha=False)
    if (details["width"], details["height"]) != (941,1672):
        raise VideoForgeError("EP01_APPROVED_V3_PARTS_CANVAS_INVALID")
    return {"blob":raw,"sha256":digest,"path":existing["file"]}

def existing_part(part: str, root: Path = ROOT) -> dict | None:
    if part not in ROLE_CONFIG:
        raise VideoForgeError("EP01_APPROVED_V3_PART_UNKNOWN")
    repo = Path(root) / REL / "assets" / "geracoes" / PRODUCER
    if not repo.exists():
        return None
    if repo.is_symlink():
        raise VideoForgeError("EP01_APPROVED_V3_PART_ARCHIVE_SYMLINK")
    candidates = []
    stem = path_of_part(part)
    for run in repo.iterdir():
        if not run.is_dir() or not run.name.isdecimal():
            continue
        files = [run / (stem + ".png"), run / (stem + "-provider-native.png")]
        found = [file for file in files if file.exists()]
        if not found:
            continue
        manifest = run / "manifesto-geracoes.json"
        if not manifest.is_file() or manifest.is_symlink():
            raise VideoForgeError("EP01_APPROVED_V3_PART_ARCHIVE_INCOMPLETE")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("producer") != PRODUCER or data.get("github_run_id") != int(run.name):
            raise VideoForgeError("EP01_APPROVED_V3_PART_ARCHIVE_PROVENANCE_INVALID")
        for file in found:
            rows = [entry for entry in data.get("images", []) if entry.get("file") == file.name]
            if len(rows) != 1 or hashlib.sha256(file.read_bytes()).hexdigest() != rows[0].get("sha256"):
                raise VideoForgeError("EP01_APPROVED_V3_PART_ARCHIVED_SHA_MISMATCH")
        final = files[0] if files[0] in found else found[0]
        candidates.append({"run_id": int(run.name), "file": final.relative_to(root).as_posix(),
                           "sha256": hashlib.sha256(final.read_bytes()).hexdigest()})
    return max(candidates,key=lambda x:x["run_id"]) if candidates else None

def prepare(part: str, root: Path = ROOT) -> dict:
    root = Path(root)
    if part not in ROLE_CONFIG:
        raise VideoForgeError("EP01_APPROVED_V3_PART_NOT_REQUESTABLE")
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    validate_plan(root)
    if existing_part(part,root):
        raise VideoForgeError("EP01_APPROVED_V3_PART_ALREADY_ARCHIVED_NO_REPEAT")
    aligned = aligned_source(root)
    reference_images, reference_proofs = _reference_bible(SHOT, part, root)
    role = ROLE_CONFIG[part]["role"]
    prompt = (
        "Using IMAGE ONE (the source C01-P04 V3 APPROVED BY THE CREATOR, "
        "technically padded by one bottom row only) as an immutable precise "
        "composition reference, and SHA-verified Visual Bible images attached "
        "after it, generate ONE NEW INDEPENDENT full-frame PNG asset. "
        "NOT a crop, alpha-mask extraction, trace, segmentation, collage, "
        "new camera view, pose sheet, or character turnaround. "
        "The resulting art must match the exact pixel-scale placement, size, "
        "angle and lighting of the V3 scene from the 941x1672 portrait canvas "
        "while rendering ONLY the requested component with new pixels. "
        "No resizing, no recentering, no motion blur, no fake checkerboard "
        "transparency and no words/HUD. "
        + ROLE_CONFIG[part]["prompt"] + " "
        + ("BACKGROUND must be opaque and clean." if role=="background"
           else "Character/object output MUST have actual transparent RGBA alpha "
           "outside its silhouette (alpha zero); draw no room pixels. ")
        + "Correct anatomy and limb contact, no duplicated hands or spears. "
        "After output, human visual composition review is REQUIRED. "
        "No automatic rig, render, MP4 or YouTube upload."
    )
    if len(prompt) > 5000:
        raise VideoForgeError("EP01_APPROVED_V3_PART_PROMPT_TOO_LONG")
    return {"part": part, "role": role, "transparent": role!="background",
            "prompt":prompt, "source":aligned, "references":reference_images,
            "reference_proofs":reference_proofs,
            "images":[aligned["blob"],*reference_images]}

def validate_and_save(part: str, raw: bytes, root: Path, spec: dict) -> dict:
    from PIL import Image, ImageChops
    if part not in ROLE_CONFIG:
        raise VideoForgeError("EP01_APPROVED_V3_PART_NOT_ALLOWED")
    base = Path(root) / "output" / CHANNEL / "videos" / VIDEO / "imagens"
    stem = path_of_part(part)
    expected = [base / (stem + ext) for ext in
                (".png", ".production.json", "-provider-native.png",
                 "-provider-native.production.json")]
    if any(p.exists() or p.is_symlink() for p in expected):
        raise VideoForgeError("EP01_APPROVED_V3_PART_OUTPUT_EXISTS")
    with Image.open(BytesIO(raw)) as i:
        if i.format!="PNG":
            raise VideoForgeError("EP01_APPROVED_V3_PART_NON_PNG")
        i.load()
        image_mode = "RGBA" if "A" in i.getbands() else "RGB"
        img = i.convert(image_mode)
    role = ROLE_CONFIG[part]["role"]
    transparent = role != "background"
    qa_errors = []
    if transparent:
        if image_mode != "RGBA":
            qa_errors.append("missing_rgba_alpha")
        else:
            low,hi=img.getchannel("A").getextrema()
            if low!=0 or hi<128:
                qa_errors.append("invalid_or_empty_alpha")
    elif img.getbands() not in (("R","G","B"),("R","G","B","A")):
        qa_errors.append("background_invalid_channels")
    width,height=img.size
    # A newly generated transparent sprite may have a native canvas different
    # from the scene. Preserve its pixels and defer scale/anchor registration to
    # rig QA instead of falsifying a full-scene layer by resizing/cropping it.
    # This is NOT a technically ready same-canvas compositing layer.
    needs_registration = width!=941 or height not in (1671,1672)
    if needs_registration and not (512 <= width <= 2048 and 512 <= height <= 3072):
        qa_errors.append("implausible_native_canvas")
    base.mkdir(parents=True,exist_ok=True)
    # Store byte-exact provider image under its own name only when padding.
    original_digest = hashlib.sha256(raw).hexdigest()
    output_blob = raw
    postprocess = "none"
    native_file = None
    if not qa_errors and not needs_registration and height == 1671:
        native_file = base / (stem + "-provider-native.png")
        native_file.write_bytes(raw)
        if transparent:
            updated = Image.new("RGBA",(941,1672),(0,0,0,0))
        else:
            updated = Image.new("RGB",(941,1672),(0,0,0))
        updated.paste(img,(0,0))
        if not transparent:
            # Last opaque row is repeated; alpha parts instead receive
            # one fully transparent row. Both keep the 1671 source rows exact.
            updated.paste(img.crop((0,1670,941,1671)),(0,1671))
        if ImageChops.difference(updated.crop((0,0,941,1671)),img).getbbox():
            raise VideoForgeError("EP01_APPROVED_V3_PART_ALIGNMENT_CHANGED_PIXELS")
        buf=BytesIO()
        updated.save(buf,"PNG",optimize=True)
        output_blob=buf.getvalue()
        postprocess="append_one_row_without_resampling"
    # Always preserve a generated PNG even when QA fails. The archival step
    # persists it with the exact provider digest and a rejection status.
    dest = base / (stem + ".png")
    dest.write_bytes(output_blob)
    report = {
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "candidate_scene_shot_id":SHOT,"component":part,"asset_role":role,
        "asset_id":stem,"generation_method":"proxy_generated_separate_image",
        "not_a_pixel_cutout":True,
        "sha256":hashlib.sha256(output_blob).hexdigest(),
        "source_image_sha256":spec["source"]["sha256"],
        "approved_original_sha256":SOURCE_SHA,
        "source_originals_sha_verified":[
            {"asset_id":"c01-p04-scene-mother-facing-throne-v3-native-aligned",
             "sha256":spec["source"]["sha256"],"path":spec["source"]["path"]},
            *spec["reference_proofs"]],
        "provider_native_sha256":original_digest,
        "provider_native_dimensions":[width,height],
        "technical_postprocess":postprocess,
        "source_original_pixels_unchanged":True,
        "width":941 if postprocess!="none" else width,
        "height":1672 if postprocess!="none" else height,
        "transparent_alpha_required":transparent,
        "alpha_channel_checked":image_mode=="RGBA" if transparent else None,
        "technical_qa":(
            "rejected_"+",".join(qa_errors) if qa_errors
            else ("candidate_native_canvas_requires_spatial_registration"
                  if needs_registration
                  else "candidate_needs_visual_alignment_review")),
        "scene_canvas":[941,1672],
        "native_canvas_requires_spatial_registration":bool(needs_registration),
        "source_is_independent_sprite_not_mother_cutout":True,
        "placement_verified":False,"visual_recomposition_approved":False,
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "provider_image_calls":1,
    }
    (base/(stem+".production.json")).write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if native_file is not None:
        native_meta = dict(report)
        native_meta.update({"asset_id":stem+"-provider-native",
                            "sha256":original_digest,"width":width,"height":height,
                            "technical_postprocess":"none_raw_provider_preserved"})
        (base/(stem+"-provider-native.production.json")).write_text(
            json.dumps(native_meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_APPROVED_V3_PART",json.dumps(
        {"component":part,"sha256":report["sha256"],
         "native_sha256":original_digest,"technical_qa":report["technical_qa"],
         "provider_calls":1,"rig_ready":False},ensure_ascii=False))
    if qa_errors:
        raise VideoForgeError("EP01_APPROVED_V3_PART_REJECTED_BUT_ARCHIVE "+",".join(qa_errors))
    return report

def generate(part: str,url: str,root: Path = ROOT, model: str = "gpt-image-2") -> dict:
    if model!="gpt-image-2":
        raise VideoForgeError("EP01_APPROVED_V3_PART_MODEL_NOT_ALLOWED")
    spec=prepare(part,root)
    payload={
        "model":model,"n":1,"size":"1024x1536",
        "background":"transparent" if spec["transparent"] else "opaque",
        "prompt":spec["prompt"],"output_format":"png",
        "response_format":"b64_json","stream":False,
        "images":[{"image_url":"data:image/png;base64,"+base64.b64encode(b).decode("ascii")}
                  for b in spec["images"]],
    }
    result=proxy_images.call_proxy(url,"/v1/images/edits",
                                  os.getenv("CODEX_PROXY_API_KEY",""),payload)
    raw,ext=proxy_images.decode_image(result)
    if ext!=".png":
        raise VideoForgeError("EP01_APPROVED_V3_PART_PROVIDER_NOT_PNG")
    return validate_and_save(part,raw,root,spec)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--part",required=True,choices=ROLE_CONFIG.keys())
    parser.add_argument("--url",required=True)
    args=parser.parse_args()
    try:
        generate(args.part,args.url)
    except (VideoForgeError,ValueError,OSError,ImportError,proxy_images.ProxyImageError) as err:
        print("EP01_APPROVED_V3_PART_STOPPED",str(err),file=sys.stderr)
        sys.exit(2)

if __name__=="__main__":
    main()
