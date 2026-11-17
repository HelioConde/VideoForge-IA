"""Revisão LOCALIZADA candidata da C01-P02: luva, bainha e casaco.

Rejeição humana: painéis 2 e 4 da última prancha.
Uma geração editada do frame-mãe, com originais intactos e SHA.
NUNCA substitui mãe V1/arte canônica, não gera pose e não libera rig.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys

from . import image_generation_policy, proxy_images
from .errors import VideoForgeError
from .ep01_shot_layers import mother_source
from .layered_shot_plan import CHANNEL, VIDEO, REL, ROOT
from .ep01_contact_gate import EXPECTED_MOTHER_SHA
from .scene_layers import png_info

ASSET="c01-p02-scene-mother-contact-v3"
PATCH_ASSET="c01-p02-contact-local-patch-v3"
PRODUCER="production-contact-repair-v3"
SCHEMA="videoforge/ep01-contact-repair-candidate/v1"
ROI=(370,790,900,1660)  # mão inferior, espada, bocal, bainha, roupa
MAX_BYTES=32_000_000


def read_owner_review(root:Path=ROOT)->dict:
    path=Path(root)/REL/"REVISAO-ERRO-PAINEIS-C01-P02.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size>25000:
        raise VideoForgeError("EP01_REPAIR_OWNER_REVIEW_MISSING")
    item=json.loads(path.read_text(encoding="utf-8"))
    if (item.get("schema")!="videoforge/ep01-user-visual-rejection/v1"
        or item.get("source_mother_sha256")!=EXPECTED_MOTHER_SHA
        or item.get("owner_review",{}).get("rejected_panels")!=[2,4]
        or item.get("owner_review",{}).get("status")!="rejeitado"
        or item.get("human_approval") is not False):
        raise VideoForgeError("EP01_REPAIR_OWNER_REVIEW_INVALID")
    return item


def archived_candidate(root:Path=ROOT)->dict|None:
    root=Path(root)
    folder=root/REL/"assets"/"geracoes"/PRODUCER
    if folder.is_symlink():
        raise VideoForgeError("EP01_REPAIR_ARCHIVE_SYMLINK")
    if not folder.exists():return None
    candidates=[]
    for run in folder.iterdir():
        if run.is_symlink():
            raise VideoForgeError("EP01_REPAIR_ARCHIVE_RUN_SYMLINK")
        if not run.is_dir() or not run.name.isdecimal():continue
        target=run/(ASSET+".png")
        manifest=run/"manifesto-geracoes.json"
        if target.is_symlink() or manifest.is_symlink():
            raise VideoForgeError("EP01_REPAIR_ARCHIVE_FILE_SYMLINK")
        if not target.exists():continue
        if not manifest.is_file():
            raise VideoForgeError("EP01_REPAIR_INCOMPLETE_ARCHIVE")
        payload=json.loads(manifest.read_text(encoding="utf-8"))
        items=[x for x in payload.get("images",[])
               if isinstance(x,dict) and x.get("file")==target.name]
        if (payload.get("channel")!=CHANNEL or payload.get("video_id")!=VIDEO
            or payload.get("producer")!=PRODUCER
            or payload.get("github_run_id")!=int(run.name) or len(items)!=1):
            raise VideoForgeError("EP01_REPAIR_ARCHIVE_META_INVALID")
        sha=hashlib.sha256(target.read_bytes()).hexdigest()
        if sha!=items[0].get("sha256"):
            raise VideoForgeError("EP01_REPAIR_ARCHIVED_BYTES_MISMATCH")
        candidates.append({"run_id":int(run.name),"sha256":sha})
    return max(candidates,key=lambda x:x["run_id"]) if candidates else None


def prepare(root:Path=ROOT)->dict:
    root=Path(root)
    review=read_owner_review(root)
    mother,raw,dim=mother_source(root)
    if (mother.get("mother_sha256")!=EXPECTED_MOTHER_SHA
        or hashlib.sha256(raw).hexdigest()!=EXPECTED_MOTHER_SHA
        or [dim["width"],dim["height"]]!=[941,1672]):
        raise VideoForgeError("EP01_REPAIR_MOTHER_MISMATCH")
    if archived_candidate(root):
        raise VideoForgeError("EP01_REPAIR_CANDIDATE_ALREADY_ARCHIVED")
    prompt=(
        "EDIÇÃO CIRÚRGICA da imagem original anexada, anime fantasia medieval "
        "semi-realista. NÃO redesenhe todo o enquadramento, NÃO faça poses, "
        "prancha ou colagem. A arte de origem e a identidade do personagem "
        "devem permanecer iguais. Corrija exclusivamente o CONTATO na metade "
        "inferior direita: luva escura inferior do carrasco, bainha de couro "
        "vermelho vinho com decoração dourada e bocal, espada já parcialmente "
        "desembainhada, e borda do casaco escuro. "
        "ERRO A EVITAR: bainha entrando DENTRO da roupa ou sendo ocultada por "
        "pano que deveria estar atrás; a bainha deve ficar claramente "
        "À FRENTE do casaco, à frente de sua dobra, e ATRÁS dos dedos da "
        "luva inferior, que seguram a bainha com contato anatômico contínuo. "
        "A lâmina fica acima e entra alinhada no bocal da bainha; a luva "
        "superior continua segurando o cabo e o pomo da espada, sem lâmina "
        "atravessar a mão. Não inventar bainha duplicada, mão extra ou "
        "espada flutuante. Manter a perspectiva, comprimento e eixo dos "
        "objetos exatamente semelhantes ao frame de referência. "
        "NÃO alterar o rosto/roupa restante, trono, cenário, vitrais, "
        "escadaria, iluminação, escala e geometria fora da região de contato. "
        "Manter imagem VERTICAL única, mesmo enquadramento e coordenadas "
        "dos objetos. Render nítido e limpo. Sem texto/logos. "
        "Esta é apenas a versão CANDIDATA V3; não dar aprovação automática."
    )
    return {"mother_sha256":EXPECTED_MOTHER_SHA,"original":raw,
            "width":941,"height":1672,"prompt":prompt,
            "review":review, "roi":ROI}


def generate(url:str,model:str="gpt-image-2",root:Path=ROOT)->dict:
    root=Path(root)
    image_generation_policy.assert_image_generation_allowed(CHANNEL,VIDEO,root)
    if model!="gpt-image-2":
        raise VideoForgeError("EP01_REPAIR_MODEL_NOT_ALLOWED")
    spec=prepare(root)
    folder=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    if folder.is_symlink() or folder.exists() and any(folder.iterdir()):
        raise VideoForgeError("EP01_REPAIR_OUTPUT_NOT_EMPTY")
    response=proxy_images.call_proxy(
        url,"/v1/images/edits",os.getenv("CODEX_PROXY_API_KEY",""),
        {"model":model,"prompt":spec["prompt"],"n":1,
         "size":"1024x1536","background":"opaque",
         "output_format":"png","response_format":"b64_json","stream":False,
         "images":[{"image_url":"data:image/png;base64,"+
                    base64.b64encode(spec["original"]).decode("ascii")}]})
    raw,ext=proxy_images.decode_image(response)
    if ext!=".png" or len(raw)>MAX_BYTES:
        raise VideoForgeError("EP01_REPAIR_RETURNED_INVALID_PNG")
    dimensions=png_info(raw,require_alpha=False)
    candidate_size=[dimensions["width"],dimensions["height"]]
    native_size=candidate_size==[941,1672]
    # Preserve candidate as raw evidence even if its canvas differs.
    # A soft local repair is only possible for an EXACT matching canvas.
    folder.mkdir(parents=True,exist_ok=True)
    original=root/REL/"assets"/"geracoes"/"production-scene-mother-v2"/"44036287313"/"c01-p02-scene-mother.png"
    if original.is_symlink() or not original.is_file():
        raise VideoForgeError("EP01_REPAIR_ORIGINAL_ARCHIVE_MISSING")
    path=folder/(ASSET+".png")
    path.write_bytes(raw)
    digest=hashlib.sha256(raw).hexdigest()
    entries=[]
    data={
        "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
        "asset_id":ASSET,"candidate_scene_shot_id":"C01-P02",
        "sha256":digest,"source_mother_sha256":EXPECTED_MOTHER_SHA,
        "source_originals_sha_verified":[{"id":"c01-p02-scene-mother",
           "sha256":EXPECTED_MOTHER_SHA,
           "path":str(original.relative_to(root).as_posix())}],
        "revision_reason":"user_rejected_panels_2_and_4",
        "source_review_file":"REVISAO-ERRO-PAINEIS-C01-P02.json",
        "new_canvas":candidate_size,"source_canvas":[941,1672],
        "same_canvas":native_size,"technical_qa":"candidate_requires_visual_review",
        "source_unchanged":True,"candidate_is_not_canonical":True,
        "human_visual_approval":False,"rig_authorized":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "provider_image_calls":1
    }
    entries.append(data)
    if native_size:
        from PIL import Image, ImageFilter, ImageChops, ImageStat
        with Image.open(io.BytesIO(spec["original"])) as img:
            source_img=img.convert("RGB")
        with Image.open(io.BytesIO(raw)) as img:
            edit_img=img.convert("RGB")
        # Only the intersection of the edit and feathered lower-right
        # contact ROI changes. All pixels outside ROI remain original.
        alpha=Image.new("L",source_img.size,0)
        from PIL import ImageDraw
        draw=ImageDraw.Draw(alpha)
        draw.rectangle((ROI[0]+18,ROI[1]+18,ROI[2]-18,ROI[3]-18),fill=255)
        alpha=alpha.filter(ImageFilter.GaussianBlur(radius=17))
        patched=Image.composite(edit_img,source_img,alpha)
        patch_file=folder/(PATCH_ASSET+".png")
        patched.save(patch_file,"PNG",optimize=True)
        blob=patch_file.read_bytes()
        patch_digest=hashlib.sha256(blob).hexdigest()
        # Outside region is exact original; global MAE for QA only.
        difference=ImageChops.difference(source_img,patched)
        delta=round(sum(ImageStat.Stat(difference).mean)/3,3)
        entries.append({
            "schema":SCHEMA,"channel":CHANNEL,"video_id":VIDEO,
            "asset_id":PATCH_ASSET,"candidate_scene_shot_id":"C01-P02",
            "sha256":patch_digest,
            "source_mother_sha256":EXPECTED_MOTHER_SHA,
            "source_originals_sha_verified":[
               {"id":"c01-p02-scene-mother","sha256":EXPECTED_MOTHER_SHA,
                "path":str(original.relative_to(root).as_posix())},
               {"id":ASSET,"sha256":digest,
                "path":str(path.relative_to(root).as_posix())}],
            "crop_roi":list(ROI),
            "source_unrelated_pixels_retained":True,
            "no_spatial_resampling":True,
            "mean_rgb_difference_from_source":delta,
            "technical_qa":"local_edit_candidate_not_approved",
            "human_visual_approval":False,"rig_authorized":False,
            "mp4_generated":False,"youtube_uploaded":False,
            "provider_image_calls":0
        })
    for entry in entries:
        stem=entry["asset_id"]
        (folder/(stem+".production.json")).write_text(
            json.dumps(entry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_HAND_SHEATH_CONTACT_REPAIR_CANDIDATE",json.dumps({
        "sha256":digest,"same_canvas":native_size,
        "source_unchanged":True,"files":[x["asset_id"] for x in entries],
        "human_approved":False,"provider_calls":1}))
    return data


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--url",required=True)
    args=parser.parse_args()
    try:
        generate(args.url)
    except (OSError,ValueError,VideoForgeError,proxy_images.ProxyImageError) as e:
        print("EP01_CONTACT_REPAIR_STOPPED",str(e),file=sys.stderr)
        raise SystemExit(2)


if __name__=="__main__":
    main()
