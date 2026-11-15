"""Inventário dos 37 planos × 14 imagens-mãe existentes (somente leitura).

Nunca confunde referência geral da cena com imagem-mãe específica do
plano/câmera, nem infere identidade aprovada a partir de um PNG.
O resultado é um documento de produção, não uma aprovação de render.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from .cinematic_direction import load_plan,ROOT
from .cinematic_shot_assets import build_edl,_png_valid,validate_edl
from .errors import VideoForgeError

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"
REPORT="qa-inventario-tomadas-cinema.json"
PRIORITY={"close_up":1,"extreme_close_up":1,"over_shoulder":2,
          "two_shot":2,"insert":2,"low_angle":3,"action":3,
          "medium":3,"tracking":3,"match_cut":3,"wide":4}

def audit(root:Path=ROOT)->dict:
    base=root/"canal"/CHANNEL/"videos"/VIDEO
    plan=load_plan(CHANNEL,VIDEO,root)
    edl=build_edl(CHANNEL,VIDEO,root)
    validate_edl(edl)
    if plan is None or edl["shotCount"]!=37:
        raise VideoForgeError("CINEMATIC_INVENTORY_PLAN_NOT_VALID")
    reference_status=plan["reference_approval"]
    mother_index={}
    for n in range(1,15):
        rel=f"assets/cenas-mae/cena-{n:02d}.png"
        p=base/rel
        if not p.is_file() or p.is_symlink():
            raise VideoForgeError("CINEMATIC_LEGACY_MOTHER_NOT_FOUND:"+rel)
        digest=sha256(p.read_bytes()).hexdigest()
        if not _png_valid(p,digest,False,(1024,1536)):
            raise VideoForgeError("CINEMATIC_LEGACY_MOTHER_INVALID:"+rel)
        mother_index[f"C{n:02d}"]={
            "path":rel,"sha256":digest,
            "role":"archived_scene_reference_only",
            "shotSpecificAngleVerified":False,
            "canonicalIdentityVerified":False,
            "automaticallyRenderable":False,
        }
    available_legacy_rgba=sorted(
        p.relative_to(base).as_posix()
        for p in (base/"assets"/"cena-01"/"rig-drafts").rglob("*.png")
        if p.is_file() and not p.is_symlink()
    )
    direct=[]
    missing=0
    types=Counter()
    priorities=Counter()
    for original in edl["shots"]:
        item=next(s for s in plan["shots"] if s["id"]==original["id"])
        if original["type"]=="black":
            direct.append({
                "id":original["id"],"type":"black",
                "renderableWithoutArt":True,"status":"black_no_png_needed",
                "priority":None,
            })
            continue
        missing+=int(not original["renderAllowed"])
        kinds=item["shot_type"]
        types[kinds]+=1
        priority=PRIORITY[kinds]
        priorities[str(priority)]+=1
        direct.append({
            "id":original["id"],
            "scene":original["scene"],
            "shotType":kinds,
            "focus":item["primary_focus"],
            "priority":priority,
            "sourceReferenceOnly":mother_index[original["scene"]]["path"],
            "sourceReferenceSha256":mother_index[original["scene"]]["sha256"],
            "sourceLegacyReferenceIsNotApprovedShotArt":True,
            "requiresDifferentCameraArtworkIfReferenceAngleDiffers":True,
            "requiredMother":original["assetPaths"]["mother"],
            "requiredBackground":original["assetPaths"]["background"],
            "requiredRig":original["assetPaths"]["rig"],
            "requiredQA":original["assetPaths"]["qa"],
            "ownMotherPresent":not (
                "SHOT_MOTHER_MISSING" in original["blockers"]
            ),
            "renderApproved":original["renderAllowed"],
            "blockers":original["blockers"],
        })
    if len(available_legacy_rgba)<20:
        raise VideoForgeError("CINEMATIC_INVENTORY_LEGACY_ART_NOT_INDEXED")
    visual_count=sum(types.values())
    blocker_counts=Counter(b for shot in edl["shots"] for b in shot["blockers"])
    result={
        "schema":"videoforge/scene-reference-triage/v1",
        "channel":CHANNEL,"video_id":VIDEO,
        "source":"direcao-cinematografica-planos.json",
        "edl":"timeline-cinematografica.json",
        "imageGenerationCalls":0,"writtenPNGs":0,
        "legacySceneMotherCount":len(mother_index),
        "legacySceneMothers":mother_index,
        "legacyScene01DraftPNGs":len(available_legacy_rgba),
        "legacyScene01DraftsNotApproved":True,
        "shotsTotal":len(direct),
        "blackOnlyShots":len(direct)-visual_count,
        "visualShots":visual_count,
        "visualShotsPendingApproval":missing,
        "visualShotsApproved":visual_count-missing,
        "blockerCounts":dict(sorted(blocker_counts.items())),
        "faceCloseups":types.get("close_up",0)+types.get("extreme_close_up",0),
        "shotTypes":dict(sorted(types.items())),
        "productionPriorities":dict(sorted(priorities.items())),
        "canonicalReferenceConflict":reference_status["canonical_identity_conflict_detected"],
        "approvedChatImagesAvailableInRepo":edl["canonicalReferencesArchived"],
        "newImageGenerationAllowed":False,
        "officialMP4Allowed":edl["renderOfficialAllowed"],
        "rules":[
            "14 mães antigas servem como referência de local e paleta; não há 36 câmeras independentes verificadas",
            "Não fazer crop/zoom de rosto pequeno na mãe geral para fingir o close",
            "Comparar cada plano com o eixo, direção, posição dos olhos e luz da cena anterior",
            "Antes de produzir novos closes, resolver versão de figurino e rosto de Kael/Elara",
            "C01 conta com rascunhos de partes de Kael/guardas/rei: não são rigs de 37 tomadas",
            "Não gerar nenhum PNG enquanto SEM-GERACAO-NOVAS-IMAGENS.lock estiver ativo",
        ],
        "shots":direct,
    }
    return result

def main()->int:
    try:
        data=audit()
        path=ROOT/"canal"/CHANNEL/"videos"/VIDEO/REPORT
        if path.is_symlink():
            raise VideoForgeError("CINEMATIC_INVENTORY_REPORT_SYMLINK")
        text=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
        if not path.exists() or path.read_text(encoding="utf8")!=text:
            path.write_text(text,encoding="utf8")
        print("CINEMATIC_REFERENCE_INVENTORY",json.dumps({
            "sceneMothers":data["legacySceneMotherCount"],
            "visualShotsPending":data["visualShotsPendingApproval"],
            "faceCloseups":data["faceCloseups"],
            "archivedDraftsC01":data["legacyScene01DraftPNGs"],
            "newImagesGenerated":0,
        }))
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError) as exc:
        print("CINEMATIC_REFERENCE_INVENTORY_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
