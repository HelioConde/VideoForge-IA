"""Draw genuinely independent fore-/background grip pieces for C01-P04 V3.

Uses immutable exact-SHA creator-approved mother as visual reference.
The close-up is reference-only (NEVER a final PNG layer).
One paid call per run; outputs remain unapproved until inspected in a
spear-between-palm-and-fingers composition with grounded coordinates.
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
from .ep01_approved_v3_parts import aligned_source, existing_part
from .ep01_c01p04_v3_guard_grip_v2 import archived as archived_guard_v2
from .ep01_proxy_separate_parts import _reference_bible
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

SCHEMA = "videoforge/ep01-c01p04-v3-grip-occlusion-parts/v1"
PRODUCER = "production-c01p04-v3-grip-occlusion-v1"
APPROVED_SHA = "a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
ALIGNED_SHA = "b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
REFERENCE = REL / "REFERENCIA-PEGADA-APROVADA-C01-P04-V3.json"
SIDES = {
    "left": {
        "guard": "character-guarda_esquerdo",
        "spear": "object-lanca-esquerda",
        "bbox": [0, 760, 375, 1230],
        "hand_xy": [175, 970],
        "base_xy": [65, 1130],
        "tip_xy": [525, 430],
        "perspective": "LEFT guard in the left foreground; preserve left-side gauntlet",
    },
    "right": {
        "guard": "character-guarda_direito",
        "spear": "object-lanca-direita",
        "bbox": [562, 760, 941, 1230],
        "hand_xy": [800, 970],
        "base_xy": [923, 1130],
        "tip_xy": [395, 430],
        "perspective": "RIGHT guard on right side, separately preserve the mirrored hand perspective",
    },
}
ROLES = ("palm-rear", "fingers-front")

def asset(side: str, role: str) -> str:
    if side not in SIDES or role not in ROLES:
        raise VideoForgeError("GRIP_V1_UNKNOWN_SIDE_OR_ROLE")
    return f"c01-p04-v3-{side}-grip-{role}-v1"

def archived(side: str, role: str, root: Path=ROOT) -> dict | None:
    dest = Path(root) / REL / "assets" / "geracoes" / PRODUCER
    if not dest.exists():
        return None
    if dest.is_symlink():
        raise VideoForgeError("GRIP_V1_SYMLINK")
    name = asset(side,role)+".png"
    found=[]
    for d in dest.iterdir():
        if not d.is_dir() or not d.name.isdigit():
            continue
        png = d / name
        if not png.exists():
            continue
        record = png.with_suffix(".production.json")
        manifest = d / "manifesto-geracoes.json"
        if any(p.is_symlink() or not p.is_file() for p in (png,record,manifest)):
            raise VideoForgeError("GRIP_V1_ARCHIVE_INCOMPLETE")
        raw=png.read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        proof=json.loads(record.read_text(encoding="utf-8"))
        register=json.loads(manifest.read_text(encoding="utf-8"))
        matching=[v for v in register.get("images",[]) if v.get("file")==name]
        if (proof.get("sha256")!=sha
                or proof.get("side")!=side
                or proof.get("grip_role")!=role
                or proof.get("schema")!=SCHEMA
                or register.get("producer")!=PRODUCER
                or len(matching)!=1
                or matching[0].get("sha256")!=sha):
            raise VideoForgeError("GRIP_V1_ARCHIVE_SHA_INVALID")
        found.append({"run_id":int(d.name),"sha256":sha,
                      "path":png.relative_to(root).as_posix(),
                      "technical_qa":proof.get("technical_qa")})
    return max(found,key=lambda x:x["run_id"]) if found else None

def verified_art(item: dict, root: Path=ROOT) -> bytes:
    rel=Path(item["file"])
    if (rel.is_absolute() or ".." in rel.parts
            or not rel.is_relative_to(REL / "assets" / "geracoes")):
        raise VideoForgeError("GRIP_V1_UNSAFE_SOURCE_PATH")
    path=Path(root)/rel
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("GRIP_V1_SOURCE_FILE_MISSING")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=item["sha256"]:
        raise VideoForgeError("GRIP_V1_SOURCE_SHA_MISMATCH")
    return raw

def prepare(side: str, role: str, root: Path=ROOT) -> dict:
    from PIL import Image
    if side not in SIDES or role not in ROLES:
        raise VideoForgeError("GRIP_V1_TARGET_INVALID")
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if archived(side,role,root):
        raise VideoForgeError("GRIP_V1_ALREADY_ARCHIVED_NO_DUPLICATE_CALL")
    ref_file=root/REFERENCE
    if ref_file.is_symlink() or not ref_file.is_file():
        raise VideoForgeError("GRIP_V1_APPROVED_REFERENCE_MISSING")
    ref=json.loads(ref_file.read_text(encoding="utf-8"))
    if (ref.get("schema")!="videoforge/ep01-c01p04-approved-grip-reference/v1"
        or ref.get("source_mother_sha256")!=APPROVED_SHA
        or ref.get("source_technical_canvas_sha256")!=ALIGNED_SHA
        or ref.get("approval_scope")!="grip_reference_only_not_independent_layers"
        or ref.get("human_approval_of_new_hand_layers") is not False
        or ref.get("rig_ready") is not False):
        raise VideoForgeError("GRIP_V1_APPROVAL_REFERENCE_INVALID")
    source=aligned_source(root)
    if source["sha256"]!=ALIGNED_SHA:
        raise VideoForgeError("GRIP_V1_MOTHER_SHA_INVALID")
    cfg=SIDES[side]
    roi_field=f"{'left' if side=='left' else 'right'}_guard_reference_roi_approx_xyxy"
    if ref.get(roi_field)!=cfg["bbox"]:
        raise VideoForgeError("GRIP_V1_CROP_REFERENCE_CHANGED")
    guard=archived_guard_v2(cfg["guard"],root) if side=="left" else None
    if guard is None:
        guard=existing_part(cfg["guard"],root)
    spear=existing_part(cfg["spear"],root)
    if not guard or not spear:
        raise VideoForgeError("GRIP_V1_GUARD_OR_SPEAR_MISSING")
    with Image.open(BytesIO(source["blob"])) as im:
        im.load()
        if im.format!="PNG" or im.size!=(941,1672):
            raise VideoForgeError("GRIP_V1_MOTHER_CANVAS_CHANGED")
        # This is a reference only. It is NEVER saved as an asset.
        guide=im.convert("RGB").crop(tuple(cfg["bbox"]))
        buff=BytesIO();guide.save(buff,"PNG")
        guide_blob=buff.getvalue()
    bible_images,bible_refs=_reference_bible("C01-P04",cfg["guard"],root)
    refs=[source["blob"],guide_blob,verified_art(guard,root),
          verified_art(spear,root),*bible_images[:3]]
    if not 4<=len(refs)<=8:
        raise VideoForgeError("GRIP_V1_REFERENCE_COUNT_INVALID")
    grip=cfg["hand_xy"];butt=cfg["base_xy"];tip=cfg["tip_xy"]
    role_text=(
        "Create ONLY the CAMERA-FAR REAR GAUNTLET / PALM part of the "
        "grasping hand, including the natural wrist joining the forearm. "
        "The rear palm passes BEHIND an imaginary wooden spear shaft. "
        "NO separate near-side fingers or thumb in this PNG; the near-side "
        "fingers are a separate RGBA sprite. The palm must not hide the "
        "shaft when the shaft is composited in front of this layer."
        if role=="palm-rear" else
        "Create ONLY the CAMERA-NEAR FINGERS AND THUMB visibly CURLING "
        "in front of the spear shaft, from the approved hand close-up. "
        "Show anatomically accurate knuckles and connected glove fingertips "
        "with an open channel exactly the thickness of the invisible shaft. "
        "NO isolated fist floating to one side, and NO palm/forearm/entire "
        "gauntlet copied into this sprite: the rear palm is a different "
        "RGBA layer. The fingers must overlap the shaft when composited."
    )
    prompt=(
        "New original artwork for one anatomical hand SUB-LAYER of an "
        "already-approved medieval fantasy anime/manhwa throne scene. "
        "Do NOT copy source pixels. Image 1: immutable approved "
        "C01-P04 V3 mother; Image 2: close-up of the creator-approved "
        "CORRECT spear grip (ONLY for anatomy), Image 3: earlier separate "
        "guard as armor reference (its grip is NOT approved); Image 4: "
        "standalone spear as material/angle reference. "
        "The correct topology MUST be rear palm -> real spear shaft -> "
        "front fingers and thumb. " +cfg["perspective"]+". "
        "The spear is a real separate object with lower butt point "
        f"({butt[0]},{butt[1]}) and tip ({tip[0]},{tip[1]}) in the "
        "approved scene; the grasp is near "
        f"({grip[0]},{grip[1]}). The shaft runs THROUGH the hand, "
        "continuing clearly below it; it must NOT be next to the fist. "
        +role_text+" "
        "Deliver ONE isolated newly painted RGBA PNG with true alpha zero "
        "everywhere except this hand sub-component, matching the SMALL "
        "hand appearance and exact glove color/lighting/angle in the source. "
        "Use full-scene 9:16 conceptual coordinates and keep the fragment "
        "near original hand location; do not zoom hand to fill the canvas. "
        "NO spear pixels, NO floor, NO throne, NO text, NO checkerboard, "
        "NO extra fingers, NO detached wrist, NO other characters. "
        "This image is a candidate for visual QA, not an approved sprite, "
        "not a rig asset and not a pose-sheet."
    )
    return {"side":side,"role":role,"images":refs,"prompt":prompt,
            "guide_sha256":hashlib.sha256(guide_blob).hexdigest(),
            "mother":source,"source_guard":guard,"source_spear":spear,
            "bible_refs":bible_refs[:3]}

def generate(side: str, role: str, url: str, root: Path=ROOT)->dict:
    from PIL import Image
    result=prepare(side,role,root)
    payload={
      "model":"gpt-image-2","n":1,"size":"1024x1536",
      "background":"transparent","output_format":"png",
      "response_format":"b64_json","stream":False,
      "prompt":result["prompt"],
      "images":[{"image_url":"data:image/png;base64,"+
                 base64.b64encode(data).decode("ascii")}
                for data in result["images"]],
    }
    response=proxy_images.call_proxy(url,"/v1/images/edits",
                                    os.getenv("CODEX_PROXY_API_KEY",""),payload)
    raw,ext=proxy_images.decode_image(response)
    if ext!=".png":
        raise VideoForgeError("GRIP_V1_PROVIDER_NOT_PNG")
    with Image.open(BytesIO(raw)) as img:
        img.load()
        if img.format!="PNG": raise VideoForgeError("GRIP_V1_BAD_PNG")
        width,height=img.size
        has_alpha="A" in img.getbands()
        rgba=img.convert("RGBA")
    issues=[]
    if not has_alpha:
        issues.append("missing_true_alpha")
    else:
        amin,amax=rgba.getchannel("A").getextrema()
        if amin!=0 or amax<128:
            issues.append("alpha_invalid_or_empty")
    if not (512<=width<=2048 and 512<=height<=3072):
        issues.append("unexpected_native_canvas")
    bbox=rgba.getchannel("A").point(lambda a:255 if a>=16 else 0).getbbox()
    if bbox is None:
        issues.append("empty_alpha_bbox")
    elif (bbox[3]-bbox[1])/height>0.50:
        issues.append("hand_too_large_or_character_instead_of_hand")
    dest=Path(root)/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    file=dest/(asset(side,role)+".png")
    proof=file.with_suffix(".production.json")
    if file.exists() or proof.exists() or file.is_symlink() or proof.is_symlink():
        raise VideoForgeError("GRIP_V1_OUTPUT_EXISTS")
    dest.mkdir(parents=True,exist_ok=True)
    file.write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    record={
       "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
       "candidate_scene_shot_id":"C01-P04",
       "side":side,"grip_role":role,"asset_id":asset(side,role),
       "sha256":sha,"width":width,"height":height,
       "alpha_bbox_xyxy":list(bbox) if bbox else None,
       "technical_qa":"candidate_pending_hand_contact_review" if not issues
           else "rejected_"+",".join(issues),
       "source_image_sha256":ALIGNED_SHA,
       "approved_original_sha256":APPROVED_SHA,
       "approved_grip_reference_manifest":REFERENCE.as_posix(),
       "provider_guide_sha256":result["guide_sha256"],
       "source_originals_sha_verified":[
          {"asset_id":"c01-p04-v3-approved-aligned",
           "sha256":ALIGNED_SHA,"path":result["mother"]["path"]},
          {"asset_id":"guard_previous","sha256":result["source_guard"]["sha256"],
           "path":result["source_guard"]["file"]},
          {"asset_id":"spear_previous","sha256":result["source_spear"]["sha256"],
           "path":result["source_spear"]["file"]},
          *result["bible_refs"]],
       "generation_method":"new_independent_proxy_rgba_hand_piece",
       "cropped_approved_reference_only_for_guidance":True,
       "source_pixels_unchanged":True,
       "provider_image_calls":1,
       "joint_position_verified":False,"hand_spear_contact_verified":False,
       "human_visual_approval":False,"rig_ready":False,
       "mp4_generated":False,"youtube_uploaded":False
    }
    proof.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",
                     encoding="utf-8")
    print("EP01_GRIP_OCCLUSION_V1",json.dumps({
        "side":side,"role":role,"sha256":sha,"canvas":[width,height],
        "bbox":record["alpha_bbox_xyxy"],"qa":record["technical_qa"],
        "hand_contact_verified":False},ensure_ascii=False))
    if issues:
        raise VideoForgeError("GRIP_V1_REJECTED_BUT_SAVED "+",".join(issues))
    return record

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--side",choices=SIDES,required=True)
    cli.add_argument("--role",choices=ROLES,required=True)
    cli.add_argument("--url",required=True)
    args=cli.parse_args()
    try:
        generate(args.side,args.role,args.url)
    except (OSError,ValueError,ImportError,VideoForgeError,proxy_images.ProxyImageError) as e:
        print("EP01_GRIP_OCCLUSION_STOP",str(e),file=sys.stderr)
        sys.exit(2)
