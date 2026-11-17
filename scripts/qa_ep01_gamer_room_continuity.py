"""Independent visual QA contact sheet for the medieval-to-gamer-room cut.

No AI calls; previews are for QA only and never generate sprites/rig.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageOps
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

SHOTS=["C03-P01","C03-P02","C04-P01","C04-P02"]
LABELS=[
"C03-P01 | reflexo azul na iris",
"C03-P02 | match cut ao monitor",
"C04-P01 | Kael no quarto, mouse/teclado",
"C04-P02 | monitor e interface posterior"
]
SCHEMA="videoforge/ep01-gamer-room-qa/v1"


def build()->dict:
    reg=ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
    j=json.loads(reg.read_text(encoding="utf-8"))
    entries=j["geracoes"]
    rows=[]
    image_list=[]
    for shot,label in zip(SHOTS,LABELS):
        ident=shot.lower()+"-scene-mother"
        results=[x for x in entries if x.get("asset")==ident
                 and "/production-scene-mother-v2/" in str(x.get("arquivo",""))]
        if len(results)!=1:
            raise RuntimeError("EP01_GAMER_QA_MOTHER_NOT_UNIQUE "+shot)
        row=results[0]
        rel=Path(row["arquivo"])
        if (rel.is_absolute() or ".." in rel.parts or
            not rel.is_relative_to(REL/"assets"/"geracoes"/"production-scene-mother-v2")):
            raise RuntimeError("EP01_GAMER_QA_PATH_UNSAFE "+shot)
        path=ROOT/rel
        proof=path.with_suffix(".production.json")
        if (path.is_symlink() or proof.is_symlink() or
            not path.is_file() or not proof.is_file()):
            raise RuntimeError("EP01_GAMER_QA_SOURCE_MISSING "+shot)
        blob=path.read_bytes()
        report=json.loads(proof.read_text(encoding="utf-8"))
        digest=sha256(blob).hexdigest()
        if (digest!=row.get("sha256") or report.get("sha256")!=digest or
            report.get("human_visual_approval") is not False):
            raise RuntimeError("EP01_GAMER_QA_SHA_INVALID "+shot)
        with Image.open(BytesIO(blob)) as img:
            if img.format!="PNG":
                raise RuntimeError("EP01_GAMER_QA_NOT_PNG "+shot)
            pic=img.convert("RGB").copy()
        rows.append({"shot_id":shot,"sha256":digest,"path":rel.as_posix(),
                     "size":[pic.width,pic.height],
                     "technical_png_ok":True,"human_visual_approval":False})
        image_list.append((label,pic))
    tile_w,tile_h=510,880
    canvas=Image.new("RGB",(2*tile_w+34,2*tile_h+90),"#edeae5")
    pen=ImageDraw.Draw(canvas)
    pen.text((18,12),"DORAMA EP01 | IRIS AZUL -> QUARTO GAMER -> MONITOR",fill="#1a1a1a")
    for k,(title,img) in enumerate(image_list):
        col=k%2
        row=k//2
        x=18+col*tile_w
        y=58+row*tile_h
        pen.text((x,y),title,fill="#202020")
        thumb=ImageOps.contain(img,(tile_w-30,tile_h-75),Image.Resampling.LANCZOS)
        canvas.paste(thumb,(x+(tile_w-30-thumb.width)//2,y+28))
    pen.text((20,canvas.height-32),
             "QA de continuidade de cena; sem sprites recortados, sem aprovacoes de rig.",
             fill="#9b2828")
    out=ROOT/REL/"QA-C03-C04-CONTINUIDADE-QUARTO.jpg"
    canvas.save(out,"JPEG",quality=84,optimize=True)
    data={
        "schema":SCHEMA,
        "shots":rows,
        "sheet":"QA-C03-C04-CONTINUIDADE-QUARTO.jpg",
        "sheet_sha256":sha256(out.read_bytes()).hexdigest(),
        "checks_for_review":[
          "C03-P01 eyes blue reflection matches C03-P02 blue monitor light",
          "C03-P02 scene uses bedroom not medieval throne",
          "Kael casual outfit and face match C04-P01 and visual bible",
          "room architecture, desk, monitor and illumination remain consistent",
          "hand actually grips mouse and rests on keyboard with plausible anatomy",
          "C04-P02 monitor screen has no AI-painted UI/text",
          "match-cut is two consecutive shots, not split-screen collage"
        ],
        "technical_provenance_qa":"passed",
        "visual_continuity_qa":"awaiting_review",
        "human_visual_approval":False,
        "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False,
        "provider_calls":0
    }
    (ROOT/REL/"QA-C03-C04-CONTINUIDADE-QUARTO.json").write_text(
        json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_GAMER_ROOM_QA",json.dumps({
        "shots":len(rows),"sha":data["sheet_sha256"],"human_approved":False,
        "paid_calls":0},ensure_ascii=False))
    return data


if __name__=="__main__":
    try:
        build()
    except (RuntimeError,ValueError,OSError) as exc:
        print("EP01_GAMER_ROOM_QA_BLOCKED",str(exc),file=sys.stderr)
        raise SystemExit(2)
