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
    # The first generated C08-P02 Kael candidate contains the whole cart.
    # V2 deliberately reuses the canon "character-kael" role, while the
    # versioned logical ID avoids rewriting or rebilling the archived V1.
    canonical_part=(
        "character-kael" if shot_id=="C08-P02" and part_id in {"character-kael-v2","character-kael-v3"}
        else "object-carrinho" if (shot_id,part_id)==("C08-P02","object-carrinho-v2")
        else "object-coroa-aldric" if (shot_id,part_id)==("C02-P01","object-coroa-aldric-v2")
        else part_id)
    requests=[x for x in shot["images"]["proxy_generation_requests"]
              if x["id"]==canonical_part]
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
            # Do not include the separate cart Bible image in character V2:
            # V1 fused the cart and Kael into a single alpha object.
            "character-kael-v2": ("biblia-kael-medieval-base-v1",),
            "character-kael-v3": ("biblia-kael-medieval-base-v1",),
            "object-carrinho": ("biblia-carrinho-base-v1","biblia-kael-medieval-base-v1"),
            "object-carrinho-v2": ("biblia-carrinho-base-v1",),
        }
        if component in priority:
            selected=[name for name in priority[component] if name in ids]
            expected_ref_count=1 if component in ("character-kael-v2","character-kael-v3","object-carrinho-v2") else 2
            if len(selected)!=expected_ref_count:
                raise VideoForgeError("EP01_C08_MISSING_REQUIRED_CANONICAL_REFERENCE")
    if (shot_id,component)==("C02-P01","object-coroa-aldric-v2"):
        # V2 uses only the direct king/crown identity reference. The failed
        # V1 landscape sprite is never attached to a regeneration request.
        selected=["biblia-aldric-tribunal-v1"]
        if selected[0] not in ids:
            raise VideoForgeError("EP01_CROWN_V2_MISSING_CANONICAL_REFERENCE")
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


def exact_canvas_size(dimensions) -> str:
    """Validate the native gpt-image-2 request size without changing pixels.

    Constraints: docs/EP01-CANVAS-CONTRACT.md. A valid request still needs
    output canvas/alpha/placement QA; the proxy is not assumed to honor it.
    """
    if (not isinstance(dimensions, (tuple, list)) or len(dimensions) != 2
            or any(type(edge) is not int or edge <= 0 for edge in dimensions)):
        raise VideoForgeError("EP01_PROXY_PARTS_UNSUPPORTED_NATIVE_CANVAS")
    width, height = dimensions
    if (max(width, height) > 3840 or width % 16 or height % 16
            or max(width, height) > 3 * min(width, height)
            or not 655360 <= width * height <= 8294400):
        raise VideoForgeError("EP01_PROXY_PARTS_UNSUPPORTED_NATIVE_CANVAS")
    return f"{width}x{height}"


def prepare(shot_id:str,part_id:str,root:Path=ROOT,*,
            require_supported_canvas:bool=False)->dict:
    """Inspect source provenance; production callers must validate its canvas."""

    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    shot,request=read_shot(shot_id,part_id,root)
    # C01-P02 mother V1 is rejected; block before any legacy asset lookup.
    if shot_id=="C01-P02":
        raise VideoForgeError("EP01_PROXY_PARTS_C01_P02_MOTHER_NOT_CANONICAL")
    if existing_part(shot_id,part_id,root):
        raise VideoForgeError("EP01_PROXY_PARTS_ALREADY_ARCHIVED_NO_REPEAT")
    if (shot_id,part_id)==("C08-P02","character-kael-v2"):
        rejected=existing_part("C08-P02","character-kael",root)
        if not rejected or rejected["sha256"]!=(
                "2579d5786f89957ea776c8c17b76371027fffd2ce43a4e3fba6505201db029d1"):
            raise VideoForgeError("EP01_KAEL_V2_REJECTED_PREDECESSOR_NOT_VERIFIED")
    if (shot_id,part_id)==("C08-P02","object-carrinho-v2"):
        rejected=existing_part("C08-P02","object-carrinho",root)
        if (not rejected or rejected["sha256"] !=
                "bf78eae46f5d6836a7834fff8714c6e3072f23e523d6fbe73ac8b9b5accb47ab"):
            raise VideoForgeError("EP01_CART_V2_PREDECESSOR_NOT_VERIFIED")
    if (shot_id,part_id)==("C02-P01","object-coroa-aldric-v2"):
        rejected=existing_part("C02-P01","object-coroa-aldric",root)
        if not rejected or rejected["sha256"]!=(
                "acf47957dfc7cc92a443b065cb348014a2132ab742bc0040391dc4bc76282b9f"):
            raise VideoForgeError("EP01_CROWN_V2_REJECTED_PREDECESSOR_NOT_VERIFIED")
    enforce_source_qa(shot)
    mother,proof=mother_source(shot_id,root)
    refs,proofs=_reference_bible(shot_id,part_id,root)
    if (shot_id,part_id)==("C08-P02","character-kael-v3"):
        from .ep01_c08_proxy_composite import RECORDS, MOTHER_SHA
        if proof["sha256"] != MOTHER_SHA:
            raise VideoForgeError("EP01_KAEL_V3_MOTHER_CHANGED")
        for role, component in (("kael","character-kael-v2"), ("cart","object-carrinho-v2")):
            item=existing_part(shot_id,component,root)
            if not item or item["sha256"] != RECORDS[role]["sha256"]:
                raise VideoForgeError("EP01_KAEL_V3_CONTACT_SOURCE_CHANGED")
            if role=="cart":
                refs.append((root/item["file"]).read_bytes())
                proofs.append({"asset_id":item["asset_id"],"sha256":item["sha256"],"path":item["file"]})
    typ=request["role"]
    # Explicitly bind the native source orientation before spending an image call.
    # Valid request dimensions do not guarantee matching provider output.
    native_canvas = png_info(mother)
    source_w, source_h = native_canvas["width"], native_canvas["height"]
    if require_supported_canvas:
        exact_canvas_size((source_w, source_h))
    orientation = "VERTICAL portrait" if source_h > source_w else (
        "HORIZONTAL landscape" if source_w > source_h else "SQUARE")
    common=(
        f"CANVAS CONTRACT: image one is {source_w}x{source_h} pixels "
        f"(WIDTH={source_w}, HEIGHT={source_h}, {orientation}). "
        f"Output must keep WIDTH={source_w} and HEIGHT={source_h} IN THAT ORDER; "
        f"NEVER transpose to {source_h}x{source_w}, rotate the frame, or "
        "reframe the subject. The transparent full-frame margins count. "
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
    if (shot_id,part_id)==("C08-P02","character-kael-v2"):
        # The first version visibly incorporated the CART itself.
        # Remove any cart reference from the image inputs and require a
        # character-only redraw, with hands completed where cart occluded them.
        instruction=(
            "Draw ONLY the single person KAEL from the mother frame, as an "
            "INDEPENDENT character sprite with authentic transparent RGBA "
            "outside the person. NOT a crop of the mother image. "
            "IMPORTANT ERROR TO CORRECT: the previous character candidate "
            "included the ENTIRE wooden cart, wheels, handles, and planks. "
            "THIS OUTPUT MUST CONTAIN ZERO CART PIXELS. "
            "NO wheels, no wooden vehicle, no gold-rimmed cart corners, "
            "NO wooden box, handles, axle, floor, alley, or shadow cutout. "
            "The FULL RIGHT-HAND SIDE from 72 percent of the image width to "
            "the far right, across the lower middle, MUST remain transparent. "
            "Generate ONLY Kael's body, hair, face, red cape, leather armour, "
            "boots, forearms, fingers and both hands as fully drawn anatomy. "
            "The hands may extend toward the right where the cart was, "
            "but no cart or wooden handle may be rendered. "
            "Keep his actual original size and frame location on the LEFT, "
            "leaning forward from his original pushing pose, both feet "
            "grounded. Fill in the previously occluded limb contours. "
            "Preserve original identity, anatomy, lighting, costume, colours "
            "and perspective. DO NOT enlarge or center Kael. "
            "The first image is the scene-mother as a positional reference "
            "and the second is ONLY the canonical KAEL identity reference. "
            "The final pixels must be freshly generated, and the background "
            "fully alpha=0, not black opaque or a fake checkerboard. "
            "If you cannot eliminate the cart, do not replace the body "
            "with a new pose: visual QA will reject the result."
        )
    if (shot_id,part_id)==("C08-P02","object-carrinho-v2"):
        instruction=(
            "Create a COMPLETELY NEW independently drawn transparent RGBA PNG "
            "of ONLY the original wooden handcart, not a segmented/cropped copy. "
            "You must preserve the VERTICAL portrait composition from IMAGE ONE, "
            "which is the C08-P02 continuity mother, native 1053x1493. "
            "The cart occupies the RIGHT side and lower-middle of the SOURCE "
            "portrait, while empty transparent space remains at the top and "
            "LEFT. NEVER make a landscape 1512x1040 object render, a catalog "
            "product photo or an enlarged/recentered handcart. "
            "Do NOT change the viewpoint, shape, length of handles, physical "
            "perspective, material, size, or cart orientation from the mother. "
            "Match the EXACT on-screen bounding rectangle and camera angle "
            "of the partly offscreen cart at the right side of source shot. "
            "Do NOT center a complete newly exposed cart: generate its hidden "
            "construction only where needed, preserving source framing. "
            "The cart has ONE rigid wooden chassis, TWO fully circular wheels, "
            "coherent axle, spokes, wooden beams and the canonical fleur-de-lys "
            "gold ornament. Use IMAGE TWO solely for visual identity. "
            "NO Kael, no hands, no red cape, no guards, no other characters, "
            "NO alley, bricks, pavement, painted background, cast landscape "
            "or fake checkerboard. Everything outside cart is alpha=0. "
            "Do NOT flatten wheel sprites into the character. Future wheel "
            "articulation is separate and not automatically approved. "
            "Never regenerate the C08 scene mother or overwrite the rejected "
            "landscape object from the first proxy run. "
            "This new cart is a QA candidate, NOT a rig-ready production asset."
        )
    if (shot_id,part_id)==("C08-P02","character-kael-v3"):
        instruction=(
            "Generate a new independent RGBA layer of Kael ONLY. Image 1 is the 1053x1493 mother: "
            "keep its portrait framing, full torso, feet, scale and position. Image 2 specifies Kael's identity. "
            "Image 3 is the actual cart layer, for hand placement only: align its upper left corner to the "
            "mother. Leave all cart pixels TRANSPARENT in your output. Kael alone pushes from the left. "
            "Draw both hands anatomically joined to his forearms. The upper hand must close firmly around "
            "the gold corner fixture in the box x560-635 y615-713. The lower palm and curled fingers "
            "grip the side rail within x555-650 y740-830. Preserve plausible finger occlusion so a cart "
            "layer placed behind the character appears firmly grasped. No hanging fingers, detached hands, "
            "baked-in wood, wheels, background, guards or passers-by. Do not move the cart or alter Kael's "
            "stance to fake contact. Full drawing to original frame edges, native transparent canvas.")
    if (shot_id,part_id)==("C02-P01","object-coroa-aldric-v2"):
        instruction=(
            "Create a fresh independent transparent RGBA crown asset for "
            "Aldric using the first image as its exact portrait frame and the "
            "second image only as the canonical crown/king identity reference. "
            "This is version 2 after the rejected crown V1 was generated as a "
            "1774x887 landscape. Do NOT attach, copy, resize, crop, or use the "
            "rejected V1 pixels. The required native canvas is exactly "
            "941x1672 portrait, matching the scene mother. Keep the crown at "
            "the top of Aldric's head in the close frontal C02-P01 frame, at "
            "the same small on-screen scale, perspective and x/y placement as "
            "the crown visible on the mother; do not center or enlarge it. "
            "Only the complete crown, including hidden band behind hair, may "
            "be opaque; every other pixel is true alpha=0. No head, hair, "
            "skin, beard, throne, background, extra crown, title, or fake "
            "checkerboard. Preserve the gold filigree and red gems from the "
            "canonical Aldric Bible. Candidate only; placement, composition, "
            "visual identity, rig readiness and approval remain unverified."
        )
    prompt=common+instruction
    if len(prompt)>5000:
        raise VideoForgeError("EP01_PROXY_PARTS_PROMPT_TOO_LONG")
    versioned_predecessor=(
        {"asset_id":"c02-p01-object-coroa-aldric",
         "sha256":"acf47957dfc7cc92a443b065cb348014a2132ab742bc0040391dc4bc76282b9f",
         "attached_to_generation_request":False}
        if (shot_id,part_id)==("C02-P01","object-coroa-aldric-v2") else None)
    return {"shot_id":shot_id,"part_id":part_id,"role":typ,
            "mother":mother,"mother_proof":proof,
            "refs":refs,"ref_proofs":proofs,"prompt":prompt,
            "versioned_from_rejected_predecessor":versioned_predecessor,
            "source_dimensions":(source_w,source_h),
            "transparent":typ!="background"}


def right_side_prop_coverage(image) -> float:
    """QA-only high-alpha share in a C08 Kael zone reserved for the cart.

    This is not a segmentation algorithm and must never produce rig sprites.
    The person remains on the left side of the approved shot. The original
    V1 Kael output erroneously occupied this whole right-hand cart region.
    """
    if "A" not in image.getbands():
        return 1.0
    from PIL import ImageStat
    w,h=image.size
    region=image.getchannel("A").crop(
        (int(w*.72),int(h*.42),w,int(h*.90)))
    binary=region.point(lambda x: 255 if x>=128 else 0)
    return round(ImageStat.Stat(binary).mean[0]/255,6)


def generate(shot_id:str,part_id:str,url:str,root:Path=ROOT,model:str="gpt-image-2")->dict:
    if model!="gpt-image-2":
        raise VideoForgeError("EP01_PROXY_PARTS_MODEL_NOT_ALLOWED")
    spec=prepare(shot_id,part_id,root,require_supported_canvas=True)
    requested_size=exact_canvas_size(spec["source_dimensions"])
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
             "size":requested_size,
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
            if (abs(im.width-source_w)<=2 and abs(im.height-source_h)<=2):
                # Minor native output canvas differences also occur outside
                # C07/C08: C01-P05 guard-right was 941x1671 vs mother 941x1672.
                # Archive every original provider pixel and REQUIRE independent
                # edge/alpha + visual QA. Never stretch/resize the source here.
                qa="candidate_minor_edge_delta_requires_alignment_qa"
            elif (shot_id in ("C08-P02","C08-P03","C07-P03")
                    and (im.width,im.height)==(1024,1536)):
                qa="candidate_native_model_canvas_requires_placement_qa"
            else:
                qa="rejected_canvas_mismatch_no_pixel_resizing"
        else:
            qa="candidate_proxy_generated_separate_image"
        cart_alpha_fraction=(right_side_prop_coverage(im)
                             if shot_id=="C08-P02" and part_id in {"character-kael-v2","character-kael-v3"}
                             else None)
        if (cart_alpha_fraction is not None and cart_alpha_fraction>0.02
                and not qa.startswith("rejected")):
            qa="rejected_character_contains_cart_or_wrong_canvas_placement"
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
        "requested_size":requested_size,
        "provider_canvas":list(dims),
        "coordinate_alignment_required": dims != spec["source_dimensions"],
        "source_visual_approval":False,
        "transparent_alpha_required":spec["transparent"],
        "technical_qa":qa,
        "qa_only_cart_zone_high_alpha_fraction":cart_alpha_fraction,
        "qa_only_cart_zone_maximum_for_character_v2":0.02 if cart_alpha_fraction is not None else None,
        "placement_verified":False,
        "visual_recomposition_approved":False,
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "model":model,"provider_image_calls":1
    }
    if spec.get("versioned_from_rejected_predecessor"):
        report["versioned_from_rejected_predecessor"] = spec["versioned_from_rejected_predecessor"]
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
