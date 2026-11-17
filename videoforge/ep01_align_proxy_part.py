"""QA-only native-canvas alignment of independent proxy-generated PNG.

Never extracts sprites from a scene-mother. Zero AI calls. Keeps original bytes
permanently and produces a new separately-versioned, audited candidate only for
one/two missing BOTTOM rows, without resampling or moving any source pixel.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys

from .ep01_proxy_separate_parts import PRODUCER as SOURCE_PRODUCER, existing_part, read_shot
from .ep01_shot_mother import existing_mother
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from .errors import VideoForgeError

PRODUCER="production-proxy-separate-alignment-v1"
MAX_BOTTOM_PAD=2
SCHEMA="videoforge/proxy-separate-canvas-alignment/v1"


def prepare(shot_id:str,part_id:str,root:Path=ROOT)->dict:
    root=Path(root)
    _,req=read_shot(shot_id,part_id,root)
    if shot_id=="C01-P02":
        raise VideoForgeError("EP01_ALIGN_REJECTED_MOTHER_NOT_ALLOWED")
    source=existing_part(shot_id,part_id,root)
    mother=existing_mother(shot_id,root)
    if not source or not mother:
        raise VideoForgeError("EP01_ALIGN_SOURCE_MISSING")
    source_file=root/Path(source["file"])
    proof_file=source_file.with_suffix(".production.json")
    if proof_file.is_symlink() or not proof_file.is_file():
        raise VideoForgeError("EP01_ALIGN_PROOF_MISSING")
    proof=json.loads(proof_file.read_text(encoding="utf-8"))
    if (proof.get("sha256")!=source["sha256"] or
        proof.get("generation_method")!="proxy_generated_separate_image" or
        proof.get("technical_qa")!="rejected_canvas_mismatch_no_pixel_resizing" or
        proof.get("source_mother_sha256")!=mother["sha256"] or
        proof.get("human_visual_approval") is not False or
        proof.get("candidate_scene_shot_id")!=shot_id or
        proof.get("component")!=part_id):
        raise VideoForgeError("EP01_ALIGN_SOURCE_NOT_VERIFIED_PROXY_IMAGE")
    width,height=proof["source_canvas"]
    if (type(width) is not int or type(height) is not int or
        proof.get("width")!=width or
        type(proof.get("height")) is not int or
        not 1 <= height-proof["height"] <= MAX_BOTTOM_PAD):
        raise VideoForgeError("EP01_ALIGN_NOT_SMALL_BOTTOM_PAD")
    raw=source_file.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=source["sha256"]:
        raise VideoForgeError("EP01_ALIGN_SOURCE_SHA_INVALID")
    return {"shot_id":shot_id,"part_id":part_id,"source":source,
            "source_proof":proof,"raw":raw,"expected_canvas":(width,height),
            "padding":height-proof["height"],"role":req["role"]}


def write_candidate(shot_id:str,part_id:str,root:Path=ROOT)->dict:
    root=Path(root)
    spec=prepare(shot_id,part_id,root)
    from PIL import Image,ImageChops
    asset_id=shot_id.lower()+"-"+part_id+"-native-aligned-v1"
    destination=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    dst=destination/(asset_id+".png")
    meta=destination/(asset_id+".production.json")
    if dst.is_symlink() or dst.exists() or meta.is_symlink() or meta.exists():
        raise VideoForgeError("EP01_ALIGN_OUTPUT_ALREADY_EXISTS")
    with Image.open(BytesIO(spec["raw"])) as source:
        source.load()
        role=spec["role"]
        mode="RGB" if role=="background" else "RGBA"
        if role!="background" and "A" not in source.getbands():
            raise VideoForgeError("EP01_ALIGN_NO_RGBA_ON_TRANSPARENT_COMPONENT")
        if source.size!=(spec["expected_canvas"][0],spec["source_proof"]["height"]):
            raise VideoForgeError("EP01_ALIGN_SOURCE_DIMENSIONS_CHANGED")
        original=source.convert(mode)
        target=Image.new(mode,spec["expected_canvas"],
                         (0,0,0) if role=="background" else (0,0,0,0))
        target.paste(original,(0,0))
        if role=="background":
            last=original.crop((0,original.height-1,original.width,original.height))
            for y in range(original.height,target.height):
                target.paste(last,(0,y))
        if ImageChops.difference(
                target.crop((0,0,original.width,original.height)),original).getbbox():
            raise VideoForgeError("EP01_ALIGN_SOURCE_PIXELS_CHANGED")
        if role=="background":
            for y in range(original.height,target.height):
                if ImageChops.difference(
                        target.crop((0,y,target.width,y+1)),
                        original.crop((0,original.height-1,original.width,original.height))
                   ).getbbox():
                    raise VideoForgeError("EP01_ALIGN_BOTTOM_PADDING_INCONSISTENT")
        else:
            if target.getchannel("A").getextrema()[0]!=0:
                raise VideoForgeError("EP01_ALIGN_NO_TRANSPARENT_BORDER")
        buff=BytesIO()
        target.save(buff,"PNG",optimize=True)
        raw_out=buff.getvalue()
    destination.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(raw_out)
    sha=hashlib.sha256(raw_out).hexdigest()
    metadata={
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "candidate_scene_shot_id":shot_id,"asset_id":asset_id,
        "source_mother_sha256":spec["source_proof"]["source_mother_sha256"],
        "source_image_sha256":spec["source"]["sha256"],
        "source_originals_sha_verified":[{
            "id":spec["source_proof"]["asset_id"],
            "sha256":spec["source"]["sha256"],
            "path":spec["source"]["file"]}],
        "generation_method":"proxy_generated_separate_image",
        "technical_postprocess":"pad_bottom_only_no_crop_or_rescale",
        "source_pixels_unchanged":True,"bottom_rows_added":spec["padding"],
        "padding_method":"repeat_last_background_row" if spec["role"]=="background"
                         else "add_transparent_rows",
        "width":spec["expected_canvas"][0],"height":spec["expected_canvas"][1],
        "sha256":sha,
        "technical_qa":"candidate_canvas_aligned_needs_visual_recomposition_qa",
        "human_visual_approval":False,"rig_ready":False,
        "youtube_uploaded":False,"mp4_generated":False,
        "provider_image_calls":0
    }
    meta.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_PROXY_PART_ALIGNED",json.dumps({
        "source_sha":spec["source"]["sha256"],"asset":asset_id,
        "aligned_sha":sha,"bottom_rows_added":spec["padding"],"paid_calls":0}))
    return metadata


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--shot-id",required=True)
    p.add_argument("--part",required=True)
    a=p.parse_args()
    try:
        write_candidate(a.shot_id,a.part)
    except (ValueError,OSError,ImportError,VideoForgeError) as exc:
        print("EP01_PROXY_PART_ALIGNMENT_STOPPED",str(exc),file=sys.stderr)
        raise SystemExit(2)

if __name__=="__main__":
    main()
