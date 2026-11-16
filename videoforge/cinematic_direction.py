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


# A direcao V1 permanece intacta para seus QA/EDL antigos.
# Apenas o EP01 com versao REMAKE ativa consulta o manifesto novo.
REMAKE_CHANNEL="alchemy-lab"
REMAKE_EPISODE="mmorpg-conquiste-a-princesa-ep01"
REMAKE_VERSION="remake-v2-20261115"
REMAKE_SCHEMA="videoforge/alchemy-remake-autonomy-plan/v1"


def load_active_remake_plan(channel:str,video_id:str,root:Path=ROOT)->dict|None:
    """Ler e validar o manifesto V2 de producao, sem herdar o lock da V1."""
    if (channel,video_id)!=(REMAKE_CHANNEL,REMAKE_EPISODE):
        return None
    base=Path(root)/"canal"/channel/"videos"/video_id
    state=_read(base/"estado-atual.json",100_000)
    if state.get("active_production_version")!=REMAKE_VERSION:
        return None
    if state.get("active_production_manifest")!="remake-ep01-planos.json":
        raise VideoForgeError("REMAKE_ACTIVE_MANIFEST_MISMATCH")
    manifest=_read(base/"remake-ep01-planos.json",300_000)
    validate_active_remake_plan(channel,video_id,manifest,root)
    return manifest


def validate_active_remake_plan(channel:str,video_id:str,manifest:dict,root:Path=ROOT)->dict:
    """Validacao fail-closed dos 37 planos e limites de autorizacao editorial."""
    if (not isinstance(manifest,dict) or manifest.get("schema")!=REMAKE_SCHEMA
            or manifest.get("version")!=REMAKE_VERSION
            or manifest.get("channel")!=channel or manifest.get("video_id")!=video_id
            or manifest.get("source_story")!="roteiro.json"
            or manifest.get("style_id")!="cinematic-semi-realistic-fantasy-anime"):
        raise VideoForgeError("REMAKE_SHOT_MANIFEST_ORIGIN_INVALID")
    authorization=manifest.get("authorization")
    if (not isinstance(authorization,dict)
            or authorization.get("new_image_generation_editorially_allowed") is not True
            or authorization.get("no_editorial_image_count_limit") is not True
            or authorization.get("unapproved_youtube_upload_forbidden") is not True):
        raise VideoForgeError("REMAKE_SHOT_AUTHORIZATION_INVALID")
    base=Path(root)/"canal"/channel/"videos"/video_id
    state=_read(base/"estado-atual.json",100_000)
    if (state.get("active_production_version")!=REMAKE_VERSION
            or state.get("remake_v2",{}).get("generation_editorially_authorized") is not True
            or state.get("locks",{}).get("no_youtube_upload") is not True):
        raise VideoForgeError("REMAKE_SHOT_STATE_MISMATCH")
    story=_read(base/"roteiro.json",200_000)
    scenes=story.get("scenes",[])
    if not isinstance(scenes,list) or len(scenes)<1:
        raise VideoForgeError("REMAKE_SHOT_SCENES_MISSING")
    story_shots={}
    for sc in scenes:
        for sh in sc.get("shots",[]):
            sid=sh.get("shot_id")
            if sid in story_shots:
                raise VideoForgeError("REMAKE_STORY_SHOT_DUPLICATED")
            story_shots[sid]=(sc.get("scene_id"),sh.get("start_frame"),sh.get("end_exclusive"))
    fmt=manifest.get("format",{})
    if (fmt.get("fps")!=30 or fmt.get("width")!=1080 or fmt.get("height")!=1920
            or type(fmt.get("total_frames")) is not int or fmt["total_frames"]<=0):
        raise VideoForgeError("REMAKE_SHOT_FORMAT_INVALID")
    plans=manifest.get("shots")
    declared=manifest.get("plan",{})
    if (not isinstance(plans,list) or len(plans)<declared.get("shots_minimum",37)
            or declared.get("scenes")!=len(scenes)
            or len(plans)!=len(story_shots)):
        raise VideoForgeError("REMAKE_SHOT_COVERAGE_INVALID")
    cursor=0
    seen=set()
    types={}
    for order,shot in enumerate(plans,1):
        if not isinstance(shot,dict):
            raise VideoForgeError("REMAKE_SHOT_ENTRY_INVALID")
        sid=shot.get("shot_id")
        scene=shot.get("scene_id")
        typ=shot.get("shot_type")
        if (not isinstance(sid,str) or not SHOT_ID.fullmatch(sid)
                or sid in seen or typ not in ALLOWED_TYPES or sid not in story_shots
                or scene!=story_shots[sid][0]
                or shot.get("order")!=order or shot.get("frame_start")!=cursor
                or type(shot.get("frame_end_exclusive")) is not int
                or shot["frame_end_exclusive"]<=cursor
                or (scene,cursor,shot["frame_end_exclusive"])!=story_shots[sid]):
            raise VideoForgeError("REMAKE_SHOT_TIMELINE_MISMATCH")
        cast=shot.get("cast")
        cam=shot.get("camera")
        if (not isinstance(cast,list) or any(not isinstance(x,str) for x in cast)
                or not isinstance(cam,dict)
                or not isinstance(cam.get("description"),str)
                or len(cam["description"])<25
                or not isinstance(cam.get("dramatic_direction"),str)
                or not isinstance(cam.get("position_and_intent"),str)
                or not isinstance(cam.get("depth_of_field"),str)
                or not isinstance(shot.get("emotion"),str)
                or not isinstance(shot.get("focus"),str)):
            raise VideoForgeError("REMAKE_SHOT_DIRECTION_INCOMPLETE")
        if ((typ=="black")!=(sid=="C01-P01")
                or shot.get("require_new_mother")!=(typ!="black")
                or (typ!="black" and (type(cam.get("lens_mm")) is not int
                    or not 20<=cam["lens_mm"]<=160))
                or (scene in ("C01","C02") and "elara" in cast)):
            raise VideoForgeError("REMAKE_SHOT_VISUAL_CONTRACT_INVALID")
        # Um relatorio falso nao pode autorizar render.
        if (shot.get("publishable") is True
                and not (shot.get("qa_approved") is True
                    and shot.get("human_visual_approved") is True
                    and shot.get("motion_qa_passed") is True
                    and isinstance(shot.get("art_mother_sha256"),str))):
            raise VideoForgeError("REMAKE_SHOT_FALSE_PUBLICATION_APPROVAL")
        seen.add(sid)
        types[typ]=types.get(typ,0)+1
        cursor=shot["frame_end_exclusive"]
    if cursor!=fmt["total_frames"] or seen!=set(story_shots):
        raise VideoForgeError("REMAKE_SHOT_COVERAGE_OR_DURATION_INVALID")
    if types.get("black")!=1 or declared.get("art_required")!=len(plans)-1:
        raise VideoForgeError("REMAKE_SHOT_ART_COUNT_INVALID")
    return {"shot_count":len(plans),"art_required":len(plans)-1,
            "duration_frames":cursor,"source":"remake-ep01-planos.json",
            "editorial_images_unlimited":True}


def _remake_to_cinematic_shot(shot:dict)->dict:
    cam=shot["camera"]
    return {
        "id":shot["shot_id"],"scene":shot["scene_id"],
        "shot_type":shot["shot_type"],"primary_focus":shot["focus"],
        "visual_prompt":cam["description"],"emotion":shot["emotion"],
        "characters":shot["cast"],"start_frame":shot["frame_start"],
        "end_frame_exclusive":shot["frame_end_exclusive"],
        "lens_mm":cam["lens_mm"],"depth_of_field":cam["depth_of_field"],
        "camera_orientation":cam["position_and_intent"],
        "dramatic_direction":cam["dramatic_direction"],
        "remake_source":"remake-ep01-planos.json",
    }


def _remake_anchor_state(channel:str,video_id:str,root:Path=ROOT)->dict:
    manifest=load_active_remake_plan(channel,video_id,root)
    if manifest is None:
        raise VideoForgeError("REMAKE_ACTIVE_MANIFEST_NOT_FOUND")
    anchors=manifest.get("identity_anchors")
    if (not isinstance(anchors,list) or not anchors
            or anchors[0].get("id")!="character-bible"):
        raise VideoForgeError("REMAKE_CANONICAL_ANCHOR_MISSING")
    anchor=anchors[0]
    from .remake_autopilot import verified_asset
    episode=Path(root)/"canal"/channel/"videos"/video_id
    verified=verified_asset(episode,anchor.get("path"),anchor.get("sha256"))
    if verified:
        # Verificacao de dimensao/PNG real, nao so existencia/sha textual.
        try:
            from .scene_layers import png_info
            info=png_info((episode/anchor["path"]).read_bytes(),require_alpha=False)
            # Reference artwork can be portrait-but-not-canonical size.
            # Do not resample or stretch identity PNGs just to satisfy the
            # OUTPUT canvas. The edited scene-mother remains 1024x1536.
            width,height=info.get("width"),info.get("height")
            verified=(type(width) is int and type(height) is int
                      and 512<=width<=2048 and 512<=height<=3072
                      and width<=height)
        except (OSError,ValueError,VideoForgeError):
            verified=False
    approved=(verified and anchor.get("human_approved") is True
              and anchor.get("status")=="approved")
    return {"source_image_files_verified":bool(verified),
            "human_approved":bool(approved),
            "source_sha256":anchor.get("sha256") if verified else None,
            "status":"reference_approved" if approved else "pending_reference_upload_and_identity_lock"}


def assert_scene_reference_matches_anchor(channel:str,video_id:str,sha256:str,
                                          root:Path=ROOT)->None:
    """Nao aceitar artifact de outra referencia, mesmo que haja uma ancora valida."""
    if load_active_remake_plan(channel,video_id,root) is None:
        return
    state=_remake_anchor_state(channel,video_id,root)
    if not state["human_approved"] or state["source_sha256"]!=sha256:
        raise VideoForgeError("REMAKE_SCENE_REFERENCE_ANCHOR_SHA_MISMATCH")


def resolve_shot(channel:str,video_id:str,number:int,
                 shot_id:str|None=None,root:Path=ROOT)->dict|None:
    remake=load_active_remake_plan(channel,video_id,root)
    if remake is not None:
        story=_read(Path(root)/"canal"/channel/"videos"/video_id/"roteiro.json")
        if type(number) is not int or number<1 or number>len(story["scenes"]):
            raise VideoForgeError("CINEMATIC_SCENE_NUMBER_INVALID")
        scene=f"C{number:02d}"
        if shot_id is None:
            goal=story["scenes"][number-1].get("story_goal","")
            found=re.search(r"C[0-9]{2}-P[0-9]{2}",goal)
            shot_id=found.group(0) if found else next(
                (s["shot_id"] for s in remake["shots"]
                 if s["scene_id"]==scene and s["shot_type"]!="black"),None)
        if not isinstance(shot_id,str) or not SHOT_ID.fullmatch(shot_id):
            raise VideoForgeError("CINEMATIC_SHOT_ID_INVALID")
        selected=[s for s in remake["shots"]
                  if s["scene_id"]==scene and s["shot_id"]==shot_id]
        if len(selected)!=1:
            raise VideoForgeError("CINEMATIC_SHOT_NOT_IN_SCENE")
        return _remake_to_cinematic_shot(selected[0])
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
        *(["ESTILO OBRIGATORIO: Cinematic Semi-Realistic Fantasy Anime.",
           "Direcao dramatica do remake V2:",shot["dramatic_direction"],
           "Ponto de foco do quadro:",shot["primary_focus"],
           "Identidade, roupas, perspectiva e iluminacao iguais a ancora V2 aprovada."]
          if shot.get("remake_source")=="remake-ep01-planos.json" else []),
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
    """V2: referencia canonica em PNG SHA-verificada E aprovada; V1: legado."""
    if load_active_remake_plan(channel,video_id,root) is not None:
        base=Path(root)/"canal"/channel/"videos"/video_id
        if (base/"SEM-GERACAO-NOVAS-IMAGENS.lock").exists():
            raise VideoForgeError("CINEMATIC_NEW_IMAGE_GENERATION_NOT_AUTHORIZED")
        if not _remake_anchor_state(channel,video_id,root)["human_approved"]:
            raise VideoForgeError("CINEMATIC_CANONICAL_REFERENCE_NOT_APPROVED")
        return
    plan=load_plan(channel,video_id,root)
    if plan is None:
        return
    review=plan.get("reference_approval",{})
    if (review.get("canonical_identity_conflict_detected") is True
            or review.get("chat_generated_reference_files")=="not_uploaded_to_this_repository"):
        raise VideoForgeError("CINEMATIC_CANONICAL_REFERENCE_NOT_APPROVED")
    if plan.get("production_gate",{}).get("new_generation_allowed") is not True:
        raise VideoForgeError("CINEMATIC_NEW_IMAGE_GENERATION_NOT_AUTHORIZED")


def validate_visual_reference_gate(channel:str,video_id:str,root:Path=ROOT)->dict:
    remake=load_active_remake_plan(channel,video_id,root)
    if remake is not None:
        anchor=_remake_anchor_state(channel,video_id,root)
        policy=_read(Path(root)/"canal"/channel/"videos"/video_id/"autonomy-policy.json")
        provider_approved=(policy.get("paid_provider_calls_approved") is True
                           and type(policy.get("max_chargeable_calls_per_run")) is int
                           and policy["max_chargeable_calls_per_run"]>=1)
        return {
            "plan_available":True,
            "active_manifest":"remake-ep01-planos.json",
            "new_image_generation_allowed":bool(
                anchor["human_approved"] and provider_approved
                and not (Path(root)/"canal"/channel/"videos"/video_id/
                         "SEM-GERACAO-NOVAS-IMAGENS.lock").exists()),
            "source_image_files_verified":anchor["source_image_files_verified"],
            "canonical_identity_conflict":not anchor["human_approved"],
            "status":anchor["status"],
            "paid_provider_calls_approved":provider_approved,
            "editorial_generation_authorized":True,
        }
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
    plan=load_active_remake_plan(args.channel,args.video_id)
    if plan is not None:
        report=validate_active_remake_plan(args.channel,args.video_id,plan)
    else:
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
