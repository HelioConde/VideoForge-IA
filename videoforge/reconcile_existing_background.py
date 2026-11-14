"""Reconcilia FUNDO EXISTENTE à cena-mãe, sem gerar conteúdo novo via IA.

Fora das máscaras de elenco/props, conserva exatamente os pixels RGB da
cena-mãe. Somente regiões cobertas por personagens/armas usam o fundo
reconstruído já existente. O efeito de borda é matemático e auditável.
Não gera novo cenário, underlay anatômico, rig ou vídeo.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"
SELECTION=BASE/"rig-selecao-artes-c01.json"
OUTPUT=BASE/"assets/cena-01/candidatos/background-reconciliado-CANDIDATO.png"
REPORT=BASE/"qa-background-reconciliado-c01.json"

class BackgroundError(ValueError):
    pass

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verified_png(path:Path,expected_sha:str,mode:str)->np.ndarray:
    if path.is_symlink() or not path.is_file() or sha(path)!=expected_sha:
        raise BackgroundError("ASSET_SOURCE_SHA_MISMATCH: "+str(path))
    with Image.open(path) as im:
        if im.size!=(1024,1536) or im.mode!=mode:
            raise BackgroundError("SOURCE_CANVAS_MODE_INVALID: "+str(path))
        return np.asarray(im).copy()

def reconcile()->dict:
    if OUTPUT.exists() or REPORT.exists():
        raise BackgroundError("RECONCILIATION_ALREADY_EXISTS_NO_OVERWRITE")
    if not (BASE/"SEM-GERACAO-NOVAS-IMAGENS.lock").is_file():
        raise BackgroundError("IMAGE_GENERATION_LOCK_REQUIRED")
    doc=json.loads(SELECTION.read_text(encoding="utf8"))
    if doc.get("schema")!="videoforge/alchemy-episode-scene1-preferred-assets/v1":
        raise BackgroundError("SELECTION_SCHEMA_INVALID")
    archive=json.loads((BASE/"assets/manifesto-arquivo.json").read_text(encoding="utf8"))
    bgs=[x for x in archive["entries"] if x.get("kind")=="reconstructed_background"]
    if len(bgs)!=1:
        raise BackgroundError("RECONSTRUCTED_BACKGROUND_NOT_UNIQUE")
    primary=doc["sourceMother"]
    if bgs[0]["path"]!=str(BASE.relative_to(ROOT)/doc["preferredAssets"]["background"]["path"]):
        raise BackgroundError("BACKGROUND_PROVENANCE_PATH_INVALID")
    mother=verified_png(BASE/primary["path"],primary["sha256"],"RGB")
    background=verified_png(BASE/doc["preferredAssets"]["background"]["path"],
                            bgs[0]["sha256"],"RGB")
    active=[doc["preferredAssets"]["kael"],doc["preferredAssets"]["aldric"]]
    active+=doc["preferredAssets"]["guards"]
    active+=doc["preferredAssets"]["spears"]
    presence=np.zeros((1536,1024),dtype=np.uint8)
    for part in active:
        rgba=verified_png(BASE/part["path"],part["sha256"],"RGBA")
        presence=np.maximum(presence,(rgba[:,:,3]>=30).astype(np.uint8))
    # Dilatação tem margem conservadora nas bordas de armas, cabelo e mantos.
    core=cv2.dilate(presence,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(35,35)))
    outer=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)))
    # Usar fundo já reconstruído no interior, pintura original fora da região.
    weight=cv2.GaussianBlur(core.astype(np.float32),(0,0),sigmaX=5,sigmaY=5)
    weight[core>0]=1.0
    weight[outer==0]=0.0
    weights=weight[:,:,None]
    result=np.rint(np.clip(
       mother.astype(np.float32)*(1-weights)+
       background.astype(np.float32)*weights,0,255)).astype(np.uint8)
    stable=(outer==0)
    if not np.array_equal(result[stable],mother[stable]):
        raise BackgroundError("UNTOUCHED_MOTHER_PIXELS_CHANGED")
    if np.count_nonzero(core)<200_000 or np.count_nonzero(stable)<500_000:
        raise BackgroundError("RECONCILIATION_MASK_IMPLAUSIBLE")
    original_mae=float(np.mean(np.abs(background.astype(np.int16)-mother.astype(np.int16))))
    candidate_mae=float(np.mean(np.abs(result.astype(np.int16)-mother.astype(np.int16))))
    if candidate_mae > original_mae + 0.000001:
        raise BackgroundError("RECONCILIATION_DID_NOT_IMPROVE_RGB_MATCH")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(result,"RGB").save(OUTPUT,optimize=True)
    report={
       "schema":"videoforge/existing-background-reconciliation/v1",
       "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
       "scene":"C01",
       "sourceMotherSHA256":primary["sha256"],
       "reconstructedBackgroundSHA256":bgs[0]["sha256"],
       "resultPNG":str(OUTPUT.relative_to(BASE)),
       "resultSHA256":sha(OUTPUT),
       "sourcePixelsPreservedOutsideMask":True,
       "untouchedMotherPixelCount":int(np.count_nonzero(stable)),
       "insideCharacterOrSpearCorePixelCount":int(np.count_nonzero(core)),
       "featherBandPixelCount":int(np.count_nonzero((outer>0)&(core==0))),
       "canvas":[1024,1536],
       "globalRGBMeanAbsDiffVersusMother":{
          "previousBackground":round(original_mae,4),
          "reconciledCandidate":round(candidate_mae,4),
          "reductionPct":round(100*(original_mae-candidate_mae)/original_mae,2) if original_mae else 0
       },
       "pixelArtSources":["existing_original_scene_RGB","existing_reconstructed_background_RGB"],
       "newImageGenerationCalls":0,
       "newImaginedDetails":False,
       "pixelCompositingOnly":True,
       "humanVisualApproved":False,
       "occludedAnatomyReconstructed":False,
       "officialRigReady":False,
       "renderMP4Approved":False,
       "youtubeUploaded":False,
       "warnings":[
          "Ajuste de cor matemático não equivale a cenário reconstruído artisticamente aprovado",
          "Pode haver halos na transição da máscara e artefatos da reconstrução original",
          "Se um objeto se mover para além do núcleo reconstruído, ainda poderá revelar pixels antigos",
          "Não trocar o background de produção sem inspeção visual frame-a-frame"
       ]
    }
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BACKGROUND_RECONCILED",json.dumps(report["globalRGBMeanAbsDiffVersusMother"]), "no AI generation")
    return report

def main()->int:
    try:reconcile();return 0
    except (BackgroundError,OSError,ValueError,KeyError) as ex:
        print("BACKGROUND_RECONCILE_BLOCKED",str(ex),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
