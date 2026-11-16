"""Audit the real archived V2 identity reference without provider calls.

The report is technical/provenance evidence, NOT human visual approval.
Natural source dimensions are preserved; non-portrait reference never becomes
an approved mother scene automatically.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from .errors import VideoForgeError
from .production_art import archived_reference,read_plan,asset_prompt,ROOT
from .remake_autopilot import EPISODE

EP_CHANNEL="alchemy-lab"
EP_ID="mmorpg-conquiste-a-princesa-ep01"
ASSET_ID="character-bible"
QA_NAME="QA-CHARACTER-BIBLE-V2.json"


def inspect_reference(root:Path=ROOT) -> dict:
    root=Path(root)
    ref=archived_reference(EP_CHANNEL,EP_ID,ASSET_ID,root)
    if ref is None:
        return {
            "schema":"videoforge/reference-art-qa/v1",
            "status":"missing_reference",
            "requires_human_visual_review":True,
            "provider_calls":0,
            "youtube_uploaded":False,
        }
    plan,story=read_plan(EP_CHANNEL,EP_ID,root)
    _,expected=asset_prompt(plan,story,ASSET_ID)
    character_bible=plan.get("character_bible")
    if (not isinstance(character_bible,dict)
            or not all(isinstance(character_bible.get(c),str)
                       and character_bible[c].strip()
                       for c in ("kael","elara","aldric"))):
        raise VideoForgeError("REFERENCE_QA_CHARACTER_BRIEF_MISSING")
    target_width,target_height=[int(v) for v in expected.split("x")]
    sw,sh=ref["width"],ref["height"]
    scale=min(target_width/sw,target_height/sh)
    fit_w=min(target_width,round(sw*scale))
    fit_h=min(target_height,round(sh*scale))
    pad_x=target_width-fit_w
    pad_y=target_height-fit_h
    return {
        "schema":"videoforge/reference-art-qa/v1",
        "scope":EP_CHANNEL+"/"+EP_ID,
        "asset_id":ASSET_ID,
        "status":"technical_valid_human_identity_review_pending",
        "source":{
            "path":ref["path"],
            "run_id":ref["run_id"],
            "sha256":ref["sha256"],
            "width":sw,"height":sh,"bytes":ref["bytes"],
            "sha_verified":True,
            "png_structure_verified":True,
            "source_pixels_unmodified":True,
        },
        "requested_format":{
            "width":target_width,"height":target_height,
            "source_dimensions_match_requested":(sw,sh)==(target_width,target_height),
            "source_aspect_ratio":round(sw/sh,6),
            "target_aspect_ratio":round(target_width/target_height,6),
            "preview_only_contain_fit":{
                "scale":round(scale,8),"fit_width":fit_w,"fit_height":fit_h,
                "padding_left":pad_x//2,"padding_right":pad_x-pad_x//2,
                "padding_top":pad_y//2,"padding_bottom":pad_y-pad_y//2,
                "rendered":False,"pixels_resampled":False,
                "use":"layout guide only; do not deform original faces or bodies"
            },
        },
        "identity_review_criteria":{
            "kael":character_bible["kael"],
            "elara":character_bible["elara"],
            "aldric":character_bible["aldric"],
            "no_new_unplanned_characters":True,
            "no_text_watermarks_hud":True,
            "preserve_original_facial_features_and_outfits":True,
            "require_character_identity_comparison":True,
        },
        "generation_provenance_limits":{
            "generation_used_text_prompt_only":True,
            "approved_originals_attached_to_generation":False,
            "approved_reference_images_sha_imported_in_repo":
                not plan.get("remake_v2_20261115",{}).get("original_reference_sha_missing_in_repo",True),
            "claim_exact_original_identity_match":False,
            "cannot_approve_until_reference_comparison":True,
        },
        "human_review":{
            "approved":False,"kael_identity_verified":False,
            "elara_identity_verified":False,
            "aldric_identity_verified":False,
            "character_count_and_full_body_verified":False,
            "style_consistency_vs_previously_approved_art_verified":False,
            "anatomy_and_hand_artifacts_verified":False,
            "review_status":"not_reviewed",
        },
        "downstream":{
            "approved_canonical_anchor":False,
            "can_generate_shot_specific_mothers":False,
            "can_build_rig_from_this_sheet":False,
            "youtube_upload":False,
            "new_image_call_required_for_technical_qa":False,
        },
        "provider_calls":0,
    }


def sync_reference_report(root:Path=ROOT) -> dict:
    report=inspect_reference(root)
    if report["status"]=="missing_reference":
        return report
    episode=Path(root)/EPISODE
    path=episode/QA_NAME
    if path.is_symlink():
        raise VideoForgeError("REFERENCE_QA_TARGET_SYMLINK")
    serialized=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if not path.exists() or path.read_text(encoding="utf-8")!=serialized:
        path.write_text(serialized,encoding="utf-8")
        print("REFERENCE_QA_CHECKPOINT_UPDATED")
    else:
        print("REFERENCE_QA_CHECKPOINT_CURRENT")
    return report


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=sync_reference_report() if args.sync else inspect_reference()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("REFERENCE_ART_QA",json.dumps({
        "status":report["status"],
        "sha":report.get("source",{}).get("sha256"),
        "dimensions_match":report.get("requested_format",{}).get("source_dimensions_match_requested"),
        "provider_calls":0,"approval":False,
    }))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
