#!/usr/bin/env python3
"""SHA-verified QA preview of C01-P04 guards/lanças without fabricating approval."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parents[1]
EP=Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
BIBLE=ROOT/"canal"/"alchemy-lab"/"biblia-visual"/"REGISTRO-GERACOES.json"
ASSET="c01-p04-scene-mother"
EXPECTED_SHA="156a9376298166045654706e75b876a20b7f8201c70d6d494ae9a2b7465f5ab3"


def main():
    reg=json.loads(BIBLE.read_text(encoding="utf-8"))
    hits=[x for x in reg.get("geracoes",[]) if x.get("asset")==ASSET]
    if len(hits)!=1: raise RuntimeError("EP01_C01P04_MOTHER_NOT_UNIQUE")
    item=hits[0]
    file=Path(item["arquivo"])
    prefix=EP/"assets"/"geracoes"/"production-scene-mother-v2"
    if file.is_absolute() or ".." in file.parts or not file.is_relative_to(prefix):
        raise RuntimeError("EP01_C01P04_UNSAFE_SOURCE")
    origin=ROOT/file
    if origin.is_symlink() or not origin.is_file():
        raise RuntimeError("EP01_C01P04_SOURCE_MISSING")
    raw=origin.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=item.get("sha256") or sha!=EXPECTED_SHA:
        raise RuntimeError("EP01_C01P04_SHA_MISMATCH")
    with Image.open(io.BytesIO(raw)) as source:
        if source.format!="PNG" or source.size!=(941,1672):
            raise RuntimeError("EP01_C01P04_SOURCE_SIZE_INVALID")
        im=source.convert("RGB")
    # Preview crops are ONLY visual QA, never final sprites/cutouts.
    W,H=im.size
    slices=[
        ("A C01-P04 INTEIRO",im),
        ("B GUARDA ESQUERDO / LANCA",im.crop((0,round(H*.2),round(W*.53),round(H*.86)))),
        ("C GUARDA DIREITO / LANCA",im.crop((round(W*.47),round(H*.2),W,round(H*.86)))),
        ("D CRUZAMENTO CENTRAL",im.crop((round(W*.2),round(H*.10),round(W*.8),round(H*.72)))),
    ]
    board=Image.new("RGB",(1350,1510),"#f2f2f2")
    pen=ImageDraw.Draw(board)
    for i,(label,frame) in enumerate(slices):
        x=(i%2)*675+8;y=(i//2)*730+10
        pen.text((x+5,y),label,fill="#242424")
        thumb=ImageOps.contain(frame,(647,690),Image.Resampling.LANCZOS)
        board.paste(thumb,(x+(647-thumb.width)//2,y+25))
    pen.text((15,1480),
       "CANDIDATA; CONFIRA AS MAOS NO TERCO INFERIOR DA LANCA. SEM RIG.",
       fill="#a82929")
    output=ROOT/EP/"QA-C01-P04-LANCAS-CONTATO.jpg"
    board.save(output,"JPEG",quality=88,optimize=True)
    report={
        "schema":"videoforge/ep01-c01p04-guard-grip-qa/v1",
        "shot_id":"C01-P04","mother_sha256":sha,
        "preview_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "preview":"QA-C01-P04-LANCAS-CONTATO.jpg",
        "source_size":[W,H],"crop_purpose":"QA_only_not_rig_assets",
        "review_targets":["guard-left-hand-on-lower-shaft","guard-right-hand-on-lower-shaft",
                          "spear-cross-X-high","hands-not-floating","king-outfit"],
        "technical_qa":"verified_sha_and_contact_sheet",
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,"provider_calls":0}
    (ROOT/EP/"QA-C01-P04-LANCAS-CONTATO.json").write_text(
         json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_C01P04_GUARD_QA_PREVIEW",json.dumps({"sha256":sha,"approved":False}))

if __name__=="__main__":
    main()
