"""EP01 V3: three geography-specific visual-bible backgrounds, then eleven scene mothers.

Exactly ONE provider request per child run. Archived SHA proof is mandatory.
Never overwrite V2 assets, approve shots, unlock rigs, or publish YouTube.
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

from .errors import VideoForgeError
from .image_generation_policy import assert_image_generation_allowed
from .production_art import archived_reference
from .scene_layers import png_info
from . import proxy_images

ROOT = Path(__file__).resolve().parents[1]
EP = Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
PLAN_FILE = "CORRECAO-CENARIOS-TRONO-V3.json"
SHOT_PRODUCER = "production-continuity-v3-mother"
EXPECTED_SHOTS = (
    "C01-P03", "C01-P05", "C07-P03", "C07-P04", "C08-P01", "C08-P02",
    "C08-P03", "C08-P04", "C08-P05", "C09-P01", "C09-P02"
)
EXPECTED_PLACES = (
    "biblia-largo-encontro-arken-v3",
    "biblia-gargalo-servico-arken-v3",
    "biblia-escadaria-saida-arken-v3"
)
SHA = re.compile(r"^[a-f0-9]{64}$")


def load_plan(root=ROOT):
    data=json.loads((Path(root)/EP/PLAN_FILE).read_text(encoding="utf-8"))
    settings=data["art_generation_policy"]
    if (data.get("schema")!="videoforge/ep01-shot-continuity-v3/v1"
        or data.get("shots_total")!=42 or data.get("frames_total")!=4890
        or data.get("fps")!=30 or data.get("parent_revision")!="continuity-v2"
        or [x["id"] for x in data["backgrounds"]]!=list(EXPECTED_PLACES)
        or [x["id"] for x in data["shots"]]!=list(EXPECTED_SHOTS)
        or settings.get("calls_per_action_max")!=1
        or settings.get("do_not_retry_429") is not True
        or data.get("originals_never_overwritten") is not True
        or data["throne"].get("anchor")!="C01-P04"
        or data["throne"].get("king_posture") !=
            "Aldric seated throughout C01-P03/C01-P04/C01-P05/C02-P01/C02-P02"
        or "C01-P04" not in data.get("original_approved_visuals_preserved",[])
        or set(data["forbidden_outputs"]) !=
           {"youtube_upload","autonomous_human_visual_approval","automatic_rig_approval"}):
        raise ValueError("EP01_V3_PLAN_OR_SAFETY_INVALID")
    for shot in data["shots"]:
        if (shot.get("source_policy")!="generate" or shot.get("legacy_source_locked") is not True
            or shot.get("human_visual_approval") is not False
            or shot.get("rig_ready") is not False or shot.get("youtube_uploaded") is not False
            or not isinstance(shot.get("prompt"),str) or len(shot["prompt"])<130
            or not 1<=len(shot.get("ref",[]))<=7):
            raise ValueError("EP01_V3_SHOT_INVALID")
    for place in data["backgrounds"]:
        if (place.get("kind")!="background_reference"
            or not place.get("reference_asset_ids") or len(place["prompt"])<130):
            raise ValueError("EP01_V3_PLACE_INVALID")
    safe={x["id"] for x in data["backgrounds"]}
    for shot in data["shots"]:
        if shot["location"] not in safe and shot["location"] != "sala-do-trono":
            raise ValueError("EP01_V3_UNMAPPED_LOCATION")
        if shot["location"] in safe and shot["location"] not in shot["ref"]:
            raise ValueError("EP01_V3_BACKGROUND_NOT_ATTACHED")
    if set(data["shots"][6]["ref"])!={EXPECTED_PLACES[1],"biblia-carrinho-base-v1"}:
        raise ValueError("EP01_V3_CART_ALONE_NO_HUMANS")
    return data


def rows(root=ROOT):
    doc=load_plan(root)
    return {row["id"]:row for row in doc["backgrounds"]+doc["shots"]}


def is_background(asset_id):
    return asset_id in EXPECTED_PLACES


def filename(asset_id):
    if is_background(asset_id):
        return asset_id+".png"
    if asset_id not in EXPECTED_SHOTS:
        raise ValueError("EP01_V3_UNEXPECTED_SHOT")
    return asset_id.lower()+"-continuity-v3-scene-mother.png"


def producer(asset_id):
    if is_background(asset_id):
        return "production-art-request-"+asset_id
    if asset_id not in EXPECTED_SHOTS:
        raise ValueError("EP01_V3_INVALID_ASSET")
    return SHOT_PRODUCER


def archived(asset_id,root=ROOT):
    root=Path(root)
    if asset_id not in rows(root):
        raise ValueError("EP01_V3_UNKNOWN_ASSET")
    # Backgrounds must be known by archived_reference, which verifies
    # the permanent manifest and PNG before allowing further use.
    if is_background(asset_id):
        hit=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",asset_id,root)
        if not hit:
            return None
        return {"file":str(EP/hit["path"]),"sha256":hit["sha256"],
                "dimensions":[hit["width"],hit["height"]],"run_id":hit["run_id"],
                "human_visual_approval":False}
    folder=root/EP/"assets"/"geracoes"/SHOT_PRODUCER
    if folder.is_symlink():
        raise ValueError("EP01_V3_ARCHIVE_SYMLINK")
    if not folder.exists():
        return None
    found=[]
    for run in folder.iterdir():
        if run.is_symlink() or not run.is_dir() or not run.name.isdigit():
            raise ValueError("EP01_V3_RUN_PATH_UNSAFE")
        path=run/filename(asset_id)
        manifest=run/"manifesto-geracoes.json"
        if path.is_symlink() or manifest.is_symlink():
            raise ValueError("EP01_V3_ARCHIVE_SOURCE_SYMLINK")
        if not path.exists():
            continue
        if not manifest.is_file():
            raise ValueError("EP01_V3_ARCHIVE_INCOMPLETE")
        doc=json.loads(manifest.read_text(encoding="utf-8"))
        matches=[r for r in doc.get("images",[]) if r.get("file")==path.name]
        if (doc.get("schema")!="videoforge/permanent-generated-image-archive/v1"
            or doc.get("channel")!="alchemy-lab"
            or doc.get("video_id")!="mmorpg-conquiste-a-princesa-ep01"
            or doc.get("producer")!=SHOT_PRODUCER
            or doc.get("github_run_id")!=int(run.name)
            or len(matches)!=1):
            raise ValueError("EP01_V3_MANIFEST_BAD")
        blob=path.read_bytes()
        info=png_info(blob,require_alpha=False)
        digest=hashlib.sha256(blob).hexdigest()
        if (digest!=matches[0]["sha256"]
            or [info["width"],info["height"]]!=
                [matches[0]["width"],matches[0]["height"]]):
            raise ValueError("EP01_V3_ARCHIVED_SHA_BAD")
        found.append({"file":str(path.relative_to(root)).replace("\\","/"),
                      "sha256":digest,
                      "dimensions":[info["width"],info["height"]],
                      "run_id":int(run.name),"human_visual_approval":False})
    return max(found,key=lambda x:x["run_id"]) if found else None


def prepare(asset_id,root=ROOT):
    root=Path(root)
    doc=rows(root)
    if asset_id not in doc:
        raise ValueError("EP01_V3_UNKNOWN_ASSET")
    if archived(asset_id,root):
        raise ValueError("EP01_V3_ALREADY_ARCHIVED_NO_REPLAY")
    item=doc[asset_id]
    ids=item["reference_asset_ids"] if is_background(asset_id) else item["ref"]
    refs=[]
    blobs=[]
    for ref_id in ids:
        row=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",ref_id,root)
        if row is None:
            raise ValueError("EP01_V3_REFERENCE_NOT_YET_ARCHIVED "+ref_id)
        source=root/EP/row["path"]
        if (source.is_symlink() or not source.is_file()
            or not source.resolve().is_relative_to((root/EP).resolve())):
            raise ValueError("EP01_V3_UNSAFE_REFERENCE")
        data=source.read_bytes()
        if hashlib.sha256(data).hexdigest()!=row["sha256"]:
            raise ValueError("EP01_V3_REFERENCE_SHA_MISMATCH")
        refs.append({"id":ref_id,"sha256":row["sha256"]})
        blobs.append(data)
    if item.get("reference_scene_shot_id"):
        # C01-P04 is the creator-approved ANCHOR: read and verify real PNG and SHA,
        # attach it, never modify it. No fallback to generic throne portraits.
        from .ep01_camera_batch import build_plan,checked_source
        shot=next(s for s in build_plan(root,"continuity-v2")["shots"]
                  if s["id"]==item["reference_scene_shot_id"])
        if shot["approval_status"]!="exact_sha_approval_record_exists":
            raise ValueError("EP01_V3_THRONE_ANCHOR_NOT_APPROVED")
        checked_source(root,shot["source"])
        raw=(root/shot["source"]["file"]).read_bytes()
        blobs.append(raw)
        refs.append({"id":"approved-scene-C01-P04","sha256":shot["source"]["sha256"]})
    prefix=("ENVIRONMENTAL CONCEPT REFERENCE 9:16. DRAW ONLY EMPTY BACKGROUND, no "
            "people, no silhouettes, no cart, no text, no logos, preserve medieval "
            "anime/manhwa style but create a genuinely DISTINCT street location. "
            if is_background(asset_id) else
            "SINGLE COHERENT FRAME 9:16 fantasy anime/manhwa drama, use the "
            "actual SHA-pinned images provided for facial/wardrobe architecture "
            "continuity. No split panels, no subtitles, no background repetition. "
            "The shot inherits its NEW LOCATION from its own V3 reference. "
            "Never introduce extra guards, duplicate body parts, false hand grip "
            "or unrequested cart. If throne is shown Aldric remains seated. ")
    prompt=(prefix+f"ASSET {asset_id}. "+item["prompt"]+
       " Candidate for human review only. No automatic art or rig approval.")
    return item,blobs,refs,prompt


def generate(asset_id,url,root=ROOT):
    root=Path(root)
    assert_image_generation_allowed("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",root)
    item,blobs,refs,prompt=prepare(asset_id,root)
    data=proxy_images.call_proxy(url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),{
        "model":"gpt-image-2","prompt":prompt,
        "size":"1024x1536","n":1,"background":"opaque",
        "output_format":"png","response_format":"b64_json","stream":False,
        "images":[{"image_url":"data:image/png;base64,"+
                    base64.b64encode(x).decode("ascii")} for x in blobs]
    })
    blob,ext=proxy_images.decode_image(data)
    if ext!=".png":
        raise ValueError("EP01_V3_NOT_PNG")
    info=png_info(blob,require_alpha=False)
    if not 512<=info["width"]<=2048 or not 512<=info["height"]<=3072:
        raise ValueError("EP01_V3_UNEXPECTED_CANVAS")
    if info["width"]>=info["height"]:
        raise ValueError("EP01_V3_NOT_PORTRAIT")
    directory=root/"output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/imagens"
    directory.mkdir(parents=True,exist_ok=True)
    filename_=filename(asset_id)
    path=directory/filename_
    if path.exists() or path.is_symlink():
        raise ValueError("EP01_V3_NO_OVERWRITE")
    path.write_bytes(blob)
    digest=hashlib.sha256(blob).hexdigest()
    proof={
        "schema":"videoforge/ep01-background-and-shot-v3/v1",
        "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
        "asset_id":path.stem,
        "visual_bible_reference_id":asset_id if is_background(asset_id) else None,
        "candidate_scene_shot_id":asset_id if not is_background(asset_id) else None,
        "source_originals_sha_verified":refs,
        "sha256":digest,"width":info["width"],"height":info["height"],
        "kind":"environment_reference" if is_background(asset_id) else "scene_mother",
        "generation_method":"proxy_generated_separate_versioned_image",
        "source_revision":"v3",
        "human_visual_approval":False,"rig_ready":False,
        "youtube_uploaded":False,"official_mp4":False,
        "provider_image_calls":1
    }
    path.with_suffix(".production.json").write_text(
        json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"asset":asset_id,"sha256":digest,"file":filename_,
            "kind":proof["kind"],"approved":False}


def revised_camera_plan(v2_plan,root=ROOT,require_generated=True):
    doc=load_plan(root)
    if (len(v2_plan.get("shots",[]))!=42 or
        sum(s["duration_frames"] for s in v2_plan["shots"])!=4890):
        raise ValueError("EP01_V3_BAD_V2_BASE")
    candidates={s["id"]:s for s in doc["shots"]}
    shots=[]
    for shot in v2_plan["shots"]:
        row=dict(shot)
        if row["id"] in candidates:
            # Remove stale V2 blocking/motion labels tied to the rejected scene.
            # V3 gets new source-specific QA before any rig can be enabled.
            row.pop("continuity_gate",None)
            source=archived(row["id"],root)
            if source is None and require_generated:
                raise ValueError("EP01_V3_MOTHER_PENDING "+row["id"])
            row["source"]=source
            row["revision"]="continuity-v3"
            row["narrative_beat"]=candidates[row["id"]]["prompt"][:125]
            row["approval_status"]="candidate_v3_pending_creator_review"
            row["direction_reviewed"]=False
            row["rig"]={"enabled":False,"independent_hands":False,"required_components":[]}
            row["qa_required"]=list(dict.fromkeys(
                row.get("qa_required",[])+["location_distinctness_and_crosscut_king_pose_review"]))
            row["camera"]={"mode":"continuity_v3_review","start":{"zoom":1,"x":50,"y":50},
                           "end":{"zoom":1.015,"x":50,"y":50},
                           "dolly":0,"true_parallax":False}
            row["lighting"]={"exposure_start":1,"exposure_end":1,"warm_glow":0}
            row["focus"]={"mode":"original_painted_focus",
                          "blur_start_px":0,"blur_end_px":0}
            row["location_v3"]=candidates[row["id"]]["location"]
        shots.append(row)
    anchor=next(x for x in shots if x["id"]=="C01-P04")
    pinned=next(x for x in v2_plan["shots"] if x["id"]=="C01-P04")
    if anchor["source"]!=pinned["source"] or anchor["approval_status"]!=pinned["approval_status"]:
        raise ValueError("EP01_V3_ANCHOR_CHANGED")
    result=dict(v2_plan)
    result["shots"]=shots
    result["revision"]="continuity-v3"
    result["visual_approval_pending"]=True
    result["rig_approved"]=False
    result["youtube_upload"]=False
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asset-id")
    p.add_argument("--url")
    p.add_argument("--check",action="store_true")
    p.add_argument("--print-producer",action="store_true")
    args=p.parse_args()
    try:
        if args.check:
            doc=load_plan()
            print(json.dumps({"new_backgrounds":len(doc["backgrounds"]),
                              "new_mothers":len(doc["shots"]),
                              "v3_shots_total":42,"fps":30,"frames":4890,
                              "youtube_upload":False}))
            return 0
        if args.print_producer:
            if not args.asset_id:
                p.error("--asset-id required")
            print(producer(args.asset_id))
            return 0
        if not args.asset_id or not args.url:
            p.error("--asset-id and --url required")
        print("EP01_V3_IMAGE_CANDIDATE",json.dumps(
            generate(args.asset_id,args.url),ensure_ascii=False))
        return 0
    except (OSError,ValueError,VideoForgeError,proxy_images.ProxyImageError) as exc:
        print("EP01_V3_STOP_NO_AUTORETRY",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
