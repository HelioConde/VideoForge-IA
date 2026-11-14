"""Separação DETERMINÍSTICA de pixels já existentes, sem IA e sem desenho novo.

Este recorte não é um rig: não cria pixels de áreas ocultas, não altera
personagens, não declara movimentos aprovados. Peças ficam com canvas original
e pivôs provisórios, aguardando underlay/QA humano.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw, ImageChops
except ImportError:
    Image=ImageDraw=ImageChops=None

SCHEMA="videoforge/existing-pixel-partition/v1"
EXPECTED_SIZE=(1024,1536)

class SplitError(ValueError):
    pass

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_plan(path:Path)->dict:
    if path.is_symlink() or not path.is_file():
        raise SplitError("PARTITION_PLAN_MISSING")
    data=json.loads(path.read_text(encoding="utf8"))
    if (data.get("schema")!=SCHEMA or data.get("channel")!="alchemy-lab"
        or data.get("video_id")!="mmorpg-conquiste-a-princesa-ep01"
        or data.get("no_generation") is not True
        or data.get("human_visual_approval") is not False):
        raise SplitError("PARTITION_ORIGIN_INVALID")
    if not isinstance(data.get("layers"),list) or len(data["layers"])<2:
        raise SplitError("PARTITION_LAYERS_MISSING")
    return data

def split_existing(source:Path, plan_path:Path, dest:Path)->dict:
    if Image is None: raise SplitError("PILLOW_REQUIRED_FOR_LOCAL_PIXEL_EXTRACTION")
    plan=read_plan(plan_path)
    if source.is_symlink() or not source.is_file() or sha(source)!=plan.get("source_sha256"):
        raise SplitError("SOURCE_SHA_MISMATCH")
    if dest.exists():
        raise SplitError("SPLIT_DESTINATION_EXISTS_NO_OVERWRITE")
    im=Image.open(source)
    if im.mode == "RGB" and plan.get("allow_opaque_scene_mother") is True:
        # A alfa opaca é apenas representação dos pixels RGB EXISTENTES;
        # nenhum personagem, cenário ou detalhe é gerado.
        im=im.convert("RGBA")
    if im.mode!="RGBA" or im.size!=EXPECTED_SIZE:
        raise SplitError("SOURCE_REQUIRES_CANONICAL_1024x1536_RGBA")
    width,height=im.size
    # Máscaras binárias; nunca inventar ou pintar um pixel de personagem.
    # A máscara é a única derivação: cada pixel existente vai para UMA peça.
    accumulated=Image.new("L",(width,height),0)
    components=[]
    parent=dest.parent
    if not parent.exists(): parent.mkdir(parents=True,exist_ok=True)
    dest.mkdir(parents=True)
    restored=Image.new("RGBA",im.size,(0,0,0,0))
    src_alpha=im.getchannel("A")
    for cfg in plan["layers"]:
        name=cfg.get("id")
        if not isinstance(name,str) or not name.replace("-","").isalnum() or len(name)>48:
            raise SplitError("PARTITION_NAME_INVALID")
        mask=Image.new("L",im.size,0)
        if cfg.get("kind")=="remainder":
            # Lote residual explicitamente suspeito; NÃO é asset de personagem.
            mask=ImageChops.invert(accumulated)
        elif cfg.get("kind")=="polygon":
            poly=cfg.get("vertices")
            if (not isinstance(poly,list) or len(poly)<3 or len(poly)>36
                or any(not isinstance(x,list) or len(x)!=2
                       or any(type(v) is not int or v<0 or v>max(width,height) for v in x)
                       for x in poly)):
                raise SplitError("PARTITION_POLYGON_INVALID")
            ImageDraw.Draw(mask).polygon([tuple(x) for x in poly],fill=255)
            mask=ImageChops.subtract(mask,accumulated)
        elif cfg.get("kind")=="stroke":
            points=cfg.get("points")
            width_px=cfg.get("width_px")
            head=cfg.get("head_polygon")
            butt=cfg.get("butt_polygon")
            def valid_points(items, minimum=2, maximum=30):
                return (isinstance(items,list) and minimum<=len(items)<=maximum
                        and all(isinstance(pair,list) and len(pair)==2
                                and all(type(n) is int and 0<=n<=max(width,height)
                                        for n in pair) for pair in items))
            if (not valid_points(points) or type(width_px) is not int
                    or not 1<=width_px<=30
                    or (head is not None and not valid_points(head,3))
                    or (butt is not None and not valid_points(butt,3))):
                raise SplitError("PARTITION_STROKE_INVALID")
            painter=ImageDraw.Draw(mask)
            painter.line([tuple(p) for p in points],fill=255,width=width_px,joint="curve")
            if head is not None:
                painter.polygon([tuple(p) for p in head],fill=255)
            if butt is not None:
                painter.polygon([tuple(p) for p in butt],fill=255)
            # No cruzamento, cada pixel vai APENAS à primeira lança
            # desenhada no plano. Contato/mãos ainda exigem QA.
            mask=ImageChops.subtract(mask,accumulated)
        else:
            raise SplitError("PARTITION_MASK_KIND_INVALID")
        if cfg.get("kind")=="remainder" and cfg is not plan["layers"][-1]:
            raise SplitError("PARTITION_REMAINDER_MUST_BE_LAST")
        accumulated=ImageChops.lighter(accumulated,mask)
        isolated=Image.new("RGBA",im.size,(0,0,0,0))
        isolated.paste(im,(0,0),mask)
        mask_opaque=mask.point(lambda x:255 if x else 0)
        isolated.putalpha(ImageChops.multiply(src_alpha,mask_opaque))
        filename=name+".png"
        isolated.save(dest/filename,optimize=True)
        # Unir com seleção binária, preservando pixels da origem sem blending.
        restored.paste(isolated,(0,0),mask)
        pivot=cfg.get("pivot_xy")
        if pivot is not None and (
            not isinstance(pivot,list) or len(pivot)!=2
            or any(type(v) is not int or v<0 or v>max(width,height) for v in pivot)
        ):
            raise SplitError("PARTITION_PIVOT_INVALID")
        components.append({
            "id":name,"file":filename,"sha256":sha(dest/filename),
            "bbox_global":list(isolated.getbbox()) if isolated.getbbox() else None,
            "pivot_xy_provisional":pivot,
            "animation_ready":False,
            "human_visual_approval":False,
            "pixels_copied_not_generated":True,
            "category":cfg.get("qa_status") or ("rejected_residual" if cfg["kind"]=="remainder"
                        else "draft_anatomical_cutout"),
        })
    # RGB invisível de pixels alfa=0 não é parte da arte visível.
    mismatch=ImageChops.difference(restored,im)
    visible=src_alpha.point(lambda a:255 if a else 0)
    mismatch_visible=Image.composite(mismatch,Image.new("RGBA",im.size,(0,0,0,0)),visible)
    if mismatch_visible.getbbox() is not None:
        raise SplitError("PARTITION_ROUNDTRIP_NOT_EXACT")
    # A imagem recombinada não é uma nova cena: é cópia idêntica da origem.
    qa={
        "schema":"videoforge/existing-pixel-split-qa/v1",
        "channel":plan["channel"],"video_id":plan["video_id"],
        "scene":plan["scene"],"source_file":str(source),
        "source_sha256":sha(source),"canvas":{"width":width,"height":height},
        "pieces":components,"piece_count":len(components),
        "source_mode":("RGB_opaque" if plan.get("allow_opaque_scene_mother") else "RGBA"),
        "neutral_roundtrip_pixel_exact":True,
        "source_pixels_created_or_painted":0,
        "source_pixels_discarded":0,
        "alpha_alignment": "unverified_for_actual_joint_deformation",
        "hidden_anatomy_underlays":"missing",
        "halo_and_background_contamination":"requires_human_review",
        "pivots":"provisional",
        "head_closed_same_image":"not_available_no_eyes_visible",
        "actual_rig":"pending","human_visual_approval":False,
        "video_official":False,"youtube_uploaded":False,
        "explicit_restriction":"Não usar estes recortes diretamente como rig aprovado.",
    }
    (dest/"split-qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("EXISTING_SPLIT_OK",len(components),"parts; original pixels preserved")
    return qa

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--dest",type=Path,required=True)
    args=ap.parse_args()
    try:
        split_existing(args.source,args.plan,args.dest)
        return 0
    except (SplitError,ValueError,OSError) as exc:
        print("EXISTING_SPLIT_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
