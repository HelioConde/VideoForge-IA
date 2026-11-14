"""QA de recomposição da cena 1 usando somente artes já arquivadas.

Não gera, redesenha, recorta nem regrava imagens. Apenas lê RGBA e RGB,
recompõe em memória e publica métricas JSON. Aprovado artístico fica falso.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
EPISODE=ROOT/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"
DOC=EPISODE/"rig-selecao-artes-c01.json"
REPORT=EPISODE/"qa-recomposicao-c01.json"
SIZE=(1024,1536)
THRESHOLDS=(12,24,48)

class QAError(ValueError):
    pass

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_png(asset:dict[str,Any],rgba:bool)->np.ndarray:
    rel=Path(asset["path"])
    if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower()!=".png":
        raise QAError("UNSAFE_PATH: "+str(rel))
    path=EPISODE/rel
    if path.is_symlink() or not path.is_file():
        raise QAError("SOURCE_MISSING: "+str(rel))
    if sha256(path)!=asset["sha256"]:
        raise QAError("SHA_MISMATCH: "+str(rel))
    with Image.open(path) as im:
        if im.size!=SIZE or im.mode not in (("RGBA",) if rgba else ("RGB","RGBA")):
            raise QAError("BAD_PIXEL_FORMAT: "+str(rel))
        return np.asarray(im.convert("RGBA" if rgba else "RGB"),dtype=np.uint8).copy()

def composite_rgb(background:np.ndarray,foreground:np.ndarray)->np.ndarray:
    """RGBA sobre RGB via straight alpha, sem alterar os PNGs de origem."""
    a=foreground[:,:,3:4].astype(np.float32)/255.
    return background*(1.0-a)+foreground[:,:,:3].astype(np.float32)*a

def stat_region(diff:np.ndarray,region:tuple[int,int,int,int])->dict[str,Any]:
    x0,y0,x1,y1=region
    sample=diff[y0:y1,x0:x1,:]
    if sample.size==0:
        raise QAError("EMPTY_REGION")
    per_px=np.max(sample,axis=2)
    return {
        "rectXYXY":[x0,y0,x1,y1],
        "meanAbsoluteRGB":round(float(np.mean(sample)),3),
        "pixelErrorMaxMean":round(float(np.mean(per_px)),3),
        "fractionAnyChannelGT12":round(float(np.mean(per_px>12)),6),
        "fractionAnyChannelGT24":round(float(np.mean(per_px>24)),6),
        "fractionAnyChannelGT48":round(float(np.mean(per_px>48)),6),
        "maxChannelError":int(np.max(sample)),
    }

def audit()->dict[str,Any]:
    if not (EPISODE/"SEM-GERACAO-NOVAS-IMAGENS.lock").exists():
        raise QAError("NO_GENERATION_POLICY_LOCK_MISSING")
    if REPORT.exists():
        raise QAError("QA_REPORT_ALREADY_EXISTS_NO_OVERWRITE")
    d=json.loads(DOC.read_text(encoding="utf8"))
    if d.get("schema")!="videoforge/alchemy-episode-scene1-preferred-assets/v1":
        raise QAError("BAD_SELECTION_SCHEMA")
    p=d["preferredAssets"]
    source=read_png(d["sourceMother"],False)
    background=read_png({"path":p["background"]["path"],
                         "sha256":d.get("backgroundSHA256") or
                         json.loads((EPISODE/"assets/manifesto-arquivo.json").read_text(encoding="utf8"))[
                          "entries"][next(i for i,x in enumerate(json.loads(
                           (EPISODE/"assets/manifesto-arquivo.json").read_text(encoding="utf8"))[
                           "entries"]) if x.get("kind")=="reconstructed_background")]["sha256"]},
                       False)
    # Ordem de oclusão provisória: fundo, rei, guardas, Kael, lanças.
    layers=[
        ("aldric",p["aldric"]),
        ("guarda_esquerdo",p["guards"][0]),
        ("guarda_direito",p["guards"][1]),
        ("kael",p["kael"]),
        ("lanca_direita",p["spears"][1]),
        ("lanca_esquerda",p["spears"][0]),
    ]
    # RGBA em coordenadas idênticas da mãe, sem alongamento.
    canvas=background.astype(np.float32)
    alphas={}
    for label,asset in layers:
        im=read_png(asset,True)
        alphas[label]=im[:,:,3].astype(np.uint8)
        canvas=composite_rgb(canvas,im)
    canvas=np.rint(np.clip(canvas,0,255)).astype(np.uint8)
    delta=np.abs(canvas.astype(np.int16)-source.astype(np.int16)).astype(np.uint8)
    roi={
        "fullFrame":(0,0,1024,1536),
        "kingAndThrone":(310,240,740,680),
        "guardLeft":(0,370,435,1240),
        "guardRight":(595,370,1024,1240),
        "kael":(282,720,686,1440),
        "crossedSpears":(290,285,765,860),
        "unoccupiedUpper":(0,0,1024,240),
    }
    metrics={label:stat_region(delta,reg) for label,reg in roi.items()}
    pairs={}
    for label_a,label_b in (("aldric","guarda_esquerdo"),("aldric","guarda_direito"),
                            ("kael","lanca_direita"),("kael","lanca_esquerda"),
                            ("guarda_esquerdo","lanca_esquerda"),
                            ("guarda_direito","lanca_direita"),
                            ("lanca_esquerda","lanca_direita")):
        a=alphas[label_a]>=128
        b=alphas[label_b]>=128
        overlap=int(np.count_nonzero(a&b))
        pairs[label_a+"__"+label_b]={
            "opaqueOverlapPixels":overlap,
            "firstLayerOpaquePixels":int(np.count_nonzero(a)),
            "secondLayerOpaquePixels":int(np.count_nonzero(b)),
            "potentialOcclusionContact":overlap>0,
        }
    union=np.zeros((1536,1024),dtype=bool)
    for x in alphas.values():
        union|=(x>=128)
    diff_background=np.abs(background.astype(np.int16)-source.astype(np.int16))
    unaffected=~union
    if not np.any(unaffected):
        raise QAError("ALL_PIXELS_COVERED_INVALID")
    report={
        "schema":"videoforge/scene1-neutral-composition-audit/v1",
        "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
        "scene":"C01","sourceSHA256":d["sourceMother"]["sha256"],
        "mode":"read-only in-memory neutral composite","imageGenerationCalls":0,
        "createdPixelFiles":0,"renderMP4":False,"youtubeUploaded":False,
        "selectionPath":"rig-selecao-artes-c01.json",
        "compositionOrder":[x[0] for x in layers],
        "metricsByRegion":metrics,"alphaOverlapPairs":pairs,
        "unoccupiedBackgroundMeanAbsoluteRGB":round(float(np.mean(diff_background[unaffected])),3),
        "unoccupiedPixelFraction":round(float(np.mean(unaffected)),6),
        "humanVisualApproval":False,
        "readyForMeshRig":False,
        "readyForOfficialRender":False,
        "diagnosis":[
            "A recomposição neutra é diagnóstico, não prova de camadas animáveis.",
            "A ordem de oclusão atual é provisória; lanças/luvas podem precisar de fatias de frente e trás.",
            "A reconstrução oculta sob mãos, braços e tecidos ainda é ausente.",
            "Qualquer desvio alto exige limpeza local de máscaras/oclusões sem chamar gerador de imagens.",
            "Não sobrepor sprites à imagem-mãe com personagens já desenhados.",
        ],
    }
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("SCENE1_COMPOSITE_AUDIT",json.dumps({
        "fullMAE":metrics["fullFrame"]["meanAbsoluteRGB"],
        "framePixelGT24":metrics["fullFrame"]["fractionAnyChannelGT24"],
        "kingMAE":metrics["kingAndThrone"]["meanAbsoluteRGB"],
        "sourcePixels":int(1024*1536),
        "imageCalls":0,"artisticApproval":False
    }))
    return report

def main()->int:
    try:
        audit()
        return 0
    except (QAError,ValueError,OSError,KeyError,IndexError) as ex:
        print("SCENE1_COMPOSITE_QA_BLOCKED",str(ex),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
