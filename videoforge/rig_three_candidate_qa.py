"""Compare extracted head/body against the SAME original scene-mother.

Image AI provides candidate alpha/occlusion geometry. The published head
sprite always takes original visible pixels (not AI-repainted skin/hair).
The closed head is copied from the previously user-approved original full
closed frame using the EXACT same alpha mask. This is a review-only asset
pack; unresolved hidden anatomy/hair cannot become an approved rig.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from .animation_manual import enforce_animation_manual
from .rig_three_art import load_plan,check_source
from . import scene_layers
from .errors import VideoForgeError

WIDTH,HEIGHT=1024,1536
BYTES=WIDTH*HEIGHT*4


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(path:Path)->bytearray:
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("RIG_CANDIDATE_FILE_MISSING")
    scene_layers.png_info(path.read_bytes(),require_alpha=True)
    p=subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
        "-i",str(path),"-frames:v","1","-f","rawvideo","-pix_fmt","rgba","-"],
        capture_output=True,timeout=90,check=False)
    if p.returncode!=0 or len(p.stdout)!=BYTES:
        raise VideoForgeError("RIG_CANDIDATE_DECODE_FAILED")
    return bytearray(p.stdout)


def encode_crop(path:Path,rgba:bytearray,bbox:list[int])->None:
    x,y,w,h=bbox
    if not (0<=x<WIDTH and 0<=y<HEIGHT and 0<w<=WIDTH-x and 0<h<=HEIGHT-y):
        raise VideoForgeError("RIG_CANDIDATE_CROP_INVALID")
    chunk=bytearray()
    for row in range(y,y+h):
        offset=(row*WIDTH+x)*4
        chunk.extend(rgba[offset:offset+w*4])
    p=subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
        "-f","rawvideo","-pixel_format","rgba",
        "-video_size",f"{w}x{h}","-framerate","1",
        "-i","-","-frames:v","1","-compression_level","6",str(path)],
        input=bytes(chunk),capture_output=True,timeout=90,check=False)
    if p.returncode:
        raise VideoForgeError("RIG_CANDIDATE_PNG_ENCODE_FAILED")
    info=scene_layers.png_info(path.read_bytes(),require_alpha=True)
    if (info["width"],info["height"])!=(w,h):
        raise VideoForgeError("RIG_CANDIDATE_OUTPUT_INVALID")


def bbox_of(rgba:bytearray,roi:list[int])->list[int]:
    minx,miny,maxx,maxy=WIDTH,HEIGHT,-1,-1
    x0,y0,x1,y1=roi
    for y in range(y0,y1):
        for x in range(x0,x1):
            if rgba[(y*WIDTH+x)*4+3]>20:
                minx=min(minx,x);miny=min(miny,y)
                maxx=max(maxx,x);maxy=max(maxy,y)
    if maxx<minx:
        raise VideoForgeError("RIG_CANDIDATE_EMPTY_MASK")
    return [minx,miny,maxx-minx+1,maxy-miny+1]


def _verify_qa(file:Path,part:str,blob:Path,plan:dict):
    d=json.loads(file.read_text(encoding="utf-8"))
    if (d.get("schema")!="videoforge/rig-three-art-candidate/v1" or
        d.get("part")!=part or d.get("source_original_sha256")!=plan["reference_sha256"] or
        d.get("source_scene_mother_sha256")!=plan["scene_mother_sha256"] or
        d.get("output_sha256")!=sha(blob) or
        d.get("human_visual_approval") is not False or
        d.get("output_png_technical_status")!="candidate_rgba_verified"):
        raise VideoForgeError("RIG_CANDIDATE_ARTIFACT_NOT_VERIFIED")


def foreign_character_pixel(original:bytes,ai:bytes)->bool:
    """Off-character dark pixels under IA's pink repaint imply a foreign body.

    This is an inexpensive heuristic used to REJECT questionable masks, never
    an automatic way to approve them. No character identity inference.
    """
    return (original[0]<170 and original[1]<120 and
            ai[0]>200 and ai[0]-original[0]>80)


def compose(input_source:Path,input_head:Path,input_body:Path,
            input_eyes:Path,destination:Path,channel:str,video_id:str)->dict:
    enforce_animation_manual()
    plan=load_plan(channel,video_id)
    check_source(input_source,plan)
    original_path=input_source/plan["reference_file"]
    orig=decode(original_path)
    # Same source PNG edited previously; alpha outside eyes is identical.
    closed_files=list(input_eyes.rglob("character-eyes-closed-safe.png"))
    reports=list(input_eyes.rglob("closed-character.qa.json"))
    if len(closed_files)!=1 or len(reports)!=1:
        raise VideoForgeError("RIG_CANDIDATE_APPROVED_BLINK_ARTIFACT_MISSING")
    closed_path=closed_files[0]
    eye_report=reports[0]
    e=json.loads(eye_report.read_text(encoding="utf-8"))
    if (e.get("schema")!="videoforge/closed-character-pixel-qa/v1" or
        e.get("original_character_sha256")!=sha(original_path) or
        e.get("safe_full_closed_sha256")!=sha(closed_path) or
        e.get("non_eye_pixels_changed")!=0 or e.get("alpha_pixels_changed")!=0):
        raise VideoForgeError("RIG_CANDIDATE_APPROVED_BLINK_SOURCE_INVALID")
    closed=decode(closed_path)
    by_id={x["id"]:x for x in plan["steps"]}
    blobs={}
    edits={}
    for part,folder in (("head-open",input_head),("body-no-head",input_body)):
        step=by_id[part]
        raw_candidates=list(folder.rglob(step["output"]))
        reports=list(folder.rglob(part+".qa.json"))
        if len(raw_candidates)!=1 or len(reports)!=1:
            raise VideoForgeError("RIG_CANDIDATE_PART_ARTIFACT_MISSING")
        _verify_qa(reports[0],part,raw_candidates[0],plan)
        blobs[part]=decode(raw_candidates[0])
        edits[part]=raw_candidates[0]
    destination.mkdir(parents=True,exist_ok=False)
    head=bytearray(BYTES)
    head_closed=bytearray(BYTES)
    body=bytearray(BYTES)
    head_roi=by_id["head-open"]["roi"]
    body_roi=by_id["body-no-head"]["roi"]
    total_head_visible=total_body_visible=0
    inspected_upper_pixels=foreign_upper_pixels=0
    head_mask=blobs["head-open"]
    body_raw=blobs["body-no-head"]
    # Use a common geometric mask for open/closed. Never use AI-generated
    # face RGB in head, preserves the approved character exact pixels.
    for y in range(HEIGHT):
        for x in range(WIDTH):
            k=(y*WIDTH+x)*4
            if head_roi[0]<=x<head_roi[2] and head_roi[1]<=y<head_roi[3]:
                a=min(orig[k+3],head_mask[k+3])
                if a>20:
                    if y<1180 and orig[k+3]>100 and head_mask[k+3]>100:
                        inspected_upper_pixels+=1
                        if foreign_character_pixel(orig[k:k+3],head_mask[k:k+3]):
                            foreign_upper_pixels+=1
                    head[k:k+3]=orig[k:k+3]
                    head_closed[k:k+3]=closed[k:k+3]
                    head[k+3]=head_closed[k+3]=a
                    total_head_visible+=1
            if body_roi[0]<=x<body_roi[2] and body_roi[1]<=y<body_roi[3]:
                a=body_raw[k+3]
                if a>20:
                    # Inpainted hidden anatomy comes only from candidate.
                    body[k:k+4]=body_raw[k:k+4]
                    total_body_visible+=1
    if total_head_visible<45000 or total_body_visible<6000:
        raise VideoForgeError(f"RIG_CANDIDATE_COVERAGE_LOW_{total_head_visible}_{total_body_visible}")
    head_box=bbox_of(head,head_roi)
    body_box=bbox_of(body,body_roi)
    encode_crop(destination/"head-open.png",head,head_box)
    encode_crop(destination/"head-closed.png",head_closed,head_box)
    encode_crop(destination/"body-no-head.png",body,body_box)
    # Neutral pose: body behind exact original head. Compare only the original
    # Anya target region. This is diagnostic, NOT automatic visual approval.
    pixels=0;diff=0;overlap=0;changed_original_outside_eyes=0
    for y in range(head_roi[1],HEIGHT):
        for x in range(head_roi[0],head_roi[2]):
            k=(y*WIDTH+x)*4
            ah=head[k+3];ab=body[k+3]
            if ah>40 and ab>40:overlap+=1
            amax=ah+ab*(255-ah)//255
            if orig[k+3]<100 or amax<100:continue
            pixels+=1
            for c in range(3):
                value=(head[k+c]*ah+body[k+c]*ab*(255-ah)//255)//max(1,amax)
                diff+=abs(value-orig[k+c])
    error=diff/(3*max(1,pixels))
    overlapping_fraction=overlap/max(1,total_head_visible+total_body_visible)
    foreign_ratio=foreign_upper_pixels/max(1,inspected_upper_pixels)
    isolation_status=("rejected_foreign_character_or_background_fragments"
                      if foreign_upper_pixels>1800 or foreign_ratio>.08
                      else "candidate_only_requires_human_review")
    # Export real neutral assembly and a visible RGB-diff image for review.
    # Alpha outside the original Anya ROI remains zero; none of these previews
    # can be misinterpreted as an approved video or a reference for new images.
    composed=bytearray(BYTES)
    difference=bytearray(BYTES)
    for y in range(head_roi[1],HEIGHT):
        for x in range(head_roi[0],head_roi[2]):
            k=(y*WIDTH+x)*4
            ah=head[k+3];ab=body[k+3]
            out_a=ah+ab*(255-ah)//255
            if out_a>0:
                composed[k+3]=out_a
                for ch in range(3):
                    composed[k+ch]=max(0,min(255,(head[k+ch]*ah+
                        body[k+ch]*ab*(255-ah)//255)//max(1,out_a)))
            if orig[k+3]>20:
                difference[k+3]=255
                for ch in range(3):
                    difference[k+ch]=min(255,
                        abs(composed[k+ch]-orig[k+ch])*3)
    encode_crop(destination/"neutral-composition-candidate.png",
                composed,[0,0,WIDTH,HEIGHT])
    encode_crop(destination/"roundtrip-diff-review.png",
                difference,[0,0,WIDTH,HEIGHT])
    result={
      "schema":"videoforge/rig-three-candidate-roundtrip-qa/v1",
      "channel":channel,"video_id":video_id,"scene":"cena-01",
      "manual":plan["canonical_manual"],
      "source_original_sha256":plan["reference_sha256"],
      "scene_mother_sha256":plan["scene_mother_sha256"],
      "head_open_bbox":head_box,
      "head_closed_bbox":head_box,
      "body_no_head_bbox":body_box,
      "head_mask_visible_pixels":total_head_visible,
      "body_mask_visible_pixels":total_body_visible,
      "overlapping_head_body_pixels":overlap,
      "overlap_fraction":round(overlapping_fraction,5),
      "neutral_roundtrip_mean_abs_rgb_error":round(error,3),
      "foreign_character_suspect_pixels":foreign_upper_pixels,
      "upper_mask_inspected_pixels":inspected_upper_pixels,
      "foreign_character_suspect_ratio":round(foreign_ratio,5),
      "silhouette_isolation_qa":isolation_status,
      "ready_for_rig":False,
      "head_color_source":"pixel_identical_original_character",
      "closed_head_source":"user_approved_safe_full_closed_png",
      "closed_head_outside_eyes_source_unchanged":True,
      "hidden_anatomy_generated_from_original_reference":True,
      "has_independent_hair_mesh":False,
      "mechanical_qa":"candidate_prepared_not_approved",
      "humanReview":{
        "partsReconstructed":False,
        "noDuplicatedPixels":False,
        "roundTripComposition":False,
        "hairAndFaceOcclusion":False,
        "seamsAndPivot":False
      },
      "mesh_rig_operational":False,
      "youtube_uploaded":False,
    }
    (destination/"qa.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RIG_THREE_RECONSTRUCTION_CANDIDATE_QA",json.dumps(result,ensure_ascii=False))
    return result


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--head",required=True,type=Path)
    p.add_argument("--body",required=True,type=Path)
    p.add_argument("--closed",required=True,type=Path)
    p.add_argument("--dest",required=True,type=Path)
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    a=p.parse_args()
    try:
        result=compose(a.source,a.head,a.body,a.closed,a.dest,a.channel,a.video_id)
        if result["silhouette_isolation_qa"].startswith("rejected"):
            print("RIG_THREE_CANDIDATE_REJECTED_OTHER_CHARACTERS",
                  result["foreign_character_suspect_pixels"],file=sys.stderr)
            return 3
        return 0
    except (VideoForgeError,scene_layers.LayerError,ValueError,OSError,KeyError) as exc:
        print("RIG_THREE_RECONSTRUCTION_QA_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
