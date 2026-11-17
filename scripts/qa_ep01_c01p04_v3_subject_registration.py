"""QA-only SUBJECT-space registration of independent V3 sprites to their scene.

Unlike whole-PNG fit, align opaque bbox to provisional scene ROIs, keeping the
aspect ratio. Does NOT change originals or save rig assets. Every candidate
requires HUMAN VISUAL review and consistent spear-hand contacts.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
import sys
from PIL import Image,ImageOps,ImageDraw,ImageFont
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge.ep01_approved_v3_parts import aligned_source
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_native_registration import source_entry,native_alpha_bbox

BASENAME="QA-C01-P04-V3-REGISTRO-SILHUETAS"
EXPECTED_SOURCE="b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
TARGETS={
  # These ROIs are manual *candidates* inferred from the V3 mother visual.
  # They are NOT verified individual character masks or approved anchors.
  "character-aldric":{"target_bbox":[406,181,663,508],"ground_anchor":"seat_on_throne"},
  "character-guarda_esquerdo":{"target_bbox":[3,523,332,1325],"ground_anchor":"left_floor_contact"},
  "character-guarda_direito":{"target_bbox":[621,519,939,1328],"ground_anchor":"right_floor_contact"},
}
def font(size):
    try:return ImageFont.truetype("DejaVuSans.ttf",size)
    except OSError:return ImageFont.load_default()

def subject_transform(native_bbox,target,variant):
    sx1,sy1,sx2,sy2=native_bbox
    dx1,dy1,dx2,dy2=target
    w=sx2-sx1; h=sy2-sy1
    if min(w,h,dx2-dx1,dy2-dy1)<=0:
        raise ValueError("EP01_SUBJECT_REGISTRATION_BAD_BBOX")
    base=min((dx2-dx1)/w,(dy2-dy1)/h)
    factor={"A-fit-target":1.0,"B-90pct":0.90,"C-110pct":1.10}[variant]
    scale=base*factor
    new_width=w*scale;new_height=h*scale
    # Align center X, ground / throne contact Y, not top-left canvas.
    center_x=(dx1+dx2)/2
    bottom_y=dy2
    offset_x=round(center_x - ((sx1+sx2)/2)*scale)
    offset_y=round(bottom_y - sy2*scale)
    bbox=[round(sx1*scale+offset_x),round(sy1*scale+offset_y),
          round(sx2*scale+offset_x),round(sy2*scale+offset_y)]
    return {"scale":round(scale,7),"offset_xy":[offset_x,offset_y],
            "preview_bbox_scene_xyxy":bbox,
            "variant":variant,"uniform_scale":True,"approved":False}

def scene_overlay(mother,src,transform,target):
    if mother.size != (941,1672):
        raise ValueError("EP01_SUBJECT_REGISTRATION_BAD_MOTHER")
    new=(max(1,round(src.width*transform["scale"])),
         max(1,round(src.height*transform["scale"])))
    preview=src.resize(new,Image.Resampling.LANCZOS)
    color=preview.copy()
    color.putalpha(preview.getchannel("A").point(lambda a:round(a*0.65)))
    out=mother.convert("RGBA").copy()
    out.alpha_composite(color,transform["offset_xy"])
    d=ImageDraw.Draw(out)
    bbox=transform["preview_bbox_scene_xyxy"]
    d.rectangle(tuple(bbox),outline=(255,40,40,255),width=5)
    d.rectangle(tuple(target),outline=(15,230,150,255),width=3)
    return out.convert("RGB")

def thumb(im,w=320,h=570):
    out=Image.new("RGB",(w,h),"white")
    small=ImageOps.contain(im,(w,h),Image.Resampling.LANCZOS)
    out.paste(small,((w-small.width)//2,(h-small.height)//2))
    return out

def main():
    root=ROOT/REL
    src=aligned_source()
    if src["sha256"]!=EXPECTED_SOURCE:
        raise ValueError("EP01_SUBJECT_REGISTRATION_SHA_CHANGED")
    with Image.open(BytesIO(src["blob"])) as im:
        mother=im.convert("RGB")
    master=json.loads((root/"QA-C01-P04-V3-CAMADAS-INDEPENDENTES.json").read_text(encoding="utf-8"))
    if master.get("technical_reference_sha256")!=EXPECTED_SOURCE:
        raise ValueError("EP01_SUBJECT_REGISTRATION_PARTS_QA_MISMATCH")
    board=Image.new("RGB",(4*351+35,3*650+82),"#ece9e5")
    d=ImageDraw.Draw(board)
    d.text((20,9),"EP01 C01-P04 V3 | CORRIGIR ESCALA DOS SPRITES",font=font(23),fill="#151515")
    d.text((20,44),"PRÉVIAS A/B/C: escalas proporcionais, NÃO ALTERAM PNG / NÃO AUTORIZAM RIG.",font=font(15),fill="#a72f22")
    records=[]
    for i,(part,cfg) in enumerate(TARGETS.items()):
        if part=="character-aldric" or part=="character-guarda_esquerdo":
            obj,data=source_entry(part,master)
        else:
            obj,data=verified_art(part)
        rawbox=native_alpha_bbox(obj)
        anchor=cfg["target_bbox"]
        y=82+i*650
        # Original reference first for visual scale/composition matching.
        variants=[("MÃE APROVADA",mother,None)]
        row={"part":part,"source_sha256":data["sha256"],
             "native_dimensions":list(obj.size),
             "native_alpha_bbox_xyxy":list(rawbox),
             "provisional_reference_roi_xyxy":anchor,
             "provisional_anchor":cfg["ground_anchor"],
             "options":[],"accepted_transform":None,
             "human_visual_approved":False,"rig_ready":False,
             "for_qa_only":True}
        for variant in ("A-fit-target","B-90pct","C-110pct"):
            t=subject_transform(rawbox,anchor,variant)
            result=scene_overlay(mother,obj,t,anchor)
            variants.append((variant,result,t))
            row["options"].append(t)
        for j,(label,view,t) in enumerate(variants):
            x=14+j*351
            d.rounded_rectangle((x,y,x+340,y+635),radius=6,fill="#ffffff")
            d.text((x+8,y+9),part.replace("character-","")+" | "+label,
                   font=font(14),fill="#242424")
            board.paste(thumb(view),(x+10,y+43))
            if t:
                d.text((x+9,y+615),"s="+str(t["scale"])[:8]+" (QA)",font=font(11),fill="#a72f22")
        records.append(row)
    dest=root/(BASENAME+".jpg")
    board.save(dest,"JPEG",quality=88,optimize=True)
    report={"schema":"videoforge/ep01-c01p04-v3-subject-space-registration/v1",
            "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
            "creator_approved_original_sha256":"a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd",
            "reference_sha256":EXPECTED_SOURCE,"board":dest.name,
            "board_sha256":sha256(dest.read_bytes()).hexdigest(),
            "targets":records,
            "placement_rois_are_provisional":True,
            "geometry_is_preview_only_no_final_sprite_export":True,
            "no_repeated_model_calls":True,
            "rig_ready":False,"human_approved_registration":False,
            "mp4_generated":False,"youtube_uploaded":False,
            "next":"Inspect A/B/C and spear contact; accept exact transform explicitly or regenerate wrong sprites using framed guides"}
    (root/(BASENAME+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_SUBJECT_REGISTRATION_QA",json.dumps({
        "targets":[{"id":t["part"],"options":[o["scale"] for o in t["options"]]} for t in records],
        "rig_ready":False,"provider_calls":0},ensure_ascii=False))
    return report

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,RuntimeError) as e:
        print("EP01_SUBJECT_REGISTRATION_FAILED",str(e),file=sys.stderr)
        sys.exit(2)
