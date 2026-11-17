#!/usr/bin/env python3
"""Contact sheet of historical V1 vs corrected V2 mother candidates, SHA verified.

Never approves V2, creates character crops for animation, calls proxy or renders MP4.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageChops,ImageStat

from videoforge.ep01_corrected_mother_v2 import REJECTED_SOURCES,PRODUCER
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL
from videoforge.ep01_shot_mother import ARCHIVE_PRODUCER,existing_mother

def main()->None:
    registry=json.loads((ROOT/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json").read_text(encoding="utf-8"))
    view=[]
    proof_rows=[]
    for shot in ("C01-P03","C01-P04"):
        old=existing_mother(shot)
        if not old or old["sha256"]!=REJECTED_SOURCES[shot]:
            raise RuntimeError("EP01_V2_COMPARE_REJECTED_SOURCE_CHANGED")
        filename=shot.lower()+"-scene-mother.png"
        p=ROOT/REL/"assets"/"geracoes"/ARCHIVE_PRODUCER/str(old["run_id"])/filename
        oldraw=p.read_bytes()
        if hashlib.sha256(oldraw).hexdigest()!=old["sha256"]:
            raise RuntimeError("EP01_V2_COMPARE_V1_SHA_FAILED")
        asset=shot.lower()+"-scene-mother-v2"
        rows=[x for x in registry.get("geracoes",[]) if x.get("asset")==asset]
        if len(rows)!=1:
            raise RuntimeError("EP01_V2_COMPARE_MISSING_ARCHIVED_CORRECTED_MOTHER")
        row=rows[0]
        rel=Path(row["arquivo"])
        if (rel.is_absolute() or ".." in rel.parts or
            not rel.is_relative_to(REL/"assets"/"geracoes"/PRODUCER)):
            raise RuntimeError("EP01_V2_COMPARE_UNSAFE_SOURCE")
        f=ROOT/rel;metadata=f.with_suffix(".production.json")
        if f.is_symlink() or metadata.is_symlink() or not f.is_file() or not metadata.is_file():
            raise RuntimeError("EP01_V2_COMPARE_PROVENANCE_MISSING")
        raw=f.read_bytes()
        report=json.loads(metadata.read_text(encoding="utf-8"))
        if (hashlib.sha256(raw).hexdigest()!=row["sha256"] or
            report.get("sha256")!=row["sha256"] or
            report.get("source_image_sha256")!=old["sha256"] or
            report.get("generation_method")!="proxy_edited_versioned_scene_mother" or
            report.get("human_visual_approval") is not False or
            report.get("technical_qa") not in (
                "candidate_valid_png_no_visual_approval","rejected_canvas_mismatch")):
            raise RuntimeError("EP01_V2_COMPARE_REPORT_INVALID")
        raw_version_sha=row["sha256"]
        raw_version_rel=rel.as_posix()
        # The original V2 provider image is immutable. Only C01-P04
        # required 1px bottom padding; the aligned candidate has its own SHA.
        if shot=="C01-P04":
            from videoforge.ep01_align_corrected_mother_v2 import (
                ASSET as ALIGN_ASSET,PRODUCER as ALIGN_PRODUCER)
            aligned=[x for x in registry.get("geracoes",[])
                     if x.get("asset")==ALIGN_ASSET and
                     f"/{ALIGN_PRODUCER}/" in str(x.get("arquivo",""))]
            if len(aligned)!=1:
                raise RuntimeError("EP01_V2_COMPARE_ALIGNED_P04_NOT_ARCHIVED")
            row=aligned[0]
            rel=Path(row["arquivo"])
            if (rel.is_absolute() or ".." in rel.parts or
                not rel.is_relative_to(REL/"assets"/"geracoes"/ALIGN_PRODUCER)):
                raise RuntimeError("EP01_V2_COMPARE_ALIGNED_PATH_INVALID")
            f=ROOT/rel;metadata=f.with_suffix(".production.json")
            if f.is_symlink() or metadata.is_symlink() or not f.is_file() or not metadata.is_file():
                raise RuntimeError("EP01_V2_COMPARE_ALIGNED_FILE_MISSING")
            raw=f.read_bytes()
            report=json.loads(metadata.read_text(encoding="utf-8"))
            if (hashlib.sha256(raw).hexdigest()!=row["sha256"] or
                report.get("sha256")!=row["sha256"] or
                report.get("source_image_sha256")!=raw_version_sha or
                report.get("source_mother_sha256")!=old["sha256"] or
                report.get("source_pixels_unchanged") is not True or
                report.get("technical_postprocess")!="pad_bottom_one_row_no_crop_no_resize" or
                report.get("human_visual_approval") is not False):
                raise RuntimeError("EP01_V2_COMPARE_ALIGNED_PROVENANCE_MISMATCH")
        with Image.open(io.BytesIO(oldraw)) as im: orig=im.convert("RGB")
        with Image.open(io.BytesIO(raw)) as im: fixed=im.convert("RGB")
        if orig.size!=(941,1672) or fixed.size!=orig.size:
            raise RuntimeError("EP01_V2_COMPARE_CANVAS_DIFFERENT")
        diff=ImageChops.difference(orig,fixed)
        rgbmean=round(sum(ImageStat.Stat(diff).mean)/3,4)
        proof_rows.append({"shot":shot,"v1_sha256":old["sha256"],
                           "v2_provider_raw_sha256":raw_version_sha,
                           "v2_provider_raw_path":raw_version_rel,
                           "v2_preview_sha256":row["sha256"],
                           "v2_preview_path":str(rel),
                           "v2_aligned_one_bottom_row":shot=="C01-P04",
                           "source_v1_png":str(p.relative_to(ROOT)),
                           "global_mean_rgb_difference":rgbmean,
                           "human_visual_approval":False})
        view.extend([
            (f"{shot} — V1 REPROVADA",orig),
            (f"{shot} — V2 CANDIDATA",fixed)
        ])
    w,h=1360,2500
    board=Image.new("RGB",(w,h),"#ececec")
    pen=ImageDraw.Draw(board)
    for i,(label,img) in enumerate(view):
        x=(i%2)*680+10;y=(i//2)*1220+18
        pen.text((x+10,y),label,fill="#202020")
        thumb=ImageOps.contain(img,(650,1160),Image.Resampling.LANCZOS)
        board.paste(thumb,(x+(650-thumb.width)//2,y+26))
    pen.text((12,h-30),"QA VISUAL: postura, elenco, pegada das lanças, roupa, perspectiva. SEM APROVAÇÃO.",
             fill="#9c2626")
    ep=ROOT/REL;output=ep/"QA-MAES-C01-P03-P04-V2.jpg"
    board.save(output,"JPEG",quality=86,optimize=True)
    report={
        "schema":"videoforge/ep01-mother-repair-v2-visual-compare/v1",
        "sources":proof_rows,
        "contact_sheet":"QA-MAES-C01-P03-P04-V2.jpg",
        "contact_sheet_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "visual_approval":False,"rig_ready":False,"mp4_generated":False,
        "youtube_uploaded":False,"provider_calls":0}
    (ep/"QA-MAES-C01-P03-P04-V2.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_V2_CORRECTED_MOTHERS_PREVIEW",json.dumps({
        "shots":[r["shot"] for r in proof_rows],"human_approval":False,"paid_calls":0
    }))

if __name__=="__main__":
    main()
