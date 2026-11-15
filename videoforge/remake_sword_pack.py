"""Assemble C01-P02 from permanent per-run GitHub image archives.

No proxy, generated images, fake screenshots, auto-approval or YouTube. Looks
up actual archived producer PNGs by SHA and their exact scene-mother provenance.
Only the existing ThreeCanvas validator can authorize a technical preview.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys

from .errors import VideoForgeError
from .remake_autopilot import ROOT,EPISODE,verified_asset
from .remake_sword_preview import (
    CH,VID,SHOT,W,H,PARTS,SCHEMA,ARTIFACT_PREFIX,
    canonical_anchor,compare_source_to_neutral,decode_rgba_for_qa,
    validate_package,sha,read_json,
)
from .scene_layers import png_info

ARCHIVE_SCHEMA="videoforge/permanent-generated-image-archive/v1"
PACK_SCHEMA="videoforge/remake-sword-pack-report/v1"
MOTHER_NAME="cena-01-c01-p02.png"
MOTHER_PRODUCER="production-scene-request"
PART_PRODUCER="production-rgba-request"
UNDERLAY_PRODUCER="production-sword-underlay-request"
RUN_RE=re.compile(r"[1-9][0-9]{0,19}\Z")


def _archived(episode:Path,producer:str,filename:str)->list[dict]:
    """Find immutable candidates, only from the exact channel/video/producer."""
    archive=episode/"assets"/"geracoes"/producer
    if not archive.exists():return []
    if archive.is_symlink() or not archive.is_dir():
        raise VideoForgeError("REMAKE_PACK_ARCHIVE_DIRECTORY_UNSAFE")
    found=[]
    for run in archive.iterdir():
        if run.is_symlink() or not run.is_dir() or not RUN_RE.fullmatch(run.name):
            continue
        manifest_path=run/"manifesto-geracoes.json"
        try:doc=read_json(manifest_path)
        except VideoForgeError:continue
        if (doc.get("schema")!=ARCHIVE_SCHEMA or doc.get("producer")!=producer
            or doc.get("channel")!=CH or doc.get("video_id")!=VID
            or doc.get("github_run_id")!=int(run.name)
            or doc.get("production_approved") is not False
            or doc.get("youtube_uploaded") is not False):
            continue
        images=[x for x in doc.get("images",[]) if isinstance(x,dict)
                and x.get("file")==filename]
        if len(images)!=1:
            continue
        entry=images[0]
        relative=f"assets/geracoes/{producer}/{run.name}/{filename}"
        if not verified_asset(episode,relative,entry.get("sha256")):
            continue
        raw=episode/relative
        try:
            info=png_info(raw.read_bytes(),
                          require_alpha=False if producer in (MOTHER_PRODUCER,UNDERLAY_PRODUCER)
                          else True,min_visible_fraction=.0002)
        except (ValueError,OSError):continue
        if (info["width"],info["height"])!=(W,H):
            continue
        found.append({"run_id":int(run.name),"producer":producer,
                      "path":raw,"sha256":entry["sha256"],
                      "archive_manifest":manifest_path})
    return sorted(found,key=lambda x:x["run_id"],reverse=True)


def _find_mother(episode:Path,anchor_sha:str)->dict|None:
    for entry in _archived(episode,MOTHER_PRODUCER,MOTHER_NAME):
        report=entry["path"].with_suffix(".production.json")
        try:doc=read_json(report)
        except VideoForgeError:continue
        if (doc.get("schema")=="videoforge/production-scene/v1"
            and doc.get("channel")==CH and doc.get("video_id")==VID
            and doc.get("number")==1 and doc.get("scene")=="c01"
            and doc.get("shot_id")==SHOT and doc.get("shot_specific") is True
            and doc.get("reference_sha256")==anchor_sha
            and doc.get("sha256")==entry["sha256"]
            and doc.get("technical_qa")=="valid_png_opaque"
            and doc.get("youtube_uploaded") is False):
            return {**entry,"production_report":report}
    return None


def _find_part(episode:Path,part:str,mother_sha:str)->dict|None:
    if part=="underlay":
        producer=UNDERLAY_PRODUCER
        expected_schema="videoforge/remake-underlay-candidate/v1"
    elif part in ("sheath","blade","hand"):
        producer=PART_PRODUCER
        expected_schema="videoforge/rgba-part-candidate/v1"
    else:
        raise VideoForgeError("REMAKE_PACK_UNKNOWN_PART")
    for entry in _archived(episode,producer,part+".png"):
        qa_path=entry["path"].with_suffix(".qa.json")
        try:qa=read_json(qa_path)
        except VideoForgeError:continue
        if (qa.get("schema")!=expected_schema
            or qa.get("channel")!=CH or qa.get("video_id")!=VID
            or qa.get("output_sha256")!=entry["sha256"]
            or qa.get("scene_mother_sha256")!=mother_sha
            or qa.get("technical_status") not in
               (("candidate_opaque_verified",) if part=="underlay"
                 else ("candidate_rgba_verified",))
            or qa.get("human_visual_approval") is not False
            or qa.get("youtube_uploaded") is not False):
            continue
        if part=="underlay":
            if qa.get("shot_id")!=SHOT:
                continue
        else:
            if qa.get("scene_number")!=1 or qa.get("part_id")!=part:
                continue
        return {**entry,"qa_report":qa_path}
    return None


def locate(root:Path=ROOT)->dict:
    """Read-only, deterministic scan. Block safely if upstream has not generated."""
    episode=Path(root)/EPISODE
    try:anchor=canonical_anchor(root)
    except VideoForgeError as exc:
        return {"ready":False,"blocker":str(exc),"anchor":None,
                "mother":None,"parts":{}}
    mother=_find_mother(episode,anchor["sha256"])
    if mother is None:
        return {"ready":False,"blocker":"REMAKE_PACK_REAL_C01_P02_MOTHER_NOT_ARCHIVED",
                "anchor":anchor,"mother":None,"parts":{}}
    # Do not loop forever when a preview's original source is already QA'd.
    recorded=episode/"QA-C01-P02-REMAKE-V2.json"
    if recorded.is_file() and not recorded.is_symlink():
        try:prior=read_json(recorded)
        except VideoForgeError:prior={}
        if (prior.get("schema")=="videoforge/remake-sword-preview-qa/v1"
            and prior.get("source_mother_sha256")==mother["sha256"]
            and prior.get("anchor_sha256")==anchor["sha256"]
            and prior.get("technical_preview_only") is True
            and prior.get("official_video_approved") is False
            and prior.get("youtube_uploaded") is False):
            return {"ready":False,
                "blocker":"REMAKE_PACK_SAME_SOURCE_ALREADY_RENDERED_TECHNICALLY",
                "anchor":anchor,"mother":mother,"parts":{}}
    parts={k:_find_part(episode,k,mother["sha256"]) for k in PARTS}
    missing=[k for k,v in parts.items() if v is None]
    return {"ready":not missing,
      "blocker":("REMAKE_PACK_MISSING_SAME_MOTHER_PARTS:"+",".join(missing)) if missing else None,
      "anchor":anchor,"mother":mother,"parts":parts}


def scan(root:Path=ROOT)->dict:
    found=locate(root)
    return {"schema":PACK_SCHEMA,"shot_id":SHOT,"ready":found["ready"],
        "blocker":found["blocker"],"source_mother_sha256":(
            found["mother"]["sha256"] if found["mother"] else None),
        "archived_sources_found":{part:entry is not None
            for part,entry in found["parts"].items()},
        "next_work":("package_existing_original_pngs_no_image_generation"
                     if found["ready"] else "await_real_art_and_origin_approval"),
        "new_image_generation_calls":0,
        "automatic_paid_provider_calls":False,
        "official_video_approved":False,"youtube_uploaded":False}


def _anatomical_estimate(package:Path)->tuple[list[int],dict]:
    """Source-pixel heuristic for DRAFT ONLY; *not* a human wrist approval."""
    _,boxes=compare_source_to_neutral(package)
    hx0,hy0,hx1,hy1=boxes["hand"]
    bx0,by0,bx1,by1=boxes["blade"]
    if hx1-hx0<3 or hy1-hy0<3 or bx1-bx0<3 or by1-by0<3:
        raise VideoForgeError("REMAKE_PACK_MASK_GEOMETRY_TOO_SMALL")
    hand=decode_rgba_for_qa(package/"hand.png")
    target_y=max(hy0,min(hy1-1,int(hy0+(hy1-hy0)*.87)))
    xs=[x for x in range(hx0,hx1)
        if hand[(target_y*W+x)*4+3]>127]
    if not xs:
        raise VideoForgeError("REMAKE_PACK_WRIST_PIVOT_CANNOT_BE_INFERRED")
    pivot=[(min(xs)+max(xs))//2,target_y]
    # Estimate a movement direction from actual blade silhouette, never a
    # fabricated measurement. It is reviewed before editorial approval.
    axis=-72 if (by1-by0)>(bx1-bx0) else -12
    rad=math.radians(axis)
    ux,uy=math.cos(rad),math.sin(rad)
    max_dx=((W+12-bx1)/ux if ux>0 else (bx0+12)/-ux) if abs(ux)>1e-8 else 400
    max_dy=((H+12-by1)/uy if uy>0 else (by0+12)/-uy) if abs(uy)>1e-8 else 400
    requested=min(210,max(8,int(max(bx1-bx0,by1-by0)*.22)))
    travel=int(min(requested,max_dx-2,max_dy-2,240))
    if travel<2:
        raise VideoForgeError("REMAKE_PACK_NO_ROOM_FOR_SWORD_DRAW")
    return pivot,{"beginFrame":7,"finishFrame":72,"travelPx":travel,
                  "axisDeg":axis,"handFollow":.80,"handRotationDeg":2.0}


def assemble(source_run_id:int,output:Path,root:Path=ROOT)->dict:
    if type(source_run_id) is not int or source_run_id<=0:
        raise VideoForgeError("REMAKE_PACK_RUN_ID_REQUIRED")
    src=locate(root)
    if not src["ready"]:
        raise VideoForgeError(src["blocker"])
    output=Path(output)
    if output.is_symlink() or (output.exists() and any(output.iterdir())):
        raise VideoForgeError("REMAKE_PACK_DESTINATION_NOT_EMPTY")
    output.mkdir(parents=True,exist_ok=True)
    mother=src["mother"]
    filemap={
      "scene-mother.png":mother["path"],
      "scene-mother.production.json":mother["production_report"],
      **{part+".png":src["parts"][part]["path"] for part in PARTS},
    }
    for name,from_path in filemap.items():
        dest=output/name
        if from_path.is_symlink() or dest.exists():
            raise VideoForgeError("REMAKE_PACK_SYMLINK_OR_COLLISION")
        shutil.copyfile(from_path,dest)
    pivot,draw=_anatomical_estimate(output)
    parts_meta={part:{
       "producer":src["parts"][part]["producer"],
       "source_run_id":src["parts"][part]["run_id"],
       "sha256":src["parts"][part]["sha256"],
       "original_metadata_path":src["parts"][part]["qa_report"].as_posix(),
    } for part in PARTS}
    artifact=ARTIFACT_PREFIX+str(source_run_id)
    bundle={"schema":SCHEMA,"channel":CH,"video_id":VID,"shot_id":SHOT,
      "source_run_id":source_run_id,"source_artifact":artifact,
      "anchor_sha256":src["anchor"]["sha256"],
      "sha256":{"scene-mother":mother["sha256"],
                **{part:src["parts"][part]["sha256"] for part in PARTS}},
      "source_archives":{
        "scene-mother":{"producer":MOTHER_PRODUCER,
           "source_run_id":mother["run_id"],"sha256":mother["sha256"]},
        **parts_meta,
      },
      "wristPivot":pivot,"draw":draw,
      "draft_motion_heuristic_only":True,"human_motion_review_required":True,
      "human_visual_approved":False,"official_video_approved":False,
      "youtube_uploaded":False}
    (output/"sword-bundle.json").write_text(
      json.dumps(bundle,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    qa=validate_package(output,source_run_id,root)
    report={"schema":PACK_SCHEMA,"shot_id":SHOT,
      "status":"SOURCE_BUNDLE_VERIFIED_NOT_HUMAN_APPROVED",
      "artifact_name":artifact,"source_run_id":source_run_id,
      "neutral_mae_rgb":qa["neutral_mae_rgb"],
      "source_mother_sha256":mother["sha256"],
      "sources":bundle["source_archives"],
      "rig_pivot_draft":pivot,"rig_draw_draft":draw,
      "draft_motion_heuristic_only":True,"human_motion_review_required":True,
      "technical_preview_only":True,"new_image_generation_calls":0,
      "official_video_approved":False,"youtube_uploaded":False}
    (output/"package.qa.json").write_text(
      json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def main()->int:
    p=argparse.ArgumentParser(description="Assemble real C01-P02 shot from verified GitHub archive")
    p.add_argument("action",choices=["scan","pack"])
    p.add_argument("--output-dir",type=Path)
    p.add_argument("--run-id",type=int,default=0)
    args=p.parse_args()
    try:
        if args.action=="scan":
            report=scan()
            print("REMAKE_C01_P02_PACK_SCAN",json.dumps(report,ensure_ascii=False))
            if args.output_dir is not None:
                args.output_dir.mkdir(parents=True,exist_ok=True)
                (args.output_dir/"pack-scan.json").write_text(
                    json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        else:
            if args.output_dir is None:
                raise VideoForgeError("REMAKE_PACK_OUTPUT_DIR_REQUIRED")
            report=assemble(args.run_id,args.output_dir)
            print("REMAKE_C01_P02_PACKAGE",json.dumps(report,ensure_ascii=False))
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError) as exc:
        print("REMAKE_C01_P02_PACK_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
