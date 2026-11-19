"""Read-only edge alignment of a REAL proxy-generated C08-P02 image candidate.

The first background-clean call (run 44427271895) generated a full independent
image, 1054x1493 versus mother 1053x1493, then failed the strict canvas gate.
The bytes are permanently SHA-archived. Make a SEPARATE 1053x1493 candidate
by dropping only the final 1px column, no resize or image regeneration.
This does not approve the visual result, underlay or spatial placement.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops

from .ep01_continuity_motion import ROOT, EP, read as read_motion

RUN_ID=44427271895
PRODUCER="production-proxy-separate-part-v1"
STEM="c08-p02-background-clean"
ORIGINAL_REL=EP/"assets"/"geracoes"/PRODUCER/str(RUN_ID)/(STEM+".png")
META_REL=ORIGINAL_REL.with_suffix(".production.json")
OUTPUT_SIZE=(1053,1493)
PROVIDER_SIZE=(1054,1493)
PROVIDER_SHA="d1c40c69b65d3a59141ee1bf84135c4f9a5a470062441c855daaa4d52213d0ad"


def checked_source(root=ROOT):
    original=Path(root)/ORIGINAL_REL
    report=Path(root)/META_REL
    if any(p.is_symlink() or not p.is_file() for p in (original,report)):
        raise ValueError("Real generated source and evidence must exist in permanent archive")
    raw=original.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    meta=json.loads(report.read_text(encoding="utf-8"))
    mother=read_motion(root)["source_reference_shas"]["C08-P02"]
    if (digest != PROVIDER_SHA or meta.get("sha256")!=digest
            or meta.get("asset_id")!=STEM
            or meta.get("generation_method")!="proxy_generated_separate_image"
            or meta.get("not_a_pixel_cutout") is not True
            or meta.get("source_image_sha256")!=mother["sha256"]
            or meta.get("provider_image_calls")!=1
            or meta.get("human_visual_approval") is not False
            or meta.get("rig_ready") is not False
            or meta.get("width")!=PROVIDER_SIZE[0]
            or meta.get("height")!=PROVIDER_SIZE[1]
            or tuple(meta.get("source_canvas",[]))!=OUTPUT_SIZE):
        raise ValueError("Source provenance, bytes, or security gates changed")
    return original,meta


def align(root: Path, output_dir: Path) -> dict:
    root=Path(root).resolve()
    target=Path(output_dir)
    if (target.is_symlink() or target.resolve().is_relative_to(root)
            or target.exists() and any(target.iterdir())):
        raise ValueError("No writes into source repo, no overwrite of existing candidates")
    original,meta=checked_source(root)
    with Image.open(original) as img:
        img.load()
        if img.format!="PNG" or img.size!=PROVIDER_SIZE:
            raise ValueError("Native generated PNG dimensions changed")
        mode="RGBA" if "A" in img.getbands() else "RGB"
        native=img.convert(mode)
        aligned=native.crop((0,0,*OUTPUT_SIZE))
        # Explicit pixel-exact content test: no scaling, re-drawing, or shifting.
        if ImageChops.difference(aligned,native.crop((0,0,*OUTPUT_SIZE))).getbbox():
            raise ValueError("Edge alignment modified more than the extra column")
        source_right=native.crop((OUTPUT_SIZE[0],0,PROVIDER_SIZE[0],PROVIDER_SIZE[1]))
        removed_pixels=PROVIDER_SIZE[1]
        if source_right.size!=(1,PROVIDER_SIZE[1]):
            raise ValueError("Unexpected amount of edge removed")
        target.mkdir(parents=True,exist_ok=True)
        result=target/(STEM+"-one-column-aligned-UNAPPROVED.png")
        aligned.save(result,optimize=True)
        if Image.open(result).size!=OUTPUT_SIZE:
            raise ValueError("Aligned image not mother-sized")
    qa={
      "schema":"videoforge/ep01-c08-candidate-alignment/v1",
      "shot_id":"C08-P02","part":"background-clean",
      "source_run_id":RUN_ID,
      "source_generated_png":ORIGINAL_REL.as_posix(),
      "source_sha256":PROVIDER_SHA,
      "source_mother_sha256":meta["source_mother_sha256"],
      "aligned_candidate_png":result.name,
      "aligned_sha256":hashlib.sha256(result.read_bytes()).hexdigest(),
      "provider_dimensions":list(PROVIDER_SIZE),
      "mother_dimensions":list(OUTPUT_SIZE),
      "edge_columns_removed_right":1,"pixel_resampling":False,
      "pixel_translation":False,"original_provider_png_changed":False,
      "final_visual_alignment_approved":False,
      "hidden_background_geometry_verified":False,
      "independent_qa_completed":False,
      "rig_ready":False,"publishable":False,"youtube_publications":0,
      "new_provider_calls":0,"new_model_images":0,
      "status":"technical_canvas_candidate_requires_visual_QA",
    }
    (target/"alignment-qa.json").write_text(
        json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return qa


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    a=parser.parse_args()
    print(json.dumps(align(ROOT,a.output_dir),ensure_ascii=False))


if __name__=="__main__":
    main()
