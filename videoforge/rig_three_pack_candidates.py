"""Pack source-derived Anya sprites into cropped PNGs + a BLOCKED rig draft.

The output rig.json is intentionally rejected by the official visual-review
gate. These are authentic same-canvas aligned candidate sprites, not a
shortcut around approval or a finished ThreeCanvas render.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

from .animation_manual import enforce_animation_manual
from .errors import VideoForgeError
from .rig_three_art import load_plan
from .rig_three_contract import validate_rig_folder, ThreeRigError
from .rig_three_hand_split import read_rgba, sha, unique, write
from .rig_three_hair_draft import W,H,SOURCE_SHA

SCENE="cena-01"
CHANNEL="otaku-br"
VIDEO="spy-x-family-familia-de-mentira"
LAYERS=(
 ("body-no-head","body-no-hair-residue-draft.png",20,None),
 ("head-open","head-open-with-side-hair-underlay-draft.png",30,None),
 ("head-closed","head-closed-with-side-hair-underlay-draft.png",30,None),
 ("hair-front-left","hair-left-with-original-shoulder-fragment-draft.png",35,4),
 ("hair-front-right","hair-right-with-original-shoulder-fragment-draft.png",36,4),
 ("hand","hand-foreground-candidate.png",50,None),
)


def _bbox(image,np):
    ys,xs=np.where(image[:,:,3]>0)
    if not len(xs):
        raise VideoForgeError("RIG_CANDIDATE_EMPTY_SPRITE")
    return [int(xs.min()),int(ys.min()),
            int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1)]


def pack(art_dir:Path,corrected_dir:Path,dest:Path):
    enforce_animation_manual()
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise VideoForgeError("RIG_CANDIDATE_PACK_OPENCV_REQUIRED") from exc
    if dest.exists() or dest.is_symlink():
        raise VideoForgeError("RIG_CANDIDATE_PACK_NO_OVERWRITE")
    report=json.loads(unique(art_dir,"qa.json").read_text(encoding="utf-8"))
    corrected=json.loads(unique(corrected_dir,"qa.json").read_text(encoding="utf-8"))
    if (report.get("schema")!="videoforge/rig-three-anya-hair-underlay-draft/v1"
            or report.get("reference_original_sha256")!=SOURCE_SHA
            or report.get("human_visual_approval") is not False
            or report.get("real_threecanvas_render_passed") is not False
            or report.get("neutral_pixels_with_rgb_error_gt20")!=0
            or report.get("neutral_pixels_with_alpha_error_gt3")!=0
            or corrected.get("source_original_sha256")!=SOURCE_SHA):
        raise VideoForgeError("RIG_CANDIDATE_PACK_QA_SOURCE_INVALID")
    source_plan=load_plan(CHANNEL,VIDEO)
    scene_sha=source_plan["scene_mother_sha256"]
    images={}
    for layer,filename,_,_ in LAYERS:
        folder=corrected_dir if layer=="hand" else art_dir
        corresponding=corrected if layer=="hand" else report
        source=unique(folder,filename)
        if corresponding.get("files",{}).get(filename)!=sha(source):
            raise VideoForgeError("RIG_CANDIDATE_PACK_FILE_SHA_INVALID_"+layer)
        pixels=read_rgba(source,cv2,np)
        if pixels.shape!=(H,W,4):
            raise VideoForgeError("RIG_CANDIDATE_PACK_INPUT_CANVAS_INVALID")
        images[layer]=pixels
    if np.any(images["head-open"][:,:,3]!=images["head-closed"][:,:,3]):
        raise VideoForgeError("RIG_CANDIDATE_PACK_EYE_ALPHA_INVALID")
    changed=np.any(images["head-open"][:,:,:3]!=images["head-closed"][:,:,:3],axis=2)
    eye_count=int(np.count_nonzero(changed))
    if not 1000<=eye_count<=30000:
        raise VideoForgeError("RIG_CANDIDATE_PACK_EYE_REGION_INVALID")
    head_box=_bbox(images["head-open"],np)
    if _bbox(images["head-closed"],np)!=head_box:
        raise VideoForgeError("RIG_CANDIDATE_PACK_HEAD_BBOX_INVALID")
    dest.mkdir(parents=True)
    specs=[]
    for layer,_,z,amplitude in LAYERS:
        image=images[layer]
        box=head_box if layer in ("head-open","head-closed") else _bbox(image,np)
        x,y,w,h=box
        cropped=image[y:y+h,x:x+w].copy()
        filename=layer+".png"
        write(dest/filename,cropped,cv2)
        # Cropping must preserve all alpha and every visible source RGB pixel.
        reread=read_rgba(dest/filename,cv2,np)
        restored=np.zeros_like(image)
        restored[y:y+h,x:x+w]=reread
        if np.any(restored[:,:,3]!=image[:,:,3]):
            raise VideoForgeError("RIG_CANDIDATE_PACK_ALPHA_ROUNDTRIP_INVALID")
        nonzero=image[:,:,3]>0
        if np.any(restored[:,:,:3][nonzero]!=image[:,:,:3][nonzero]):
            raise VideoForgeError("RIG_CANDIDATE_PACK_RGB_ROUNDTRIP_INVALID")
        spec={"id":layer,"file":filename,"bbox":box,
              "sha256":sha(dest/filename),"z":z}
        if amplitude is not None:
            spec["mesh"]={"columns":7,"rows":9,"pinnedRows":[0],
                          "amplitudePx":amplitude}
        specs.append(spec)
    rig={
      "schema":"videoforge/rig-three/v1",
      "channel":CHANNEL,"video_id":VIDEO,"scene":SCENE,
      "sceneMotherSha256":scene_sha,
      "canvas":{"width":W,"height":H},
      "neckPivot":[515,1429],
      "headMaxRotationDeg":2,
      "blinkFrames":[74,173],
      "eyeEditQa":{"nonEyePixelsChanged":0,"alphaPixelsChanged":0},
      "humanReview":{
         "partsReconstructed":False,"noDuplicatedPixels":False,
         "roundTripComposition":False,"hairAndFaceOcclusion":False,
         "seamsAndPivot":False
      },
      "layers":specs,
      "candidateSourceOriginalSHA256":SOURCE_SHA,
      "provisional":True,
      "youtubeUpload":False
    }
    (dest/"rig.json").write_text(json.dumps(rig,ensure_ascii=False,indent=2)+"\n",
                                 encoding="utf-8")
    # Crucial: prove the real production validator rejects the candidate.
    blocked=False
    try:
        validate_rig_folder(dest,channel=CHANNEL,video_id=VIDEO,
                            scene=SCENE,scene_mother_sha256=scene_sha,
                            frames=240)
    except ThreeRigError as exc:
        if "THREE_RIG_HUMAN_REVIEW_REQUIRED" not in str(exc):
            raise
        blocked=True
    if not blocked:
        raise VideoForgeError("RIG_CANDIDATE_PACK_FAIL_CLOSED_BROKEN")
    qa={
       "schema":"videoforge/rig-three-cropped-draft-pack/v1",
       "channel":CHANNEL,"video_id":VIDEO,"scene":SCENE,
       "source_character_sha256":SOURCE_SHA,
       "scene_mother_sha256":scene_sha,
       "layers_cropped":len(specs),
       "deformable_side_hair_meshes":2,
       "mesh_grid":"7x9","root_pinned_row":0,
       "original_canvas":[W,H],
       "closed_open_head_bbox_identical":True,
       "approved_eye_change_pixels_preserved":eye_count,
       "crop_roundtrip_alpha_and_visible_rgb_exact":True,
       "pivot_is_provisional":True,
       "Loid_Yor_static_composition_integration":"pending",
       "human_art_review":"pending",
       "real_anime_ThreeCanvas_render":"pending",
       "rig_production_validation":"EXPECTED_REJECTION_HUMAN_REVIEW_REQUIRED",
       "human_visual_approval":False,
       "rig_operational":False,
       "video_official":False,"youtube_uploaded":False,
       "files":{p.name:sha(p) for p in dest.glob("*.png")},
    }
    (dest/"pack.qa.json").write_text(json.dumps(qa,ensure_ascii=False,
                                            indent=2)+"\n",encoding="utf-8")
    print("RIG_THREE_ANYA_CROPPED_DRAFT_PACK",json.dumps(qa))
    return qa


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--art",required=True,type=Path)
    ap.add_argument("--corrected",required=True,type=Path)
    ap.add_argument("--dest",required=True,type=Path)
    args=ap.parse_args()
    try:
        pack(args.art,args.corrected,args.dest)
        return 0
    except (ThreeRigError,VideoForgeError,OSError,ValueError,KeyError) as exc:
        print("RIG_THREE_ANYA_CROPPED_PACK_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
