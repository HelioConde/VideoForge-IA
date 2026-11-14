"""Reaplica máscaras de peças JÁ EXISTENTES à silhueta alinhada da cena-mãe.

Não cria cabelo/olhos/braços novos: somente transforma coordenadas
das máscaras anteriores e recorta pixels do PNG corrigido. Não aprova rig.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image

BASE=Path(__file__).resolve().parents[1]/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"

class MaskError(ValueError):
    pass
from .split_existing_png_parts import split_existing

OLD = BASE/"assets/cena-01/candidatos/kael-rgba-candidate.png"
NEW = BASE/"assets/cena-01/rig-drafts/kael-alinhado-original/kael-alinhado-mesma-cena-mae-CANDIDATO.png"
QA = BASE/"assets/cena-01/rig-drafts/kael-alinhado-original/qa.json"
OLD_PLAN = BASE/"rig-pixel-partition.json"
NEW_PLAN = BASE/"rig-kael-alinhado-pixel-partition.json"
OUT = BASE/"assets/cena-01/rig-drafts/kael-alinhado-partes"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def bound_alpha(path: Path) -> tuple[int,int,int,int]:
    im=Image.open(path)
    if im.mode!="RGBA" or im.size!=(1024,1536):
        raise MaskError("KAEL_ALPHA_CANVAS_MISMATCH")
    crop=im.getchannel("A").point(lambda v: 255 if v>=190 else 0)
    box=crop.getbbox()
    if not box:
        raise MaskError("KAEL_EMPTY_ALPHA")
    return box

def run(base: Path=BASE) -> dict:
    old=base/"assets/cena-01/candidatos/kael-rgba-candidate.png"
    new=base/"assets/cena-01/rig-drafts/kael-alinhado-original/kael-alinhado-mesma-cena-mae-CANDIDATO.png"
    qa_path=base/"assets/cena-01/rig-drafts/kael-alinhado-original/qa.json"
    old_plan_path=base/"rig-pixel-partition.json"
    dest_plan=base/"rig-kael-alinhado-pixel-partition.json"
    output=base/"assets/cena-01/rig-drafts/kael-alinhado-partes"
    for p in (old,new,qa_path,old_plan_path):
        if p.is_symlink() or not p.is_file():
            raise MaskError("KAEL_REMAP_SOURCE_MISSING")
    if output.exists() or dest_plan.exists():
        raise MaskError("KAEL_REMAP_DEST_EXISTS")
    qa=json.loads(qa_path.read_text(encoding="utf8"))
    old_plan=json.loads(old_plan_path.read_text(encoding="utf8"))
    if qa.get("outputSHA256")!=sha(new) or qa.get("previousCandidateSHA256")!=sha(old):
        raise MaskError("KAEL_REMAP_SHA_MISMATCH")
    if old_plan.get("source_sha256")!=sha(old) or len(old_plan.get("layers",[]))<10:
        raise MaskError("KAEL_REMAP_PLAN_INVALID")
    x0,y0,x1,y1=bound_alpha(old)
    u0,v0,u1,v1=bound_alpha(new)
    sx=(u1-u0)/(x1-x0)
    sy=(v1-v0)/(y1-y0)
    if not (0.53<sx<0.62 and 0.53<sy<0.62):
        raise MaskError("KAEL_REMAP_SCALE_OUTSIDE_SAFE_REGION")
    def xf(pt: list[int]) -> list[int]:
        px=int(round(u0+(pt[0]-x0)*sx))
        py=int(round(v0+(pt[1]-y0)*sy))
        return [max(0,min(1023,px)),max(0,min(1535,py))]
    plan=copy.deepcopy(old_plan)
    plan.update({
        "source_sha256":sha(new),
        "source_path":"assets/cena-01/rig-drafts/kael-alinhado-original/kael-alinhado-mesma-cena-mae-CANDIDATO.png",
        "no_generation":True,
        "human_visual_approval":False,
        "source_is_character_candidate_not_approved":True,
        "geometryRemap":{"fromAlphaBbox":[x0,y0,x1,y1],
                         "toAlphaBbox":[u0,v0,u1,v1],
                         "scaleX":round(sx,6),"scaleY":round(sy,6),
                         "kind":"rough_affine_partition_draft_NOT_pose_matched",
                         "preservesSourceRGB":True},
        "warning":"Recorte determinístico, geometria de partes é aproximação; requer QA anatômico e underlays antes de rig."
    })
    for layer in plan["layers"]:
        if layer["kind"]=="polygon":
            layer["vertices"]=[xf(q) for q in layer["vertices"]]
        if layer.get("pivot_xy") is not None:
            layer["pivot_xy"]=xf(layer["pivot_xy"])
        layer["qa_status"]="draft_affine_requires_anatomical_review" if layer["kind"]!="remainder" else "rejected_unclassified_residual"
    dest_plan.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    qa_parts=split_existing(new,dest_plan,output)
    occupied=[(x["id"],x["bbox_global"]) for x in qa_parts["pieces"]
              if x["id"]!="residual-halo-REJECTED" and x["bbox_global"]]
    if len(occupied)<9:
        raise MaskError("KAEL_REMAP_TOO_FEW_NONEMPTY_PARTS")
    report={
        "schema":"videoforge/remapped-existing-kael-qa/v1",
        "sourceAlignedSHA256":sha(new),
        "sourceOldSHA256":sha(old),
        "parts":qa_parts["piece_count"],
        "nonemptyActiveParts":len(occupied),
        "visiblePixelRoundtrip":qa_parts["neutral_roundtrip_pixel_exact"],
        "imageGenerationCalls":0,
        "humanVisualApproval":False,
        "bodyRigReady":False,
        "headEyeRigReady":False,
        "underlaysAvailable":False,
        "warnings":["Máscaras aproximadas transferidas por escala e translação, não rastreamento anatômico",
                    "Roundtrip prova conservação dos pixels visíveis, não rig articulado",
                    "Não animar antes de revisão de articulações/underlay/cabelo"],
        "status":"draft_only"
    }
    (output/"remap-qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("KAEL_REMAP_SUCCESS",len(occupied),"candidate parts; no image generation")
    return report

if __name__=="__main__":
    try:
        run()
    except (MaskError,ValueError,OSError) as err:
        print("KAEL_REMAP_BLOCKED",str(err),file=sys.stderr)
        raise SystemExit(2)
