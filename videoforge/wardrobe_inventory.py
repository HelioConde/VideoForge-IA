"""Audit EXISTING wardrobe visuals for human review without generating any art."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from .remake_autopilot import EPISODE,ROOT
from .wardrobe_review import owner_review,source_readiness
from .scene_layers import png_info
from .errors import VideoForgeError

SOURCES=[
 ("aldric","Aldric: candidato RGB da cena 01","assets/cena-01/rig-drafts/aldric-origem/aldric-RGB-da-mae-CANDIDATO.png","V1 candidate, not an owner-approved costume"),
 ("aldric","Aldric: corpo/vestimenta recortados","assets/cena-01/rig-drafts/aldric-partes/corpo-vestimenta-restante.png","V1 partial layer, not full-body canon"),
 ("aldric","Aldric: cena mae antiga no salao","assets/cenas-mae/cena-01.png","V1 scene context, non-canonical"),
 ("elara","Elara: close originalmente aprovado para estilo","assets/referencias/chat-aprovadas/elara-close-trono.png","Exact chat-original for visual style, NOT entire costume approval"),
 ("elara","Elara: enquadramento original C12-P02","assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png","Exact original camera framing, not wardrobe approval"),
 ("elara","Elara: cena mae antiga C12","assets/cenas-mae/cena-12.png","V1 scene context, non-canonical"),
]
REPORT="QA-INVENTARIO-FIGURINOS-V2.json"
DOC="REVISAR-OPCOES-FIGURINO-V2.md"

def inventory(root:Path=ROOT,sync:bool=False)->dict:
    ep=Path(root)/EPISODE
    owner,contract=owner_review(root)
    ready=source_readiness(root)
    rows=[]
    for actor,label,relative,origin in SOURCES:
        file=ep/relative
        if file.is_symlink() or not file.is_file() or not file.stat().st_size:
            raise VideoForgeError("WARDROBE_INVENTORY_EXISTING_SOURCE_MISSING")
        raw=file.read_bytes()
        if not raw.startswith(b"\x89PNG\r\n\x1a\n") or len(raw)>15000000:
            raise VideoForgeError("WARDROBE_INVENTORY_IMAGE_INVALID")
        info=png_info(raw,require_alpha=False)
        rows.append({
            "actor":actor,"label":label,"path":relative,"origin":origin,
            "sha256":hashlib.sha256(raw).hexdigest(),
            "dimensions":[info["width"],info["height"]],
            "exists":True,"owner_approved_full_outfit":False,
            "usable_as_grounded_r2_without_new_review":False,
            "source_pixels_modified":False
        })
    result={
       "schema":"videoforge/wardrobe-candidate-inventory/v1",
       "scope":owner["scope"],"status":"existing_candidates_waiting_for_owner_costume_review",
       "rejected_v2_sha256":owner["sha256"],
       "candidate_count":len(rows),"candidates":rows,
       "required_owner_approved_complete_outfits":ready["required"],
       "verified_owner_approved_complete_outfits":ready["verified"],
       "r2_ready":ready["r2_ready"],
       "visual_approval":False,"images_generated":0,
       "image_provider_calls":0,"youtube_uploaded":False,
    }
    if sync:
        report=ep/REPORT
        markdown=ep/DOC
        if report.is_symlink() or markdown.is_symlink():
            raise VideoForgeError("WARDROBE_INVENTORY_REPORT_SYMLINK")
        content=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
        if not report.is_file() or report.read_text(encoding="utf-8")!=content:
            report.write_text(content,encoding="utf-8")
        lines=[
           "# Revisao de figurinos — fontes ja arquivadas (ainda NAO aprovadas)",
           "",
           "O usuario reprovou a prancha grounded R1 por diferencas no traje do rei Aldric e no painel ROXO do peitoral da princesa Elara.",
           "As artes abaixo sao somente opcoes de inspeção. Algumas sao recortes/cenas legadas V1. Nem SHA valido nem estilo previamente aprovado significam traje completo aprovado.",
           "",
        ]
        for row in rows:
            lines.extend([
               "## "+row["label"],"",
               "Origem: "+row["origin"],
               "",
               "SHA-256: "+row["sha256"],"",
               "!["+row["actor"]+"]("+row["path"]+")","",
            ])
        lines.extend([
           "## Regras antes da proxima geracao","",
           "- Elara no palacio deve manter SEMPRE painel roxo na blusa/corpete e detalhes brancos, violetas e dourados; disfarce de rua e uma variante narrativa diferente.",
           "- Aldric deve manter as mesmas vestes reais bordo/vinho e dourado, gola clara e coroa, sem redesign.",
           "- As imagens legadas so podem ser usadas como referencias finais se forem inspecionadas e explicitamente aprovadas pelo usuario. Nunca promover candidatas automaticamente.",
           "- Se nenhum modelo existente for fiel, obter/impor referencias individuais do traje completo de Elara e Aldric antes da R2.",
           "",
           "Fontes completas aprovadas: "+str(ready["verified"])+"/"+str(ready["required"])+".",
           "Status R2: BLOQUEADA ate aprovacao visual e SHA das duas vestimentas.",
           "Nenhuma imagem nova gerada ou publicada neste inventario.","",
        ])
        content="\n".join(lines)
        if not markdown.is_file() or markdown.read_text(encoding="utf-8")!=content:
            markdown.write_text(content,encoding="utf-8")
    return result

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--sync",action="store_true")
    args=ap.parse_args()
    value=inventory(sync=args.sync)
    print("WARDROBE_INVENTORY",json.dumps({
        "candidates":value["candidate_count"],
        "approved_outfits":value["verified_owner_approved_complete_outfits"],
        "r2_ready":value["r2_ready"],"provider_calls":0}))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
