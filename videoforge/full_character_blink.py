"""Edit the SAME full character image: ONLY close the eyes; never redraw a sprite.

The edit is produced by the VideoForge Codex Proxy. A separate, deterministic
compose command restores EVERY original pixel and original alpha outside the
eye-only mask. Remotion swaps full character frames, never overlays eyelids.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

from . import proxy_images as proxy, scene_layers
from .production_scene_layers import read_plan
from .errors import VideoForgeError

WIDTH, HEIGHT = 1024, 1536
SCHEMA = "videoforge/full-character-closed-eyes/v1"


def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_info(source:Path,manifest:Path,channel:str,video_id:str,number:int)->tuple[dict,dict]:
    _plan,_story,entry=read_plan(channel,video_id,number)
    if not source.is_file() or source.is_symlink() or not manifest.is_file() or manifest.is_symlink():
        raise VideoForgeError("BLINK_FULL_ORIGINAL_MISSING")
    m=scene_layers._read_manifest(manifest)
    if ((m.get("channel"),m.get("video_id"),m.get("scene"))
            !=(channel,video_id,f"cena-{number:02d}")):
        raise VideoForgeError("BLINK_FULL_WRONG_SCENE")
    record=m.get("layers",{}).get("character-main",{})
    if record.get("technical_status")!="verified" or record.get("sha256")!=digest(source):
        raise VideoForgeError("BLINK_FULL_SOURCE_HASH_MISMATCH")
    scene_sha=m.get("source",{}).get("sha256","")
    if not isinstance(scene_sha,str) or len(scene_sha)!=64:
        raise VideoForgeError("BLINK_FULL_SCENE_MOTHER_SHA_MISSING")
    info=scene_layers.png_info(source.read_bytes(),require_alpha=True)
    if (info["width"],info["height"])!=(WIDTH,HEIGHT):
        raise VideoForgeError("BLINK_FULL_IMAGE_DIMENSIONS_INVALID")
    spec=entry.get("eyes_closed",{})
    if not isinstance(spec,dict) or not isinstance(spec.get("roi_original_canvas"),list):
        raise VideoForgeError("BLINK_FULL_EYE_PLAN_MISSING")
    return entry,m


def prompt_for_character(entry:dict)->str:
    """Identical full-character frame, with only the target eyes shut."""
    return (
        "EDICAO DE IMAGEM, NAO GERACAO DE UM NOVO DESENHO. "
        "USE EXATAMENTE A IMAGEM RGBA DO PERSONAGEM QUE FOI ANEXADA como "
        "imagem-base e referencia unica; nao copie outra ilustracao. "
        "UNICA MUDANCA PERMITIDA: feche suavemente OS DOIS OLHOS da Anya GRANDE "
        "em primeiro plano, no terco inferior, como uma piscada natural. "
        "Substitua somente iris/pupilas e abertura ocular por palpebras FECHADAS "
        "que pertençam exatamente ao mesmo rosto. "
        "NADA MAIS PODE MUDAR: cabelo, franja inclusive fios sobre os olhos, "
        "rosto, pele, sobrancelhas, boca, expressão fora dos olhos, roupa, "
        "acessorios, posição, tamanho, pose, proporções, enquadramento, "
        "outros personagens e seus olhos, fundo/transparencia, sombras, "
        "traços e cores devem permanecer IDENTICOS à entrada. "
        "NAO redesenhe a Anya nem altere qualquer detalhe além dos olhos. "
        "Nao adicione camada avulsa de palpebras: devolva a IMAGEM INTEIRA "
        "do mesmo personagem com os dois olhos fechados, na MESMA POSICAO "
        "do canvas 1024x1536, PNG com transparencia RGBA real conservada. "
        "Sem novos personagens, objetos, textos, bordas ou mudança de camera."
    )


def generate(source:Path,manifest:Path,channel:str,video_id:str,number:int,
             url:str,model:str,output:Path)->dict:
    entry,m=source_info(source,manifest,channel,video_id,number)
    if model not in proxy.IMAGE_MODELS:
        raise VideoForgeError("BLINK_FULL_MODEL_NOT_ALLOWED")
    if output.exists() or output.is_symlink():
        raise VideoForgeError("BLINK_FULL_OUTPUT_ALREADY_EXISTS")
    prompt=prompt_for_character(entry)
    blob=source.read_bytes()
    # Exactly ONE image edit request. NEVER retry 429 or substitute a new pose.
    response=proxy.call_proxy(url,"/v1/images/edits",
        os.getenv("CODEX_PROXY_API_KEY",""),{
        "model":model,"prompt":prompt,"n":1,"size":f"{WIDTH}x{HEIGHT}",
        "background":"transparent","output_format":"png",
        "response_format":"b64_json","stream":False,"input_fidelity":"high",
        "images":[{"image_url":"data:image/png;base64,"+base64.b64encode(blob).decode("ascii")}],
    })
    edited,ext=proxy.decode_image(response)
    if ext!=".png":
        raise VideoForgeError("BLINK_FULL_EDIT_MUST_BE_PNG")
    info=scene_layers.png_info(edited,require_alpha=True)
    if (info["width"],info["height"])!=(WIDTH,HEIGHT):
        raise VideoForgeError("BLINK_FULL_EDIT_CHANGED_CANVAS")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(edited)
    qa={
        "schema":SCHEMA,"channel":channel,"video_id":video_id,
        "number":number,"scene":entry["scene"],"model":model,
        "method":"edit_same_full_original_character_image_only_close_eyes",
        "original_character_sha256":digest(source),
        "source_scene_mother_sha256":m["source"]["sha256"],
        "ai_full_closed_sha256":hashlib.sha256(edited).hexdigest(),
        "original_reference_used":True,"image_edit_calls":1,
        "closed_eyes_after_pixel_qa":False,
        "visual_approval":False,"official_video_created":False,
        "youtube_uploaded":False,
    }
    output.with_suffix(".production.json").write_text(
        json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BLINK_SAME_CHARACTER_EDIT_OK",json.dumps(qa,ensure_ascii=False))
    return qa


def _raw_rgba(path:Path)->bytearray:
    info=scene_layers.png_info(path.read_bytes(),require_alpha=True)
    if (info["width"],info["height"])!=(WIDTH,HEIGHT):
        raise VideoForgeError("BLINK_FULL_RGBA_SIZE_INVALID")
    try:
        p=subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
                          "-i",str(path),"-frames:v","1","-pix_fmt","rgba",
                          "-f","rawvideo","-"],capture_output=True,
                         timeout=70,check=False)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise VideoForgeError("BLINK_FULL_FFMPEG_UNAVAILABLE") from exc
    if p.returncode or len(p.stdout)!=WIDTH*HEIGHT*4:
        raise VideoForgeError("BLINK_FULL_RGBA_DECODE_FAILED")
    return bytearray(p.stdout)


def _save_rgba(path:Path,buf:bytearray)->None:
    if path.exists() or path.is_symlink():
        raise VideoForgeError("BLINK_FULL_OUTPUT_ALREADY_EXISTS")
    p=subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
                      "-f","rawvideo","-pixel_format","rgba",
                      "-video_size",f"{WIDTH}x{HEIGHT}","-framerate","1",
                      "-i","-","-frames:v","1","-compression_level","6",str(path)],
                     input=bytes(buf),capture_output=True,timeout=70,check=False)
    if p.returncode:
        raise VideoForgeError("BLINK_FULL_RGBA_ENCODE_FAILED")
    scene_layers.png_info(path.read_bytes(),require_alpha=True)


def eye_weight(x:int,y:int,ellipses:list)->float:
    """Eye-only matte. Outside both eyes, alpha is EXACTLY zero."""
    w=0.0
    for e in ellipses:
        if len(e)!=4:raise VideoForgeError("BLINK_FULL_ELLIPSE_INVALID")
        cx,cy,rx,ry=e
        if rx<=0 or ry<=0:raise VideoForgeError("BLINK_FULL_ELLIPSE_INVALID")
        dist=math.hypot((x-cx)/rx,(y-cy)/ry)
        t=max(0.0,min(1.0,(1.0-dist)/.12))
        w=max(w,t*t*(3-2*t))
    return w


def compose_same_character(original:Path,edited:Path,production_report:Path,
                           output:Path,qa_path:Path,
                           eyes:list)->dict:
    """Never composite a visible sticker on the character's hair.

    The closed variant is a complete same-size image with ALL non-eye bytes
    retained from the original, and original alpha retained everywhere.
    """
    if output.exists() or qa_path.exists() or output.is_symlink() or qa_path.is_symlink():
        raise VideoForgeError("BLINK_FULL_NO_OVERWRITE")
    try:
        meta=json.loads(production_report.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise VideoForgeError("BLINK_FULL_PRODUCTION_REPORT_MISSING") from exc
    if (meta.get("schema")!=SCHEMA or
        meta.get("original_character_sha256")!=digest(original) or
        meta.get("ai_full_closed_sha256")!=digest(edited) or
        meta.get("method")!="edit_same_full_original_character_image_only_close_eyes"):
        raise VideoForgeError("BLINK_FULL_ORIGIN_INVALID")
    if not (isinstance(eyes,list) and len(eyes)==2 and
            all(isinstance(e,list) and len(e)==4 and all(isinstance(n,(int,float)) for n in e) for e in eyes)):
        raise VideoForgeError("BLINK_FULL_EYE_REGIONS_REQUIRED")
    base=_raw_rgba(original)
    ai=_raw_rgba(edited)
    safe=bytearray(base)  # exactly preserves every non-eye pixel, including ALPHA
    modified=0;hair_protected=0;diff_sum=0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            w=eye_weight(x,y,eyes)
            if w<=0:continue
            k=(y*WIDTH+x)*4
            r,g,b,a=base[k:k+4]
            # Protect original pink hair in the eye region, not a guessed new fringe.
            hair=(a>=200 and r>=175 and g>=85 and b>=65 and
                  (r-g)>=65 and (r-b)>=65)
            if hair:
                hair_protected+=1
                continue
            if a<160 or ai[k+3]<150:continue
            for ch in range(3):
                safe[k+ch]=max(0,min(255,round(base[k+ch]*(1-w)+ai[k+ch]*w)))
            if max(abs(safe[k+j]-base[k+j]) for j in range(3))>=10:
                modified+=1
                diff_sum+=sum(abs(safe[k+j]-base[k+j]) for j in range(3))
    if modified<900 or modified>30000 or diff_sum<50000:
        raise VideoForgeError(f"BLINK_FULL_EYE_CHANGE_NOT_CREDIBLE_{modified}_{diff_sum}")
    _save_rgba(output,safe)
    # Prove alpha is byte-identical and all non-eye pixels preserved.
    outside_differences=alpha_differences=0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            k=(y*WIDTH+x)*4
            if safe[k+3]!=base[k+3]:alpha_differences+=1
            if eye_weight(x,y,eyes)<=0 and safe[k:k+4]!=base[k:k+4]:
                outside_differences+=1
    if outside_differences or alpha_differences:
        raise VideoForgeError("BLINK_FULL_NON_EYE_PIXELS_CHANGED")
    result={
        "schema":"videoforge/closed-character-pixel-qa/v1",
        "mode":"swap_full_character_image_during_blink",
        "source_scene_mother_sha256":meta["source_scene_mother_sha256"],
        "original_character_sha256":digest(original),
        "ai_full_closed_sha256":digest(edited),
        "safe_full_closed_sha256":digest(output),
        "eye_pixels_changed":modified,
        "total_rgb_delta_inside_eyes":diff_sum,
        "hair_pixels_protected":hair_protected,
        "non_eye_pixels_changed":outside_differences,
        "alpha_pixels_changed":alpha_differences,
        "only_eyes_modified_technical_qa":"passed",
        "visual_approval":False,"official_video_created":False,"youtube_uploaded":False,
    }
    qa_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BLINK_FULL_CHARACTER_PIXEL_QA_OK",json.dumps(result,ensure_ascii=False))
    return result


def main()->int:
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="command",required=True)
    gen=sub.add_parser("generate")
    for q in (gen,):
        q.add_argument("--channel",required=True);q.add_argument("--video-id",required=True)
        q.add_argument("--number",required=True,type=int)
        q.add_argument("--source",required=True,type=Path)
        q.add_argument("--manifest",required=True,type=Path)
        q.add_argument("--output",required=True,type=Path)
    gen.add_argument("--url",required=True);gen.add_argument("--model",default="gpt-image-2")
    comb=sub.add_parser("compose")
    comb.add_argument("--original",required=True,type=Path)
    comb.add_argument("--ai-edited",required=True,type=Path)
    comb.add_argument("--production-report",required=True,type=Path)
    comb.add_argument("--safe-output",required=True,type=Path)
    comb.add_argument("--qa-output",required=True,type=Path)
    comb.add_argument("--eye-regions",required=True)
    a=p.parse_args()
    try:
        if a.command=="generate":
            generate(a.source,a.manifest,a.channel,a.video_id,a.number,a.url,a.model,a.output)
        else:
            compose_same_character(a.original,a.ai_edited,a.production_report,
                                   a.safe_output,a.qa_output,json.loads(a.eye_regions))
        return 0
    except (VideoForgeError,scene_layers.LayerError,proxy.ProxyImageError,ValueError,OSError,KeyError) as exc:
        print("BLINK_FULL_CHARACTER_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
