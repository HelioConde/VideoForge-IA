"""Human QA only: compare SHA-approved source, text-only sheet, grounded sheet."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from .errors import VideoForgeError
from .production_art import archived_reference,ROOT
from .grounded_identity import EXPECTED,inputs
from .remake_autopilot import EPISODE

REPORT="QA-IDENTIDADE-GROUNDED-V2.json"
DOC="REVISAR-GROUNDED-V2.md"
PREVIEWS={"kael":"QA-KAEL-TRIPLO-V2.jpg","elara":"QA-ELARA-TRIPLO-V2.jpg"}

def sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def write_if_changed(path:Path,data:bytes)->None:
    if path.is_symlink():
        raise VideoForgeError("GROUNDED_REVIEW_OUTPUT_SYMLINK")
    if not path.is_file() or path.read_bytes()!=data:
        path.write_bytes(data)

def provenance(episode:Path,new:dict)->list[dict]:
    path=(episode/new["path"]).with_suffix(".production.json")
    if path.is_symlink() or not path.is_file():
        raise VideoForgeError("GROUNDED_REVIEW_PRODUCER_REPORT_MISSING")
    try:
        proof=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError,UnicodeError):
        raise VideoForgeError("GROUNDED_REVIEW_PRODUCER_REPORT_INVALID") from None
    expected=[{"actor":actor,"id":sid,"path":rel,"sha256":digest}
              for actor,(sid,rel,digest) in EXPECTED.items()]
    if (proof.get("schema")!="videoforge/production-art-result/v1"
            or proof.get("asset_id")!="character-bible-grounded"
            or proof.get("channel")!="alchemy-lab"
            or proof.get("video_id")!="mmorpg-conquiste-a-princesa-ep01"
            or proof.get("sha256")!=new["sha256"]
            or proof.get("source_images_attached_to_request")!=2
            or proof.get("source_originals_sha_verified")!=expected
            or proof.get("human_visual_approval") is not False
            or proof.get("official_video_created") is not False
            or proof.get("youtube_uploaded") is not False):
        raise VideoForgeError("GROUNDED_REVIEW_ORIGINAL_PROVENANCE_INVALID")
    return expected

def compare(root:Path=ROOT,sync:bool=False)->dict:
    root=Path(root)
    ep=root/EPISODE
    old=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                           "character-bible",root)
    new=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                           "character-bible-grounded",root)
    if new is None:
        return {"schema":"videoforge/grounded-identity-review/v1",
                "status":"waiting_for_grounded_candidate","provider_calls":0,
                "human_approved":False}
    if old is None:
        raise VideoForgeError("GROUNDED_REVIEW_OLD_SHEET_MISSING")
    proof=provenance(ep,new)
    try:
        from PIL import Image,ImageDraw,ImageFont,ImageOps
    except ImportError as e:
        raise VideoForgeError("GROUNDED_REVIEW_PILLOW_REQUIRED") from e
    sheets=[]
    for item in (old,new):
        blob=(ep/item["path"]).read_bytes()
        if sha(blob)!=item["sha256"]:
            raise VideoForgeError("GROUNDED_REVIEW_SHEET_SHA_CHANGED")
        with Image.open(io.BytesIO(blob)) as im:
            im.load()
            if im.format!="PNG" or im.size!=(item["width"],item["height"]):
                raise VideoForgeError("GROUNDED_REVIEW_PNG_INVALID")
            sheets.append(im.convert("RGB"))
    comps=[]
    for source in inputs(root):
        actor=source["actor"]
        with Image.open(io.BytesIO(source["bytes"])) as im:
            im.load()
            if im.format!="PNG":
                raise VideoForgeError("GROUNDED_REVIEW_ORIGINAL_PNG_INVALID")
            original=im.convert("RGB")
        canvas=Image.new("RGB",(2380,1220),(19,24,33))
        dr=ImageDraw.Draw(canvas)
        font=ImageFont.load_default(size=20)
        small=ImageFont.load_default(size=16)
        triples=[
            (original,actor.upper()+" — ORIGINAL POR SHA",source["sha256"]),
            (sheets[0],"PRANCHA ANTERIOR — SÓ TEXTO",old["sha256"]),
            (sheets[1],"NOVA PRANCHA — 2 PNGs ANEXADOS",new["sha256"]),
        ]
        for i,(image,label,digest) in enumerate(triples):
            x=25+i*790
            dr.text((x,24),label,fill="white",font=font)
            dr.text((x,63),digest[:32],fill=(188,201,215),font=small)
            scaled=ImageOps.contain(image,(740,1040),Image.Resampling.LANCZOS)
            canvas.paste(scaled,(x+(740-scaled.width)//2,
                                 105+(1040-scaled.height)//2))
        dr.text((25,1185),"PREVIA QA: nao aprova identidade; originais PNG preservados.",
                fill=(245,221,168),font=small)
        output=io.BytesIO()
        canvas.save(output,"JPEG",quality=91,subsampling=0,optimize=True)
        data=output.getvalue()
        if sync:
            write_if_changed(ep/PREVIEWS[actor],data)
        comps.append({
            "actor":actor,"original_sha256":source["sha256"],
            "text_candidate_sha256":old["sha256"],
            "grounded_candidate_sha256":new["sha256"],
            "preview_path":PREVIEWS[actor],"preview_sha256":sha(data),
            "human_identity_approved":False,"original_png_modified":False,
        })
    report={
        "schema":"videoforge/grounded-identity-review/v1",
        "status":"grounded_png_sha_verified_visual_review_pending",
        "scope":"alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
        "grounded_run_id":new["run_id"],"grounded_sha256":new["sha256"],
        "grounded_dimensions":[new["width"],new["height"]],
        "old_text_only_sha256":old["sha256"],
        "sha_verified_provider_input_sources":proof,
        "comparisons":comps,
        "aldric_individual_reference_sha_missing":True,
        "human_approved":False,"canonical_approved":False,
        "provider_calls":0,"original_png_modified":False,
        "new_art_generated_during_qa":False,"full_mp4":False,
        "youtube_uploaded":False,
    }
    if sync:
        write_if_changed(ep/REPORT,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())
        lines=[
            "# EP01 V2 - comparar original, arte de texto e arte baseada em PNG",
            "",
            "As duas fontes de Kael/Elara foram realmente anexadas à nova geração, por SHA.",
            "A prova de anexos NÃO equivale à correspondência visual nem à aprovação.",
            "",
            "## Kael",
            "![Kael original vs anterior vs nova]("+PREVIEWS["kael"]+")",
            "",
            "## Elara",
            "![Elara original vs anterior vs nova]("+PREVIEWS["elara"]+")",
            "",
            "## Critérios de revisão",
            "- [ ] Kael mantém face, olhos âmbar, cabelo escuro e capa vinho",
            "- [ ] Elara mantém face, olhos violeta, cabelo dourado e trajes",
            "- [ ] Aldric: falta original individual aprovado",
            "- [ ] Sem anatomia duplicada, personagens extras ou mudanças de estilo",
            "- [ ] Sem cortar/deformar rostos para preencher formato diferente",
            "",
            "**Não canonizar ou disparar tomadas com base apenas nestas prévias.**",
            "Manter as duas pranchas arquivadas com SHA. Sem MP4 oficial/YouTube.",
            "",
        ]
        write_if_changed(ep/DOC,("\n".join(lines)).encode())
    return report

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--sync",action="store_true")
    args=ap.parse_args()
    d=compare(sync=args.sync)
    print("GROUNDED_REVIEW_QA",json.dumps({
        "status":d["status"],"comparisons":len(d.get("comparisons",[])),
        "human_approved":False,"provider_calls":0,
    }))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
