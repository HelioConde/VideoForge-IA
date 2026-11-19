"""C08-P02 source-pinned contact and C08-P03 continuity REVIEW PACK.

This is deliberately an artifact-only visual review aid, NOT an image edit,
a regenerated AI part, a rig, a claim of good grip, or a finished MP4.
Uses the three independently proxy-generated unapproved RGBA/RGB images.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

from . import ep01_c08_proxy_composite as source_comp
from . import ep01_cart_kinematics as motion
from . import ep01_camera_batch as camera
from . import ep01_continuity_motion as continuity
from . import ep01_continuity_v2 as story

ROOT=source_comp.ROOT
SCHEMA="videoforge/ep01-c08-p02-grip-review-packet/v1"
# Rectangles are exact SOURCE CANVAS pixel regions in the existing archived
# shot. These are intentionally *human* contact regions, not generated masks.
ROIS={
    "upper_hand":(560,615,635,713),
    "lower_hand":(555,740,650,830),
    "wheel_and_ground":(440,830,1020,1310),
}
PREVIEW="c08-p02-contact-qa-review-board.png"
COMPOSITE="c08-p02-three-generated-layers-review.jpg"
SOURCE_PARTS=("background","cart","kael")
EXPECTED_SHOT_IDS=(
    "C07-P01","C07-P02","C07-P03","C07-P04",
    "C08-P01","C08-P02","C08-P03","C08-P04","C08-P05",
)


def sha(path:Path)->str:
    hash=hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda:inp.read(1024*1024),b""):
            hash.update(block)
    return hash.hexdigest()


def mask_count(image:Image.Image)->int:
    """Count pixels from an 8-bit alpha threshold mask (not a skin detector)."""
    return image.histogram()[255]


def mask_stats(kael:Image.Image,cart:Image.Image,region:tuple)->dict:
    # A 192 threshold excludes faint semitransparent antialiasing. Alpha
    # overlap tells only layer geometry, NEVER anatomical plausibility.
    if (kael.size!=source_comp.CANVAS or cart.size!=source_comp.CANVAS
            or any(not isinstance(v,int) for v in region)):
        raise ValueError("Only the original source canvas/pixel ROIs are accepted")
    x0,y0,x1,y1=region
    if not (0<=x0<x1<=kael.width and 0<=y0<y1<=kael.height):
        raise ValueError("Unsafe contact ROI")
    km=kael.getchannel("A").crop(region).point(lambda p:255 if p>=192 else 0)
    cm=cart.getchannel("A").crop(region).point(lambda p:255 if p>=192 else 0)
    kc=mask_count(km)
    cc=mask_count(cm)
    if not kc or not cc:
        raise ValueError("The expected contact ROI does not contain both source layers")
    overlap=mask_count(ImageChops.multiply(km,cm))
    nearest_radius=0 if overlap else None
    grown=cm
    if not overlap:
        for radius in range(1,33):
            grown=grown.filter(ImageFilter.MaxFilter(3))
            if ImageChops.multiply(km,grown).getbbox() is not None:
                nearest_radius=radius
                break
    return {
        "roi_px":[x0,y0,x1,y1],
        "opaque_kael_px":kc,
        "opaque_cart_px":cc,
        "opaque_intersection_px":overlap,
        "kael_region_fraction_over_cart":round(overlap/kc,6),
        "chebyshev_proximity_radius_px":nearest_radius,
        "can_prove_correct_grip":False,
        "alpha_only_not_hand_anatomy":True,
    }


def narrative_handoff(root:Path)->dict:
    doc=story.read_plan(root)
    coverage=camera.build_plan(root,"continuity-v2")
    motion_doc=continuity.read(root)
    poses=motion.build_poses(motion_doc)
    kinematics=motion.validate_poses(poses)
    shots=doc["shots"]
    indexed={s["id"]:s for s in coverage["shots"]}
    if ([s["id"] for s in shots]!=list(EXPECTED_SHOT_IDS)
            or len(coverage["shots"])!=42 or len(indexed)!=42
            or not set(EXPECTED_SHOT_IDS).issubset(indexed)
            or any(indexed[sid].get("fps")!=30 for sid in EXPECTED_SHOT_IDS)
            or len(poses)!=240 or kinematics["frames_checked"]!=240
            or kinematics["continuous_cut"] is not True
            or kinematics["rig_with_real_assets_approved"] is not False):
        raise ValueError("Narrative, EDL or 240-frame source readback changed")
    for item in shots:
        edl=indexed[item["id"]]
        if (edl["start_frame"]!=item["start_frame"]
                or edl["duration_frames"]!=item["end_exclusive"]-item["start_frame"]):
            raise ValueError("Nine approved-plan time ranges differ from 42-shot EDL")
    p02=indexed["C08-P02"]
    p03=indexed["C08-P03"]
    if (p02["start_frame"]!=2550 or p02["duration_frames"]!=130
            or p03["start_frame"]!=2680 or p03["duration_frames"]!=110
            or p03["start_frame"]!=p02["start_frame"]+p02["duration_frames"]
            or poses[129].shot_id!="C08-P02"
            or poses[130].shot_id!="C08-P03"
            or abs(poses[129].yaw_degrees-90)>1e-7
            or abs(poses[130].yaw_degrees-90)>1e-7):
        raise ValueError("Cart cut between C08-P02 and C08-P03 has drifted")
    return {
        "total_shots":42,"regional_shots":list(EXPECTED_SHOT_IDS),
        "regional_shots_matched":9,
        "c08p02_frame_range":[2550,2680],
        "c08p03_frame_range":[2680,2790],
        "kinematic_frames":240,
        "at_cut_yaw_degrees":[poses[129].yaw_degrees,poses[130].yaw_degrees],
        "kinematic_continuity":True,
        "artistic_axis_and_visual_contact_approved":False,
        "real_wheel_rgba_parts_present":False,
        "rendered_character_animation":False,
    }


def make_board(composite:Path, destination:Path)->None:
    with Image.open(composite) as raw:
        frame=raw.convert("RGB")
        if frame.size!=source_comp.CANVAS:
            raise ValueError("Review board requires the exact aligned source canvas")
        width,height=520,415
        sheet=Image.new("RGB",(width*3,height),(244,244,244))
        try:
            font=ImageFont.truetype("DejaVuSans.ttf",20)
        except OSError:
            font=ImageFont.load_default()
        cards=[
            ("Mao superior: contato pendente",(475,560,710,775)),
            ("Mao inferior: rever pegada",(500,720,765,895)),
            ("Rodas e apoio no chao",ROIS["wheel_and_ground"]),
        ]
        for i,(heading,region) in enumerate(cards):
            img=ImageOps.contain(frame.crop(region),(width-18,height-74))
            x=i*width+(width-img.width)//2
            y=60+(height-70-img.height)//2
            sheet.paste(img,(x,y))
            draw=ImageDraw.Draw(sheet)
            draw.text((i*width+10,12),heading,font=font,fill=(30,30,30))
            draw.rectangle((x-1,y-1,x+img.width,y+img.height),
                           outline=(60,60,60),width=2)
        sheet.save(destination,format="PNG",optimize=True)


def produce(root:Path,outdir:Path)->dict:
    root=Path(root).resolve()
    dest=Path(outdir).resolve()
    if (dest==root or dest.is_relative_to(root) or outdir.is_symlink()
            or dest.exists() and any(dest.iterdir())):
        raise ValueError("Contact QA must never overwrite source or another review")
    verified=source_comp.verified_sources(root)
    if set(verified)!=set(SOURCE_PARTS):
        raise ValueError("Three approved-provenance independent source candidates required")
    dest.mkdir(parents=True,exist_ok=True)
    composed=source_comp.build(root,dest/"recomposition")
    if (composed["source_pngs_SHA_verified"]!=3
            or composed["new_proxy_calls"]!=0
            or composed["human_visual_approval"] is not False
            or composed["kael_upper_hand_to_cart_contact_approved"] is not False
            or composed["rig_ready"] is not False):
        raise ValueError("Source composition falsely claimed visual approval")
    aligned={}
    for role in ("kael","cart"):
        with Image.open(verified[role]["path"]) as src:
            aligned[role]=source_comp.alignment(role,src)[0].convert("RGBA")
    masks={name:mask_stats(aligned["kael"],aligned["cart"],rect)
           for name,rect in ROIS.items() if name!="wheel_and_ground"}
    # These exact pinned source ROIs have no upper-hand pixel overlap, but
    # the lower hand overlays the cart. Neither is an anatomical pass.
    if (masks["upper_hand"]["opaque_intersection_px"]!=0
            or masks["upper_hand"]["chebyshev_proximity_radius_px"] is None
            or masks["upper_hand"]["chebyshev_proximity_radius_px"]<1
            or masks["lower_hand"]["opaque_intersection_px"]<100):
        raise ValueError("C08-P02 grip geometry changed: new visual QA required")
    make_board(dest/"recomposition"/COMPOSITE,dest/PREVIEW)
    source_hashes={role:source_comp.RECORDS[role]["sha256"] for role in SOURCE_PARTS}
    aligned_hashes={role:composed["native_source_QA"][role]["sha256_aligned"]
                    for role in SOURCE_PARTS}
    report={
        "schema":SCHEMA,"scene":"C08-P02","source_mother_sha256":source_comp.MOTHER_SHA,
        "separate_source_png_sha256":source_hashes,
        "aligned_review_png_sha256":aligned_hashes,
        "generation_method":"three_existing_independently_proxy_generated_images",
        "new_paid_proxy_calls":0,"new_generated_images":0,
        "original_pngs_overwritten":0,"image_resampling":False,
        "source_rois":{k:list(v) for k,v in ROIS.items()},
        "geometry_alpha":masks,
        "visual_observations_requiring_human_confirmation":[
            "upper hand hangs above the cart fixture; visible grip not demonstrated",
            "lower hand overlaps the side rail; overlap alone does not prove a secure push grip",
            "cart wheel/ground and caster depth must be checked against the mother",
        ],
        "narrative_42_shot_handoff":narrative_handoff(root),
        "preview_board":PREVIEW,
        "preview_board_sha256":sha(dest/PREVIEW),
        "composite_file":"recomposition/"+COMPOSITE,
        "composite_file_sha256":sha(dest/"recomposition"/COMPOSITE),
        "status":"blocked_pending_contact_art_and_human_visual_qa",
        "agent_05_provenance_audit":True,
        "agent_06_visual_contact_qa_proposal":True,
        "agent_08_kinematic_readback":True,
        "agent_09_edl_readback":True,
        "agent_12_automatic_source_byte_qa_not_visual_approval":True,
        "upper_hand_contact_approved":False,
        "lower_hand_contact_approved":False,
        "wheel_sprites_independently_generated":False,
        "visual_mother_likeness_approved":False,
        "human_visual_approval":False,"rig_ready":False,
        "animated_episode_ready":False,"youtube_published":False,
    }
    (dest/"c08-p02-contact-review.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def verify_report(root:Path,outdir:Path)->dict:
    """Independent reread: check every pinned source and output digest."""
    root=Path(root).resolve()
    dest=Path(outdir).resolve()
    report=json.loads((dest/"c08-p02-contact-review.json").read_text(encoding="utf-8"))
    required=source_comp.verified_sources(root)
    if (report.get("schema")!=SCHEMA or report.get("status")!="blocked_pending_contact_art_and_human_visual_qa"
            or report.get("source_mother_sha256")!=source_comp.MOTHER_SHA
            or report.get("new_paid_proxy_calls")!=0
            or report.get("new_generated_images")!=0
            or report.get("human_visual_approval") is not False
            or report.get("rig_ready") is not False
            or report.get("youtube_published") is not False
            or report.get("upper_hand_contact_approved") is not False
            or report.get("lower_hand_contact_approved") is not False
            or report.get("wheel_sprites_independently_generated") is not False):
        raise ValueError("Review report must not promote source pixels into visual approval")
    for role,row in required.items():
        if (report.get("separate_source_png_sha256",{}).get(role)!=sha(row["path"])
                or report["separate_source_png_sha256"][role]!=source_comp.RECORDS[role]["sha256"]):
            raise ValueError("Independent image provenance changed")
    if (sha(dest/report["preview_board"])!=report["preview_board_sha256"]
            or sha(dest/report["composite_file"])!=report["composite_file_sha256"]):
        raise ValueError("Review artifacts have been modified after report")
    upper=report["geometry_alpha"]["upper_hand"]
    lower=report["geometry_alpha"]["lower_hand"]
    if (upper["opaque_intersection_px"]!=0
            or upper["chebyshev_proximity_radius_px"] is None
            or upper["chebyshev_proximity_radius_px"]<1
            or lower["opaque_intersection_px"]<100):
        raise ValueError("Upper/lower hand evidence changed")
    # Rebuild the two masks independently from their archived native PNGs.
    layers={}
    for role in ("kael","cart"):
        with Image.open(required[role]["path"]) as image:
            layers[role]=source_comp.alignment(role,image)[0].convert("RGBA")
    for name in ("upper_hand","lower_hand"):
        if report["geometry_alpha"][name]!=mask_stats(
                layers["kael"],layers["cart"],ROIS[name]):
            raise ValueError("ROI contact evidence no longer matches the image source")
    if report["narrative_42_shot_handoff"]!=narrative_handoff(root):
        raise ValueError("C08-P02/03 narrative readback mismatch")
    return {"rechecked_source_images":3,"contact_regions":2,
            "shots_source_matched":9,"technical_pose_frames":240,
            "new_paid_calls":0,"qa_technical_verified":True,
            "art_visual_approved":False,"rig_ready":False,
            "originals_mutated":False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args()
    report=produce(ROOT,args.output_dir)
    tech=verify_report(ROOT,args.output_dir)
    print(json.dumps({
        "source_sha_count":3,
        "upper_hand_intersection":report["geometry_alpha"]["upper_hand"]["opaque_intersection_px"],
        "upper_hand_proximity_px":report["geometry_alpha"]["upper_hand"]["chebyshev_proximity_radius_px"],
        "lower_hand_intersection":report["geometry_alpha"]["lower_hand"]["opaque_intersection_px"],
        "qa":tech,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
