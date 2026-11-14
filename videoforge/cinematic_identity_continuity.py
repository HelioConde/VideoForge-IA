"""Cinematic character identity and wardrobe contract for the 37-shot EP01.

No image generation and no automatic facial recognition. The reference
hashes are *style examples*, not rig approvals. Human QA and imported
unmodified source originals remain mandatory before render.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from .cinematic_direction import ROOT,load_plan
from .errors import VideoForgeError

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"
SCHEMA="videoforge/character-continuity-v2/v1"
SOURCE_MANIFEST="referencias-cinematograficas-aprovadas-no-chat.json"
OUTPUT="continuidade-figurinos-37-planos.json"
MAIN_CAST={"kael","elara"}
REF_IDS={"kael":"ref-kael-close-c12","elara":"ref-elara-close-c12"}
SUPPORTED_ROLE_VARIANTS={
    "kael":{"palace_trial_red_cloak","modern_world","arken_red_cloak"},
    "elara":{"street_disguise","royal_white_violet"},
}

def costume_for(character:str,scene_number:int)->str:
    if character=="kael":
        if scene_number<=3:
            return "palace_trial_red_cloak"
        if scene_number==4:
            return "modern_world"
        return "arken_red_cloak"
    if character=="elara":
        if scene_number<12:
            return "street_disguise"
        return "royal_white_violet"
    raise VideoForgeError("CINEMATIC_CONTINUITY_UNKNOWN_MAIN_CHARACTER")

def shot_requirements(shot:dict,reference_ids:dict[str,str])->dict:
    scene=shot.get("scene")
    sid=shot.get("id")
    if not isinstance(scene,str) or not re.fullmatch(r"C\d{2}",scene):
        raise VideoForgeError("CINEMATIC_CONTINUITY_SCENE_INVALID")
    if not isinstance(sid,str) or not sid.startswith(scene+"-"):
        raise VideoForgeError("CINEMATIC_CONTINUITY_SHOT_SCENE_MISMATCH")
    num=int(scene[1:])
    cast=shot.get("characters")
    if not isinstance(cast,list):
        raise VideoForgeError("CINEMATIC_CONTINUITY_CAST_INVALID")
    roles={}
    for character in cast:
        if character not in MAIN_CAST:
            continue
        wardrobe=costume_for(character,num)
        roles[character]={
            "character_id":character,
            "style_reference_id":REF_IDS[character],
            "style_reference_sha256":reference_ids[character],
            "identity_version":"v2_preferred_not_source_approved",
            "wardrobe_version":wardrobe,
            "hair_identity":"dark_voluminous_amber_eyes" if character=="kael"
                else "golden_blonde_violet_eyes",
            "must_match_original_approved_style_reference":True,
            "requires_human_visual_continuity_review":True,
            "is_princess_identity_revealed":(
                num>=12 if character=="elara" else None
            ),
        }
    if "elara" in roles and num<12 and roles["elara"]["wardrobe_version"]!="street_disguise":
        raise VideoForgeError("CINEMATIC_ELARA_REVEAL_BEFORE_C12")
    return {
        "shot_id":sid,"scene":scene,"shot_type":shot["shot_type"],
        "main_character_requirements":roles,
        "is_black_opening":shot["shot_type"]=="black",
        "planned_cast":cast,
        "art_and_rig_approved":False,
    }

def build_continuity(root:Path=ROOT)->dict:
    base=root/"canal"/CHANNEL/"videos"/VIDEO
    manifest_file=base/SOURCE_MANIFEST
    manifest=json.loads(manifest_file.read_text(encoding="utf-8"))
    samples=manifest.get("approved_samples",[])
    refs={x["id"]:x["original_sha256"] for x in samples}
    if (len(refs)!=2 or set(refs)!=set(REF_IDS.values())
            or any(not isinstance(v,str) or len(v)!=64 for v in refs.values())):
        raise VideoForgeError("CINEMATIC_CONTINUITY_SOURCE_REFERENCE_MISSING")
    ids={actor:refs[ref] for actor,ref in REF_IDS.items()}
    plan=load_plan(CHANNEL,VIDEO,root)
    if plan is None or len(plan["shots"])!=37:
        raise VideoForgeError("CINEMATIC_CONTINUITY_37_SHOTS_REQUIRED")
    shots=[shot_requirements(s,ids) for s in plan["shots"]]
    if len({s["shot_id"] for s in shots})!=37:
        raise VideoForgeError("CINEMATIC_CONTINUITY_DUPLICATE_SHOT")
    from .cinematic_chat_references import reference_status
    original_sources_verified=(
        reference_status(root)["original_source_files_sha_verified"]==2
    )
    return {
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "source":SOURCE_MANIFEST,
        "source_approved_for_visual_preference_only":True,
        "canonical_references_imported":original_sources_verified,
        "generator_locked":(base/"SEM-GERACAO-NOVAS-IMAGENS.lock").is_file(),
        "image_generation_calls":0,
        "total_shots":37,
        "black_openings":sum(x["is_black_opening"] for x in shots),
        "shots_with_kael":sum("kael" in x["main_character_requirements"] for x in shots),
        "shots_with_elara":sum("elara" in x["main_character_requirements"] for x in shots),
        "elara_street_disguise_shots":sum(
            x["main_character_requirements"].get("elara",{}).get("wardrobe_version")=="street_disguise" for x in shots
        ),
        "elara_royal_shots":sum(
            x["main_character_requirements"].get("elara",{}).get("wardrobe_version")=="royal_white_violet" for x in shots
        ),
        "production_render_allowed":False,
        "notes":[
            "Kael: rosto e cabelo v2; figurino do mundo moderno apenas na C04",
            "Elara: capuz de rua nas cenas C07-C10; vestido branco-violeta apenas na revelacao C12 em diante",
            "As roupas mudam por narrativa; o rosto e o cabelo devem permanecer reconheciveis",
            "O registro define requisitos, não comprova que o PNG existente corresponde à descrição",
            "Nenhum shot tem aprovacao automática de rig ao registrar continuidade",
        ],
        "shots":shots,
    }

def validate_actor_wardrobe(shot:dict,rig:dict,qa:dict,reference_imported:bool)->None:
    """Rig+human QA gate for each visible Kael/Elara actor."""
    if not reference_imported:
        raise VideoForgeError("CINEMATIC_CONTINUITY_EXACT_STYLE_SOURCE_NOT_IMPORTED")
    role_map=shot["main_character_requirements"]
    listed=rig.get("actors")
    if not isinstance(listed,list):
        raise VideoForgeError("CINEMATIC_CONTINUITY_ACTOR_LIST_MISSING")
    actor_index={a.get("id"):a for a in listed if isinstance(a,dict)}
    if not set(role_map).issubset(actor_index):
        raise VideoForgeError("CINEMATIC_CONTINUITY_MAIN_ACTOR_NOT_IN_RIG")
    review=qa.get("character_continuity_review")
    if not isinstance(review,dict):
        raise VideoForgeError("CINEMATIC_CONTINUITY_HUMAN_REVIEW_MISSING")
    for character,expected in role_map.items():
        actor=actor_index[character]
        continuity=actor.get("continuity")
        human=review.get(character)
        if not isinstance(continuity,dict) or not isinstance(human,dict):
            raise VideoForgeError("CINEMATIC_CONTINUITY_RECORD_MISSING")
        required=("style_reference_sha256","wardrobe_version","hair_identity")
        if any(continuity.get(k)!=expected[k] for k in required):
            raise VideoForgeError("CINEMATIC_CONTINUITY_WRONG_FACE_HAIR_OR_COSTUME")
        if human.get("approved") is not True or any(
            human.get(k)!=expected[k] for k in required
        ):
            raise VideoForgeError("CINEMATIC_CONTINUITY_HUMAN_QA_REQUIRED")
        if (character=="elara" and
            human.get("princess_identity_revealed") is not expected["is_princess_identity_revealed"]):
            raise VideoForgeError("CINEMATIC_CONTINUITY_SPOILER_OR_REVEAL_WRONG")



def verify_shot_continuity(shot:dict,rig:dict,qa:dict,
                           root:Path=ROOT)->None:
    """Recheck import+SHA and the actual actor against this shot's wardrobe."""
    if not any(x in MAIN_CAST for x in shot.get("characters",[])):
        return
    report=build_continuity(root)
    policy=next((x for x in report["shots"] if x["shot_id"]==shot["id"]),None)
    if policy is None or policy["planned_cast"]!=shot["characters"]:
        raise VideoForgeError("CINEMATIC_CONTINUITY_SHOT_NOT_IN_SOURCE_PLAN")
    validate_actor_wardrobe(
        policy,rig,qa,report["canonical_references_imported"]
    )

def main()->int:
    try:
        report=build_continuity()
        path=ROOT/"canal"/CHANNEL/"videos"/VIDEO/OUTPUT
        if path.is_symlink():
            raise VideoForgeError("CINEMATIC_CONTINUITY_REPORT_SYMLINK")
        content=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
        if not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.write_text(content,encoding="utf-8")
        print("CONTINUITY_REPORT",json.dumps({
            "shots":report["total_shots"],
            "kael":report["shots_with_kael"],
            "elara":report["shots_with_elara"],
            "disguise":report["elara_street_disguise_shots"],
            "royal":report["elara_royal_shots"],
            "images_generated":0,
        }))
        return 0
    except (VideoForgeError,OSError,ValueError,KeyError,TypeError) as exc:
        print("CONTINUITY_BLOCKED",str(exc))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
