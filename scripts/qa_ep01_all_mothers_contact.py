"""Generate SHA-checked EP01 mother contact sheets for HUMAN review only.

Does not approve art, generate new art, segment sprites or run an image model.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFont
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

BASE=REL/"assets"/"geracoes"
NAME="QA-EP01-MAES-CATALOGO"
INVENTORY=ROOT/REL/"CHECKPOINT-IMAGENS-EP01-AUTO.json"

def font(sz):
    try: return ImageFont.truetype("DejaVuSans.ttf",sz)
    except OSError: return ImageFont.load_default()

def checked(path,digest):
    rel=Path(path)
    if rel.is_absolute() or ".." in rel.parts or not rel.is_relative_to(BASE):
        raise ValueError("Invalid archived source path")
    p=ROOT/rel
    if p.is_symlink() or not p.is_file(): raise ValueError("Missing original PNG: "+path)
    blob=p.read_bytes()
    if sha256(blob).hexdigest()!=digest: raise ValueError("SHA mismatch: "+path)
    with Image.open(BytesIO(blob)) as src:
        if src.format!="PNG" or min(src.size)<512:
            raise ValueError("Unexpected PNG canvas: "+path)
        return src.convert("RGB").copy()

def run():
    obj=json.loads(INVENTORY.read_text(encoding="utf-8"))
    if (obj.get("schema")!="videoforge/ep01-image-inventory-auto/v1"
        or obj.get("channel")!=CHANNEL or obj.get("video_id")!=VIDEO
        or obj.get("visual_shots")!=39
        or obj.get("human_visual_approval") is not False):
        raise ValueError("Invalid checkpoint")
    ids=sorted(set(obj["original_mother_shot_ids"]) |
               set(obj["missing_original_mother_shot_ids"]))
    if len(ids)!=39: raise ValueError("Must inventory exactly 39 visual shots")
    sources=obj["original_mothers"]
    sheets=[]
    for page in range(2):
        W,H=1350,2150
        board=Image.new("RGB",(W,H),"#eae8e3")
        pen=ImageDraw.Draw(board)
        pen.text((30,17),f"EP01 | REVISÃO DAS IMAGENS-MÃE | PRANCHA {page+1}/2",
                 font=font(24),fill="#111111")
        pen.text((30,53),"GERAÇÃO NÃO É APROVAÇÃO. Conferir mãos, objetos, figurinos, câmera e continuidade.",
                 font=font(15),fill="#a12e25")
        for index,shot in enumerate(ids[page*20:(page+1)*20]):
            col=index%5; row=index//5
            x=25+col*263; y=95+row*512
            pen.rounded_rectangle((x,y,x+250,y+497),radius=8,fill="#ffffff")
            pen.text((x+12,y+8),shot,font=font(21),fill="#222222")
            entry=sources.get(shot)
            if entry is not None:
                thumb=ImageOps.contain(checked(entry["file"],entry["sha256"]),
                                      (229,437),Image.Resampling.LANCZOS)
                board.paste(thumb,(x+(250-thumb.width)//2,y+35))
                pen.text((x+11,y+474),
                         "V1 REPROVADA - VER ALTERNATIVAS" if shot in {"C01-P02","C01-P03","C01-P04"}
                         else "GERADA - REVISÃO PENDENTE",
                         font=font(10),fill="#a33024" if shot in {"C01-P02","C01-P03","C01-P04"} else "#97600a")
            else:
                pen.text((x+35,y+231),"PENDENTE",font=font(20),fill="#ab3425")
        dest=ROOT/REL/f"{NAME}-{page+1:02}.jpg"
        board.save(dest,"JPEG",quality=88,optimize=True)
        sheets.append({"file":dest.name,"sha256":sha256(dest.read_bytes()).hexdigest()})
    alternates=obj.get("versioned_mother_candidates",[])
    if alternates:
        board=Image.new("RGB",(1350,625),"#eae8e3")
        pen=ImageDraw.Draw(board)
        pen.text((26,16),"EP01 - C01 | VERSÕES ALTERNATIVAS (NÃO APROVADAS)",
                 font=font(23),fill="#161616")
        pen.text((26,53),"Comparar com originais reprovadas: mãos, espada, bainha e posição do elenco.",
                 font=font(14),fill="#a33024")
        for i,entry in enumerate(alternates[:5]):
            x=25+i*263;y=93
            pen.rounded_rectangle((x,y,x+250,y+500),radius=8,fill="#ffffff")
            pen.text((x+10,y+8),entry["asset"][:25],font=font(11),fill="#222222")
            thumb=ImageOps.contain(checked(entry["file"],entry["sha256"]),
                                   (229,443),Image.Resampling.LANCZOS)
            board.paste(thumb,(x+(250-thumb.width)//2,y+34))
            pen.text((x+10,y+477),"CANDIDATA / QA PENDENTE",
                     font=font(11),fill="#a33024")
        out=ROOT/REL/(NAME+"-C01-ALTERNATIVAS.jpg")
        board.save(out,"JPEG",quality=88,optimize=True)
        sheets.append({"file":out.name,"sha256":sha256(out.read_bytes()).hexdigest()})
    result={"schema":"videoforge/ep01-contact-sheet-review/v1",
            "channel":CHANNEL,"video_id":VIDEO,"visual_shots":39,
            "mother_count":obj["visual_shots_with_original_mother"],
            "remaining":obj["visual_shots_missing_original_mother"],
            "sheets":sheets,"alternate_candidate_count":len(alternates),
            "historical_rejected_original_shots":["C01-P02","C01-P03","C01-P04"],
            "human_visual_approval":False,
            "rig_ready":False,"youtube_uploaded":False,
            "image_generation_calls":0,"no_sprite_extraction":True,
            "manual_checks":["personagem consistente","mãos e anatomia",
                             "carrinho/espada/lanças e contato",
                             "roupas e bainha","ângulos de câmera",
                             "continuidade de cenários e iluminação"]}
    (ROOT/REL/f"{NAME}.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_CONTACT_SHEETS",json.dumps(result,ensure_ascii=False))
    return result

if __name__=="__main__":run()
