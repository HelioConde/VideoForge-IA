"""Preview-only spatial registration candidates for C01-P04 V3 native RGBA pieces.

Never changes archived PNGs, never creates final rig assets, never approves
alignment or scene composition. Only Pillow contact sheets and JSON evidence.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps
from videoforge.ep01_approved_v3_parts import aligned_source
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO

NAME = "QA-C01-P04-V3-REGISTRO-ESPACIAL"
SOURCE_REPORT = ROOT / REL / "QA-C01-P04-V3-CAMADAS-INDEPENDENTES.json"
EXPECTED_MOTHER_SHA = "b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
EXPECTED_ORIGINAL_SHA = "a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd"
SCENE = (941, 1672)
TARGETS = ("character-aldric", "character-guarda_esquerdo")


def font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def source_entry(part: str, report: dict) -> tuple[Image.Image, dict]:
    if part not in TARGETS:
        raise ValueError("EP01_REGISTER_TARGET_NOT_ALLOWED")
    rows = [x for x in report.get("parts", []) if x.get("part") == part]
    if len(rows) != 1:
        raise ValueError("EP01_REGISTER_PART_NOT_UNIQUE")
    data = rows[0]
    rel = Path(data["file"])
    if (rel.is_absolute() or ".." in rel.parts or
            not rel.is_relative_to(REL / "assets" / "geracoes")):
        raise ValueError("EP01_REGISTER_BAD_ARCHIVE_PATH")
    file = ROOT / rel
    proof = file.with_suffix(".production.json")
    if any(x.is_symlink() or not x.is_file() for x in (file, proof)):
        raise ValueError("EP01_REGISTER_MISSING_ARCHIVE_PROOF")
    raw = file.read_bytes()
    digest = sha256(raw).hexdigest()
    meta = json.loads(proof.read_text(encoding="utf-8"))
    if (digest != data["sha256"] or meta.get("sha256") != digest
            or meta.get("component") != part
            or meta.get("candidate_scene_shot_id") != "C01-P04"
            or meta.get("source_image_sha256") != EXPECTED_MOTHER_SHA
            or meta.get("human_visual_approval") is not False
            or meta.get("rig_ready") is not False
            or data.get("visual_approval") is not False
            or data.get("spatial_registration_pending") is not True
            or data.get("native_canvas_dimensions") != [981,1602]):
        raise ValueError("EP01_REGISTER_PROVENANCE_REJECTED " + part)
    with Image.open(BytesIO(raw)) as i:
        if i.format != "PNG" or i.size != (981,1602) or "A" not in i.getbands():
            raise ValueError("EP01_REGISTER_NATIVE_CANVAS_OR_ALPHA_REJECTED")
        image = i.convert("RGBA")
    amin,amax = image.getchannel("A").getextrema()
    if amin != 0 or amax < 128:
        raise ValueError("EP01_REGISTER_TRANSPARENCY_INVALID")
    return image, data


def native_alpha_bbox(image: Image.Image) -> tuple[int,int,int,int]:
    # A small alpha>15 threshold avoids unimportant 1-2px edge halos.
    a = image.getchannel("A").point(lambda v: 255 if v >= 16 else 0)
    bbox = a.getbbox()
    if bbox is None:
        raise ValueError("EP01_REGISTER_EMPTY_ALPHA")
    if bbox[2]-bbox[0] < 12 or bbox[3]-bbox[1] < 12:
        raise ValueError("EP01_REGISTER_IMPLAUSIBLE_ALPHA_BBOX")
    return bbox


def proposals(src_size: tuple[int,int], scene_size: tuple[int,int] = SCENE) -> list[dict]:
    sw,sh=src_size
    tw,th=scene_size
    if min(sw,sh,tw,th) <= 0:
        raise ValueError("EP01_REGISTER_BAD_DIMENSIONS")
    # NONE of these is a verified registration, only alternatives for QA.
    scale_fit = min(tw/sw,th/sh)
    candidates = [
      {"id":"A-top-left-native","scale":1.0,"offset_xy":[0,0],
       "explanation":"Native 1:1 at scene origin, with clipping outside the preview only"},
      {"id":"B-centered-native","scale":1.0,
       "offset_xy":[round((tw-sw)/2),round((th-sh)/2)],
       "explanation":"Native 1:1 centered on the scene canvas"},
      {"id":"C-uniform-fit","scale":round(scale_fit,6),
       "offset_xy":[round((tw-round(sw*scale_fit))/2),
                    round((th-round(sh*scale_fit))/2)],
       "explanation":"Uniform scale fit for preview only, not an exported or approved sprite"},
    ]
    return candidates


def overlay(mother: Image.Image, sprite: Image.Image, candidate: dict,
            bbox: tuple[int,int,int,int]) -> tuple[Image.Image, list[int]]:
    if mother.size != SCENE:
        raise ValueError("EP01_REGISTER_MOTHER_CANVAS_CHANGED")
    factor=candidate["scale"]
    if factor != 1:
        new_size=(round(sprite.width*factor),round(sprite.height*factor))
        scaled=sprite.resize(new_size,Image.Resampling.LANCZOS)
    else:
        scaled=sprite
    x,y=candidate["offset_xy"]
    canvas=mother.convert("RGBA").copy()
    # Blend the incoming sprite, exposing duplicate outlines as a QA signal.
    faded=scaled.copy()
    faded.putalpha(faded.getchannel("A").point(lambda a:round(a*0.6)))
    canvas.alpha_composite(faded,(x,y))
    b=[round(bbox[0]*factor+x),round(bbox[1]*factor+y),
       round(bbox[2]*factor+x),round(bbox[3]*factor+y)]
    d=ImageDraw.Draw(canvas)
    d.rectangle(tuple(b),outline=(255,40,45,255),width=4)
    return canvas,b


def tile(image: Image.Image, label: str, subtitle: str):
    out=Image.new("RGB",(314,620),"white")
    d=ImageDraw.Draw(out)
    d.text((8,7),label,font=font(15),fill="#111111")
    d.text((8,30),subtitle[:43],font=font(12),fill="#a33125")
    thumb=ImageOps.contain(image.convert("RGB"),(288,550),Image.Resampling.LANCZOS)
    out.paste(thumb,((314-thumb.width)//2,60))
    return out


def create() -> dict:
    src=aligned_source()
    if src["sha256"] != EXPECTED_MOTHER_SHA:
        raise ValueError("EP01_REGISTER_APPROVED_REFERENCE_CHANGED")
    report=json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    if (report.get("schema") != "videoforge/ep01-c01p04-v3-independent-layer-review/v1"
            or report.get("approved_original_source_sha256") != EXPECTED_ORIGINAL_SHA
            or report.get("technical_reference_sha256") != EXPECTED_MOTHER_SHA
            or report.get("rig_ready") is not False):
        raise ValueError("EP01_REGISTER_QA_REPORT_INVALID")
    with Image.open(BytesIO(src["blob"])) as i:
        mother=i.convert("RGB")
    if mother.size != SCENE:
        raise ValueError("EP01_REGISTER_REFERENCE_CANVAS_CHANGED")
    output=Image.new("RGB",(4*325+20,2*655+88),"#e9e9e6")
    pen=ImageDraw.Draw(output)
    pen.text((17,13),"C01-P04 V3 | REGISTRO ESPACIAL - 3 PROPOSTAS",font=font(23),fill="#101010")
    pen.text((17,48),"NÃO APROVADO / NÃO USAR NO RIG: conferir visualmente escala e contato.",font=font(15),fill="#a12a24")
    records=[]
    for row,part in enumerate(TARGETS):
        sprite,data=source_entry(part,report)
        bbox=native_alpha_bbox(sprite)
        proposals_for_part=proposals(sprite.size)
        box_height_fraction=(bbox[3]-bbox[1])/sprite.height
        box_fraction=((bbox[2]-bbox[0])*(bbox[3]-bbox[1]))/(sprite.width*sprite.height)
        alpha_hist=sprite.getchannel("A").histogram()
        visible_alpha_count=sum(alpha_hist[16:])
        visible_alpha_fraction=visible_alpha_count/(sprite.width*sprite.height)
        # Only a QA warning: this is a wide-shot mother, and an actor
        # occupying almost the full image height is suspect, not verified.
        suspicious_scale=part=="character-guarda_esquerdo" and box_height_fraction>0.8
        result={"part":part,"source_file":data["file"],"source_sha256":data["sha256"],
                "source_dimensions":list(sprite.size),"alpha_bbox_native_xyxy":list(bbox),
                "bbox_canvas_fraction":round(box_fraction,5),
                "bbox_height_fraction":round(box_height_fraction,5),
                "visible_alpha_pixel_fraction":round(visible_alpha_fraction,5),
                "scale_warning":("subject_almost_full_height_review_before_registration"
                                  if suspicious_scale else "visual_scale_review_pending"),
                "candidate_is_spatially_registered":False,
                "options":[],"selected_option":None,"human_visual_approval":False,
                "registration_authorized_for_rig":False}
        y=83+row*655
        output.paste(tile(sprite,"FONTE NATIVA / "+part,"PNG RGBA 981x1602, sem mexer nos pixels"),(15,y))
        for col,prop in enumerate(proposals_for_part,1):
            image,bbox_scene=overlay(mother,sprite,prop,bbox)
            sub=("ESCALA 1:1 / candidato" if prop["scale"]==1
                 else "ESCALA SÓ NA PRÉVIA / NÃO APROVADO")
            output.paste(tile(image,prop["id"],sub),(15+col*325,y))
            result["options"].append({**prop,"alpha_bbox_preview_xyxy":bbox_scene,
                "visual_approval":False,
                "preview_transform_only":True,"no_exported_sprite":True})
        records.append(result)
    base=ROOT/REL
    preview=base/( "QA-C01-P04-V3-REGISTRO-ESPACIAL.jpg")
    preview.parent.mkdir(parents=True,exist_ok=True)
    output.save(preview,"JPEG",quality=87,optimize=True)
    summary={
        "schema":"videoforge/ep01-c01p04-v3-native-registration-proposals/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "source_mother_sha256":EXPECTED_MOTHER_SHA,
        "original_creator_approved_sha256":EXPECTED_ORIGINAL_SHA,
        "board_path":preview.name,
        "board_sha256":sha256(preview.read_bytes()).hexdigest(),
        "pieces":records,
        "candidate_method":"preview-only compositing native sprite with alpha bbox; no final alignment",
        "hypotheses_are_not_spatial_measurements":True,
        "model_generation_calls":0,
        "source_pixels_changed":False,
        "rig_ready":False,"human_approval_of_registration":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "next_step":"human visual comparison against mother; confirm source ROI and contact before adopting a spatial transform",
    }
    (base/(NAME+".json")).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_NATIVE_REGISTRATION_QA_ONLY",json.dumps({
        "pieces":len(records),"proposals":sum(len(x["options"]) for x in records),
        "file":preview.name,"sha256":summary["board_sha256"],
        "rig_ready":False,"model_calls":0},ensure_ascii=False))
    return summary


if __name__ == "__main__":
    try:create()
    except (OSError,ValueError,RuntimeError) as exc:
        print("EP01_NATIVE_REGISTRATION_QA_FAILED",str(exc),file=sys.stderr)
        sys.exit(2)
