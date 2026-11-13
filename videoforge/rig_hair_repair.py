"""Restore complete source hair and REUSE the previously approved blink pixels.

Never sends an AI request. The old closed-eye image was generated against the
same source and only changes eye RGB inside a narrow mask. Rebase that exact
pixel difference onto a freshly extracted full-hair head so no strands vanish.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from . import proxy_images, rig_candidate, rig_eye_ai, scene_layers
from .errors import VideoForgeError

SCHEMA="videoforge/full-hair-eye-rebase/v1"


class HairRepairError(VideoForgeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def restore(candidate_dir: Path, archived_eye_dir: Path,
            plan_path: Path, source_dir: Path) -> dict:
    plan=rig_candidate._load_json(plan_path)
    artifact=rig_candidate._load_json(source_dir/"manifest.json")
    rig=rig_candidate._load_json(candidate_dir/"rig.json")
    archive=rig_candidate._load_json(archived_eye_dir/"manifest.json")
    qa=rig_candidate._load_json(candidate_dir/"candidate.qa.json")
    provenance=rig_candidate._load_json(candidate_dir/"asset-provenance.json")

    identity=tuple(plan.get(k) for k in ("channel","video_id","scene"))
    for doc in (artifact,rig,archive):
        if tuple(doc.get(k) for k in ("channel","video_id","scene"))!=identity:
            raise HairRepairError("HAIR_REBASE_CROSS_CHANNEL")
    source_sha=artifact["source"]["sha256"]
    if (plan.get("source_sha256")!=source_sha or
        rig.get("source_sha256")!=source_sha or
        archive.get("source_sha256")!=source_sha or
        provenance.get("source_scene_sha256")!=source_sha):
        raise HairRepairError("HAIR_REBASE_SOURCE_SHA_MISMATCH")
    if (archive.get("schema")!="videoforge/original-eye-ai-archive/v1" or
        archive.get("human_review") is not False or
        archive.get("publishable") is not False or
        archive.get("model_calls_for_eye")!=1):
        raise HairRepairError("HAIR_REBASE_ARCHIVE_NOT_TRUSTED")
    if (qa.get("status")!="draft_unapproved" or
        qa.get("rig_ready_for_remotion") is not False or
        qa.get("human_visual_approval") is not False or
        rig.get("candidate_only") is not True or
        any(rig.get("human_review",{}).values())):
        raise HairRepairError("HAIR_REBASE_MUST_REMAIN_UNAPPROVED")
    coverage=qa.get("head_full_hair_guard_alpha_coverage")
    if (not isinstance(coverage,(int,float)) or coverage < .9998 or
        qa.get("head_mask_variant")!="head_full_polygon"):
        raise HairRepairError("HAIR_REBASE_HAIR_GUARD_FAILED")
    expected=archive.get("files_sha256",{})
    if set(expected)!={"head-open.png","head-closed-ai.png","face-closed-ai-reference.png"}:
        raise HairRepairError("HAIR_REBASE_ARCHIVE_ASSET_LIST_INVALID")

    width,height=artifact["source"]["width"],artifact["source"]["height"]
    old=[]
    for name in ("head-open.png","head-closed-ai.png"):
        file=archived_eye_dir/name
        data=scene_layers._read_png(file)
        if _sha(data)!=expected[name]:
            raise HairRepairError("HAIR_REBASE_ARCHIVE_HASH_INVALID")
        info=scene_layers.png_info(data,require_alpha=True)
        if (info["width"],info["height"])!=(width,height):
            raise HairRepairError("HAIR_REBASE_ARCHIVE_SIZE_INVALID")
        old.append(rig_candidate._image(file,width,height))

    now_path=candidate_dir/"head-open.png"
    current_bytes=scene_layers._read_png(now_path)
    if _sha(current_bytes)!=rig["assets"]["head-open.png"]:
        raise HairRepairError("HAIR_REBASE_CURRENT_HEAD_HASH_INVALID")
    current=rig_candidate._image(now_path,width,height)
    changed=bytearray(current)
    eye_regions=rig_eye_ai._eye_regions(plan)
    original_open,old_closed=old
    count=0
    for i in range(width*height):
        a=i*4
        if original_open[a:a+4]==old_closed[a:a+4]:
            continue
        x,y=i%width,i//width
        if rig_eye_ai._weight(x+.5,y+.5,eye_regions)<=0:
            raise HairRepairError("HAIR_REBASE_EDIT_OUTSIDE_EYE_MASK")
        if (original_open[a+3] != old_closed[a+3] or
            original_open[a+3] < 245):
            raise HairRepairError("HAIR_REBASE_EYE_ALPHA_CHANGED")
        if current[a:a+4]!=original_open[a:a+4]:
            raise HairRepairError("HAIR_REBASE_ORIGINAL_EYE_MISMATCH")
        changed[a:a+3]=old_closed[a:a+3]
        count+=1
    if not 100<=count<=12000:
        raise HairRepairError("HAIR_REBASE_EYE_CHANGE_COUNT_INVALID")

    target=candidate_dir/"head-closed-ai.png"
    if target.exists() or target.is_symlink():
        raise HairRepairError("HAIR_REBASE_NO_OVERWRITE")
    rig_candidate._write_png(target,changed,width,height)
    closed_sha=_sha(scene_layers._read_png(target))
    rig["assets"]["head-closed-ai.png"]=closed_sha
    # The new result is a rebase, not a new AI inference or an editorial approval.
    qa["eye_close_technique"]="original_masked_ai_edit_rebased_full_hair"
    qa["model_calls_for_eye"]=1
    qa["model_calls_for_this_repair"]=0
    qa["reused_eye_pixels"]=count
    qa["head_full_hair_guard_alpha_coverage"]=coverage
    qa["generated_eye_sha256"]=closed_sha
    qa["human_visual_approval"]=False
    qa["rig_ready_for_remotion"]=False
    qa["publishable"]=False
    provenance["model_calls"]=1
    provenance["eye_ai_edit"]={
        "schema":"videoforge/eye-ai-edit/v1",
        "human_review":False,"model_calls":1,
        "model_calls_in_this_repair":0,
        "source_sha256":source_sha,
        "original_eye_run_id":archive["source_run_id"],
        "original_closed_head_sha256":expected["head-closed-ai.png"],
        "closed_head_sha256":closed_sha,
        "all_pixels_outside_old_eye_mask_preserved":True,
        "full_hair_restored_from_character_main":True,
    }
    provenance["rebase_schema"]=SCHEMA
    for filename,doc in (
        ("rig.json",rig),
        ("candidate.qa.json",qa),
        ("asset-provenance.json",provenance),
    ):
        (candidate_dir/filename).write_text(
            json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {
        "schema":SCHEMA,"channel":identity[0],"video_id":identity[1],
        "scene":identity[2],"source_sha256":source_sha,
        "eye_edited_pixels_reused":count,
        "model_calls_in_this_repair":0,
        "hair_alpha_coverage":coverage,
        "head_closed_sha256":closed_sha,
        "review_required":True,"publishable":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description="Recuperar cabelo sem gerar novas imagens")
    parser.add_argument("--candidate-dir",type=Path,required=True)
    parser.add_argument("--archived-eye-dir",type=Path,required=True)
    parser.add_argument("--source-dir",type=Path,required=True)
    parser.add_argument("--plan",type=Path,required=True)
    args=parser.parse_args()
    try:
        print(json.dumps(restore(
            args.candidate_dir,args.archived_eye_dir,args.plan,args.source_dir
        ),ensure_ascii=False))
    except (HairRepairError,rig_candidate.CandidateError,
            scene_layers.LayerError,rig_eye_ai.EyeAIError,VideoForgeError) as e:
        print("RIG_HAIR_REPAIR_BLOCKED:",str(e),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
