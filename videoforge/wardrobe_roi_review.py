"""SHA-based visual annotation boards from unapproved historic frames.
Draft V1 polygons are NOT beard/garment ROIs; no image or identity approval.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE
from .wardrobe_review import owner_review, source_readiness

REPORT="QA-ROI-FIGURINOS-V2.json"
GUIDE="REVISAR-ROI-FIGURINOS-V2.md"
BOARDS={"aldric":"QA-ALDRIC-ROI-PROPOSTAS-V2.jpg",
        "elara":"QA-ELARA-ROI-CENAS-V2.jpg"}
KING="assets/cena-01/rig-drafts/aldric-origem/aldric-RGB-da-mae-CANDIDATO.png"
ELARA="assets/referencias/chat-aprovadas/elara-close-trono.png"
ELARA_SHA="bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a"

def load_png(ep,rel,sha=None):
    from PIL import Image
    file=ep/rel
    if file.is_symlink() or not file.is_file() or not 50<=file.stat().st_size<=16000000:
        raise VideoForgeError("ROI_SOURCE_NOT_SAFE")
    raw=file.read_bytes()
    hash_=hashlib.sha256(raw).hexdigest()
    if sha is not None and sha!=hash_:
        raise VideoForgeError("ROI_SHA_MISMATCH")
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.format!="PNG":
            raise VideoForgeError("ROI_SOURCE_NOT_PNG")
        image=im.convert("RGB")
    return image,hash_

def save_if_changed(file,blob):
    if file.is_symlink():
        raise VideoForgeError("ROI_OUTPUT_SYMLINK")
    if not file.is_file() or file.read_bytes()!=blob:
        file.write_bytes(blob)

def board(panels,actor,polygons):
    from PIL import Image,ImageDraw,ImageFont,ImageOps
    canvas=Image.new("RGB",(2080,1060),(21,25,34))
    dr=ImageDraw.Draw(canvas)
    label=ImageFont.load_default(size=19)
    small=ImageFont.load_default(size=16)
    head=("ALDRIC: POLIGONOS V1 NAO APROVADOS"
          if actor=="aldric" else "ELARA: ANOTAR CORPETE ROXO ANTES DE MEDIR")
    dr.text((25,18),head,font=label,fill="white")
    dr.text((25,55),"Fontes existentes; sem reconhecedor de pessoa ou tecido.",font=small,fill=(206,218,232))
    for i,p in enumerate(panels):
        x=25+i*690
        im=p["image"].copy()
        if actor=="aldric" and i==0:
            marker=ImageDraw.Draw(im)
            for j,poly in enumerate(polygons):
                pts=poly["vertices"]
                color=((252,201,81),(98,214,203),(251,119,173))[j%3]
                marker.line(pts+[pts[0]],fill=color,width=5)
        scaled=ImageOps.contain(im,(655,838),Image.Resampling.LANCZOS)
        canvas.paste(scaled,(x+(655-scaled.width)//2,
                             100+(838-scaled.height)//2))
        dr.text((x,957),p["label"],font=small,fill=(244,244,244))
        dr.text((x,986),"SHA "+p["sha256"][:31],font=small,fill=(182,200,219))
    dr.text((25,1027),"SO QA | arte original intacta | C02/C03: pose e personagem nao confirmados",
            font=small,fill=(245,215,152))
    out=io.BytesIO()
    canvas.save(out,format="JPEG",quality=88,optimize=True,subsampling=0)
    return out.getvalue()

def prepare(root:Path=ROOT,sync:bool=False):
    root=Path(root)
    ep=root/EPISODE
    owner,_=owner_review(root)
    readiness=source_readiness(root)
    rig_file=ep/"rig-aldric-pixel-partition.json"
    if rig_file.is_symlink() or not rig_file.is_file():
        raise VideoForgeError("ROI_RIG_DRAFT_MISSING")
    rig=json.loads(rig_file.read_text(encoding="utf-8"))
    if (rig.get("schema")!="videoforge/existing-pixel-partition/v1"
            or rig.get("source_path")!=KING
            or rig.get("human_visual_approval") is not False
            or rig.get("canvas")!={"width":1024,"height":1536}):
        raise VideoForgeError("ROI_RIG_DRAFT_UNTRUSTED")
    polygons=[]
    for id_ in ("coroa-cabelo-rosto","manto-esquerdo","manto-direito"):
        selected=[x for x in rig["layers"] if x["id"]==id_]
        if len(selected)!=1: raise VideoForgeError("ROI_POLYGON_MISSING")
        pts=selected[0]["vertices"]
        if (not isinstance(pts,list) or len(pts)<3
                or any(not isinstance(p,list) or len(p)!=2
                       or type(p[0]) is not int or type(p[1]) is not int
                       or not 0<=p[0]<1024 or not 0<=p[1]<1536 for p in pts)):
            raise VideoForgeError("ROI_POLYGON_INVALID")
        polygons.append({"id":id_,"vertices":pts,
                         "semantic_beard_or_center_confirmed":False})
    sources={
      "aldric":[
       (KING,"Aldric C01 (candidato sentado)",rig["source_sha256"]),
       ("assets/cenas-mae/cena-02.png","C02 (pose nao verificada)",None),
       ("assets/cenas-mae/cena-03.png","C03 (pose nao verificada)",None)],
      "elara":[
       (ELARA,"Close Elara (fonte chat)",ELARA_SHA),
       ("assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png",
        "C12-P02 fonte cinematografica",None),
       ("assets/cenas-mae/cena-12.png","C12 antiga (nao canonica)",None)]
    }
    previews={}
    for actor,specs in sources.items():
        panels=[]
        for relative,name,expected in specs:
            image,sha=load_png(ep,relative,expected)
            panels.append({"image":image,"path":relative,"label":name,
                           "sha256":sha})
        jpeg=board(panels,actor,polygons)
        if sync: save_if_changed(ep/BOARDS[actor],jpeg)
        previews[actor]={
          "path":BOARDS[actor],
          "sha256":hashlib.sha256(jpeg).hexdigest(),
          "sources":[{"path":x["path"],"sha256":x["sha256"],
                      "label":x["label"],"approved_full_costume":False}
                     for x in panels],
          "draft_polygons":polygons if actor=="aldric" else [],
        }
    regions=[]
    for actor,region in (("aldric","beard"),("aldric","garment_outer"),
                         ("aldric","garment_center"),("elara","royal_bodice")):
        regions.append({
          "actor":actor,"semantic_region":region,
          "source_a_sha256":None,"source_b_sha256":None,
          "source_a_polygon":None,"source_b_polygon":None,
          "mask_pair_human_verified":False,
          "auto_compare_ready":False,
          "status":"awaiting_semantically_verified_region_pair"
        })
    result={
      "schema":"videoforge/wardrobe-roi-review/v1",
      "status":"six_existing_images_prepared_for_roi_labeling",
      "previews":previews,
      "region_slots":regions,
      "king_polygons_from_unapproved_v1_rig":True,
      "king_c02_c03_pose_known":False,
      "actual_beard_roi_verified":False,
      "actual_outer_center_roi_verified":False,
      "actual_elara_bodice_roi_verified":False,
      "approved_full_costumes":readiness["verified"],
      "owner_rejected_candidate_sha256":owner["sha256"],
      "automatic_approval":False,
      "provider_calls":0,"source_pngs_unchanged":True,
      "official_video_created":False,"youtube_uploaded":False,
    }
    if sync:
        save_if_changed(ep/REPORT,(json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode())
        rows=[
          "# EP01 V2 — revisão de regiões para filtro preciso de cor","",
          "As linhas desenhadas sobre Aldric são polígonos do rig V1 NÃO aprovados.",
          "Eles incluem cabeça/coroa ou partes do manto, e NÃO isolam só barba ou centro da roupa.","",
          "## Aldric — C01, C02 e C03","",
          "![Alinhamento do rei]("+BOARDS["aldric"]+")","",
          "C01 mostra os polígonos de cabeça/mantos V1. A identidade e pose em C02 e C03 não foram verificadas; precisam ser selecionadas antes de comparar sentado versus em pé.","",
          "## Elara — close, C12 e cena antiga","",
          "![Alinhamento da princesa]("+BOARDS["elara"]+")","",
          "Nenhuma dessas fontes fornece automaticamente a máscara do peitoral roxo do vestido palaciano.","",
          "## Regiões que exigem identificação",
          "- [ ] Barba de Aldric nas duas poses",
          "- [ ] Tecido exterior de Aldric nas duas poses",
          "- [ ] Tecido central de Aldric nas duas poses",
          "- [ ] Corpete real de Elara nas duas imagens palacianas","",
          "Cada máscara precisa preservar o SHA da fonte e ser validada semanticamente antes da medição.",
          "O sistema continua reprovando a referência antiga e não aprova a R2 sem fontes corretas.","",
        ]
        save_if_changed(ep/GUIDE,("\n".join(rows)).encode())
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    v=p.parse_args()
    result=prepare(sync=v.sync)
    print("ROI_PREVIEW",json.dumps({
      "images":sum(len(x["sources"]) for x in result["previews"].values()),
      "regions_pending":len(result["region_slots"]),
      "approved":False,"provider_calls":0,
    }))

if __name__=="__main__":
    main()
