"""EP01: ask the image proxy to DRAW one independent shot component per run.

Never use crop, polygon alpha mask, source pixel extraction or segmentation
to produce sprites. Mother + Bible images are references for fresh AI-generated
background / RGBA character / object. Artifacts remain unapproved candidates.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys

from . import image_generation_policy, proxy_images
from .ep01_shot_mother import existing_mother, read_refs, ARCHIVE_PRODUCER, MAX_REFERENCE_PNGS_PER_REQUEST
from .production_art import archived_reference
from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO, validate as validate_plan
from .scene_layers import png_info

PRODUCER = "production-proxy-separate-part-v1"
SCHEMA = "videoforge/ep01-proxy-separate-part/v1"
SHOT = re.compile(r"^C\d\d-P\d\d$")
PART = re.compile(r"^(background-clean|character-[a-z0-9_-]+|object-[a-z0-9_-]+)$")


def read_shot(shot_id: str, part_id: str, root: Path = ROOT) -> tuple[dict,dict]:
    validate_plan(root)
    if not isinstance(shot_id, str) or not SHOT.fullmatch(shot_id) or shot_id=="C01-P01":
        raise VideoForgeError("EP01_PROXY_PARTS_INVALID_SHOT")
    if not isinstance(part_id, str) or not PART.fullmatch(part_id):
        raise VideoForgeError("EP01_PROXY_PARTS_INVALID_COMPONENT")
    plan=json.loads((Path(root)/REL/"PLANO-CAMADAS-CAMERA-EP01.json").read_text(encoding="utf-8"))
    shot=next((x for x in plan["shots"] if x["id"]==shot_id),None)
    if not shot:
        raise VideoForgeError("EP01_PROXY_PARTS_SHOT_NOT_FOUND")
    requests=[x for x in shot["images"]["proxy_generation_requests"] if x["id"]==part_id]
    if len(requests)!=1 or requests[0].get("method")!="proxy_generated_separate_image":
        raise VideoForgeError("EP01_PROXY_PARTS_NOT_IN_SHOT_PLAN")
    return shot,requests[0]


def existing_part(shot_id: str, part_id: str, root: Path = ROOT) -> dict | None:
    registry=Path(root)/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
    items=json.loads(registry.read_text(encoding="utf-8")).get("geracoes",[])
    asset_id=shot_id.lower()+"-"+part_id
    # An older pixel-cutout producer may have the SAME logical asset ID.
    # It must never be accepted as our independent proxy-generated image.
    matches=[x for x in items if x.get("asset")==asset_id and
             f"/{PRODUCER}/" in str(x.get("arquivo",""))]
    if not matches:
        return None
    if len(matches)!=1:
        raise VideoForgeError("EP01_PROXY_PARTS_DUPLICATE_REGISTRY")
    row=matches[0]
    path=Path(row["arquivo"])
    expected=REL/"assets"/"geracoes"/PRODUCER
    if path.is_absolute() or ".." in path.parts or not path.is_relative_to(expected):
        raise VideoForgeError("EP01_PROXY_PARTS_UNSAFE_ARCHIVE")
    blob_path=Path(root)/path
    if blob_path.is_symlink() or not blob_path.is_file():
        raise VideoForgeError("EP01_PROXY_PARTS_ARCHIVED_BYTES_MISSING")
    digest=hashlib.sha256(blob_path.read_bytes()).hexdigest()
    if digest!=row.get("sha256"):
        raise VideoForgeError("EP01_PROXY_PARTS_ARCHIVE_SHA_MISMATCH")
    return {"asset_id":asset_id,"sha256":digest,"file":str(path)}


def mother_source(shot_id: str, root: Path = ROOT) -> tuple[bytes,dict]:
    # C01-P02 is specifically still in review. Never reuse its rejected V1
    # mother or the unapproved V3/V4 local patches as a source for rig parts.
    if shot_id=="C01-P02":
        raise VideoForgeError("EP01_PROXY_PARTS_C01_P02_MOTHER_NOT_CANONICAL")
    # The C07/C08 continuity pass introduced distinct, SHA-pinned V2 scene
    # mothers. They are the authoritative source for these exact shots.
    # Do not silently fall back to the older original mother or to OpenCV PNGs.
    if shot_id in ("C07-P03", "C08-P02", "C08-P03"):
        from .ep01_continuity_motion import read as read_motion, EP as episode
        motion = read_motion(root)
        src = motion["source_reference_shas"][shot_id]
        relative = episode / src["asset"]
        file = Path(root) / relative
        if (file.is_symlink() or not file.is_file()
                or not file.resolve().is_relative_to((Path(root)/episode).resolve())):
            raise VideoForgeError("EP01_PROXY_PARTS_V2_SOURCE_MISSING")
        blob = file.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (digest != src["sha256"]
                or motion["QA"]["art_approval"] is not False
                or motion["QA"]["rig_ready"] is not False
                or motion["rules"]["never_modify_original_png"] is not True):
            raise VideoForgeError("EP01_PROXY_PARTS_V2_MOTHER_SHA_OR_POLICY_CHANGED")
        return blob, {
            "asset_id": shot_id.lower()+"-scene-mother-continuity-v2",
            "sha256": digest, "path": relative.as_posix(),
            "status": "unapproved_versioned_mother_reference_only"
        }
    item=existing_mother(shot_id,root)
    if not item:
        raise VideoForgeError("EP01_PROXY_PARTS_MOTHER_NOT_GENERATED")
    rel=REL/"assets"/"geracoes"/ARCHIVE_PRODUCER/str(item["run_id"])/(shot_id.lower()+"-scene-mother.png")
    path=Path(root)/rel
    proof=path.with_suffix(".production.json")
    if (path.is_symlink() or proof.is_symlink() or
        not path.is_file() or not proof.is_file()):
        raise VideoForgeError("EP01_PROXY_PARTS_MOTHER_PROOF_MISSING")
    raw=path.read_bytes()
    metadata=json.loads(proof.read_text(encoding="utf-8"))
    if (hashlib.sha256(raw).hexdigest()!=item["sha256"] or
        metadata.get("sha256")!=item["sha256"] or
        metadata.get("candidate_scene_shot_id")!=shot_id or
        metadata.get("human_visual_approval") is not False):
        raise VideoForgeError("EP01_PROXY_PARTS_MOTHER_SHA_OR_STATUS_CHANGED")
    return raw,{"asset_id":shot_id.lower()+"-scene-mother","sha256":item["sha256"],"path":rel.as_posix()}


def _reference_bible(shot_id: str, component: str, root:Path) -> tuple[list[bytes],list[dict]]:
    refplan=read_refs(root)
    ids=next(row["reference_asset_ids"] for row in refplan["shots"] if row["id"]==shot_id)
    # Prioritize the requested subject, then contextual references. The mother
    # itself is always supplied separately; do not exceed provider request bound.
    keyword=component.replace("character-","").replace("object-","").replace("_","-")
    scored=sorted(enumerate(ids), key=lambda row: (
        0 if keyword in row[1] or keyword.replace("-","") in row[1].replace("-","") else
        1 if component=="background-clean" and any(z in row[1] for z in ("sala","quarto","floresta","palacio","cenari")) else 2,
        row[0]))
    selected=[x[1] for x in scored[:MAX_REFERENCE_PNGS_PER_REQUEST-1]]
    if shot_id=="C08-P02":
        # Keep the same mother V2 but send only subject-relevant references.
        # The image proxy failed with HTTP 500 on the five-input Kael
        # transparency request, so do not amplify unrelated image inputs.
        priority={
            "background-clean": ("biblia-beco-base-v1","biblia-carrinho-base-v1"),
            "character-kael": ("biblia-kael-medieval-base-v1","biblia-carrinho-base-v1"),
            "object-carrinho": ("biblia-carrinho-base-v1","biblia-kael-medieval-base-v1"),
        }
        if component in priority:
            selected=[name for name in priority[component] if name in ids]
            if len(selected)!=2:
                raise VideoForgeError("EP01_C08_MISSING_REQUIRED_CANONICAL_REFERENCE")
    data=[]
    proofs=[]
    for ident in selected:
        obj=archived_reference(CHANNEL,VIDEO,ident,root)
        if not obj:
            raise VideoForgeError("EP01_PROXY_PARTS_MISSING_BIBLE_REFERENCE "+ident)
        p=Path(root)/REL/obj["path"]
        if p.is_symlink() or not p.is_file() or p.stat().st_size>35_000_000:
            raise VideoForgeError("EP01_PROXY_PARTS_BAD_BIBLE_REFERENCE "+ident)
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=obj["sha256"]:
            raise VideoForgeError("EP01_PROXY_PARTS_REFERENCE_SHA_MISMATCH "+ident)
        data.append(raw)
        proofs.append({"asset_id":ident,"sha256":obj["sha256"],"path":str((REL/obj["path"]).as_posix())})
    return data,proofs


def enforce_source_qa(shot:dict)->None:
    """A rejected mother is a stop signal, not a reason to draw more parts."""
    if shot.get("qa",{}).get("require_versioned_mother_v2_before_more_proxy_parts") is True:
        raise VideoForgeError("EP01_PROXY_PARTS_MOTHER_REJECTED_NEW_VERSION_REQUIRED")


def prepare(shot_id:str,part_id:str,root:Path=ROOT)->dict:
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    shot,request=read_shot(shot_id,part_id,root)
    # C01-P02 mother V1 is rejected; block before any legacy asset lookup.
    if shot_id=="C01-P02":
        raise VideoForgeError("EP01_PROXY_PARTS_C01_P02_MOTHER_NOT_CANONICAL")
    if existing_part(shot_id,part_id,root):
        raise VideoForgeError("EP01_PROXY_PARTS_ALREADY_ARCHIVED_NO_REPEAT")
    enforce_source_qa(shot)
    mother,proof=mother_source(shot_id,root)
    refs,proofs=_reference_bible(shot_id,part_id,root)
    typ=request["role"]
    common=(
        "Use the ATTACHED first image as fixed visual reference of ONE cinematic "
        "semi-realistic fantasy anime 2D shot. Other attachments are SHA-verified "
        "Visual Bible identity/object references. Create a NEW INDEPENDENT image "
        "with newly generated pixels: no cropping/segmentation/erasing alpha from "
        "the original image. Preserve EXACT subject identity, costume, colors, "
        "lighting, camera angle, scale, perspective, orientation and positioning. "
        "This is an IMAGE EDIT anchored to the original frame, NOT a new "
        "poster, portrait, medium close-up or auto-framed character shot. "
        "The target must occupy the EXACT ORIGINAL bounding box in pixel "
        "coordinates and the same number of source-frame pixels as the "
        "visible figure/object, with all other regions EMPTY TRANSPARENT "
        "in the output if a character/prop. Never recenter, zoom, enlarge, "
        "shrink, rotate, change pose or re-stage the target. The FULL CANVAS "
        "with generous originally empty margins must remain unchanged in "
        "dimensions and coordinates. Do not copy unrelated source RGB pixels "
        "or generate a fresh composition. "
        "No extra figures, weapons, duplicate edges, watermarks, typography or "
        "grid/checkerboard fake transparency. Generate the object/character's "
        "previously hidden geometry needed for articulated movement. "
        "The result is a visual candidate, NOT approved for rig or publication. "
        f"Shot {shot_id}. Beat: {shot['editorial_beat']}. "
        f"Visible frame intention: {shot['visual_prompt']}. "
    )
    if shot_id == "C08-P02":
        common += (
            "The authoritative continuity V2 frame shows ONLY Kael pushing "
            "the same wooden handcart near the RIGHT alley wall. NO pursuers, "
            "guards, Elara or bystanders belong to this shot, even if an older "
            "story prompt refers to masked pursuers reacting. The entire frame "
            "must maintain the exact camera angle and perspective of continuity V2. "
            "For the cart, preserve the wooden chassis, two wheels, spokes, "
            "wheel hubs, handle and contact position of Kael with the handle. "
            "This is candidate art; no source image has visual or rig approval. "
        )
    elif shot_id == "C08-P03":
        common += (
            "Use the same physical cart and identity from C08-P02: now rotated "
            "across the alley as a 90-degree barricade, Kael on the SAFE right "
            "side and exactly two masked pursuers on the opposite left side. "
            "Do not hallucinate a different cart and do not draw Elara here. "
        )
    if typ=="background":
        instruction=(
            "Generate ONLY the EMPTY CLEAN BACKGROUND of this same shot, OPAQUE "
            "RGB/RGBA. Remove every person, weapon and animatable prop and "
            "fully redraw hidden architecture, floors, throne and lighting "
            "consistently. No person/object silhouettes or transparent holes.")
    elif typ=="character":
        instruction=(
            f"Generate ONLY character '{part_id[len('character-'):]}' as a new "
            "independent full-canvas PNG with REAL transparent RGBA pixels "
            "outside the figure; the character must preserve hands, facial "
            "features, clothing, silhouette and shot-relative placement. "
            "NO scene background, weapons, other characters, or fake alpha grid. "
            "Generate missing anatomy behind movable objects as appropriate "
            "without changing VISIBLE art or moving limbs. NO HERO PORTRAIT "
            "CROP, full-height giant person, new pose or enlarged actor. "
            "Preserve the large blank transparent regions above/beside the "
            "character when the mother has those empty margins. "
            "For C01-P03, Kael is KNEELING in the lower foreground and Aldric "
            "is a SMALLER figure in the middle distance before the throne; "
            "neither may occupy the whole frame or be moved toward camera.")
    else:
        instruction=(
            f"Generate ONLY movable object '{part_id[len('object-'):]}' as a new "
            "separate full-canvas PNG with REAL transparent RGBA around the "
            "object. Keep canon ornamentation, perspective, correct attachment "
            "and complete hidden shape. No owner hand, background, other props "
            "or character skin baked in. Sword/bainha: respect physical "
            "alignment and actual scabbard opening; spears: wooden SHAFT BASE "
            "is where the guard grips, never the tip or floating shaft.")
    prompt=common+instruction
    if len(prompt)>5000:
        raise VideoForgeError("EP01_PROXY_PARTS_PROMPT_TOO_LONG")
    return {"shot_id":shot_id,"part_id":part_id,"role":typ,
            "mother":mother,"mother_proof":proof,
            "refs":refs,"ref_proofs":proofs,"prompt":prompt,
            "source_dimensions":(png_info(mother)["width"],png_info(mother)["height"]),
            "transparent":typ!="background"}


def generate(shot_id:str,part_id:str,url:str,root:Path=ROOT,model:str="gpt-image-2")->dict:
    if model!="gpt-image-2":
        raise VideoForgeError("EP01_PROXY_PARTS_MODEL_NOT_ALLOWED")
    spec=prepare(shot_id,part_id,root)
    base=Path(root)/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    asset_id=shot_id.lower()+"-"+part_id
    image=base/(asset_id+".png")
    meta=base/(asset_id+".production.json")
    if any(x.exists() or x.is_symlink() for x in (image,meta)):
        raise VideoForgeError("EP01_PROXY_PARTS_OUTPUT_ALREADY_EXISTS")
    # Validate local PNG reader BEFORE spending the single provider call.
    try:
        from PIL import Image
    except ImportError as exc:
        raise VideoForgeError("EP01_PROXY_PARTS_PILLOW_NOT_AVAILABLE_BEFORE_PAID_CALL") from exc
    inputs=[spec["mother"]]+spec["refs"]
    payload={"model":model,"n":1,"prompt":spec["prompt"],
             "size":"1024x1536",
             "background":"transparent" if spec["transparent"] else "opaque",
             "output_format":"png","response_format":"b64_json","stream":False,
             "images":[{"image_url":"data:image/png;base64,"+
                 base64.b64encode(raw).decode("ascii")} for raw in inputs]}
    answer=proxy_images.call_proxy(
        url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),payload)
    raw,ext=proxy_images.decode_image(answer)
    if ext!=".png":
        raise VideoForgeError("EP01_PROXY_PARTS_NOT_PNG")
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.format!="PNG":
            raise VideoForgeError("EP01_PROXY_PARTS_BAD_PNG")
        is_rgba="A" in im.getbands()
        if spec["transparent"] and not is_rgba:
            qa="rejected_no_real_alpha_channel"
        elif spec["transparent"] and im.getchannel("A").getextrema()[0]!=0:
            qa="rejected_no_transparent_pixels"
        elif spec["transparent"] and im.getchannel("A").getextrema()[1]<128:
            qa="rejected_empty_transparent_asset"
        elif (im.width,im.height)!=spec["source_dimensions"]:
            source_w, source_h=spec["source_dimensions"]
            if (shot_id in ("C08-P02","C08-P03","C07-P03")
                    and abs(im.width-source_w)<=2
                    and abs(im.height-source_h)<=2):
                # We observed C08-P02 background from the real proxy as
                # 1054x1493 versus the 1053x1493 mother. Archive all ORIGINAL
                # provider pixels. A separate, SHA-backed edge alignment may
                # make a candidate copy, but the raw never gets overwritten.
                qa="candidate_minor_edge_delta_requires_alignment_qa"
            elif (shot_id in ("C08-P02","C08-P03","C07-P03")
                    and (im.width,im.height)==(1024,1536)):
                qa="candidate_native_model_canvas_requires_placement_qa"
            else:
                qa="rejected_canvas_mismatch_no_pixel_resizing"
        else:
            qa="candidate_proxy_generated_separate_image"
        dims=(im.width,im.height)
    base.mkdir(parents=True,exist_ok=True)
    image.write_bytes(raw)
    digest=hashlib.sha256(raw).hexdigest()
    report={
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "asset_id":asset_id,"candidate_scene_shot_id":shot_id,
        "component":part_id,"asset_role":spec["role"],
        "generation_method":"proxy_generated_separate_image",
        "not_a_pixel_cutout":True,"sha256":digest,
        "source_image_sha256":spec["mother_proof"]["sha256"],
        "source_mother_sha256":spec["mother_proof"]["sha256"],
        "source_originals_sha_verified":[spec["mother_proof"],*spec["ref_proofs"]],
        "source_images_attached_to_request":len(inputs),
        "width":dims[0],"height":dims[1],
        "source_canvas":list(spec["source_dimensions"]),
        "provider_canvas":list(dims),
        "coordinate_alignment_required": dims != spec["source_dimensions"],
        "source_visual_approval":False,
        "transparent_alpha_required":spec["transparent"],
        "technical_qa":qa,"placement_verified":False,
        "visual_recomposition_approved":False,
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "model":model,"provider_image_calls":1
    }
    meta.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_PROXY_SEPARATE_PART",json.dumps({
        "asset_id":asset_id,"sha256":digest,"qa":qa,
        "human_approved":False,"provider_calls":1}))
    if qa.startswith("rejected"):
        raise VideoForgeError("EP01_PROXY_PARTS_GENERATED_REJECTED_BUT_ARCHIVED "+qa)
    return report


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--shot-id",required=True)
    parser.add_argument("--part",required=True)
    parser.add_argument("--url",required=True)
    arg=parser.parse_args()
    try:
        generate(arg.shot_id,arg.part,arg.url)
    except (VideoForgeError,proxy_images.ProxyImageError,ValueError,OSError) as exc:
        print("EP01_PROXY_PARTS_BLOCKED",str(exc),file=sys.stderr)
        raise SystemExit(2)


if __name__=="__main__":
    main()
