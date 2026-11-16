"""QA de subtração candidata de pixels não pertencentes ao figurino.

Gera nova prancha e PNGs separados; preserva máscaras anteriores, fontes e
contrato semântico. Exclusões são propostas da prancha, não verdade-terreno.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE
from .wardrobe_roi_candidates import verified_file, board_to_source
from .wardrobe_roi_refine import run as base_run, refine_mask, isolated_png

EXCLUSIONS="ROI-EXCLUSOES-CANDIDATAS-V3.json"
REPORT="QA-ROI-EXCLUSOES-V3.json"
BOARD="QA-ROI-EXCLUSOES-V3.jpg"
CONTEXT_BOARD="QA-ROI-CONTEXTO-V3.jpg"
OUTPUT="assets/qa-roi-exclusions-v3"
EXPECTED=[(a,r,s) for a,r in
    (("aldric","barba"),("aldric","tecido_externo"),
     ("aldric","painel_central"),("elara","corpete_roxo_palacio"))
    for s in ("a","b")]


def apply_exclusions(mask, proposed, size, source_index, protected=None):
    """Subtrai máscaras candidatas sem alterar imagem original nem anexar aprovação."""
    from PIL import Image, ImageDraw
    if mask.mode != "L" or mask.size != size:
        raise VideoForgeError("ROI_EXCLUSION_MASK_GEOMETRY")
    if not isinstance(proposed,list) or len(proposed)>12:
        raise VideoForgeError("ROI_EXCLUSION_INVALID_LIST")
    out=mask.copy()
    before=sum(bool(v) for v in mask.tobytes())
    remove=Image.new("1",size,0)
    painter=ImageDraw.Draw(remove)
    converted=[]
    for board_poly in proposed:
        vertices=board_to_source(board_poly,size,source_index)
        painter.polygon(vertices,fill=1)
        converted.append([list(v) for v in vertices])
    if protected is not None:
        if not isinstance(protected,list) or len(protected)>12:
            raise VideoForgeError("ROI_EXCLUSION_INVALID_PROTECTED_LIST")
        keep=Image.new("1",size,0)
        pen=ImageDraw.Draw(keep)
        for polygon in protected:
            pen.polygon(board_to_source(polygon,size,source_index),fill=1)
        # Protecao explicita prevalece: nunca apagar silenciosamente area marcada.
        from PIL import ImageChops
        if ImageChops.logical_and(remove,keep).getbbox():
            raise VideoForgeError("ROI_EXCLUSION_TOUCHES_PROTECTED_REGION")
    pix=out.load()
    rp=remove.load()
    removed=0
    if converted:
        coords=[v for poly in converted for v in poly]
        for y in range(max(0,min(p[1] for p in coords)),min(size[1],max(p[1] for p in coords)+1)):
            for x in range(max(0,min(p[0] for p in coords)),min(size[0],max(p[0] for p in coords)+1)):
                if rp[x,y] and pix[x,y]:
                    removed+=1
                    pix[x,y]=0
    if before-removed<128:
        raise VideoForgeError("ROI_EXCLUSION_REMOVED_TOO_MUCH")
    return out,{"before":before,"removed":removed,"after":before-removed,
                "fraction_removed_percent":round(100*removed/before,2),
                "exclusion_polygons_native_px":converted}


def verify_exclusion_pixels(source, before_mask, after_mask, png, box, expected_removed):
    """Comprova subtracao e pixels originais; nao valida semantica da selecao."""
    from PIL import Image, ImageChops
    if (before_mask.mode != "L" or after_mask.mode != "L"
            or before_mask.size != source.size or after_mask.size != source.size):
        raise VideoForgeError("ROI_EXCLUSION_MASK_GEOMETRY")
    if (len(box) != 4 or any(type(v) is not int for v in box)
            or not 0 <= box[0] < box[2] <= source.width
            or not 0 <= box[1] < box[3] <= source.height):
        raise VideoForgeError("ROI_EXCLUSION_CROP_GEOMETRY")
    before, after = before_mask.tobytes(), after_mask.tobytes()
    if any(a not in (0, b) for b, a in zip(before, after)):
        raise VideoForgeError("ROI_EXCLUSION_ALPHA_NOT_SUBTRACTION")
    removed = sum(bool(b) and not a for b, a in zip(before, after))
    if type(expected_removed) is not int or removed != expected_removed:
        raise VideoForgeError("ROI_EXCLUSION_COUNT_MISMATCH")
    crop_alpha = after_mask.crop(box)
    if sum(bool(a) for a in crop_alpha.tobytes()) != sum(bool(a) for a in after):
        raise VideoForgeError("ROI_EXCLUSION_CROP_LOSES_PIXELS")
    with Image.open(io.BytesIO(png)) as decoded:
        if decoded.format != "PNG" or decoded.mode != "RGBA" or decoded.size != crop_alpha.size:
            raise VideoForgeError("ROI_EXCLUSION_PNG_GEOMETRY")
        if ImageChops.difference(decoded.getchannel("A"), crop_alpha).getbbox():
            raise VideoForgeError("ROI_EXCLUSION_PNG_ALPHA_CHANGED")
        if ImageChops.difference(decoded.convert("RGB"), source.convert("RGB").crop(box)).getbbox():
            raise VideoForgeError("ROI_EXCLUSION_RGB_CHANGED")
    return {"rgb_matches_source_crop": True, "alpha_only_subtraction": True,
            "crop_preserves_all_retained_pixels": True, "removed_pixels_verified": removed,
            "semantic_approval": False}


def review_crops(source, before, after, box):
    """Quatro recortes alinhados: fonte, antes, removidos e depois; sem inpainting."""
    from PIL import ImageChops
    margin=max(24, (max(box[2]-box[0],box[3]-box[1]))//2)
    context=(max(0,box[0]-margin),max(0,box[1]-margin),
             min(source.width,box[2]+margin),min(source.height,box[3]+margin))
    original=source.convert("RGB").crop(context)
    removed=ImageChops.subtract(before,after)
    panels=[original]
    for mask in (before,removed,after):
        image=original.convert("RGBA")
        image.putalpha(mask.crop(context))
        panels.append(image)
    return panels,context


def run(root:Path=ROOT,sync=False):
    from PIL import Image,ImageDraw,ImageFont,ImageOps
    ep=Path(root)/EPISODE
    path=ep/EXCLUSIONS
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("ROI_EXCLUSION_MANIFEST_MISSING")
    config=json.loads(path.read_text(encoding="utf-8"))
    rows=config.get("rows",[])
    if (config.get("schema")!="videoforge/wardrobe-roi-manual-exclusion-proposals/v1"
            or config.get("automatic_semantic_validation") is not False
            or config.get("promote_to_official_contract") is not False
            or [(x.get("actor"),x.get("region"),x.get("side")) for x in rows]!=EXPECTED):
        raise VideoForgeError("ROI_EXCLUSION_MANIFEST_INVALID")
    prev=base_run(root,sync=False)
    index={(x["actor"],x["semantic_region"],side["side"]):side
           for x in prev["regions"] for side in x["sources"]}
    canvas=Image.new("RGB",(1280,1660),(23,27,36))
    context_canvas=Image.new("RGB",(1600,2440),(23,27,36))
    context_draw=ImageDraw.Draw(context_canvas)
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.load_default(size=16)
    context_draw.text((16,12),"ROI V3 - CONTEXTO ORIGINAL | ANTES | REMOVIDOS | DEPOIS - SEM APROVACAO",font=font,fill="white")
    for column,label in enumerate(("FONTE COM CONTEXTO","MASCARA ANTERIOR","PIXELS REMOVIDOS","MASCARA FINAL")):
        context_draw.text((16+column*400,42),label,font=font,fill=(228,210,172))
    draw.text((20,15),"EP01 V2 - MASCARAS V3 CANDIDATAS: ANTES / DEPOIS",font=font,fill="white")
    draw.text((20,45),"Mesma fonte PNG SHA, mesma geometria e cores; propostas sem aprovacao.",font=font,fill=(228,210,172))
    results=[]
    files={}
    for i,item in enumerate(rows):
        key=(item["actor"],item["region"],item["side"])
        entry=index[key]
        im=verified_file(ep,entry["source_path"],entry["source_sha256"],image_only=True)
        polygon=[tuple(p) for p in entry["candidate_polygon_native_px"]]
        raw_mask,_,_,_=refine_mask(im,polygon,item["region"])
        source_index=0 if item["side"]=="a" else 1
        new_mask,delta=apply_exclusions(raw_mask,item["exclude_board_polygons"],im.size,source_index,
                                        item.get("protected_board_polygons"))
        original_png,_=isolated_png(im,raw_mask,polygon)
        clean_png,box=isolated_png(im,new_mask,polygon)
        integrity=verify_exclusion_pixels(im,raw_mask,new_mask,clean_png,box,delta["removed"])
        panels,context_box=review_crops(im,raw_mask,new_mask,box)
        for column,panel in enumerate(panels):
            background=Image.new("RGB",panel.size,(57,60,70))
            background.paste(panel,mask=panel.getchannel("A") if panel.mode=="RGBA" else None)
            tile=ImageOps.contain(background,(380,240),Image.Resampling.NEAREST)
            context_canvas.paste(tile,(10+column*400+(380-tile.width)//2,95+i*290+(240-tile.height)//2))
        context_draw.text((16,75+i*290),f"{item['actor']} / {item['region']} / {item['side']} - {delta['removed']} removidos",font=font,fill="white")
        name=f"{item['actor']}-{item['region']}-{item['side']}-EXCLUSAO-CANDIDATA.png"
        files[ep/OUTPUT/name]=clean_png
        # Every preview tile shows the same crop, before and after.
        from PIL import Image as PilImage
        for column,blob in enumerate((original_png,clean_png)):
            with PilImage.open(io.BytesIO(blob)) as src:
                image=src.convert("RGBA")
                background=PilImage.new("RGB",image.size,(57,60,70))
                background.paste(image,mask=image.getchannel("A"))
                tile=ImageOps.contain(background,(570,144),Image.Resampling.LANCZOS)
            xx=20+column*630+(570-tile.width)//2
            yy=85+i*194+(144-tile.height)//2
            canvas.paste(tile,(xx,yy))
        draw.text((20,85+i*194+147),
                  f"{item['actor']} / {item['region']} / {item['side']}: {delta['removed']} px removidos ({delta['fraction_removed_percent']}%)",
                  font=font,fill=(238,225,193))
        results.append({
            "actor":item["actor"],"region":item["region"],"side":item["side"],
            "source_path":entry["source_path"],
            "source_sha256":entry["source_sha256"],
            "reason_unverified":item["reason"],
            "semantic_status":"EVIDENCIA_INSUFICIENTE",
            "protected_board_polygons":item.get("protected_board_polygons",[]),
            "candidate_exclusion":delta,
            "cleaned_candidate_path":f"{OUTPUT}/{name}",
            "cleaned_candidate_sha256":hashlib.sha256(clean_png).hexdigest(),
            "cleaned_candidate_crop_xyxy":list(box),
            "pixel_integrity":integrity,
            "context_review_box_xyxy":list(context_box),
            "semantically_verified":False,"official_art_usable":False,
        })
    draw.text((20,1640),"0 MASCARAS VERIFICADAS | R2 BLOQUEADA | SEM IMAGEM PAGA",font=font,fill=(246,198,140))
    stream=io.BytesIO()
    canvas.save(stream,format="JPEG",quality=88,optimize=True)
    files[ep/BOARD]=stream.getvalue()
    context_stream=io.BytesIO()
    context_canvas.save(context_stream,format="JPEG",quality=92,optimize=True)
    files[ep/CONTEXT_BOARD]=context_stream.getvalue()
    report={
        "schema":"videoforge/wardrobe-exclusion-candidates/v1",
        "status":"EXCLUSION_PROPOSALS_ONLY",
        "results":results,
        "context_review_board":CONTEXT_BOARD,
        "context_review_board_sha256":hashlib.sha256(context_stream.getvalue()).hexdigest(),
        "context_preview_only_not_measurement":True,
        "candidate_count":8,"verified_semantic_masks":0,
        "official_roi_pairs_ready":0,"r2_blocked":True,
        "owner_rejections_remain":True,"paid_calls":0,
        "image_sources_unchanged":True,
        "official_mp4":False,"youtube_uploaded":False,
    }
    files[ep/REPORT]=(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode()
    if sync:
        for target,blob in files.items():
            if target.is_symlink():raise VideoForgeError("ROI_EXCLUSION_OUTPUT_SYMLINK")
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.is_file() or target.read_bytes()!=blob:
                target.write_bytes(blob)
    return report


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--sync",action="store_true")
    a=arg.parse_args()
    result=run(sync=a.sync)
    print("EXCLUSION_QA",json.dumps({
        "candidates":result["candidate_count"],
        "verified":result["verified_semantic_masks"],
        "official_pairs":result["official_roi_pairs_ready"],
        "paid_calls":0,"r2_blocked":True,
    }))


if __name__=="__main__":
    main()
