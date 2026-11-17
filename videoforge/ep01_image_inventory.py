"""Compute precise mother-shot coverage from immutable visual-bible registry.

No proxy calls. No claim that a generated PNG is human-approved or rig-ready.
Writers use the same registry that the permanent GitHub archive just updated.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from .errors import VideoForgeError

SCHEMA="videoforge/ep01-image-inventory-auto/v1"
ORIGINAL=re.compile(r"^(c\d\d-p\d\d)-scene-mother$")
SHOT=re.compile(r"^C\d\d-P\d\d$")
PROXY_DIR="/production-proxy-separate-part-v1/"
OUTPUT="CHECKPOINT-IMAGENS-EP01-AUTO.json"


def calculate(root:Path=ROOT)->dict:
    root=Path(root)
    plan_path=root/REL/"PLANO-CAMADAS-CAMERA-EP01.json"
    index_path=root/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json"
    try:
        plan=json.loads(plan_path.read_text(encoding="utf-8"))
        index=json.loads(index_path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError) as exc:
        raise VideoForgeError("EP01_INVENTORY_SOURCE_UNREADABLE") from exc
    if not isinstance(plan.get("shots"),list) or len(plan["shots"])!=40:
        raise VideoForgeError("EP01_INVENTORY_EXPECTED_40_SHOTS")
    expected=[x["id"] for x in plan["shots"] if x["id"]!="C01-P01"]
    if (len(expected)!=39 or len(expected)!=len(set(expected))
        or any(not SHOT.fullmatch(x) for x in expected)):
        raise VideoForgeError("EP01_INVENTORY_SHOT_PLAN_INVALID")
    originals={}
    for item in index.get("geracoes",[]):
        name=item.get("asset","")
        match=ORIGINAL.fullmatch(name)
        if not match:
            continue
        shot=match.group(1).upper()
        if shot not in expected:
            raise VideoForgeError("EP01_INVENTORY_UNKNOWN_SHOT "+shot)
        if shot in originals:
            raise VideoForgeError("EP01_INVENTORY_DUPLICATED_ORIGINAL "+shot)
        path=Path(item.get("arquivo",""))
        producer=REL/"assets"/"geracoes"/"production-scene-mother-v2"
        if path.is_absolute() or ".." in path.parts or not path.is_relative_to(producer):
            raise VideoForgeError("EP01_INVENTORY_SOURCE_NOT_CANONICAL "+shot)
        sha=item.get("sha256","")
        if not isinstance(sha,str) or not re.fullmatch(r"[0-9a-f]{64}",sha):
            raise VideoForgeError("EP01_INVENTORY_MOTHER_HASH_INVALID "+shot)
        file=root/path
        if file.is_symlink() or not file.is_file():
            raise VideoForgeError("EP01_INVENTORY_MOTHER_MISSING "+shot)
        originals[shot]={
            "sha256":sha,
            "file":path.as_posix(),
            "dimensions":[item.get("width"),item.get("height")],
            "human_visual_approval":False,
            "source_status":"archived_candidate_not_an_approved_scene"
        }
    candidates=[]
    independent=[]
    for item in index.get("geracoes",[]):
        n=item.get("asset","")
        file=str(item.get("arquivo",""))
        if PROXY_DIR in file:
            independent.append({
                "asset":n,"sha256":item.get("sha256"),
                "file":file,
                "human_visual_approval":False
            })
        if (re.match(r"^c\d\d-p\d\d-scene-mother-v\d+$",n)
            or re.match(r"^c\d\d-p\d\d-scene-mother-v\d+-native-aligned",n)
            or "scene-mother-contact" in n):
            candidates.append({
                "asset":n,"sha256":item.get("sha256"),
                "file":file,
                "human_visual_approval":False
            })
    missing=[shot for shot in expected if shot not in originals]
    result={
        "schema":SCHEMA,
        "channel":CHANNEL,
        "video_id":VIDEO,
        "shots_total":40,
        "black_shot":"C01-P01",
        "visual_shots":39,
        "visual_shots_with_original_mother":len(originals),
        "visual_shots_missing_original_mother":len(missing),
        "original_mother_shot_ids":[shot for shot in expected if shot in originals],
        "missing_original_mother_shot_ids":missing,
        "original_mothers":originals,
        "versioned_mother_candidates":candidates,
        "separate_proxy_generated_asset_count":len(independent),
        "separate_proxy_generated_assets":independent,
        "counts_are_generated_not_approved":True,
        "human_visual_approval":False,
        "rig_ready":False,
        "mp4_generated":False,
        "youtube_uploaded":False,
        "source_of_truth":"canal/alchemy-lab/biblia-visual/REGISTRO-GERACOES.json",
        "no_provider_calls":True
    }
    return result


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--write",action="store_true")
    args=p.parse_args()
    result=calculate()
    if args.write:
        dest=ROOT/REL/OUTPUT
        dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_INVENTORY",json.dumps({
        "mothers":result["visual_shots_with_original_mother"],
        "missing":result["visual_shots_missing_original_mother"],
        "proxy_separate":result["separate_proxy_generated_asset_count"],
        "human_approved":False
    },ensure_ascii=False))


if __name__=="__main__":
    main()
