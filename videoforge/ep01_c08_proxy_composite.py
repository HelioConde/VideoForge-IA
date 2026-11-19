"""EP01 C08-P02: compose THREE NEW independently proxy-generated images.

No OpenCV crops or segmentation become production sprites. Original provider
outputs are SHA-verified and NEVER modified. Tiny non-scaling canvas corrections
make disposable review copies only. Does not approve 2D rig or animation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops

from .ep01_continuity_motion import ROOT, EP, read as motion_plan
from .ep01_proxy_separate_parts import right_side_prop_coverage

CANVAS=(1053,1493)
MOTHER_SHA="3c21b7d82d69b1445b45cb1a23582e556c910530b568c26ae0d48b4873c38721"
PRODUCER="production-proxy-separate-part-v1"
RECORDS={
    "background":{
        "stem":"c08-p02-background-clean","run_id":44427271895,
        "sha256":"d1c40c69b65d3a59141ee1bf84135c4f9a5a470062441c855daaa4d52213d0ad",
        "dimensions":[1054,1493],"opaque":True,"crop_right":1,"crop_bottom":0,
        "pad_right":0,"pad_bottom":0,
    },
    "cart":{
        "stem":"c08-p02-object-carrinho-v2","run_id":44445488354,
        "sha256":"df5371baa402fb437e8671ffb6b11a21e640ec0ac5e589073d89850de1add65b",
        "dimensions":[1039,1514],"opaque":False,"crop_right":0,"crop_bottom":21,
        "pad_right":14,"pad_bottom":0,
    },
    "kael":{
        "stem":"c08-p02-character-kael-v2","run_id":44443878252,
        "sha256":"cbf8dc00f81788dd26675f1a16df2c971b44e287665ccf4ecbc59d698a6bec4d",
        "dimensions":[1054,1492],"opaque":False,"crop_right":1,"crop_bottom":0,
        "pad_right":0,"pad_bottom":1,
    },
}


def digest(path: Path) -> str:
    result=hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda:fp.read(1024*1024),b""):
            result.update(chunk)
    return result.hexdigest()


def source_paths(root:Path,role:str)->tuple[Path,Path]:
    row=RECORDS[role]
    rel=(EP/"assets"/"geracoes"/PRODUCER/str(row["run_id"])/row["stem"])
    return Path(root)/(str(rel)+".png"),Path(root)/(str(rel)+".production.json")


def verified_sources(root:Path=ROOT)->dict:
    source=motion_plan(root)["source_reference_shas"]["C08-P02"]
    if source["sha256"]!=MOTHER_SHA:
        raise ValueError("C08-P02 official mother changed")
    docs={}
    for role,expected in RECORDS.items():
        png,meta_path=source_paths(root,role)
        if (png.is_symlink() or meta_path.is_symlink()
                or not png.is_file() or not meta_path.is_file()):
            raise ValueError("Missing or unsafe archived proxy-generated artwork")
        if digest(png)!=expected["sha256"]:
            raise ValueError("Archived generated image bytes changed")
        meta=json.loads(meta_path.read_text(encoding="utf-8"))
        if (meta.get("sha256")!=expected["sha256"]
                or meta.get("asset_id")!=expected["stem"]
                or meta.get("source_mother_sha256")!=MOTHER_SHA
                or meta.get("generation_method")!="proxy_generated_separate_image"
                or meta.get("not_a_pixel_cutout") is not True
                or meta.get("provider_image_calls")!=1
                or meta.get("human_visual_approval") is not False
                or meta.get("rig_ready") is not False
                or [meta.get("width"),meta.get("height")]!=expected["dimensions"]
                or meta.get("source_canvas")!=list(CANVAS)):
            raise ValueError(f"Bad independent generation proof: {role}")
        with Image.open(png) as image:
            image.load()
            if (image.format!="PNG" or image.size!=tuple(expected["dimensions"])
                    or (role!="background" and "A" not in image.getbands())):
                raise ValueError(f"Invalid native PNG/alpha: {role}")
        docs[role]={"path":png,"proof":meta}
    return docs


def alignment(role:str,image:Image.Image)->tuple[Image.Image,dict]:
    rule=RECORDS[role]
    mode="RGB" if rule["opaque"] else "RGBA"
    image=image.convert(mode)
    w,h=image.size
    cropped=image.crop((0,0,w-rule["crop_right"],h-rule["crop_bottom"]))
    if not rule["opaque"]:
        alpha=image.getchannel("A")
        if rule["crop_right"] and alpha.crop((w-rule["crop_right"],0,w,h)).getbbox():
            raise ValueError("Alignment would cut off actual sprite on the right")
        if rule["crop_bottom"] and alpha.crop((0,h-rule["crop_bottom"],w,h)).getbbox():
            raise ValueError("Alignment would cut off actual sprite at bottom")
    output=Image.new(mode,CANVAS, (0,0,0) if rule["opaque"] else (0,0,0,0))
    if cropped.size!=(CANVAS[0]-rule["pad_right"],
                       CANVAS[1]-rule["pad_bottom"]):
        raise ValueError("Alignment rule does not produce the master canvas")
    output.paste(cropped,(0,0))
    if ImageChops.difference(output.crop((0,0,*cropped.size)),cropped).getbbox():
        raise ValueError("Pixel-alignment changed the provider's retained pixels")
    return output,{
        "input_dimensions":[w,h],"canvas":list(CANVAS),
        "crop_right_px":rule["crop_right"],"crop_bottom_px":rule["crop_bottom"],
        "pad_right_px":rule["pad_right"],"pad_bottom_px":rule["pad_bottom"],
        "visible_sprite_pixels_removed":False if not rule["opaque"] else None,
        "pixel_resampling":False,"pixel_shift":False,
    }


def build(root:Path,output_dir:Path)->dict:
    root=Path(root).resolve()
    dest=Path(output_dir)
    if (dest.is_symlink() or dest.resolve().is_relative_to(root)
            or dest.exists() and any(dest.iterdir())):
        raise ValueError("Do not write inside repository or overwrite any asset")
    docs=verified_sources(root)
    dest.mkdir(parents=True,exist_ok=True)
    aligned={}
    technical={}
    for role,item in docs.items():
        with Image.open(item["path"]) as src:
            current,alignment_qa=alignment(role,src)
        aligned[role]=current.convert("RGBA")
        file=dest/(role+"-PROXY-GENERATED-ALIGNED-UNAPPROVED.png")
        current.save(file,optimize=True)
        with Image.open(file) as saved:
            saved.load()
            expected=current.convert(saved.mode)
            if ImageChops.difference(saved,expected).getbbox():
                raise ValueError("Serialized review copy pixels are not exact")
        technical[role]={
            "generated_art_id":RECORDS[role]["stem"],
            "provider_run_id":RECORDS[role]["run_id"],
            "sha256_source":RECORDS[role]["sha256"],
            "sha256_aligned":digest(file),
            "source_provenance":"proxy_generated_separate_image",
            "aligned_artifact":file.name,
            "original_png_modified":False,
            "rig_ready":False,
            "human_visual_approval":False,
            **alignment_qa
        }
    kael_fraction=right_side_prop_coverage(aligned["kael"])
    if kael_fraction>0.02:
        raise ValueError("Kael still has cart pixels embedded at right")
    preview=Image.alpha_composite(
        Image.alpha_composite(aligned["background"],aligned["cart"]),
        aligned["kael"]).convert("RGB")
    preview.save(dest/"c08-p02-three-generated-layers-review.jpg",quality=94)
    for role in RECORDS:
        png,_=source_paths(root,role)
        if digest(png)!=RECORDS[role]["sha256"]:
            raise ValueError("Original provider PNG mutated during review")
    qa={
        "schema":"videoforge/ep01-c08-real-proxy-3-layers-qa/v1",
        "shot_id":"C08-P02",
        "source_mother_sha256":MOTHER_SHA,
        "real_independent_generation_calls_already_completed":3,
        "generation_method":"proxy_generated_separate_image",
        "source_roles_order":["background","cart","kael"],
        "native_source_QA":technical,
        "qa_cart_zone_opacity_kael":kael_fraction,
        "qa_cart_zone_maximum":0.02,
        "source_pngs_SHA_verified":3,
        "new_proxy_calls":0,"new_image_generations":0,
        "image_scaling":False,"image_warping":False,
        "original_images_overwritten":0,
        "composite_preview":"c08-p02-three-generated-layers-review.jpg",
        "background_geometry_visual_approved":False,
        "cart_identity_and_placement_approved":False,
        "kael_upper_hand_to_cart_contact_approved":False,
        "kael_lower_hand_to_cart_contact_approved":False,
        "recomposition_approved_against_mother":False,
        "cart_independent_wheel_layers_generated":False,
        "rig_ready":False,"rig_physical_qa":False,
        "animation_complete":False,
        "human_visual_approval":False,
        "final_mp4_ready":False,
        "youtube_publications":0,
        "next_gate":"Independent visual review of contact, source likeness, underlay and cart identity before rig layers."
    }
    (dest/"composite-qa.json").write_text(
        json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return qa


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    q=build(ROOT,args.output_dir)
    print(json.dumps({"real_generated_assets_checked":q["source_pngs_SHA_verified"],
                      "kael_cart_contamination":q["qa_cart_zone_opacity_kael"],
                      "rig_ready":q["rig_ready"],
                      "preview_file":q["composite_preview"],
                      "additional_paid_calls":0},ensure_ascii=False))


if __name__=="__main__":
    main()
