"""Recortes DETERMINÍSTICOS de contato da cena-mãe C01-P02.

Nunca usa o PNG da bainha rejeitada (981x1602), nem reinterpreta a
espada, o fundo ou os dedos com IA. Pixel RGB de cada recorte vem do
PNG original SHA-verificado: deslocamento (0,0), escala 1, sem pose.
Polígonos são máscaras iniciais de QA, NÃO aprovação visual/rig.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageStat

from .errors import VideoForgeError
from .ep01_shot_layers import mother_source
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

SCHEMA="videoforge/ep01-contact-source-pixel-cutouts/v1"
PRODUCER="production-contact-source-masks-v1"
GRID=(606,1084)  # coordenadas de anotação sobre TODO o enquadramento original
EXPECTED_MOTHER_SHA="b055b93e2174625adb4b7f5eb4f5a40f88f9353bce0fe50e0ac193d6eb002a5e"
# Polígonos de silhueta aproximados em uma prévia reduzida, transpostos
# para o CANVAS DA MÃE. São sementes conservadoras, sujeitas a QA visual.
# A bainha é parcialmente ocultada pela LUVA INFERIOR: não inventar
# material oculto no frame de referência.
MASK_POLYGONS={
    "object-bainha-source-visible":[
        [(265,588),(308,576),(370,575),(394,594),(405,619),(398,641),
         (376,670),(397,714),(418,757),(361,789),(325,742),
         (302,703),(285,672),(268,644)],
        [(374,902),(425,882),(454,893),(474,948),(498,1017),
         (519,1084),(397,1084),(369,1012),(362,963)]
    ],
    "hand-upper-contact-occlusion":[
        [(122,179),(162,159),(204,169),(239,185),(266,205),
         (274,237),(268,271),(271,299),(246,324),
         (224,350),(195,365),(148,358),(115,337),
         (100,309),(95,264),(100,220)]
    ],
    "hand-lower-contact-occlusion":[
        [(303,751),(330,721),(374,699),(428,686),(473,703),
         (504,733),(513,760),(508,797),(497,838),(480,864),
         (454,900),(414,921),(361,936),(328,914),(303,884),(291,839),(290,787)]
    ],
}
CONTACT_ORDER=["object-bainha-source-visible","hand-upper-contact-occlusion",
               "hand-lower-contact-occlusion"]


def polygon_mask(canvas:tuple[int,int], name:str) -> Image.Image:
    if name not in MASK_POLYGONS:
        raise VideoForgeError("EP01_CONTACT_UNKNOWN_MASK")
    width,height=canvas
    if canvas!=(941,1672):
        raise VideoForgeError("EP01_CONTACT_MOTHER_CANVAS_CHANGED")
    mask=Image.new("L",canvas,0)
    draw=ImageDraw.Draw(mask)
    for poly in MASK_POLYGONS[name]:
        vertices=[(round(x*width/GRID[0]),round(y*height/GRID[1]))
                  for x,y in poly]
        if len(vertices)<3:
            raise VideoForgeError("EP01_CONTACT_MASK_EMPTY_POLYGON")
        draw.polygon(vertices, fill=255)
    return mask


def make_source_cutouts(mother_png:bytes)->tuple[dict[str,Image.Image],dict]:
    with Image.open(io.BytesIO(mother_png)) as origin:
        if origin.format!="PNG" or origin.size!=(941,1672):
            raise VideoForgeError("EP01_CONTACT_SOURCE_NOT_NATIVE_PNG")
        mother=origin.convert("RGBA")
    masks={name:polygon_mask(mother.size,name) for name in CONTACT_ORDER}
    # A bainha nunca se sobrepõe aos dedos originais. O contato é
    # preservado pela LUVA EM CIMA dos objetos na composição.
    both_gloves=ImageChops.lighter(
        masks["hand-upper-contact-occlusion"],
        masks["hand-lower-contact-occlusion"])
    masks["object-bainha-source-visible"]=ImageChops.subtract(
        masks["object-bainha-source-visible"],both_gloves)
    cutouts={}
    report={}
    mother_rgb=mother.convert("RGB")
    for name in CONTACT_ORDER:
        mask=masks[name]
        if mask.getbbox() is None:
            raise VideoForgeError("EP01_CONTACT_MASK_EMPTY "+name)
        rgba=mother.copy()
        rgba.putalpha(mask)
        original_pixels=rgba.convert("RGB")
        difference=ImageChops.difference(original_pixels,mother_rgb)
        if difference.getbbox() is not None:
            raise VideoForgeError("EP01_CONTACT_SOURCE_RGB_MUST_NOT_CHANGE")
        bounds=mask.getbbox()
        report[name]={
            "alpha_bbox":list(bounds),
            "filled_pixels":mask.histogram()[255],
            "rgb_source_unchanged":True,
            "canvas":[mother.width,mother.height],
            "offset":[0,0],"scale":1,"color_resampling":False,
            "draft_polygon_requires_visual_review":True,
        }
        cutouts[name]=rgba
    return cutouts,report


def build(root:Path=ROOT)->dict:
    root=Path(root)
    plan,raw,info=mother_source(root)
    if plan["mother_sha256"]!=EXPECTED_MOTHER_SHA:
        raise VideoForgeError("EP01_CONTACT_SHA_CHANGED")
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_MOTHER_SHA:
        raise VideoForgeError("EP01_CONTACT_ORIGINAL_MOTHER_TAMPERED")
    target=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    if target.is_symlink():
        raise VideoForgeError("EP01_CONTACT_OUTPUT_SYMLINK")
    if target.exists() and any(target.iterdir()):
        raise VideoForgeError("EP01_CONTACT_OUTPUT_NOT_EMPTY_STOP")
    parts,qa=make_source_cutouts(raw)
    target.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name in CONTACT_ORDER:
        stem="c01-p02-"+name
        image_path=target/(stem+".png")
        meta_path=target/(stem+".production.json")
        parts[name].save(image_path,"PNG",optimize=True)
        digest=hashlib.sha256(image_path.read_bytes()).hexdigest()
        row={
            "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
            "asset_id":stem,"candidate_scene_shot_id":"C01-P02",
            "sha256":digest,
            "source_mother_sha256":EXPECTED_MOTHER_SHA,
            "source_originals_sha_verified":[
                {"id":"c01-p02-scene-mother",
                 "sha256":EXPECTED_MOTHER_SHA,
                 "path":plan["mother_archive_png"]}],
            "mask_qa":qa[name],
            "technical_qa":"source_pixels_unmodified_mask_candidate_only",
            "visual_approval":False,"hand_sword_contact_approved":False,
            "occluded_parts_invented":False,"rig_approved":False,
            "youtube_uploaded":False,"mp4_generated":False,
            "image_provider_calls":0,
        }
        meta_path.write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n",
                             encoding="utf-8")
        rows.append(row)
    print("EP01_CONTACT_SOURCE_PIXEL_CANDIDATES",json.dumps({
        "source_sha256":EXPECTED_MOTHER_SHA,
        "assets":[r["asset_id"] for r in rows],
        "image_provider_calls":0,
        "visual_approved":False},ensure_ascii=False))
    return {"cutouts":parts,"qa":qa,"metadata":rows}


if __name__=="__main__":
    build()
