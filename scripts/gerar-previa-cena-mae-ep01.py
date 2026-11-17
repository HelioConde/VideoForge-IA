#!/usr/bin/env python3
"""Prévia JPG real de frame de cena-mãe arquivado, sem geração nem aprovação."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
EP = Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
BIBLE = ROOT / "canal/alchemy-lab/biblia-visual"


def main():
    doc=json.loads((BIBLE/"REGISTRO-GERACOES.json").read_text(encoding="utf-8"))
    entries=[x for x in doc["geracoes"] if x.get("asset")=="c01-p02-scene-mother"]
    if len(entries)!=1:
        raise SystemExit("MOTHER_PREVIEW_REQUIRES_ONE_REAL_SHA_ARCHIVED")
    row=entries[0]
    relative=Path(row["arquivo"])
    if (relative.is_absolute() or ".." in relative.parts
            or not relative.is_relative_to(EP / "assets/geracoes/production-scene-mother-v2")):
        raise SystemExit("MOTHER_PREVIEW_UNSAFE_ARCHIVE_SOURCE")
    src=ROOT/relative
    if src.is_symlink() or not src.is_file() or src.stat().st_size>35_000_000:
        raise SystemExit("MOTHER_PREVIEW_SOURCE_MISSING")
    blob=src.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=row["sha256"]:
        raise SystemExit("MOTHER_PREVIEW_SOURCE_SHA_MISMATCH")
    with Image.open(io.BytesIO(blob)) as im:
        if im.format!="PNG" or (im.width,im.height)!=(row["width"],row["height"]):
            raise SystemExit("MOTHER_PREVIEW_DIMENSIONS_INVALID")
        thumbnail=ImageOps.contain(im.convert("RGB"),(630,1110),Image.Resampling.LANCZOS)
    sheet=Image.new("RGB",(660,1190),"#f0f0f0")
    sheet.paste(thumbnail,((660-thumbnail.width)//2,51))
    pen=ImageDraw.Draw(sheet)
    pen.text((15,15),"C01-P02 | CENA-MAE REAL | QA PENDENTE",fill="#222222",font=ImageFont.load_default())
    pen.text((15,1164),"PNG SHA "+row["sha256"][:24]+"... | NAO APROVADO",fill="#555555")
    name="QA-C01-P02-CENA-MAE.jpg"
    out=ROOT/EP/name
    buffer=io.BytesIO()
    sheet.save(buffer,"JPEG",quality=82,optimize=True)
    jpg=buffer.getvalue()
    if not out.exists() or out.read_bytes()!=jpg:
        out.write_bytes(jpg)
    meta={
        "schema":"videoforge/ep01-scene-mother-preview/v1",
        "source_sha256":row["sha256"],"source_png":row["arquivo"],
        "jpg":name,"jpg_sha256":hashlib.sha256(jpg).hexdigest(),
        "no_image_provider_calls":True,"visual_approval":False,
        "layers_generated":False,"mp4_generated":False,"youtube_uploaded":False,
    }
    target=out.with_suffix(".json")
    data=json.dumps(meta,ensure_ascii=False,indent=2)+"\n"
    if not target.exists() or target.read_text(encoding="utf-8")!=data:
        target.write_text(data,encoding="utf-8")
    print("EP01_MOTHER_VISUAL_QA_PREVIEW_GENERATED",json.dumps({"source_sha256":row["sha256"],"jpg_bytes":len(jpg)}))


if __name__=="__main__":
    main()
