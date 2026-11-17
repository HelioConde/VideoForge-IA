#!/usr/bin/env python3
"""Prancha auditável dos recortes por pixels da mãe; não aprova o rig.

Lê a mãe SHA-verificada, as camadas já existentes e os novos recortes;
verifica integridade RGB no núcleo dos recortes, guarda a oclusão real
das luvas POR CIMA da espada e bainha, e mede erro de recomposição.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps, ImageChops, ImageStat

from videoforge.ep01_contact_cutouts import (CONTACT_ORDER, EXPECTED_MOTHER_SHA)
from videoforge.ep01_shot_layers import mother_source
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

OUT=ROOT/REL
BASE=ROOT/"output"/CHANNEL/"videos"/VIDEO/"imagens"
REG=ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"


def load_registered(asset:str, rows:list)->Image.Image:
    entries=[row for row in rows if row.get("asset")==asset]
    if len(entries)!=1:
        raise RuntimeError("CONTACT_QA_ARCHIVE_MISSING_OR_MULTIPLE "+asset)
    row=entries[0]
    rel=Path(row["arquivo"])
    if rel.is_absolute() or ".." in rel.parts or not rel.is_relative_to(REL/"assets"/"geracoes"):
        raise RuntimeError("CONTACT_QA_PATH_UNSAFE")
    path=ROOT/rel
    if path.is_symlink() or not path.is_file() or path.stat().st_size>35_000_000:
        raise RuntimeError("CONTACT_QA_SOURCE_NOT_FILE")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=row["sha256"]:
        raise RuntimeError("CONTACT_QA_SOURCE_SHA_INVALID")
    with Image.open(io.BytesIO(raw)) as image:
        if image.format!="PNG":
            raise RuntimeError("CONTACT_QA_IMAGE_NOT_PNG")
        return image.convert("RGBA")


def main():
    source,mother_raw,canvas=mother_source()
    if source["mother_sha256"]!=EXPECTED_MOTHER_SHA:
        raise RuntimeError("CONTACT_QA_MOTHER_SHA_CHANGED")
    with Image.open(io.BytesIO(mother_raw)) as im:
        mother=im.convert("RGBA")
    rows=json.loads(REG.read_text(encoding="utf-8"))["geracoes"]
    archived={
        "background":load_registered("c01-p02-background-aligned",rows),
        "carrasco":load_registered("c01-p02-character-carrasco",rows),
        "espada":load_registered("c01-p02-object-espada",rows),
    }
    cutouts={}
    proofs={}
    for name in CONTACT_ORDER:
        stem="c01-p02-"+name
        path=BASE/(stem+".png")
        meta=BASE/(stem+".production.json")
        if not path.is_file() or not meta.is_file():
            raise RuntimeError("CONTACT_QA_NEW_SOURCE_MISSING "+name)
        record=json.loads(meta.read_text(encoding="utf-8"))
        raw=path.read_bytes()
        if (record.get("sha256")!=hashlib.sha256(raw).hexdigest() or
            record.get("source_mother_sha256")!=EXPECTED_MOTHER_SHA or
            record.get("visual_approval") is not False):
            raise RuntimeError("CONTACT_QA_NEW_SOURCE_SHA_OR_APPROVAL_INVALID")
        with Image.open(io.BytesIO(raw)) as im:
            if im.format!="PNG" or im.size!=mother.size:
                raise RuntimeError("CONTACT_QA_NEW_LAYER_NOT_NATIVE")
            part=im.convert("RGBA")
        # Os pixels de cores visíveis são os MESMOS da imagem aprovada como
        # referência pelo usuário, sem redesenho. Apenas ALFA é definido.
        rgb=part.convert("RGB")
        if ImageChops.difference(rgb,mother.convert("RGB")).getbbox() is not None:
            raise RuntimeError("CONTACT_QA_SOURCE_PIXELS_REDRAWN")
        cutouts[name]=part
        proofs[name]=record["mask_qa"]
    stack=archived["background"]
    stack=Image.alpha_composite(stack,cutouts["object-bainha-source-visible"])
    stack=Image.alpha_composite(stack,archived["espada"])
    stack=Image.alpha_composite(stack,archived["carrasco"])
    # Oclusão SEMPRE acima de espada/bainha e alinhada no lugar original.
    stack=Image.alpha_composite(stack,cutouts["hand-upper-contact-occlusion"])
    stack=Image.alpha_composite(stack,cutouts["hand-lower-contact-occlusion"])
    delta=ImageChops.difference(stack.convert("RGB"),mother.convert("RGB"))
    mean=round(sum(ImageStat.Stat(delta).mean)/3,3)
    contrast=ImageOps.autocontrast(delta)
    checker=Image.new("RGBA",mother.size,(190,194,200,255))
    sheath=Image.alpha_composite(checker,cutouts["object-bainha-source-visible"])
    hands=Image.alpha_composite(checker,cutouts["hand-upper-contact-occlusion"])
    hands=Image.alpha_composite(hands,cutouts["hand-lower-contact-occlusion"])
    all_masks=mother.convert("RGB").copy()
    border=ImageDraw.Draw(all_masks)
    # O contorno apenas existe nesta imagem de QA, NUNCA no PNG original.
    for name,color in (("object-bainha-source-visible","#4fd0a9"),
                       ("hand-upper-contact-occlusion","#f5a623"),
                       ("hand-lower-contact-occlusion","#e54650")):
        border.rectangle(proofs[name]["alpha_bbox"],outline=color,width=5)
    entries=[
        ("01 / MÃE ORIGINAL (REFERÊNCIA)",mother),
        ("02 / BAINHA: PIXEL DA MÃE",sheath),
        ("03 / LUVAS: FRENTE DA ESPADA",hands),
        ("04 / COMPOSTO DE TESTE (NÃO APROVADO)",stack),
        ("05 / ERRO DE RECOMPOSIÇÃO AMPLIADO",contrast),
        ("06 / BOUNDING BOXES DAS MÁSCARAS",all_masks),
    ]
    tile_w,tile_h=395,720
    preview=Image.new("RGB",(3*tile_w+30,2*tile_h+80),"#ededed")
    painter=ImageDraw.Draw(preview)
    painter.text((18,12),"C01-P02 / PIXELS REAIS + OCLUSÃO. IMAGENS ANTERIORES REJEITADAS.",
                 fill="#202020")
    for i,(label,part) in enumerate(entries):
        x=14+(i%3)*tile_w
        y=45+(i//3)*tile_h
        painter.text((x,y),label,fill="#242424")
        thumb=ImageOps.contain(part.convert("RGB"),(tile_w-24,tile_h-70),Image.Resampling.LANCZOS)
        preview.paste(thumb,(x+(tile_w-24-thumb.width)//2,y+25))
    painter.text((18,preview.height-26),
                 f"RGB diff médio: {mean}/255. Aprovação visual pendente. Sem MP4.",
                 fill="#9a2e2e")
    dst=OUT/"QA-C01-P02-CONTATO-PIXELS.jpg"
    preview.save(dst,"JPEG",quality=82,optimize=True)
    report={
        "schema":"videoforge/ep01-source-contact-comparison/v1",
        "shot_id":"C01-P02","mother_sha256":EXPECTED_MOTHER_SHA,
        "source_native_size":list(mother.size),
        "source_rgb_exact_core":True,"position":[0,0],"scale":1,
        "unmodified_sword_bainha_981x1602_rejected":True,
        "layer_order":["background-aligned","bainha-source-visible","espada-candidate",
                       "carrasco-candidate","upper-glove-source","lower-glove-source"],
        "masks":proofs,
        "rgb_composition_mean_absolute_diff":mean,
        "comparison_only":True,"human_visual_approval":False,
        "rig_done":False,"mp4_generated":False,"youtube_uploaded":False,
        "jpg_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
        "image_provider_calls":0,
    }
    (OUT/"QA-C01-P02-CONTATO-PIXELS.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CONTACT_QA_PIXEL_MASKS_PREVIEW",
          json.dumps({"mean_diff":mean,"source_sha":EXPECTED_MOTHER_SHA,
                      "not_approved":True,"provider_calls":0}))


if __name__=="__main__":
    main()
