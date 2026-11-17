"""Numerical QA: quantify alpha contact in anatomical grip previews.

This checks 2D overlap in a reference ROI, NOT whether fingers truly grasp a
shaft in 3D. No actual sprite edits and no final transforms are saved.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys
from PIL import Image, ImageChops
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge import ep01_c01p04_right_grip_v1 as grip
from scripts.qa_ep01_c01p04_right_grip_v1_contact import registered,SCENE
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_spear_registration import spear_endpoints,draw_spear_preview

NAME="QA-C01-P04-V3-GUARDA-DIREITO-CONTATO-METRICAS"
CONTACT_ROI=(650,850,855,1120)
VARIANTS=[
 {"id":"R1-close-wrist","forearm-cuff":(-20,30),
  "palm-rear":(12,0),"fingers-front":(12,0)},
 {"id":"R2-shaft-through-fingers","forearm-cuff":(-35,40),
  "palm-rear":(22,0),"fingers-front":(25,0)},
 {"id":"R3-tightest-provisional","forearm-cuff":(-45,52),
  "palm-rear":(32,6),"fingers-front":(35,6)},
]

def scene_mask(img:Image.Image,offset:tuple[int,int]):
    layer=Image.new("L",SCENE,0)
    layer.paste(img.getchannel("A"),offset)
    return layer.crop(CONTACT_ROI).point(lambda v:255 if v>=128 else 0)

def intersection_count(a:Image.Image,b:Image.Image)->int:
    if a.mode!="L" or b.mode!="L" or a.size!=b.size:
        raise ValueError("GRIP_QA_METRIC_SHAPE")
    return ImageChops.multiply(a,b).histogram()[255]

def main():
    root=ROOT/REL
    role_metadata={}
    for role in grip.ROLES:
        item=grip.archive(role)
        if not item:
            raise ValueError("GRIP_QA_METRIC_MISSING "+role)
        role_metadata[role]=item
    spear,record=verified_art("object-lanca-direita")
    points=spear_endpoints(spear)
    spear_preview,guide=draw_spear_preview(spear,points,[923,1130],[395,430])
    spear_mask=scene_mask(spear_preview,(0,0))
    rows=[]
    for cfg in VARIANTS:
        images={}
        transforms={}
        for role in grip.ROLES:
            image,offset,info=registered(role,cfg[role])
            if info["source_sha256"]!=role_metadata[role]["sha256"]:
                raise ValueError("GRIP_QA_METRIC_SHA_CHANGED "+role)
            images[role]=scene_mask(image,offset)
            transforms[role]={"source_sha256":info["source_sha256"],
                              "offset_xy":list(offset),
                              "uniform_scale_preview":info["uniform_scale_for_preview"]}
        pairs={
            "forearm_to_palm":intersection_count(images["forearm-cuff"],images["palm-rear"]),
            "palm_to_spear":intersection_count(images["palm-rear"],spear_mask),
            "fingers_to_spear":intersection_count(images["fingers-front"],spear_mask),
            "palm_to_fingers":intersection_count(images["palm-rear"],images["fingers-front"]),
        }
        warnings=[name+"_NO_ALPHA_OVERLAP" for name,v in pairs.items() if v==0]
        rows.append({
            "id":cfg["id"],
            "pixel_intersections_in_contact_roi":pairs,
            "zero_overlap_warnings":warnings,
            "all_pairs_touch_in_2d":not warnings,
            "source_transformations_are_preview_only":transforms,
            "anatomical_accuracy_verified":False,
            "visual_approval":False,
        })
    result={
       "schema":"videoforge/ep01-c01p04-v3-grip-contact-metrics/v1",
       "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
       "approved_original_sha256":grip.APPROVED_SHA,
       "contact_roi_xyxy":list(CONTACT_ROI),
       "spear_sha256":record["sha256"],
       "spear_preview_transform":guide,
       "variants":rows,
       "what_it_proves":"Count of hard-alpha pixel intersection of independent objects at provisional positions",
       "what_it_does_not_prove":"Correct grip anatomy, true depth order, style or motion continuity",
       "pixel_counts_are_not_approval":True,
       "human_visual_approval":False,
       "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False,
       "provider_calls":0
    }
    out=root/(NAME+".json")
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GRIP_V3_CONTACT_PIXEL_METRICS",json.dumps({
        "variants":[{"id":x["id"],
                     "counts":x["pixel_intersections_in_contact_roi"],
                     "warnings":x["zero_overlap_warnings"]} for x in rows],
        "visual_approved":False},ensure_ascii=False))
    return result

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,RuntimeError) as e:
        print("GRIP_V3_METRIC_QA_FAILED",str(e),file=sys.stderr)
        sys.exit(2)
