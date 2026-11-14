"""Isola guardas a partir de PIXELS EXISTENTES (sem desenho/IA).

Fonte RGB: cena-mãe original, nunca o recorte de grupo reilustrado.
O alfa do antigo recorte serve APENAS como sugestão de máscara espacial.
Arestas são suavizadas deterministicamente; armaduras, rostos, tecidos e
cores são sempre copiados do PNG original. Contato/underlays permanecem
pendentes: candidatos não são rigs aprovados.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "canal" / "alchemy-lab" / "videos" / "mmorpg-conquiste-a-princesa-ep01"
MOTHER = BASE / "assets/cenas-mae/cena-01.png"
GROUP = BASE / "assets/cena-01/candidatos/character-group-REJECTED.png"
SPEARS = BASE / "assets/cena-01/rig-drafts/lancas"
OUTPUT = BASE / "assets/cena-01/rig-drafts/guardas-refinados"
MOTHER_SHA = "544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf"
# A imagem de grupo serve como máscara CANDIDATA, jamais como textura final.
GROUP_SHA = "e9d0f6a1e69a4a49e30e8744be6b3ae3b4c8caf46bf1ebcf69fee3572889bcb9"
GUARDS = (
    {"id": "guarda-esquerdo", "rect": (0,395,420,1233),
     "seed": (157,600), "spear": "lanca-guarda-esquerdo-CANDIDATE.png"},
    {"id": "guarda-direito", "rect": (607,395,1024,1233),
     "seed": (877,610), "spear": "lanca-guarda-direito-CANDIDATE.png"},
)

class MaskError(ValueError):
    pass

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verified_image(path: Path, expected: str, mode: str) -> Image.Image:
    if path.is_symlink() or not path.is_file():
        raise MaskError("SOURCE_MISSING_OR_SYMLINK:" + str(path))
    if digest(path) != expected:
        raise MaskError("SOURCE_SHA_MISMATCH:" + str(path))
    im = Image.open(path)
    if im.size != (1024,1536) or im.mode != mode:
        raise MaskError("SOURCE_MODE_OR_SIZE_INVALID:" + str(path))
    im.load()
    return im

def isolate_guard(mother: np.ndarray, alpha_guide: np.ndarray, definition: dict) -> tuple[np.ndarray,np.ndarray,dict]:
    x1,y1,x2,y2 = definition["rect"]
    sx,sy = definition["seed"]
    if not(x1 <= sx < x2 and y1 <= sy < y2):
        raise MaskError("SEED_OUTSIDE_ROI")
    # Recorte de grupo contém sombras e trono. Alfa >= 200 recupera
    # contorno principal; componentes soltos são descartados.
    local = np.ascontiguousarray((alpha_guide[y1:y2,x1:x2] >= 200).astype("uint8"))
    count,labels,stats,_ = cv2.connectedComponentsWithStats(local,8)
    label = int(labels[sy-y1,sx-x1])
    if label == 0 or label >= count:
        raise MaskError("GUARD_SEED_NOT_FOREGROUND")
    pixels = int(stats[label, cv2.CC_STAT_AREA])
    if pixels < 90_000 or pixels > 200_000:
        raise MaskError("GUARD_COMPONENT_AREA_UNEXPECTED:" + str(pixels))
    cropmask = (labels==label).astype("uint8")*255
    # Não dilatar: área adicional pode copiar pedra/mão de outro personagem.
    cropmask = cv2.morphologyEx(cropmask,cv2.MORPH_CLOSE,
                                np.ones((3,3),dtype=np.uint8))
    full=np.zeros((1536,1024),dtype=np.uint8)
    full[y1:y2,x1:x2]=cropmask
    # Antialias de bordas do recorte, sem alterar nenhuma cor RGB original.
    soft=cv2.GaussianBlur(full,(3,3),0.55)
    soft[cv2.erode(full,np.ones((3,3),dtype=np.uint8))==255]=255
    a = np.dstack((mother,soft.astype(np.uint8)))
    return a,soft,{"componentPixelCount":pixels,
                   "maskForegroundPixels":int(np.count_nonzero(soft)),
                   "bbox":[int(v) for v in (x1+stats[label,cv2.CC_STAT_LEFT],
                     y1+stats[label,cv2.CC_STAT_TOP],
                     x1+stats[label,cv2.CC_STAT_LEFT]+stats[label,cv2.CC_STAT_WIDTH],
                     y1+stats[label,cv2.CC_STAT_TOP]+stats[label,cv2.CC_STAT_HEIGHT])],
                   "seed":list(definition["seed"]),"roi":list(definition["rect"])}

def run(root: Path=BASE, output: Path=OUTPUT) -> dict:
    if output.is_symlink() or output.exists():
        raise MaskError("REFINED_GUARDS_OUTPUT_ALREADY_EXISTS")
    mother=verified_image(root/"assets/cenas-mae/cena-01.png",MOTHER_SHA,"RGB")
    group=verified_image(root/"assets/cena-01/candidatos/character-group-REJECTED.png",GROUP_SHA,"RGBA")
    source=np.asarray(mother)
    guide=np.asarray(group.getchannel("A"))
    # Não consumir modelos nem preencher áreas anteriormente ocultas.
    prepared=[]
    for definition in GUARDS:
        rgba, alpha, metrics=isolate_guard(source,guide,definition)
        id_=definition["id"]
        candidate=Image.fromarray(rgba,"RGBA")
        spear_path=root/"assets/cena-01/rig-drafts/lancas"/definition["spear"]
        if spear_path.is_symlink() or not spear_path.is_file():
            raise MaskError("SPEAR_MASK_NOT_FOUND")
        spear=Image.open(spear_path)
        if spear.mode!="RGBA" or spear.size!=(1024,1536):
            raise MaskError("SPEAR_MASK_INVALID")
        spear_a=np.asarray(spear.getchannel("A"))
        # Preparação de versão S/ lança: buracos reais são conservados como
        # defeito explícito, não retocados falsamente.
        overlap=(spear_a>0) & (alpha>0)
        alpha_no_spear=alpha.copy()
        alpha_no_spear[overlap]=0
        second=Image.fromarray(np.dstack((source,alpha_no_spear)),"RGBA")
        metrics["spearOverlapRemovedPixels"]=int(np.count_nonzero(overlap))
        metrics["spearHolesNeedUnderlay"]=True
        metrics["sourceRGBUnmodified"]=True
        metrics["groupRGBAUsedAsTexture"]=False
        metrics["humanVisualApproved"]=False
        metrics["rigReady"]=False
        prepared.append((id_,candidate,second,metrics))
    output.mkdir(parents=True)
    records=[]
    for id_,first,second,metrics in prepared:
        p1=output/(id_+"-origem-rgb-candidato.png")
        p2=output/(id_+"-sem-lanca-BURACOS.png")
        first.save(p1,optimize=True)
        second.save(p2,optimize=True)
        records.append({"id":id_,
            "sourceMotherSHA256":MOTHER_SHA,"maskGuideSHA256":GROUP_SHA,
            "candidateRGBFromMother":p1.name,
            "candidateSHA256":digest(p1),
            "candidateNoSpearWithHoles":p2.name,
            "candidateNoSpearSHA256":digest(p2),
            "qa":metrics})
    report={"schema":"videoforge/deterministic-guard-extraction/v1",
        "channel":"alchemy-lab",
        "video_id":"mmorpg-conquiste-a-princesa-ep01",
        "scene":"cena-01","imageGenerationCalls":0,
        "sourcing":"100pct_RGB_from_original_mother; alpha_from_existing_group_mask",
        "guardCount":len(records),"technicalStatus":"candidate_needs_visual_review",
        "humanVisualApproval":False,"underlays":False,
        "officialRig":False,"mp4Rendered":False,"youtubeUploaded":False,
        "limitations":[
            "Há lanças desenhadas por cima das luvas na própria cena-mãe",
            "Sprites sem lança contêm buracos que exigem reconstrução fiel de material oculto",
            "A máscara de grupo foi derivada por IA anteriormente e pode errar cabelos ou dobras",
            "A separação do corpo em cabeça, mãos, braços e roupa ainda não ocorreu",
            "NUNCA sobrepor recortes sobre cena-mãe original que já contém personagens",
        ],"guards":records}
    (output/"qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("GUARD_PIXELS_REFINEMENT_OK",len(records),"guards, no IA, visual QA pending")
    return report

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=BASE)
    p.add_argument("--output",type=Path,default=OUTPUT)
    x=p.parse_args()
    try:
        run(x.root,x.output)
        return 0
    except (MaskError,OSError,ValueError,cv2.error) as ex:
        print("GUARD_PIXELS_REFINEMENT_BLOCKED",str(ex),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
