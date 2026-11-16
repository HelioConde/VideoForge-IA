"""Derive wardrobe continuity for ALL 40 current EP01 V2 shots.

Older '37-planos' records are historical, NOT the production source of truth.
No model, no thumbnails, no wardrobe approval, no rig/render/upload.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT,EPISODE
from .wardrobe_review import owner_review,source_readiness

OUT="CONTINUIDADE-FIGURINOS-V2-40-TOMADAS.json"
DOC="REGRAS-FIGURINOS-V2-40-TOMADAS.md"

def derive(root:Path=ROOT,sync:bool=False)->dict:
    ep=Path(root)/EPISODE
    owner,contract=owner_review(root)
    ready=source_readiness(root)
    source=ep/"remake-ep01-planos.json"
    if not source.is_file() or source.is_symlink():
        raise VideoForgeError("WARDROBE40_PRODUCTION_PLAN_MISSING")
    plan=json.loads(source.read_text(encoding="utf-8"))
    if (plan.get("schema")!="videoforge/alchemy-remake-autonomy-plan/v1"
            or plan.get("channel")!="alchemy-lab"
            or plan.get("video_id")!="mmorpg-conquiste-a-princesa-ep01"):
        raise VideoForgeError("WARDROBE40_PRODUCTION_PLAN_INVALID")
    shots=plan.get("shots",[])
    if len(shots)!=40 or plan["format"]["total_frames"]!=4890:
        raise VideoForgeError("WARDROBE40_SHOT_COUNT_OR_FRAMES_INVALID")
    seen=set()
    records=[]
    cursor=0
    for shot in shots:
        sid=shot.get("shot_id")
        if (not isinstance(sid,str) or re.fullmatch(r"C\d{2}-P\d{2}",sid) is None
                or sid in seen or shot.get("frame_start")!=cursor
                or type(shot.get("frame_end_exclusive")) is not int
                or shot["frame_end_exclusive"]<=cursor):
            raise VideoForgeError("WARDROBE40_TIMELINE_OR_SHOT_INVALID")
        seen.add(sid)
        cursor=shot["frame_end_exclusive"]
        scene=int(sid[1:3])
        cast=shot.get("cast")
        if not isinstance(cast,list) or any(not isinstance(c,str) for c in cast):
            raise VideoForgeError("WARDROBE40_CAST_INVALID")
        if "elara" in cast and scene<7:
            raise VideoForgeError("WARDROBE40_EARLY_PRINCESS_CAST_INVALID")
        if "elara" in cast and scene==11:
            raise VideoForgeError("WARDROBE40_ELARA_BEFORE_REVEAL_INVALID")
        costumes={}
        if "kael" in cast:
            variant=("palace_trial_red_cloak" if scene<=3 else
                     "modern_world" if scene==4 else "arken_red_cloak")
            costumes["kael"]={
                "variant":variant,
                "reference_sha":"edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f",
                "must_preserve":"dark hair, amber eyes, burgundy scarf/cloak, dark and gilded pauldron with blue stone except modern-world costume",
                "human_full_costume_approved":False,
            }
        if "elara" in cast:
            if 7<=scene<=10:
                costumes["elara"]={
                    "variant":"street_disguise",
                    "must_preserve":"same face and golden hair identity under street hood; NO royal outfit shown during disguise",
                    "royal_purple_bodice_required":False,
                    "human_full_costume_approved":False,
                }
            elif scene>=12:
                costumes["elara"]={
                    "variant":"royal_white_violet_purple_bodice",
                    "must_preserve":contract["rules"]["elara_palace"],
                    "royal_purple_bodice_required":True,
                    "approved_full_costume_reference_sha":None,
                    "human_full_costume_approved":False,
                }
            else:
                raise VideoForgeError("WARDROBE40_ELARA_CAST_UNEXPECTED_SCENE")
        if "aldric" in cast:
            if not (scene<=3 or scene>=12):
                raise VideoForgeError("WARDROBE40_ALDRIC_CAST_UNEXPECTED_SCENE")
            costumes["aldric"]={
                "variant":"royal_burgundy_gold",
                "must_preserve":contract["rules"]["aldric_royal"],
                "approved_full_costume_reference_sha":None,
                "human_full_costume_approved":False,
            }
        has_royal=("aldric" in costumes or
                   "elara" in costumes and costumes["elara"]["variant"]=="royal_white_violet_purple_bodice")
        records.append({
            "shot_id":sid,
            "scene":shot["shot_id"][:3],
            "frame_start":shot["frame_start"],
            "frame_end_exclusive":shot["frame_end_exclusive"],
            "cast":cast,
            "costumes":costumes,
            "requires_verified_royal_costume":has_royal,
            "source_old_37_shot_registry_is_not_authoritative":True,
            "rejected_grounded_sha_forbidden":owner["sha256"],
            "characters_or_costumes_auto_approved":False,
            "official_shot_render_allowed":False,
        })
    if cursor!=4890:
        raise VideoForgeError("WARDROBE40_TIMELINE_INCOMPLETE")
    result={
        "schema":"videoforge/remake-wardrobe-continuity-40/v1",
        "scope":"alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
        "authoritative_plan":"remake-ep01-planos.json",
        "historical_only_file":"continuidade-figurinos-37-planos.json",
        "source_owner_review":"REVISAO-FIGURINO-V2.json",
        "source_contract":"CONTRATO-FIGURINO-V2.json",
        "rejected_reference_sha256":owner["sha256"],
        "total_shots":len(records),
        "total_frames":4890,
        "shots_with_elara_royal":sum(x["costumes"].get("elara",{}).get("royal_purple_bodice_required") is True for x in records),
        "shots_with_elara_disguise":sum(x["costumes"].get("elara",{}).get("variant")=="street_disguise" for x in records),
        "shots_with_aldric":sum("aldric" in x["costumes"] for x in records),
        "royal_costume_review_required_shots":[x["shot_id"] for x in records if x["requires_verified_royal_costume"]],
        "verified_owner_approved_full_royal_outfits":ready["verified"],
        "required_owner_approved_full_royal_outfits":ready["required"],
        "cannot_auto_generate_character_art_before_full_outfit_approval":True,
        "cannot_render_full_episode_before_identity_review":True,
        "human_approved":False,
        "image_provider_calls":0,
        "new_art_generated":False,
        "youtube_uploaded":False,
        "shots":records,
    }
    if sync:
        report=ep/OUT
        md=ep/DOC
        if report.is_symlink() or md.is_symlink():
            raise VideoForgeError("WARDROBE40_REPORT_SYMLINK")
        payload=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
        if not report.is_file() or report.read_text(encoding="utf-8")!=payload:
            report.write_text(payload,encoding="utf-8")
        lines=[
            "# EP01 V2 — continuidade dos figurinos nas 40 tomadas",
            "",
            "Fonte de verdade: \`remake-ep01-planos.json\` (40 tomadas / 4890 quadros).",
            "O cadastro \`continuidade-figurinos-37-planos.json\` é **histórico**, não usar para liberar roupas ou animações.",
            "",
            "### Contrato de roupas",
            "",
            "- **Elara palácio, a partir de C12:** traje branco-perola/violeta/dourado com painel **ROXO no peitoral**, mesma localização, roupa inteira aprovada e rosto/hair identity fiéis.",
            "- **Elara rua, C07–C10:** disfarce de rua, não usar vestido do palácio até a revelação C12.",
            "- **Aldric:** uniforme real vinho/bordô com ouro, gola clara, ornamentos e coroa constantes em C01–C03 e C12–C14.",
            "- **Kael:** preservar identidade e as variantes planejadas (julgamento, mundo moderno C04, reino de Arken).",
            "",
            "### Revisão operacional",
            "",
            "Toda tomada com figurino real de Aldric ou Elara contém bloqueio até suas fontes originais completas serem aprovadas por SHA e conferidas visualmente.",
            "Este documento **não promove** imagens legadas, pranchas rejeitadas ou camadas RGBA a referências aprovadas.",
            "",
            "Tomadas com Elara no vestido do palácio: **"+str(result["shots_with_elara_royal"])+"**; com disfarce: **"+str(result["shots_with_elara_disguise"])+"**; com Aldric: **"+str(result["shots_with_aldric"])+"**.",
            "Figurinos completos aprovados: **"+str(ready["verified"])+"/"+str(ready["required"])+"**.",
            "",
            "Ver também [revisão de detalhes](REVISAR-DETALHES-FIGURINOS-V2.md) e [contrato R2](CONTRATO-FIGURINO-V2.json).",
            "",
        ]
        txt="\n".join(lines)
        if not md.is_file() or md.read_text(encoding="utf-8")!=txt:
            md.write_text(txt,encoding="utf-8")
    return result

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    args=p.parse_args()
    result=derive(sync=args.sync)
    print("WARDROBE40_QA",json.dumps({
       "shots":result["total_shots"],
       "royal_elara":result["shots_with_elara_royal"],
       "street_elara":result["shots_with_elara_disguise"],
       "aldric":result["shots_with_aldric"],
       "approved_full_outfits":result["verified_owner_approved_full_royal_outfits"],
       "provider_calls":0,
    }))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
