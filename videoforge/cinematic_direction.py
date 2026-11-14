"""Direção de fotografia por tomada para doramas 2D no VideoForge.

Planejamento reutilizável, opt-in por episódio; nenhuma imagem é gerada aqui.
O roteiro define elencos/frames e a bíblia define identidades. Um close
pode usar imagem-mãe própria; NUNCA um crop de rosto minúsculo como rig final.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from .errors import VideoForgeError
from .paths import CHANNEL_IDS, IDENTIFIER

ROOT=Path(__file__).resolve().parents[1]
SCHEMA="videoforge/cinematic-shot-plan/v1"
SHOT_ID=re.compile(r"^C[0-9]{2}-P[0-9]{2}$")
ALLOWED_TYPES={
    "black","insert","low_angle","wide","close_up","extreme_close_up",
    "match_cut","over_shoulder","medium","tracking","two_shot","action",
}
CLOSE_TYPES={"close_up","extreme_close_up"}
CHARACTER_GROUPS={"guarda_esquerdo":"guardas","guarda_direito":"guardas",
                  "mascarado_1":"mascarados","mascarado_2":"mascarados",
                  "figurantes":"figurantes","carrasco":"carrasco"}
REQUIRES_OVERLAY={"C04-P02","C05-P03","C06-P02","C13-P01","C13-P02","C14-P03"}

def _read(path:Path,max_bytes:int=300_000)->dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>max_bytes:
        raise VideoForgeError("CINEMATIC_SHOT_SOURCE_MISSING_OR_TOO_BIG")
    try:
        data=json.loads(path.read_text(encoding="utf8"))
    except (ValueError,UnicodeError,OSError) as exc:
        raise VideoForgeError("CINEMATIC_SHOT_JSON_INVALID") from exc
    if not isinstance(data,dict):
        raise VideoForgeError("CINEMATIC_SHOT_ROOT_INVALID")
    return data

def shot_plan_file(channel:str,video_id:str,root:Path=ROOT)->Path:
    if channel not in CHANNEL_IDS or not IDENTIFIER.fullmatch(video_id):
        raise VideoForgeError("CINEMATIC_SHOT_CHANNEL_INVALID")
    return root/"canal"/channel/"videos"/video_id/"direcao-cinematografica-planos.json"

def load_plan(channel:str,video_id:str,root:Path=ROOT)->dict|None:
    path=shot_plan_file(channel,video_id,root)
    if not path.exists():
        return None
    plan=_read(path)
    validate_plan(channel,video_id,plan,root)
    return plan

def validate_plan(channel:str,video_id:str,plan:dict,root:Path=ROOT)->dict:
    base=root/"canal"/channel/"videos"/video_id
    direction=_read(base/"direcao-rig-remotion.json",300_000)
    story=_read(base/"roteiro.json",200_000)
    if (plan.get("schema")!=SCHEMA or plan.get("channel")!=channel
            or plan.get("video_id")!=video_id
            or plan.get("status")!="shot_descriptions_prepared_assets_not_generated"
            or plan.get("generative_image_calls")!=0
            or plan.get("production_gate",{}).get("new_generation_allowed") is not False):
        raise VideoForgeError("CINEMATIC_PLAN_ORIGIN_POLICY_INVALID")
    if not isinstance(plan.get("shots"),list):
        raise VideoForgeError("CINEMATIC_SHOTS_MISSING")
    requested={(s["id"],t["id"]):t
               for s in direction["scenes"] for t in s["shots"]}
    scenes={s["id"]:s for s in direction["scenes"]}
    covered=set()
    distribution={}
    for item in plan["shots"]:
        if not isinstance(item,dict):
            raise VideoForgeError("CINEMATIC_SHOT_ENTRY_INVALID")
        sid=item.get("id")
        scene=item.get("scene")
        key=(scene,sid)
        if (scene not in scenes or not isinstance(sid,str)
                or not SHOT_ID.fullmatch(sid) or key in covered or key not in requested):
            raise VideoForgeError("CINEMATIC_SHOT_ID_MISSING_OR_DUPLICATED")
        covered.add(key)
        shot=requested[key]
        typ=item.get("shot_type")
        if typ not in ALLOWED_TYPES:
            raise VideoForgeError("CINEMATIC_SHOT_TYPE_INVALID")
        distribution[typ]=distribution.get(typ,0)+1
        if (item.get("start_frame")!=shot["startFrame"]
                or item.get("end_frame_exclusive")!=shot["endFrameExclusive"]
                or item.get("characters")!=shot["characters"]):
            raise VideoForgeError("CINEMATIC_SHOT_STORYBOARD_MISMATCH")
        if (not isinstance(item.get("visual_prompt"),str)
                or not 25<=len(item["visual_prompt"])<=480
                or not isinstance(item.get("primary_focus"),str)
                or not item.get("emotion")):
            raise VideoForgeError("CINEMATIC_SHOT_DESCRIPTION_INVALID")
        if item.get("hud_policy")!=("remotion_overlay" if sid in REQUIRES_OVERLAY else "none"):
            raise VideoForgeError("CINEMATIC_SHOT_HUD_POLICY_INVALID")
        if item.get("approved_for_render") is not False:
            raise VideoForgeError("CINEMATIC_SHOT_IMPROPERLY_APPROVED")
        if typ=="black" and (sid!="C01-P01" or item["characters"]):
            raise VideoForgeError("CINEMATIC_BLACK_ONLY_C01_P01")
        if typ!="black" and (not isinstance(item.get("lens_mm"),int)
                or item.get("lens_mm")<20 or item.get("lens_mm")>160):
            raise VideoForgeError("CINEMATIC_LENS_INVALID")
        if sid.startswith(("C01-","C02-")) and "elara" in item["characters"]:
            raise VideoForgeError("CINEMATIC_PRINCESS_REVEAL_EARLY")
    if covered!=set(requested):
        raise VideoForgeError("CINEMATIC_COVERAGE_INCOMPLETE")
    if sum(distribution.get(x,0) for x in CLOSE_TYPES)<10:
        raise VideoForgeError("CINEMATIC_TOO_FEW_FACE_CLOSEUPS")
    if distribution.get("over_shoulder",0)<3 or distribution.get("wide",0)<3:
        raise VideoForgeError("CINEMATIC_NO_VISUAL_VARIETY")
    if plan.get("shot_distribution")!=distribution:
        raise VideoForgeError("CINEMATIC_SHOT_DISTRIBUTION_INVALID")
    return {"shot_count":len(covered),"types":distribution,
            "face_closeups":sum(distribution.get(x,0) for x in CLOSE_TYPES),
            "no_new_images":True}

def resolve_shot(channel:str,video_id:str,number:int,
                 shot_id:str|None=None,root:Path=ROOT)->dict|None:
    plan=load_plan(channel,video_id,root)
    if plan is None:
        if shot_id is not None:
            raise VideoForgeError("CINEMATIC_SHOT_NOT_CONFIGURED")
        return None
    story=_read(root/"canal"/channel/"videos"/video_id/"roteiro.json")
    if type(number) is not int or number<1 or number>len(story["scenes"]):
        raise VideoForgeError("CINEMATIC_SCENE_NUMBER_INVALID")
    scene=f"C{number:02d}"
    if shot_id is None:
        goal=story["scenes"][number-1].get("story_goal","")
        match=re.search(r"C[0-9]{2}-P[0-9]{2}",goal)
        shot_id=match.group(0) if match else next(
            (shot["id"] for shot in plan["shots"]
             if shot["scene"]==scene and shot["shot_type"]!="black"),None)
    if not isinstance(shot_id,str) or not SHOT_ID.fullmatch(shot_id):
        raise VideoForgeError("CINEMATIC_SHOT_ID_INVALID")
    match=[item for item in plan["shots"] if item["scene"]==scene and item["id"]==shot_id]
    if len(match)!=1:
        raise VideoForgeError("CINEMATIC_SHOT_NOT_IN_SCENE")
    return match[0]

def prompt_direction(shot:dict)->str:
    if shot["shot_type"]=="black":
        raise VideoForgeError("CINEMATIC_BLACK_FRAME_NEVER_GENERATE_IMAGE")
    # Não é cartaz com 5 personagens. A direção deve dominar o prompt,
    # respeitando a linha do tempo do roteiro e mantendo as identidades.
    return " ".join((
        "TOMADA CINEMATOGRÁFICA ÚNICA de dorama MMORPG 2D, não cartaz.",
        "Plano:",shot["id"]+".",
        "Enquadramento:",shot["shot_type"]+".",
        "Lente virtual:",str(shot["lens_mm"])+"mm.",
        "Profundidade de campo:",shot["depth_of_field"]+".",
        "Câmera:",shot["camera_orientation"]+".",
        "Emoção:",shot["emotion"]+".",
        "Composição:",shot["visual_prompt"],
        "Rosto idêntico à referência canônica, olhos e expressão naturais,",
        "traço, cabelo, roupas, arquitetura, eixo e iluminação iguais nos cortes.",
        "Não inventar pessoas desfocadas no fundo.",
        "Sem qualquer texto, logo, missão ou HUD pintado no PNG;",
        "interfaces e legendas são adicionadas pelo Remotion separadamente.",
        "Essa imagem-mãe do plano precisa ter seus PRÓPRIOS recortes RGBA",
        "e anatomia oculta reconstruída antes de movimento articulado real.",
    ))

def canon_cast_for_shot(shot:dict,canonical:dict)->tuple[tuple[str,...],tuple[str,...]]:
    seen=[]
    # Cada ator pode ser 'guardas', ou duplas guarda_esquerdo/direito.
    for actor in shot["characters"]:
        key=CHARACTER_GROUPS.get(actor,actor)
        if key in canonical and key not in seen:
            seen.append(key)
        elif key=="carrasco":
            continue  # Apenas punho/espada visíveis, nenhum rosto para inventar
        elif key not in canonical:
            # Entidades genéricas (figurantes/mascarados) seguem o roteiro,
            # sem tentar reutilizar a bíblia facial dos protagonistas.
            continue
    return tuple(seen),tuple(k for k in canonical if k not in seen)

def assert_shot_generation_ready(channel:str,video_id:str,root:Path=ROOT)->None:
    """Bloquear nova imagem se referencias do chat divergem da biblia anterior."""
    plan=load_plan(channel,video_id,root)
    if plan is None:
        return  # Videos sem opt-in continuam com regra do gerador legado
    review=plan.get("reference_approval",{})
    if (review.get("canonical_identity_conflict_detected") is True
            or review.get("chat_generated_reference_files")=="not_uploaded_to_this_repository"):
        raise VideoForgeError("CINEMATIC_CANONICAL_REFERENCE_NOT_APPROVED")
    if plan.get("production_gate",{}).get("new_generation_allowed") is not True:
        raise VideoForgeError("CINEMATIC_NEW_IMAGE_GENERATION_NOT_AUTHORIZED")

def validate_visual_reference_gate(channel:str,video_id:str,root:Path=ROOT)->dict:
    plan=load_plan(channel,video_id,root)
    if plan is None:
        return {"plan_available":False,"new_image_generation_allowed":False}
    conflicting=plan.get("reference_approval",{}).get("canonical_identity_conflict_detected")
    return {"plan_available":True,"new_image_generation_allowed":False,
            "source_image_files_verified":False,
            "canonical_identity_conflict":conflicting is True,
            "status":"pending_reference_upload_and_identity_lock"}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(description="Validar direção cinematográfica SEM gerar imagens")
    p.add_argument("--channel",default="alchemy-lab")
    p.add_argument("--video-id",default="mmorpg-conquiste-a-princesa-ep01")
    p.add_argument("--shot-id")
    args=p.parse_args()
    plan=load_plan(args.channel,args.video_id)
    if plan is None:
        raise SystemExit("NO_CINEMATIC_PLAN")
    report=validate_plan(args.channel,args.video_id,plan)
    if args.shot_id:
        number=int(args.shot_id[1:3])
        shot=resolve_shot(args.channel,args.video_id,number,args.shot_id)
        print(prompt_direction(shot))
    else:
        print(json.dumps(report,ensure_ascii=False))
