"""Read-only visual review sheet for independently generated C01-P04 grip V3.

Makes no pixel cutouts as final assets, no masks for rig and no approvals.
It uses only exact-SHA original assets and already-archived generated parts.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from PIL import Image,ImageOps,ImageDraw,ImageFont
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge import ep01_c01p04_grip_v3 as grip
from videoforge.ep01_approved_v3_parts import aligned_source

BASENAME="QA-C01-P04-V3-ANATOMIA-PEGADA"
BOARD_SIZE=(1070,710)
def font(s):
    try:return ImageFont.truetype("DejaVuSans.ttf",s)
    except OSError:return ImageFont.load_default()

def review(role):
    old=grip.archive(role)
    if not old:
        return None
    rel=Path(old["file"])
    if not rel.is_relative_to(REL/"assets"/"geracoes") or ".." in rel.parts:
        raise ValueError("GRIP_V3_QA_UNSAFE_FILE")
    file=ROOT/rel
    proof=file.with_suffix(".production.json")
    data=file.read_bytes()
    doc=json.loads(proof.read_text(encoding="utf-8"))
    if (sha256(data).hexdigest()!=old["sha256"]
        or doc.get("sha256")!=old["sha256"]
        or doc.get("schema")!=grip.SCHEMA
        or doc.get("role")!=role
        or doc.get("source_image_sha256")!=grip.ALIGNED_SHA
        or doc.get("grip_guide_reference_sha256")!=grip.GUIDE_SHA
        or doc.get("anatomical_component_visual_approved") is not False
        or doc.get("rig_ready") is not False):
        raise ValueError("GRIP_V3_QA_BAD_PROVENANCE")
    with Image.open(BytesIO(data)) as im:
        im.load()
        if im.format!="PNG":
            raise ValueError("GRIP_V3_QA_BAD_PNG")
        art=im.convert("RGBA")
    return {"role":role,"source":old,"proof":doc,"image":art}

def picture(img,caption,w=335,h=570,checkered=False):
    tile=Image.new("RGB",(w,h),"#ffffff")
    d=ImageDraw.Draw(tile)
    d.text((10,7),caption[:42],fill="#111111",font=font(15))
    if checkered:
        board=Image.new("RGBA",(w-20,h-55),"#efefef")
        bd=ImageDraw.Draw(board)
        for yy in range(0,board.height,24):
            for xx in range(0,board.width,24):
                if (xx//24+yy//24)%2==0:
                    bd.rectangle((xx,yy,xx+23,yy+23),fill="#dedede")
        thumb=ImageOps.contain(img,(board.width,board.height),Image.Resampling.LANCZOS)
        board.alpha_composite(thumb,((board.width-thumb.width)//2,
                                   (board.height-thumb.height)//2))
        tile.paste(board.convert("RGB"),(10,40))
    else:
        thumb=ImageOps.contain(img.convert("RGB"),(w-20,h-55),Image.Resampling.LANCZOS)
        tile.paste(thumb,((w-thumb.width)//2,40))
    return tile

def main():
    ref=aligned_source()
    if ref["sha256"]!=grip.ALIGNED_SHA:
        raise ValueError("GRIP_V3_QA_MOTHER_CHANGED")
    with Image.open(BytesIO(ref["blob"])) as i:
        approved=i.convert("RGB").crop((0,760,375,1230))
    guide=grip.reference(ROOT,grip.GUIDE_FILE,grip.GUIDE_SHA)
    with Image.open(BytesIO(guide)) as i:
        canonical=i.convert("RGB")
    records=[]
    available=[x for x in (review(r) for r in grip.ROLES) if x is not None]
    if not available:
        raise ValueError("GRIP_V3_QA_NO_NEW_PARTS")
    for entry in available:
        role=entry["role"];img=entry["image"]
        canvas=Image.new("RGB",BOARD_SIZE,"#e9e9e8")
        pen=ImageDraw.Draw(canvas)
        pen.text((12,10),"C01-P04 V3 / QA CAMADA "+role.upper(),font=font(22),fill="#181818")
        pen.text((12,42),"REFERENCIAS A ESQUERDA; NOVO PNG A DIREITA; NENHUM RIG APROVADO",
                 font=font(13),fill="#a53626")
        first=picture(approved,"MÃE APROVADA - PEGADA")
        second=picture(canonical,"GUIA DE ANATOMIA (CANDIDATO)")
        third=picture(img,"GERAÇÃO V3 / "+role,checkered=True)
        for col,pic in enumerate((first,second,third)):
            canvas.paste(pic,(12+col*352,90))
        dest=ROOT/REL/(BASENAME+"-"+role.upper()+".jpg")
        canvas.save(dest,"JPEG",quality=85,optimize=True)
        meta=entry["proof"]
        records.append({
            "role":role,
            "source_file":entry["source"]["file"],
            "source_sha256":entry["source"]["sha256"],
            "technical_qa":meta["technical_qa"],
            "native_canvas":[img.width,img.height],
            "alpha_bbox_xyxy":meta["alpha_bbox_xyxy"],
            "likely_oversized_bbox_warning":meta["likely_oversized_native_bbox_warning"],
            "review_sheet":dest.name,
            "review_sheet_sha256":sha256(dest.read_bytes()).hexdigest(),
            "human_visual_approved":False,
            "rig_ready":False,
        })
    report={
        "schema":"videoforge/ep01-c01p04-grip-v3-review/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "creator_approved_original_sha256":grip.APPROVED_SHA,
        "approved_aligned_sha256":grip.ALIGNED_SHA,
        "guide_not_approved_as_final_sha256":grip.GUIDE_SHA,
        "parts":records,"all_parts_generated":len(records)==3,
        "requires_manual_visual_review":True,
        "checks":["armour matches source (no extra fingers)",
                  "palm sits behind shaft; must be a PALM, not a tube",
                  "front fingertips and thumb wrap across a real spear",
                  "consistent spatial anchors, hand and shaft contact",
                  "avoid duplicated knuckles and gaps in frame sequence"],
        "automatic_rig_ready":False,"human_visual_approval":False,
        "model_calls":0,"mp4_generated":False,"youtube_uploaded":False
    }
    file=ROOT/REL/(BASENAME+".json")
    file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GRIP_V3_REVIEW",json.dumps({"parts":[x["role"] for x in records],
       "rig_ready":False,"new_model_calls":0},ensure_ascii=False))
    return report

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,RuntimeError) as e:
        print("GRIP_V3_REVIEW_FAILED",str(e),file=sys.stderr)
        sys.exit(2)
