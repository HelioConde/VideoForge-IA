"""Edição REAL de olhos via Codex Proxy, sempre usando a imagem original.

1. Recebe artifact original verificado de otaku-br (cena-base.png).
2. Recorta a face original, amplia em 1024^2 e envia imagem + mascara na
   rota /v1/images/edits. Uma unica chamada explicitamente autorizada.
3. Desamplia e usa somente os pixels gerados na mascara dos olhos, misturando
   no head-open original. Fora da mascara o sprite e bit-exato ao original.
4. head-closed-ai.png e artifact de RASCUNHO; sem aprovar/publicar sozinho.
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

from . import proxy_images as proxy
from . import rig_candidate as candidate
from . import scene_layers
from .errors import VideoForgeError

CROP = (256, 200, 320)  # pixels: x, y, dimensao quadrada na cena original
UPSCALED_SIZE = 1024
SCHEMA = "videoforge/eye-ai-edit/v1"
EDITED_NAME = "face-closed-ai.png"
FINAL_NAME = "head-closed-ai.png"


class EyeAIError(VideoForgeError):
    pass


def read_json(path: Path) -> dict:
    data=candidate._load_json(path)
    return data


def _verify_source(source_dir: Path, plan_path: Path) -> tuple[dict,dict]:
    plan=read_json(plan_path)
    manifest=read_json(source_dir/"manifest.json")
    if manifest.get("schema")!=scene_layers.SCHEMA:
        raise EyeAIError("EYE_SOURCE_MANIFEST_INVALID")
    if plan.get("schema")!=candidate.PLAN_SCHEMA:
        raise EyeAIError("EYE_PLAN_SCHEMA_INVALID")
    for key in ("channel","video_id","scene"):
        if manifest.get(key)!=plan.get(key):
            raise EyeAIError("EYE_SOURCE_IDENTITY_MISMATCH")
    source=manifest.get("source",{})
    if plan.get("source_sha256")!=source.get("sha256"):
        raise EyeAIError("EYE_SOURCE_HASH_MISMATCH")
    if plan.get("canvas")!={"width":1024,"height":1536}:
        raise EyeAIError("EYE_SOURCE_CANVAS_INVALID")
    blob=scene_layers._read_png(source_dir/"cena-base.png")
    if hashlib.sha256(blob).hexdigest()!=source["sha256"]:
        raise EyeAIError("EYE_SOURCE_BYTES_CHANGED")
    info=scene_layers.png_info(blob)
    if (info["width"],info["height"])!=(1024,1536):
        raise EyeAIError("EYE_SOURCE_SIZE_INVALID")
    if not isinstance(plan.get("eye_polygons"),list) or len(plan["eye_polygons"])!=2:
        raise EyeAIError("EYE_PLAN_EYES_INVALID")
    return plan,manifest


def _ffmpeg_png(src: Path, dst: Path, filtergraph: str) -> None:
    cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
         "-i",str(src),"-vf",filtergraph,"-frames:v","1","-pix_fmt","rgba",
         "-f","image2",str(dst)]
    try:
        p=subprocess.run(cmd,capture_output=True,timeout=50,check=True)
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
        raise EyeAIError("EYE_IMAGE_RESAMPLE_FAILED") from None
    if not dst.is_file():
        raise EyeAIError("EYE_IMAGE_RESAMPLE_MISSING")


def _eye_regions(plan:dict) -> list[tuple[float,float,float,float]]:
    out=[]
    for points in plan["eye_polygons"]:
        if len(points)<3:
            raise EyeAIError("EYE_POLYGON_INVALID")
        xy=[candidate._point(p,1024,1536) for p in points]
        x0,x1=min(x for x,_ in xy),max(x for x,_ in xy)
        y0,y1=min(y for _,y in xy),max(y for _,y in xy)
        if not (CROP[0]<x0<x1<CROP[0]+CROP[2]
                and CROP[1]<y0<y1<CROP[1]+CROP[2]):
            raise EyeAIError("EYE_MASK_OUTSIDE_FACE")
        # Uma margem pequena inclui cílios e pálpebra, mas não franja/nariz.
        out.append(((x0+x1)/2,(y0+y1)/2,(x1-x0)/2+8,(y1-y0)/2+7))
    return out


def _weight(x:float,y:float,areas:list[tuple[float,float,float,float]]) -> float:
    """Feather radial: peso 1 no centro, cai suavemente ate zero na borda."""
    best=0.
    for cx,cy,rx,ry in areas:
        q=math.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2)
        if q<=.65:
            return 1.
        if q<1:
            t=(1-q)/.35
            t=t*t*(3-2*t)
            best=max(best,t)
    return best


def prepare(source_dir:Path,plan_path:Path,workdir:Path) -> dict:
    if workdir.exists() or workdir.is_symlink():
        raise EyeAIError("EYE_WORKDIR_ALREADY_EXISTS")
    plan,manifest=_verify_source(source_dir,plan_path)
    workdir.mkdir(parents=True)
    x,y,w=CROP
    _ffmpeg_png(source_dir/"cena-base.png",workdir/"reference-face.png",
                f"crop={w}:{w}:{x}:{y},scale=1024:1024:flags=lanczos")
    # Mascara alfa 0 em volta dos olhos, alfa 255 no resto. Segue /images/edits.
    areas=_eye_regions(plan)
    mask=bytearray(UPSCALED_SIZE*UPSCALED_SIZE*4)
    for py in range(UPSCALED_SIZE):
        sy=y+(py+.5)*w/UPSCALED_SIZE
        for px in range(UPSCALED_SIZE):
            sx=x+(px+.5)*w/UPSCALED_SIZE
            a=0 if _weight(sx,sy,areas)>.01 else 255
            off=4*(py*UPSCALED_SIZE+px)
            mask[off:off+4]=bytes((255,255,255,a))
    candidate._write_png(workdir/"edit-mask.png",mask,UPSCALED_SIZE,UPSCALED_SIZE)
    ref=scene_layers.png_info(scene_layers._read_png(workdir/"reference-face.png"))
    ms=scene_layers.png_info(scene_layers._read_png(workdir/"edit-mask.png"),require_alpha=True)
    if (ref["width"],ref["height"],ms["width"],ms["height"])!=(1024,1024,1024,1024):
        raise EyeAIError("EYE_REFERENCE_MASK_DIMENSIONS")
    report={
      "schema":SCHEMA,
      "channel":plan["channel"],"video_id":plan["video_id"],"scene":plan["scene"],
      "source_sha256":manifest["source"]["sha256"],
      "plan_sha256":hashlib.sha256(plan_path.read_bytes()).hexdigest(),
      "reference_sha256":hashlib.sha256((workdir/"reference-face.png").read_bytes()).hexdigest(),
      "mask_sha256":hashlib.sha256((workdir/"edit-mask.png").read_bytes()).hexdigest(),
      "source_crop":{"x":x,"y":y,"width":w,"height":w},
      "status":"prepared_not_generated","model_calls":0,"human_visual_approval":False,
      "publishable":False
    }
    (workdir/"eye-ai.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report


EDIT_PROMPT=(
  "EDIT THE UPLOADED ORIGINAL ANIME FACE, DO NOT REDESIGN IT. The mask marks "
  "ONLY TWO EYE REGIONS. Close both visible eyes naturally, the farther eye "
  "is partially hidden under the brown fringe. Replace the existing iris and "
  "eyeball with beautifully hand-painted closed upper eyelids, fine delicate "
  "eyelashes, skin shading matching the ORIGINAL skin, warm sunset lighting and "
  "the same exact eye placement and camera profile. Keep brown hair, eyebrow, "
  "nose, mouth, ears, facial structure, skin tone, line work, hairstyle, "
  "expression, perspective, golden highlights, and background unchanged. "
  "The rest of the image should remain pixel-identical. No new eyes, no "
  "darker thick blocks, no simple artificial straight strokes, no skin "
  "rectangles, no redesigned character, no crop or zoom. One image only."
)


def edit(url:str,api_key:str,workdir:Path,model:str) -> dict:
    meta=read_json(workdir/"eye-ai.json")
    if meta.get("schema")!=SCHEMA or meta.get("status")!="prepared_not_generated":
        raise EyeAIError("EYE_EDIT_PREPARATION_INVALID")
    if model not in ("gpt-image-2","gpt-image-1.5"):
        raise EyeAIError("EYE_EDIT_MODEL_INVALID")
    for name,key in (("reference-face.png","reference_sha256"),("edit-mask.png","mask_sha256")):
        if hashlib.sha256(scene_layers._read_png(workdir/name)).hexdigest()!=meta[key]:
            raise EyeAIError("EYE_EDIT_REFERENCE_CHANGED")
    if (workdir/EDITED_NAME).exists():
        raise EyeAIError("EYE_EDIT_ALREADY_GENERATED")
    # API de edicao usada pelas camadas do VideoForge, agora com mascara explicita.
    # Nao converte em geracao sem imagem de referencia se o proxy nao suportar.
    payload={
      "model":model,"prompt":EDIT_PROMPT,"n":1,"size":"1024x1024",
      "output_format":"png","response_format":"b64_json","stream":False,
      "images":[{"image_url":"data:image/png;base64,"+
                 base64.b64encode((workdir/"reference-face.png").read_bytes()).decode("ascii")}],
      "mask":{"image_url":"data:image/png;base64,"+
              base64.b64encode((workdir/"edit-mask.png").read_bytes()).decode("ascii")}
    }
    if model=="gpt-image-1.5":
        payload["input_fidelity"]="high"
    result=proxy.call_proxy(url,"/v1/images/edits",api_key,payload)
    blob,extension=proxy.decode_image(result)
    if extension!=".png":
        raise EyeAIError("EYE_EDIT_OUTPUT_NOT_PNG")
    info=scene_layers.png_info(blob)
    w,h=info["width"],info["height"]
    # O proxy pode produzir canvas horizontal/vertical apesar de pedido quadrado.
    # Salvar o ORIGINAL da resposta em vez de desperdiçar a chamada de IA.
    if not (min(w,h)>=512 and max(w,h)<=1536 and max(w,h)/min(w,h)<=1.5):
        raise EyeAIError("EYE_EDIT_OUTPUT_UNUSABLE_RESOLUTION")
    (workdir/EDITED_NAME).write_bytes(blob)
    meta["status"]="generated_pending_review"
    meta["model"]=model
    meta["model_calls"]=1
    meta["actual_size"]={"width":w,"height":h}
    meta["expected_size"]={"width":1024,"height":1024}
    meta["face_closed_sha256"]=hashlib.sha256(blob).hexdigest()
    (workdir/"eye-ai.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    return meta


def apply(source_dir:Path,plan_path:Path,workdir:Path,
          candidate_dir:Path) -> dict:
    plan,manifest=_verify_source(source_dir,plan_path)
    meta=read_json(workdir/"eye-ai.json")
    if meta.get("status")!="generated_pending_review" or meta.get("model_calls")!=1:
        raise EyeAIError("EYE_EDIT_NOT_GENERATED")
    if meta["source_sha256"]!=manifest["source"]["sha256"]:
        raise EyeAIError("EYE_EDIT_SOURCE_CHANGED")
    if meta["plan_sha256"]!=hashlib.sha256(plan_path.read_bytes()).hexdigest():
        raise EyeAIError("EYE_EDIT_PLAN_CHANGED")
    result=scene_layers._read_png(workdir/EDITED_NAME)
    if hashlib.sha256(result).hexdigest()!=meta["face_closed_sha256"]:
        raise EyeAIError("EYE_EDIT_OUTPUT_HASH_MISMATCH")
    result_info=scene_layers.png_info(result)
    iw,ih=result_info["width"],result_info["height"]
    expected=meta.get("actual_size",{"width":1024,"height":1024})
    if (iw,ih)!=(expected.get("width"),expected.get("height")):
        raise EyeAIError("EYE_EDIT_OUTPUT_WRONG_SIZE")
    rigname=candidate_dir/"rig.json"
    rig=read_json(rigname)
    if (rig.get("channel"),rig.get("video_id"),rig.get("scene"))!=(
        plan["channel"],plan["video_id"],plan["scene"]):
        raise EyeAIError("EYE_EDIT_CROSS_CHANNEL")
    if rig.get("source_sha256")!=meta["source_sha256"] or not rig.get("candidate_only"):
        raise EyeAIError("EYE_EDIT_CANDIDATE_SOURCE_INVALID")
    assets=rig.get("assets",{})
    head_path=candidate_dir/"head-open.png"
    if hashlib.sha256(scene_layers._read_png(head_path)).hexdigest()!=assets.get("head-open.png"):
        raise EyeAIError("EYE_EDIT_HEAD_OPEN_HASH_INVALID")
    target=candidate_dir/FINAL_NAME
    if target.exists():
        raise EyeAIError("EYE_EDIT_CLOSED_HEAD_ALREADY_EXISTS")
    x0,y0,w=CROP
    original=candidate._image(head_path,1024,1536)
    reference=candidate._image(source_dir/"cena-base.png",1024,1536)
    regions=_eye_regions(plan)
    # Testar varios enquadramentos SEM redesenhar o rosto.
    # Escolher o que melhor preserva cabelo/bochecha fora dos olhos.
    filters=[f"scale={w}:{w}:flags=lanczos"]
    square=min(iw,ih)
    if iw!=ih:
        movement=max(iw,ih)-square
        for frac in (0.,.25,.5,.75,1.):
            offset=round(movement*frac)
            ox,oy=(offset,0) if iw>ih else (0,offset)
            filters.append(f"crop={square}:{square}:{ox}:{oy},scale={w}:{w}:flags=lanczos")
    options=[]
    for k,filtergraph in enumerate(filters):
        scaled=workdir/f"face-closed-aligned-{k}.png"
        _ffmpeg_png(workdir/EDITED_NAME,scaled,filtergraph)
        pixels=candidate._image(scaled,w,w)
        errors,count=0,0
        for py in range(30,w-20,8):
            for px in range(25,w-25,8):
                x,y=x0+px,y0+py
                if _weight(x+.5,y+.5,regions)>.1:
                    continue
                a=4*(y*1024+x)
                b=4*(py*w+px)
                errors+=sum(abs(reference[a+c]-pixels[b+c]) for c in range(3))
                count+=3
        options.append((errors/max(count,1),k,pixels))
    best_score,best_variant,generated=min(options,key=lambda item:(item[0],item[1]))
    if best_score>120:
        raise EyeAIError("EYE_EDIT_REFERENCE_ALIGNMENT_FAILED")
    closed=bytearray(original)
    change_sum=0
    mixed_count=0
    for y in range(y0,y0+w):
        for x in range(x0,x0+w):
            alpha=_weight(x+.5,y+.5,regions)
            if alpha<=0:continue
            off=4*(y*1024+x)
            if original[off+3]<245:
                continue # absolutamente nenhuma mudanca no cabelo/fundo transparente
            gi=4*((y-y0)*w+x-x0)
            change_sum+=sum(abs(original[off+c]-generated[gi+c]) for c in range(3))
            for c in range(3):
                closed[off+c]=round(original[off+c]*(1-alpha)+generated[gi+c]*alpha)
            mixed_count+=1
    if mixed_count<120 or change_sum/mixed_count<6:
        raise EyeAIError("EYE_EDIT_IMAGE_DID_NOT_CHANGE_EYES")
    # Garante que fora das regioes de olhos os bytes sao identicos, inclusive alfa.
    candidate._write_png(target,closed,1024,1536)
    checksum=hashlib.sha256(target.read_bytes()).hexdigest()
    assets[FINAL_NAME]=checksum
    rig["assets"]=assets
    rig["candidate_only"]=True
    rig["human_review"]={"no_duplicate_parts":False,"pixel_alignment":False,"occlusion_order":False}
    rigname.write_text(json.dumps(rig,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report_path=candidate_dir/"candidate.qa.json"
    qa=read_json(report_path)
    qa["eye_close_technique"]="image_edit_original_reference_masked"
    qa["model_calls_for_eye"]=1
    qa["generated_eye_sha256"]=checksum
    qa["human_visual_approval"]=False
    qa["rig_ready_for_remotion"]=False
    qa["publishable"]=False
    qa["eye_ai_modified_pixels"]=mixed_count
    qa["eye_ai_rgb_diff_average"]=round(change_sum/mixed_count,2)
    qa["eye_ai_reference_alignment_score"]=round(best_score,2)
    qa["eye_ai_alignment_variant"]=best_variant
    qa["eye_ai_output_dimensions"]=meta.get("actual_size",{"width":1024,"height":1024})
    report_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    prov_path=candidate_dir/"asset-provenance.json"
    prov=read_json(prov_path)
    prov["model_calls"]=1
    prov["eye_ai_edit"]={
       "schema":SCHEMA,"model":meta["model"],
       "source_sha256":meta["source_sha256"],
       "face_reference_sha256":meta["reference_sha256"],
       "mask_sha256":meta["mask_sha256"],
       "model_output_sha256":meta["face_closed_sha256"],
       "closed_head_sha256":checksum,
       "original_outside_mask_unchanged":True,
       "human_review":False,"model_calls":1
    }
    prov_path.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return qa


def main() -> int:
    p=argparse.ArgumentParser(description="Editar olhos com IA usando somente cena ORIGINAL")
    p.add_argument("action",choices=("prepare","edit","apply"))
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--plan",type=Path)
    p.add_argument("--workdir",type=Path,required=True)
    p.add_argument("--candidate-dir",type=Path)
    p.add_argument("--url")
    p.add_argument("--model",default="gpt-image-1.5")
    args=p.parse_args()
    try:
        if args.action=="prepare":
            if args.source_dir is None or args.plan is None:raise EyeAIError("EYE_SOURCE_REQUIRED")
            result=prepare(args.source_dir,args.plan,args.workdir)
        elif args.action=="edit":
            if not args.url:raise EyeAIError("EYE_PROXY_URL_REQUIRED")
            result=edit(args.url,os.getenv("CODEX_PROXY_API_KEY",""),args.workdir,args.model)
        else:
            if not all((args.source_dir,args.plan,args.candidate_dir)):
                raise EyeAIError("EYE_APPLY_INPUTS_REQUIRED")
            result=apply(args.source_dir,args.plan,args.workdir,args.candidate_dir)
        print(json.dumps(result,ensure_ascii=False))
    except (VideoForgeError,EyeAIError,scene_layers.LayerError,
            candidate.CandidateError,proxy.ProxyImageError) as e:
        print("EYE_AI_EDIT_BLOCKED:",e,file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
