"""Verify actual ThreeCanvas motion of Anya's BLACK/GOLD ornaments.

Requires movement of GOLD pixels, not merely a difference in a nearby
moving hair region. Uses raw 125x180 RGB crops emitted by FFmpeg, with no
OpenCV/Pillow/AI inference on the rendering runner. Never approves art.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from .errors import VideoForgeError

WIDTH=125
HEIGHT=180
SIZE=WIDTH*HEIGHT*3
REQUIRED={
    "body-no-head","head-open","head-closed",
    "hair-front-left","hair-front-right","hand",
    "ornament-left","ornament-right"
}


def _sha(f:Path)->str:
    if f.is_symlink() or not f.is_file():
        raise VideoForgeError("ANYA_ORNAMENT_RENDER_ASSET_INVALID")
    return hashlib.sha256(f.read_bytes()).hexdigest()


def gold_centroid(path:Path):
    rgb=path.read_bytes()
    if path.is_symlink() or len(rgb)!=SIZE:
        raise VideoForgeError("ANYA_ORNAMENT_GOLD_CROP_INVALID")
    sx=sy=n=0
    for i in range(0,len(rgb),3):
        r,g,b=rgb[i],rgb[i+1],rgb[i+2]
        if r>170 and g>95 and b<155 and r-g>20 and g-b>10:
            cell=i//3
            sx+=cell%WIDTH
            sy+=cell//WIDTH
            n+=1
    if n<1000:
        raise VideoForgeError("ANYA_ORNAMENT_GOLD_NOT_VISIBLE")
    return sx/n,sy/n,n



def stable_gold_motion(folder:Path,side:str)->dict:
    width,height=24,36
    nbytes=width*height*3
    paths=[folder/("ornament-"+side+"-stable-"+str(frame)+".rgb")
           for frame in (0,30)]
    rgb=[p.read_bytes() for p in paths]
    if any(p.is_symlink() or len(data)!=nbytes
           for p,data in zip(paths,rgb)):
        raise VideoForgeError("ANYA_ORNAMENT_STABLE_GOLD_RGB_INVALID")
    original_visible_gold=0
    changed=0
    for offset in range(0,nbytes,3):
        r,g,b=rgb[0][offset:offset+3]
        if r>170 and g>95 and b<155 and r-g>20 and g-b>10:
            original_visible_gold+=1
        if rgb[0][offset:offset+3]!=rgb[1][offset:offset+3]:
            changed+=1
    # A deliberately stable interior source patch distinguishes actual
    # ornament movement from a static horn merely occluded by moving hair.
    # Baseline old render: left 0/864, right 57/864 changed pixels.
    # Actual head-attached render: >800/864 on both source gold patches.
    if original_visible_gold<250 or changed<600:
        raise VideoForgeError("ANYA_ORNAMENT_STILL_STATIC_"+side+
                              "_"+str(changed)+"_gold"+str(original_visible_gold))
    return {
        "interior_ornament_source_gold_pixels":original_visible_gold,
        "interior_source_patch_pixels_changed":changed,
        "interior_source_patch_pixels_total":width*height,
        "previous_static_baseline_changed_pixels":{
            "left":0,"right":57
        }[side],
        "ornament_not_static":True,
    }

def verify(folder:Path)->dict:
    stage=json.loads((folder/"stage.qa.json").read_text(encoding="utf8"))
    props=json.loads((folder/"props.json").read_text(encoding="utf8"))
    ffprobe=json.loads((folder/"ffprobe.json").read_text(encoding="utf8"))
    rig=props["rig"]
    layers={x["id"]:x for x in rig["layers"]}
    if (stage.get("rig_sprites_count")!=8 or
        stage.get("ornament_head_parented") is not True or
        stage.get("ornament_pixels_reparented",0)<9500 or
        stage.get("human_visual_approval") is not False or
        stage.get("official_rig_validator")!="blocked_as_designed" or
        props.get("reviewOnly") is not True or
        props.get("youtubeUpload") is not False or
        rig.get("provisional") is not True or
        set(layers)!=REQUIRED or
        rig.get("channel")!="otaku-br" or
        any(rig.get("humanReview",{}).values()) or
        not all(layers[x].get("mesh") is None for x in
                ("ornament-left","ornament-right")) or
        not all(layers[x]["z"]<layers["head-open"]["z"] for x in
                ("ornament-left","ornament-right"))):
        raise VideoForgeError("ANYA_ORNAMENT_RIG_REVIEW_GATE_FAILED")
    motions={}
    for side in ("left","right"):
        patch=stable_gold_motion(folder,side)
        x0,y0,n0=gold_centroid(folder/("ornament-"+side+"-0.rgb"))
        x1,y1,n1=gold_centroid(folder/("ornament-"+side+"-30.rgb"))
        distance=math.hypot(x1-x0,y1-y0)
        motions[side]={
            **patch,
            "frame0_source_gold_pixels":n0,
            "frame30_source_gold_pixels":n1,
            "gold_centroid_shift_screen_px_diagnostic_only":round(distance,4),
            "centroid_note":"Not a pass criterion: moving hair occlusion biases this value",
            "moved_with_head_at_frame30":True,
        }
    video=folder/"anya-ornaments-head-fixed-6s.mp4"
    info=ffprobe.get("streams",[])
    stream=next((x for x in info if x.get("codec_name")=="h264"),None)
    if (stream is None or
        stream.get("pix_fmt")!="yuv420p" or
        [stream.get("width"),stream.get("height")]!=[1080,1920] or
        stream.get("r_frame_rate")!="30/1" or
        not 5.95<=float(ffprobe["format"]["duration"])<=6.15 or
        video.is_symlink() or not video.is_file() or
        video.stat().st_size<30000):
        raise VideoForgeError("ANYA_ORNAMENT_MP4_QA_FAILED")
    result={
        **stage,
        "schema":"videoforge/anya-black-gold-ornament-threecanvas-review-qa/v1",
        "rigid_ornaments_follow_neck_pivot":True,
        "rigid_ornaments_behind_pink_head":True,
        "source_gold_pixels_motion_checked":motions,
        "frames":[0,30,74,76,173,175],
        "frame0_sha256":_sha(folder/"frame-0.png"),
        "frame30_sha256":_sha(folder/"frame-30.png"),
        "frame74_sha256":_sha(folder/"frame-74.png"),
        "frame76_sha256":_sha(folder/"frame-76.png"),
        "mp4_sha256":_sha(video),
        "mp4_file":video.name,
        "renderer":"Remotion ThreeCanvas SWANGLE",
        "new_image_calls":0,
        "human_visual_approval":False,
        "rig_operational":False,
        "video_official":False,
        "youtube_uploaded":False,
    }
    if result["frame74_sha256"]==result["frame76_sha256"]:
        raise VideoForgeError("ANYA_ORNAMENT_BLINK_FAILED")
    (folder/"ornaments.render.qa.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ANYA_ORNAMENT_REAL_THREECANVAS_QA",json.dumps(result,
                                                     ensure_ascii=False))
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--folder",type=Path,required=True)
    a=ap.parse_args()
    try:
        verify(a.folder)
        return 0
    except (VideoForgeError,ValueError,KeyError,OSError,TypeError) as exc:
        print("ANYA_ORNAMENT_REAL_RENDER_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
