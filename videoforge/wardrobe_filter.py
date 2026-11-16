"""Deterministic, provenance-labeled wardrobe continuity review for EP01 V2.

Known mismatches are explicit user observations and may be auto-REJECTED.
No visual AI is run here, and no subject-pixel masks have been supplied:
unknown appearances may never be auto-APPROVED. Review every affected shot
as a dependency, not a false claim of an observed error in that shot.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .remake_autopilot import ROOT, EPISODE
from .wardrobe_review import owner_review, source_readiness
from .errors import VideoForgeError

NAMES={"aldric":"CHECKLIST-FIGURINO-ALDRIC.json",
       "elara":"CHECKLIST-FIGURINO-ELARA.json",
       "kael":"CHECKLIST-FIGURINO-KAEL.json"}
REPORT="RELATORIO-FILTRO-FIGURINO-V2.json"
REVIEW="RELATORIO-APROVACAO-REPROVACAO-FIGURINO.md"

def _read_json(path:Path)->dict:
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("WARDROBE_FILTER_INPUT_MISSING")
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError,UnicodeError):
        raise VideoForgeError("WARDROBE_FILTER_BAD_JSON") from None
    if not isinstance(data,dict):
        raise VideoForgeError("WARDROBE_FILTER_BAD_JSON")
    return data

def _check(actor:str,entry:dict)->list[dict]:
    if (entry.get("schema")!="videoforge/character-wardrobe-checklist/v1"
            or entry.get("character")!=actor
            or entry.get("human_approval") is not False
            or entry.get("current_decision") not in ("REPROVADO","REVISAO_PENDENTE")
            or entry.get("auto_approve_without_segmented_pixel_evidence") is not False
            or not isinstance(entry.get("rules"),list) or len(entry["rules"])<6):
        raise VideoForgeError("WARDROBE_FILTER_UNTRUSTED_CHECKLIST")
    rules=entry["rules"]
    if any(not isinstance(r,dict) or r.get("level")!="blocking" or
           not isinstance(r.get("must"),str) or not r["must"] for r in rules):
        raise VideoForgeError("WARDROBE_FILTER_RULES_INVALID")
    issues=entry.get("known_defects",[])
    if not isinstance(issues,list):
        raise VideoForgeError("WARDROBE_FILTER_DEFECTS_INVALID")
    return issues

def _facts(checklists:dict)->list[dict]:
    king=checklists["aldric"]["known_defects"]
    purple=checklists["elara"]["known_defects"]
    if (len(king)<2 or len(purple)<1
            or {x.get("id") for x in king if isinstance(x,dict)}
                !={"aldric_red_black_inversion","aldric_beard_color_changed"}):
        raise VideoForgeError("WARDROBE_FILTER_OWNER_REPORT_INCOMPLETE")
    inversion=next(x for x in king if x["id"]=="aldric_red_black_inversion")
    a,b=inversion["scene_a"],inversion["scene_b"]
    if (a.get("outer_garment_color")!="vermelho" or
            a.get("center_panel_color")!="preto" or
            b.get("outer_garment_color")!="preto" or
            b.get("center_panel_color")!="vermelho"):
        raise VideoForgeError("WARDROBE_FILTER_RED_BLACK_INVERSION_UNVERIFIED")
    beard=next(x for x in king if x["id"]=="aldric_beard_color_changed")
    if beard.get("beard_color_difference_confirmed_by_user") is not True:
        raise VideoForgeError("WARDROBE_FILTER_BEARD_CHANGE_NOT_RECORDED")
    chest=next(x for x in purple if x["id"]=="elara_purple_bodice_missing")
    present={x.get("purple_present") for x in chest.get("compared_panels",[])}
    if present!={True,False}:
        raise VideoForgeError("WARDROBE_FILTER_BODICE_REPORT_INCOMPLETE")
    findings=[
     {"actor":"aldric","code":"aldric_red_black_inversion",
      "verdict":"REPROVADO","severity":"CRITICO","evidence":"owner_report_not_pixel_measured",
      "detected_by":"semantic_comparison_of_user_descriptions",
      "description":"Rei sentado: roupa externa VERMELHA e centro PRETO. Em pé: roupa externa PRETA e centro VERMELHO. As cores inverteram sem mudança de roupa.",
      "correction":"Fixar um único mapa de cores por área de tecido, mesma variante sentada ou em pé.",
      "exact_frame_coordinates":None},
     {"actor":"aldric","code":"aldric_beard_color_changed",
      "verdict":"REPROVADO","severity":"CRITICO","evidence":"owner_report_not_pixel_measured",
      "detected_by":"explicit_owner_visual_feedback",
      "description":"Cor da barba muda e a identidade visual deixa de parecer o mesmo rei; tonalidades numéricas não medidas.",
      "correction":"Rever barba/cabelo contra uma referência individual aprovada; bloquear mudança de cor/silhueta sem arco narrativo.",
      "exact_frame_coordinates":None},
     {"actor":"elara","code":"elara_purple_bodice_missing",
      "verdict":"REPROVADO","severity":"CRITICO","evidence":"owner_report_not_pixel_measured",
      "detected_by":"semantic_comparison_of_user_descriptions",
      "description":"Parte ROXA no peitoral do vestido real aparece em uma imagem e some ou muda na outra.",
      "correction":"Manter painel roxo exatamente no mesmo lugar, tamanho e traço do traje palaciano em todos os ângulos.",
      "exact_frame_coordinates":None},
    ]
    return findings

def evaluate(root:Path=ROOT,sync:bool=False)->dict:
    root=Path(root)
    episode=root/EPISODE
    owner,contract=owner_review(root)
    approved=source_readiness(root)
    originals=_read_json(episode/"CONTINUIDADE-FIGURINOS-V2-40-TOMADAS.json")
    if (originals.get("schema")!="videoforge/remake-wardrobe-continuity-40/v1"
            or originals.get("total_shots")!=40
            or originals.get("total_frames")!=4890
            or originals.get("rejected_reference_sha256")!=owner.get("sha256")):
        raise VideoForgeError("WARDROBE_FILTER_WRONG_STORYBOARD")
    all_checks={name:_read_json(episode/file) for name,file in NAMES.items()}
    problems={name:_check(name,item) for name,item in all_checks.items()}
    if any(x.get("critical") is not True or x.get("reported") is not True
           for actor in ("aldric","elara") for x in problems[actor]):
        raise VideoForgeError("WARDROBE_FILTER_REJECTION_REQUIRES_OWNER_EVIDENCE")
    findings=_facts(all_checks)
    shots=[]
    impact={"aldric":[],"elara_royal":[],"elara_street":[],"kael":[]}
    for shot in originals["shots"]:
        sid=shot["shot_id"]
        outfits=shot["costumes"]
        affected=[]
        if "aldric" in outfits:
            impact["aldric"].append(sid)
            affected+=["aldric_red_black_inversion","aldric_beard_color_changed"]
        if outfits.get("elara",{}).get("royal_purple_bodice_required") is True:
            impact["elara_royal"].append(sid)
            affected.append("elara_purple_bodice_missing")
        elif "elara" in outfits:
            impact["elara_street"].append(sid)
        if "kael" in outfits:
            impact["kael"].append(sid)
        shots.append({
          "shot_id":sid,
          "affected_by_unapproved_character_reference":bool(affected),
          "blocking_known_reference_defects":sorted(set(affected)),
          "individual_shot_pixels_visually_checked":False,
          "verdict":"BLOQUEADO_POR_REFERENCIA_REPROVADA" if affected
                    else "REVISAO_VISUAL_PENDENTE",
          "official_render_allowed":False,
        })
    outcome={
      "schema":"videoforge/wardrobe-filter-result/v1",
      "scope":owner["scope"],
      "review_date":"2026-11-16",
      "owner_report_verified":True,
      "decision":{"aldric":"REPROVADO","elara_palace":"REPROVADO",
                  "elara_street":"REVISAO_PENDENTE","kael":"REVISAO_PENDENTE"},
      "source_decision_provenance":"explicit_owner_report_2026-11-16",
      "findings":findings,
      "inspections_required":{
        name:{"rules":len(check["rules"]),"approved":False,
              "source":"CHECKLIST-FIGURINO-"+name.upper()+".json"}
        for name,check in all_checks.items()
      },
      "shot_impact":impact,
      "shot_risk_register":shots,
      "shot_count":len(shots),
      "total_frames":originals["total_frames"],
      "reference_compare_source":"REVISAR-DETALHES-FIGURINOS-V2.md",
      "comparison_qa":"QA-FIGURINO-DETALHES-V2.json",
      "approved_full_outfits":approved["verified"],
      "required_full_outfits":approved["required"],
      "pixel_level_outfit_or_beard_segmentation_available":False,
      "pixel_color_statistics_claimed":False,
      "manual_check_of_unreviewed_shots_required":True,
      "approved_for_canonical_use":False,
      "r2_dispatched":False,
      "provider_calls":0,
      "new_images_generated":False,
      "official_mp4_created":False,
      "youtube_uploaded":False,
    }
    if sync:
        dest=episode/REPORT
        md=episode/REVIEW
        if dest.is_symlink() or md.is_symlink():
            raise VideoForgeError("WARDROBE_FILTER_OUTPUT_SYMLINK")
        content=json.dumps(outcome,ensure_ascii=False,indent=2)+"\n"
        if not dest.exists() or dest.read_text(encoding="utf-8")!=content:
            dest.write_text(content,encoding="utf-8")
        lines=[
            "# Resultado do filtro de figurino — EP01 V2 (40 tomadas)",
            "",
            "## Veredito resumido",
            "",
            "**ALDRIC: REPROVADO — 2 problemas críticos reportados pelo proprietário.**",
            "**ELARA (palácio): REPROVADA — 1 problema crítico reportado pelo proprietário.**",
            "**KAEL: REVISÃO PENDENTE — não há defeito específico confirmado; isso não é aprovação.**",
            "**ELARA (rua): REVISÃO PENDENTE — o corpete roxo NÃO é exigido no disfarce.**",
            "",
            "Os problemas abaixo são baseados no seu relato e nas descrições semânticas, **não numa medição automática de pixels**. O sistema verificou a contradição entre as versões descritas; não inventou cores numéricas nem inspeções de fotos que não ocorreram.",
            "",
            "## Diferenças filtradas",
            "",
        ]
        for item in findings:
            lines += [
                "### "+item["actor"].upper()+" — "+item["code"]+" (CRÍTICO, REPROVADO)",
                "",
                "**Diferença:** "+item["description"],
                "",
                "**Correção exigida:** "+item["correction"],
                "",
                "**Fonte da evidência:** relato visual explícito do proprietário; sem máscaras de roupa/barba nem coordenadas verificadas.",
                "",
            ]
        lines += [
            "## Tomadas afetadas pelo risco da referência",
            "",
            "**Aldric (7 tomadas):** "+", ".join(impact["aldric"])+".",
            "",
            "**Elara com traje real (6 tomadas):** "+", ".join(impact["elara_royal"])+".",
            "",
            "**Elara em disfarce (9 tomadas):** não foi aplicado o erro do peitoral roxo a esta variante narrativa.",
            "",
            "Essas são **dependências bloqueadas**, não uma alegação de que cada PNG de cada tomada tenha sido inspecionado e reprovado.",
            "",
            "## Checklists completos e provas visuais",
            "",
            "- [Checklist de Aldric](CHECKLIST-FIGURINO-ALDRIC.json) — barba, cor exterior/central, gola, bordados, manto, coroa e pose",
            "- [Checklist de Elara](CHECKLIST-FIGURINO-ELARA.json) — roxo do corpete, vestido e variante rua/palácio",
            "- [Checklist de Kael](CHECKLIST-FIGURINO-KAEL.json) — capa vinho, ombreira dourada, pedra azul e variantes",
            "- [Comparações de figurinos já arquivadas](REVISAR-DETALHES-FIGURINOS-V2.md)",
            "- [Resultados completos por tomada em JSON](RELATORIO-FILTRO-FIGURINO-V2.json)",
            "",
            "## Antes de aprovar alguma correção",
            "",
            "- [ ] Referência individual completa de Aldric aprovada, com cores e barba travadas",
            "- [ ] Referência individual do vestido palaciano de Elara aprovada, com painel roxo idêntico",
            "- [ ] Comparação visual da nova arte com cada fonte aprovada",
            "- [ ] Revisão de Kael e da variante de rua sem falsas exigências do corpete real",
            "- [ ] Se houver comparação automática de pixel, fornecer máscaras/ROIs realmente verificadas (sem inventar coordenadas)",
            "",
            "Aprovação automática **NÃO** foi executada; R2 permanece bloqueada, nenhuma imagem paga, MP4 ou publicação ocorreu nesta rodada.",
            "",
        ]
        txt="\n".join(lines)
        if not md.exists() or md.read_text(encoding="utf-8")!=txt:
            md.write_text(txt,encoding="utf-8")
    return outcome

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--sync",action="store_true")
    args=parser.parse_args()
    data=evaluate(sync=args.sync)
    print("WARDROBE_FILTER",json.dumps({
        "aldric":data["decision"]["aldric"],
        "elara_palace":data["decision"]["elara_palace"],
        "kael":data["decision"]["kael"],
        "critical_issues":len(data["findings"]),
        "shot_count":data["shot_count"],
        "provider_calls":0,
    }))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
