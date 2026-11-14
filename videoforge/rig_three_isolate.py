"""Isolate Anya's REAL original pixels from Loid/Yor without a new AI image.

This is an *asset preparation* step (not render), using GrabCut once with
guidance from the existing same-image AI head candidate. It yields a clean
large-Anya silhouette, background/other-characters counterpart, hair draft
and pixel-perfect full-character blink variants. All outputs are DRAFTS.

The renderer cannot call this step; artifacts are reused by SHA after QA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from .animation_manual import enforce_animation_manual
from .rig_three_art import load_plan, check_source
from .errors import VideoForgeError

W,H=1024,1536
SOURCE_SHA="c3b21ecd072d3fbf6978f04e6cde5db5d9083e13871b475e6f8c9229a15b0b2c"
CLOSED_SHA="668434bae05289b4400224012b420bfc94e07bee2b972b2e2add2b6d0e8b9694"
# Restricts segmentation to the full-size Anya at the BOTTOM of the original.
# Coordinates are guide constraints, not replacement art.
ROW_BOUNDS=[
  (890,480,480),(912,460,535),(945,455,545),(978,391,623),
  (1010,341,690),(1030,316,718),(1070,276,747),(1110,260,765),
  (1170,235,782),(1240,223,792),(1300,207,804),(1360,201,812),
  (1410,208,807),(1460,229,791),(1500,285,738),(1535,295,729),
]


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_rgba(path:Path,cv2,np):
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("RIG_ISOLATE_SOURCE_MISSING")
    b=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
    if b is None or b.shape!=(H,W,4) or b.dtype!=np.uint8:
        raise VideoForgeError("RIG_ISOLATE_WRONG_RGBA_OR_CANVAS")
    return cv2.cvtColor(b,cv2.COLOR_BGRA2RGBA)


def _write_rgba(path:Path,a,cv2,np):
    if path.exists() or path.is_symlink():
        raise VideoForgeError("RIG_ISOLATE_NO_OVERWRITE")
    if a.shape!=(H,W,4) or a.dtype!=np.uint8:
        raise VideoForgeError("RIG_ISOLATE_OUTPUT_INVALID")
    if not cv2.imwrite(str(path),cv2.cvtColor(a,cv2.COLOR_RGBA2BGRA)):
        raise VideoForgeError("RIG_ISOLATE_ENCODE_FAILED")


def _candidate_path(folder:Path,filename:str,qa_name:str,plan:dict,part:str)->Path:
    matches=list(folder.rglob(filename))
    metas=list(folder.rglob(qa_name))
    if len(matches)!=1 or len(metas)!=1:
        raise VideoForgeError("RIG_ISOLATE_UNIQUE_HEAD_CANDIDATE_REQUIRED")
    report=json.loads(metas[0].read_text(encoding="utf-8"))
    if (report.get("schema")!="videoforge/rig-three-art-candidate/v1" or
        report.get("part")!=part or
        report.get("source_original_sha256")!=plan["reference_sha256"] or
        report.get("output_sha256")!=sha(matches[0]) or
        report.get("output_png_technical_status")!="candidate_rgba_verified" or
        report.get("human_visual_approval") is not False):
        raise VideoForgeError("RIG_ISOLATE_UNVERIFIED_AI_SEED")
    return matches[0]


def isolate(source:Path,head_folder:Path,closed_folder:Path,
            output:Path,channel:str,video_id:str)->dict:
    enforce_animation_manual()
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise VideoForgeError("RIG_ISOLATE_PREPARATION_REQUIRES_PINNED_OPENCV") from exc
    plan=load_plan(channel,video_id)
    check_source(source,plan)
    origpath=source/"character-main.png"
    if sha(origpath)!=SOURCE_SHA:
        raise VideoForgeError("RIG_ISOLATE_ORIGINAL_SHA_MISMATCH")
    original=_read_rgba(origpath,cv2,np)
    headpath=_candidate_path(head_folder,"head-open-candidate.png",
                              "head-open.qa.json",plan,"head-open")
    candidate=_read_rgba(headpath,cv2,np)
    closed_matches=list(closed_folder.rglob("character-eyes-closed-safe.png"))
    qa_matches=list(closed_folder.rglob("closed-character.qa.json"))
    if len(closed_matches)!=1 or len(qa_matches)!=1:
        raise VideoForgeError("RIG_ISOLATE_BLINK_MISSING")
    clpath=closed_matches[0]
    metadata=json.loads(qa_matches[0].read_text(encoding="utf-8"))
    if (sha(clpath)!=CLOSED_SHA or
        metadata.get("schema")!="videoforge/closed-character-pixel-qa/v1" or
        metadata.get("original_character_sha256")!=SOURCE_SHA or
        metadata.get("safe_full_closed_sha256")!=CLOSED_SHA or
        metadata.get("non_eye_pixels_changed")!=0 or
        metadata.get("alpha_pixels_changed")!=0):
        raise VideoForgeError("RIG_ISOLATE_BLINK_ORIGIN_INVALID")
    closed=_read_rgba(clpath,cv2,np)
    if np.any(closed[:,:,3]!=original[:,:,3]):
        raise VideoForgeError("RIG_ISOLATE_BLINK_ALPHA_NOT_IDENTICAL")

    y,x=np.indices((H,W))
    rows=np.array(ROW_BOUNDS,dtype=np.float64)
    left=np.interp(np.arange(H),rows[:,0],rows[:,1])
    right=np.interp(np.arange(H),rows[:,0],rows[:,2])
    plausible=(y>=905)&(x>=left[y]-15)&(x<=right[y]+15)
    src=original.astype(np.int16)
    r,g,b=src[:,:,0],src[:,:,1],src[:,:,2]
    alpha=original[:,:,3]
    pink=(r>165)&(g>90)&(b>65)&((r-g)>50)&((r-b)>55)&plausible
    face=((x-518)/135)**2+((y-1240)/155)**2<1
    face=face&plausible&(alpha>200)&(y>1115)&(y<1404)
    gc=np.full((H,W),cv2.GC_BGD,dtype=np.uint8)
    gc[plausible]=cv2.GC_PR_BGD
    gc[plausible&(candidate[:,:,3]>80)]=cv2.GC_PR_FGD
    gc[plausible&(alpha<20)]=cv2.GC_BGD
    gc[pink&(candidate[:,:,3]>80)&(alpha>200)]=cv2.GC_FGD
    gc[face&(candidate[:,:,3]>200)]=cv2.GC_FGD
    bgr=cv2.cvtColor(original[:,:,:3],cv2.COLOR_RGB2BGR)
    bg=np.zeros((1,65),np.float64)
    fg=np.zeros((1,65),np.float64)
    cv2.grabCut(bgr,gc,None,bg,fg,7,cv2.GC_INIT_WITH_MASK)
    mask=((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD))&plausible&(alpha>0)
    n,labels,stats,_=cv2.connectedComponentsWithStats(mask.astype(np.uint8),8)
    if n<2:
        raise VideoForgeError("RIG_ISOLATE_NO_CONNECTED_FOREGROUND")
    idx=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]))
    mask=(labels==idx)
    count=int(np.count_nonzero(mask))
    if count<180000 or count>260000 or np.any(mask[:905]):
        raise VideoForgeError("RIG_ISOLATE_SIZE_OUT_OF_SAFE_ENVELOPE")
    ys,xs=np.where(mask)
    bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    if not(190<=bbox[0]<=250 and 900<=bbox[1]<=940
           and 750<=bbox[2]<=825 and bbox[3]>=1490):
        raise VideoForgeError("RIG_ISOLATE_BOUNDING_BOX_UNSAFE")

    # A disjoint partition of the ORIGINAL pixels, not a repaint.
    main=original.copy()
    others=original.copy()
    main[:,:,3]=np.where(mask,original[:,:,3],0).astype(np.uint8)
    others[:,:,3]=np.where(mask,0,original[:,:,3]).astype(np.uint8)
    main_closed=closed.copy()
    main_closed[:,:,3]=main[:,:,3]
    # For source-alpha edges both layers have identical original RGB.
    # Compositing the partition restores the original exactly in straight RGBA.
    partition_error=int(np.count_nonzero((main[:,:,3].astype(np.int16)+
        others[:,:,3].astype(np.int16))!=original[:,:,3]))
    if partition_error:
        raise VideoForgeError("RIG_ISOLATE_NONDISJOINT_PARTITION")
    if np.any(main[:,:,:3]!=original[:,:,:3]) or np.any(
            others[:,:,:3]!=original[:,:,:3]):
        raise VideoForgeError("RIG_ISOLATE_ORIGINAL_COLOR_CHANGED")
    if np.any(main_closed[:,:,:3][~mask] != closed[:,:,:3][~mask]):
        raise VideoForgeError("RIG_ISOLATE_CLOSED_FRAME_OUTSIDE_MASK_CHANGED")

    # Hair-only candidate from visible original pixels. Its corresponding
    # underlay is NOT reconstructed yet, so it CANNOT enable deformable rig.
    hair=(mask&(r>115)&(g>50)&((r-g)>65)&((r-b)>68)&
          (g/np.maximum(r,1)<.75)&(y>915)&(y<1505)).astype(np.uint8)
    hair=cv2.morphologyEx(hair,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    hair=cv2.dilate(hair,np.ones((3,3),np.uint8),iterations=2)
    hair=(hair.astype(bool)&mask)
    nc,l,st,_=cv2.connectedComponentsWithStats(hair.astype(np.uint8),8)
    hair_clean=np.zeros((H,W),dtype=bool)
    for i in range(1,nc):
        if st[i,cv2.CC_STAT_AREA]>180:
            hair_clean|=(l==i)
    hair_count=int(np.count_nonzero(hair_clean))
    if hair_count<100000 or hair_count>190000:
        raise VideoForgeError("RIG_ISOLATE_HAIR_SEED_UNSAFE")
    hair_png=original.copy()
    hair_png[:,:,3]=np.where(hair_clean,original[:,:,3],0).astype(np.uint8)

    # Intersect old AI head mask with REAL Anya only. Keep result
    # labeled *head silhouette candidate*, since hand/neck still need work.
    head=original.copy()
    head[:,:,3]=np.where(mask&(candidate[:,:,3]>20),
                        np.minimum(original[:,:,3],candidate[:,:,3]),0).astype(np.uint8)
    if np.any(head[:,:,3][~mask]):
        raise VideoForgeError("RIG_ISOLATE_FOREIGN_CHARACTERS_INSIDE_HEAD")

    if output.exists():
        raise VideoForgeError("RIG_ISOLATE_OUTPUT_ALREADY_EXISTS")
    output.mkdir(parents=True)
    for name,data in (
        ("anya-original-isolated.png",main),
        ("anya-closed-isolated.png",main_closed),
        ("other-characters-static.png",others),
        ("head-silhouette-draft.png",head),
        ("hair-front-mask-draft.png",hair_png),
    ):
        _write_rgba(output/name,data,cv2,np)
    # Same underlying original image, no duplicate characters.
    checker=np.zeros((H,W,3),np.uint8)
    checker[:]=[33,38,51]
    a=main[:,:,3:4].astype(np.float32)/255.
    composite=(main[:,:,:3]*a +checker*(1-a)).astype(np.uint8)
    if not cv2.imwrite(str(output/"anya-isolation-review.jpg"),
                       cv2.cvtColor(composite,cv2.COLOR_RGB2BGR)):
        raise VideoForgeError("RIG_ISOLATE_PREVIEW_ENCODE_FAILED")
    result={
       "schema":"videoforge/rig-three-character-isolation-qa/v1",
       "channel":channel,"video_id":video_id,"scene":"cena-01",
       "manual":"docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md",
       "original_sha256":SOURCE_SHA,
       "approved_blink_source_sha256":CLOSED_SHA,
       "original_visible_anyas_pixels":count,
       "bbox_original_canvas":bbox,
       "original_partition_alpha_differences":partition_error,
       "hair_candidate_pixels":hair_count,
       "source_pixels_repainted":0,
       "all_parts_reference_same_original":True,
       "full_character_blink_preserved":True,
       "foreign_characters_in_anya_layer":"excluded_by_connected_mask_and_roi_candidate",
       "head_status":"draft_requires_hand_and_neck_reconstruction",
       "hair_status":"mask_candidate_requires_underlay_roundtrip_and_hair_line_QA",
       "whole_character_isolation_status":"technical_candidate_only",
       "human_visual_approval":False,
       "rig_operational":False,
       "video_official":False,
       "youtube_uploaded":False,
       "files":{p.name:sha(p) for p in output.glob("*.png")},
    }
    (output/"qa.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RIG_THREE_ANYA_ISOLATION_CANDIDATE_QA",
          json.dumps(result,ensure_ascii=False))
    return result


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    ap.add_argument("--head",required=True,type=Path)
    ap.add_argument("--closed",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--channel",default="otaku-br")
    ap.add_argument("--video-id",default="spy-x-family-familia-de-mentira")
    a=ap.parse_args()
    try:
        isolate(a.source,a.head,a.closed,a.output,a.channel,a.video_id)
        return 0
    except (VideoForgeError,ValueError,OSError,KeyError) as exc:
        print("RIG_THREE_ANYA_ISOLATION_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
