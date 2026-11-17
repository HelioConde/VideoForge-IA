"""One paid generation: anatomical guide of a hand REALLY wrapping a visible spear.

This is a QA/reference candidate ONLY, not a rig or a separable sprite.
The approved mother remains immutable. We create no final sprite cutouts.
"""
from __future__ import annotations

import base64
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import sys

from . import image_generation_policy,proxy_images
from .errors import VideoForgeError
from .ep01_approved_v3_parts import aligned_source,existing_part
from .layered_shot_plan import ROOT,REL,CHANNEL,VIDEO

SCHEMA="videoforge/ep01-c01p04-grip-topology-guide/v1"
PRODUCER="production-c01p04-v3-canonical-grip-guide-v1"
ASSET="c01-p04-v3-left-grip-with-real-spear-reference-v1"
SIDE="left"
SHA_APPROVED="a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
SHA_ALIGNED="b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"

def existing(root:Path=ROOT):
    d=Path(root)/REL/"assets"/"geracoes"/PRODUCER
    if not d.exists():return None
    matches=[]
    for folder in d.iterdir():
        if not folder.is_dir() or not folder.name.isdigit():continue
        file=folder/(ASSET+".png")
        if not file.exists():continue
        proof=file.with_suffix(".production.json")
        manifest=folder/"manifesto-geracoes.json"
        if any(x.is_symlink() or not x.is_file() for x in (file,proof,manifest)):
            raise VideoForgeError("GUIDE_V1_ARCHIVE_INCOMPLETE")
        digest=hashlib.sha256(file.read_bytes()).hexdigest()
        p=json.loads(proof.read_text(encoding="utf-8"))
        m=json.loads(manifest.read_text(encoding="utf-8"))
        rows=[v for v in m.get("images",[]) if v.get("file")==file.name]
        if (p.get("sha256")!=digest or p.get("schema")!=SCHEMA
            or m.get("producer")!=PRODUCER
            or len(rows)!=1 or rows[0].get("sha256")!=digest):
            raise VideoForgeError("GUIDE_V1_PROVENANCE_INVALID")
        matches.append({"run_id":int(folder.name),"sha256":digest,
                        "file":file.relative_to(root).as_posix()})
    return max(matches,key=lambda x:x["run_id"]) if matches else None

def read_reference(item:dict,root:Path)->bytes:
    path=Path(item["file"])
    if path.is_absolute() or ".." in path.parts or not path.is_relative_to(REL/"assets"/"geracoes"):
        raise VideoForgeError("GUIDE_V1_UNSAFE_PATH")
    file=root/path
    if file.is_symlink() or not file.is_file():raise VideoForgeError("GUIDE_V1_MISSING_SOURCE")
    blob=file.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=item["sha256"]:
        raise VideoForgeError("GUIDE_V1_BAD_SHA")
    return blob

def prepare(root:Path=ROOT):
    from PIL import Image
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if existing(root):raise VideoForgeError("GUIDE_V1_ALREADY_ARCHIVED")
    aligned=aligned_source(root)
    if aligned["sha256"]!=SHA_ALIGNED:raise VideoForgeError("GUIDE_V1_MOTHER_CHANGED")
    guide_manifest=root/REL/"REFERENCIA-PEGADA-APROVADA-C01-P04-V3.json"
    m=json.loads(guide_manifest.read_text(encoding="utf-8"))
    if (m["source_mother_sha256"]!=SHA_APPROVED
        or m["source_technical_canvas_sha256"]!=SHA_ALIGNED
        or m["approval_scope"]!="grip_reference_only_not_independent_layers"):
        raise VideoForgeError("GUIDE_V1_APPROVAL_SOURCE_MISMATCH")
    guard=existing_part("character-guarda_esquerdo",root)
    spear=existing_part("object-lanca-esquerda",root)
    if not guard or not spear:raise VideoForgeError("GUIDE_V1_GUARD_SPEAR_MISSING")
    with Image.open(BytesIO(aligned["blob"])) as im:
        if im.size!=(941,1672):raise VideoForgeError("GUIDE_V1_CANVAS_CHANGED")
        crop=im.convert("RGB").crop((0,760,375,1230))
        buff=BytesIO();crop.save(buff,"PNG")
        ref= buff.getvalue()
    imgs=[ref,aligned["blob"],read_reference(spear,root),read_reference(guard,root)]
    prompt=(
      "CREATE ONE SINGLE HIGH QUALITY ANATOMICAL CLOSE-UP ILLUSTRATION: "
      "the LEFT royal guard's armoured gauntlet PHYSICALLY HOLDING a REAL "
      "straight wooden spear shaft. Match Image 1 (the exact close-up crop "
      "of the creator-approved, anatomically CORRECT grip) as your primary "
      "reference for how the solid shaft sits within the fist, not beside it. "
      "Image 2 is the full approved throne room for identity and lighting; "
      "Image 3 has the independent spear's exact red-brown wood and gold tip; "
      "Image 4 has the guard armour material, but the grip in this image "
      "is previously REJECTED, do not imitate its closed fist. "
      "The shaft MUST be visibly passing THROUGH the curled fingers and "
      "palm: palm BEHIND the shaft, index/middle/ring/little fingers and "
      "THUMB wrap IN FRONT of the shaft. Fingertips close around its "
      "cylindrical width with natural knuckles and no holes. The spear "
      "extends a LONG visible distance downward PAST the hand to the "
      "lower butt, and upward diagonally RIGHT toward the tip. "
      "The arm/wrist is visibly connected to the hand, with the "
      "same gilded plate steel vambrace and brown leather gloves as "
      "the approved reference. FRAME tightly on hand/forearm and a "
      "long segment of spear, never show throne or a whole person. "
      "ANATOMY FIRST: five fingers including thumb, realistic grip "
      "contours and occlusion, clean contact with no floating staff, "
      "no doubled hands, no split fingers. 2D semi-realistic anime/manhwa "
      "fantasy painterly style and original golden highlights. "
      "This is a NEW single anatomical REFERENCE IMAGE of complete "
      "hand plus real shaft, NOT a final animation layer, and will "
      "be used to generate separate palm, shaft, fingers only after "
      "visual acceptance. No text, no labels, no HUD or other props."
    )
    return {"images":imgs,"prompt":prompt,
            "cropped_reference_sha256":hashlib.sha256(ref).hexdigest(),
            "aligned_source":aligned,"guard":guard,"spear":spear}

def generate(url:str,root:Path=ROOT):
    from PIL import Image
    obj=prepare(root)
    payload={"model":"gpt-image-2","n":1,"size":"1024x1024",
       "background":"opaque","output_format":"png","response_format":"b64_json",
       "stream":False,"prompt":obj["prompt"],
       "images":[{"image_url":"data:image/png;base64,"+
                  base64.b64encode(b).decode("ascii")} for b in obj["images"]]}
    response=proxy_images.call_proxy(url,"/v1/images/edits",
                        os.getenv("CODEX_PROXY_API_KEY",""),payload)
    png,ext=proxy_images.decode_image(response)
    if ext!=".png":raise VideoForgeError("GUIDE_V1_IMAGE_NOT_PNG")
    with Image.open(BytesIO(png)) as im:
        im.load()
        if im.format!="PNG":raise VideoForgeError("GUIDE_V1_INVALID")
        dimensions=list(im.size)
    root=Path(root)
    out=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    file=out/(ASSET+".png")
    meta=out/(ASSET+".production.json")
    if file.exists() or meta.exists():raise VideoForgeError("GUIDE_V1_OUTPUT_EXISTS")
    out.mkdir(parents=True,exist_ok=True)
    file.write_bytes(png)
    digest=hashlib.sha256(png).hexdigest()
    tech="candidate_reference_only"
    if any(x<512 or x>2048 for x in dimensions):
        tech="rejected_unexpected_canvas"
    data={
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "candidate_scene_shot_id":"C01-P04","asset_id":ASSET,
        "sha256":digest,"width":dimensions[0],"height":dimensions[1],
        "approved_grip_reference_sha256":SHA_APPROVED,
        "source_image_sha256":SHA_ALIGNED,
        "source_originals_sha_verified":[
            {"asset_id":"mother_aligned","sha256":SHA_ALIGNED,"path":obj["aligned_source"]["path"]},
            {"asset_id":"spear","sha256":obj["spear"]["sha256"],"path":obj["spear"]["file"]},
            {"asset_id":"guard_older","sha256":obj["guard"]["sha256"],"path":obj["guard"]["file"]}],
        "input_grip_crop_sha256":obj["cropped_reference_sha256"],
        "generation_method":"new_proxy_render_of_complete_hand_and_real_spear_for_reference_only",
        "technical_qa":tech,"actual_finger_shaft_contact_human_approved":False,
        "may_be_used_as_final_animation_asset":False,
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,"provider_image_calls":1,
    }
    meta.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_CANONICAL_GRIP_GUIDE",json.dumps({
       "sha256":digest,"dimensions":dimensions,
       "technical_qa":tech,"approved":False},ensure_ascii=False))
    if tech.startswith("rejected"):
        raise VideoForgeError("GUIDE_V1_REJECTED_BUT_ARCHIVED")
    return data

if __name__=="__main__":
    try:
        generate(os.environ["PROXY_ENDPOINT"])
    except (VideoForgeError,OSError,ValueError,ImportError,proxy_images.ProxyImageError) as exc:
        print("EP01_CANONICAL_GRIP_GUIDE_STOP",str(exc),file=sys.stderr)
        sys.exit(2)
