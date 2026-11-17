"""Preview-only recomposition of independent V3 characters over independent clean BG.

The reference V3 mother is NEVER altered. Native RGBA actors get reversible
uniform scene-space transformations only in temporary QA screenshots;
NO rig assets or final rendering are produced.
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
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from scripts.qa_ep01_c01p04_v3_native_registration import source_entry
from scripts.qa_ep01_c01p04_v3_subject_registration import TARGETS, subject_transform, native_alpha_bbox

BASENAME="QA-C01-P04-V3-RECOMPOSICAO-LIMPA"
REPORT=ROOT/REL/"QA-C01-P04-V3-REGISTRO-SILHUETAS.json"
QA=ROOT/REL/"QA-C01-P04-V3-CAMADAS-INDEPENDENTES.json"
SOURCE="b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"

def font(sz):
    try:return ImageFont.truetype("DejaVuSans.ttf",sz)
    except OSError:return ImageFont.load_default()

def transformed(src:Image.Image, op:dict):
    dest_size=(round(src.width*op["scale"]),round(src.height*op["scale"]))
    if min(dest_size)<=0 or max(dest_size)>5000:
        raise ValueError("EP01_COMPOSITE_UNSAFE_SCALE")
    return src.resize(dest_size,Image.Resampling.LANCZOS),tuple(op["offset_xy"])

def create():
    root=ROOT/REL
    ref=aligned_source()
    if ref["sha256"]!=SOURCE:raise ValueError("EP01_COMPOSITE_SOURCE_CHANGED")
    with Image.open(BytesIO(ref["blob"])) as f:
        mother=f.convert("RGBA")
    reg=json.loads(REPORT.read_text(encoding="utf-8"))
    qa=json.loads(QA.read_text(encoding="utf-8"))
    if (reg.get("reference_sha256")!=SOURCE
        or reg.get("human_approved_registration") is not False
        or reg.get("rig_ready") is not False
        or qa.get("technical_reference_sha256")!=SOURCE):
        raise ValueError("EP01_COMPOSITE_REFERENCES_UNVERIFIED")
    bg,bginfo=verified_art("background-clean")
    kael,kinf=verified_art("character-kael")
    if bg.size!=(941,1672) or kael.size!=(941,1672):
        raise ValueError("EP01_COMPOSITE_FULL_CANVAS_SOURCE_INVALID")
    sprites={}
    for part in TARGETS:
        if part in ("character-aldric","character-guarda_esquerdo"):
            img,details=source_entry(part,qa)
        else:
            img,details=verified_art(part)
        entries=[entry for entry in reg["targets"] if entry["part"]==part]
        if len(entries)!=1 or entries[0]["source_sha256"]!=details["sha256"]:
            raise ValueError("EP01_COMPOSITE_SOURCE_SHA_MISMATCH "+part)
        if entries[0]["native_alpha_bbox_xyxy"]!=list(native_alpha_bbox(img)):
            raise ValueError("EP01_COMPOSITE_NATIVE_ALPHA_BBOX_CHANGED "+part)
        sprites[part]=(img,entries[0])
    variants=[
        {"id":"A-A-A","king":"A-fit-target","left":"A-fit-target","right":"A-fit-target"},
        {"id":"A-A-B","king":"A-fit-target","left":"A-fit-target","right":"B-90pct"},
        {"id":"A-B-B","king":"A-fit-target","left":"B-90pct","right":"B-90pct"},
    ]
    output=Image.new("RGB",(4*350+32,720),"#eceae5")
    d=ImageDraw.Draw(output)
    d.text((15,9),"C01-P04 V3 | RECOMPOSICAO LIMPA SEM DUPLICAR A MAE",font=font(22),fill="#1d1d1d")
    d.text((15,42),"PREVIA (SEM LANCAS). ESCALAS E ANCORAS NAO APROVADAS. NAO USAR NO RIG.",font=font(15),fill="#9d302a")
    thumbnails=[("MAE APROVADA",mother.convert("RGB"))]
    records=[]
    for var in variants:
        scene=bg.convert("RGBA").copy()
        opts={}
        for part,vname in [
            ("character-aldric",var["king"]),
            ("character-guarda_esquerdo",var["left"]),
            ("character-guarda_direito",var["right"])]:
            src,meta=sprites[part]
            opts_map={x["variant"]:x for x in meta["options"]}
            if vname not in opts_map:raise ValueError("EP01_COMPOSITE_MISSING_REGISTER")
            transform=opts_map[vname]
            resized,offset=transformed(src,transform)
            scene.alpha_composite(resized,offset)
            opts[part]={"source_sha256":meta["source_sha256"],
                        "variant":vname,"scale":transform["scale"],
                        "offset_xy":list(offset),"preview_only":True}
        scene.alpha_composite(kael)
        thumbnails.append((var["id"]+" SEM LANCAS",scene.convert("RGB")))
        records.append({"id":var["id"],"parts":opts,"human_approved":False})
    for i,(label,im) in enumerate(thumbnails):
        x=10+i*351;y=73
        d.rounded_rectangle((x,y,x+340,y+630),radius=8,fill="#ffffff")
        d.text((x+8,y+8),label,font=font(16),fill="#232323")
        thumb=ImageOps.contain(im,(321,570),Image.Resampling.LANCZOS)
        output.paste(thumb,(x+(340-thumb.width)//2,y+37))
    image=root/(BASENAME+".jpg")
    output.save(image,"JPEG",quality=84,optimize=True)
    sm=root/(BASENAME+"-PREVIEW.jpg")
    small=ImageOps.contain(output,(1030,640),Image.Resampling.LANCZOS)
    small.save(sm,"JPEG",quality=72,optimize=True)
    result={
        "schema":"videoforge/ep01-c01p04-v3-provisional-clean-recomposition/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "approved_original_mother_sha256":"a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd",
        "mother_technical_reference_sha256":SOURCE,
        "clean_background_sha256":bginfo["sha256"],
        "kael_sha256":kinf["sha256"],
        "sources_are_independent_proxy_images":True,
        "comparisons":records,
        "full_board":image.name,"full_board_sha256":sha256(image.read_bytes()).hexdigest(),
        "preview_board":sm.name,"preview_sha256":sha256(sm.read_bytes()).hexdigest(),
        "spears_in_preview":False,"parts_are_native_pixels_preserved":True,
        "resample_applied_to_original_PNGs":False,
        "image_provider_calls":0,"auto_visual_approval":False,
        "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False,
        "next":"Compare orientation and costume; then solve exact pole-to-hand contacts with 2 independent spears",
    }
    (root/(BASENAME+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_C01P04_CLEAN_COMPOSITE_QA",json.dumps({
        "variants":[x["id"] for x in records],"provider_calls":0,"rig_ready":False},ensure_ascii=False))
    return result

if __name__=="__main__":
    try:create()
    except (OSError,ValueError,RuntimeError) as e:
        print("EP01_CLEAN_COMPOSITION_FAILED",str(e),file=sys.stderr)
        sys.exit(2)
