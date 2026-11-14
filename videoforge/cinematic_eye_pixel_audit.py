"""Auditoria de recortes oculares por pixels existentes, sem criar imagens.

C12-P01 exige quatro partes RGBA (pupilas e pálpebras), um head-open
com underlay opaco e duas máscaras aprováveis de região segura de
esclerótica. Mede *todos* os deslocamentos entre 0..12px, 0..1px.
Uma máscara perfeita NÃO comprova cores de esclerótica nem ausência de
pupila duplicada — QA humano adicional continua obrigatório.

Todas as imagens são LIDAS por SHA e processadas exclusivamente em
memória. Não faz chamadas de geração, não escreve PNG nem MP4.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from PIL import Image, ImageChops, ImageFilter

from .errors import VideoForgeError

VISIBLE_ALPHA_THRESHOLD=1
SAFE_ALPHA_THRESHOLD=254
REQUIRED_PARTS={
    "head-open",
    "pupil-left","pupil-right","eyelid-left","eyelid-right",
}
EYE_SIDES=("left","right")
CANVAS=(1024,1536)

def opaque(mask:Image.Image,threshold:int=VISIBLE_ALPHA_THRESHOLD)->Image.Image:
    if mask.mode!="L":
        raise VideoForgeError("CINEMATIC_EYE_ALPHA_EXPECTED")
    # Include antialiased edges with alpha >= 1; they can bleed visibly
    # during motion against light-colored sclera. Head and safe masks
    # require near-total opacity to prevent transparent face holes.
    return mask.point(lambda value:255 if value>=threshold else 0)

def pixel_count(mask:Image.Image)->int:
    return mask.histogram()[255]

def translate_mask(mask:Image.Image,dx:int)->Image.Image:
    """Translate without toroidal ImageChops.offset wrap or image creation."""
    if type(dx) is not int or dx<0 or dx>12:
        raise VideoForgeError("CINEMATIC_EYE_TRANSLATION_NOT_ALLOWED")
    result=Image.new("L",mask.size,0)
    result.paste(mask,(dx,0))
    return result

def verify_alpha_sweep(head_alpha:Image.Image,
                       layers:dict[str,Image.Image],
                       safe_masks:dict[str,Image.Image],
                       pupil_distance:int=12,eyelid_distance:int=1)->dict:
    """Pure pixel-level geometry; source images unchanged."""
    if (head_alpha.mode!="L" or set(layers)!=REQUIRED_PARTS-{"head-open"}
            or set(safe_masks)!=set(EYE_SIDES)
            or any(im.mode!="L" or im.size!=head_alpha.size
                   for im in [*layers.values(),*safe_masks.values()])
            or not 0<pupil_distance<=12 or not 0<eyelid_distance<=1):
        raise VideoForgeError("CINEMATIC_EYE_MASK_INPUT_INVALID")
    head=opaque(head_alpha,SAFE_ALPHA_THRESHOLD)
    if pixel_count(head)<10:
        raise VideoForgeError("CINEMATIC_EYE_HEAD_UNDERLAY_EMPTY")
    report={"canvas":list(head.size),
            "subpixelBilinearFringeMarginPx":1,
            "visibleAlphaThreshold":VISIBLE_ALPHA_THRESHOLD,
            "underlayAndSafeAlphaThreshold":SAFE_ALPHA_THRESHOLD,
            "pupilMaxShiftPx":pupil_distance,
            "eyelidMaxShiftPx":eyelid_distance,
            "eyes":{}}
    for side in EYE_SIDES:
        safe=opaque(safe_masks[side],SAFE_ALPHA_THRESHOLD)
        if pixel_count(safe)<10:
            raise VideoForgeError("CINEMATIC_EYE_SCLERA_MASK_EMPTY_"+side)
        measured={}
        for kind,max_shift in (("pupil",pupil_distance),("eyelid",eyelid_distance)):
            region=opaque(layers[kind+"-"+side])
            size=pixel_count(region)
            if size<3:
                raise VideoForgeError("CINEMATIC_EYE_PART_EMPTY_"+kind+"_"+side)
            measurements=[]
            for dx in range(max_shift+1):
                shifted=translate_mask(region,dx)
                # Do not allow clipping at image boundaries.
                clipped=size-pixel_count(shifted)
                # Only counting high-alpha pixels: fully source-aligned masks.
                escaped=pixel_count(ImageChops.subtract(shifted,safe))
                exposed=pixel_count(ImageChops.subtract(shifted,head))
                # Real Remotion/Three render samples texture at fractional
                # pixel coordinates between integer keyframes; with linear
                # filtering a nonzero alpha source can affect 1 neighbor.
                # A 3x3 max filter conservatively checks this fringe in
                # both axes, avoiding false safety at half-pixel positions.
                bilinear_support=shifted.filter(ImageFilter.MaxFilter(3))
                subpixel_escape=pixel_count(ImageChops.subtract(bilinear_support,safe))
                subpixel_underlay=pixel_count(ImageChops.subtract(bilinear_support,head))
                measurements.append({
                    "shiftPx":dx,
                    "maskedPixels":size,
                    "clippedAtCanvasPixels":clipped,
                    "outsideScleraSafePixels":escaped,
                    "withoutHeadUnderlayPixels":exposed,
                    "fractionalFilterOutsideScleraPixels":subpixel_escape,
                    "fractionalFilterWithoutHeadUnderlayPixels":subpixel_underlay,
                })
                if clipped or escaped or exposed or subpixel_escape or subpixel_underlay:
                    raise VideoForgeError(
                        "CINEMATIC_EYE_PIXEL_BLEED_OR_UNDERLAY_MISSING:"
                        +kind+"-"+side+":shift="+str(dx)
                        +":clip="+str(clipped)
                        +":escape="+str(escaped)
                        +":underlay="+str(exposed)
                        +":fractional_escape="+str(subpixel_escape)
                        +":fractional_underlay="+str(subpixel_underlay)
                    )
            measured[kind]={
                "opaquePixels":size,
                "fullSweepPassed":True,
                "shiftTests":len(measurements),
                "maxShiftPx":max_shift,
                "worstEscapedPixels":0,
                "worstUnderlayMissingPixels":0,
                "worstFractionalFilterEscapedPixels":0,
                "worstFractionalFilterUnderlayMissingPixels":0,
            }
        report["eyes"][side]=measured
    report.update({
        "sweepsTested":2*(pupil_distance+1)+2*(eyelid_distance+1),
        "alphaSafetyVerified":True,
        "rgbScleraArtAccuracyNotProven":True,
        "pupilDuplicatePaintNotProvenByMasks":True,
        "humanVisualApprovalStillRequired":True,
        "newImagesCreated":0,
        "imageGenerationCalls":0,
    })
    return report

def _load_rgba(episode:Path,definition:dict,canvas:tuple[int,int]=CANVAS)->Image.Image:
    """Load actual approved crop from one shot after SHA and IHDR validation."""
    from .cinematic_shot_assets import _file_from_rel, _png_valid
    if not isinstance(definition,dict):
        raise VideoForgeError("CINEMATIC_EYE_LAYER_DEFINITION_INVALID")
    try:
        bbox=definition["bbox"]
        rel=definition["path"]
        sha=definition["sha256"]
    except KeyError as exc:
        raise VideoForgeError("CINEMATIC_EYE_LAYER_PROVENANCE_MISSING") from exc
    if (not isinstance(bbox,list) or len(bbox)!=4
            or any(type(v) is not int for v in bbox)
            or bbox[0]<0 or bbox[1]<0 or bbox[2]<=0 or bbox[3]<=0
            or bbox[0]+bbox[2]>canvas[0] or bbox[1]+bbox[3]>canvas[1]):
        raise VideoForgeError("CINEMATIC_EYE_BBOX_INVALID")
    path=_file_from_rel(episode,rel)
    if not _png_valid(path,sha,True,(bbox[2],bbox[3])):
        raise VideoForgeError("CINEMATIC_EYE_PNG_SHA_OR_RGBA_MISMATCH")
    with Image.open(path) as im:
        crop=im.getchannel("A").copy()
    full=Image.new("L",canvas,0)
    full.paste(crop,(bbox[0],bbox[1]))
    return full

def audit_existing_eye_assets(episode:Path,shot_id:str,
                              rig:dict,qa:dict,
                              require_human_approval:bool=True)->dict:
    """Per-shot preflight. Never infers a human approval from a pixel test."""
    if shot_id!="C12-P01":
        raise VideoForgeError("CINEMATIC_EYE_AUDIT_WRONG_SHOT")
    parts=rig.get("parts")
    actors=rig.get("actors")
    if not isinstance(parts,list) or not isinstance(actors,list) or len(actors)!=1:
        raise VideoForgeError("CINEMATIC_EYE_AUDIT_PARTS_OR_ACTORS_MISSING")
    index={p["name"]:p for p in parts if isinstance(p,dict) and
           isinstance(p.get("name"),str)}
    if len(index)!=len(parts):
        raise VideoForgeError("CINEMATIC_EYE_AUDIT_PART_NAMES_NOT_UNIQUE")
    character=actors[0].get("rig",{})
    layers=character.get("layers",[])
    matching={}
    for layer in layers:
        if not isinstance(layer,dict):
            raise VideoForgeError("CINEMATIC_EYE_AUDIT_LAYER_INVALID")
        if layer.get("id") not in REQUIRED_PARTS:
            continue
        part=index.get(layer["id"])
        if (part is None or part.get("path")!=layer.get("file")
                or part.get("bbox")!=layer.get("bbox")
                or part.get("sha256")!=layer.get("sha256")):
            raise VideoForgeError("CINEMATIC_EYE_LAYER_NOT_FROM_OWN_MOTHER")
        matching[layer["id"]]=part
    if set(matching)!=REQUIRED_PARTS:
        raise VideoForgeError("CINEMATIC_EYE_AUDIT_FIVE_CROPS_REQUIRED")
    eye_meta=character.get("eyeRig")
    if not isinstance(eye_meta,dict):
        raise VideoForgeError("CINEMATIC_EYE_AUDIT_SCLERA_METADATA_MISSING")
    masks=eye_meta.get("scleraSafeMasks")
    if not isinstance(masks,dict) or set(masks)!=set(EYE_SIDES):
        raise VideoForgeError("CINEMATIC_EYE_AUDIT_TWO_SAFE_MASKS_REQUIRED")
    # Two manually reviewed eye masks must be linked to their own mother.
    from .cinematic_shot_assets import validate_shot_canvas
    native_canvas=validate_shot_canvas(rig)
    if character.get("canvas")!=rig.get("canvas"):
        raise VideoForgeError("CINEMATIC_EYE_ACTOR_CANVAS_MISMATCH")
    prefix="assets/planos/"+shot_id+"/"
    verified={}
    for side,asset in masks.items():
        if not isinstance(asset,dict) or not asset.get("path","").startswith(prefix):
            raise VideoForgeError("CINEMATIC_EYE_SAFE_MASK_NOT_FROM_OWN_SHOT")
        if asset.get("mother_sha256")!=rig.get("source_sha256"):
            raise VideoForgeError("CINEMATIC_EYE_SAFE_MASK_WRONG_MOTHER")
        verified[side]=_load_rgba(episode,asset,native_canvas)
    head=_load_rgba(episode,matching["head-open"],native_canvas)
    segments={name:_load_rgba(episode,matching[name],native_canvas)
              for name in sorted(REQUIRED_PARTS-{"head-open"})}
    report=verify_alpha_sweep(head,segments,verified)
    report["sourceMotherSha256"]=rig.get("source_sha256")
    report["safeMaskSourceSHA256"]={side:masks[side]["sha256"] for side in EYE_SIDES}
    report["pupilSourceSHA256"]={
        side:index["pupil-"+side]["sha256"] for side in EYE_SIDES
    }
    report["eyelidSourceSHA256"]={
        side:index["eyelid-"+side]["sha256"] for side in EYE_SIDES
    }
    # A mask alone cannot prove a face has no painted duplicate pupil.
    # Human signoff remains independent and mandatory.
    if require_human_approval and any(qa.get(k) is not True for k in (
        "human_visual_approved","eye_sclera_underlays_verified",
        "eye_mask_no_bleed_verified",
        "no_duplicate_pupils_in_head_verified",
    )):
        raise VideoForgeError("CINEMATIC_EYE_PIXEL_HUMAN_APPROVAL_MISSING")
    return report


def readiness_report(episode:Path)->dict:
    """Reproducible JSON status. Pending assets do not become approved."""
    from .cinematic_shot_assets import _load_json
    lock=episode/"SEM-GERACAO-NOVAS-IMAGENS.lock"
    if not lock.is_file():
        raise VideoForgeError("CINEMATIC_EYE_IMAGE_GENERATION_LOCK_REQUIRED")
    shot_folder=episode/"assets/planos/C12-P01"
    rig_file=shot_folder/"rig.json"
    qa_file=shot_folder/"qa.json"
    report={
        "schema":"videoforge/eye-pixel-readiness-report/v1",
        "channel":"alchemy-lab",
        "video_id":"mmorpg-conquiste-a-princesa-ep01",
        "shot":"C12-P01",
        "source":"assets/planos/C12-P01/",
        "method":"recompute alpha envelope of four original RGBA eye parts",
        "imageGenerationCalls":0,
        "newPNGFiles":0,
        "mp4Rendered":False,
        "youtubeUploaded":False,
        "automatedAlphaApproved":False,
        "humanVisualApproved":False,
        "officialRigApproved":False,
        "status":"awaiting_own_shot_art",
        "blockers":[],
    }
    if not rig_file.is_file():
        report["blockers"].append("SHOT_RIG_JSON_MISSING")
    if not qa_file.is_file():
        report["blockers"].append("SHOT_QA_JSON_MISSING")
    if report["blockers"]:
        return report
    try:
        rig=_load_json(rig_file)
        qa=_load_json(qa_file)
        from .cinematic_eye_motion import check_eye_performance
        analysis=audit_existing_eye_assets(
            episode,"C12-P01",rig,qa,require_human_approval=False
        )
        report["automatedAlphaApproved"]=True
        report["pixelEnvelope"]=analysis
        report["status"]="alpha_passed_human_review_pending"
        report["humanVisualApproved"]=qa.get("human_visual_approved") is True
        try:
            check_eye_performance("C12-P01",rig,qa)
        except VideoForgeError as exc:
            report["blockers"].append(str(exc))
        else:
            report["status"]="eye_pixel_and_human_qa_verified_only"
            # The remaining episode shots and cinematic rig still need QA.
            report["officialRigApproved"]=False
    except (VideoForgeError,ValueError,KeyError,OSError) as exc:
        report["status"]="blocked_by_missing_or_invalid_eye_art"
        report["blockers"].append(str(exc))
    return report

def main()->int:
    parser=argparse.ArgumentParser(
        description="Readiness JSON for Kael C12-P01; no art or MP4 generated"
    )
    parser.add_argument("--report",action="store_true",
                        help="Version report inside episode folder")
    args=parser.parse_args()
    from .cinematic_shot_assets import ROOT
    episode=ROOT/"canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
    try:
        doc=readiness_report(episode)
        encoded=json.dumps(doc,ensure_ascii=False,indent=2)+"\n"
        if args.report:
            path=episode/"qa-pixel-olhos-c12-p01.json"
            if path.is_symlink():
                raise VideoForgeError("CINEMATIC_EYE_REPORT_SYMLINK_NOT_ALLOWED")
            if not path.exists() or path.read_text(encoding="utf8")!=encoded:
                path.write_text(encoded,encoding="utf8")
        print("CINEMATIC_EYE_READINESS",json.dumps({
            "status":doc["status"],
            "alphaQA":doc["automatedAlphaApproved"],
            "humanQA":doc["humanVisualApproved"],
            "blockers":doc["blockers"],
            "imagesGenerated":0,
        },ensure_ascii=False))
        return 0
    except (VideoForgeError,OSError,ValueError) as exc:
        print("CINEMATIC_EYE_READINESS_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
