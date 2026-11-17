#!/usr/bin/env python3
"""Prévia de registro/encaixe de bainha por translação pura; nenhuma IA paga.

A entrada bruta RGBA é preservada. Não reduz ou aumenta nenhum pixel;
apenas demonstra alternativas de pivô/posição no quadro da cena-mãe.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

from videoforge.layered_shot_plan import ROOT, REL
from videoforge.ep01_shot_layers import mother_source

SOURCE_NAMES=[
("c01-p02-background-aligned","background"),
("c01-p02-character-carrasco","character"),
("c01-p02-object-espada","sword"),
("c01-p02-object-bainha","scabbard"),
]
OFFSETS=[(0,300),(0,500),(0,650),(0,800),(-80,650),(80,650)]

def img_for(asset,registry):
    items=[x for x in registry["geracoes"] if x.get("asset")==asset]
    if len(items)!=1: raise ValueError("REGISTER_SOURCE_MISSING "+asset)
    r=items[0]
    p=Path(r["arquivo"])
    if (p.is_absolute() or ".." in p.parts or
        not p.is_relative_to(REL/"assets"/"geracoes")):
        raise ValueError("REGISTER_UNSAFE_PATH")
    f=ROOT/p
    if f.is_symlink() or not f.is_file():raise ValueError("REGISTER_UNSAFE_FILE")
    raw=f.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=r["sha256"]:
        raise ValueError("REGISTER_TAMPERED_SOURCE")
    with Image.open(io.BytesIO(raw)) as i:
        if i.format!="PNG":raise ValueError("REGISTER_NOT_PNG")
        return i.convert("RGBA"),r

def main():
    mother_info,mother_raw,can=mother_source()
    with Image.open(io.BytesIO(mother_raw)) as im:
        mother=im.convert("RGBA")
    doc=json.loads((ROOT/"canal/alchemy-lab/biblia-visual/REGISTRO-GERACOES.json").read_text())
    assets={}
    records={}
    for name,key in SOURCE_NAMES:
        assets[key],records[key]=img_for(name,doc)
    w,h=mother.size
    for k in ("background","character","sword"):
        if assets[k].size!=(w,h):raise ValueError("REGISTER_SOURCE_NOT_NATIVE")
    if assets["scabbard"].size!=(981,1602):
        raise ValueError("REGISTER_UNEXPECTED_REJECTED_SCABBARD_SIZE")
    colw,rowh=335,625
    out=Image.new("RGB",(3*colw+24,3*rowh+65),"#eaeaea")
    draw=ImageDraw.Draw(out)
    draw.text((13,7),"C01-P02 • REGISTRO BAINHA | SEM RESIZE, SOMENTE TRANSLACAO",fill="#222222")
    def put(panel,label,index):
        x=12+(index%3)*colw
        y=32+(index//3)*rowh
        thumbnail=ImageOps.contain(panel.convert("RGB"),(315,575),Image.Resampling.LANCZOS)
        out.paste(thumbnail,(x+(315-thumbnail.width)//2,y+24))
        draw.text((x+2,y+3),label,fill="#222222")
    put(mother,"CENA-MAE ORIGINAL (OBJETIVO)",0)
    bare=Image.alpha_composite(assets["background"],assets["character"])
    bare=Image.alpha_composite(bare,assets["sword"])
    put(bare,"SEM BAINHA (BASE DA QA)",1)
    for i,(dx,dy) in enumerate(OFFSETS):
        layer=Image.new("RGBA",(w,h),(0,0,0,0))
        layer.paste(assets["scabbard"],(dx,dy))
        frame=Image.alpha_composite(assets["background"],layer)
        frame=Image.alpha_composite(frame,assets["character"])
        frame=Image.alpha_composite(frame,assets["sword"])
        put(frame,f"BAINHA: deslocamento ({dx},{dy}) / sem escala",i+2)
    pen="Posicoes para analise, nao arte aprovada. PNG bruto e SHAs originais preservados."
    draw.text((12,out.height-30),pen,fill="#8c3030")
    io_bytes=io.BytesIO()
    out.save(io_bytes,"JPEG",quality=84,optimize=True)
    raw=io_bytes.getvalue()
    target=ROOT/REL/"QA-C01-P02-REGISTRO-BAINHA.jpg"
    if not target.is_file() or target.read_bytes()!=raw:
        target.write_bytes(raw)
    qa={
        "schema":"videoforge/ep01-scabbard-registration-preview/v1",
        "mother_sha256":mother_info["mother_sha256"],
        "scabbard_raw_sha256":records["scabbard"]["sha256"],
        "scabbard_source_canvas":list(assets["scabbard"].size),
        "target_scene_canvas":[w,h],
        "offset_trials":OFFSETS,"no_resampling_of_original_layer":True,
        "png_sources_intact":True,"visual_review_pending":True,
        "registered_layer_saved":False,"rig_applied":False,"youtube_uploaded":False,
        "jpg_sha256":hashlib.sha256(raw).hexdigest()
    }
    j=target.with_suffix(".json")
    content=json.dumps(qa,indent=2,ensure_ascii=False)+"\n"
    if not j.is_file() or j.read_text(encoding="utf-8")!=content:j.write_text(content,encoding="utf-8")
    print("EP01_SCABBARD_OFFSETS_PREVIEW",json.dumps({"offsets":OFFSETS,"no_proxy_calls":True}))

if __name__=="__main__":
    main()
