"""Creator-facing QA comparison of both separate grips against approved mother.

Display only; exact-SHA inputs; reversible geometry; not a pose, rig asset,
approved registration or final MP4. No generative calls or pixel cutouts.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
from PIL import Image,ImageOps,ImageDraw,ImageFont
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge.ep01_approved_v3_parts import aligned_source
from videoforge import ep01_c01p04_grip_v3 as left,ep01_c01p04_right_grip_v1 as right
from scripts.qa_ep01_c01p04_grip_v3_contact import registered as left_registered,SCENE
from scripts.qa_ep01_c01p04_right_grip_v1_contact import registered as right_registered
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_spear_registration import spear_endpoints,draw_spear_preview

NAME="QA-C01-P04-V3-DUAS-PEGADAS-CONFERENCIA"
SELECTIONS={
 "left":{
   "source_module":"left_grip_v3","spear_part":"object-lanca-esquerda",
   "base":[65,1130],"tip":[525,430],
   "box":[90,865,280,1080],
   "candidate":"R3-tightest-provisional",
   "offsets":{"forearm-cuff":[45,52],"palm-rear":[-32,6],"fingers-front":[-35,6]}},
 "right":{
   "source_module":"right_grip_v1","spear_part":"object-lanca-direita",
   "base":[923,1130],"tip":[395,430],
   "box":[650,865,840,1080],
   "candidate":"W3-cuff-right30",
   "offsets":{"forearm-cuff":[30,50],"palm-rear":[22,0],"fingers-front":[25,0]}}
}
def font(n):
    try:return ImageFont.truetype("DejaVuSans.ttf",n)
    except OSError:return ImageFont.load_default()
def display(src:Image.Image,label:str):
    out=Image.new("RGB",(340,460),"#ffffff")
    d=ImageDraw.Draw(out)
    d.text((8,9),label,font=font(15),fill="#232323")
    thumb=ImageOps.contain(src.convert("RGB"),(319,405),Image.Resampling.LANCZOS)
    out.paste(thumb,((out.width-thumb.width)//2,40))
    return out
def create():
    mother=aligned_source()
    if mother["sha256"]!=left.ALIGNED_SHA or mother["sha256"]!=right.ALIGNED_SHA:
        raise ValueError("TWO_GRIPS_MOTHER_SHA_CHANGED")
    with Image.open(BytesIO(mother["blob"])) as im:
        approved=im.convert("RGB")
    board=Image.new("RGB",(4*352+18,574),"#e9e8e4")
    pen=ImageDraw.Draw(board)
    pen.text((14,9),"EP01 C01-P04 V3 / DUAS PEGADAS COMPARADAS",font=font(24),fill="#161616")
    pen.text((14,43),"Apenas QA. Original aprovado; sprites V3 e transformacoes ainda NAO aprovados.",font=font(15),fill="#a42b21")
    manifest={}
    for index,side in enumerate(("left","right")):
        cfg=SELECTIONS[side]
        register=left_registered if side=="left" else right_registered
        engine=left if side=="left" else right
        for role in engine.ROLES:
            if engine.archive(role) is None:
                raise ValueError("TWO_GRIPS_ARCHIVED_PART_MISSING "+side+" "+role)
        spear,proof=verified_art(cfg["spear_part"])
        sp,transform=draw_spear_preview(spear,spear_endpoints(spear),
                                       cfg["base"],cfg["tip"])
        canvas=Image.new("RGBA",SCENE,(0,0,0,0))
        detail={}
        for role in ("forearm-cuff","palm-rear"):
            layer,pos,data=register(role,tuple(cfg["offsets"][role]))
            canvas.alpha_composite(layer,pos)
            detail[role]=data
        canvas.alpha_composite(sp)
        layer,pos,data=register("fingers-front",tuple(cfg["offsets"]["fingers-front"]))
        canvas.alpha_composite(layer,pos)
        detail["fingers-front"]=data
        box=tuple(cfg["box"])
        original=approved.crop(box)
        stage=canvas.crop(box)
        check=Image.new("RGBA",stage.size,(234,234,234,255))
        check.alpha_composite(stage)
        panels=[
            (f"{side.upper()} - MAE APROVADA",original),
            (f"{side.upper()} - {cfg['candidate']} (QA)",check.convert("RGB"))]
        for j,(label,image) in enumerate(panels):
            x=10+(index*2+j)*352
            board.paste(display(image,label),(x,78))
        manifest[side]={
           "candidate":cfg["candidate"],
           "source_sha256_by_component":{r:detail[r]["source_sha256"] for r in engine.ROLES},
           "source_spear_sha256":proof["sha256"],
           "provisional_coordinates_xyxy":cfg["box"],
           "offset_delta_xy_by_layer":cfg["offsets"],
           "spear_preview_transform":transform,
           "mirror_of_opposite_guard":False,
           "approved_registration":False,
           "human_visual_approval":False,
           "rig_ready":False}
    dest=ROOT/REL/(NAME+".jpg")
    board.save(dest,"JPEG",quality=88,optimize=True)
    report={
        "schema":"videoforge/ep01-c01p04-v3-both-grips-visual-qa/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "original_approved_image_sha256":left.APPROVED_SHA,
        "aligned_mother_sha256":left.ALIGNED_SHA,
        "panels":manifest,
        "board":dest.name,"board_sha256":sha256(dest.read_bytes()).hexdigest(),
        "qa_only_no_source_pixel_edits":True,
        "model_calls":0,"rig_ready":False,
        "hand_contact_verified":False,"spatial_registration_approved":False,
        "human_visual_approval":False,"mp4_generated":False,"youtube_uploaded":False,
        "next":"creator inspect both grips; if good confirm reference candidate before rig; otherwise adjust only failing transform or sublayer"}
    (ROOT/REL/(NAME+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TWO_GRIPS_QA_READY",json.dumps({
        "panels":list(manifest),"review_only":True,"rig_ready":False},ensure_ascii=False))
    return report
if __name__=="__main__":
    create()
