"""Versioned second attempt for Aldric C01-P04 approved V3.

First Aldric independent proxy candidate (run 44158759629) was archived,
but rejected for generating 1200x1310 instead of the 941x1672 shot canvas.
This tool makes exactly ONE NEW image using approved mother + Bible references.
Do not crop/resize rejected candidate into a false passing sprite.
"""
from __future__ import annotations

import base64
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import sys

from . import image_generation_policy, proxy_images
from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from .ep01_approved_v3_parts import aligned_source
from .ep01_proxy_separate_parts import _reference_bible
from .scene_layers import png_info

PART = "character-aldric"
SHOT = "C01-P04"
SOURCE_RUN = 44158759629
SOURCE_PRODUCER = "production-c01p04-approved-v3-independent-parts"
REJECTED_ASSET = "c01-p04-v3-character-aldric"
REJECTED_SHA = "934e2129e0d42db47610eff327d37d6b369d4a2258e53f7997edef4314a32828"
PRODUCER = "production-c01p04-v3-independent-parts-repair-v2"
ASSET = "c01-p04-v3-character-aldric-repair-v2"
SCHEMA = "videoforge/ep01-c01p04-approved-v3-aldric-repair/v2"

def rejected_original(root: Path = ROOT) -> dict:
    relative = REL / "assets" / "geracoes" / SOURCE_PRODUCER / str(SOURCE_RUN) / (REJECTED_ASSET + ".png")
    file = Path(root) / relative
    proof = file.with_suffix(".production.json")
    manifest = file.parent / "manifesto-geracoes.json"
    if any(p.is_symlink() or not p.is_file() for p in (file,proof,manifest)):
        raise VideoForgeError("EP01_ALDRIC_REPAIR_REJECTED_INPUT_MISSING")
    blob = file.read_bytes()
    doc = json.loads(proof.read_text(encoding="utf-8"))
    archive = json.loads(manifest.read_text(encoding="utf-8"))
    matching=[x for x in archive.get("images",[]) if x.get("file")==file.name]
    if (sha256(blob).hexdigest()!=REJECTED_SHA
        or doc.get("sha256")!=REJECTED_SHA
        or doc.get("candidate_scene_shot_id")!=SHOT
        or doc.get("component")!=PART
        or doc.get("technical_qa")!="rejected_unacceptable_canvas"
        or doc.get("provider_native_dimensions") != [1200,1310]
        or doc.get("human_visual_approval") is not False
        or doc.get("rig_ready") is not False
        or archive.get("producer")!=SOURCE_PRODUCER
        or archive.get("github_run_id")!=SOURCE_RUN
        or len(matching)!=1 or matching[0].get("sha256")!=REJECTED_SHA):
        raise VideoForgeError("EP01_ALDRIC_REPAIR_REJECTED_EVIDENCE_CHANGED")
    return {"sha256":REJECTED_SHA,"path":relative.as_posix(),"reason":"wrong_canvas_and_character_scale"}

def archived(root: Path = ROOT) -> dict | None:
    directory = Path(root)/REL/"assets"/"geracoes"/PRODUCER
    if not directory.exists():
        return None
    if directory.is_symlink():
        raise VideoForgeError("EP01_ALDRIC_REPAIR_ARCHIVE_SYMLINK")
    found=[]
    for run in directory.iterdir():
        if not run.is_dir() or not run.name.isdecimal():
            continue
        image=run/(ASSET+".png")
        if not image.exists():
            continue
        meta=image.with_suffix(".production.json")
        manifest=run/"manifesto-geracoes.json"
        if any(p.is_symlink() or not p.is_file() for p in (image,meta,manifest)):
            raise VideoForgeError("EP01_ALDRIC_REPAIR_ARCHIVE_INCOMPLETE")
        blob=image.read_bytes();digest=sha256(blob).hexdigest()
        m=json.loads(meta.read_text(encoding="utf-8"))
        a=json.loads(manifest.read_text(encoding="utf-8"))
        rows=[x for x in a.get("images",[]) if x.get("file")==image.name]
        if (m.get("sha256")!=digest or a.get("producer")!=PRODUCER
            or a.get("github_run_id")!=int(run.name)
            or len(rows)!=1 or rows[0].get("sha256")!=digest):
            raise VideoForgeError("EP01_ALDRIC_REPAIR_ARCHIVE_SHA_INVALID")
        found.append({"run_id":int(run.name),"sha256":digest,
                      "technical_qa":m.get("technical_qa"),
                      "file":image.relative_to(root).as_posix()})
    return max(found,key=lambda x:x["run_id"]) if found else None

def prepare(root:Path=ROOT) -> dict:
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if archived(root):
        raise VideoForgeError("EP01_ALDRIC_REPAIR_ALREADY_ARCHIVED_NO_REPEAT")
    reference=aligned_source(root)
    failed=rejected_original(root)
    raws,refs=_reference_bible(SHOT,PART,root)
    prompt=(
        "The FIRST image is the EXACT APPROVED 941x1672 WIDE THRONE ROOM "
        "cinematic portrait canvas. It is the absolute camera/layout template. "
        "Create ONE INDEPENDENT PNG RGBA of ONLY the KING ALDRIC from that "
        "same image, at the EXACT SAME SMALL size and XY coordinates: he is "
        "seated far away at the TOP CENTER OF THE RED CARPET STAIRS, on his "
        "central high throne. KING MUST REMAIN SMALL like the original. "
        "Output image framing is NOT a close-up, bust, portrait, card, "
        "turnaround, character design sheet or recentered person. "
        "Keep the ENTIRE 941x1672 9:16 canvas, all spaces outside "
        "the KING ALDRIC silhouette must be ACTUAL FULLY TRANSPARENT "
        "ALPHA=0, including the large blank area BELOW the royal seat. "
        "No throne, red steps, Kael, guards, spears, panels, backgrounds, "
        "checkerboard pixels, captions, watermarks or HUD. "
        "Retain the EXACT facial features, silver beard, crown, red/gold "
        "garments, fur mantle, sitting anatomy, relative lighting and "
        "occlusion to throne from image one and attached Visual Bible. "
        "THIS IS A NEW INDEPENDENT IMAGE, never a pixel crop or alpha "
        "segmentation of the approved source. Render missing body geometry "
        "to allow later motion, without changing visible parts. "
        "IMPORTANT: prior rejected attempt created 1200x1310 (different "
        "aspect and scale). DO NOT repeat this; return full 941x1672 "
        "canvas while king remains tiny and distant. The image is only "
        "a candidate for placement and alpha QA; NO rig or publication."
    )
    return {"source":reference,"rejected":failed,"refs":refs,
            "images":[reference["blob"],*raws],"prompt":prompt}

def generate(url:str,model:str="gpt-image-2",root:Path=ROOT) -> dict:
    from PIL import Image,ImageChops
    if model!="gpt-image-2":
        raise VideoForgeError("EP01_ALDRIC_REPAIR_MODEL_NOT_ALLOWED")
    root=Path(root)
    spec=prepare(root)
    payload={
        "model":model,"n":1,"size":"1024x1536","background":"transparent",
        "output_format":"png","response_format":"b64_json","stream":False,
        "prompt":spec["prompt"],
        "images":[{"image_url":"data:image/png;base64,"+
                  base64.b64encode(x).decode("ascii")} for x in spec["images"]],
    }
    reply=proxy_images.call_proxy(
        url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),payload)
    raw,ext=proxy_images.decode_image(reply)
    if ext!=".png":
        raise VideoForgeError("EP01_ALDRIC_REPAIR_NOT_PNG")
    with Image.open(BytesIO(raw)) as im:
        im.load()
        if im.format!="PNG":
            raise VideoForgeError("EP01_ALDRIC_REPAIR_BAD_PNG")
        rgba="A" in im.getbands()
        pix=im.convert("RGBA")
        dimensions=list(im.size)
    errors=[]
    if not rgba: errors.append("no_real_alpha")
    else:
        lo,hi=pix.getchannel("A").getextrema()
        if lo!=0 or hi<128:
            errors.append("invalid_or_empty_alpha")
    if dimensions[0]!=941 or dimensions[1] not in (1671,1672):
        errors.append("unacceptable_canvas")
    dest=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    img=dest/(ASSET+".png")
    proof=dest/(ASSET+".production.json")
    native=dest/(ASSET+"-provider-native.png")
    nproof=dest/(ASSET+"-provider-native.production.json")
    if any(x.is_symlink() or x.exists() for x in (img,proof,native,nproof)):
        raise VideoForgeError("EP01_ALDRIC_REPAIR_OUTPUT_EXISTS")
    dest.mkdir(parents=True,exist_ok=True)
    transformed=raw
    postprocess="none"
    if not errors and dimensions==[941,1671]:
        native.write_bytes(raw)
        extended=Image.new("RGBA",(941,1672),(0,0,0,0))
        extended.alpha_composite(pix,(0,0))
        if ImageChops.difference(extended.crop((0,0,941,1671)),pix).getbbox():
            raise VideoForgeError("EP01_ALDRIC_REPAIR_ALIGNMENT_CHANGED_PIXELS")
        buf=BytesIO();extended.save(buf,"PNG",optimize=True)
        transformed=buf.getvalue()
        postprocess="append_bottom_transparent_row_no_resize"
    img.write_bytes(transformed)
    final=sha256(transformed).hexdigest()
    report={
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "candidate_scene_shot_id":SHOT,"asset_id":ASSET,"component":PART,
        "generation_method":"proxy_generated_separate_image_new_revision",
        "not_a_pixel_cutout":True,
        "source_image_sha256":spec["source"]["sha256"],
        "approved_original_sha256":"a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd",
        "replaces_rejected_candidate_sha256":spec["rejected"]["sha256"],
        "sha256":final,"provider_native_sha256":sha256(raw).hexdigest(),
        "provider_native_dimensions":dimensions,
        "source_originals_sha_verified":[
            {"asset_id":"c01-p04-scene-mother-facing-throne-v3-native-aligned",
             "sha256":spec["source"]["sha256"],"path":spec["source"]["path"]},
            *spec["refs"]],
        "technical_postprocess":postprocess,
        "width":941 if postprocess!="none" else dimensions[0],
        "height":1672 if postprocess!="none" else dimensions[1],
        "technical_qa":"candidate_needs_visual_alignment_review" if not errors else "rejected_"+",".join(errors),
        "alpha_channel_checked":rgba,
        "human_visual_approval":False,"placement_verified":False,
        "visual_recomposition_approved":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,"provider_image_calls":1
    }
    proof.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                     encoding="utf-8")
    if native.exists():
        native_report=dict(report,asset_id=ASSET+"-provider-native",
                           sha256=sha256(raw).hexdigest(),
                           width=dimensions[0],height=dimensions[1],
                           technical_postprocess="none_raw_provider_preserved")
        nproof.write_text(json.dumps(native_report,ensure_ascii=False,indent=2)+"\n",
                          encoding="utf-8")
    print("EP01_ALDRIC_REPAIR_V2",json.dumps({
        "sha256":final,"qa":report["technical_qa"],
        "original_provider_dimensions":dimensions,
        "provider_calls":1,"approved":False},ensure_ascii=False))
    if errors:
        raise VideoForgeError("EP01_ALDRIC_REPAIR_REJECTED_BUT_ARCHIVED "+",".join(errors))
    return report

if __name__=="__main__":
    try:generate(os.environ["PROXY_ENDPOINT"])
    except (OSError,ValueError,ImportError,VideoForgeError,proxy_images.ProxyImageError) as exc:
        print("EP01_ALDRIC_REPAIR_STOPPED",str(exc),file=sys.stderr)
        sys.exit(2)
