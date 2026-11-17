"""EP01 C01-P04: independent anatomical sublayers, one new PNG per paid call.

Order: forearm-cuff -> palm-rear -> fingers-front, with the existing separate
spear between palm and fingers. The creator approved ONLY the original V3
mother grip. Every derived/new part remains pending visual approval.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import sys

from PIL import Image

from . import image_generation_policy, proxy_images
from .errors import VideoForgeError
from .ep01_approved_v3_parts import aligned_source, existing_part
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

SCHEMA = "videoforge/ep01-c01p04-right-grip-v1-independent-part/v1"
PRODUCER = "production-c01p04-right-grip-v1-independent-part"
SHOT = "C01-P04"
ROLES = ("forearm-cuff","palm-rear","fingers-front")
APPROVED_SHA = "a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
ALIGNED_SHA = "b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
GUIDE_SHA = "eaeafebd244b9059006b7cfe74dcc4ebeeecf3471102283f883c52ad8032e16c"
GUIDE_FILE = (REL / "assets" / "geracoes" / "production-c01p04-v3-canonical-grip-guide-v1"
              / "44183662671" / "c01-p04-v3-left-grip-with-real-spear-reference-v1.png")
APPROVAL_FILE = REL / "REFERENCIA-PEGADA-APROVADA-C01-P04-V3.json"
ROLENAMES = {
    "forearm-cuff": "RIGHT FOREARM CUFF ONLY: gilded armor plate and wrist articulation, without any palm or fingers. Short sleeve end with open wrist ring, no hollow detached tube pretending to be a hand. Must connect to arm, matching exact approved outfit.",
    "palm-rear": "RIGHT REAR PALM ONLY: actual open glove palm surface with the natural hand base connecting to the wrist, behind the imaginary cylindrical spear. NOT a forearm guard, NOT a clenched fist, and NO near-side fingers. Must leave the appropriate shaft channel; visible flesh/leather/plate palm with functional hand structure.",
    "fingers-front": "RIGHT FRONT DIGITS LAYER ONLY. Draw EXACTLY the four camera-facing CURVED individual fingers (index, middle, ring, little) and the opposite THUMB in a thin connected arc, each showing distinct natural phalange plates and separated tips wrapping the imaginary cylindrical wooden shaft. Preserve a clear TRANSPARENT OPEN SLOT for the shaft between the digits and where the rear palm would be. This is a narrow OVERLAY STRIP of articulated fingers; no solid mitten shape, no closed fist silhouette, no palm surface, no cuff, no wrist, no forearm. The fingers visibly hook toward the viewer around the grip, and must not be painted as a generic glove.",
}
SCENE_GUIDANCE = {
    "forearm-cuff": "Original RIGHT guard wrist and forearm near x=720..840, y=785..980 in the 941x1672 mother scene.",
    "palm-rear": "Original rear of RIGHT guard's grasping hand near x=715..805, y=925..1005 in the 941x1672 mother scene.",
    "fingers-front": "Original RIGHT guard fingertips across spear near x=713..810, y=935..1005 in the 941x1672 mother scene.",
}

def name(role: str) -> str:
    if role not in ROLES:
        raise VideoForgeError("RIGHT_GRIP_V1_INVALID_ROLE")
    return "c01-p04-v3-right-grip-" + role + "-v1"

def archive(role: str, root: Path = ROOT):
    if role not in ROLES:
        raise VideoForgeError("RIGHT_GRIP_V1_INVALID_ROLE")
    folder = Path(root)/REL/"assets"/"geracoes"/PRODUCER
    if not folder.exists():
        return None
    if folder.is_symlink():
        raise VideoForgeError("RIGHT_GRIP_V1_ARCHIVE_SYMLINK")
    items=[]
    for run in folder.iterdir():
        if not run.is_dir() or not run.name.isdecimal():
            continue
        file=run/(name(role)+".png")
        if not file.exists():
            continue
        proof=file.with_suffix(".production.json")
        manifest=run/"manifesto-geracoes.json"
        if any(x.is_symlink() or not x.is_file() for x in (file,proof,manifest)):
            raise VideoForgeError("RIGHT_GRIP_V1_ARCHIVE_INCOMPLETE")
        digest=sha256(file.read_bytes()).hexdigest()
        p=json.loads(proof.read_text(encoding="utf-8"))
        m=json.loads(manifest.read_text(encoding="utf-8"))
        matches=[x for x in m.get("images",[]) if x.get("file")==file.name]
        if (p.get("sha256")!=digest or p.get("schema")!=SCHEMA or
            p.get("role")!=role or m.get("producer")!=PRODUCER or
            len(matches)!=1 or matches[0].get("sha256")!=digest or
            m.get("github_run_id")!=int(run.name)):
            raise VideoForgeError("RIGHT_GRIP_V1_ARCHIVE_BAD_SHA_OR_PROVENANCE")
        items.append({"run_id":int(run.name),"sha256":digest,
                      "file":file.relative_to(root).as_posix(),
                      "technical_qa":p.get("technical_qa")})
    return max(items,key=lambda x:x["run_id"]) if items else None

def reference(root: Path, path: Path, expected_sha: str):
    if path.is_absolute() or ".." in path.parts or not path.is_relative_to(REL/"assets"/"geracoes"):
        raise VideoForgeError("RIGHT_GRIP_V1_UNSAFE_REFERENCE")
    file=root/path
    if file.is_symlink() or not file.is_file():
        raise VideoForgeError("RIGHT_GRIP_V1_REFERENCE_MISSING")
    data=file.read_bytes()
    if sha256(data).hexdigest()!=expected_sha:
        raise VideoForgeError("RIGHT_GRIP_V1_REFERENCE_SHA_CHANGED")
    return data

def prep(role: str, root: Path = ROOT):
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if archive(role,root):
        raise VideoForgeError("RIGHT_GRIP_V1_ALREADY_ARCHIVED_NO_DUPLICATE_CHARGE")
    approved=aligned_source(root)
    if approved["sha256"]!=ALIGNED_SHA:
        raise VideoForgeError("RIGHT_GRIP_V1_APPROVED_SOURCE_CHANGED")
    record=root/APPROVAL_FILE
    if record.is_symlink() or not record.is_file():
        raise VideoForgeError("RIGHT_GRIP_V1_APPROVED_MANIFEST_MISSING")
    doc=json.loads(record.read_text(encoding="utf-8"))
    if (doc.get("schema")!="videoforge/ep01-c01p04-approved-grip-reference/v1"
        or doc.get("source_mother_sha256")!=APPROVED_SHA
        or doc.get("source_technical_canvas_sha256")!=ALIGNED_SHA
        or doc.get("approval_scope")!="grip_reference_only_not_independent_layers"
        or doc.get("rig_ready") is not False):
        raise VideoForgeError("RIGHT_GRIP_V1_APPROVED_MANIFEST_INVALID")
    existing_spear=existing_part("object-lanca-direita",root)
    if not existing_spear:
        raise VideoForgeError("RIGHT_GRIP_V1_SPEAR_MISSING")
    spear=reference(root,Path(existing_spear["file"]),existing_spear["sha256"])
    guide=reference(root,GUIDE_FILE,GUIDE_SHA)
    original_right_guard=existing_part("character-guarda_direito",root)
    if original_right_guard is None:
        raise VideoForgeError("RIGHT_GRIP_V1_GUARD_REFERENCE_MISSING")
    guard=reference(root,Path(original_right_guard["file"]),original_right_guard["sha256"])
    with Image.open(BytesIO(approved["blob"])) as im:
        if im.format!="PNG" or im.size!=(941,1672):
            raise VideoForgeError("RIGHT_GRIP_V1_REFERENCE_DIMENSIONS_CHANGED")
        crop=im.convert("RGB").crop((562,760,941,1230))
        out=BytesIO();crop.save(out,format="PNG")
        closeup=out.getvalue()
    prompt=(
      "RIGHT SIDE ONLY: preserve separate guard to the RIGHT of the throne. "
      "PAINT EXACTLY ONE NEW INDEPENDENT RGBA ART COMPONENT, not a photo or "
      "pose sheet. IMAGE 1 is the approved mother image, IMAGE 2 is its "
      "correct RIGHT guard real grip close-up, IMAGE 3 is an anatomical study "
      "of the LEFT guard to explain grip topology ONLY, not to mirror handedness. "
      "IMAGE 4 is the actual independent RIGHT spear reference; IMAGE 5 is "
      "the original RIGHT guard for armor and directional identity. The approved mother is canonical for "
      "lighting, camera angle, proportions and palette. The anatomical "
      "study is reference ONLY, not approved source art to copy pixels from. "
      "TARGET SINGLE COMPONENT: " +ROLENAMES[role]+" "+
      SCENE_GUIDANCE[role]+" "
      "CRUCIAL: We are NOT asking for a whole hand holding a spear in this "
      "PNG. Anatomically different hand sublayers will be independently "
      "composited with the actual spear between rear and front pieces. "
      "The RIGHT guard must retain its OWN side perspective and original "
      "handedness; DO NOT copy the left guard silhouette or flip its colors. "
      "No spear pixels or wooden line in this output. No background, "
      "steps, throne, character body, extra gloves, checkerboard, text, "
      "watermark or HUD. True alpha zero outside only this small isolated "
      "component. Keep exact shape/metal engravings/lighting, no new armor "
      "style. If source aspect differs, preserve artwork without distortion, "
      "do not zoom the isolated component to fill the frame: it is tiny "
      "in the full 9:16 scene. This is a CANDIDATE requiring visual QA. "
      "Do NOT create a complete clenched fist."
    )
    return {"role":role,"images":[approved["blob"],closeup,guide,spear,guard],
            "prompt":prompt,"source_sha256":approved["sha256"],
            "guide_sha256":GUIDE_SHA,"spear_sha256":existing_spear["sha256"],
            "closeup_sha256":sha256(closeup).hexdigest(),
            "right_guard_sha256":original_right_guard["sha256"]}

def generate(role: str, url: str, root: Path = ROOT):
    obj=prep(role,root)
    payload={"model":"gpt-image-2","n":1,"size":"1024x1536",
             "background":"transparent","output_format":"png",
             "response_format":"b64_json","stream":False,
             "prompt":obj["prompt"],
             "images":[{"image_url":"data:image/png;base64,"+
                        base64.b64encode(x).decode("ascii")} for x in obj["images"]]}
    answer=proxy_images.call_proxy(url,"/v1/images/edits",
                    os.getenv("CODEX_PROXY_API_KEY",""),payload)
    data,ext=proxy_images.decode_image(answer)
    if ext!=".png":
        raise VideoForgeError("RIGHT_GRIP_V1_PROVIDER_NOT_PNG")
    with Image.open(BytesIO(data)) as im:
        im.load()
        if im.format!="PNG":
            raise VideoForgeError("RIGHT_GRIP_V1_BAD_PNG")
        dims=list(im.size)
        alpha="A" in im.getbands()
        rgba=im.convert("RGBA")
    issues=[]
    if not alpha or rgba.getchannel("A").getextrema()[0]!=0 or rgba.getchannel("A").getextrema()[1]<128:
        issues.append("invalid_alpha")
    if not 512<=dims[0]<=2048 or not 512<=dims[1]<=3072:
        issues.append("implausible_dimensions")
    bbox=rgba.getchannel("A").point(lambda x:255 if x>=16 else 0).getbbox()
    if bbox is None:
        issues.append("empty_sprite")
    area=((bbox[2]-bbox[0])*(bbox[3]-bbox[1])/(dims[0]*dims[1])) if bbox else 0
    # Only warning: a full limb may be correct in a native canvas; do not crop.
    scale_warning=(bbox is not None and (bbox[3]-bbox[1])/dims[1]>0.72)
    out=Path(root)/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    img=out/(name(role)+".png")
    proof=out/(name(role)+".production.json")
    if img.is_symlink() or proof.is_symlink() or img.exists() or proof.exists():
        raise VideoForgeError("RIGHT_GRIP_V1_OUTPUT_EXISTS")
    out.mkdir(parents=True,exist_ok=True)
    img.write_bytes(data)
    digest=sha256(data).hexdigest()
    record={
      "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
      "candidate_scene_shot_id":SHOT,"role":role,"asset_id":name(role),
      "sha256":digest,"width":dims[0],"height":dims[1],
      "alpha_bbox_xyxy":list(bbox) if bbox else None,
      "alpha_bbox_area_fraction":round(area,5),
      "likely_oversized_native_bbox_warning":scale_warning,
      "technical_qa":("candidate_pending_spatial_and_anatomical_review"
                      if not issues else "rejected_"+",".join(issues)),
      "source_image_sha256":obj["source_sha256"],
      "approved_original_sha256":APPROVED_SHA,
      "grip_guide_reference_sha256":GUIDE_SHA,
      "grip_closeup_reference_sha256":obj["closeup_sha256"],
      "independent_spear_reference_sha256":obj["spear_sha256"],
      "right_guard_reference_sha256":obj["right_guard_sha256"],
      "generation_method":"fresh_independent_proxy_rgba",
      "side":"right",
      "mirror_left_guard_as_final_art":False,
      "provider_image_calls":1,
      "anatomical_component_visual_approved":False,
      "hand_spear_contact_verified":False,
      "spatial_registration_approved":False,
      "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False
    }
    proof.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_C01P04_RIGHT_GRIP_V1",json.dumps({
       "role":role,"sha256":digest,"size":dims,"bbox":record["alpha_bbox_xyxy"],
       "technical_qa":record["technical_qa"],"approved":False},ensure_ascii=False))
    if issues:
        raise VideoForgeError("RIGHT_GRIP_V1_REJECTED_BUT_ARCHIVED "+",".join(issues))
    return record

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--role",required=True,choices=ROLES)
    parser.add_argument("--url",required=True)
    args=parser.parse_args()
    try:
        generate(args.role,args.url)
    except (VideoForgeError,proxy_images.ProxyImageError,OSError,ValueError,ImportError) as exc:
        print("EP01_RIGHT_GRIP_V1_STOP",str(exc),file=sys.stderr)
        sys.exit(2)
