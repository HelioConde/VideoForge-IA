"""Offline-only C01-P04 anatomical grip test with correct alpha overlap order.

Provisional, reversible sprite transforms shown in QA JPEGs only.
NO animation asset, no mask/cutout from creator-approved mother, no rig.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
import sys
from PIL import Image, ImageOps, ImageDraw, ImageFont
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge.ep01_approved_v3_parts import aligned_source
from videoforge import ep01_c01p04_grip_v3 as grip
from scripts.qa_ep01_c01p04_grip_v3 import review
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_spear_registration import (
    spear_endpoints, draw_spear_preview)

BASENAME="QA-C01-P04-V3-PEGADA-CONTATO"
# Editorial ROIs: approximate from the approved mother, NOT approved geometry.
TARGETS={
  "forearm-cuff":[67,780,218,965],
  "palm-rear":[143,920,235,1024],
  "fingers-front":[149,930,241,1018],
}
SCENE=(941,1672)

def f(sz):
    try:return ImageFont.truetype("DejaVuSans.ttf",sz)
    except OSError:return ImageFont.load_default()

def registered(role,variant_x=0):
    evidence=review(role)
    if evidence is None:
        raise RuntimeError("GRIP_V3_CONTACT_PART_MISSING "+role)
    src=evidence["image"]
    p=evidence["proof"]
    box=p["alpha_bbox_xyxy"]
    if not box:
        raise RuntimeError("GRIP_V3_CONTACT_ALPHA_EMPTY "+role)
    target=TARGETS[role]
    bw=box[2]-box[0];bh=box[3]-box[1]
    sw=target[2]-target[0];sh=target[3]-target[1]
    if min(bw,bh,sw,sh)<=0:
        raise RuntimeError("GRIP_V3_CONTACT_BAD_BOUNDS")
    scale=min(sw/bw,sh/bh)
    w=max(1,round(src.width*scale));h=max(1,round(src.height*scale))
    if w>1200 or h>1500:
        raise RuntimeError("GRIP_V3_CONTACT_UNSAFE_PREVIEW_RESIZE")
    pic=src.resize((w,h),Image.Resampling.LANCZOS)
    middle_x=(target[0]+target[2])/2
    x=round(middle_x-(box[0]+box[2])/2*scale)
    y=round(target[3]-box[3]*scale)
    if role=="fingers-front":
        x+=variant_x
    return pic,(x,y),{
        "role":role,"source_sha256":evidence["source"]["sha256"],
        "native_canvas":[src.width,src.height],
        "native_alpha_bbox":box,
        "target_roi_provisional_xyxy":target,
        "uniform_scale_for_preview":round(scale,7),
        "offset_xy":[x,y],
        "approved":False,"preview_only":True
    }

def panel(image,label,w=330,h=525):
    tile=Image.new("RGB",(w,h),"#ffffff")
    d=ImageDraw.Draw(tile)
    d.text((9,8),label,font=f(14),fill="#222222")
    shot=ImageOps.contain(image.convert("RGB"),(w-18,h-43),Image.Resampling.LANCZOS)
    tile.paste(shot,((w-shot.width)//2,36))
    return tile

def create():
    base=ROOT/REL
    mother=aligned_source()
    if mother["sha256"]!=grip.ALIGNED_SHA:
        raise RuntimeError("GRIP_V3_CONTACT_SOURCE_CHANGED")
    with Image.open(BytesIO(mother["blob"])) as im:
        mother_rgb=im.convert("RGB")
    # Complete set must be archived with exact SHA first.
    independent={role:registered(role,0) for role in grip.ROLES}
    spear,spear_rec=verified_art("object-lanca-esquerda")
    points=spear_endpoints(spear)
    shaft,shaft_map=draw_spear_preview(spear,points,[65,1130],[525,430])
    paper=Image.new("RGB",(4*342+20,638),"#ebeae6")
    draw=ImageDraw.Draw(paper)
    draw.text((15,9),"EP01 C01-P04 V3 | PEGADA: PALMA -> LANCA -> DEDOS",font=f(23),fill="#1e1e1e")
    draw.text((15,40),"SOMENTE PREVIA DE QA. Escala/pegada ainda nao aprovadas; PNGs originais imutaveis.",
              font=f(13),fill="#a82d22")
    src_crop=mother_rgb.crop((0,750,375,1240))
    paper.paste(panel(src_crop,"MAE APROVADA - PEGADA"),(8,80))
    candidates=[]
    for i,shift in enumerate((-8,0,8),1):
        canvas=Image.new("RGBA",SCENE,(0,0,0,0))
        contacts={}
        for role in ("forearm-cuff","palm-rear"):
            pic,pos,proof=independent[role]
            canvas.alpha_composite(pic,pos)
            contacts[role]=proof
        canvas.alpha_composite(shaft)
        pic,pos,proof=registered("fingers-front",shift)
        canvas.alpha_composite(pic,pos)
        contacts["fingers-front"]=proof
        # Contact crop used exclusively for QA; never an exported rig part.
        crop=canvas.crop((0,750,375,1240))
        # checker background reveals mistaken alpha holes; original PNG remains unchanged
        check=Image.new("RGBA",crop.size,(235,235,235,255))
        d=ImageDraw.Draw(check)
        for y in range(0,check.height,24):
            for x in range(0,check.width,24):
                if (x//24+y//24)%2==0:
                    d.rectangle((x,y,x+23,y+23),fill=(215,215,215,255))
        check.alpha_composite(crop)
        paper.paste(panel(check.convert("RGB"),f"CONTATO {i} / dedos shift {shift:+d}px"),(8+i*342,80))
        candidates.append({"id":f"contact-{i}","front_finger_shift_px":shift,
                           "source_parts":contacts,"spear_sha256":spear_rec["sha256"],
                           "spear_transform":shaft_map,
                           "visual_approved":False})
    dest=base/(BASENAME+".jpg")
    paper.save(dest,"JPEG",quality=88,optimize=True)
    report={
        "schema":"videoforge/ep01-c01p04-v3-grip-contact-review/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "mother_approved_original_sha256":grip.APPROVED_SHA,
        "technical_mother_reference_sha256":grip.ALIGNED_SHA,
        "rendering_for_review_only":True,
        "geometry_is_editorial_not_verified":True,
        "compositing_layer_order":[
            "forearm-cuff","palm-rear","spear-independent","fingers-front"],
        "candidates":candidates,
        "board":dest.name,"board_sha256":sha256(dest.read_bytes()).hexdigest(),
        "anatomical_contact_verified":False,
        "spatial_registration_approved":False,
        "human_visual_approval":False,
        "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False,
        "proxy_model_calls":0,
        "next":"inspect gaps, shaft position between digits, hand direction and arm seam against approved mother; if wrong regenerate only failing art, never approve transformations from previews",
    }
    (base/(BASENAME+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GRIP_V3_CONTACT_QA",json.dumps({
        "candidate_count":len(candidates),
        "parts":[p for p in grip.ROLES],
        "spear_sha256":spear_rec["sha256"],"rig_ready":False,"new_calls":0}))
    return report

if __name__=="__main__":
    try:create()
    except (OSError,ValueError,RuntimeError) as e:
        print("GRIP_V3_CONTACT_QA_STOP",str(e),file=sys.stderr)
        sys.exit(2)
