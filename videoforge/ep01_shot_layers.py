"""Extração de camadas reais do mesmo PNG de cena-mãe EP01.

Cada execução faz até UMA edição no Codex Proxy, sem geração de poses.
A saída preserva o PNG de origem, um candidato RGBA ou fundo opaco
e QA técnico. Aprovação visual e recomposição permanecem pendentes.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from .errors import VideoForgeError
from . import image_generation_policy, proxy_images
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from .ep01_shot_mother import existing_mother
from .scene_layers import png_info, LayerError

SCHEMA="videoforge/ep01-scene-mother-extracted-parts/v1"
PRODUCER="production-shot-layer-v2"
VALID_PARTS={"background-clean","character-carrasco","object-espada","object-bainha"}


def read_plan(root:Path=ROOT)->dict:
    path=Path(root)/REL/"CAMADAS-C01-P02.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size>25_000:
        raise VideoForgeError("EP01_LAYER_PLAN_MISSING")
    try:
        doc=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError) as e:
        raise VideoForgeError("EP01_LAYER_PLAN_INVALID") from e
    if (doc.get("schema")!=SCHEMA or doc.get("channel")!=CHANNEL or
        doc.get("video_id")!=VIDEO or doc.get("shot_id")!="C01-P02" or
        doc.get("max_chargeable_calls_per_part_run")!=1 or
        doc.get("no_retry_on_429") is not True or
        doc.get("youtube_upload") is not False or
        doc.get("mp4_generated") is not False or
        doc.get("source_policy")!="all_layers_edits_of_exact_same_mother_png_sha_not_independent_poses"):
        raise VideoForgeError("EP01_LAYER_PLAN_SCOPE_INVALID")
    parts=doc.get("parts")
    if (not isinstance(parts,list) or len(parts)!=4 or
        {x.get("id") for x in parts if isinstance(x,dict)}!=VALID_PARTS):
        raise VideoForgeError("EP01_LAYER_PARTS_INVALID")
    for x in parts:
        if (x.get("mode") not in {"opaque","transparent"} or
            (x["id"]=="background-clean")!=(x["mode"]=="opaque") or
            not isinstance(x.get("description"),str) or
            not 200<=len(x["description"])<=2500 or
            x.get("source")!="scene-mother"):
            raise VideoForgeError("EP01_LAYER_DESCRIPTION_INVALID")
    return doc


def mother_source(root:Path=ROOT):
    root=Path(root)
    plan=read_plan(root)
    item=existing_mother("C01-P02",root)
    if item is None or item.get("run_id")!=plan["mother_run_id"]:
        raise VideoForgeError("EP01_LAYER_MOTHER_ORIGIN_NOT_ARCHIVED")
    rel=Path(plan["mother_archive_png"])
    expected=REL/"assets"/"geracoes"/"production-scene-mother-v2"/str(item["run_id"])/"c01-p02-scene-mother.png"
    if rel!=expected or rel.is_absolute() or ".." in rel.parts:
        raise VideoForgeError("EP01_LAYER_MOTHER_PATH_INVALID")
    image=root/rel
    if image.is_symlink() or not image.is_file() or image.stat().st_size>35_000_000:
        raise VideoForgeError("EP01_LAYER_SOURCE_UNSAFE")
    raw=image.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=plan["mother_sha256"] or sha!=item["sha256"]:
        raise VideoForgeError("EP01_LAYER_MOTHER_SHA_TAMPERED")
    info=png_info(raw)
    if (info["width"]!=plan["mother_dimensions"]["width"] or
        info["height"]!=plan["mother_dimensions"]["height"]):
        raise VideoForgeError("EP01_LAYER_MOTHER_DIMENSIONS_CHANGED")
    return plan,raw,info


def archived_layer(part:str,root:Path=ROOT)->dict|None:
    folder=Path(root)/REL/"assets"/"geracoes"/PRODUCER
    if folder.is_symlink():
        raise VideoForgeError("EP01_LAYER_ARCHIVE_SYMLINK")
    if not folder.exists():
        return None
    match=[]
    asset="c01-p02-"+part+".png"
    for run in folder.iterdir():
        if run.is_symlink():
            raise VideoForgeError("EP01_LAYER_ARCHIVE_RUN_SYMLINK")
        if not run.is_dir() or not run.name.isdecimal():
            continue
        img=run/asset
        manifest=run/"manifesto-geracoes.json"
        if img.is_symlink() or manifest.is_symlink():
            raise VideoForgeError("EP01_LAYER_ARCHIVE_FILE_SYMLINK")
        if not img.exists() and not manifest.exists():
            continue
        if not img.is_file() and manifest.is_file():
            obj=json.loads(manifest.read_text(encoding="utf-8"))
            if any(x.get("file")==asset for x in obj.get("images",[]) if isinstance(x,dict)):
                raise VideoForgeError("EP01_LAYER_ARCHIVE_MISSING_PNG_STOP")
            continue
        if not img.is_file() or not manifest.is_file():
            raise VideoForgeError("EP01_LAYER_ARCHIVE_INCOMPLETE_STOP")
        try:
            obj=json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError,ValueError,UnicodeError) as e:
            raise VideoForgeError("EP01_LAYER_ARCHIVE_BAD_JSON") from e
        subset=[x for x in obj.get("images",[]) if isinstance(x,dict) and x.get("file")==asset]
        if (obj.get("schema")!="videoforge/permanent-generated-image-archive/v1" or
            obj.get("producer")!=PRODUCER or obj.get("channel")!=CHANNEL or
            obj.get("video_id")!=VIDEO or obj.get("github_run_id")!=int(run.name) or
            len(subset)!=1):
            raise VideoForgeError("EP01_LAYER_ARCHIVE_PROVENANCE_INVALID")
        b=img.read_bytes()
        sha=hashlib.sha256(b).hexdigest()
        if sha!=subset[0].get("sha256"):
            raise VideoForgeError("EP01_LAYER_ARCHIVE_SHA_CHANGED")
        match.append({"run_id":int(run.name),"sha256":sha})
    return max(match,key=lambda x:x["run_id"]) if match else None


def prepare(part:str,root:Path=ROOT)->dict:
    doc,blob,info=mother_source(root)
    if part not in VALID_PARTS:
        raise VideoForgeError("EP01_LAYER_UNKNOWN_COMPONENT")
    if archived_layer(part,root):
        raise VideoForgeError("EP01_LAYER_ALREADY_ARCHIVED")
    component=next(x for x in doc["parts"] if x["id"]==part)
    transparent=component["mode"]=="transparent"
    text=(
        "EDITE LOCALMENTE A IMAGEM-MÃE ORIGINAL ANEXADA. "
        "Esta tarefa NÃO é geração de cena independente, NÃO é folha de poses "
        "e NÃO pode inventar enquadramento novo. "
        f"EXTRAIR CAMADA {part} da tomada C01-P02: {component['description']} "
        f"A composição original tem {info['width']}x{info['height']} pixels. "
        "Preserve EXATAMENTE a mesma escala, posição, direção da câmera, "
        "anatomia, iluminação e localização relativa no canvas original. "
        "Não reposicionar objeto, não espelhar, não inventar corpo fora do enquadramento. "
        "Se for recorte, tudo fora do objeto deve ter canal ALFA 0 real; "
        "não desenhar quadriculado falso, sombra de fundo ou quadro branco. "
        "A imagem-mãe permanece como referência visual imutável; "
        "a recomposição será conferida depois. Sem texto/logos."
    )
    if len(text)>4400:
        raise VideoForgeError("EP01_LAYER_PROMPT_TOO_LONG")
    return {"part":part,"source_sha256":doc["mother_sha256"],"source":blob,
            "dimensions":(info["width"],info["height"]), "component":component,
            "prompt":text,"transparent":transparent,"mother_path":doc["mother_archive_png"]}


def generate(part:str,url:str,model:str="gpt-image-2",root:Path=ROOT)->dict:
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if model!="gpt-image-2":
        raise VideoForgeError("EP01_LAYER_MODEL_NOT_ALLOWED")
    spec=prepare(part,root)
    stem="c01-p02-"+part
    destination=Path(root)/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    target=destination/(stem+".png")
    meta=destination/(stem+".production.json")
    if target.is_symlink() or meta.is_symlink() or target.exists() or meta.exists():
        raise VideoForgeError("EP01_LAYER_OUTPUT_ALREADY_EXISTS")
    response=proxy_images.call_proxy(
        url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),
        {"model":model,"prompt":spec["prompt"],"n":1,"size":"1024x1536",
         "background":"transparent" if spec["transparent"] else "opaque",
         "output_format":"png","response_format":"b64_json","stream":False,
         "images":[{"image_url":"data:image/png;base64,"+
                    base64.b64encode(spec["source"]).decode("ascii")}]})
    raw,extension=proxy_images.decode_image(response)
    if extension!=".png":
        raise VideoForgeError("EP01_LAYER_OUTPUT_NOT_PNG")
    # O upstream pode devolver 941x1670 a partir do frame-mãe 941x1672.
    # Um delta vertical de <=2 pixels é reparável SEM esticar ou recortar:
    # preservar o PNG bruto como segunda imagem auditada e preencher a borda.
    original_provider_png=None
    edge_alignment=None
    try:
        qa=png_info(raw,require_alpha=spec["transparent"])
        technical=("candidate_rgba_verified" if spec["transparent"]
                   else "candidate_opaque_background_verified")
        if (qa["width"],qa["height"])!=spec["dimensions"]:
            native_w,native_h=spec["dimensions"]
            short= native_h-qa["height"]
            if qa["width"]==native_w and 1<=short<=2:
                import io
                from PIL import Image
                original_provider_png=raw
                with Image.open(io.BytesIO(raw)) as im:
                    mode="RGBA" if spec["transparent"] else "RGB"
                    source=im.convert(mode)
                frame=Image.new(
                    "RGBA" if spec["transparent"] else "RGB",
                    (native_w,native_h),
                    (0,0,0,0) if spec["transparent"] else (0,0,0))
                frame.paste(source,(0,0))
                if not spec["transparent"]:
                    last=source.crop((0,source.height-1,source.width,source.height))
                    for line in range(short):
                        frame.paste(last,(0,source.height+line))
                buffer=io.BytesIO()
                frame.save(buffer,"PNG",optimize=True)
                raw=buffer.getvalue()
                qa=png_info(raw,require_alpha=spec["transparent"])
                if (qa["width"],qa["height"])!=spec["dimensions"]:
                    raise VideoForgeError("EP01_LAYER_EDGE_ALIGNMENT_FAILED")
                technical=("candidate_rgba_edge_aligned_verified" if spec["transparent"]
                           else "candidate_background_edge_aligned_verified")
                edge_alignment={
                    "original_size":[source.width,source.height],
                    "aligned_size":[native_w,native_h],
                    "bottom_rows_added":short,
                    "original_pixels_resampled":False,
                    "original_pixels_shifted":False,
                    "method":"transparent_padding" if spec["transparent"] else "repeat_last_row"
                }
            else:
                technical="rejected_canvas_mismatch"
    except LayerError as exc:
        qa={"error":str(exc)}
        technical="rejected_alpha_or_png_qa"
    output_sha=hashlib.sha256(raw).hexdigest()
    destination.mkdir(parents=True,exist_ok=True)
    target.write_bytes(raw)
    if original_provider_png is not None:
        raw_name=stem+"-provider-raw"
        raw_file=destination/(raw_name+".png")
        raw_meta=destination/(raw_name+".production.json")
        if raw_file.exists() or raw_meta.exists() or raw_file.is_symlink() or raw_meta.is_symlink():
            raise VideoForgeError("EP01_LAYER_PROVIDER_RAW_EXISTS")
        raw_file.write_bytes(original_provider_png)
        raw_meta.write_text(json.dumps({
            "schema":"videoforge/ep01-unaligned-provider-layer/v1",
            "channel":CHANNEL,"video_id":VIDEO,
            "asset_id":raw_name,"candidate_scene_shot_id":"C01-P02",
            "sha256":hashlib.sha256(original_provider_png).hexdigest(),
            "source_originals_sha_verified":[
                {"id":"c01-p02-scene-mother","sha256":spec["source_sha256"],
                 "path":spec["mother_path"]}],
            "technical_qa":"raw_unaligned_preserved_before_deterministic_border_padding",
            "human_visual_approval":False,"youtube_uploaded":False,
            "rig_approved":False,
        },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    meta_record={
        "schema":"videoforge/ep01-shot-layer-result/v1",
        "channel":CHANNEL,"video_id":VIDEO,"asset_id":stem,
        "candidate_scene_shot_id":"C01-P02",
        "sha256":output_sha,"source_mother_sha256":spec["source_sha256"],
        "source_originals_sha_verified":[
            {"id":"c01-p02-scene-mother","sha256":spec["source_sha256"],
             "path":spec["mother_path"]}],
        "source_images_attached_to_request":1,
        "technical_qa":technical,"png_info":qa,
        "edge_alignment":edge_alignment, "provider_raw_preserved":original_provider_png is not None,
        "human_visual_approval":False,"recomposition_review":"pending",
        "rig_approved":False,"mp4_generated":False,"youtube_uploaded":False,
    }
    meta.write_text(json.dumps(meta_record,ensure_ascii=False,indent=2)+"\n",
                    encoding="utf-8")
    if technical.startswith("rejected_"):
        raise VideoForgeError("EP01_LAYER_GENERATED_BUT_QA_REJECTED_ARCHIVE_CANDIDATE "+technical)
    return meta_record


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--part",required=True)
    parser.add_argument("--url",required=True)
    args=parser.parse_args()
    try:
        item=generate(args.part,args.url)
        print("EP01_LAYER_REAL_PNG",json.dumps({
            "part":args.part,"sha256":item["sha256"],
            "technical_qa":item["technical_qa"],
            "human_visual_approval":False,"youtube_uploaded":False}))
        return 0
    except (VideoForgeError,proxy_images.ProxyImageError,OSError,ValueError) as exc:
        print("EP01_LAYER_STOPPED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
