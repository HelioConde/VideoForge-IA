"""Camada de espada visível recortada dos pixels da C01-P02.

Substitui na QA o recorte artificial de espada que aparecia POR CIMA
dos dedos. Não estica, não translada, não inventa a lâmina escondida.
A máscara manual é um CANDIDATO, não uma animação aprovada.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
from .errors import VideoForgeError
from .ep01_shot_layers import mother_source
from .ep01_contact_cutouts import (make_source_cutouts, GRID,
                                   EXPECTED_MOTHER_SHA)
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

ASSET="c01-p02-object-espada-source-visible"
PRODUCER="production-source-sword-cutout-v1"
# Coordenadas no mesmo grid da cena-mãe. É uma máscara de objetos
# visíveis, não reconstrução da geometria oculta sob a luva/bainha.
SWORD_REGIONS=[
 [(116,116),(140,99),(165,97),(186,111),(201,139),
  (194,168),(173,190),(138,181),(113,155)],
 [(146,156),(189,151),(216,210),(222,246),(182,253),(148,213)],
 [(103,323),(143,305),(173,315),(197,333),(260,316),
  (314,299),(353,290),(366,309),(364,344),(337,354),
  (297,370),(280,397),(299,433),(325,502),(351,578),
  (334,608),(303,562),(276,499),(251,446),(235,407),
  (211,380),(176,366),(143,391),(115,405),(102,374),(97,345)]
]


def sword_mask(canvas:tuple[int,int], gloves:dict)->Image.Image:
    if canvas!=(941,1672):
        raise VideoForgeError("EP01_SWORD_MOTHER_CANVAS_CHANGED")
    mask=Image.new("L",canvas,0)
    draw=ImageDraw.Draw(mask)
    for polygon in SWORD_REGIONS:
        scaled=[(round(x*canvas[0]/GRID[0]),round(y*canvas[1]/GRID[1]))
                for x,y in polygon]
        draw.polygon(scaled,fill=255)
    blocked=ImageChops.lighter(
        gloves["hand-upper-contact-occlusion"].getchannel("A"),
        gloves["hand-lower-contact-occlusion"].getchannel("A"))
    mask=ImageChops.subtract(mask,blocked)
    if not mask.getbbox():
        raise VideoForgeError("EP01_SWORD_MASK_EMPTY")
    if ImageChops.darker(mask,blocked).getbbox():
        raise VideoForgeError("EP01_SWORD_STILL_ABOVE_HAND")
    return mask


def candidate(mother_bytes:bytes)->tuple[Image.Image,dict]:
    gloves,_=make_source_cutouts(mother_bytes)
    from io import BytesIO
    with Image.open(BytesIO(mother_bytes)) as im:
        if im.format!="PNG" or im.size!=(941,1672):
            raise VideoForgeError("EP01_SWORD_SOURCE_NOT_PNG_NATIVE")
        mother=im.convert("RGBA")
    mask=sword_mask(mother.size,gloves)
    candidate=mother.copy()
    candidate.putalpha(mask)
    if ImageChops.difference(candidate.convert("RGB"),
                             mother.convert("RGB")).getbbox() is not None:
        raise VideoForgeError("EP01_SWORD_SOURCE_COLORS_CHANGED")
    return candidate,{
        "canvas":[941,1672],"bbox":list(mask.getbbox()),
        "visible_pixels":mask.histogram()[255],
        "source_rgb_exact":True,"source_coordinate_offset":[0,0],
        "source_scale":1,"original_pixels_resampled":False,
        "hands_occlude_sword":True,"not_visible_sword_extension_generated":True,
        "mask_draft_for_visual_review":True,
    }


def build(root:Path=ROOT)->dict:
    root=Path(root)
    doc,raw,info=mother_source(root)
    if (doc["mother_sha256"]!=EXPECTED_MOTHER_SHA or
        hashlib.sha256(raw).hexdigest()!=EXPECTED_MOTHER_SHA):
        raise VideoForgeError("EP01_SWORD_MOTHER_SHA_INVALID")
    sword,qa=candidate(raw)
    output=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    if output.is_symlink() or output.exists() and any(output.iterdir()):
        raise VideoForgeError("EP01_SWORD_OUTPUT_NOT_EMPTY")
    output.mkdir(parents=True,exist_ok=True)
    image_path=output/(ASSET+".png")
    json_path=output/(ASSET+".production.json")
    sword.save(image_path,"PNG",optimize=True)
    png=image_path.read_bytes()
    row={
        "schema":"videoforge/ep01-sword-source-mask/v1",
        "channel":CHANNEL,"video_id":VIDEO,
        "asset_id":ASSET,"candidate_scene_shot_id":"C01-P02",
        "sha256":hashlib.sha256(png).hexdigest(),
        "source_mother_sha256":EXPECTED_MOTHER_SHA,
        "source_originals_sha_verified":[{
            "id":"c01-p02-scene-mother",
            "path":doc["mother_archive_png"],
            "sha256":EXPECTED_MOTHER_SHA}],
        "mask_qa":qa,"technical_qa":"source_pixels_unmodified_sword_candidate_only",
        "old_proxy_sword_approved":False,"source_mask_approved":False,
        "hand_contact_qc":"candidate_waiting_visual_recomposition",
        "rig_approved":False,"youtube_uploaded":False,"mp4_generated":False,
        "image_provider_calls":0,
    }
    json_path.write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n",
                         encoding="utf-8")
    print("EP01_SWORD_SOURCE_PIXELS_CANDIDATE",json.dumps({
        "sha256":row["sha256"],"bbox":qa["bbox"],"paid_calls":0}))
    return row


if __name__=="__main__":
    build()
