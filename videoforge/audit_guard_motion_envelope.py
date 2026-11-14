"""Auditoria geométrica de lacunas em articulações existentes, SEM gerar arte.

A partir dos PNGs já versionados para o tribunal C01, gira máscaras de
antebraço+mão somente em memória (não salva PNGs ou vídeo). Mede quanto
da silhueta de origem desaparece quando a articulação se desloca.
Não supõe que interpolação, máscara ou pose neutra constituem underlay.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"
INPUT=BASE/"rig-guardas-articulacoes-c01.json"
SOURCE=BASE/"rig-selecao-artes-c01.json"
REPORT=BASE/"qa-guardas-envelope-movimento-c01.json"
ALPHA_T=128
ANGLES=(-18,-8,-2,0,2,8,18)
RES=(1024,1536)

class MotionAuditError(ValueError):
    pass

def check_image(rel:str, sha:str)->Image.Image:
    p=Path(rel)
    if p.is_absolute() or ".." in p.parts or p.suffix!=".png":
        raise MotionAuditError("UNSAFE_IMAGE_PATH")
    f=BASE/p
    if f.is_symlink() or not f.is_file():
        raise MotionAuditError("MISSING_IMAGE: "+rel)
    if hashlib.sha256(f.read_bytes()).hexdigest()!=sha:
        raise MotionAuditError("BAD_SHA: "+rel)
    with Image.open(f) as im:
        if im.mode!="RGBA" or im.size!=RES:
            raise MotionAuditError("NOT_CANONICAL_RGBA: "+rel)
        return im.getchannel("A").copy()

def binary(alpha:Image.Image)->Image.Image:
    return alpha.point(lambda v:255 if v>=ALPHA_T else 0)

def count_foreground(mask:Image.Image)->int:
    return mask.histogram()[255]

def union(*layers:Image.Image)->Image.Image:
    if not layers:
        raise MotionAuditError("EMPTY_UNION")
    output=layers[0]
    for layer in layers[1:]:
        output=ImageChops.lighter(output,layer)
    return output

def rotate(alpha:Image.Image,angle:float,pivot:list[int])->Image.Image:
    if angle==0:
        return alpha
    if not isinstance(pivot,list) or len(pivot)!=2 or any(type(v) is not int for v in pivot):
        raise MotionAuditError("UNMEASURED_PIVOT")
    return alpha.rotate(angle,Image.Resampling.NEAREST,expand=False,center=tuple(pivot),fillcolor=0)

def compare_silhouette(reference:Image.Image,moved:Image.Image)->dict[str,int|float]:
    missing=ImageChops.subtract(reference,moved)
    novel=ImageChops.subtract(moved,reference)
    m=count_foreground(missing)
    n=count_foreground(novel)
    total=count_foreground(reference)
    return {"missingExistingOpaquePixels":m,"movedToPreviouslyEmptyPixels":n,
            "silhouettePreservedPct":round(100*(total-m)/total,4) if total else 0}

def audit()->dict[str,Any]:
    if REPORT.exists():
        raise MotionAuditError("REPORT_EXISTS_NO_OVERWRITE")
    if not (BASE/"SEM-GERACAO-NOVAS-IMAGENS.lock").is_file():
        raise MotionAuditError("IMAGE_LOCK_MISSING")
    rig=json.loads(INPUT.read_text(encoding="utf8"))
    selected=json.loads(SOURCE.read_text(encoding="utf8"))
    if rig.get("schema")!="videoforge/guard-rig-draft-kinematics/v1" or rig.get("status")!="DRAFT_BLOCKED":
        raise MotionAuditError("RIG_NOT_DRAFT_BLOCKED")
    if rig.get("hardGates",{}).get("animation_or_render_allowed") is not False:
        raise MotionAuditError("RIG_RENDER_UNEXPECTEDLY_ALLOWED")
    original={row["id"]:row for row in selected["preferredAssets"]["guards"]}
    rows=[]
    for guard in rig["rigRoots"]:
        name=guard["id"]
        source=original[name]
        if guard["flags"]["armMotionReady"] is not False:
            raise MotionAuditError("ARM_MOTION_ALREADY_ENABLED")
        source_alpha=binary(check_image(source["path"],source["sha256"]))
        parts={row["id"]:binary(check_image(row["png"],row["sha256"]))
               for row in guard["parts"]}
        initial=union(*parts.values())
        neutral=compare_silhouette(source_alpha,initial)
        if neutral["missingExistingOpaquePixels"]!=0 or neutral["movedToPreviouslyEmptyPixels"]!=0:
            raise MotionAuditError("NEUTRAL_MASKS_NOT_ROUNDTRIP_EXACT")
        elbow=guard["jointCoordinates"]["elbow"]
        if not isinstance(elbow,list) or len(elbow)!=2:
            raise MotionAuditError("ELBOW_PIVOT_MISSING")
        fixed=union(parts["body-remainder"],parts["upper-arm"])
        moved_arm=union(parts["forearm"],parts["gripping-hand"])
        samples=[]
        for deg in ANGLES:
            rotated=rotate(moved_arm,deg,elbow)
            render_union=union(fixed,rotated)
            metrics=compare_silhouette(source_alpha,render_union)
            metrics["forearmAngleDeg"]=deg
            # O alvo do roteiro inclui 18° de rotação. Medida não autoriza
            # movimento: mostra buracos que apareceriam se a cena fosse animada.
            metrics["underlayMissing"]=deg!=0 and metrics["missingExistingOpaquePixels"]>0
            samples.append(metrics)
        if any(x["missingExistingOpaquePixels"]!=0 for x in samples if x["forearmAngleDeg"]==0):
            raise MotionAuditError("NEUTRAL_ANGLE_EXPOSED_PIXELS")
        target=18 if name=="guarda-esquerdo" else -18
        final=next(x for x in samples if x["forearmAngleDeg"]==target)
        rows.append({
          "id":name,
          "sourceSHA256":source["sha256"],
          "elbowPivotProvisionalXY":elbow,
          "referenceOpaquePixels":count_foreground(source_alpha),
          "neutralRoundtrip":True,
          "proposedTargetForearmRotationDeg":target,
          "targetMissingOpaquePixels":final["missingExistingOpaquePixels"],
          "targetNewlyExposedAreaPixels":final["movedToPreviouslyEmptyPixels"],
          "motionSafeWithoutUnderlay":final["missingExistingOpaquePixels"]==0,
          "samples":samples,
        })
    if len(rows)!=2:
        raise MotionAuditError("TWO_GUARDS_REQUIRED")
    result={
       "schema":"videoforge/guard-motion-hole-envelope/v1",
       "channel":"alchemy-lab",
       "video_id":"mmorpg-conquiste-a-princesa-ep01",
       "scene":"C01",
       "shot":"C01-P04",
       "inputRig":"rig-guardas-articulacoes-c01.json",
       "algorithm":"rotate only arm masks around provisional elbow pivots and measure alpha holes",
       "anglesDeg":list(ANGLES),
       "pixelsRGBGeneratedOrModified":0,
       "imageGenerationCalls":0,
       "writtenImageFiles":0,
       "renderMP4":False,
       "youtubeUploaded":False,
       "humanVisualApproval":False,
       "preservesSourcePNG":True,
       "roundtripNeutralVerified":True,
       "underlaysAvailable":False,
       "rotationsAreExecutedInOfficialRig":False,
       "rigReady":False,
       "officialRenderAllowed":False,
       "limitations":[
          "Conserva a capa, pernas e a pose de cabeça existentes; só antebraço+mão são testados",
          "O teste é de silhueta: não identifica costuras de textura, dedos ocultos nem detalhes inventados",
          "A lança está já cruzada na arte original e não foi rotacionada nem apagada neste teste",
          "Pivôs ainda são estimados, não aprovados",
          "Qualquer buraco exposto sem underlay impede o movimento; zero buracos NÃO equivale a aprovação do rig",
       ],
       "guards":rows,
    }
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("GUARD_HOLE_AUDIT",json.dumps([{"guard":x["id"],"target":x["proposedTargetForearmRotationDeg"],
                   "holes":x["targetMissingOpaquePixels"],"motionSafe":x["motionSafeWithoutUnderlay"]}
                   for x in rows]))
    return result

if __name__=="__main__":
    try:audit()
    except (MotionAuditError,KeyError,ValueError,OSError,ZeroDivisionError) as e:
        print("GUARD_HOLE_AUDIT_BLOCKED",str(e),file=sys.stderr)
        raise SystemExit(2)
