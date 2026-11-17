"""Offline alignment of versioned C01-P04 V2 image from 941x1671 to 941x1672.

Zero proxy image calls, source pixels unchanged. Not final art approval.
"""
from __future__ import annotations
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
from .errors import VideoForgeError
from .ep01_corrected_mother_v2 import PRODUCER as SOURCE_PRODUCER
from .layered_shot_plan import ROOT,REL,CHANNEL,VIDEO

SHOT="C01-P04"
SOURCE_SHA="cf19543377960b2100148846f9d77852ca94510c949c62c27b9390e4fbee0f84"
PARENT_SHA="156a9376298166045654706e75b876a20b7f8201c70d6d494ae9a2b7465f5ab3"
PRODUCER="production-scene-mother-v2-aligned"
ASSET="c01-p04-scene-mother-v2-native-aligned-v1"
SCHEMA="videoforge/ep01-mother-v2-one-row-alignment/v1"


def prepare(root:Path=ROOT)->dict:
    root=Path(root)
    reg=json.loads((root/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json").read_text())
    hits=[x for x in reg["geracoes"] if x.get("asset")=="c01-p04-scene-mother-v2" and
          f"/{SOURCE_PRODUCER}/" in str(x.get("arquivo",""))]
    if len(hits)!=1 or hits[0].get("sha256")!=SOURCE_SHA:
        raise VideoForgeError("EP01_V2_ALIGN_SOURCE_MISSING")
    if any(x.get("asset")==ASSET and f"/{PRODUCER}/" in str(x.get("arquivo","")) for x in reg["geracoes"]):
        raise VideoForgeError("EP01_V2_ALIGN_ALREADY_ARCHIVED")
    path=Path(hits[0]["arquivo"])
    if path.is_absolute() or ".." in path.parts or not path.is_relative_to(REL/"assets"/"geracoes"/SOURCE_PRODUCER):
        raise VideoForgeError("EP01_V2_ALIGN_UNSAFE_SOURCE")
    file=root/path;proof=file.with_suffix(".production.json")
    if any(p.is_symlink() or not p.is_file() for p in (file,proof)):
        raise VideoForgeError("EP01_V2_ALIGN_PROOF_MISSING")
    blob=file.read_bytes()
    meta=json.loads(proof.read_text())
    if (hashlib.sha256(blob).hexdigest()!=SOURCE_SHA or
        meta.get("sha256")!=SOURCE_SHA or
        meta.get("source_image_sha256")!=PARENT_SHA or
        meta.get("output_canvas")!=[941,1671] or
        meta.get("source_canvas")!=[941,1672] or
        meta.get("technical_qa")!="rejected_canvas_mismatch" or
        meta.get("human_visual_approval") is not False or
        meta.get("candidate_scene_shot_id")!=SHOT):
        raise VideoForgeError("EP01_V2_ALIGN_SOURCE_PROVENANCE_INVALID")
    return {"blob":blob,"file":path.as_posix(),"meta":meta}


def generate(root:Path=ROOT)->dict:
    from PIL import Image,ImageChops
    root=Path(root);spec=prepare(root)
    dest=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    out=dest/(ASSET+".png");proof=dest/(ASSET+".production.json")
    if out.exists() or proof.exists() or out.is_symlink() or proof.is_symlink():
        raise VideoForgeError("EP01_V2_ALIGN_OUTPUT_EXISTS")
    with Image.open(BytesIO(spec["blob"])) as input_img:
        input_img.load()
        if input_img.format!="PNG" or input_img.size!=(941,1671):
            raise VideoForgeError("EP01_V2_ALIGN_INPUT_DIMENSIONS_CHANGED")
        src=input_img.convert("RGB")
    dst=Image.new("RGB",(941,1672),(0,0,0))
    dst.paste(src,(0,0))
    last=src.crop((0,1670,941,1671))
    dst.paste(last,(0,1671))
    if ImageChops.difference(dst.crop((0,0,941,1671)),src).getbbox():
        raise VideoForgeError("EP01_V2_ALIGN_PIXELS_CHANGED")
    if ImageChops.difference(dst.crop((0,1671,941,1672)),last).getbbox():
        raise VideoForgeError("EP01_V2_ALIGN_ROW_NOT_COPIED")
    buf=BytesIO();dst.save(buf,"PNG",optimize=True);raw=buf.getvalue()
    dest.mkdir(parents=True,exist_ok=True)
    out.write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    doc={
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "asset_id":ASSET,"candidate_scene_shot_id":SHOT,
        "sha256":sha,"source_image_sha256":SOURCE_SHA,
        "source_mother_sha256":PARENT_SHA,
        "source_originals_sha_verified":[{"asset_id":"c01-p04-scene-mother-v2",
                                            "sha256":SOURCE_SHA,"path":spec["file"]}],
        "generation_method":"proxy_edited_versioned_scene_mother",
        "technical_postprocess":"pad_bottom_one_row_no_crop_no_resize",
        "source_pixels_unchanged":True,"width":941,"height":1672,
        "technical_qa":"candidate_canvas_aligned_needs_human_visual_qa",
        "human_visual_approval":False,"rig_ready":False,"provider_image_calls":0,
        "mp4_generated":False,"youtube_uploaded":False
    }
    proof.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_MOTHER_V2_NATIVE_ALIGNED",json.dumps({
        "sha256":sha,"source":SOURCE_SHA,"paid_calls":0,"human_approval":False}))
    return doc


if __name__=="__main__":
    try: generate()
    except (OSError,ValueError,VideoForgeError,ImportError) as exc:
        print("EP01_MOTHER_V2_ALIGNMENT_STOPPED",str(exc),file=sys.stderr)
        raise SystemExit(2)
