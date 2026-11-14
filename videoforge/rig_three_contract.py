"""Contract for a real 2D mesh rig in Remotion/Three.js (opt-in only).

No fallback that animates a flattened PNG may identify itself as a mesh rig.
The caller must supply independent RGBA sprites from the SAME scene-mother,
with measured original-canvas coordinates and human visual approval.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
from pathlib import Path
from .errors import VideoForgeError
from .scene_layers import png_info

SCHEMA = "videoforge/rig-three/v1"
SAFE_NAME = re.compile(r"^[a-z][a-z0-9-]{0,55}\.png$")
REQUIRED = {"body-no-head", "head-open", "head-closed"}
MESH_TYPES = {"cape", "hair-front", "hair-front-left", "hair-front-right", "hair-back", "cloth"}
ALLOWED_TYPES = REQUIRED | MESH_TYPES | {"arm-left", "arm-right", "hand", "prop", "seam-underlay", "ornament-left", "ornament-right"}
MAX_LAYERS = 24


class ThreeRigError(VideoForgeError):
    pass


def _sha(value:object)->str:
    if not isinstance(value,str) or not re.fullmatch("[0-9a-f]{64}",value):
        raise ThreeRigError("THREE_RIG_SHA_INVALID")
    return value


def _finite(value:object,lo:float,hi:float)->float:
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:
        raise ThreeRigError("THREE_RIG_PARAMETER_INVALID")
    return float(value)


def _rect(value:object,width:int,height:int)->list:
    if not isinstance(value,list) or len(value)!=4:
        raise ThreeRigError("THREE_RIG_BBOX_MISSING")
    x,y,w,h=value
    x=_finite(x,0,width);y=_finite(y,0,height)
    w=_finite(w,1,width);h=_finite(h,1,height)
    if x+w>width or y+h>height:
        raise ThreeRigError("THREE_RIG_BBOX_OUTSIDE_CANVAS")
    return [x,y,w,h]


def _mesh(layer:dict)->dict|None:
    entry=layer.get("mesh")
    if entry is None:
        return None
    if layer.get("id") not in MESH_TYPES:
        raise ThreeRigError("THREE_RIG_MESH_ON_UNSUPPORTED_PART")
    if not isinstance(entry,dict) or set(entry)!={"columns","rows","pinnedRows","amplitudePx"}:
        raise ThreeRigError("THREE_RIG_MESH_KEYS_INVALID")
    cols,rows=entry["columns"],entry["rows"]
    if type(cols) is not int or not 2<=cols<=16 or type(rows) is not int or not 2<=rows<=20:
        raise ThreeRigError("THREE_RIG_MESH_DENSITY_INVALID")
    if entry["pinnedRows"]!=[0]:
        raise ThreeRigError("THREE_RIG_MESH_MUST_PIN_ROOT")
    return {"columns":cols,"rows":rows,"pinnedRows":[0],
            "amplitudePx":_finite(entry["amplitudePx"],0.1,12.0)}


def validate_rig_folder(folder:Path,*,channel:str,video_id:str,scene:str,
                        scene_mother_sha256:str,frames:int)->dict:
    if folder.is_symlink() or not folder.is_dir():
        raise ThreeRigError("THREE_RIG_FOLDER_MISSING")
    manifest=folder/"rig.json"
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size>32000:
        raise ThreeRigError("THREE_RIG_MANIFEST_MISSING")
    try:
        doc=json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError) as exc:
        raise ThreeRigError("THREE_RIG_MANIFEST_INVALID") from exc
    if doc.get("schema")!=SCHEMA or any(doc.get(k)!=v for k,v in (
        ("channel",channel),("video_id",video_id),("scene",scene),
        ("sceneMotherSha256",_sha(scene_mother_sha256)))):
        raise ThreeRigError("THREE_RIG_PROVENANCE_INVALID")
    canvas=doc.get("canvas")
    if not isinstance(canvas,dict) or set(canvas)!={"width","height"}:
        raise ThreeRigError("THREE_RIG_CANVAS_INVALID")
    width,height=canvas["width"],canvas["height"]
    if type(width) is not int or type(height) is not int or not 64<=width<=4096 or not 64<=height<=4096:
        raise ThreeRigError("THREE_RIG_CANVAS_INVALID")
    layers=doc.get("layers")
    if not isinstance(layers,list) or not 3<=len(layers)<=MAX_LAYERS:
        raise ThreeRigError("THREE_RIG_LAYER_COUNT_INVALID")
    ids=[item.get("id") for item in layers if isinstance(item,dict)]
    if len(ids)!=len(layers) or len(set(ids))!=len(ids) or not REQUIRED.issubset(ids):
        raise ThreeRigError("THREE_RIG_REQUIRED_PARTS_MISSING_OR_DUPLICATED")
    if any(x not in ALLOWED_TYPES for x in ids):
        raise ThreeRigError("THREE_RIG_PART_NAME_INVALID")
    review=doc.get("humanReview")
    if not isinstance(review,dict) or any(review.get(k) is not True for k in (
        "partsReconstructed","noDuplicatedPixels","roundTripComposition",
        "hairAndFaceOcclusion","seamsAndPivot")):
        raise ThreeRigError("THREE_RIG_HUMAN_REVIEW_REQUIRED")
    qa=doc.get("eyeEditQa")
    if not isinstance(qa,dict) or qa.get("nonEyePixelsChanged")!=0 or qa.get("alphaPixelsChanged")!=0:
        raise ThreeRigError("THREE_RIG_EYE_EDIT_QA_REQUIRED")
    piv=doc.get("neckPivot")
    if not isinstance(piv,list) or len(piv)!=2:
        raise ThreeRigError("THREE_RIG_NECK_PIVOT_REQUIRED")
    pivot=[_finite(piv[0],0,width),_finite(piv[1],0,height)]
    head_deg=_finite(doc.get("headMaxRotationDeg"),.05,2)
    blink=doc.get("blinkFrames")
    if not isinstance(blink,list) or not blink or len(blink)>12 or any(
        type(n) is not int or not 4<=n<frames-4 for n in blink
    ) or any(b-a<12 for a,b in zip(blink,blink[1:])):
        raise ThreeRigError("THREE_RIG_BLINK_FRAMES_INVALID")
    paths=set()
    validated=[]
    for item in layers:
        file=item.get("file")
        if not isinstance(file,str) or not SAFE_NAME.fullmatch(file) or file in paths:
            raise ThreeRigError("THREE_RIG_FILE_UNSAFE_OR_DUPLICATED")
        paths.add(file)
        asset=folder/file
        if asset.is_symlink() or not asset.is_file() or asset.stat().st_size>24_000_000:
            raise ThreeRigError("THREE_RIG_ASSET_MISSING")
        raw=asset.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=_sha(item.get("sha256")):
            raise ThreeRigError("THREE_RIG_ASSET_HASH_MISMATCH")
        info=png_info(raw,require_alpha=True)
        bbox=_rect(item.get("bbox"),width,height)
        if not all(float(v).is_integer() for v in bbox):
            raise ThreeRigError("THREE_RIG_BBOX_PIXEL_COORDS_REQUIRED")
        if (info["width"],info["height"])!=(int(bbox[2]),int(bbox[3])):
            raise ThreeRigError("THREE_RIG_CROP_CANVAS_MISMATCH")
        mesh=_mesh(item)
        z=item.get("z")
        if type(z) is not int or not -50<=z<=50:
            raise ThreeRigError("THREE_RIG_Z_INVALID")
        validated.append({"id":item["id"],"file":"vf-scene/rig-three/"+file,
                          "bbox":bbox,"sha256":_sha(item["sha256"]),"z":z,
                          **({"mesh":mesh} if mesh is not None else {})})
    head=[item for item in validated if item["id"]=="head-open"][0]
    if not (head["bbox"][0] <= pivot[0] <= head["bbox"][0]+head["bbox"][2]
            and head["bbox"][1] <= pivot[1] <= head["bbox"][1]+head["bbox"][3]):
        raise ThreeRigError("THREE_RIG_NECK_PIVOT_OUTSIDE_HEAD")
    for n in ("head-open","head-closed"):
        if [x for x in validated if x["id"]==n][0]["bbox"]!=head["bbox"]:
            raise ThreeRigError("THREE_RIG_EYES_SWAP_MISALIGNED")
    # Duplicate body/head pixels are a VISUAL/roundtrip review contract,
    # never inferred merely from a valid alpha channel.
    return {"schema":SCHEMA,"canvas":canvas,"sceneMotherSha256":scene_mother_sha256,
            "layers":validated,"neckPivot":pivot,
            "headMaxRotationDeg":head_deg,"blinkFrames":blink,
            "rigType":"independent-parts-and-deformable-mesh",
            "technicalAssetsVerified":True,"humanVisualReview":True,
            "youtubeUploaded":False}
