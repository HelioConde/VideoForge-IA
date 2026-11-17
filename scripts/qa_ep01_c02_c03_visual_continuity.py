#!/usr/bin/env python3
"""Storyboard comparison (no cutouts, rig, image generation or visual approval)."""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageOps

from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

SCHEMA = "videoforge/ep01-c02-c03-visual-continuity-qa/v1"
SOURCES = [
    ("C01-P03 V2 | Kael ajoelhado e Aldric", "c01-p03-scene-mother-v2",
     "production-scene-mother-repair-v2"),
    ("C02-P01 | close do rei Aldric", "c02-p01-scene-mother",
     "production-scene-mother-v2"),
    ("C02-P02 | Kael em panico contido", "c02-p02-scene-mother",
     "production-scene-mother-v2"),
    ("C03-P01 | reflexo azul na iris", "c03-p01-scene-mother",
     "production-scene-mother-v2")
]


def get_source(source_id: str, producer: str, entries: list) -> tuple[Image.Image,dict]:
    matches=[row for row in entries if row.get("asset")==source_id
             and f"/{producer}/" in str(row.get("arquivo",""))]
    if len(matches)!=1:
        raise RuntimeError("EP01_CONTINUITY_EXPECTED_UNIQUE_MOTHER "+source_id)
    row=matches[0]
    rel=Path(row["arquivo"])
    if (rel.is_absolute() or ".." in rel.parts or
        not rel.is_relative_to(REL/"assets"/"geracoes"/producer)):
        raise RuntimeError("EP01_CONTINUITY_INVALID_SOURCE_PATH "+source_id)
    file=ROOT/rel
    proof=file.with_suffix(".production.json")
    if file.is_symlink() or proof.is_symlink() or not file.is_file() or not proof.is_file():
        raise RuntimeError("EP01_CONTINUITY_MISSING_SOURCE "+source_id)
    raw=file.read_bytes()
    digest=sha256(raw).hexdigest()
    meta=json.loads(proof.read_text(encoding="utf-8"))
    if (digest!=row.get("sha256") or meta.get("sha256")!=digest
        or meta.get("human_visual_approval") is not False):
        raise RuntimeError("EP01_CONTINUITY_SHA_PROOF_FAILED "+source_id)
    with Image.open(BytesIO(raw)) as im:
        if im.format!="PNG":
            raise RuntimeError("EP01_CONTINUITY_NOT_PNG "+source_id)
        img=im.convert("RGB").copy()
    return img,{
        "asset_id":source_id, "sha256":digest,
        "file":rel.as_posix(),
        "canvas":[img.width,img.height],
        "expected_canvas":[941,1672],
        "canvas_compatible":img.size==(941,1672),
        "human_approval":False
    }


def create_qa() -> dict:
    reg=ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
    data=json.loads(reg.read_text(encoding="utf-8"))
    src=[(name,*get_source(id,prod,data["geracoes"]))
         for name,id,prod in SOURCES]
    tile_width, tile_height=530,880
    board=Image.new("RGB",(tile_width*2+32,tile_height*2+90),"#f2f0eb")
    draw=ImageDraw.Draw(board)
    draw.text((20,14),"DORAMA EP01 | CONTINUIDADE DE KAEL, ALDRIC, LUZ E CAMERA",
              fill="#181818")
    for i,(name,img,meta) in enumerate(src):
        x=20+(i%2)*tile_width
        y=60+(i//2)*tile_height
        draw.text((x,y),name,fill="#252525")
        thumb=ImageOps.contain(img,(tile_width-25,tile_height-70),
                               Image.Resampling.LANCZOS)
        board.paste(thumb,(x+(tile_width-25-thumb.width)//2,y+24))
        if not meta["canvas_compatible"]:
            draw.text((x,y+tile_height-31),"CANVAS DIVERGENTE - QA PENDENTE",fill="#ad2e23")
    draw.text((20,board.height-34),
              "Comparacao editorial; nenhum quadro ou personagem foi recortado para rig.",
              fill="#ad2e23")
    output=ROOT/REL/"QA-C02-C03-CONTINUIDADE-IMAGENS.jpg"
    board.save(output,"JPEG",quality=84,optimize=True)
    report={
        "schema":SCHEMA,
        "panel_count":len(src),
        "frames":[dict(item[2],caption=item[0]) for item in src],
        "board":"QA-C02-C03-CONTINUIDADE-IMAGENS.jpg",
        "board_sha256":sha256(output.read_bytes()).hexdigest(),
        "checks_needing_visual_review":[
           "identity_of_kael_between_near_and_extreme_close",
           "aldric_crown_hair_beard_and_gold_burgundy_costume",
           "kael_injury_eyes_hair_texture",
           "light_and_throne_room_continuity",
           "blue_iris_reflection_inside_eye",
           "no_new_unplanned_character_or_object",
           "framing_is_new_shot_not_enlarged_pixel_cutout"
        ],
        "no_image_provider_calls":True,
        "comparison_uses_original_mothers":True,
        "generated_separate_rig_images":False,
        "assistant_visual_review":"pending",
        "human_visual_approval":False,
        "rig_ready":False,
        "mp4_generated":False,
        "youtube_uploaded":False
    }
    (ROOT/REL/"QA-C02-C03-CONTINUIDADE-IMAGENS.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"
    )
    print("EP01_STORYBOARD_QA_READY",json.dumps({
        "shot_count":len(src),
        "sha":report["board_sha256"],
        "human_approved":False,
        "provider_calls":0},ensure_ascii=False))
    return report


if __name__=="__main__":
    try:
        create_qa()
    except (OSError,ValueError,RuntimeError) as exc:
        print("EP01_STORYBOARD_QA_BLOCKED",str(exc),file=sys.stderr)
        sys.exit(2)
