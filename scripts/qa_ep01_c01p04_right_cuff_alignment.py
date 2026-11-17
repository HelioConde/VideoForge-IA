"""C01-P04 right-guard wrist alignment grid; QA-only, no final sprites.

Uses previously generated, SHA-verified forearm, palm, fingertips, spear
and approved mother. Never authorizes animation or overwrites PNG originals.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
from PIL import Image,ImageDraw,ImageOps,ImageFont
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge.ep01_approved_v3_parts import aligned_source
from videoforge import ep01_c01p04_right_grip_v1 as grip
from scripts.qa_ep01_c01p04_right_grip_v1_contact import registered,SCENE
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_spear_registration import spear_endpoints,draw_spear_preview
from scripts.qa_ep01_c01p04_right_grip_v1_metrics import scene_mask,intersection_count

BASENAME="QA-C01-P04-V3-GUARDA-DIREITO-ALINHAMENTO-PUNHO-V2"
ROI=(640,845,855,1100)
OPTIONS=[
  {"id":"W1-cuff-neutral","cuff":[0,40],"palm":[22,0],"digits":[25,0]},
  {"id":"W2-cuff-right15","cuff":[15,45],"palm":[22,0],"digits":[25,0]},
  {"id":"W3-cuff-right30","cuff":[30,50],"palm":[22,0],"digits":[25,0]},
  {"id":"W4-cuff-right45","cuff":[45,55],"palm":[22,0],"digits":[25,0]},
]
def font(n):
    try:return ImageFont.truetype("DejaVuSans.ttf",n)
    except OSError:return ImageFont.load_default()
def tile(img,label):
    w,h=300,440
    board=Image.new("RGB",(w,h),"white")
    d=ImageDraw.Draw(board)
    d.text((9,9),label,font=font(15),fill="#222222")
    thumb=ImageOps.contain(img.convert("RGB"),(284,392),Image.Resampling.LANCZOS)
    board.paste(thumb,((w-thumb.width)//2,36))
    return board
def make():
    src=aligned_source()
    if src["sha256"]!=grip.ALIGNED_SHA:
        raise RuntimeError("RIGHT_CUFF_QA_APPROVED_SOURCE_CHANGED")
    for role in grip.ROLES:
        if not grip.archive(role):
            raise RuntimeError("RIGHT_CUFF_QA_MISSING_PART "+role)
    with Image.open(BytesIO(src["blob"])) as img:
        mother=img.convert("RGB")
    spear,sm=verified_art("object-lanca-direita")
    shaft,shaftmap=draw_spear_preview(spear,spear_endpoints(spear),
                                    [923,1130],[395,430])
    out=Image.new("RGB",(5*310+18,555),"#e6e6e3")
    drawer=ImageDraw.Draw(out)
    drawer.text((15,12),"C01-P04 / GUARDA DIREITO: ENCAIXE DA BRAÇADEIRA",font=font(23),fill="#151515")
    drawer.text((15,46),"Apenas propostas de registro espacial, nenhum PNG alterado, nao usar no rig.",font=font(14),fill="#a12323")
    approved_crop=mother.crop(ROI)
    out.paste(tile(approved_crop,"MAE APROVADA"),(8,92))
    records=[]
    for ix,item in enumerate(OPTIONS,1):
        forearm,forearm_pos,forearm_info=registered("forearm-cuff",tuple(item["cuff"]))
        palm,palm_pos,palm_info=registered("palm-rear",tuple(item["palm"]))
        fingers,digits_pos,digits_info=registered("fingers-front",tuple(item["digits"]))
        canvas=Image.new("RGBA",SCENE,(0,0,0,0))
        canvas.alpha_composite(forearm,forearm_pos)
        canvas.alpha_composite(palm,palm_pos)
        canvas.alpha_composite(shaft)
        canvas.alpha_composite(fingers,digits_pos)
        wrist=canvas.crop(ROI)
        background=Image.new("RGBA",wrist.size,(230,230,230,255))
        background.alpha_composite(wrist)
        out.paste(tile(background.convert("RGB"),item["id"]),(8+ix*310,92))
        cuff_mask=scene_mask(forearm,forearm_pos)
        palm_mask=scene_mask(palm,palm_pos)
        fingers_mask=scene_mask(fingers,digits_pos)
        shaft_mask=scene_mask(shaft,(0,0))
        overlap={
           "forearm_to_palm":intersection_count(cuff_mask,palm_mask),
           "palm_to_spear":intersection_count(palm_mask,shaft_mask),
           "fingers_to_spear":intersection_count(fingers_mask,shaft_mask)
        }
        drawer.text((12+ix*310,535),"F/P="+str(overlap["forearm_to_palm"]),font=font(13),fill="#333333")
        records.append({
           "id":item["id"],"offset_deltas_provisional":item,
           "preview_transforms":{"cuff":forearm_info,"palm":palm_info,"fingers":digits_info},
           "alpha_intersection_pixels":overlap,
           "anatomical_contact_proven":False,
           "user_approved":False,"rig_ready":False
        })
    file=ROOT/REL/(BASENAME+".jpg")
    out.save(file,"JPEG",quality=86,optimize=True)
    result={
        "schema":"videoforge/ep01-c01p04-v3-right-cuff-placement-grid/v2",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "mother_sha256":grip.APPROVED_SHA,
        "spear_sha256":sm["sha256"],"shaft_transform_qa_only":shaftmap,
        "board":file.name,"board_sha256":sha256(file.read_bytes()).hexdigest(),
        "candidates":records,"best_option":None,
        "all_rois_are_editorial_estimates":True,
        "alpha_overlap_is_not_visual_approval":True,
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "proxy_calls":0
    }
    (ROOT/REL/(BASENAME+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_RIGHT_CUFF_QA",json.dumps({"variants":[{
        "id":x["id"],"intersections":x["alpha_intersection_pixels"]
    } for x in records],"rig_ready":False},ensure_ascii=False))
    return result
if __name__=="__main__":
    make()
