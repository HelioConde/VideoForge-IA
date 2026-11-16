"""Refinamento cromático exploratório das oito ROIs reais do EP01.

Máscaras por cor dentro de polígonos CANDIDATOS, não segmentação semântica,
nem avaliação oficial de qualidade. O formato de saída preserva SHA, pose
não confirmada e necessidade de revisão humana. Zero chamadas pagas.
"""
from __future__ import annotations

import argparse
import colorsys
import hashlib
import io
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import EPISODE, ROOT
from .wardrobe_roi_candidates import (
    MANIFEST, INVENTORY, REGIONS, board_to_source, verified_file,
)

REPORT = "QA-ROI-MASCARAS-REFINADAS-V2.json"
BOARD = "QA-ROI-MASCARAS-REFINADAS-V2.jpg"
CROP_DIR = "assets/qa-roi-figurino-v2"
SCHEMA = "videoforge/wardrobe-color-seed-masks/v1"


def color_candidate(region, rgb):
    """Restrição conservadora de cor, sem assumir que achou a peça certa."""
    r, g, b = rgb[:3]
    hue, sat, val = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    angle = hue * 360
    if region == "barba":
        # Cinza/prata mais neutro: reduz pele de bochecha/lábio, mas pode
        # descartar fios em sombra quente; revisão visual permanece obrigatória.
        return (.17 <= val <= .98 and sat <= .19 and min(r,g,b) >= 39
                and abs(r-g) <= 18 and abs(g-b) <= 22)
    if region == "tecido_externo":
        # Tecido escuro, excluindo a maioria dos bordados brilhantes.
        return .06 <= val < .42 and sat <= .38
    if region == "painel_central":
        # Vinho/vermelho; não incluir ouro, pele ou iluminação magenta.
        return .11 <= val <= .88 and sat >= .26 and (angle < 17 or angle >= 348)
    if region == "corpete_roxo_palacio":
        return .10 <= val <= .95 and sat >= .24 and 235 <= angle < 329
    raise VideoForgeError("ROI_REFINE_UNKNOWN_REGION")


def refine_mask(im, vertices, region):
    """Separa pixels candidatos usando ROI geométrica + filtro cromático."""
    from PIL import Image, ImageDraw

    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(vertices, fill=255)
    x0 = max(0, min(x for x, y in vertices))
    x1 = min(im.width-1, max(x for x, y in vertices))
    y0 = max(0, min(y for x, y in vertices))
    y1 = min(im.height-1, max(y for x, y in vertices))
    pix = im.load()
    alpha = mask.load()
    original_area = 0
    selected_area = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not alpha[x,y]:
                continue
            original_area += 1
            if color_candidate(region, pix[x,y]):
                selected_area += 1
            else:
                alpha[x,y] = 0
    if original_area < 128:
        raise VideoForgeError("ROI_REFINE_POLYGON_TOO_SMALL")
    # Fallback is explicitly forbidden: do not recycle broad polygon on failure.
    success = selected_area >= 128 and selected_area / original_area >= .04
    return mask, original_area, selected_area, success


def isolated_png(im, mask, vertices):
    from PIL import Image
    margin = 8
    xy = (
        max(0, min(x for x,y in vertices) - margin),
        max(0, min(y for x,y in vertices) - margin),
        min(im.width, max(x for x,y in vertices) + margin + 1),
        min(im.height, max(y for x,y in vertices) + margin + 1),
    )
    image = im.convert("RGBA")
    image.putalpha(mask)
    cut = image.crop(xy)
    stream = io.BytesIO()
    cut.save(stream, format="PNG", optimize=True)
    return stream.getvalue(), xy


def visual_tile(im, mask, vertices):
    from PIL import Image, ImageDraw, ImageOps
    # Transparência é representada pelo fundo escuro, não pela cor preta da peça.
    sample = im.copy().convert("RGBA")
    sample.putalpha(mask)
    margin = max(28, int(max(max(x for x,y in vertices)-min(x for x,y in vertices),
                              max(y for x,y in vertices)-min(y for x,y in vertices))*.7))
    x0 = max(0, min(x for x,y in vertices)-margin)
    y0 = max(0, min(y for x,y in vertices)-margin)
    x1 = min(im.width, max(x for x,y in vertices)+margin+1)
    y1 = min(im.height,max(y for x,y in vertices)+margin+1)
    crop = sample.crop((x0,y0,x1,y1))
    background = Image.new("RGB", crop.size, (48,51,63))
    background.paste(crop,mask=crop.getchannel("A"))
    return ImageOps.contain(background,(545,232),Image.Resampling.LANCZOS)


def run(root:Path=ROOT, sync:bool=False):
    from PIL import Image, ImageDraw, ImageFont

    ep = Path(root) / EPISODE
    config = ep / MANIFEST
    inventory_path = ep / INVENTORY
    if any(p.is_symlink() for p in (config, inventory_path)):
        raise VideoForgeError("ROI_REFINE_METADATA_UNSAFE")
    meta = json.loads(config.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    pairs = meta.get("pairs",[])
    if (meta.get("schema") != "videoforge/roi-candidate-annotation/v1"
        or meta.get("human_semantic_verification") is not False
        or meta.get("can_change_canonical_status") is not False
        or [(p.get("actor"),p.get("semantic_region")) for p in pairs] != REGIONS
        or inventory.get("schema") != "videoforge/wardrobe-roi-review/v1"):
        raise VideoForgeError("ROI_REFINE_UNTRUSTED_MANIFEST")

    canvas = Image.new("RGB",(1260,1485),(21,25,34))
    pen = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=15)
    pen.text((23,16),"EP01 - MASCARAS POR COR (CANDIDATAS / SEM APROVACAO)",font=font,fill="white")
    pen.text((23,45),"Somente pixels dos PNGs SHA verificados. Cinza = transparente / nao selecionado.",font=small,fill=(219,213,186))
    samples = []
    payloads = {}
    for n, row in enumerate(pairs):
        actor, region = row["actor"],row["semantic_region"]
        y = 80 + n * 338
        pen.text((20,y),f"{actor.upper()} - {region}: ISOLE POR COR; REVISAR ANATOMIA",font=font,fill="white")
        pair_sources = []
        for j, side in enumerate(("a","b")):
            idx = meta["source_indices"][actor][j]
            info = inventory["previews"][actor]["sources"][idx]
            im = verified_file(ep,info["path"],info["sha256"],image_only=True)
            verts = board_to_source(row["board_points_"+side],im.size,idx)
            mask, original, retained, viable = refine_mask(im,verts,region)
            data, crop_xyxy = isolated_png(im,mask,verts)
            out_path = f"{CROP_DIR}/{actor}-{region}-{side}-CANDIDATO.png"
            target = ep / out_path
            payloads[target] = data
            tile = visual_tile(im,mask,verts)
            x = 25 + 610*j
            canvas.paste(tile,(x+(555-tile.width)//2,y+34))
            pen.text((x,y+266),f"{side.upper()}: {retained}/{original} px = {retained*100/original:.1f}% selecionados",font=small,fill="white")
            pen.text((x,y+291),f"SHA origem {info['sha256'][:20]} | sem aprovacao",font=small,fill=(186,203,216))
            pair_sources.append({
                "side":side, "source_path":info["path"],
                "source_sha256":info["sha256"],"source_size":list(im.size),
                "candidate_polygon_native_px":[list(p) for p in verts],
                "seed_polygon_pixels":original,"color_isolated_pixels":retained,
                "retained_percent":round(retained/original*100,2),
                "mask_viable_for_visual_review":viable,
                "candidate_cutout_path":out_path,
                "candidate_cutout_sha256":hashlib.sha256(data).hexdigest(),
                "candidate_cutout_box_xyxy":list(crop_xyxy),
                "semantic_mask_verified":False,"official_color_comparison_eligible":False,
            })
        samples.append({
            "actor":actor,"semantic_region":region,
            "status":"CANDIDATAS_A_CONFERIR",
            "sources":pair_sources,
            "difference_is_not_an_official_finding":True,
            "automatic_approval":False,
            "automatic_rejection":False,
        })

    pen.text((23,1456),"8 MASCARAS CANDIDATAS | 0 VALIDADAS | R2 BLOQUEADA | NENHUMA IA PAGA",font=small,fill=(249,204,148))
    jpg=io.BytesIO()
    canvas.save(jpg,"JPEG",quality=90,optimize=True)
    payloads[ep/BOARD]=jpg.getvalue()
    report={
        "schema":SCHEMA,
        "status":"COLOR_FILTERED_PIXEL_CANDIDATES_NOT_SEMANTICALLY_VERIFIED",
        "regions":samples,
        "candidate_masks":8,
        "verified_semantic_masks":0,
        "verified_semantic_pairs":0,
        "previous_owner_rejections_remain":True,
        "r2_blocked":True,
        "canonical_art_approved":False,
        "new_paid_images":0,
        "provider_calls":0,"official_mp4":False,"youtube_uploaded":False,
        "source_images_unchanged":True,
    }
    payloads[ep/REPORT]=(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    if sync:
        for path,data in payloads.items():
            if path.is_symlink():
                raise VideoForgeError("ROI_REFINE_OUTPUT_SYMLINK")
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.is_file() or path.read_bytes()!=data:
                path.write_bytes(data)
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    args = p.parse_args()
    obj=run(sync=args.sync)
    print("ROI_COLOR_REFINEMENT",json.dumps({
        "candidates":obj["candidate_masks"],
        "semantic_verified":obj["verified_semantic_masks"],
        "paid_calls":0,"r2_blocked":True,
    }))


if __name__ == "__main__":
    main()
