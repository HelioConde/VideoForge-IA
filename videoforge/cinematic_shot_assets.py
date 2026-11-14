"""Montagem editorial de tomadas (EDL) com verificação fail-closed de assets.

Não gera, edita, baixa ou renderiza imagens. Integra o plano cinematográfico
ao contrato do rig ThreeCanvas/Remotion; nunca considera cena-mãe geral
equivalente à foto de close. Lê somente assets por tomada e SHA-256.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from .cinematic_direction import load_plan, ROOT
from .errors import VideoForgeError

SCHEMA = "videoforge/cinematic-shot-edl/v1"
QA_SCHEMA = "videoforge/cinematic-shot-visual-qa/v1"
RIG_SCHEMA = "videoforge/cinematic-shot-rig/v1"
_SHA = re.compile(r"^[0-9a-f]{64}$")
PNG_MAGIC = bytes((137,80,78,71,13,10,26,10))
CANVAS = (1024,1536)

def _load_json(path:Path, limit:int=200_000)->dict:
    if (path.is_symlink() or not path.is_file() or path.stat().st_size>limit):
        raise VideoForgeError("CINEMATIC_ASSET_JSON_MISSING")
    try:
        d=json.loads(path.read_text(encoding="utf8"))
    except (ValueError,UnicodeError,OSError) as e:
        raise VideoForgeError("CINEMATIC_ASSET_JSON_INVALID") from e
    if not isinstance(d,dict):
        raise VideoForgeError("CINEMATIC_ASSET_JSON_BAD_ROOT")
    return d

def _file_from_rel(root:Path,relative:str)->Path:
    if not isinstance(relative,str) or not relative or "\\" in relative:
        raise VideoForgeError("CINEMATIC_ASSET_PATH_INVALID")
    p=Path(relative)
    if p.is_absolute() or ".." in p.parts or p.parts[0]!="assets":
        raise VideoForgeError("CINEMATIC_ASSET_PATH_INVALID")
    path=root/p
    if path.is_symlink():
        raise VideoForgeError("CINEMATIC_ASSET_SYMLINK_BLOCKED")
    # Rejeita symlink intermediário, não só no próprio arquivo.
    for parent in path.parents:
        if parent==root.parent:
            break
        if parent.is_symlink():
            raise VideoForgeError("CINEMATIC_ASSET_PARENT_SYMLINK_BLOCKED")
    return path

def _png_valid(path:Path, sha:str, rgba:bool|None=None)->bool:
    if not isinstance(sha,str) or not _SHA.fullmatch(sha):
        return False
    if path.is_symlink() or not path.is_file():
        return False
    raw=path.read_bytes()
    if (len(raw)<34 or raw[:8]!=PNG_MAGIC or raw[12:16]!=b"IHDR"
            or hashlib.sha256(raw).hexdigest()!=sha):
        return False
    size=(int.from_bytes(raw[16:20],"big"),int.from_bytes(raw[20:24],"big"))
    if size!=CANVAS:
        return False
    color_type=raw[25]
    return color_type in ((6,) if rgba is True else (2,6) if rgba is False else (2,6))

def expected_shot_paths(shot_id:str)->dict[str,str]:
    if not re.fullmatch(r"C[0-9]{2}-P[0-9]{2}",shot_id):
        raise VideoForgeError("CINEMATIC_SHOT_ID_PATH_INVALID")
    parent=f"assets/planos/{shot_id}"
    return {
        "mother":f"{parent}/scene-mother.png",
        "background":f"{parent}/background-reconstructed.png",
        "rig":f"{parent}/rig.json",
        "qa":f"{parent}/qa.json",
    }

def validate_shot_art(episode:Path,shot:dict,paths:dict)->tuple[bool,list[str],dict]:
    """Não aceita planos de outra mãe, manifests sem SHA ou QA reprovado."""
    sid=shot["id"]
    failures=[]
    data={}
    rig_path=_file_from_rel(episode,paths["rig"])
    qa_path=_file_from_rel(episode,paths["qa"])
    mother_path=_file_from_rel(episode,paths["mother"])
    bg_path=_file_from_rel(episode,paths["background"])
    if not mother_path.is_file():
        failures.append("SHOT_MOTHER_MISSING")
    if not bg_path.is_file():
        failures.append("SHOT_BACKGROUND_MISSING")
    if not rig_path.is_file():
        failures.append("SHOT_RIG_MISSING")
    if not qa_path.is_file():
        failures.append("SHOT_VISUAL_QA_MISSING")
    if failures:
        return False,failures,{}
    rig=_load_json(rig_path)
    qa=_load_json(qa_path)
    if (rig.get("schema")!=RIG_SCHEMA or rig.get("shot_id")!=sid
            or rig.get("scene")!=shot["scene"]):
        failures.append("SHOT_RIG_PROVENANCE_INVALID")
    for key,asset,alpha in (
       ("source_sha256",mother_path,False),
       ("background_sha256",bg_path,False),
    ):
        if not _png_valid(asset,rig.get(key),alpha):
            failures.append("SHOT_"+key.upper()+"_INVALID")
    parts=rig.get("parts")
    if not isinstance(parts,list) or len(parts)<2:
        failures.append("SHOT_INDEPENDENT_PARTS_MISSING")
        parts=[]
    piece_names=set()
    for part in parts:
        if not isinstance(part,dict) or not isinstance(part.get("name"),str):
            failures.append("SHOT_PART_ENTRY_INVALID")
            continue
        if part["name"] in piece_names:
            failures.append("SHOT_PART_DUPLICATED")
        piece_names.add(part["name"])
        try:
            file=_file_from_rel(episode,part["path"])
        except (VideoForgeError,KeyError):
            failures.append("SHOT_PART_PATH_INVALID")
            continue
        if not str(file.relative_to(episode)).startswith(f"assets/planos/{sid}/"):
            failures.append("SHOT_PART_NOT_FROM_OWN_MOTHER")
        if not _png_valid(file,part.get("sha256"),True):
            failures.append("SHOT_PART_RGBA_OR_SHA_INVALID")
        if (part.get("underlay_verified") is not True
                or part.get("pivot_measured") is not True):
            failures.append("SHOT_PART_UNDERLAY_OR_PIVOT_NOT_VERIFIED")
    if rig.get("whole_png_motion") is not False:
        failures.append("SHOT_FLAT_PNG_MOTION_FORBIDDEN")
    if rig.get("all_parts_from_same_mother") is not True:
        failures.append("SHOT_CROSS_SCENE_REUSED_PARTS_FORBIDDEN")
    if (qa.get("schema")!=QA_SCHEMA or qa.get("shot_id")!=sid
            or qa.get("mother_sha256")!=rig.get("source_sha256")):
        failures.append("SHOT_VISUAL_QA_PROVENANCE_INVALID")
    for k in ("human_visual_approved","neutral_roundtrip_approved",
              "mesh_rig_approved","hidden_anatomy_verified",
              "independent_movement_verified","camera_axis_consistent",
              "facial_identity_consistent"):
        if qa.get(k) is not True:
            failures.append("SHOT_QA_PENDING_"+k.upper())
    if not isinstance(qa.get("qa_frames"),list) or len(qa["qa_frames"])<3:
        failures.append("SHOT_QA_FRAME_COVERAGE_MISSING")
    data={
        "mother_sha256":rig.get("source_sha256"),
        "background_sha256":rig.get("background_sha256"),
        "rig_parts":len(parts),
        "qa_frames":qa.get("qa_frames"),
    }
    return not failures, sorted(set(failures)), data

def build_edl(channel:str,video_id:str,root:Path=ROOT)->dict:
    plan=load_plan(channel,video_id,root)
    if plan is None:
        raise VideoForgeError("CINEMATIC_EDL_PLAN_MISSING")
    base=root/"canal"/channel/"videos"/video_id
    locked=(base/"SEM-GERACAO-NOVAS-IMAGENS.lock").is_file()
    timeline=sorted(plan["shots"],key=lambda s:s["start_frame"])
    if not timeline or timeline[0]["start_frame"]!=0:
        raise VideoForgeError("CINEMATIC_EDL_NOT_FROM_FRAME_ZERO")
    shots=[]
    next_frame=0
    ready_count=0
    for shot in timeline:
        start=shot["start_frame"];end=shot["end_frame_exclusive"]
        if type(start)!=int or type(end)!=int or start!=next_frame or end<=start:
            raise VideoForgeError("CINEMATIC_EDL_GAP_OVERLAP_OR_ZERO")
        next_frame=end
        paths=None if shot["shot_type"]=="black" else expected_shot_paths(shot["id"])
        if paths is None:
            status="black_no_art_required"
            approved=True
            issues=[]
            evidence={}
        else:
            approved,issues,evidence=validate_shot_art(base,shot,paths)
            if not approved and locked:
                issues.append("NO_NEW_IMAGE_GENERATION_LOCK_ACTIVE")
            if not approved and plan["reference_approval"]["canonical_identity_conflict_detected"]:
                issues.append("CANONICAL_VISUAL_REFERENCE_CONFLICT")
            status="ready_for_render" if approved else "shot_art_or_rig_pending"
            if approved:
                ready_count+=1
        shots.append({
            "id":shot["id"],"scene":shot["scene"],
            "startFrame":start,"endFrameExclusive":end,
            "durationFrames":end-start,
            "type":shot["shot_type"],
            "emotion":shot["emotion"],
            "focus":shot["primary_focus"],
            "characters":shot["characters"],
            "hudPolicy":shot["hud_policy"],
            "transition":"hard_cut",
            "assetPaths":paths,
            "assetEvidence":evidence,
            "status":status,
            "rigApproved":approved if paths is not None else False,
            "renderAllowed":approved,
            "blockers":sorted(set(issues)),
        })
    # Conferir a duração pedida pelo roteiro, sem assumir que um MP4 já existe.
    fps=30
    if next_frame!=4890 or len(shots)!=37:
        raise VideoForgeError("CINEMATIC_EDL_EXPECTED_TIMELINE_MISMATCH")
    first=scenes=shots[0]
    if first["type"]!="black" or first["renderAllowed"] is not True:
        raise VideoForgeError("CINEMATIC_EDL_BLACK_OPENING_INVALID")
    can_render=all(s["renderAllowed"] for s in shots)
    return {
        "schema":SCHEMA,"channel":channel,"video_id":video_id,
        "source":"direcao-cinematografica-planos.json",
        "format":{"fps":fps,"width":1080,"height":1920,
                  "totalFrames":next_frame,"durationSeconds":next_frame/fps},
        "sourceArtworkFormat":{"width":1024,"height":1536,
                               "fit":"cover_no_stretch"},
        "shotCount":len(shots),
        "blackShots":sum(s["type"]=="black" for s in shots),
        "artRequiredShots":len(shots)-1,
        "artAndRigApprovedShots":ready_count,
        "unapprovedShots":len(shots)-1-ready_count,
        "visualReferenceConflict":bool(plan["reference_approval"]["canonical_identity_conflict_detected"]),
        "noImageGenerationLock":locked,
        "newImageGenerationCalls":0,
        "pixelFilesCreated":0,
        "renderOfficialAllowed":can_render,
        "youtubeUploaded":False,
        "status":"ready_for_official_render" if can_render else "pipeline_pendente",
        "time":"all boundaries are absolute frames, end exclusive, deterministic hard cuts",
        "shots":shots,
    }

def validate_edl(doc:dict)->None:
    if doc.get("schema")!=SCHEMA:
        raise VideoForgeError("CINEMATIC_EDL_SCHEMA_INVALID")
    shots=doc.get("shots")
    if not isinstance(shots,list) or len(shots)!=doc.get("shotCount"):
        raise VideoForgeError("CINEMATIC_EDL_SHOTS_INVALID")
    cursor=0;names=set()
    for shot in shots:
        if (shot["startFrame"]!=cursor or shot["endFrameExclusive"]<=cursor
                or shot["id"] in names):
            raise VideoForgeError("CINEMATIC_EDL_SHOTS_GAP_OVERLAP_DUPLICATE")
        cursor=shot["endFrameExclusive"]
        names.add(shot["id"])
        if shot.get("renderAllowed") is True and shot["type"]!="black" and shot.get("rigApproved") is not True:
            raise VideoForgeError("CINEMATIC_EDL_UNAPPROVED_RIG_EXPOSED")
    if cursor!=doc["format"]["totalFrames"]:
        raise VideoForgeError("CINEMATIC_EDL_LENGTH_INVALID")
    if doc["renderOfficialAllowed"]!=all(s["renderAllowed"] for s in shots):
        raise VideoForgeError("CINEMATIC_EDL_GATES_INCONSISTENT")

def main()->int:
    p=argparse.ArgumentParser(description="Gerar somente manifesto EDL para Remotion")
    p.add_argument("--channel",default="alchemy-lab")
    p.add_argument("--video-id",default="mmorpg-conquiste-a-princesa-ep01")
    p.add_argument("--output",type=Path,default=None)
    args=p.parse_args()
    try:
        doc=build_edl(args.channel,args.video_id)
        validate_edl(doc)
        content=json.dumps(doc,ensure_ascii=False,indent=2)+"\n"
        if args.output is None:
            print(content)
        else:
            target=args.output
            if target.is_symlink() or target.exists():
                raise VideoForgeError("CINEMATIC_EDL_NO_OVERWRITE")
            base=ROOT/"canal"/args.channel/"videos"/args.video_id
            if target.parent.resolve()!=base.resolve() or target.suffix!=".json":
                raise VideoForgeError("CINEMATIC_EDL_OUTPUT_MUST_BE_LOCAL_JSON")
            target.write_text(content,encoding="utf8")
            print("CINEMATIC_EDL_CREATED",target,doc["shotCount"],
                  "shots, approved",doc["artAndRigApprovedShots"],
                  "render",doc["renderOfficialAllowed"])
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError) as exc:
        print("CINEMATIC_EDL_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
