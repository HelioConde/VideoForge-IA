"""Compare V2 corrected left guard in full scene and hand closeup.

All transforms and layer orders are QA PREVIEWS ONLY. No alteration to
independent PNGs or approved mother, no final rig sprites or rendering.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from PIL import Image,ImageOps,ImageDraw,ImageFont

from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge.ep01_approved_v3_parts import aligned_source
from videoforge.ep01_c01p04_v3_guard_grip_v2 import archived as grip_archived,SCHEMA as GRIP_SCHEMA
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_native_registration import source_entry,native_alpha_bbox
from scripts.qa_ep01_c01p04_v3_subject_registration import subject_transform,TARGETS
from scripts.qa_ep01_c01p04_v3_spear_registration import (
    spear_endpoints,draw_spear_preview,VARIANTS)

BASE="QA-C01-P04-V3-GUARDA-ESQUERDO-PEGADA-V2"
SOURCE_SHA="b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
PART="character-guarda_esquerdo"

def font(n):
    try:return ImageFont.truetype("DejaVuSans.ttf",n)
    except OSError:return ImageFont.load_default()

def checked_new():
    info=grip_archived(PART)
    if info is None:raise ValueError("GRIP_QA_V2_NOT_ARCHIVED")
    path=ROOT/info["file"]
    proof=path.with_suffix(".production.json")
    if not proof.is_file() or path.is_symlink() or proof.is_symlink():
        raise ValueError("GRIP_QA_PROOF_MISSING")
    raw=path.read_bytes()
    data=json.loads(proof.read_text(encoding="utf-8"))
    if (sha256(raw).hexdigest()!=info["sha256"]
        or data.get("schema")!=GRIP_SCHEMA
        or data.get("component")!=PART
        or data.get("source_image_sha256")!=SOURCE_SHA
        or data.get("sha256")!=info["sha256"]
        or data.get("human_visual_approval") is not False
        or data.get("rig_ready") is not False):
        raise ValueError("GRIP_QA_V2_PROVENANCE_MISMATCH")
    with Image.open(BytesIO(raw)) as image:
        if image.format!="PNG" or "A" not in image.getbands():
            raise ValueError("GRIP_QA_V2_NOT_RGBA")
        result=image.convert("RGBA")
    return result, info["sha256"],data

def place_actor(src,bbox,roi,variant="A-fit-target"):
    t=subject_transform(bbox,roi,variant)
    size=(round(src.width*t["scale"]),round(src.height*t["scale"]))
    if min(size)<=0:raise ValueError("GRIP_QA_SCALE_INVALID")
    resized=src.resize(size,Image.Resampling.LANCZOS)
    return resized,tuple(t["offset_xy"]),t

def thumb(im,sz=(315,558)):
    img=ImageOps.contain(im.convert("RGB"),sz,Image.Resampling.LANCZOS)
    result=Image.new("RGB",sz,"white")
    result.paste(img,((sz[0]-img.width)//2,(sz[1]-img.height)//2))
    return result

def main():
    root=ROOT/REL
    src=aligned_source()
    if src["sha256"]!=SOURCE_SHA:
        raise ValueError("GRIP_QA_SOURCE_SHA_CHANGED")
    with Image.open(BytesIO(src["blob"])) as m:
        mother=m.convert("RGB")
    cfg=json.loads((root/"QA-C01-P04-V3-CAMADAS-INDEPENDENTES.json").read_text(encoding="utf-8"))
    obj=json.loads((root/"QA-C01-P04-V3-REGISTRO-SILHUETAS.json").read_text(encoding="utf-8"))
    byid={x["part"]:x for x in obj["targets"]}
    bg,bgmeta=verified_art("background-clean")
    kael,kaelmeta=verified_art("character-kael")
    king,kingmeta=source_entry("character-aldric",cfg)
    right,rightmeta=verified_art("character-guarda_direito")
    leftold,leftmeta=source_entry(PART,cfg)
    leftnew,leftnewsha,record=checked_new()
    kingx=byid["character-aldric"]
    rightx=byid["character-guarda_direito"]
    lx=byid[PART]
    kingp=place_actor(king,native_alpha_bbox(king),kingx["provisional_reference_roi_xyxy"])
    rightp=place_actor(right,native_alpha_bbox(right),rightx["provisional_reference_roi_xyxy"],"B-90pct")
    oldp=place_actor(leftold,native_alpha_bbox(leftold),lx["provisional_reference_roi_xyxy"])
    newp=place_actor(leftnew,native_alpha_bbox(leftnew),lx["provisional_reference_roi_xyxy"])
    spearold={}
    for p in ("object-lanca-esquerda","object-lanca-direita"):
        im,_=verified_art(p)
        spearold[p]=im
    # The S4 pole endpoints are draft editorial hypotheses only.
    cand=next(x for x in VARIANTS if x["id"]=="S4-through-grips")
    transformed_spears=[]
    for tag,p in (("left","object-lanca-esquerda"),("right","object-lanca-direita")):
        im=spearold[p]
        placed,meta=draw_spear_preview(im,spear_endpoints(im),
                                       cand[tag+"_base"],cand[tag+"_tip"])
        transformed_spears.append(placed)
    def assemble(left,order):
        scene=bg.convert("RGBA").copy()
        for im,pos,meta in (kingp,rightp):
            scene.alpha_composite(im,pos)
        if order=="under":
            for pole in transformed_spears:scene.alpha_composite(pole)
        scene.alpha_composite(left[0],left[1])
        if order=="over":
            for pole in transformed_spears:scene.alpha_composite(pole)
        scene.alpha_composite(kael)
        return scene.convert("RGB")
    options=[
       ("MÃE APROVADA",mother),
       ("GUARDA ANTIGO + HASTES POR CIMA",assemble(oldp,"over")),
       ("GUARDA V2 + HASTES POR CIMA",assemble(newp,"over")),
       ("GUARDA V2 + HASTES SOB DEDOS",assemble(newp,"under")),
    ]
    paper=Image.new("RGB",(4*337+20,682),"#ece9e5")
    d=ImageDraw.Draw(paper)
    d.text((12,9),"C01-P04 V3 | NOVA PEGADA GUARDA ESQUERDO V2",font=font(23),fill="#151515")
    d.text((12,39),"SEM APROVACAO. Comparar escala, luva, haste e dedos. Sprites nao alterados.",font=font(15),fill="#a12a22")
    for i,(label,pic) in enumerate(options):
        x=8+i*337;y=70
        d.rounded_rectangle((x,y,x+325,y+596),radius=7,fill="#ffffff")
        d.text((x+7,y+10),label,font=font(12),fill="#242424")
        paper.paste(thumb(pic),(x+5,y+36))
    full=root/(BASE+".jpg")
    paper.save(full,"JPEG",quality=88,optimize=True)
    small=root/(BASE+"-PREVIEW.jpg")
    ImageOps.contain(paper,(1050,535),Image.Resampling.LANCZOS).save(
        small,"JPEG",quality=74,optimize=True)
    zoom=Image.new("RGB",(4*317+20,520),"#eceae6")
    dz=ImageDraw.Draw(zoom)
    dz.text((12,7),"PEGADA ESQUERDA V2: DETALHE DOS DEDOS vs REFERENCIA APROVADA",
            font=font(18),fill="#151515")
    dz.text((12,34),"TESTE DE CAMADAS APENAS. Nao recortar estes pixels para rig.",font=font(13),fill="#a72a22")
    for i,(label,pic) in enumerate(options):
        # Hand center estimated from the original V3; this crop is QA only.
        crop=pic.crop((20,775,330,1215))
        crop=ImageOps.contain(crop,(301,430),Image.Resampling.LANCZOS)
        x=6+i*317
        dz.text((x+6,65),label[:33],font=font(11),fill="#292929")
        zoom.paste(crop,(x+6,89))
    zpath=root/(BASE+"-MAO-ZOOM.jpg")
    zoom.save(zpath,"JPEG",quality=86,optimize=True)
    result={
       "schema":"videoforge/ep01-c01p04-v3-guard-grip-v2-qa/v1",
       "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
       "approved_source_sha256":"a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd",
       "technical_source_sha256":SOURCE_SHA,
       "old_guard_source_sha256":leftmeta["sha256"],
       "new_guard_source_sha256":leftnewsha,
       "new_guard_native_bbox_xyxy":list(native_alpha_bbox(leftnew)),
       "new_guard_native_dimensions":list(leftnew.size),
       "new_guard_technical_qa":record["technical_qa"],
       "registration_candidate":newp[2],
       "spear_pose_candidate":"S4-through-grips",
       "alternative_layering_orders":["spear_over_guard","spear_under_guard"],
       "full_board":full.name,"full_sha256":sha256(full.read_bytes()).hexdigest(),
       "preview_board":small.name,"preview_sha256":sha256(small.read_bytes()).hexdigest(),
       "hand_zoom_board":zpath.name,"hand_zoom_sha256":sha256(zpath.read_bytes()).hexdigest(),
       "hand_grip_contact_visual_approved":False,"scale_visual_approved":False,
       "original_pngs_modified":False,"no_final_mask_extraction":True,
       "provider_calls":0,"rig_ready":False,"youtube_uploaded":False,"mp4_generated":False,
    }
    (root/(BASE+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_GUARD_GRIP_V2_QA",json.dumps({
      "sha256":leftnewsha,"bbox":result["new_guard_native_bbox_xyxy"],
      "approved":False,"provider_calls":0},ensure_ascii=False))
    return result

if __name__=="__main__":
    try:main()
    except (ValueError,OSError,RuntimeError) as e:
        print("EP01_GUARD_GRIP_V2_QA_FAILED",str(e),file=sys.stderr)
        sys.exit(2)
