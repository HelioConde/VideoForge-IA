"""Generate one NEW independent C01-P04 V3 guard with anatomically correct grip.

The mother is creator-approved, immutable and SHA verified. Previous oversized
guard remains archived. Existing spear remains a distinct independent part.
A small QA-only grip crop is used as reference, never as a final rig asset.
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

from . import image_generation_policy,proxy_images
from .errors import VideoForgeError
from .ep01_approved_v3_parts import aligned_source,existing_part,ROLE_CONFIG
from .ep01_proxy_separate_parts import _reference_bible
from .layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from .scene_layers import png_info

PRODUCER="production-c01p04-v3-guard-grip-v2"
SCHEMA="videoforge/ep01-c01p04-v3-guard-grip-repair/v2"
APPROVED_SOURCE_SHA="a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
GUARDS={
 "character-guarda_esquerdo":{
  "region":[0,470,345,1380],
  "grip_center":[175,970],
  "spear_base":[65,1130],"spear_tip":[525,430],
  "grip_reference_crop":[0,790,385,1250],
  "spear_part":"object-lanca-esquerda",
  "label":"LEFT guard on image LEFT; body turned toward king and other guard"},
 "character-guarda_direito":{
  "region":[605,470,941,1380],
  "grip_center":[800,970],
  "spear_base":[923,1130],"spear_tip":[395,430],
  "grip_reference_crop":[568,790,941,1250],
  "spear_part":"object-lanca-direita",
  "label":"RIGHT guard on image RIGHT; body turned toward king and other guard"},
}

def asset(part:str)->str:
    return "c01-p04-v3-"+part+"-grip-v2"

def archived(part:str,root:Path=ROOT):
    dest=Path(root)/REL/"assets"/"geracoes"/PRODUCER
    if not dest.exists():return None
    if dest.is_symlink():raise VideoForgeError("GRIP_V2_ARCHIVE_SYMLINK")
    found=[]
    for directory in dest.iterdir():
        if not directory.is_dir() or not directory.name.isdecimal():continue
        p=directory/(asset(part)+".png")
        if not p.exists():continue
        record=p.with_suffix(".production.json")
        manifest=directory/"manifesto-geracoes.json"
        if any(x.is_symlink() or not x.is_file() for x in (p,record,manifest)):
            raise VideoForgeError("GRIP_V2_ARCHIVE_INCOMPLETE")
        raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        proof=json.loads(record.read_text(encoding="utf-8"))
        data=json.loads(manifest.read_text(encoding="utf-8"))
        matches=[x for x in data.get("images",[]) if x.get("file")==p.name]
        if (proof.get("sha256")!=digest or proof.get("component")!=part
            or data.get("producer")!=PRODUCER or len(matches)!=1
            or matches[0].get("sha256")!=digest):
            raise VideoForgeError("GRIP_V2_ARCHIVE_PROVENANCE_INVALID")
        found.append({"run_id":int(directory.name),"sha256":digest,
                      "file":p.relative_to(root).as_posix()})
    return max(found,key=lambda x:x["run_id"]) if found else None

def verified_file(relative:str,sha:str,root:Path=ROOT)->bytes:
    p=Path(root)/relative
    if (p.is_symlink() or not p.is_file() or ".." in Path(relative).parts
        or hashlib.sha256(p.read_bytes()).hexdigest()!=sha):
        raise VideoForgeError("GRIP_V2_REFERENCE_SHA_INVALID")
    return p.read_bytes()

def prepare(part:str,root:Path=ROOT)->dict:
    from PIL import Image,ImageDraw
    if part not in GUARDS:raise VideoForgeError("GRIP_V2_PART_INVALID")
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if archived(part,root):raise VideoForgeError("GRIP_V2_ALREADY_ARCHIVED_NO_REPEAT")
    approved=aligned_source(root)
    old=existing_part(part,root)
    spear=existing_part(GUARDS[part]["spear_part"],root)
    if not old or not spear:
        raise VideoForgeError("GRIP_V2_PREVIOUS_GUARD_OR_SPEAR_MISSING")
    old_bytes=verified_file(old["file"],old["sha256"],root)
    spear_bytes=verified_file(spear["file"],spear["sha256"],root)
    cfg=GUARDS[part]
    with Image.open(BytesIO(approved["blob"])) as base:
        base.load()
        if base.size!=(941,1672):raise VideoForgeError("GRIP_V2_MOTHER_DIMENSION_CHANGED")
        # Reference crop for anatomical direction ONLY, not a sprite output.
        snap=base.convert("RGB").crop(tuple(cfg["grip_reference_crop"]))
        buffer=BytesIO();snap.save(buffer,"PNG")
        grip_reference=buffer.getvalue()
    raws,proofs=_reference_bible("C01-P04",part,root)
    # Four fixed inputs + up to four already SHA-verified Visual Bible refs.
    assets=[approved["blob"],old_bytes,grip_reference,spear_bytes]+raws[:4]
    if len(assets)>8:
        raise VideoForgeError("GRIP_V2_TOO_MANY_REFERENCES")
    x1,y1,x2,y2=cfg["region"]
    bx,by=cfg["spear_base"];tx,ty=cfg["spear_tip"]
    gx,gy=cfg["grip_center"]
    prompt=(
        "Create ONE NEW independent FULL FRAME 9:16 RGBA transparent "
        "character sprite. IMAGE 1 is the exact creator-approved C01-P04 V3 "
        "mother (technical extra bottom row), lock its camera, framing, "
        "lighting and costumes. IMAGE 2 is the matching independent guard "
        "but OVERSIZED, use it ONLY for armor/cape/face details, NOT for "
        "size or placement. IMAGE 3 is a QA REFERENCE CROPPED CLOSEUP "
        "of the correctly GRASPED spear in the approved mother, used "
        "ONLY to understand fingers around shaft. IMAGE 4 is the single "
        "independently generated spear for appearance/reference, "
        "NOT to draw in this new guard asset. "
        +cfg["label"]+". On the transparent output canvas (941 pixels wide "
        "and 1672 pixels tall), the ENTIRE visible guard must fit in the "
        "ORIGINAL small scene region x="+str(x1)+".."+str(x2)+
        ", y="+str(y1)+".."+str(y2)+
        ". Maintain exact feet contact on hall floor at around y=1300, "
        "correct helmet plume around y=540, and body turned in three "
        "quarters, not re-centered, enlarged or full-canvas. "
        "The grip hand/gauntlet must be anatomically CORRECT: all five "
        "fingers and thumb visibly curl around an IMAGINARY WOODEN SHAFT "
        "at approximately x="+str(gx)+", y="+str(gy)+
        ", with arm/elbow/wrist naturally connected. Imaginary spear "
        "line starts at butt x="+str(bx)+", y="+str(by)+
        " and rises diagonally to tip x="+str(tx)+", y="+str(ty)+
        "; the hand must wrap the LOWER THIRD of this invisible diagonal, "
        "not touch only its extreme butt and never float beside it. "
        "DO NOT DRAW ANY SPEAR, shaft, blade, weapon or any other character "
        "inside this sprite because the spear is a SEPARATE RGBA image. "
        "No throne, background, stairs, Kael, Aldric, right/left other guard, "
        "fake checkerboard or text. True alpha=0 outside the isolated guard. "
        "Preserve identical golden steel plates, burgundy plume/cape, "
        "armor embroidery and lighting of the approved original. "
        "No extra limbs or duplicate hands. This is newly drawn art "
        "for individual QA, NOT a pixel crop from mother; no auto rig."
    )
    return {"part":part,"inputs":assets,"refs":proofs[:4],
            "grip_reference_sha256":hashlib.sha256(grip_reference).hexdigest(),
            "approved":approved,"old":old,"spear":spear,"prompt":prompt}

def generate(part:str,url:str,root:Path=ROOT)->dict:
    from PIL import Image
    spec=prepare(part,root)
    payload={
      "model":"gpt-image-2","n":1,"size":"1024x1536",
      "background":"transparent","output_format":"png",
      "response_format":"b64_json","stream":False,
      "prompt":spec["prompt"],
      "images":[{"image_url":"data:image/png;base64,"+
                 base64.b64encode(img).decode("ascii")} for img in spec["inputs"]]
    }
    result=proxy_images.call_proxy(url,"/v1/images/edits",
                                  os.getenv("CODEX_PROXY_API_KEY",""),payload)
    raw,ext=proxy_images.decode_image(result)
    if ext!=".png":raise VideoForgeError("GRIP_V2_PROVIDER_NOT_PNG")
    with Image.open(BytesIO(raw)) as img:
        if img.format!="PNG":raise VideoForgeError("GRIP_V2_NOT_PNG")
        img.load()
        w,h=img.size
        rgba="A" in img.getbands()
        r=img.convert("RGBA")
    violations=[]
    if not rgba or r.getchannel("A").getextrema()[0]!=0:
        violations.append("alpha_missing")
    if not 512<=w<=2048 or not 512<=h<=3072:
        violations.append("unsupported_canvas")
    # The provider can return native size; scale matching requires separate QA.
    alpha=r.getchannel("A").point(lambda n:255 if n>=16 else 0)
    bbox=alpha.getbbox()
    if bbox is None:violations.append("empty_sprite")
    if bbox:
        bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
        if bh/max(h,1)>0.76:
            violations.append("likely_oversized_actor_relative_to_canvas")
    dest=Path(root)/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    png=dest/(asset(part)+".png")
    proof=dest/(asset(part)+".production.json")
    if png.exists() or proof.exists():
        raise VideoForgeError("GRIP_V2_OUTPUT_EXISTS")
    dest.mkdir(parents=True,exist_ok=True)
    png.write_bytes(raw)
    digest=hashlib.sha256(raw).hexdigest()
    record={
      "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,"candidate_scene_shot_id":"C01-P04",
      "component":part,"asset_id":asset(part),"sha256":digest,
      "width":w,"height":h,"alpha_bbox":list(bbox) if bbox else None,
      "approved_original_sha256":APPROVED_SOURCE_SHA,
      "source_image_sha256":spec["approved"]["sha256"],
      "source_originals_sha_verified":[
        {"asset_id":"c01-p04-scene-mother-facing-throne-v3-native-aligned",
         "sha256":spec["approved"]["sha256"],"path":spec["approved"]["path"]},
        {"asset_id":"previous_"+part,"sha256":spec["old"]["sha256"],
         "path":spec["old"]["file"]},
        {"asset_id":"previous_"+GUARDS[part]["spear_part"],
         "sha256":spec["spear"]["sha256"],"path":spec["spear"]["file"]},
        *spec["refs"]],
      "qa_reference_crop_sha256":spec["grip_reference_sha256"],
      "generation_method":"fresh_proxy_rgba_sprite_not_a_pixel_crop",
      "original_and_other_guards_immutable":True,
      "new_model_calls":1,
      "technical_qa":"candidate_for_grip_and_spatial_review" if not violations
                     else "rejected_"+",".join(violations),
      "hand_spear_contact_human_verified":False,
      "other_parts_approved":False,"human_visual_approval":False,
      "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False
    }
    proof.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_GUARD_GRIP_V2",json.dumps({
       "part":part,"sha256":digest,"size":[w,h],"bbox":record["alpha_bbox"],
       "qa":record["technical_qa"],"rig_ready":False},ensure_ascii=False))
    if violations:
        raise VideoForgeError("GRIP_V2_REJECTED_BUT_SAVED "+",".join(violations))
    return record

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--part",required=True,choices=GUARDS)
    cli.add_argument("--url",required=True)
    args=cli.parse_args()
    try:generate(args.part,args.url)
    except (OSError,ValueError,ImportError,VideoForgeError,proxy_images.ProxyImageError) as e:
        print("EP01_GUARD_GRIP_V2_STOP",str(e),file=sys.stderr);sys.exit(2)
