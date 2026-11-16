"""Prancha de continuidade entre âncora aprovada e novo quadro SHA-verificado.

A comparação é VISUAL para o responsável; não calcula aprovação automática
de rostos, texturas ou roupas. Nenhum pixel das fontes é alterado.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from .remake_autopilot import ROOT, EPISODE
from .dorama_continuity import reference, _file
from .errors import VideoForgeError

REPORT="QA-C01-P04-VS-C01-P05.json"
SHEET="QA-C01-P04-VS-C01-P05.jpg"
RUN=43969450680
ASSET="c01-p05-guardas-lancas-v1"


def compare(root:Path=ROOT,sync=False):
    from PIL import Image,ImageOps,ImageDraw,ImageFont
    ep=Path(root)/EPISODE
    anchor,original=reference(root)
    location=f"assets/geracoes/production-art-request/{RUN}"
    folder=ep/location
    source=_file(ep,f"{location}/{ASSET}.png")
    meta_path=_file(ep,f"{location}/{ASSET}.production.json")
    manifest_path=_file(ep,f"{location}/manifesto-geracoes.json")
    data=source.read_bytes()
    meta=json.loads(meta_path.read_text(encoding="utf-8"))
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    sha=hashlib.sha256(data).hexdigest()
    provenance=meta.get("source_originals_sha_verified")
    if (meta.get("schema")!="videoforge/production-art-result/v1"
        or meta.get("asset_id")!=ASSET
        or meta.get("candidate_scene_shot_id")!="C01-P05"
        or meta.get("visual_continuity_anchor_sha256")!=anchor["sha256"]
        or meta.get("source_images_attached_to_request")!=1
        or not isinstance(provenance,list) or len(provenance)!=1
        or provenance[0].get("id")!="approved-visual-reference"
        or provenance[0].get("sha256")!=anchor["sha256"]
        or meta.get("sha256")!=sha
        or meta.get("human_visual_approval") is not False
        or meta.get("youtube_uploaded") is not False
        or manifest.get("github_run_id")!=RUN
        or manifest.get("channel")!="alchemy-lab"
        or len(manifest.get("images",[]))!=1
        or manifest["images"][0].get("sha256")!=sha):
        raise VideoForgeError("DORAMA_VISUAL_COMPARE_ORIGIN_MISMATCH")
    with Image.open(io.BytesIO(original)) as f:
        if f.format!="PNG":raise VideoForgeError("DORAMA_VISUAL_ANCHOR_NOT_PNG")
        im_a=f.convert("RGB")
    with Image.open(io.BytesIO(data)) as f:
        if f.format!="PNG":raise VideoForgeError("DORAMA_VISUAL_NEW_NOT_PNG")
        im_b=f.convert("RGB")
    if ((im_a.width,im_a.height)!=(anchor["width"],anchor["height"])
        or [im_b.width,im_b.height]!=[meta["actual_width"],meta["actual_height"]]):
        raise VideoForgeError("DORAMA_VISUAL_DIMENSIONS_MISMATCH")
    panel_w,panel_h=560,995
    board=Image.new("RGB",(panel_w*2+42,panel_h+140),(30,34,44))
    draw=ImageDraw.Draw(board)
    font=ImageFont.load_default(size=20)
    small=ImageFont.load_default(size=15)
    draw.text((24,17),"C01-P04 -> C01-P05 | CONTINUIDADE DO DORAMA",fill="white",font=font)
    draw.text((24,55),"Mesma referencia PNG original SHA / novo enquadramento; comparar visualmente",fill=(203,213,224),font=small)
    for i,(im,label) in enumerate(((im_a,"REFERENCIA APROVADA C01-P04"),(im_b,"NOVO QUADRO C01-P05"))):
        fitted=ImageOps.contain(im,(panel_w,panel_h),Image.Resampling.LANCZOS)
        xx=12+i*(panel_w+18)+(panel_w-fitted.width)//2
        board.paste(fitted,(xx,89+(panel_h-fitted.height)//2))
        draw.text((12+i*(panel_w+18),1093),label,fill=(244,233,187),font=small)
    draw.text((22,1130),"QA: aparencia, armaduras, lanças e luz exigem revisao; nenhum upload",fill=(225,214,196),font=small)
    output=io.BytesIO()
    board.save(output,format="JPEG",quality=88,optimize=True)
    jpeg=output.getvalue()
    result={
        "schema":"videoforge/shot-style-comparison/v1",
        "status":"COMPARED_PIXELS_FOR_HUMAN_REVIEW_NOT_APPROVED",
        "anchor_sha256":anchor["sha256"],
        "anchor_shot":"C01-P04",
        "new_shot":"C01-P05",
        "new_sha256":sha,
        "source_attached_to_generation":True,
        "reference_sha_verified":True,
        "comparison_sheet":SHEET,
        "comparison_sheet_sha256":hashlib.sha256(jpeg).hexdigest(),
        "anchor_size":list(im_a.size),
        "new_size":list(im_b.size),
        "image_pixels_unchanged":True,
        "visual_character_continuity_approved":False,
        "require_human_review":True,
        "r2_masks_revalidated":False,
        "youtube_uploaded":False,
        "generation_calls":0
    }
    if sync:
        for file,contents in ((ep/SHEET,jpeg),(ep/REPORT,(json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode())):
            if file.is_symlink():raise VideoForgeError("DORAMA_VISUAL_COMPARE_UNSAFE_OUTPUT")
            if not file.exists() or file.read_bytes()!=contents:
                file.write_bytes(contents)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    opt=p.parse_args()
    r=compare(sync=opt.sync)
    print("DORAMA_CONTINUITY_COMPARE",json.dumps({
        "anchor_sha":r["anchor_sha256"],
        "next_sha":r["new_sha256"],
        "manual_approval":False,"provider_calls":0,
    }))
if __name__=="__main__": main()
