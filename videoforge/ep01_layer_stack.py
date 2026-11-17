"""Composição C01-P02: bainha/espada à frente da roupa; luvas no topo.

NÃO regenera imagens, NÃO desloca nem escala PNGs e NÃO autoriza rig.
Todos os pixels são auditados contra SHA do frame original e camadas arquivadas.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from .ep01_shot_layers import mother_source
from .ep01_source_sword import ASSET as SWORD_ASSET
from .ep01_contact_cutouts import EXPECTED_MOTHER_SHA

ASSETS={
    "background":"c01-p02-background-aligned",
    "body":"c01-p02-character-carrasco",
    "sheath":"c01-p02-object-bainha-source-visible",
    "sword":SWORD_ASSET,
    "upper_hand":"c01-p02-hand-upper-contact-occlusion",
    "lower_hand":"c01-p02-hand-lower-contact-occlusion",
}
# A ROUPA NÃO PODE FICAR À FRENTE DA BAINHA.
REQUIRED_ORDER=("background","body","sheath","sword","upper_hand","lower_hand")
REJECTED_ORDER=("background","sheath","sword","body","upper_hand","lower_hand")
SCENE_SIZE=(941,1672)


def read_layers(root:Path=ROOT)->tuple[Image.Image,dict[str,Image.Image],dict[str,str]]:
    root=Path(root)
    mother_data,source,info=mother_source(root)
    if (mother_data["mother_sha256"]!=EXPECTED_MOTHER_SHA
        or hashlib.sha256(source).hexdigest()!=EXPECTED_MOTHER_SHA):
        raise VideoForgeError("EP01_STACK_MOTHER_SHA_CHANGED")
    with Image.open(io.BytesIO(source)) as im:
        if im.format!="PNG" or im.size!=SCENE_SIZE:
            raise VideoForgeError("EP01_STACK_MOTHER_FRAME_CHANGED")
        mother=im.convert("RGBA")
    register=root/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
    if register.is_symlink() or not register.is_file() or register.stat().st_size>1000000:
        raise VideoForgeError("EP01_STACK_REGISTRY_MISSING")
    rows=json.loads(register.read_text(encoding="utf-8"))["geracoes"]
    layers={}
    hashes={}
    for key,asset in ASSETS.items():
        entries=[row for row in rows if row.get("asset")==asset]
        if len(entries)!=1:
            raise VideoForgeError("EP01_STACK_LAYER_NOT_UNIQUE "+asset)
        row=entries[0]
        rel=Path(row["arquivo"])
        if (rel.is_absolute() or ".." in rel.parts
            or not rel.is_relative_to(REL/"assets"/"geracoes")):
            raise VideoForgeError("EP01_STACK_UNSAFE_FILE_PATH")
        path=root/rel
        meta=path.with_suffix(".production.json")
        if (path.is_symlink() or not path.is_file() or path.stat().st_size>35_000_000
            or meta.is_symlink() or not meta.is_file()):
            raise VideoForgeError("EP01_STACK_SOURCE_MISSING "+asset)
        source=path.read_bytes()
        digest=hashlib.sha256(source).hexdigest()
        proof=json.loads(meta.read_text(encoding="utf-8"))
        if (digest!=row.get("sha256") or proof.get("sha256")!=digest
            or proof.get("source_mother_sha256")!=EXPECTED_MOTHER_SHA
            or proof.get("youtube_uploaded") is not False
            or (row.get("width"),row.get("height"))!=SCENE_SIZE):
            raise VideoForgeError("EP01_STACK_BAD_LAYER_PROVENANCE "+asset)
        with Image.open(io.BytesIO(source)) as im:
            if im.format!="PNG" or im.size!=SCENE_SIZE:
                raise VideoForgeError("EP01_STACK_BAD_LAYER_CANVAS")
            layers[key]=im.convert("RGBA")
        hashes[key]=digest
    return mother,layers,hashes


def compose(layers:dict[str,Image.Image],order=REQUIRED_ORDER)->Image.Image:
    if tuple(order) not in (REQUIRED_ORDER,REJECTED_ORDER):
        raise VideoForgeError("EP01_STACK_UNKNOWN_ORDER")
    if set(layers)!=set(ASSETS) or any(x.size!=SCENE_SIZE for x in layers.values()):
        raise VideoForgeError("EP01_STACK_INPUT_LAYERS_INVALID")
    canvas=Image.new("RGBA",SCENE_SIZE,(0,0,0,0))
    for name in order:
        canvas=Image.alpha_composite(canvas,layers[name])
    return canvas


def sheath_contact_region(layers:dict[str,Image.Image])->Image.Image:
    # Pixels em que bainha e roupa se sobrepõem; retiram-se os dedos e
    # a lâmina da interseção, restando contato bainha-sobre-roupa.
    sheath=layers["sheath"].getchannel("A")
    cloth=layers["body"].getchannel("A")
    sword=layers["sword"].getchannel("A")
    hands=ImageChops.lighter(layers["upper_hand"].getchannel("A"),
                              layers["lower_hand"].getchannel("A"))
    overlap=ImageChops.darker(sheath,cloth)
    overlap=ImageChops.subtract(overlap,ImageChops.lighter(sword,hands))
    return overlap


def measure()->tuple[Image.Image,Image.Image,Image.Image,dict]:
    original,layers,hashes=read_layers()
    old=compose(layers,REJECTED_ORDER)
    fixed=compose(layers,REQUIRED_ORDER)
    reference=original.convert("RGB")
    old_diff=ImageChops.difference(old.convert("RGB"),reference)
    fixed_diff=ImageChops.difference(fixed.convert("RGB"),reference)
    mae=lambda img:round(sum(ImageStat.Stat(img).mean)/3,3)
    region=sheath_contact_region(layers)
    count=region.histogram()[255]
    if count<1:
        raise VideoForgeError("EP01_STACK_SHEATH_BODY_OVERLAP_NOT_FOUND")
    # Uma interseção mínima revela que o recorte antigo do carrasco já
    # exclui quase toda a bainha. Mudar apenas z-index NÃO resolve a
    # máscara/canvas/posicionamento das propostas antigas (0,300)/(0,500).
    # O novo preview é diagnóstico, nunca aprovado automaticamente.
    # O pixel da bainha deve aparecer à frente da roupa e usar exato RGB
    # da mãe no contato que não está ocluído por mãos/espada.
    checked=ImageChops.multiply(
        ImageChops.difference(fixed.convert("RGB"),reference).convert("L"),region)
    if checked.getbbox() is not None:
        raise VideoForgeError("EP01_STACK_SHEATH_STILL_BEHIND_CLOTHING")
    report={
        "schema":"videoforge/ep01-c01-p02-clothing-depth-audit/v1",
        "mother_sha256":EXPECTED_MOTHER_SHA,
        "layer_hashes":hashes,
        "rejected_order":list(REJECTED_ORDER),
        "corrected_order":list(REQUIRED_ORDER),
        "sword_or_sheath_resampled":False,
        "all_layers_original_native_canvas":True,
        "gloves_foreground":True,
        "sheath_above_coat":True,
        "sheath_coat_overlap_pixels_exact":count,
        "body_mask_already_excludes_most_sheath":count<100,
        "z_order_alone_not_proof_of_fix":True,
        "rejected_legacy_offsets":[[0,300],[0,500],[0,650],[0,800],[-80,650],[80,650]],
        "old_mean_rgb_difference":mae(old_diff),
        "corrected_mean_rgb_difference":mae(fixed_diff),
        "automatic_visual_approval":False,
        "rig_authorized":False,
        "mp4_rendered":False,
        "youtube_uploaded":False,
        "provider_calls":0,
    }
    return original,old,fixed,report
