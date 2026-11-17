"""Corrective V2: new separate REAR PALM, using real-shaft grip guide.

The anatomical grip guide is a candidate reference, not an approved rig asset.
All source bytes are SHA verified. Never crop an approved PNG into a final sprite.
"""
from __future__ import annotations
import base64
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import sys
from PIL import Image
from . import image_generation_policy,proxy_images
from .errors import VideoForgeError
from .ep01_approved_v3_parts import aligned_source,existing_part
from .layered_shot_plan import ROOT,REL,CHANNEL,VIDEO

SCHEMA="videoforge/ep01-c01p04-rear-palm-revision/v2"
PRODUCER="production-c01p04-v3-grip-occlusion-rear-v2"
ASSET="c01-p04-v3-left-grip-palm-rear-v2"
GUIDE_SHA="eaeafebd244b9059006b7cfe74dcc4ebeeecf3471102283f883c52ad8032e16c"
V1_REJECTED_SHA="71ddc2931b41f4083af7f548dcee49a63acd2314e6c7fa854deeac8ff3908993"
MOTHER_SHA="b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
APPROVED_SHA="a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
GUIDE_PATH=REL/"assets"/"geracoes"/"production-c01p04-v3-canonical-grip-guide-v1"/"44183662671"/"c01-p04-v3-left-grip-with-real-spear-reference-v1.png"
REJECT_PATH=REL/"assets"/"geracoes"/"production-c01p04-v3-grip-occlusion-v1"/"44182186174"/"c01-p04-v3-left-grip-palm-rear-v1.png"

def verified(path:Path,expected:str,root:Path=ROOT)->bytes:
    if path.is_absolute() or ".." in path.parts or not path.is_relative_to(REL/"assets"/"geracoes"):
        raise VideoForgeError("REAR_V2_UNSAFE_REFERENCE_PATH")
    full=Path(root)/path
    if full.is_symlink() or not full.is_file():raise VideoForgeError("REAR_V2_SOURCE_MISSING")
    blob=full.read_bytes()
    if sha256(blob).hexdigest()!=expected:raise VideoForgeError("REAR_V2_SOURCE_SHA_INVALID")
    return blob

def previous(root:Path=ROOT):
    parent=Path(root)/REL/"assets"/"geracoes"/PRODUCER
    if not parent.exists():return None
    records=[]
    for d in parent.iterdir():
        if not d.is_dir() or not d.name.isdecimal():continue
        p=d/(ASSET+".png");meta=p.with_suffix(".production.json")
        m=d/"manifesto-geracoes.json"
        if not p.exists():continue
        if any(x.is_symlink() or not x.is_file() for x in (p,meta,m)):
            raise VideoForgeError("REAR_V2_ARCHIVE_INCOMPLETE")
        digest=sha256(p.read_bytes()).hexdigest()
        doc=json.loads(meta.read_text(encoding="utf-8"))
        manifest=json.loads(m.read_text(encoding="utf-8"))
        matches=[x for x in manifest.get("images",[]) if x.get("file")==p.name]
        if (doc.get("sha256")!=digest
            or doc.get("schema")!=SCHEMA
            or manifest.get("producer")!=PRODUCER
            or len(matches)!=1 or matches[0].get("sha256")!=digest):
            raise VideoForgeError("REAR_V2_ARCHIVE_INVALID")
        records.append({"run_id":int(d.name),"sha256":digest})
    return max(records,key=lambda x:x["run_id"]) if records else None

def prepare(root:Path=ROOT)->dict:
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if previous(root):raise VideoForgeError("REAR_V2_ALREADY_GENERATED_NO_REPEAT")
    guide=verified(GUIDE_PATH,GUIDE_SHA,root)
    rejected=verified(REJECT_PATH,V1_REJECTED_SHA,root)
    aligned=aligned_source(root)
    if aligned["sha256"]!=MOTHER_SHA:raise VideoForgeError("REAR_V2_APPROVED_ALIGNMENT_CHANGED")
    qa=json.loads((root/REL/"QA-C01-P04-V3-GUIA-PEGADA-V1.json").read_text(encoding="utf-8"))
    if (qa.get("source_sha256")!=GUIDE_SHA
        or qa.get("human_visual_approval") is not False
        or qa.get("rig_ready") is not False):
        raise VideoForgeError("REAR_V2_GUIDE_QA_INVALID")
    spear=existing_part("object-lanca-esquerda",root)
    if not spear:raise VideoForgeError("REAR_V2_SPEAR_REFERENCE_MISSING")
    spearpath=Path(spear["file"])
    spear_blob=verified(spearpath,spear["sha256"],root)
    with Image.open(BytesIO(aligned["blob"])) as im:
        ref=im.convert("RGB").crop((0,760,375,1230))
        buff=BytesIO();ref.save(buff,"PNG")
    guide_crop=buff.getvalue()
    prompt=(
      "YOU ARE CREATING ONLY ONE BACK-HALF OF A REAL GRASPING HAND. "
      "Produce fresh semi-realistic anime/manhwa fantasy RGBA artwork. "
      "Image 1 is a close-up anatomical guide where fingers ACTUALLY "
      "wrap around a visible wooden spear. Image 2 is the same approved "
      "mother's close-up (true reference). Image 3 is a PREVIOUSLY REJECTED "
      "PNG showing a FULL CLOSED FIST: DO NOT COPY ITS FINGERS. Image 4 "
      "is the real independent spear reference. Image 5 is the approved "
      "full throne mother, for exact small hand position/lighting. "
      "Your output is NOT the complete fist. Draw ONLY the REAR exposed "
      "PALM / BACK OF GLOVE and a short gauntlet WRIST segment, positioned "
      "near x=175,y=970 on the portrait full-scene 941x1672 coordinate "
      "system. The palm surface sits BEHIND an imaginary continuous "
      "diagonal spear shaft. The rear piece must have a noticeable "
      "C-shaped OPEN EMPTY SPACE where a cylindrical wooden shaft would "
      "pass through, while the far-side palm wraps behind it. "
      "DELETE ALL VISIBLE FINGERS, all knuckle plates, all curled fingertips "
      "and all front-side thumb geometry from this particular output: "
      "those are drawn later as a completely different front RGBA image. "
      "DO NOT DRAW A CLENCHED FIST OR FOLDED KNUCKLES. "
      "DO NOT DRAW THE SPEAR: its independent sprite is composed above "
      "this palm. Do not add throne, floor, cloak, text, or backgrounds. "
      "Do not draw a detached disembodied finger, enlarged gauntlet, "
      "second hand, or a close-up filling the canvas. The palm and cuff "
      "must align naturally to the original guard's arm and remain SMALL "
      "in the full scene. True alpha=0 outside the palm+wrist silhouette. "
      "Output is a NEW fully independent transparent PNG, NOT a crop "
      "or deletion mask of the approved mother. QA candidate only: no rig."
    )
    return {"images":[guide,guide_crop,rejected,spear_blob,aligned["blob"]],
            "prompt":prompt,"spear_sha":spear["sha256"],
            "guide_crop_sha":sha256(guide_crop).hexdigest()}

def generate(url:str,root:Path=ROOT):
    spec=prepare(root)
    payload={
       "model":"gpt-image-2","n":1,"size":"1024x1536","background":"transparent",
       "output_format":"png","response_format":"b64_json","stream":False,
       "prompt":spec["prompt"],
       "images":[{"image_url":"data:image/png;base64,"+base64.b64encode(x).decode("ascii")}
                 for x in spec["images"]]
    }
    reply=proxy_images.call_proxy(url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),payload)
    raw,ext=proxy_images.decode_image(reply)
    if ext!=".png":raise VideoForgeError("REAR_V2_PROVIDER_NOT_PNG")
    with Image.open(BytesIO(raw)) as im:
        im.load()
        if im.format!="PNG":raise VideoForgeError("REAR_V2_BAD_PNG")
        hasalpha="A" in im.getbands()
        dims=list(im.size)
        rgba=im.convert("RGBA")
    issues=[]
    if not hasalpha or rgba.getchannel("A").getextrema()[0]!=0:
        issues.append("no_true_alpha")
    if min(dims)<512 or max(dims)>3072:
        issues.append("bad_canvas")
    box=rgba.getchannel("A").point(lambda a:255 if a>=16 else 0).getbbox()
    if box is None or (box[3]-box[1])/dims[1]>0.55:
        issues.append("empty_or_full_frame_hand")
    folder=Path(root)/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    png=folder/(ASSET+".png")
    proof=folder/(ASSET+".production.json")
    if png.exists() or proof.exists():raise VideoForgeError("REAR_V2_OUTPUT_EXISTS")
    folder.mkdir(parents=True,exist_ok=True)
    png.write_bytes(raw)
    digest=sha256(raw).hexdigest()
    record={
       "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
       "candidate_scene_shot_id":"C01-P04","asset_id":ASSET,
       "sha256":digest,"width":dims[0],"height":dims[1],
       "alpha_bbox_xyxy":list(box) if box else None,
       "technical_qa":"candidate_pending_real_grip_review" if not issues
           else "rejected_"+",".join(issues),
       "source_image_sha256":MOTHER_SHA,
       "approved_original_sha256":APPROVED_SHA,
       "grip_guide_reference_sha256":GUIDE_SHA,
       "rejected_v1_source_sha256":V1_REJECTED_SHA,
       "spear_reference_sha256":spec["spear_sha"],
       "closeup_reference_sha256":spec["guide_crop_sha"],
       "fresh_generated_rgba_not_pixel_cutout":True,
       "fingers_must_be_absent_requires_visual_qa":True,
       "front_fingers_independent_not_generated_yet":True,
       "provider_image_calls":1,"human_visual_approval":False,
       "hand_contact_verified":False,"rig_ready":False,
       "mp4_generated":False,"youtube_uploaded":False
    }
    proof.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_REAR_PALM_V2",json.dumps({
        "sha256":digest,"canvas":dims,"bbox":record["alpha_bbox_xyxy"],
        "qa":record["technical_qa"],"approved":False},ensure_ascii=False))
    if issues:raise VideoForgeError("REAR_V2_REJECTED_BUT_SAVED "+",".join(issues))
    return record

if __name__=="__main__":
    try:generate(os.environ["PROXY_ENDPOINT"])
    except (VideoForgeError,OSError,ValueError,ImportError,proxy_images.ProxyImageError) as e:
        print("EP01_REAR_PALM_V2_STOP",str(e),file=sys.stderr)
        sys.exit(2)
