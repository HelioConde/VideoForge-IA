#!/usr/bin/env python3
"""QA da espada original vs recorte do proxy, com oclusão de luvas correta.

Compara frame RGB sem converter ARTES candidatas em aprovadas.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageChops, ImageStat
from videoforge.ep01_shot_layers import mother_source
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from videoforge.ep01_source_sword import ASSET

REGISTER=ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
OUT=ROOT/"output"/CHANNEL/"videos"/VIDEO/"imagens"


def get_png(asset:str, registry:list)->Image.Image:
    rows=[r for r in registry if r.get("asset")==asset]
    if len(rows)!=1:raise RuntimeError("SWORD_QA_ASSET_NOT_UNIQUE "+asset)
    row=rows[0]
    path=Path(row["arquivo"])
    if path.is_absolute() or ".." in path.parts or not path.is_relative_to(REL/"assets"/"geracoes"):
        raise RuntimeError("SWORD_QA_INVALID_SOURCE_PATH")
    file=ROOT/path
    if file.is_symlink() or not file.is_file():raise RuntimeError("SWORD_QA_SOURCE_MISSING")
    blob=file.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=row["sha256"]:
        raise RuntimeError("SWORD_QA_SOURCE_TAMPERED")
    with Image.open(io.BytesIO(blob)) as im:
        return im.convert("RGBA")


def main():
    plan,raw,_=mother_source()
    with Image.open(io.BytesIO(raw)) as im:
        mother=im.convert("RGBA")
    registry=json.loads(REGISTER.read_text())["geracoes"]
    background=get_png("c01-p02-background-aligned",registry)
    actor=get_png("c01-p02-character-carrasco",registry)
    old_sword=get_png("c01-p02-object-espada",registry)
    sheath=get_png("c01-p02-object-bainha-source-visible",registry)
    hand_upper=get_png("c01-p02-hand-upper-contact-occlusion",registry)
    hand_lower=get_png("c01-p02-hand-lower-contact-occlusion",registry)
    sword_file=OUT/(ASSET+".png")
    sword_meta=OUT/(ASSET+".production.json")
    proof=json.loads(sword_meta.read_text(encoding="utf-8"))
    blob=sword_file.read_bytes()
    if (proof["sha256"]!=hashlib.sha256(blob).hexdigest() or
        proof["source_mother_sha256"]!=plan["mother_sha256"]):
        raise RuntimeError("SWORD_QA_NEW_SOURCE_SHA_INVALID")
    with Image.open(io.BytesIO(blob)) as im:
        newsword=im.convert("RGBA")
    if any(im.size!=mother.size for im in (
        background,actor,old_sword,sheath,hand_upper,hand_lower,newsword)):
        raise RuntimeError("SWORD_QA_CANVAS_CHANGED")
    def compose(sword:Image.Image):
        # Mãos NO TOPO. São pixels da fonte, não a espada recortada pela IA.
        full=Image.alpha_composite(background,sheath)
        full=Image.alpha_composite(full,sword)
        full=Image.alpha_composite(full,actor)
        full=Image.alpha_composite(full,hand_upper)
        full=Image.alpha_composite(full,hand_lower)
        return full
    old=compose(old_sword)
    new=compose(newsword)
    target=mother.convert("RGB")
    old_err=ImageChops.difference(target,old.convert("RGB"))
    new_err=ImageChops.difference(target,new.convert("RGB"))
    old_mean=round(sum(ImageStat.Stat(old_err).mean)/3,3)
    new_mean=round(sum(ImageStat.Stat(new_err).mean)/3,3)
    check=Image.new("RGBA",mother.size,(190,193,199,255))
    visible=Image.alpha_composite(check,newsword)
    diff=ImageOps.autocontrast(new_err)
    items=[
        ("01 / ORIGINAL (REFERÊNCIA)",mother),
        ("02 / ESPADA DO PROXY (ANTES)",old_sword),
        ("03 / ESPADA RECORTADA DA MÃE",visible),
        ("04 / COMPOSTO ANTIGO (REJEITADO)",old),
        ("05 / COMPOSTO NOVO (EM QA)",new),
        ("06 / DELTA DO COMPOSTO NOVO",diff),
    ]
    tw,th=392,720
    board=Image.new("RGB",(3*tw+26,2*th+77),"#efefef")
    painter=ImageDraw.Draw(board)
    painter.text((16,10),"C01-P02 / CONFERÊNCIA CONTATO: espada extraída da mesma mãe",fill="#222")
    for i,(label,art) in enumerate(items):
        xx=12+(i%3)*tw
        yy=38+(i//3)*th
        painter.text((xx,yy),label,fill="#222")
        thumbnail=ImageOps.contain(art.convert("RGB"),(tw-27,th-68),Image.Resampling.LANCZOS)
        board.paste(thumbnail,(xx+(tw-27-thumbnail.width)//2,yy+24))
    painter.text((14,board.height-28),
                 f"diff antigo {old_mean}/255 | diff novo {new_mean}/255. Nenhuma arte aprovada.",
                 fill="#9b3030")
    jpg=ROOT/REL/"QA-C01-P02-ESPADA-PIXELS.jpg"
    board.save(jpg,"JPEG",quality=83,optimize=True)
    report={
        "schema":"videoforge/ep01-source-sword-comparison/v1",
        "mother_sha256":plan["mother_sha256"],
        "sword_source_sha256":proof["sha256"],
        "rejected_old_sword_reference":"c01-p02-object-espada",
        "old_composite_mean_rgb_delta":old_mean,
        "new_composite_mean_rgb_delta":new_mean,
        "new_better_by_numeric_metric":new_mean<old_mean,
        "alpha_source_frame_native":True,
        "hands_final_z_order":True,
        "visual_approved":False,
        "rig_authorized":False,
        "finished_mp4":False,
        "youtube_uploaded":False,
        "image_provider_calls":0,
        "preview_sha256":hashlib.sha256(jpg.read_bytes()).hexdigest(),
    }
    (ROOT/REL/"QA-C01-P02-ESPADA-PIXELS.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_SOURCE_SWORD_QA",json.dumps(report))


if __name__=="__main__":
    main()
