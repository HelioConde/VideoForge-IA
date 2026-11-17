"""QA-only visual board for the C01-P04 approved V3 independently drawn parts.

This does NOT create sprite cutouts or final rig art. The provisional
composite is for identifying mistakes in scale, contact and alpha only.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys

from PIL import Image,ImageDraw,ImageFont,ImageOps
from videoforge.ep01_approved_v3_parts import (
    ROLE_CONFIG, SCHEMA as PART_SCHEMA, aligned_source, existing_part)
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from videoforge.ep01_approved_v3_aldric_repair import archived as archived_aldric_repair, SCHEMA as ALDRIC_SCHEMA

PREFIX="QA-C01-P04-V3-CAMADAS-INDEPENDENTES"
ORDER=["background-clean","character-kael","character-aldric",
       "character-guarda_esquerdo","character-guarda_direito",
       "object-lanca-esquerda","object-lanca-direita"]

def font(sz:int):
    try:return ImageFont.truetype("DejaVuSans.ttf",sz)
    except OSError:return ImageFont.load_default()

def check_png(blob:bytes,part:str) -> Image.Image:
    with Image.open(BytesIO(blob)) as im:
        im.load()
        if im.format!="PNG" or not (512 <= im.width <= 2048 and 512 <= im.height <= 3072):
            raise RuntimeError("EP01_C01P04_QA_BAD_PNG_CANVAS "+part)
        if part in ("background-clean", "approved-aligned-mother") and im.size!=(941,1672):
            raise RuntimeError("EP01_C01P04_QA_SCENE_BACKGROUND_MUST_BE_FULL_CANVAS "+part)
        has_alpha="A" in im.getbands()
        if part not in ("background-clean", "approved-aligned-mother"):
            if not has_alpha:
                raise RuntimeError("EP01_C01P04_QA_MISSING_ALPHA "+part)
            low,high=im.getchannel("A").getextrema()
            if low != 0 or high < 128:
                raise RuntimeError("EP01_C01P04_QA_INVALID_ALPHA "+part)
        return im.convert("RGBA").copy()

def verified_art(part:str):
    # Aldric's native RGBA revisions were archived with nonmatching canvas.
    # Review as standalone candidate only, NEVER composited without registration.
    if part == "character-aldric":
        cached=archived_aldric_repair()
        if cached is None:
            cached=existing_part(part)
    else:
        cached=existing_part(part)
    if cached is None:
        raise RuntimeError("EP01_C01P04_QA_PART_NOT_ARCHIVED "+part)
    p=ROOT / cached["file"]
    proof=p.with_suffix(".production.json")
    if any(x.is_symlink() or not x.is_file() for x in (p,proof)):
        raise RuntimeError("EP01_C01P04_QA_PROOF_MISSING "+part)
    blob=p.read_bytes()
    data=json.loads(proof.read_text(encoding="utf-8"))
    digest=sha256(blob).hexdigest()
    allowed_technical = {
        "candidate_needs_visual_alignment_review",
        "candidate_native_canvas_requires_spatial_registration",
        # Aldric repair V2 rejected only for full-scene canvas, not alpha.
        "rejected_unacceptable_canvas" if part=="character-aldric" else "",
    }
    if (digest != cached["sha256"]
            or data.get("schema") not in ({PART_SCHEMA,ALDRIC_SCHEMA} if part=="character-aldric" else {PART_SCHEMA})
            or data.get("component") != part
            or data.get("candidate_scene_shot_id") != "C01-P04"
            or data.get("sha256") != digest
            or data.get("not_a_pixel_cutout") is not True
            or data.get("human_visual_approval") is not False
            or data.get("rig_ready") is not False
            or data.get("technical_qa") not in allowed_technical):
        raise RuntimeError("EP01_C01P04_QA_PROVENANCE_FAIL "+part)
    frame=check_png(blob,part)
    must_register=frame.size!=(941,1672)
    return (frame,
            {"part":part,"file":cached["file"],"sha256":digest,
             "source_sha256":data["source_image_sha256"],
             "role":ROLE_CONFIG[part]["role"],
             "provider_native_sha256":data.get("provider_native_sha256"),
             "technical_qa":data.get("technical_qa"),
             "native_canvas_dimensions":list(frame.size),
             "spatial_registration_pending":must_register,
             "visual_approval":False})

def preview_frame(img:Image.Image) -> Image.Image:
    w,h=350,617
    check=Image.new("RGBA",(w,h),(240,240,240,255))
    d=ImageDraw.Draw(check)
    block=26
    for row in range((h+block-1)//block):
        for col in range((w+block-1)//block):
            if (row+col)%2==0:
                d.rectangle((col*block,row*block,(col+1)*block,(row+1)*block),
                            fill=(210,210,210,255))
    thumb=ImageOps.contain(img,(w,h),Image.Resampling.LANCZOS)
    xpos=(w-thumb.width)//2
    ypos=(h-thumb.height)//2
    check.alpha_composite(thumb,(xpos,ypos))
    return check.convert("RGB")

def create():
    source=aligned_source()
    mother=check_png(source["blob"],"approved-aligned-mother")
    frames={}
    metadata=[]
    for part in ORDER:
        img,proof=verified_art(part)
        frames[part]=img
        metadata.append(proof)
    # Editorial recomposition only, no render/rig approval.
    composite=frames["background-clean"].copy()
    omitted_from_composite=[]
    for part in ["character-aldric","character-guarda_esquerdo",
                 "character-guarda_direito","object-lanca-esquerda",
                 "object-lanca-direita","character-kael"]:
        if frames[part].size == (941,1672):
            composite.alpha_composite(frames[part])
        else:
            # Never stretch or guess an actor's position/scale.
            omitted_from_composite.append(part)
    items=[("MÃE APROVADA (ORIGEM V3)",mother),
           ("FUNDO LIMPO (NOVO)",frames["background-clean"]),
           ("KAEL (PNG RGBA)",frames["character-kael"]),
           ("ALDRIC (PNG RGBA)",frames["character-aldric"]),
           ("GUARDA ESQUERDO",frames["character-guarda_esquerdo"]),
           ("GUARDA DIREITO",frames["character-guarda_direito"]),
           ("LANÇA ESQUERDA",frames["object-lanca-esquerda"]),
           ("LANÇA DIREITA",frames["object-lanca-direita"]),
           ("COMPOSIÇÃO PARCIAL / NÃO USAR NO RIG",composite)]
    W,H=1195,2220
    canvas=Image.new("RGB",(W,H),"#e6e6e3")
    draw=ImageDraw.Draw(canvas)
    draw.text((23,15),"EP01 / C01-P04 V3 - PEÇAS GERADAS SEPARADAMENTE",
              font=font(23),fill="#202020")
    draw.text((23,50),"NENHUMA PEÇA APROVADA. Comparar posição, alfas, mãos, lanças e personagens.",
              font=font(15),fill="#9e2a2a")
    for i,(name,img) in enumerate(items):
        x=20+(i%3)*391
        y=88+(i//3)*703
        draw.rounded_rectangle((x,y,x+375,y+686),radius=7,fill="#ffffff")
        draw.text((x+11,y+9),name,font=font(15),fill="#222222")
        show=preview_frame(img)
        canvas.paste(show,(x+13,y+42))
    board=ROOT/REL/(PREFIX+".jpg")
    canvas.save(board,"JPEG",quality=89,optimize=True)
    report={
        "schema":"videoforge/ep01-c01p04-v3-independent-layer-review/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "approved_original_source_sha256":"a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd",
        "technical_reference_sha256":source["sha256"],
        "board":board.name,"board_sha256":sha256(board.read_bytes()).hexdigest(),
        "parts":metadata,
        "spatial_registration_pending":omitted_from_composite,
        "composite_does_not_guess_native_sprite_position":True,
        "preview_composite_for_QA_only":True,
        "human_visual_approval_of_parts":False,
        "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False,
        "manual_review_checks":[
            "background truly clean with architecture restored",
            "Kael remains kneeling and faces the throne, exact scale",
            "Aldric seated in correct high throne position",
            "both guards stay on original sides with anatomically correct gauntlets",
            "two spears are separately generated and attach at lower shafts",
            "alpha is true transparent outside sprites and no ghost background",
            "provisional layering has no doubled hands or missing cloth",
            "hidden regions are fully redrawn for later movement",
            "camera still supports planned focus and dolly out",
        ],
    }
    (ROOT/REL/(PREFIX+".json")).write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_C01P04_V3_LAYERS_QA_CREATED",json.dumps({
        "parts":len(metadata),"sha256":report["board_sha256"],
        "approved_parts":False,"paid_calls":0},ensure_ascii=False))
    return report

if __name__=="__main__":
    try:create()
    except (OSError,ValueError,RuntimeError) as err:
        print("EP01_C01P04_V3_LAYERS_QA_BLOCKED",str(err),file=sys.stderr)
        sys.exit(2)
