#!/usr/bin/env python3
"""Prancha V3 sem imagens antigas rejeitadas confundindo aprovação.

Mostra origem exata, revisão do proxy e patch local (se compatível),
além de closes de contato mão / bocal / bainha. Apenas candidatos.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps, ImageChops, ImageStat
from videoforge.ep01_shot_layers import mother_source
from videoforge.ep01_contact_repair import (ASSET, PATCH_ASSET, ROI,
                                           EXPECTED_MOTHER_SHA, PRODUCER)
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

REGISTER=ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
EPISODE=ROOT/REL


def registered(asset:str, registry:dict)->tuple[Image.Image,dict]:
    rows=[x for x in registry["geracoes"] if x.get("asset")==asset]
    if len(rows)!=1:
        raise RuntimeError("EP01_V3_CANDIDATE_MISSING_OR_DUPLICATED "+asset)
    row=rows[0]
    rel=Path(row["arquivo"])
    if (rel.is_absolute() or ".." in rel.parts
        or not rel.is_relative_to(REL/"assets"/"geracoes"/PRODUCER)):
        raise RuntimeError("EP01_V3_ASSET_OUTSIDE_ARCHIVE")
    path=ROOT/rel
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("EP01_V3_SOURCE_NOT_FILE")
    blob=path.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=row["sha256"]:
        raise RuntimeError("EP01_V3_ARCHIVE_SHA_MISMATCH")
    proof=json.loads(path.with_suffix(".production.json").read_text(encoding="utf-8"))
    if (proof["sha256"]!=row["sha256"] or
        proof.get("source_mother_sha256")!=EXPECTED_MOTHER_SHA or
        proof.get("human_visual_approval") is not False):
        raise RuntimeError("EP01_V3_PROVENANCE_OR_APPROVAL_INVALID")
    with Image.open(io.BytesIO(blob)) as im:
        if im.format!="PNG":raise RuntimeError("EP01_V3_NOT_PNG")
        im=im.convert("RGB")
    return im.copy(),row


def build():
    doc,raw,info=mother_source()
    if doc["mother_sha256"]!=EXPECTED_MOTHER_SHA:
        raise RuntimeError("EP01_V3_MOTHER_SOURCE_CHANGED")
    with Image.open(io.BytesIO(raw)) as i:
        mother=i.convert("RGB")
    registry=json.loads(REGISTER.read_text(encoding="utf-8"))
    edited,edited_meta=registered(ASSET,registry)
    has_patch=any(x.get("asset")==PATCH_ASSET for x in registry["geracoes"])
    patch=None
    patch_meta=None
    if has_patch:
        patch,patch_meta=registered(PATCH_ASSET,registry)
        if patch.size!=mother.size:
            raise RuntimeError("EP01_V3_PATCH_NOT_NATIVE_SIZE")
    same_canvas=edited.size==mother.size
    metrics={"parent_sha256":EXPECTED_MOTHER_SHA,
             "edit_sha256":edited_meta["sha256"],
             "patch_sha256":patch_meta["sha256"] if patch_meta else None,
             "source_size":list(mother.size),"candidate_size":list(edited.size),
             "same_canvas":same_canvas,
             "patch_exists":bool(patch),
             "source_not_overwritten":True,
             "owner_rejected_panels":[2,4],
             "human_approved":False,"rig_ready":False,
             "mp4_generated":False,"youtube_uploaded":False}
    if patch is not None:
        delta=ImageChops.difference(patch,mother)
        metrics["mean_rgb_difference_from_source"]=round(sum(ImageStat.Stat(delta).mean)/3,4)
        exterior=Image.new("L",mother.size,255)
        ImageDraw.Draw(exterior).rectangle(ROI,fill=0)
        spill=ImageChops.multiply(delta.convert("L"),exterior)
        metrics["exact_original_rgb_outside_roi"]=spill.getbbox() is None
        if not metrics["exact_original_rgb_outside_roi"]:
            raise RuntimeError("EP01_V3_PATCH_BLED_OUTSIDE_REGION")
    cx1,cy1,cx2,cy2=ROI
    original_crop=mother.crop(ROI)
    # Cropping new model output with same coordinates is only valid
    # for identical canvas dimensions; otherwise show independent full image.
    edited_crop=edited.crop(ROI) if same_canvas else edited
    patch_crop=patch.crop(ROI) if patch else None
    tiles=[
      ("FONTE V1: CONTATO REPROVADO",mother),
      ("EDIÇÃO V3: CANDIDATA",edited),
      ("PATCH LOCAL V3: EM REVISÃO" if patch else "PATCH AUSENTE: CANVAS DIFERENTE",
       patch if patch else Image.new("RGB",mother.size,"#c6c6c6")),
      ("CLOSE ORIGINAL: REPROVADO",original_crop),
      ("CLOSE EDIÇÃO V3: EM REVISÃO",edited_crop),
      ("CLOSE PATCH V3: EM REVISÃO" if patch_crop else "CLOSE PATCH NÃO GERADO",
       patch_crop if patch_crop else Image.new("RGB",original_crop.size,"#c6c6c6"))
    ]
    tw,th=395,690
    board=Image.new("RGB",(3*tw+36,2*th+90),"#efefef")
    draw=ImageDraw.Draw(board)
    draw.text((15,12),"C01-P02 / REVISÃO DE CONTATO V3 — SEM POSES OU DESLOCAMENTOS",fill="#222")
    for i,(caption,img) in enumerate(tiles):
        x=15+(i%3)*tw
        y=46+(i//3)*th
        draw.text((x,y),caption,fill="#642121" if "REPROVADO" in caption else "#222")
        thumbnail=ImageOps.contain(img,(tw-27,th-64),Image.Resampling.LANCZOS)
        board.paste(thumbnail,(x+(tw-27-thumbnail.width)//2,y+25))
    draw.text((15,board.height-30),
       "Aprovação visual e contato da bainha pendentes. Não usar para rig ou MP4.",
       fill="#8a2020")
    final=EPISODE/"QA-C01-P02-CONTATO-V3.jpg"
    board.save(final,"JPEG",quality=83,optimize=True)
    metrics.update({"schema":"videoforge/ep01-contact-v3-qa/v1",
         "preview_sha256":hashlib.sha256(final.read_bytes()).hexdigest(),
         "roi":list(ROI),"comparison_type":"same_scene_spatial_reference"})
    (EPISODE/"QA-C01-P02-CONTATO-V3.json").write_text(
       json.dumps(metrics,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_V3_CONTACT_PREVIEW",json.dumps(metrics,ensure_ascii=False))


if __name__=="__main__":
    build()
