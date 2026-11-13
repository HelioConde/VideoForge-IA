"""Natural, antialiased closed eyelids from the *same* scene's original pixels.

No model calls, PIL/OpenCV, extra system packages, timers or randomness.
Works on verified full-canvas RGBA. The generated portrait from the design
review is a reference for the eyelid shape, NOT an image to paste into the
character, because its perspective, texture and coordinates differ.

Two independent elements:
  * head-no-eyes: heal actual iris/lashes with intact nearby cheek pixels
    (spatial texture transfer, with feathered edges; still draft artwork).
  * eyes-closed: transparent 4x-subsample-quality cubic eyelid strokes.
This removes the old solid cream rectangle and 5-px jagged lines.
"""
from __future__ import annotations

import math

class EyeRefineError(ValueError):
    pass


def _point(value: object, width: int, height: int) -> tuple[float,float]:
    if not (isinstance(value, list) and len(value)==2 and
            all(type(n) in (int,float) and math.isfinite(n) for n in value)):
        raise EyeRefineError("EYE_BEZIER_POINT_INVALID")
    x,y=float(value[0]),float(value[1])
    if not (0 <= x < width and 0 <= y < height):
        raise EyeRefineError("EYE_BEZIER_OUTSIDE_CANVAS")
    return x,y


def _validate_curves(plan: object, count: int, width: int, height: int) -> list[dict]:
    if not isinstance(plan,list) or len(plan)!=count or not 1<=count<=2:
        raise EyeRefineError("EYE_BEZIER_COUNT_MISMATCH")
    out=[]
    for curve in plan:
        if not isinstance(curve,dict):
            raise EyeRefineError("EYE_BEZIER_INVALID")
        p=curve.get("points")
        if not isinstance(p,list) or len(p)!=4:
            raise EyeRefineError("EYE_BEZIER_NEEDS_FOUR_POINTS")
        pts=[_point(v,width,height) for v in p]
        if math.dist(pts[0],pts[-1]) < 6 or math.dist(pts[0],pts[-1]) > 140:
            raise EyeRefineError("EYE_BEZIER_LENGTH_INVALID")
        radius=curve.get("width",1.4)
        if type(radius) not in (int,float) or not .6<=radius<=2.5:
            raise EyeRefineError("EYE_BEZIER_WIDTH_INVALID")
        rgb=curve.get("color",[72,35,31])
        if not isinstance(rgb,list) or len(rgb)!=3 or any(type(v) is not int or not 0<=v<=255 for v in rgb):
            raise EyeRefineError("EYE_BEZIER_COLOR_INVALID")
        out.append({"points":pts,"width":float(radius),"color":rgb})
    return out


def _sample(src: bytearray, x: float, y: float, width: int, height: int) -> tuple[int,int,int]:
    """Bilinear sample within the RGBA character artwork, never use sky pixels."""
    x=max(0.0,min(width-2.0,x))
    y=max(0.0,min(height-2.0,y))
    x0,y0=int(x),int(y)
    fx,fy=x-x0,y-y0
    vals=[]
    for chan in range(3):
        p00=src[4*(y0*width+x0)+chan]
        p10=src[4*(y0*width+x0+1)+chan]
        p01=src[4*((y0+1)*width+x0)+chan]
        p11=src[4*((y0+1)*width+x0+1)+chan]
        vals.append(round((p00*(1-fx)+p10*fx)*(1-fy)+
                          (p01*(1-fx)+p11*fx)*fy))
    return tuple(vals)


def _skin_pixel(src: bytearray, *, x: int, y: int, center_x: float,
                center_y: float, sample_x: int, sample_y: int,
                width: int, height: int) -> tuple[int,int,int]:
    """Sample a genuine cheek texture strip, not one uniform skin swatch."""
    sx=sample_x+(x-center_x)*.63
    sy=sample_y+(y-center_y)*.18+(x-center_x)*.035
    # Only permit a local skin strip, excluding hair and background.
    sx=max(sample_x-18,min(sample_x+12,sx))
    sy=max(sample_y-8,min(sample_y+11,sy))
    pos=4*(int(sy)*width+int(sx))
    if src[pos+3]<235:
        sx,sy=sample_x,sample_y
    return _sample(src,sx,sy,width,height)


def _heal_region(head: bytearray, source: bytearray, mask: bytearray,
                 skin: tuple[int,int], width: int, height: int) -> int:
    if len(head)!=width*height*4 or len(source)!=len(head) or len(mask)!=width*height:
        raise EyeRefineError("EYE_RGBA_SIZE_INVALID")
    xs,ys=[],[]
    # Bounding box of one eye. No image-wide convolution.
    for i,a in enumerate(mask):
        if a:
            xs.append(i%width);ys.append(i//width)
    if len(xs)<10 or len(xs)>width*height*.10:
        raise EyeRefineError("EYE_MASK_EMPTY_OR_TOO_LARGE")
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    cx,cy=(minx+maxx)/2,(miny+maxy)/2
    sx,sy=skin
    anchor=4*(sy*width+sx)
    if source[anchor+3]<245:
        raise EyeRefineError("EYE_SKIN_SAMPLE_NOT_IN_CHARACTER")
    # Dilate only 2 px beyond the eye mask to remove dark eyelash fragments.
    feather=2.5
    count=0
    for y in range(max(0,miny-4),min(height,maxy+5)):
        for x in range(max(0,minx-4),min(width,maxx+5)):
            i=y*width+x
            if mask[i]:
                blend=1.0
            else:
                found=100
                for oy in range(-3,4):
                    yy=y+oy
                    if yy<miny or yy>maxy:continue
                    for ox in range(-3,4):
                        xx=x+ox
                        if xx<minx or xx>maxx:continue
                        if mask[yy*width+xx]:
                            dist=math.hypot(ox,oy)
                            if dist<found:found=dist
                blend=max(0.,1.-found/feather)
            if not blend:
                continue
            i4=i*4
            if not head[i4+3]:
                continue
            color=_skin_pixel(source,x=x,y=y,center_x=cx,center_y=cy,
                              sample_x=sx,sample_y=sy,width=width,height=height)
            for c in range(3):
                head[i4+c]=round(head[i4+c]*(1-blend)+color[c]*blend)
            count+=1
    return count


def _bezier(pts:list[tuple[float,float]], t:float) -> tuple[float,float]:
    q=1-t
    return (q*q*q*pts[0][0]+3*q*q*t*pts[1][0]+3*q*t*t*pts[2][0]+t*t*t*pts[3][0],
            q*q*q*pts[0][1]+3*q*q*t*pts[1][1]+3*q*t*t*pts[2][1]+t*t*t*pts[3][1])


def _stroke(dst: bytearray, width:int, height:int,
            pts:list[tuple[float,float]], stroke_width:float,
            color:list[int], opacity:float, *, shadow:bool=False) -> int:
    """Pixel coverage via 0.25px Bézier steps + tapered radius, no aliasing."""
    length=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
    count=max(32,math.ceil(length*4))
    cover:dict[int,float]={}
    for step in range(count+1):
        t=step/count
        x,y=_bezier(pts,t)
        if shadow:
            y+=1.75
        # Cusp-free, delicate ends. The main line is 1–2px, not blocky.
        taper=.26+.74*math.sin(math.pi*t)**.65
        radius=stroke_width*taper*(1.7 if shadow else 1.)
        left,right=math.floor(x-radius-1),math.ceil(x+radius+1)
        top,bottom=math.floor(y-radius-1),math.ceil(y+radius+1)
        for yy in range(max(0,top),min(height,bottom+1)):
            for xx in range(max(0,left),min(width,right+1)):
                d=math.hypot(xx+.5-x,yy+.5-y)
                a=max(0.,min(1.,radius+.54-d))*opacity
                i=yy*width+xx
                if a>cover.get(i,0.):
                    cover[i]=a
    for i,alpha in cover.items():
        if alpha<=0:continue
        p=4*i
        old=dst[p+3]/255.
        oa=alpha+old*(1-alpha)
        if oa<=0:continue
        for c in range(3):
            dst[p+c]=round((color[c]*alpha+dst[p+c]*old*(1-alpha))/oa)
        dst[p+3]=min(255,round(oa*255))
    return len(cover)


def create_natural_blink(head:bytearray, source:bytearray,
                         eyes:list[bytearray], samples:list[tuple[int,int]],
                         curves:object, width:int, height:int
                         ) -> tuple[bytearray,dict]:
    """Heal eyelid skin and generate a transparent RGBA closed-lid overlay."""
    if len(eyes)!=len(samples):
        raise EyeRefineError("EYE_SAMPLE_COUNT_MISMATCH")
    specs=_validate_curves(curves,len(eyes),width,height)
    closed=bytearray(width*height*4)
    healed=0
    coverage=0
    for mask,skin,curve in zip(eyes,samples,specs):
        healed+=_heal_region(head,source,mask,skin,width,height)
        # Very subtle skin crease/shadow; matches warm anime sunset lighting.
        coverage+=_stroke(closed,width,height,curve["points"],
                          curve["width"]*1.5,[128,67,54],.16,shadow=True)
        coverage+=_stroke(closed,width,height,curve["points"],
                          curve["width"],curve["color"],.94)
    visible=sum(1 for i in range(3,len(closed),4) if closed[i]>0)
    if visible<12 or visible>min(width*height*.08, sum(math.dist(c['points'][0],c['points'][-1])*15 for c in specs)):
        raise EyeRefineError("EYE_CLOSED_PIXEL_COVERAGE_INVALID")
    return closed,{
        "technique":"original-cheek-texture-transfer + antialiased tapered cubic eyelid",
        "human_review":"pending",
        "eyes":len(eyes),
        "healed_pixels":healed,
        "closed_lid_visible_pixels":visible,
        "draw_coverage":coverage,
        "external_model_calls":0,
    }
