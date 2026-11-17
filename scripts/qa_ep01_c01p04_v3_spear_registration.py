"""Preview-only similarity alignment of the two SEPARATELY generated RGBA spears.

Uses two endpoints (base and tip) to keep each spear rigid and connect it
approximately to the guards' hands. Every anchor is an EDITORIAL GUESS;
no confirmed hand contact, no alpha cutout, no rig/export/render.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
import math
from PIL import Image, ImageOps, ImageDraw, ImageFont
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge.ep01_approved_v3_parts import aligned_source
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_native_registration import source_entry
from scripts.qa_ep01_c01p04_v3_clean_recomposition import (
    REPORT as TRANSFORMS_REPORT, SOURCE as MOTHER_SOURCE)
BASE="QA-C01-P04-V3-PEGADA-LANCAS"
SCENE=(941,1672)
SOURCE_MOTHER="a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
VARIANTS=[
    {"id":"S1-cross-medium","left_base":[175,1115],"left_tip":[568,465],
     "right_base":[764,1115],"right_tip":[374,465]},
    {"id":"S2-cross-higher","left_base":[175,1160],"left_tip":[590,355],
     "right_base":[765,1160],"right_tip":[350,355]},
    {"id":"S3-cross-lower","left_base":[200,1060],"left_tip":[535,525],
     "right_base":[740,1060],"right_tip":[405,525]},
]
def font(n):
    try:return ImageFont.truetype("DejaVuSans.ttf",n)
    except OSError:return ImageFont.load_default()

def spear_endpoints(im:Image.Image):
    if im.mode!="RGBA" or im.size!=SCENE:
        raise ValueError("SPEAR_QA_NATIVE_FULL_SCENE_EXPECTED")
    a=im.getchannel("A")
    box=a.point(lambda p: 255 if p>=24 else 0).getbbox()
    if not box:raise ValueError("SPEAR_QA_EMPTY_ALPHA")
    left,top,right,bottom=box
    def median_x(y0,y1):
        xs=[]
        pix=a.load()
        for y in range(max(top,y0),min(bottom,y1)):
            for x in range(left,right):
                if pix[x,y]>=64:
                    xs.append(x)
        if not xs:
            raise ValueError("SPEAR_QA_TIP_OR_BASE_NOT_FOUND")
        xs.sort()
        return round(xs[len(xs)//2])
    tip=[median_x(top,top+14),top+6]
    base=[median_x(bottom-14,bottom),bottom-7]
    if math.dist(tip,base)<450:raise ValueError("SPEAR_QA_AXIS_IMPLAUSIBLE")
    return {"tip_xy":tip,"base_xy":base,"bbox_xyxy":list(box)}

def affine_params(src_base,src_tip,dest_base,dest_tip):
    ux=src_tip[0]-src_base[0];uy=src_tip[1]-src_base[1]
    vx=dest_tip[0]-dest_base[0];vy=dest_tip[1]-dest_base[1]
    denom=ux*ux+uy*uy
    if denom<100:return None
    scale=math.hypot(vx,vy)/math.sqrt(denom)
    theta=math.atan2(vy,vx)-math.atan2(uy,ux)
    c=math.cos(theta)/scale; s=math.sin(theta)/scale
    a,b,d,e=c,s,-s,c
    tx=src_base[0]-a*dest_base[0]-b*dest_base[1]
    ty=src_base[1]-d*dest_base[0]-e*dest_base[1]
    return (a,b,tx,d,e,ty),scale,theta

def draw_spear_preview(src:Image.Image,srcpts:dict,base,tip):
    values=affine_params(srcpts["base_xy"],srcpts["tip_xy"],base,tip)
    if values is None:raise ValueError("SPEAR_QA_DEGENERATE")
    coeffs,scale,theta=values
    out=src.transform(SCENE,Image.Transform.AFFINE,coeffs,
                      Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
    return out,{"source_tip_xy":srcpts["tip_xy"],"source_base_xy":srcpts["base_xy"],
                "preview_tip_xy":tip,"preview_base_xy":base,
                "scale":round(scale,6),"rotation_deg":round(math.degrees(theta),3),
                "preview_only":True,"physical_grip_verified":False}

def main():
    root=ROOT/REL
    src=aligned_source()
    if src["sha256"]!=MOTHER_SOURCE:raise ValueError("SPEAR_QA_MOTHER_SHA_CHANGED")
    with Image.open(BytesIO(src["blob"])) as i:
        mother=i.convert("RGB")
    transforms=json.loads(TRANSFORMS_REPORT.read_text(encoding="utf-8"))
    if (transforms.get("reference_sha256")!=MOTHER_SOURCE
        or transforms.get("human_approved_registration") is not False):
        raise ValueError("SPEAR_QA_TRANSFORM_PROVENANCE_INVALID")
    options={x["part"]:{o["variant"]:o for o in x["options"]}
             for x in transforms["targets"]}
    parts=json.loads((root/"QA-C01-P04-V3-CAMADAS-INDEPENDENTES.json").read_text(encoding="utf-8"))
    bg,_=verified_art("background-clean")
    kael,_=verified_art("character-kael")
    # Best *editorial* candidate (not approval) after 3x3 comparison:
    choices={"character-aldric":"A-fit-target",
             "character-guarda_esquerdo":"A-fit-target",
             "character-guarda_direito":"B-90pct"}
    layers={}
    for part in choices:
        image,metadata=(source_entry(part,parts) if part in
            ("character-aldric","character-guarda_esquerdo") else verified_art(part))
        if metadata["sha256"]!=next(x["source_sha256"] for x in transforms["targets"]
                                      if x["part"]==part):
            raise ValueError("SPEAR_QA_CHARACTER_SHA_MISMATCH "+part)
        op=options[part][choices[part]]
        resized=image.resize((round(image.width*op["scale"]),
                              round(image.height*op["scale"])),Image.Resampling.LANCZOS)
        layers[part]=(resized,tuple(op["offset_xy"]),metadata["sha256"])
    scene=bg.convert("RGBA").copy()
    for part in choices:
        im,pos,_=layers[part]
        scene.alpha_composite(im,pos)
    spears={}
    for part in ("object-lanca-esquerda","object-lanca-direita"):
        im,record=verified_art(part)
        spears[part]=(im,spear_endpoints(im),record["sha256"])
    paper=Image.new("RGB",(4*345+25,705),"#e9e7e4")
    pen=ImageDraw.Draw(paper)
    pen.text((15,10),"EP01 C01-P04 / POSICAO DAS LANCAS EM 3 OPCOES",font=font(22),fill="#111111")
    pen.text((15,44),"SOMENTE QA. Pegadas, intersecao e poses ainda nao aprovadas.",font=font(15),fill="#a02b26")
    panels=[("MÃE APROVADA",mother)]
    candidates=[]
    for variant in VARIANTS:
        frame=scene.copy()
        details={}
        for tag,part in (("left","object-lanca-esquerda"),
                         ("right","object-lanca-direita")):
            im,end,hashvalue=spears[part]
            pic,rec=draw_spear_preview(im,end,variant[tag+"_base"],variant[tag+"_tip"])
            frame.alpha_composite(pic)
            rec["sha256"]=hashvalue
            details[part]=rec
        frame.alpha_composite(kael)
        panels.append((variant["id"],frame.convert("RGB")))
        candidates.append({"id":variant["id"],"spear_transforms":details,
                           "characters":choices,"human_approved":False})
    for i,(label,im) in enumerate(panels):
        x=6+i*345;y=75
        pen.rounded_rectangle((x,y,x+330,y+618),radius=6,fill="#ffffff")
        pen.text((x+8,y+8),label,font=font(15),fill="#292929")
        thumb=ImageOps.contain(im,(311,565),Image.Resampling.LANCZOS)
        paper.paste(thumb,(x+(330-thumb.width)//2,y+40))
    dest=root/(BASE+".jpg")
    paper.save(dest,"JPEG",quality=87,optimize=True)
    preview=root/(BASE+"-PREVIEW.jpg")
    sm=ImageOps.contain(paper,(1024,550),Image.Resampling.LANCZOS)
    sm.save(preview,"JPEG",quality=73,optimize=True)
    # Native scene-space closeups, QA ONLY: no sprite crops are exported.
    grips=[("MAO ESQUERDA",[175,1115]),("MAO DIREITA",[764,1115])]
    detail=Image.new("RGB",(4*338+20,2*476+60),"#ebe9e5")
    p=ImageDraw.Draw(detail)
    p.text((14,10),"C01-P04 / PEGADAS: CONFERIR FINGERS + HASTES",font=font(22),fill="#111111")
    p.text((14,39),"AMPLIACOES PARA QA; nenhuma mascara/recorte serve como asset de rig.",font=font(13),fill="#a02b26")
    for row,(name,xy) in enumerate(grips):
        for col,(label,im) in enumerate(panels):
            x=8+col*338;y=65+row*476
            p.rounded_rectangle((x,y,x+328,y+458),radius=5,fill="#ffffff")
            p.text((x+8,y+5),name+" | "+label,font=font(12),fill="#242424")
            crop=im.crop((xy[0]-155,xy[1]-195,xy[0]+155,xy[1]+195))
            crop=crop.resize((310,390),Image.Resampling.LANCZOS)
            detail.paste(crop,(x+9,y+30))
            cx=x+9+155;cy=y+30+195
            p.ellipse((cx-9,cy-9,cx+9,cy+9),outline="#ff3d36",width=3)
    detail_path=root/(BASE+"-PEGADAS-ZOOM.jpg")
    detail.save(detail_path,"JPEG",quality=81,optimize=True)
    output={
      "schema":"videoforge/ep01-c01p04-v3-qa-spear-registration/v1",
      "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
      "approved_mother_sha256":SOURCE_MOTHER,
      "aligned_mother_sha256":MOTHER_SOURCE,
      "independent_spear_sources":{
         k:{"sha256":v[2],**v[1]} for k,v in spears.items()},
      "character_registration_provisional":choices,
      "candidates":candidates,"best_candidate":None,
      "source_pngs_changed":False,"only_uniform_rigid_spear_transforms":True,
      "hand_grip_contact_verified":False,
      "camera_and_animation_ready":False,
      "human_visual_approval":False,"rig_ready":False,
      "mp4_generated":False,"youtube_uploaded":False,
      "provider_calls":0,"board":dest.name,"board_sha256":sha256(dest.read_bytes()).hexdigest(),
      "preview":preview.name,"preview_sha256":sha256(preview.read_bytes()).hexdigest(),
      "hand_grip_qa_board":detail_path.name,
      "hand_grip_qa_board_sha256":sha256(detail_path.read_bytes()).hexdigest(),
      "hand_grip_centers_provisional":{"left":[175,1115],"right":[764,1115]},
      "next":"Review whether spear bases align to real fingers and tips cross above Kael; if not, regenerate gripping hands or spears as independent parts",
    }
    (root/(BASE+".json")).write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_SPEAR_QA",json.dumps({
       "candidates":[x["id"] for x in candidates],"no_calls":True,"rig_ready":False}))
    return output

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,RuntimeError) as err:
        print("EP01_SPEAR_QA_FAILED",str(err))
        raise SystemExit(2)
