"""Offline visual review sheets, based only on SHA-verified original PNGs."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from .errors import VideoForgeError
from .cinematic_chat_references import reference_status
from .production_art import archived_reference,ROOT
from .remake_autopilot import EPISODE

OUTPUTS={"kael":"QA-KAEL-V2-COMPARACAO.jpg","elara":"QA-ELARA-V2-COMPARACAO.jpg"}
REPORT="QA-COMPARACAO-IDENTIDADE-V2.json"
REVIEW="REVISAR-IDENTIDADE-EP01-V2.md"

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def _save(path:Path,data:bytes)->None:
    if path.is_symlink():
        raise VideoForgeError("VISUAL_QA_OUTPUT_SYMLINK_BLOCKED")
    if not path.is_file() or path.read_bytes()!=data:
        path.write_bytes(data)

def comparison(root:Path=ROOT,sync:bool=False)->dict:
    root=Path(root)
    base=root/EPISODE
    status=reference_status(root)
    samples=status["samples"]
    camera=status["camera_candidate_C12_P02"]
    if status["original_source_files_sha_verified"]!=2 or not camera["source_verified"]:
        return {"schema":"videoforge/identity-comparison-qa/v1",
                "status":"awaiting_original_sha_sources","provider_calls":0,
                "human_approved":False,"new_art_created":False}
    sheet=archived_reference("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",
                             "character-bible",root)
    if sheet is None:
        raise VideoForgeError("VISUAL_QA_CANDIDATE_MISSING")
    candidate_bytes=(base/sheet["path"]).read_bytes()
    if sha(candidate_bytes)!=sheet["sha256"]:
        raise VideoForgeError("VISUAL_QA_CANDIDATE_SHA_CHANGED")
    try:
        from PIL import Image,ImageDraw,ImageFont,ImageOps
    except ImportError as e:
        raise VideoForgeError("VISUAL_QA_PILLOW_REQUIRED") from e
    with Image.open(io.BytesIO(candidate_bytes)) as img:
        img.load()
        if img.format!="PNG" or img.size!=(sheet["width"],sheet["height"]):
            raise VideoForgeError("VISUAL_QA_INVALID_CANDIDATE")
        candidate=img.convert("RGB")
    results=[]
    for actor,sample in zip(("kael","elara"),samples):
        source=base/sample["expected_repo_path"]
        source_bytes=source.read_bytes()
        if sha(source_bytes)!=sample["expected_sha256"]:
            raise VideoForgeError("VISUAL_QA_ORIGINAL_SHA_CHANGED")
        with Image.open(io.BytesIO(source_bytes)) as img:
            img.load()
            if (img.format!="PNG" or img.mode!="RGB"
                    or img.size!=tuple(sample["expected_dimensions_px"])):
                raise VideoForgeError("VISUAL_QA_INVALID_ORIGINAL_PNG")
            original=img.copy()
        canvas=Image.new("RGB",(1520,1050),(19,24,33))
        draw=ImageDraw.Draw(canvas)
        font=ImageFont.load_default(size=21)
        small=ImageFont.load_default(size=16)
        draw.text((30,25),actor.upper()+" ORIGINAL APROVADO NO CHAT",fill="white",font=font)
        draw.text((790,25),"CHARACTER BIBLE V2: CANDIDATA NAO APROVADA",fill="white",font=font)
        draw.text((30,65),sample["expected_sha256"][:32],fill=(170,190,210),font=small)
        draw.text((790,65),sheet["sha256"][:32],fill=(170,190,210),font=small)
        for i,image in enumerate((original,candidate)):
            resized=ImageOps.contain(image,(720,880),method=Image.Resampling.LANCZOS)
            x=25+i*765+(720-resized.width)//2
            y=110+(880-resized.height)//2
            canvas.paste(resized,(x,y))
        draw.text((30,1010),"SOMENTE QA. Previa JPEG derivada; PNGs originais intactos. Revisao humana pendente.",
                  fill=(242,220,165),font=small)
        buf=io.BytesIO()
        canvas.save(buf,format="JPEG",quality=92,optimize=True,subsampling=0)
        binary=buf.getvalue()
        if sync:
            _save(base/OUTPUTS[actor],binary)
        results.append({"actor":actor,"original_path":sample["expected_repo_path"],
                        "original_sha256":sample["expected_sha256"],
                        "candidate_path":sheet["path"],"candidate_sha256":sheet["sha256"],
                        "qa_preview_path":OUTPUTS[actor],"qa_preview_sha256":sha(binary),
                        "original_pixels_modified":False,
                        "identity_match_approved":False})
    result={"schema":"videoforge/identity-comparison-qa/v1",
            "status":"ready_for_explicit_human_identity_review",
            "scope":"alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
            "comparisons":results,
            "camera_c12_sha_verified":True,
            "aldric_approved_individual_original_missing":True,
            "provider_calls":0,"new_art_created":False,"original_pixels_modified":False,
            "human_approved":False,"official_mp4_created":False,"youtube_uploaded":False}
    if sync:
        _save(base/REPORT,(json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode())
        md=[
            "# EP01 V2 - comparacao visual de identidade",
            "",
            "Fontes originais verificadas por SHA. O JPEG e apenas uma visualizacao.",
            "A prancha V2 foi gerada por texto, sem as fontes antigas anexadas.",
            "A integridade SHA nao comprova fidelidade do rosto, cabelo ou traje.",
            "",
            "## Kael - original versus V2",
            "",
            "![Comparacao Kael](QA-KAEL-V2-COMPARACAO.jpg)",
            "",
            "## Elara - original versus V2",
            "",
            "![Comparacao Elara](QA-ELARA-V2-COMPARACAO.jpg)",
            "",
            "## Originais preservados",
            "",
            "- [Kael original](assets/referencias/chat-aprovadas/kael-close-salao.png)",
            "- [Elara original](assets/referencias/chat-aprovadas/elara-close-trono.png)",
            "- [C12-P02 original](assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png)",
            "- [Character-bible V2 candidata]("+sheet["path"]+")",
            "",
            "## Verificacao que exige pessoa",
            "",
            "- [ ] Identidade de Kael (olhos, rosto, cabelo, roupa, idade)",
            "- [ ] Identidade de Elara (olhos violeta, cabelo dourado, coroa e vestido)",
            "- [ ] Aldric (sem close individual aprovado por SHA)",
            "- [ ] Anatomia e quantidade correta de personagens, sem membros extras",
            "- [ ] Estilo 2D consistente com os originais e sem fotorrealismo",
            "- [ ] Revelacao de Elara somente a partir de C12",
            "",
            "Os checkboxes sao apenas instrucao. Nao alteram aprovacao no JSON.",
            "Sem aprovar a identidade visual, nao liberar geracao de cenas ou upload.",
            "",
        ]
        _save(base/REVIEW,("\n".join(md)).encode("utf-8"))
    return result

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    args=p.parse_args()
    report=comparison(sync=args.sync)
    print("IDENTITY_QA",json.dumps({
        "status":report["status"],"comparison_count":len(report.get("comparisons",[])),
        "provider_calls":0,"human_approved":False,
    }))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
