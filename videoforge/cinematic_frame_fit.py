"""Pixel-safe 9:16 Remotion cover framing for each native shot source.

No resampling or editing in this validator. Keeps focal eyes/object visible
and rejects accidental face crops from forcing legacy 2:3 to 9:16.
"""
from __future__ import annotations

from .errors import VideoForgeError

OUT=(1080,1920)

def cover_viewport(source:tuple[int,int],out:tuple[int,int]=OUT)->dict:
    if (len(source)!=2 or len(out)!=2
            or any(type(k) is not int or k<1 for k in (*source,*out))):
        raise VideoForgeError("CINEMATIC_FIT_DIMENSIONS_INVALID")
    w,h=source
    ow,oh=out
    scale=max(ow/w,oh/h)
    visible_w=ow/scale
    visible_h=oh/scale
    left=(w-visible_w)/2
    top=(h-visible_h)/2
    return {
        "scale":scale,
        "visibleSourceRect":[left,top,left+visible_w,top+visible_h],
        "cropLeftPx":left,
        "cropRightPx":w-(left+visible_w),
        "cropTopPx":top,
        "cropBottomPx":h-(top+visible_h),
        "destination":[ow,oh],
        "nativeSource":[w,h],
        "nonUniformStretch":False,
    }

def validate_focal_box(source:tuple[int,int],bbox:object,
                       margin_source_px:float=2)->dict:
    """Requires whole manually marked focal point (eyes/object) visible.

    A close can deliberately crop hair or shoulder. Human QA supplies
    *focal* bbox, not a wide full-body bbox; this guards a visible expression.
    """
    f=cover_viewport(source)
    if (not isinstance(bbox,list) or len(bbox)!=4
            or any(type(x) is not int for x in bbox)
            or bbox[2]<1 or bbox[3]<1
            or bbox[0]<0 or bbox[1]<0
            or bbox[0]+bbox[2]>source[0]
            or bbox[1]+bbox[3]>source[1]):
        raise VideoForgeError("CINEMATIC_FOCAL_BOX_INVALID")
    l,t,r,b=f["visibleSourceRect"]
    x,y,w,h=bbox
    if not (x>=l+margin_source_px and y>=t+margin_source_px and
            x+w<=r-margin_source_px and
            y+h<=b-margin_source_px):
        raise VideoForgeError("CINEMATIC_FOCAL_POINT_CLIPPED_BY_9_16_CROP")
    return {
        "focalBbox":bbox,
        "focalVisibleAfter9x16Cover":True,
        "nativeCanvas":f["nativeSource"],
        "visibleSourceRect":f["visibleSourceRect"],
        "nonUniformStretch":False,
    }
