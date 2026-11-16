"""Offline costume QA: existing image + center-of-frame detail crops.

This is NOT object localization or identity matching. Torso zoom uses an
explicit geometric crop. Source SHA is rechecked; JPEGs are QA derivatives.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from .errors import VideoForgeError
from .production_art import archived_reference
from .remake_autopilot import EPISODE, ROOT
from .wardrobe_inventory import inventory
from .wardrobe_review import owner_review, source_readiness

REPORT="QA-FIGURINO-DETALHES-V2.json"
REVIEW="REVISAR-DETALHES-FIGURINOS-V2.md"
OUTPUTS={
    "aldric":"QA-ALDRIC-ROUPA-DETALE-V2.jpg",
    "elara":"QA-ELARA-PEITORAL-ROXO-V2.jpg",
}

def _sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def _saved(path:Path, data:bytes)->None:
    if path.is_symlink():
        raise VideoForgeError("WARDROBE_DETAIL_OUTPUT_SYMLINK")
    if not path.is_file() or path.read_bytes()!=data:
        path.write_bytes(data)

def compare(root:Path=ROOT,sync:bool=False)->dict:
    root=Path(root)
    ep=root/EPISODE
    sources=inventory(root)
    owner,_=owner_review(root)
    status=source_readiness(root)
    new=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                           "character-bible-grounded",root)
    if new is None or new["sha256"]!=owner["sha256"]:
        raise VideoForgeError("WARDROBE_DETAIL_REJECTED_REFERENCE_NOT_ARCHIVED")
    if owner.get("decision")!="rejected_wardrobe_inconsistency":
        raise VideoForgeError("WARDROBE_DETAIL_REVIEW_NOT_REJECTED")
    try:
        from PIL import Image,ImageDraw,ImageFont,ImageOps
    except ImportError as exc:
        raise VideoForgeError("WARDROBE_DETAIL_PILLOW_REQUIRED") from exc

    existing=sources["candidates"]
    results=[]
    for actor in ("aldric","elara"):
        actor_rows=[v for v in existing if v["actor"]==actor]
        if len(actor_rows)!=3:
            raise VideoForgeError("WARDROBE_DETAIL_THREE_SOURCES_REQUIRED")
        actor_inputs=[(v["path"],v["sha256"],v["label"],v["origin"]) for v in actor_rows]
        actor_inputs.append((new["path"],new["sha256"],
                             "V2 grounded REPROVADA — para comparação apenas",
                             "grounded candidate from two attached PNGs, owner-rejected"))
        work=[]
        for relative,sha,label,origin in actor_inputs:
            raw=(ep/relative).read_bytes()
            if _sha(raw)!=sha:
                raise VideoForgeError("WARDROBE_DETAIL_ORIGINAL_SHA_MISMATCH")
            with Image.open(io.BytesIO(raw)) as im:
                im.load()
                if im.format!="PNG":
                    raise VideoForgeError("WARDROBE_DETAIL_ORIGINAL_NOT_PNG")
                work.append((im.convert("RGB"),relative,sha,label,origin))
        width,height=2120,1320
        canvas=Image.new("RGB",(width,height),(22,26,33))
        draw=ImageDraw.Draw(canvas)
        font=ImageFont.load_default(size=18)
        small=ImageFont.load_default(size=14)
        draw.text((28,12),
                  "ALDRIC — ROUPAS PARA INSPECAO / NAO APROVADAS" if actor=="aldric"
                  else "ELARA — PARTE ROXA DO PEITORAL / NAO APROVADAS",
                  font=font,fill=(245,245,245))
        draw.text((28,48),
                  "Superior: imagem inteira. Inferior: recorte CENTRAL heuristico (nao localiza pessoas).",
                  font=small,fill=(203,209,220))
        for index,(source,relative,digest,label,origin) in enumerate(work):
            x=20+index*525
            draw.text((x,81),label[:49],font=small,fill=(238,239,240))
            draw.text((x,110),digest[:22],font=small,fill=(172,194,213))
            whole=ImageOps.contain(source,(495,670),method=Image.Resampling.LANCZOS)
            canvas.paste(whole,(x+(495-whole.width)//2,
                                 143+(670-whole.height)//2))
            w,h=source.size
            box=(int(w*.18),int(h*.26),int(w*.82),int(h*.72))
            zoom=source.crop(box)
            zoom=ImageOps.contain(zoom,(495,382),method=Image.Resampling.LANCZOS)
            canvas.paste(zoom,(x+(495-zoom.width)//2,
                                 842+(382-zoom.height)//2))
        draw.text((20,1282),
                  "JPEG QA derivado | PNGs preservados | NENHUMA aprovacao automatica | sem chamadas IA",
                  font=small,fill=(243,203,142))
        out=io.BytesIO()
        canvas.save(out,format="JPEG",quality=87,subsampling=0,optimize=True)
        blob=out.getvalue()
        if sync:
            _saved(ep/OUTPUTS[actor],blob)
        results.append({
            "actor":actor,
            "qa_jpeg_path":OUTPUTS[actor],
            "qa_jpeg_sha256":_sha(blob),
            "source_images":[{"path":r,"sha256":s,"label":t,"origin":o}
                             for _,r,s,t,o in work],
            "detail_crop_method":"center_rect_x_18_82_y_26_72",
            "detail_crop_is_subject_detection":False,
            "preserves_png_source_bytes":True,
            "original_wardrobe_approved":False,
            "generated_new_art":False,
        })
    result={
        "schema":"videoforge/wardrobe-detail-qa/v1",
        "scope":"alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
        "owner_decision":"rejected_wardrobe_inconsistency",
        "rejected_candidate_sha256":new["sha256"],
        "comparisons":results,
        "approved_full_wardrobe_references":status["verified"],
        "required_full_wardrobe_references":status["required"],
        "can_generate_r2":False,
        "human_visual_approval":False,
        "image_provider_calls":0,
        "new_images_generated":False,
        "source_pngs_modified":False,
        "official_mp4_created":False,
        "youtube_uploaded":False,
    }
    if sync:
        _saved(ep/REPORT,(json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
        lines=[
            "# EP01 V2 — revisar detalhes dos figurinos",
            "",
            "**Não aprovar a candidata grounded anterior.** Sua roupa foi reprovada por divergência em Aldric e no painel roxo de Elara.",
            "",
            "As duas folhas abaixo usam **somente imagens arquivadas**. A faixa superior mostra cada imagem original completa; a inferior amplia um retângulo central.",
            "**O zoom não detecta automaticamente o torso**: se a pessoa estiver deslocada, o recorte pode não mostrar a roupa relevante. A imagem completa está logo acima.",
            "",
            "## Aldric — comparação de traje real",
            "",
            "!["+OUTPUTS["aldric"]+"]("+OUTPUTS["aldric"]+")",
            "",
            "Conferir gola clara, túnica vinho/bordô, bordados dourados, manto, coroa e posição dos ornamentos. Não usar recorte V1 como figurino canônico sem autorização.",
            "",
            "## Elara — comparação do painel roxo",
            "",
            "!["+OUTPUTS["elara"]+"]("+OUTPUTS["elara"]+")",
            "",
            "Conferir se a peça roxa fica no **mesmo local do peitoral/corpete palaciano** e se os bordados são conservados entre diferentes enquadramentos. Não comparar disfarce de rua com roupa real.",
            "",
            "## Decisão de produção",
            "",
            "- [ ] Elara — referência de roupa de corpo inteiro selecionada e aprovada explicitamente",
            "- [ ] Aldric — referência de roupa de corpo inteiro selecionada e aprovada explicitamente",
            "- [ ] Referências originais preservadas por SHA e não apenas parecidas",
            "- [ ] A nova R2 só é solicitada depois dos dois figurinos fixados",
            "",
            "**O preenchimento dos checkboxes não altera o estado do projeto.** A decisão precisa ser comunicada explicitamente e registrada no contrato.",
            "",
        ]
        _saved(ep/REVIEW,("\n".join(lines)).encode("utf-8"))
    return result

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    args=p.parse_args()
    obj=compare(sync=args.sync)
    print("WARDROBE_DETAIL_QA",json.dumps({
        "status":obj["owner_decision"],
        "comparisons":len(obj["comparisons"]),
        "approved_full_wardrobe_references":obj["approved_full_wardrobe_references"],
        "image_provider_calls":0,"human_approved":False,
    }))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
