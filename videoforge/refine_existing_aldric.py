"""Extrai candidato Aldric com GrabCut local usando SOMENTE a cena-mãe.

Rosto, manto, tronco e botas são recortes dos próprios pixels originais.
Trono/lion armrests devem continuar separados; limiares conservadores.
NÃO é uma reconstrução das áreas ocultas e NÃO libera rig/MP4.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image

BASE=Path(__file__).resolve().parents[1]/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"
MOTHER_SHA="544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf"

class AldricCutError(ValueError): pass

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cut(root:Path=BASE)->dict:
    source=root/"assets/cenas-mae/cena-01.png"
    dest=root/"assets/cena-01/rig-drafts/aldric-origem"
    if source.is_symlink() or not source.is_file() or sha(source)!=MOTHER_SHA:
        raise AldricCutError("MOTHER_SOURCE_SHA_INVALID")
    if dest.exists() or dest.is_symlink():
        raise AldricCutError("ALDRIC_DEST_EXISTS")
    img=Image.open(source)
    if img.mode!="RGB" or img.size!=(1024,1536):
        raise AldricCutError("MOTHER_IMAGE_CANVAS_INVALID")
    scene=np.asarray(img)
    H,W=scene.shape[:2]
    grab=np.zeros((H,W),dtype=np.uint8)
    outer=np.array([(482,272),(530,269),(552,299),(557,343),(595,350),
        (626,373),(657,407),(648,436),(676,487),(697,570),(716,626),
        (334,626),(351,565),(367,495),(380,430),(389,393),(424,366),
        (460,351),(477,333)],dtype=np.int32)
    cv2.fillPoly(grab,[outer],cv2.GC_PR_BGD)
    candidates=[
        [(493,299),(544,299),(549,341),(491,343)],
        [(460,363),(583,364),(597,415),(445,416)],
        [(474,426),(585,429),(585,583),(473,579)],
        [(368,492),(436,479),(432,588),(349,606)],
        [(611,482),(671,487),(698,612),(635,611)],
        [(402,405),(437,403),(443,440),(401,445)],
        [(605,404),(637,409),(646,446),(607,448)],
        [(463,577),(615,575),(624,620),(442,621)],
    ]
    for polygon in candidates:
        cv2.fillPoly(grab,[np.array(polygon,dtype=np.int32)],cv2.GC_PR_FGD)
    sure=[(499,309,540,338),(485,373,564,397),(493,431,558,488),
          (495,510,557,553),(406,418,427,436),(613,420,627,437),
          (469,590,487,606),(576,589,608,609)]
    for x1,y1,x2,y2 in sure:
        cv2.rectangle(grab,(x1,y1),(x2,y2),cv2.GC_FGD,-1)
    # Impedir inclusão do encosto da cadeira e brasões dos leões.
    for x1,y1,x2,y2 in [(417,211,476,333),(556,218,609,340),
                         (350,425,398,513),(647,425,690,514)]:
        cv2.rectangle(grab,(x1,y1),(x2,y2),cv2.GC_BGD,-1)
    cv2.setRNGSeed(314159)
    bgd=np.zeros((1,65),dtype=np.float64)
    fgd=np.zeros((1,65),dtype=np.float64)
    bgr=cv2.cvtColor(scene,cv2.COLOR_RGB2BGR)
    cv2.grabCut(bgr,grab,None,bgd,fgd,4,cv2.GC_INIT_WITH_MASK)
    mask=np.where((grab==cv2.GC_FGD)|(grab==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    components,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
    selected=int(labels[442,514])
    if selected==0 or selected>=components:
        raise AldricCutError("ALDRIC_CORE_DISCONNECTED")
    size=int(stats[selected,cv2.CC_STAT_AREA])
    if not 45_000<=size<=90_000:
        raise AldricCutError("ALDRIC_FOREGROUND_AREA_OUTSIDE_RANGE")
    alpha=np.where(labels==selected,255,0).astype(np.uint8)
    alpha=cv2.morphologyEx(alpha,cv2.MORPH_CLOSE,np.ones((3,3),dtype=np.uint8))
    smooth=cv2.GaussianBlur(alpha,(3,3),0.55)
    smooth[cv2.erode(alpha,np.ones((3,3),dtype=np.uint8))==255]=255
    output=np.dstack((scene,smooth))
    dest.mkdir(parents=True)
    f=dest/"aldric-RGB-da-mae-CANDIDATO.png"
    Image.fromarray(output,"RGBA").save(f,optimize=True)
    x,y,w,h=[int(v) for v in stats[selected,:4]]
    report={"schema":"videoforge/aldric-deterministic-cut-qa/v1",
        "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
        "scene":"cena-01","imageGenerationCalls":0,
        "sourceSceneSHA256":MOTHER_SHA,
        "output":f.name,"outputSHA256":sha(f),
        "sourceRGBUnmodified":True,
        "segmentation":"OpenCV GrabCut with foreground and throne-exclusion seeds",
        "coreAreaPixels":size,"bboxGlobal":[x,y,x+w,y+h],
        "tronoOverdrawMayRemain":True,"hiddenBodyPartsReconstructed":False,
        "facePartsRigged":False,"humanVisualApproval":False,
        "officialRig":False,"youtubeUploaded":False,
        "status":"candidate_requires_throne_edge_and_lion_armrest_review",
        "warnings":["A máscara pode cortar partes do manto ou conter pedaços do braço do trono",
                    "A textura contém somente pixels da mãe, não preenche regiões do corpo escondidas",
                    "Revisar sobreposição com trono vazio e limpar elementos duplicados antes de rig"] }
    (dest/"qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ALDRIC_SOURCE_CUT_CANDIDATE",size,report["bboxGlobal"],"no image generation")
    return report

if __name__=="__main__":
    try: cut()
    except (AldricCutError,ValueError,OSError,cv2.error) as e:
        print("ALDRIC_CUT_BLOCKED",str(e),file=sys.stderr)
        raise SystemExit(2)
