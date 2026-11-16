"""Image RGB comparison only across SHA-checked, semantically verified polygons.

No automatic APPROVAL: a large color shift can fail; a small shift cannot
prove face, beard, costume or identity match. No file or provider mutations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from io import BytesIO
from pathlib import Path
from .errors import VideoForgeError
from .remake_autopilot import ROOT,EPISODE
from .wardrobe_pixel_audit import group_color

CONTRACT="CONTRATO-ROI-SEMANTICAS-V2.json"
OUTPUT="QA-COMPARACAO-ROI-SEMANTICA-V2.json"
DOC="RELATORIO-ROI-SEMANTICA-V2.md"
ALLOW={"barba","tecido_externo","painel_central","corpete_roxo_palacio"}

def polygon_metric(base:Path,source:dict)->dict:
    from PIL import Image,ImageDraw
    file=base/source["path"]
    if (file.is_symlink() or not file.is_file()
            or not 50<=file.stat().st_size<=16_000_000):
        raise VideoForgeError("SEMANTIC_ROI_SOURCE_INVALID")
    data=file.read_bytes()
    if hashlib.sha256(data).hexdigest()!=source["sha256"]:
        raise VideoForgeError("SEMANTIC_ROI_SOURCE_SHA_MISMATCH")
    with Image.open(BytesIO(data)) as img:
        img.load()
        if img.format!="PNG":
            raise VideoForgeError("SEMANTIC_ROI_MUST_BE_PNG")
        image=img.convert("RGB")
    width,height=image.size
    poly=source.get("polygon")
    if (not isinstance(poly,list) or not 3<=len(poly)<=100 or
            any(not isinstance(p,list) or len(p)!=2 or
                type(p[0]) is not int or type(p[1]) is not int or
                not 0<=p[0]<width or not 0<=p[1]<height for p in poly)):
        raise VideoForgeError("SEMANTIC_ROI_POLYGON_INVALID")
    mask=Image.new("1",(width,height),0)
    ImageDraw.Draw(mask).polygon([tuple(x) for x in poly],fill=1)
    # Work directly from original RGB pixels without interpolated resize.
    pix=image.load()
    mp=mask.load()
    groups=Counter()
    selected=0
    for y in range(height):
        for x in range(width):
            if mp[x,y]:
                selected+=1
                groups[group_color(*pix[x,y])]+=1
    if selected<128 or selected/(width*height)>.35:
        raise VideoForgeError("SEMANTIC_ROI_MASK_TOO_SMALL_OR_BROAD")
    return {"pixels":selected,"fraction_of_frame":round(selected/(width*height),5),
            "color_share_percent":{
                key:round(100*groups[key]/selected,2)
                for key in ("red","very_dark","purple_or_magenta","other")
            },
            "source_sha256":source["sha256"],"image_dimensions":[width,height]}

def pair_result(base:Path,row:dict)->dict:
    region=row["semantic_region"]
    actor=row["actor"]
    if region not in ALLOW or actor not in ("aldric","elara"):
        raise VideoForgeError("SEMANTIC_ROI_REGION_UNKNOWN")
    a,b=row["source_a"],row["source_b"]
    if not (a.get("pose_verified") is True and b.get("pose_verified") is True
            and a.get("semantic_polygon_verified") is True
            and b.get("semantic_polygon_verified") is True):
        return {"actor":actor,"region":region,
                "status":"EVIDENCIA_INSUFICIENTE",
                "reason":"pair_pose_or_semantic_polygon_not_yet_verified",
                "source_a_sha256":a["sha256"],"source_b_sha256":b["sha256"],
                "auto_approved":False,"official_art_usable":False}
    m1=polygon_metric(base,a)
    m2=polygon_metric(base,b)
    deltas={
        key:round(abs(m1["color_share_percent"][key] -
                      m2["color_share_percent"][key]),2)
        for key in ("red","very_dark","purple_or_magenta")
    }
    # Risk of color swap is high when a dominant color proportion differs.
    severe=max(deltas.values())>=40
    return {"actor":actor,"region":region,
            "status":"REPROVADO_POR_DIVERGENCIA_CROMATICA" if severe
                     else "REVISAO_VISUAL_AINDA_NECESSARIA",
            "metric_a":m1,"metric_b":m2,"deltas_percentage_points":deltas,
            "evidence":"sha_verified_semantically_reviewed_roi",
            "automatic_rejection":severe,
            "auto_approved":False,
            "official_art_usable":False}

def run(root:Path=ROOT,sync=False)->dict:
    root=Path(root)
    ep=root/EPISODE
    path=ep/CONTRACT
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("SEMANTIC_ROI_CONTRACT_MISSING")
    contract=json.loads(path.read_text(encoding="utf-8"))
    if (contract.get("schema")!="videoforge/wardrobe-semantic-roi-pairs/v1"
            or contract.get("preexisting_character_bible_grounded_rejected") is not True
            or contract.get("color_change_cannot_establish_complete_identity_approval") is not True):
        raise VideoForgeError("SEMANTIC_ROI_CONTRACT_UNSAFE")
    pairs=contract.get("pairs",[])
    if (len(pairs)!=4
            or [(p["actor"],p["semantic_region"]) for p in pairs]!=[
                ("aldric","barba"),("aldric","tecido_externo"),
                ("aldric","painel_central"),("elara","corpete_roxo_palacio")]):
        raise VideoForgeError("SEMANTIC_ROI_EXPECTED_PAIRS_MISSING")
    result=[pair_result(ep,row) for row in pairs]
    output={
        "schema":"videoforge/wardrobe-semantic-roi-qa/v1",
        "status":"semantic_masks_not_yet_verified" if all(
                r["status"]=="EVIDENCIA_INSUFICIENTE" for r in result)
                 else "semantic_color_comparison_completed_with_open_review",
        "pairs":result,
        "known_owner_rejections_still_active":True,
        "automatic_approved_art_count":0,
        "automatic_rejected_pairs":sum(x.get("automatic_rejection") is True for x in result),
        "unverified_pairs":sum(x["status"]=="EVIDENCIA_INSUFICIENTE" for x in result),
        "uses_only_existing_sha_verified_images":True,
        "new_image_generation":False,"provider_calls":0,
        "official_mp4":False,"youtube_uploaded":False,
    }
    if sync:
        output_path=ep/OUTPUT
        doc=ep/DOC
        if output_path.is_symlink() or doc.is_symlink():
            raise VideoForgeError("SEMANTIC_ROI_OUTPUT_SYMLINK")
        txt=json.dumps(output,ensure_ascii=False,indent=2)+"\n"
        if not output_path.exists() or output_path.read_text(encoding="utf-8")!=txt:
            output_path.write_text(txt,encoding="utf-8")
        lines=["# EP01 V2 — comparação semântica por região","",
               "O comparador foi instalado. Ele reprova diferenças cromáticas fortes somente após validação de dois PNGs SHA, pose/variante e polígonos da MESMA parte do corpo.","",
               "| Personagem | Região | Resultado |",
               "|---|---|---|"]
        for item in result:
            lines.append("| "+item["actor"]+" | "+item["region"]+" | "+item["status"]+" |")
        lines += ["",
                  "Sem verificação semântica da barba, exterior/centro e do corpete, o resultado é evidência insuficiente; NÃO aprovado.",
                  "Uma diferença numérica pequena ainda não comprova que a roupa, o rosto ou a barba estão corretos.",
                  "O filtro de cores usa limiar inicial de 40 pontos percentuais de diferença por grupo e deve ser calibrado com exemplos rotulados.",
                  "A reprovação prévia do rei e da princesa permanece ativa.",
                  "Ver [pranchas de anotação](REVISAR-ROI-FIGURINOS-V2.md) e [contrato em JSON](CONTRATO-ROI-SEMANTICAS-V2.json).",
                  ""]
        prose="\n".join(lines)
        if not doc.exists() or doc.read_text(encoding="utf-8")!=prose:
            doc.write_text(prose,encoding="utf-8")
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    args=p.parse_args()
    obj=run(sync=args.sync)
    print("SEMANTIC_ROI_QA",json.dumps({
        "regions":len(obj["pairs"]),"pending":obj["unverified_pairs"],
        "approved":0,"provider_calls":0,
    }))

if __name__=="__main__":
    main()
