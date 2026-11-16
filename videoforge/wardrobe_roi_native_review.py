"""Pranchas PNG em pixels fonte 1:1 para revisão semântica V3.

Não cria segmentos, não modifica máscaras ou fontes, nem certifica pose,
identidade, luz ou figurino. Compara RGB/alpha somente por pixels originais.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import EPISODE, ROOT
from .wardrobe_roi_archive import audit as audit_archive
from .wardrobe_roi_candidates import verified_file
from .wardrobe_roi_exclusions import review_crops

V3="QA-ROI-EXCLUSOES-V3.json"
OUT="QA-ROI-REVISAO-NATIVA-V3.json"
DIR="assets/qa-roi-review-native-v3"
REVIEW="REVISAO-SEMANTICA-ROI-V3.json"

def source_pixel_sheet(source, prior, removed, final, box):
    """Four RGB panels at 1:1 source pixels, without geometric resizing."""
    from PIL import Image, ImageChops
    if (source.mode!="RGB" or prior.mode!="L" or removed.mode!="L"
        or final.mode!="L" or
        prior.size != source.size or removed.size != source.size or
        final.size != source.size):
        raise VideoForgeError("ROI_NATIVE_GEOMETRY_INVALID")
    if (len(box)!=4 or not 0<=box[0]<box[2]<=source.width
        or not 0<=box[1]<box[3]<=source.height):
        raise VideoForgeError("ROI_NATIVE_BOX_INVALID")
    if ImageChops.difference(ImageChops.subtract(prior,final),removed).getbbox():
        raise VideoForgeError("ROI_NATIVE_REMOVED_PIXELS_INVALID")
    context=source.crop(box)
    background=(45,48,57)
    tiles=[context]
    for mask in (prior,removed,final):
        part=context.convert("RGBA")
        part.putalpha(mask.crop(box))
        panel=Image.new("RGB",context.size,background)
        panel.paste(part,mask=part.getchannel("A"))
        tiles.append(panel)
    # Headers are outside source pixels; each image tile is exact 1:1.
    width,height=context.size
    top=44
    result=Image.new("RGB",(width*4,height+top),background)
    from PIL import ImageDraw, ImageFont
    draw=ImageDraw.Draw(result)
    for i,(tile,name) in enumerate(zip(tiles,("FONTE", "ANTES", "REMOVIDOS", "DEPOIS"))):
        result.paste(tile,(i*width,top))
        draw.text((i*width+5,8),name,fill="white",font=ImageFont.load_default(size=17))
    return result

def run(root:Path=ROOT,sync=False):
    from PIL import Image, ImageChops
    ep=Path(root)/EPISODE
    verified=audit_archive(root)
    a=ep/V3
    b=ep/REVIEW
    if a.is_symlink() or b.is_symlink() or not a.is_file() or not b.is_file():
        raise VideoForgeError("ROI_NATIVE_UNSAFE_METADATA")
    report=json.loads(a.read_text(encoding="utf-8"))
    review=json.loads(b.read_text(encoding="utf-8"))
    if (review.get("can_approve_r2") is not False
        or review.get("can_edit_official_contract") is not False
        or len(review.get("rows",[]))!=8
        or len(report.get("results",[]))!=8):
        raise VideoForgeError("ROI_NATIVE_CONTRACT_UNSAFE")
    rows=[]
    payloads={}
    for index,(archive,row) in enumerate(zip(verified["rows"],report["results"])):
        key=(row["actor"],row["region"],row["side"])
        if (key!=(archive["actor"],archive["region"],archive["side"])
            or key!=tuple(review["rows"][index][k] for k in ("actor","region","side"))
            or review["rows"][index].get("status")!="EVIDENCIA_INSUFICIENTE"
            or review["rows"][index].get("source_sha256")!=row["source_sha256"]
            or review["rows"][index].get("candidate_sha256")!=row["cleaned_candidate_sha256"]):
            raise VideoForgeError("ROI_NATIVE_REVIEW_MISMATCH")
        full=verified_file(ep,row["source_path"],row["source_sha256"],image_only=True)
        crop=row["cleaned_candidate_crop_xyxy"]
        context=row["context_review_box_xyxy"]
        cut=ep/row["cleaned_candidate_path"]
        if cut.is_symlink() or not cut.is_file():
            raise VideoForgeError("ROI_NATIVE_ARCHIVED_CUT_MISSING")
        with Image.open(io.BytesIO(cut.read_bytes())) as dec:
            if dec.format!="PNG" or dec.mode!="RGBA":
                raise VideoForgeError("ROI_NATIVE_ARCHIVED_CUT_INVALID")
            final_cut=dec.copy()
        if final_cut.size!=(crop[2]-crop[0],crop[3]-crop[1]):
            raise VideoForgeError("ROI_NATIVE_ARCHIVED_CUT_DIMENSION")
        after=Image.new("L",full.size,0)
        after.paste(final_cut.getchannel("A"),(crop[0],crop[1]))
        # Rebuild previous mask using only trusted source geometry/color,
        # not pixels from a JPEG contact sheet.
        from .wardrobe_roi_refine import refine_mask
        seed=ep/"QA-ROI-MASCARAS-REFINADAS-V2.json"
        x=json.loads(seed.read_text(encoding="utf-8"))
        candidate=[s for rr in x["regions"] if rr["actor"]==row["actor"]
                   and rr["semantic_region"]==row["region"]
                   for s in rr["sources"] if s["side"]==row["side"]]
        if len(candidate)!=1:
            raise VideoForgeError("ROI_NATIVE_SEED_NOT_UNIQUE")
        prior,_,_,_=refine_mask(full,candidate[0]["candidate_polygon_native_px"],row["region"])
        removed=ImageChops.subtract(prior,after)
        png=source_pixel_sheet(full,prior,removed,after,context)
        output=io.BytesIO()
        png.save(output,format="PNG",optimize=True)
        data=output.getvalue()
        name=f"{row['actor']}-{row['region']}-{row['side']}-CONTEXTO-1X.png"
        rel=f"{DIR}/{name}"
        payloads[ep/rel]=data
        rows.append({
            "actor":row["actor"],"region":row["region"],"side":row["side"],
            "source_path":row["source_path"],"source_sha256":row["source_sha256"],
            "archived_mask_sha256":row["cleaned_candidate_sha256"],
            "native_source_crop_xyxy":context,
            "native_source_crop_width":context[2]-context[0],
            "native_source_crop_height":context[3]-context[1],
            "tile_scale_factor":1,"geometry_interpolated":False,
            "sheet_sha256":hashlib.sha256(data).hexdigest(),
            "sheet_path":rel,
            "semantically_verified":False,
        })
    result={"schema":"videoforge/native-roi-review-tiles/v1",
            "status":"NATIVE_PIXEL_PREVIEWS_REQUIRING_SEMANTIC_REVIEW",
            "tiles":rows,"tile_count":8,
            "source_patches_native_scale":True,
            "semantic_masks_verified":0,"canonical_pairs_ready":0,
            "official_contract_unchanged":True,"r2_blocked":True,
            "provider_calls":0,"official_mp4":False,"youtube_uploaded":False}
    payloads[ep/OUT]=(json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode()
    if sync:
        for path,content in payloads.items():
            if path.is_symlink():
                raise VideoForgeError("ROI_NATIVE_OUTPUT_UNSAFE")
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists() or path.read_bytes()!=content:
                path.write_bytes(content)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    args=p.parse_args()
    r=run(sync=args.sync)
    print("NATIVE_ROI_V3",json.dumps({
        "tiles":r["tile_count"],"semantic_verified":0,
        "r2_blocked":True,"paid_calls":0}))

if __name__=="__main__":
    main()
