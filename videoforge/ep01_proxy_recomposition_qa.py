"""Visual/technical QA for C01-P03 mother vs independently generated proxy assets.

ImageChops and alpha operations here create ONLY comparisons, never sprites for
animation. No paid proxy requests, no human approval, no rig or video render.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from .ep01_shot_mother import existing_mother, ARCHIVE_PRODUCER
from .ep01_proxy_separate_parts import PRODUCER as RAW_PRODUCER
from .ep01_align_proxy_part import PRODUCER as ALIGNED_PRODUCER
from .layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from .errors import VideoForgeError

SHOT="C01-P03"
EXPECTED=["background-clean","character-kael","character-aldric"]
SCHEMA="videoforge/ep01-c01p03-proxy-composition-qa/v1"


def source(root:Path=ROOT):
    root=Path(root)
    mother=existing_mother(SHOT,root)
    if not mother:
        raise VideoForgeError("EP01_PROXY_QA_MOTHER_NOT_ARCHIVED")
    rel=REL/"assets"/"geracoes"/ARCHIVE_PRODUCER/str(mother["run_id"])/(SHOT.lower()+"-scene-mother.png")
    path=root/rel
    if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=mother["sha256"]:
        raise VideoForgeError("EP01_PROXY_QA_MOTHER_HASH_INVALID")
    return mother,path


def component(part:str,mother_sha:str,root:Path=ROOT):
    root=Path(root)
    if part not in EXPECTED:
        raise VideoForgeError("EP01_PROXY_QA_UNKNOWN_COMPONENT")
    raw_id=SHOT.lower()+"-"+part
    aligned_id=raw_id+"-native-aligned-v1"
    reg=json.loads((root/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json").read_text(encoding="utf-8"))
    rows=reg.get("geracoes",[])
    raw=[x for x in rows if x.get("asset")==raw_id and f"/{RAW_PRODUCER}/" in x.get("arquivo","")]
    aligned=[x for x in rows if x.get("asset")==aligned_id and f"/{ALIGNED_PRODUCER}/" in x.get("arquivo","")]
    if len(raw)!=1 or len(aligned)!=1:
        raise VideoForgeError("EP01_PROXY_QA_MISSING_INDEPENDENT_ASSETS "+part)
    result={}
    for kind,row,producer in (("raw",raw[0],RAW_PRODUCER),("aligned",aligned[0],ALIGNED_PRODUCER)):
        rel=Path(row["arquivo"])
        if rel.is_absolute() or ".." in rel.parts or not rel.is_relative_to(REL/"assets"/"geracoes"/producer):
            raise VideoForgeError("EP01_PROXY_QA_UNSAFE_ASSET_PATH")
        path=root/rel
        proof=path.with_suffix(".production.json")
        if any(x.is_symlink() or not x.is_file() for x in (path,proof)):
            raise VideoForgeError("EP01_PROXY_QA_ASSET_MISSING")
        blob=path.read_bytes()
        meta=json.loads(proof.read_text(encoding="utf-8"))
        if (hashlib.sha256(blob).hexdigest()!=row["sha256"] or
            meta.get("sha256")!=row["sha256"] or
            meta.get("source_mother_sha256")!=mother_sha or
            meta.get("generation_method")!="proxy_generated_separate_image" or
            meta.get("human_visual_approval") is not False):
            raise VideoForgeError("EP01_PROXY_QA_PROVENANCE_MISMATCH "+part)
        if kind=="raw" and meta.get("technical_qa")!="rejected_canvas_mismatch_no_pixel_resizing":
            raise VideoForgeError("EP01_PROXY_QA_UNEXPECTED_RAW_STATUS")
        if kind=="aligned" and (meta.get("technical_qa")!="candidate_canvas_aligned_needs_visual_recomposition_qa"
            or meta.get("technical_postprocess")!="pad_bottom_only_no_crop_or_rescale"
            or meta.get("source_pixels_unchanged") is not True
            or meta.get("source_image_sha256")!=raw[0]["sha256"]
            or meta.get("bottom_rows_added")!=1):
            raise VideoForgeError("EP01_PROXY_QA_ALIGNMENT_NOT_AUDITED "+part)
        result[kind]={"file":str(rel),"sha256":row["sha256"],"metadata":meta}
    return result


def analyze(root:Path=ROOT,write:bool=True)->dict:
    from PIL import Image,ImageChops,ImageStat,ImageDraw,ImageOps
    root=Path(root)
    mother,mpath=source(root)
    parts={part:component(part,mother["sha256"],root) for part in EXPECTED}
    with Image.open(mpath) as im:
        frame=im.convert("RGB")
    if frame.size!=(941,1672):
        raise VideoForgeError("EP01_PROXY_QA_CANVAS_INVALID")
    imgs={}
    for part in EXPECTED:
        path=root/parts[part]["aligned"]["file"]
        with Image.open(path) as im:
            if im.size!=frame.size:
                raise VideoForgeError("EP01_PROXY_QA_PART_CANVAS_MISMATCH")
            if part!="background-clean":
                if "A" not in im.getbands() or im.getchannel("A").getextrema()[0]!=0:
                    raise VideoForgeError("EP01_PROXY_QA_CHARACTER_WITHOUT_ALPHA")
                if im.getchannel("A").getextrema()[1]<128:
                    raise VideoForgeError("EP01_PROXY_QA_EMPTY_CHARACTER_ALPHA")
            imgs[part]=im.convert("RGBA")
    # Aldric sits behind Kael in the throne-room shot.
    rendered=imgs["background-clean"].copy()
    rendered.alpha_composite(imgs["character-aldric"])
    rendered.alpha_composite(imgs["character-kael"])
    rgb=rendered.convert("RGB")
    diff=ImageChops.difference(frame,rgb)
    global_diff=round(sum(ImageStat.Stat(diff).mean)/3,4)
    threshold=18
    local=diff.convert("L").point(lambda v:255 if v>=threshold else 0)
    diff_ratio=round(sum(local.histogram()[1:])/ (frame.width*frame.height)*100,2)
    cover={}
    for ident in ("character-kael","character-aldric"):
        mask=imgs[ident].getchannel("A")
        hist=mask.histogram()
        pixels=frame.width*frame.height
        nonzero=sum(hist[1:])
        cover[ident]={"bbox":list(mask.getbbox()) if mask.getbbox() else None,
                      "nonzero_alpha_percent":round(nonzero/pixels*100,2),
                      "background_leak_suspected":nonzero/pixels>0.85}
    report={
        "schema":SCHEMA,"shot_id":SHOT,"mother_sha256":mother["sha256"],
        "mother_archive_run_id":mother["run_id"],
        "source_dimensions":[941,1672],
        "independent_proxy_assets":{k:{"sha256":v["aligned"]["sha256"],
                              "source_raw_sha256":v["raw"]["sha256"]}
                             for k,v in parts.items()},
        "neutral_recomposition_source_order":["background-clean","character-aldric","character-kael"],
        "technical_comparison_only":True,
        "mean_absolute_rgb_difference":global_diff,
        "different_pixels_at_threshold_percent":diff_ratio,
        "threshold_rgb_intensity":threshold,
        "character_alpha_stats":cover,
        "qa_limitations":["Ungenerated movable props may still be visible in the mother",
                          "Newly painted hidden geometry is not expected to match original pixels perfectly",
                          "MAE cannot certify anatomy, outfit, hand contact or motion",
                          "Art and frame motion still require human review"],
        "visual_review_status":"pending",
        "human_visual_approval":False,"rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "generator":"offline QA only","provider_calls":0
    }
    if write:
        episode=root/REL
        board=Image.new("RGB",(1000,1870),"#eeeeee")
        draw=ImageDraw.Draw(board)
        thumbs=[
          ("A / C01-P03 MÃE (CANDIDATA)",frame),
          ("B / RECOMPOSIÇÃO RGBA (CANDIDATA)",rgb),
          ("C / MAPA DE DIFERENÇAS",diff),
          ("D / FUNDO LIMPO DO PROXY",imgs["background-clean"].convert("RGB")),
        ]
        for i,(title,img) in enumerate(thumbs):
            x=(i%2)*500+14
            y=(i//2)*920+14
            draw.text((x,y),title,fill="#171717")
            thumb=ImageOps.contain(img,(468,866),Image.Resampling.LANCZOS)
            board.paste(thumb,(x+(468-thumb.width)//2,y+22))
        board.save(episode/"QA-C01-P03-PROXY-RECOMPOSICAO.jpg",quality=83,optimize=True)
        report["contact_sheet_sha256"]=hashlib.sha256((episode/"QA-C01-P03-PROXY-RECOMPOSICAO.jpg").read_bytes()).hexdigest()
        (episode/"QA-C01-P03-PROXY-RECOMPOSICAO.json").write_text(
           json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_PROXY_NEUTRAL_QA",json.dumps({
        "mother_sha":mother["sha256"],"mean_rgb_diff":global_diff,
        "qa_only":True,"human_visual_approval":False},ensure_ascii=False))
    return report


if __name__=="__main__":
    analyze()
