"""Exports fully approved cinematic EDL to separate Remotion/ThreeCanvas props.

No image-generation calls. Does NOT create test/fake media to satisfy QA.
Fail-closed unless all 36 source mothers, RGBA crops, underlays, meshes and
human approvals are present and SHA-validated in the SAME shot directory.
Only then can approved original pixels be copied to Remotion/public.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

from .cinematic_shot_assets import (
    ROOT, RIG_SCHEMA, QA_SCHEMA, build_edl, _load_json, _file_from_rel,
    _png_valid, CANVAS, validate_shot_canvas,
)
from .errors import VideoForgeError

OUTPUT_PREFIX="vf-cinema"

def _check_bbox(bbox:object,canvas:tuple[int,int]=CANVAS)->tuple[int,int]:
    if not (isinstance(bbox,list) and len(bbox)==4
            and all(type(k) is int for k in bbox)
            and bbox[0]>=0 and bbox[1]>=0
            and bbox[2]>0 and bbox[3]>0
            and bbox[0]+bbox[2]<=canvas[0]
            and bbox[1]+bbox[3]<=canvas[1]):
        raise VideoForgeError("CINEMATIC_EXPORTED_RIG_BBOX_INVALID")
    return bbox[2],bbox[3]

def build_props(channel:str,video_id:str,root:Path=ROOT)->tuple[dict,list[tuple[Path,str]]]:
    """Pure check/build; returns props and source -> approved public relative paths."""
    edl=build_edl(channel,video_id,root)
    if not edl["renderOfficialAllowed"]:
        raise VideoForgeError(
            "CINEMATIC_EXPORT_UNAPPROVED_SHOTS_"+
            str(edl["unapprovedShots"])
        )
    if edl["visualReferenceConflict"]:
        raise VideoForgeError("CINEMATIC_EXPORT_CANONICAL_REFERENCE_CONFLICT")
    base=root/"canal"/channel/"videos"/video_id
    public_base=OUTPUT_PREFIX+"/"+channel+"/"+video_id+"/"
    copies={}
    shots=[]
    for shot in edl["shots"]:
        record={
            "id":shot["id"],"scene":shot["scene"],
            "startFrame":shot["startFrame"],
            "endFrameExclusive":shot["endFrameExclusive"],
            "type":shot["type"],"characters":shot["characters"],
            "hudPolicy":shot["hudPolicy"],"renderAllowed":True,
        }
        if shot["type"]=="black":
            record["status"]="black_no_art_required"
            shots.append(record)
            continue
        paths=shot["assetPaths"]
        data=_load_json(base/paths["rig"])
        review=_load_json(base/paths["qa"])
        if (data.get("schema")!=RIG_SCHEMA or
            review.get("schema")!=QA_SCHEMA or
            data.get("shot_id")!=shot["id"] or
            review.get("shot_id")!=shot["id"] or
            review.get("human_visual_approved") is not True):
            raise VideoForgeError("CINEMATIC_EXPORT_PROVENANCE_OR_QA_INVALID")
        source_sha=data["source_sha256"]
        native_canvas=validate_shot_canvas(data)
        def asset(rel:str,expected:str,alpha:bool,size:tuple[int,int])->str:
            src=_file_from_rel(base,rel)
            if not rel.startswith("assets/planos/"+shot["id"]+"/"):
                raise VideoForgeError("CINEMATIC_EXPORT_CROSS_SHOT_FILE")
            if not _png_valid(src,expected,alpha,size):
                raise VideoForgeError("CINEMATIC_EXPORT_MISSING_OR_BAD_PNG_SHA")
            out=public_base+rel
            old=copies.get(out)
            if old is not None and old!=src:
                raise VideoForgeError("CINEMATIC_EXPORT_FILENAME_COLLISION")
            copies[out]=src
            return out
        # Source mother is verified for provenance but NOT composited as
        # a foreground layer, since it includes the whole already-drawn cast.
        mother=_file_from_rel(base,paths["mother"])
        if not _png_valid(mother,source_sha,False,native_canvas):
            raise VideoForgeError("CINEMATIC_EXPORT_MOTHER_INVALID")
        background=asset(paths["background"],data["background_sha256"],
                         False,native_canvas)
        parts=data.get("parts",[])
        part_index={}
        for part in parts:
            if not isinstance(part,dict) or not isinstance(part.get("name"),str):
                raise VideoForgeError("CINEMATIC_EXPORT_PART_ENTRY_INVALID")
            _check_bbox(part.get("bbox"),native_canvas)
            part_index[part["path"]]=(part["sha256"],part["bbox"])
        source_actors=data.get("actors")
        if not isinstance(source_actors,list):
            raise VideoForgeError("CINEMATIC_EXPORT_ACTORS_NOT_DECLARED")
        actors=[]
        names=set()
        for actor in source_actors:
            if not isinstance(actor,dict) or actor.get("id") in names:
                raise VideoForgeError("CINEMATIC_EXPORT_ACTOR_INVALID")
            names.add(actor["id"])
            rig=copy.deepcopy(actor.get("rig"))
            if not isinstance(rig,dict):
                raise VideoForgeError("CINEMATIC_EXPORT_RIG_MISSING")
            if (rig.get("schema")!="videoforge/rig-three/v1"
                    or rig.get("rigType")!="independent-parts-and-deformable-mesh"
                    or rig.get("technicalAssetsVerified") is not True
                    or rig.get("humanVisualReview") is not True
                    or rig.get("youtubeUploaded") is not False
                    or rig.get("sceneMotherSha256")!=source_sha
                    or rig.get("canvas")!=data.get("canvas")):
                raise VideoForgeError("CINEMATIC_EXPORT_ACTOR_RIG_UNAPPROVED")
            layers=rig.get("layers")
            if not isinstance(layers,list) or len(layers)<3 or not any(
                isinstance(layer,dict) and isinstance(layer.get("mesh"),dict)
                for layer in layers
            ):
                raise VideoForgeError("CINEMATIC_EXPORT_NOT_MESH_RIG")
            ids=set()
            for layer in layers:
                if not isinstance(layer,dict) or layer.get("id") in ids:
                    raise VideoForgeError("CINEMATIC_EXPORT_DUPLICATE_LAYER")
                ids.add(layer["id"])
                size=_check_bbox(layer.get("bbox"),native_canvas)
                rel=layer.get("file")
                if rel not in part_index or part_index[rel]!=(
                    layer.get("sha256"),layer.get("bbox")
                ):
                    raise VideoForgeError("CINEMATIC_EXPORT_LAYER_NOT_IN_QA")
                layer["file"]=asset(rel,layer["sha256"],True,size)
            if not {"body-no-head","head-open","head-closed"}.issubset(ids):
                raise VideoForgeError("CINEMATIC_EXPORT_HEAD_BODY_LAYERS_MISSING")
            if (not isinstance(rig.get("neckPivot"),list)
                    or len(rig["neckPivot"])!=2
                    or not all(isinstance(v,(float,int)) for v in rig["neckPivot"])
                    or not isinstance(rig.get("blinkFrames"),list)):
                raise VideoForgeError("CINEMATIC_EXPORT_JOINT_DATA_MISSING")
            actors.append({
                "id":actor["id"],"rig":rig,
                "motherSha256":source_sha,"approvedForShot":True,
            })
        static_ok=(not actors and review.get("static_shot_approved") is True)
        if not actors and not static_ok:
            raise VideoForgeError("CINEMATIC_EXPORT_EMPTY_RIG_UNAPPROVED")
        if shot["type"] in ("close_up","extreme_close_up") and not actors:
            raise VideoForgeError("CINEMATIC_EXPORT_CLOSEUP_WITHOUT_RIG")
        hud=None
        if shot["hudPolicy"]=="remotion_overlay":
            hud=data.get("hud")
            if not isinstance(hud,dict) or not hud.get("heading") or (
                review.get("hud_text_approved") is not True
            ):
                raise VideoForgeError("CINEMATIC_EXPORT_HUD_NOT_APPROVED")
        from .cinematic_identity_continuity import verify_shot_continuity
        verify_shot_continuity(shot,data,review,root)
        if shot["id"]=="C12-P01":
            from .cinematic_eye_motion import check_eye_performance
            from .cinematic_eye_pixel_audit import audit_existing_eye_assets
            # The exporter repeats the pixel sweep (including sclera coverage)
            # even if someone bypasses a cached EDL / QA report.
            audit_existing_eye_assets(base,shot["id"],data,review)
            record["performance"]=check_eye_performance(
                shot["id"],data,review
            )
        elif data.get("performance") is not None:
            raise VideoForgeError("CINEMATIC_EXPORT_GAZE_UNEXPECTED_SHOT")
        if shot["type"] in ("close_up","extreme_close_up","insert"):
            from .cinematic_frame_fit import validate_focal_box
            record["focalBbox"]=validate_focal_box(
                native_canvas,review.get("focal_bbox")
            )["focalBbox"]
        record.update({
            "status":"ready_for_render",
            "backgroundFile":background,
            "backgroundSha256":data["background_sha256"],
            "sourceMotherSha256":source_sha,
            "sourceCanvas":{"width":native_canvas[0],"height":native_canvas[1]},
            "actors":actors,
            "staticShotApproved":static_ok,
            "humanVisualApproved":True,
            "originShaVerified":True,
            "hud":hud,
            "audioFile":None,
        })
        shots.append(record)
    props={
        "schema":"videoforge/cinematic-remotion-episode/v1",
        "channel":channel,"videoId":video_id,
        "fps":30,"width":1080,"height":1920,
        "totalFrames":4890,
        "renderApproved":True,
        "shots":shots,
    }
    return props,sorted(((src,dst) for dst,src in copies.items()),key=lambda x:x[1])

def stage(props:dict,files:list[tuple[Path,str]],root:Path=ROOT)->Path:
    """Copies approved artwork only AFTER every SHA/QA is validated."""
    import os
    public=(root/"motion-remotion"/"public")
    target=root/"output"/props["channel"]/"videos"/props["videoId"]/"cinematic-render-props.json"
    if public.is_symlink() or target.is_symlink() or target.exists():
        raise VideoForgeError("CINEMATIC_EXPORT_STAGE_DEST_UNSAFE")
    if any((public/dst).exists() or (public/dst).is_symlink() for src,dst in files):
        raise VideoForgeError("CINEMATIC_EXPORT_ASSETS_ALREADY_STAGED")
    for src,dst in files:
        dest=public/dst
        if any(p.is_symlink() for p in dest.parents):
            raise VideoForgeError("CINEMATIC_EXPORT_PARENT_SYMLINK")
    # Files only copied AFTER entire plan & SHA validation has succeeded.
    for src,dst in files:
        out=public/dst
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(props,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return target

def main()->int:
    parser=argparse.ArgumentParser(description="Preflight/check cinematic Remotion props; no image generation")
    parser.add_argument("--channel",default="alchemy-lab")
    parser.add_argument("--video-id",default="mmorpg-conquiste-a-princesa-ep01")
    parser.add_argument("--stage",action="store_true",
                        help="Copy SHA-validated assets and write approved Remotion props")
    args=parser.parse_args()
    try:
        props,files=build_props(args.channel,args.video_id)
        if args.stage:
            dest=stage(props,files)
            print("CINEMATIC_REMOTION_READY_FOR_RENDER",dest,len(files),"assets")
        else:
            print("CINEMATIC_REMOTION_SOURCE_VERIFIED",len(files),"assets; no copy")
        return 0
    except (VideoForgeError,ValueError,OSError,KeyError,TypeError) as exc:
        print("CINEMATIC_REMOTION_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
