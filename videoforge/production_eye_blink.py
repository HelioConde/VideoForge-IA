"""Gerar camada RGBA de piscada usando a cena-mae original do VideoForge.

Nao deforma o rosto, nao cria olhos ficticios em Remotion e nao altera
a base. Um overlay de palpebras so pode ser habilitado depois de QA de ROI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from . import scene_layers
from .production_scene_layers import read_plan
from .errors import VideoForgeError


def alpha_bounds(image:Path,roi:list[int])->dict:
    """Fora da ROI, nem 1% dos pixels alfa visiveis e permitido."""
    width,height=1024,1536
    if not isinstance(roi,list) or len(roi)!=4 or not all(type(v) is int for v in roi):
        raise VideoForgeError("EYE_ROI_INVALID")
    x0,y0,x1,y1=roi
    if not (0<=x0<x1<=width and 0<=y0<y1<=height):
        raise VideoForgeError("EYE_ROI_INVALID")
    try:
        p=subprocess.run([
            "ffmpeg","-nostdin","-hide_banner","-loglevel","error",
            "-i",str(image),"-vf","alphaextract","-frames:v","1",
            "-f","rawvideo","-pix_fmt","gray","-",
        ],capture_output=True,timeout=45,check=False)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("EYE_ALPHA_DECODE_UNAVAILABLE") from exc
    if p.returncode or len(p.stdout)!=width*height:
        raise VideoForgeError("EYE_ALPHA_DECODE_INVALID")
    alpha=memoryview(p.stdout)
    count=outside=0
    for y in range(height):
        row=alpha[y*width:(y+1)*width]
        for x,px in enumerate(row):
            if px>=40:
                count+=1
                if not (x0<=x<x1 and y0<=y<y1):
                    outside+=1
    if count<120 or outside>max(50,int(count*.015)):
        raise VideoForgeError(f"EYE_OVERLAY_OUTSIDE_FACE_OR_INVISIBLE_{outside}_{count}")
    return {"alpha_visible_pixels":count,"outside_eye_region_pixels":outside,
            "region_of_interest":roi}


def generate(channel:str,video_id:str,number:int,incoming:Path,url:str,model:str)->dict:
    _plan,_story,entry=read_plan(channel,video_id,number)
    spec=entry.get("eyes_closed")
    if not isinstance(spec,dict):
        raise VideoForgeError("EYE_OVERLAY_SPEC_NOT_DEFINED")
    guidance=spec.get("guidance")
    if not isinstance(guidance,str) or not 50<len(guidance)<2500:
        raise VideoForgeError("EYE_OVERLAY_INSTRUCTION_INVALID")
    folder=scene_layers.resume(channel,video_id,f"cena-{number:02d}",incoming)
    manifest=scene_layers._read_manifest(folder/"manifest.json")
    instruction=(
        "EDITE EXATAMENTE A MESMA CENA-MAE: "+guidance+
        " Produza um sprite RGBA com somente as duas pequenas areas de "
        "palpebras FECHADAS de Anya e pele ao redor que ocluem os olhos ABERTOS. "
        "NAO refaca ou reduza a opacidade do rosto. NAO desenhe o rosto todo. "
        "Nao inclua as demais pessoas, roupas, fundo ou texto. "
        "Fora dos olhos deve existir alfa=0 REAL. "
        "Coordenadas originais de video e iluminacao identicas."
    )
    output=scene_layers.generate_layer(folder,"eyes-closed",url,
        os.getenv("CODEX_PROXY_API_KEY",""),model,instruction=instruction)
    metric=alpha_bounds(output,spec["roi_original_canvas"])
    metadata={
        "schema":"videoforge/eye-overlay-qa/v1",
        "channel":channel,"video_id":video_id,"number":number,
        "scene":entry["scene"],
        "scene_mother_sha256":manifest["source"]["sha256"],
        "eyes_rgba_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        **metric,
        "blink_centers_frames":spec.get("blink_centers_frames",[]),
        "tech_roi_qa":"passed","visual_review":"pending",
        "face_base_opacity":1,"independent_body_head_rig":False,
        "official_video_created":False,"youtube_uploaded":False,
    }
    (folder/"eye-overlay.qa.json").write_text(
        json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EYE_OVERLAY_QA_OK",json.dumps(metadata,ensure_ascii=False))
    return metadata


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--channel",required=True)
    p.add_argument("--video-id",required=True)
    p.add_argument("--number",type=int,required=True)
    p.add_argument("--incoming",type=Path,required=True)
    p.add_argument("--url",required=True)
    p.add_argument("--model",default="gpt-image-2")
    a=p.parse_args()
    try:
        generate(a.channel,a.video_id,a.number,a.incoming,a.url,a.model)
        return 0
    except (VideoForgeError,scene_layers.LayerError,ValueError,OSError,KeyError) as exc:
        print("EYE_OVERLAY_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
