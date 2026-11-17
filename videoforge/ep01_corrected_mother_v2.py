"""Versioned repairs for rejected C01-P03/P04 shot mother images.

New output pixels come only from Codex Image Proxy edits with the rejected
mother and SHA-verified Bible references attached. No in-place alterations,
no masks/crops for final art, no approvals or rig. One paid call per run.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from . import image_generation_policy,proxy_images
from .errors import VideoForgeError
from .ep01_shot_mother import existing_mother,read_refs,ARCHIVE_PRODUCER,MAX_REFERENCE_PNGS_PER_REQUEST
from .production_art import archived_reference
from .layered_shot_plan import ROOT,REL,CHANNEL,VIDEO,validate as validate_plan
from .scene_layers import png_info

PRODUCER="production-scene-mother-repair-v2"
SCHEMA="videoforge/ep01-versioned-mother-repair/v1"
REJECTED_SOURCES={
    "C01-P03":"89bc3b1b214fe5286a196171c0dc498041cd29edcf622520ecc25c24b3805765",
    "C01-P04":"156a9376298166045654706e75b876a20b7f8201c70d6d494ae9a2b7465f5ab3"
}
SHOT_PROMPTS={
    "C01-P03":(
       "Correct the attached C01-P03 frame: Kael MUST remain KNEELING "
       "in the lower foreground, anatomically connected limbs and knee on "
       "floor, head bowed, king Aldric farther back in middle distance "
       "before ornate throne. REMOVE BOTH GUARDS and their CROSSING "
       "SPEARS entirely from this shot and restore the stairs, stained "
       "glass, banners, floor and throne behind them. REMOVE the giant "
       "foreground sword as well. Only Kael and Aldric belong in this "
       "C01-P03 low-angle shot; guards and spears will be introduced in "
       "C01-P04. Keep body and outfit scale, camera perspective, facial "
       "design, red cloak, royal robes, beard, light and background "
       "identity matching the Bible. Never recenter or enlarge people."
    ),
    "C01-P04":(
       "Correct the attached C01-P04 wide establishing shot: Kael is "
       "WRONGLY STANDING in source. Draw Kael physically KNEELING on "
       "the floor at the center in the lower foreground, with at least "
       "one knee planted, bent hip and realistic aligned lower legs, "
       "bowed head. Do not leave standing duplicate silhouette. "
       "King Aldric stays SEATED on his gold throne. Guards remain "
       "on left and right: each gloved hand wraps its OWN spear shaft "
       "near its LOWER THIRD/BASE with visible fingers and thumb, "
       "shafts crossing in an X HIGH ABOVE Kael. Preserve existing "
       "composition, distant king position, lighting, individual armor, "
       "spear material, red plumes and physical occlusions. "
       "Do not change costumes, face, guard count or camera angle."
    )
}


def existing_repair(shot_id:str,root:Path=ROOT)->dict|None:
    root=Path(root)
    archive=root/REL/"assets"/"geracoes"/PRODUCER
    filename=shot_id.lower()+"-scene-mother-v2.png"
    if archive.is_symlink():
        raise VideoForgeError("EP01_MOTHER_V2_ARCHIVE_SYMLINK")
    if not archive.exists(): return None
    found=[]
    for folder in archive.iterdir():
        if folder.is_symlink(): raise VideoForgeError("EP01_MOTHER_V2_RUN_SYMLINK")
        if not folder.is_dir() or not folder.name.isdecimal(): continue
        file=folder/filename
        if not file.exists(): continue
        manifest=folder/"manifesto-geracoes.json"
        if file.is_symlink() or manifest.is_symlink() or not manifest.is_file():
            raise VideoForgeError("EP01_MOTHER_V2_ARCHIVE_INCOMPLETE")
        record=json.loads(manifest.read_text(encoding="utf-8"))
        matching=[x for x in record.get("images",[]) if x.get("file")==filename]
        digest=hashlib.sha256(file.read_bytes()).hexdigest()
        if (record.get("producer")!=PRODUCER or
            record.get("channel")!=CHANNEL or record.get("video_id")!=VIDEO or
            record.get("github_run_id")!=int(folder.name) or
            len(matching)!=1 or matching[0].get("sha256")!=digest):
            raise VideoForgeError("EP01_MOTHER_V2_ARCHIVE_PROVENANCE_MISMATCH")
        found.append({"run_id":int(folder.name),"sha256":digest})
    return max(found,key=lambda x:x["run_id"]) if found else None


def prepare(shot_id:str,root:Path=ROOT)->dict:
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if shot_id not in REJECTED_SOURCES:
        raise VideoForgeError("EP01_MOTHER_V2_UNAPPROVED_SHOT")
    validate_plan(root)
    timeline=json.loads((root/REL/"PLANO-CAMADAS-CAMERA-EP01.json").read_text(encoding="utf-8"))
    shot=next(x for x in timeline["shots"] if x["id"]==shot_id)
    if (shot.get("qa",{}).get("require_versioned_mother_v2_before_more_proxy_parts") is not True or
        shot.get("qa",{}).get("source_v1_visual_review")!="rejected_2026-11-17" or
        shot.get("images",{}).get("mother_v1_sha256")!=REJECTED_SOURCES[shot_id]):
        raise VideoForgeError("EP01_MOTHER_V2_REJECTION_EVIDENCE_MISSING")
    if existing_repair(shot_id,root):
        raise VideoForgeError("EP01_MOTHER_V2_ALREADY_ARCHIVED_NO_REPEAT")
    mother=existing_mother(shot_id,root)
    if not mother or mother.get("sha256")!=REJECTED_SOURCES[shot_id]:
        raise VideoForgeError("EP01_MOTHER_V2_REJECTED_MOTHER_NOT_MATCHED")
    path=REL/"assets"/"geracoes"/ARCHIVE_PRODUCER/str(mother["run_id"])/(shot_id.lower()+"-scene-mother.png")
    file=root/path
    if file.is_symlink() or not file.is_file() or file.stat().st_size>35_000_000:
        raise VideoForgeError("EP01_MOTHER_V2_SOURCE_MISSING")
    source=file.read_bytes()
    if hashlib.sha256(source).hexdigest()!=mother["sha256"]:
        raise VideoForgeError("EP01_MOTHER_V2_REJECTED_SOURCE_SHA_INVALID")
    refdoc=read_refs(root)
    row=next(x for x in refdoc["shots"] if x["id"]==shot_id)
    references=[];blobs=[]
    for asset in row["reference_asset_ids"]:
        item=archived_reference(CHANNEL,VIDEO,asset,root)
        if not item: raise VideoForgeError("EP01_MOTHER_V2_BIBLE_MISSING "+asset)
        ref=Path(item["path"])
        if ref.is_absolute() or ".." in ref.parts: raise VideoForgeError("EP01_MOTHER_V2_BIBLE_PATH")
        p=root/REL/ref
        if p.is_symlink() or not p.is_file() or p.stat().st_size>35_000_000:
            raise VideoForgeError("EP01_MOTHER_V2_BIBLE_MISSING_FILE")
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item["sha256"]:
            raise VideoForgeError("EP01_MOTHER_V2_BIBLE_SHA_MISMATCH")
        blobs.append(raw)
        references.append({"asset_id":asset,"sha256":item["sha256"],
                           "path":str(REL/ref)})
    if len(blobs)+1>MAX_REFERENCE_PNGS_PER_REQUEST:
        raise VideoForgeError("EP01_MOTHER_V2_TOO_MANY_WIRE_REFERENCES")
    prompt=(
        "Generate exactly ONE new FULL PORTRAIT FRAME of medieval fantasy "
        "cinematic semirealistic anime, using IMAGE ONE as the exact "
        "C01-P0x original to CORRECT, and remaining images as original "
        "SHA-verified Visual Bible references, not collage. "
        "Fix ONLY the visual continuity errors below. "
        f"Shot {shot_id}. {SHOT_PROMPTS[shot_id]} "
        "Do not create character turnarounds, pose sheets, split panes, "
        "watermarks, captions, HUD or background artifacts. "
        "Output original framing, 9:16 portrait, coherent hands/feet, "
        "perspective, lighting, material texture. "
        "After the new mother is eventually approved, ANOTHER proxy call "
        "will generate independent RGBA assets for characters and props. "
        "DO NOT create sprites by local pixel crops. "
        "This is a CANDIDATE for visual approval, NOT final rig art."
    )
    if len(prompt)>5000: raise VideoForgeError("EP01_MOTHER_V2_PROMPT_TOO_LONG")
    return {"shot":shot_id,"source":source,"source_sha":mother["sha256"],
            "source_path":str(path),"refs":references,"blobs":blobs,
            "prompt":prompt,"source_canvas":[941,1672]}


def generate(shot_id:str,url:str,model:str="gpt-image-2",root:Path=ROOT)->dict:
    if model!="gpt-image-2":
        raise VideoForgeError("EP01_MOTHER_V2_MODEL_NOT_ALLOWED")
    spec=prepare(shot_id,root)
    name=shot_id.lower()+"-scene-mother-v2"
    out=Path(root)/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    png=out/(name+".png");meta=out/(name+".production.json")
    if any(p.exists() or p.is_symlink() for p in (png,meta)):
        raise VideoForgeError("EP01_MOTHER_V2_OUTPUT_ALREADY_EXISTS")
    images=[spec["source"]]+spec["blobs"]
    payload={"model":model,"prompt":spec["prompt"],"n":1,
             "size":"1024x1536","background":"opaque",
             "output_format":"png","response_format":"b64_json","stream":False,
             "images":[{"image_url":"data:image/png;base64,"+
                        base64.b64encode(raw).decode("ascii")} for raw in images]}
    answer=proxy_images.call_proxy(
       url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),payload)
    raw,ext=proxy_images.decode_image(answer)
    if ext!=".png":
        raise VideoForgeError("EP01_MOTHER_V2_PROVIDER_NOT_PNG")
    info=png_info(raw,require_alpha=False)
    qa="candidate_valid_png_no_visual_approval" if (info["width"],info["height"])==tuple(spec["source_canvas"]) else "rejected_canvas_mismatch"
    out.mkdir(parents=True,exist_ok=True)
    png.write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    record={
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,"asset_id":name,
        "candidate_scene_shot_id":shot_id,"sha256":sha,
        "source_image_sha256":spec["source_sha"],
        "source_originals_sha_verified":[
            {"asset_id":shot_id.lower()+"-scene-mother","sha256":spec["source_sha"],
             "path":spec["source_path"]},*spec["refs"]],
        "source_images_attached_to_request":len(images),
        "generation_method":"proxy_edited_versioned_scene_mother",
        "source_canvas":spec["source_canvas"],"output_canvas":[info["width"],info["height"]],
        "technical_qa":qa,
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,"provider_image_calls":1
    }
    meta.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_VERSIONED_MOTHER_V2",json.dumps({
        "shot":shot_id,"sha256":sha,"qa":qa,"paid_calls":1,
        "human_visual_approval":False}))
    if qa.startswith("rejected"):
        raise VideoForgeError("EP01_MOTHER_V2_REJECTED_QA_BUT_ARCHIVED "+qa)
    return record


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--shot-id",required=True)
    p.add_argument("--url",required=True)
    a=p.parse_args()
    try:
        generate(a.shot_id,a.url)
    except (OSError,ValueError,VideoForgeError,proxy_images.ProxyImageError) as exc:
        print("EP01_MOTHER_V2_STOPPED",str(exc),file=sys.stderr)
        raise SystemExit(2)


if __name__=="__main__":
    main()
