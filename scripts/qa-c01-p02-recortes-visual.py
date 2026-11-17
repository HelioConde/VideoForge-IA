#!/usr/bin/env python3
"""Prancha de comparação sem chamadas de IA ou resize dos arquivos originais.

A visualização miniaturiza cópias temporárias para inspeção; nunca corrige,
aprova ou sobrescreve os PNGs originais.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFont
from videoforge.layered_shot_plan import ROOT, REL
from videoforge.ep01_shot_layers import mother_source

REGISTRY=ROOT/"canal/alchemy-lab/biblia-visual/REGISTRO-GERACOES.json"
ASSETS=[
("c01-p02-scene-mother","COMPOSIÇÃO COMPLETA"),
("c01-p02-background-aligned","BACKGROUND ALINHADO"),
("c01-p02-character-carrasco","CARRASCO RGBA"),
("c01-p02-object-espada","ESPADA RGBA"),
("c01-p02-object-bainha","BAINHA BRUTA REJEITADA"),
]

def main():
    reg=json.loads(REGISTRY.read_text(encoding="utf-8"))
    motherdoc,mother,info=mother_source()
    tile_w,tile_h=390,700
    sheet=Image.new("RGB",(tile_w*3+60,tile_h*2+90),"#ededed")
    pen=ImageDraw.Draw(sheet)
    font=ImageFont.load_default()
    pen.text((20,12),"C01-P02 RECORTES REAIS / INSPEÇÃO NÃO APROVA ARTES",font=font,fill="#222")
    report={"schema":"videoforge/ep01-cutouts-visual-qa/v1",
            "mother_sha256":motherdoc["mother_sha256"],"native_canvas":[info["width"],info["height"]],
            "compositing_claim":False,"human_visual_approval":False,"layers":[]}
    for i,(asset,title) in enumerate(ASSETS):
        rows=[x for x in reg["geracoes"] if x.get("asset")==asset]
        if len(rows)!=1: raise ValueError("QA_C01_P02_ASSET_MISSING_OR_DUPLICATED "+asset)
        row=rows[0]
        rel=Path(row["arquivo"])
        if (rel.is_absolute() or ".." in rel.parts or
            not rel.is_relative_to(REL/"assets"/"geracoes")):
            raise ValueError("QA_C01_P02_SOURCE_PATH_INVALID")
        source=ROOT/rel
        if source.is_symlink() or not source.is_file() or source.stat().st_size>35_000_000:
            raise ValueError("QA_C01_P02_SOURCE_FILE_UNSAFE")
        raw=source.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row["sha256"]:
            raise ValueError("QA_C01_P02_SOURCE_SHA_INVALID")
        with Image.open(io.BytesIO(raw)) as img:
            image=img.convert("RGBA")
        bbox=image.getchannel("A").getbbox()
        if image.mode!="RGBA":raise ValueError("IMPOSSIBLE")
        if i>1:
            panel=Image.new("RGBA",image.size,(205,208,211,255))
            # Alto contraste suficiente para perceber pixels transparentes.
            panel=Image.alpha_composite(panel,image).convert("RGB")
        else:
            panel=image.convert("RGB")
        thumbnail=ImageOps.contain(panel,(tile_w-22,tile_h-97),Image.Resampling.LANCZOS)
        column,row_i=i%3,i//3
        x=20+column*(tile_w+10)
        y=48+row_i*tile_h
        pen.text((x,y),title,font=font,fill="#1c1c1c")
        sheet.paste(thumbnail,(x+(tile_w-22-thumbnail.width)//2,y+23))
        pen.text((x,y+645),f"CANVAS {image.width}x{image.height}  SHA {row['sha256'][:16]}...",font=font,fill="#3b3b3b")
        pen.text((x,y+665),f"ALPHA BBOX: {bbox}",font=font,fill="#3b3b3b")
        report["layers"].append({"asset":asset,"sha256":row["sha256"],
                                 "size":[image.width,image.height],
                                 "alpha_bbox":list(bbox) if bbox else None,
                                 "native_canvas_match":(image.width,image.height)==
                                     (info["width"],info["height"])})
    pen.text((20,sheet.height-30),"BAINHA: imagem bruta preservada, 981x1602 vs 941x1672; SEM ALIGNMENT AUTOMÁTICO.",fill="#9b2525",font=font)
    target=ROOT/REL/"QA-C01-P02-RECORTES.jpg"
    buffer=io.BytesIO()
    sheet.save(buffer,"JPEG",quality=82,optimize=True)
    jpg=buffer.getvalue()
    if not target.is_file() or target.read_bytes()!=jpg:
        target.write_bytes(jpg)
    report["preview_sha256"]=hashlib.sha256(jpg).hexdigest()
    doc=target.with_suffix(".json")
    content=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if not doc.is_file() or doc.read_text(encoding="utf-8")!=content:
        doc.write_text(content,encoding="utf-8")
    print("EP01_CUTOUTS_PREVIEW_QA",json.dumps({"source":"sha_verified",
         "native_canvas_match":{r["asset"]:r["native_canvas_match"] for r in report["layers"]},
         "bainha_bbox":report["layers"][-1]["alpha_bbox"],
         "no_image_calls":True}))

if __name__=="__main__":
    main()
