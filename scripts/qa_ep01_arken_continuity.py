"""Arken road -> walls continuity QA. No AI calls or sprite extraction."""
from __future__ import annotations
from io import BytesIO
from hashlib import sha256
import json
import sys
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO

IDS=[
("C05-P01 / KAEL DESPERTA NA ESTRADA","c05-p01-scene-mother","production-scene-mother-v2"),
("MESTRE BIBLIA / MURALHAS DE ARKEN","biblia-arken-muralhas-base-v1","production-art-request"),
("C05-P02 / KAEL CHEGA A ARKEN","c05-p02-scene-mother","production-scene-mother-v2")
]
SCHEMA="videoforge/ep01-c05-arken-visual-qa/v1"

def build():
    registry=ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
    entries=json.loads(registry.read_text(encoding="utf-8")).get("geracoes",[])
    source=[]
    for label,asset,producer in IDS:
        matches=[x for x in entries if x.get("asset")==asset and
                 f"/{producer}/" in str(x.get("arquivo",""))]
        if len(matches)!=1:
            raise RuntimeError("EP01_ARKEN_MISSING_OR_DUPLICATE_IMAGE "+asset)
        row=matches[0]
        rel=Path(row["arquivo"])
        base=REL/"assets"/"geracoes"/producer
        if rel.is_absolute() or ".." in rel.parts or not rel.is_relative_to(base):
            raise RuntimeError("EP01_ARKEN_BAD_SOURCE_PATH "+asset)
        p=ROOT/rel
        proof=p.with_suffix(".production.json")
        if any(x.is_symlink() or not x.is_file() for x in (p,proof)):
            raise RuntimeError("EP01_ARKEN_SOURCE_MISSING "+asset)
        blob=p.read_bytes();sha=sha256(blob).hexdigest()
        m=json.loads(proof.read_text(encoding="utf-8"))
        if (sha!=row.get("sha256") or m.get("sha256")!=sha
            or m.get("human_visual_approval") is not False):
            raise RuntimeError("EP01_ARKEN_SOURCE_SHA_OR_STATUS_INVALID "+asset)
        with Image.open(BytesIO(blob)) as im:
            if im.format!="PNG":raise RuntimeError("EP01_ARKEN_NOT_PNG")
            frame=im.convert("RGB").copy()
        source.append((label,frame,{"asset":asset,"sha256":sha,"file":rel.as_posix(),
              "dimensions":[frame.width,frame.height],"approved_for_rig":False}))
    tile_w,tile_h=460,860
    board=Image.new("RGB",(3*tile_w+32,tile_h+112),"#f0f0ee")
    d=ImageDraw.Draw(board)
    d.text((14,12),"QA ARKEN: ESTRADA -> MESTRE DA CIDADE -> TOMADA C05-P02",fill="#202020")
    for k,(label,im,meta) in enumerate(source):
        x=16+k*tile_w;y=60
        d.text((x,y),label,fill="#202020")
        im=ImageOps.contain(im,(tile_w-24,tile_h-64),Image.Resampling.LANCZOS)
        board.paste(im,(x+(tile_w-24-im.width)//2,y+28))
    d.text((14,board.height-32),
           "Referencias e tomadas geradas; comparar estilo e identidade sem aprovar rig.",
           fill="#912727")
    out=ROOT/REL/"QA-C05-ARKEN-CONTINUIDADE.jpg"
    board.save(out,"JPEG",quality=85,optimize=True)
    result={"schema":SCHEMA,"shots":["C05-P01","C05-P02"],
     "panel_count":3,"sources":[s[2] for s in source],
     "sheet":out.name,"sheet_sha256":sha256(out.read_bytes()).hexdigest(),
     "manual_review_checks":["road_dirt_vegetation_and_light_match_city_approach",
       "city_walls_towers_gate_resemble_visual_bible_master",
       "kael_small_walking_on_road_and_medieval_costume_consistent",
       "no_duplicate_floating_props_or_invented_cast",
       "continuous_geography_without_change_of_portal_shape"],
     "visual_review_status":"pending",
     "human_visual_approval":False,"rig_ready":False,
     "mp4_generated":False,"youtube_uploaded":False,
     "proxy_calls":0,"no_pixel_cutouts_for_rig":True}
    (ROOT/REL/"QA-C05-ARKEN-CONTINUIDADE.json").write_text(
         json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_ARKEN_VISUAL_QA",json.dumps({"images":3,"paid_calls":0,"sha":result["sheet_sha256"]}))
    return result

if __name__=="__main__":
    try:build()
    except (OSError,ValueError,RuntimeError) as err:
        print("EP01_ARKEN_VISUAL_QA_BLOCKED",str(err),file=sys.stderr)
        sys.exit(2)
