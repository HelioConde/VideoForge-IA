#!/usr/bin/env python3
"""Compara frame original e camadas REAIS arquivadas do EP01 sem geração IA.

A camada reconstruída não é aprovada automaticamente, mesmo com diff baixo.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops, ImageStat

from videoforge.ep01_shot_layers import mother_source
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from videoforge.scene_layers import png_info

REGISTRY=ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
EXPECTED=[
    ("c01-p02-background-aligned","background"),
    ("c01-p02-character-carrasco","character"),
    ("c01-p02-object-bainha","object"),
    ("c01-p02-object-espada","object"),
]


def registered(asset:str, registry:dict, mother_sha:str)->tuple[Image.Image,dict]:
    rows=[x for x in registry["geracoes"] if x.get("asset")==asset]
    if len(rows)!=1:
        raise ValueError("EP01_RECOMPOSITION_REQUIRES_UNIQUE_ASSET "+asset)
    row=rows[0]
    rel=Path(row["arquivo"])
    if (rel.is_absolute() or ".." in rel.parts
            or not rel.is_relative_to(REL/"assets"/"geracoes")):
        raise ValueError("EP01_RECOMPOSITION_UNSAFE_SOURCE")
    path=ROOT/rel
    if path.is_symlink() or not path.is_file() or path.stat().st_size>35_000_000:
        raise ValueError("EP01_RECOMPOSITION_MISSING_LAYER "+asset)
    binary=path.read_bytes()
    if hashlib.sha256(binary).hexdigest()!=row["sha256"]:
        raise ValueError("EP01_RECOMPOSITION_LAYER_SHA_MISMATCH")
    proof=path.with_suffix(".production.json")
    if not proof.is_file() or proof.is_symlink():
        raise ValueError("EP01_RECOMPOSITION_PROVENANCE_REQUIRED")
    metadata=json.loads(proof.read_text(encoding="utf-8"))
    if asset=="c01-p02-background-aligned":
        if metadata.get("source_mother_sha256")!=mother_sha:
            raise ValueError("EP01_RECOMPOSITION_ALIGNED_MOTHER_SHA_MISMATCH")
    else:
        if metadata.get("source_mother_sha256")!=mother_sha:
            raise ValueError("EP01_RECOMPOSITION_LAYER_MOTHER_SHA_MISMATCH")
        if not str(metadata.get("technical_qa","")).startswith("candidate_"):
            raise ValueError("EP01_RECOMPOSITION_REJECTED_OR_UNCHECKED_LAYER")
    with Image.open(io.BytesIO(binary)) as im:
        if im.format!="PNG":
            raise ValueError("EP01_RECOMPOSITION_IMAGE_NOT_PNG")
        result=im.convert("RGBA")
    if (result.width,result.height)!=(row["width"],row["height"]):
        raise ValueError("EP01_RECOMPOSITION_IMAGE_DIMENSIONS_INVALID")
    return result,row


def build()->dict:
    plan,mother_raw,source_info=mother_source()
    with Image.open(io.BytesIO(mother_raw)) as im:
        mother=im.convert("RGB")
    registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
    layers={}
    records={}
    for asset,typ in EXPECTED:
        layer,row=registered(asset,registry,plan["mother_sha256"])
        if (layer.width,layer.height)!=(mother.width,mother.height):
            raise ValueError("EP01_RECOMPOSITION_CANVAS_NOT_ALIGNED "+asset)
        pixels=png_info((ROOT/row["arquivo"]).read_bytes(),require_alpha=(typ!="background"))
        layers[asset]=layer
        records[asset]={"sha256":row["sha256"],"run_id":row["github_run_id"],
                        "alpha_zero_fraction":pixels.get("alpha_zero_fraction")}
    base=layers["c01-p02-background-aligned"].copy()
    for asset in ("c01-p02-character-carrasco","c01-p02-object-bainha","c01-p02-object-espada"):
        base=Image.alpha_composite(base,layers[asset])
    recon=base.convert("RGB")
    difference=ImageChops.difference(mother,recon)
    stat=ImageStat.Stat(difference)
    mean_delta=round(sum(stat.mean)/len(stat.mean),3)
    mag=ImageOps.autocontrast(difference)
    tiles=[("CENA-MÃE ORIGINAL",mother),("RGBAs RECOMPOSTOS",recon),("DIFERENÇA AMPLIADA",mag)]
    target_size=(345,614)
    width,height=3*360+20,700
    sheet=Image.new("RGB",(width,height),"#f2f2f2")
    pen=ImageDraw.Draw(sheet)
    for i,(title,panel) in enumerate(tiles):
        x=10+i*360
        pen.text((x+4,14),title,fill="#262626",font=ImageFont.load_default())
        thumb=ImageOps.contain(panel,target_size,Image.Resampling.LANCZOS)
        sheet.paste(thumb,(x+(345-thumb.width)//2,45))
    pen.text((12,665),f"QA TECNICO | DIFF MEDIO RGB {mean_delta:.2f}/255 | NAO APROVADO AUTOMATICAMENTE",
             fill="#454545",font=ImageFont.load_default())
    out=ROOT/REL/"QA-C01-P02-RECOMPOSICAO.jpg"
    buffer=io.BytesIO()
    sheet.save(buffer,"JPEG",quality=80,optimize=True)
    jpg=buffer.getvalue()
    if not out.exists() or out.read_bytes()!=jpg:
        out.write_bytes(jpg)
    report={
        "schema":"videoforge/ep01-recomposition-qa/v1",
        "shot_id":"C01-P02","source_mother_sha256":plan["mother_sha256"],
        "source_native_pixels":[mother.width,mother.height],
        "layers":records,
        "mean_absolute_rgb_diff":mean_delta,
        "provenance_sha_checked":True,"alpha_channels_checked":True,
        "pixel_alignment_verified":True,
        "sword_grip_physical_contact_verified":False,
        "rig_completed":False,"human_visual_approval":False,
        "visual_review":"required_not_automatic",
        "mp4_generated":False,"youtube_uploaded":False,
        "preview_jpg_sha256":hashlib.sha256(jpg).hexdigest(),
    }
    report_path=ROOT/REL/"QA-C01-P02-RECOMPOSICAO.json"
    data=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if not report_path.exists() or report_path.read_text(encoding="utf-8")!=data:
        report_path.write_text(data,encoding="utf-8")
    print("EP01_RECOMPOSITION_REAL_LAYERS_QA",json.dumps({
        "source_sha256":plan["mother_sha256"],"mean_delta":mean_delta,
        "layers":list(records),"human_approved":False
    },ensure_ascii=False))
    return report


if __name__=="__main__":
    build()
