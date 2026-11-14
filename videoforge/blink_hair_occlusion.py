"""Remove overpaint from a generated blink while restoring hair in front.

Works on TWO real RGBA images of the same scene: whole-character layer and
previously generated eyelid layer. No generative AI or new characters.
Alpha is restricted to approved eye ellipses, clipped under the ORIGINAL hair
pixels, and hair-foreground is derived ONLY from original character pixels.
The output is a draft pending human facial/occlusion review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from . import scene_layers
from .errors import VideoForgeError

WIDTH, HEIGHT = 1024, 1536
# Camera-local coordinates tied to the source image, NOT universal anatomy.
# Ellipses are made to include ONLY the eyes of the large Anya in scene 01.
SCENE_01_EYES = (
    (421.0,1230.0,80.0,52.0),
    (611.0,1230.0,88.0,52.0),
)
HAIR_BOUNDS = (280,1020,740,1245)


def _ffmpeg_rgba(path:Path)->bytearray:
    if not path.is_file() or path.is_symlink():
        raise VideoForgeError("BLINK_MATTE_SOURCE_MISSING")
    info=scene_layers.png_info(path.read_bytes(),require_alpha=True)
    if (info["width"],info["height"])!=(WIDTH,HEIGHT):
        raise VideoForgeError("BLINK_MATTE_DIMENSIONS_INVALID")
    try:
        p=subprocess.run(
            ["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
             "-i",str(path),"-frames:v","1","-pix_fmt","rgba",
             "-f","rawvideo","-"],
            capture_output=True,timeout=90,check=False,
        )
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("BLINK_MATTE_FFMPEG_NOT_AVAILABLE") from exc
    if p.returncode!=0 or len(p.stdout)!=WIDTH*HEIGHT*4:
        raise VideoForgeError("BLINK_MATTE_DECODE_FAILED")
    return bytearray(p.stdout)


def _write_rgba(path:Path,data:bytearray)->None:
    if path.exists() or path.is_symlink():
        raise VideoForgeError("BLINK_MATTE_WOULD_OVERWRITE")
    if len(data)!=WIDTH*HEIGHT*4:
        raise VideoForgeError("BLINK_MATTE_BUFFER_INVALID")
    try:
        p=subprocess.run(
            ["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
             "-f","rawvideo","-pixel_format","rgba",
             "-video_size",f"{WIDTH}x{HEIGHT}","-framerate","1",
             "-i","-","-frames:v","1","-compression_level","6",str(path)],
            input=bytes(data),capture_output=True,timeout=90,check=False,
        )
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("BLINK_MATTE_ENCODER_NOT_AVAILABLE") from exc
    if p.returncode!=0:
        raise VideoForgeError("BLINK_MATTE_ENCODER_FAILED")
    info=scene_layers.png_info(path.read_bytes(),require_alpha=True)
    if (info["width"],info["height"])!=(WIDTH,HEIGHT):
        raise VideoForgeError("BLINK_MATTE_OUTPUT_DIMENSIONS_INVALID")


def eye_weight(x:int,y:int,eyes:tuple=SCENE_01_EYES)->float:
    """Feathered eye-only matte; zero outside both safe eye regions."""
    result=0.0
    for cx,cy,rx,ry in eyes:
        r=math.hypot((x-cx)/rx,(y-cy)/ry)
        # ~6px soft edge; no rectangle that can cover forehead or hair.
        t=max(0.0,min(1.0,(1.0-r)/.105))
        w=t*t*(3-2*t)
        result=max(result,w)
    return result


def _hair_color(r:int,g:int,b:int,a:int)->bool:
    """Pink hair seed on the ORIGINAL character, not the generated eyelid."""
    return a>=210 and r>=175 and g>=90 and b>=70 and (r-g)>=69 and (r-b)>=68


def _dilate(points:set[int],radius:int=4)->set[int]:
    """Protect ink outlines near hair strands, no external image library."""
    kept=set(points)
    for _ in range(radius):
        extra=set()
        for pos in kept:
            y,x=divmod(pos,WIDTH)
            if x>0:extra.add(pos-1)
            if x<WIDTH-1:extra.add(pos+1)
            if y>0:extra.add(pos-WIDTH)
            if y<HEIGHT-1:extra.add(pos+WIDTH)
        kept|=extra
    return kept


def mask_pixels(original:bytearray, eyelids:bytearray,
                eyes:tuple=SCENE_01_EYES,
                hair_bounds:tuple=HAIR_BOUNDS)->tuple[bytearray,bytearray,dict]:
    if len(original)!=WIDTH*HEIGHT*4 or len(eyelids)!=len(original):
        raise VideoForgeError("BLINK_MATTE_INPUT_SIZE_INVALID")
    left,top,right,bottom=hair_bounds
    if not (0<=left<right<=WIDTH and 0<=top<bottom<=HEIGHT):
        raise VideoForgeError("BLINK_HAIR_BOUNDS_INVALID")
    hair=set()
    for y in range(top,bottom):
        for x in range(left,right):
            k=(y*WIDTH+x)*4
            if _hair_color(*original[k:k+4]):
                hair.add(y*WIDTH+x)
    hair=_dilate(hair,4)
    safe=bytearray(eyelids)
    foreground=bytearray(len(original))
    full_before=0
    visible=0
    hair_blocked=0
    outside=0
    # Only read/modify within EYE ellipses. All other eyelid pixels removed.
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pos=y*WIDTH+x
            i=pos*4
            raw_a=eyelids[i+3]
            if raw_a>=40:full_before+=1
            w=eye_weight(x,y,eyes)
            if w<=0:
                safe[i+3]=0
            elif pos in hair:
                if raw_a>0:hair_blocked+=1
                safe[i+3]=0
            else:
                safe[i+3]=round(raw_a*w)
                if safe[i+3]>=40:
                    visible+=1
                    if w<=0:outside+=1
            # Foreground uses ONLY original hair pixels/ink, not generated art.
            if pos in hair and original[i+3]>=210:
                foreground[i:i+4]=original[i:i+4]
    # Force no orphan alpha outside face, fail if too few eyelid pixels.
    if visible<1000 or visible>50000 or outside:
        raise VideoForgeError("BLINK_EYELID_MATTE_UNSAFE")
    if full_before<visible:
        raise VideoForgeError("BLINK_MATTE_INVALID_SOURCE")
    metrics={"raw_alpha_pixels":full_before,"safe_alpha_pixels":visible,
             "hair_pixels_protected":len(hair),
             "raw_pixels_blocked_on_hair":hair_blocked,
             "pixels_outside_safe_eyes":outside,
             "source":"original_character_rgba_and_generated_eyes",
             "eyes":eyes,"hair_bounds":hair_bounds,
             "face_base_opacity_untouched":True}
    return safe,foreground,metrics


def build(source:Path,eyes:Path,output:Path,hair:Path,qa:Path,
          scene_source_sha256:str)->dict:
    if not isinstance(scene_source_sha256,str) or len(scene_source_sha256)!=64:
        raise VideoForgeError("BLINK_MATTE_SOURCE_SHA_INVALID")
    for target in (output,hair,qa):
        if target.exists() or target.is_symlink():
            raise VideoForgeError("BLINK_MATTE_WOULD_OVERWRITE")
    raw_source=_ffmpeg_rgba(source)
    raw_eyes=_ffmpeg_rgba(eyes)
    cut,front,metric=mask_pixels(raw_source,raw_eyes)
    _write_rgba(output,cut)
    _write_rgba(hair,front)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result={
        "schema":"videoforge/blink-hair-occlusion/v1",
        "scene_mother_sha256":scene_source_sha256,
        "character_original_sha256":digest(source),
        "raw_eyes_sha256":digest(eyes),
        "safe_eyes_sha256":digest(output),
        "hair_foreground_sha256":digest(hair),
        "occlusion_qa":"eye_matte_excludes_original_hair",
        "visual_approval":False,
        "rig_individual_head_hair":False,
        "youtube_uploaded":False,
        **metric,
    }
    qa.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BLINK_HAIR_OCCLUSION_QA_OK",
          json.dumps({k:v for k,v in result.items() if k not in ("eyes",)},ensure_ascii=False))
    return result


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--character",required=True,type=Path)
    p.add_argument("--eyes",required=True,type=Path)
    p.add_argument("--safe-eyes",required=True,type=Path)
    p.add_argument("--hair-foreground",required=True,type=Path)
    p.add_argument("--qa",required=True,type=Path)
    p.add_argument("--scene-mother-sha256",required=True)
    a=p.parse_args()
    try:
        build(a.character,a.eyes,a.safe_eyes,a.hair_foreground,a.qa,
              a.scene_mother_sha256)
        return 0
    except (VideoForgeError,ValueError,OSError) as exc:
        print("BLINK_HAIR_OCCLUSION_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
