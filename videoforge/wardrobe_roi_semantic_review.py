"""Verifica revisão semântica da ROI V3 em separado do teste de bytes.

O código pode detectar metadados ausentes, hashes inconsistentes e decisões
indevidas; não substitui o olhar humano nem altera contrato de aprovação.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT,EPISODE

REVIEW="REVISAO-SEMANTICA-ROI-V3.json"
SOURCE="QA-ROI-EXCLUSOES-V3.json"
RESULT="QA-REVISAO-SEMANTICA-ROI-V3.json"
KEYS=[(a,r,s) for a,r in (
    ("aldric","barba"),("aldric","tecido_externo"),
    ("aldric","painel_central"),("elara","corpete_roxo_palacio")
) for s in ("a","b")]
FIELDS=("pose_identity_verified","garment_variant_verified",
        "correct_anatomical_region_verified","occlusion_review_verified",
        "lighting_difference_ruled_out")

def verify(root:Path=ROOT,sync:bool=False):
    ep=Path(root)/EPISODE
    files=[ep/REVIEW,ep/SOURCE]
    if any(x.is_symlink() or not x.is_file() for x in files):
        raise VideoForgeError("SEMANTIC_REVIEW_INPUT_UNSAFE")
    review=json.loads(files[0].read_text(encoding="utf-8"))
    candidate=json.loads(files[1].read_text(encoding="utf-8"))
    rows=review.get("rows",[])
    archived=candidate.get("results",[])
    if (review.get("schema")!="videoforge/wardrobe-v3-semantic-review/v1"
            or review.get("can_edit_official_contract") is not False
            or review.get("can_approve_r2") is not False
            or len(rows)!=8 or len(archived)!=8
            or [(x.get("actor"),x.get("region"),x.get("side")) for x in rows]!=KEYS
            or [(x.get("actor"),x.get("region"),x.get("side")) for x in archived]!=KEYS):
        raise VideoForgeError("SEMANTIC_REVIEW_CONTRACT_INVALID")
    validated=0
    output=[]
    for row,source in zip(rows,archived):
        if (row.get("source_sha256")!=source.get("source_sha256")
                or row.get("candidate_sha256")!=source.get("cleaned_candidate_sha256")):
            raise VideoForgeError("SEMANTIC_REVIEW_SOURCE_HASH_MISMATCH")
        values=[row.get(field) for field in FIELDS]
        if any(type(v) is not bool for v in values):
            raise VideoForgeError("SEMANTIC_REVIEW_INVALID_FLAGS")
        # Never infer an approval from a comment; affirmative review requires
        # evidence and named reviewer, but this QA still cannot approve R2.
        if row.get("status") not in ("EVIDENCIA_INSUFICIENTE","REVISAO_HUMANA_DOCUMENTADA"):
            raise VideoForgeError("SEMANTIC_REVIEW_STATUS_UNSAFE")
        if row["status"]=="REVISAO_HUMANA_DOCUMENTADA":
            if (not all(values)
                or not isinstance(row.get("human_reviewer"),str)
                or not row["human_reviewer"].strip()
                or not isinstance(row.get("review_evidence"),str)
                or not row["review_evidence"].strip()):
                raise VideoForgeError("SEMANTIC_REVIEW_EVIDENCE_REQUIRED")
            validated+=1
        elif row.get("human_reviewer") is not None or row.get("review_evidence") is not None:
            raise VideoForgeError("SEMANTIC_REVIEW_PARTIAL_EVIDENCE")
        output.append({
            "actor":row["actor"],"region":row["region"],"side":row["side"],
            "status":row["status"],"risk":row["risk"],
            "verified_source_sha256":row["source_sha256"],
            "verified_mask_sha256":row["candidate_sha256"],
            "ready_for_canonical_comparison":False,
        })
    result={
        "schema":"videoforge/roi-semantic-review-qa/v1",
        "status":"HUMAN_REVIEW_REQUIRED",
        "rows":output,
        "candidate_count":len(output),
        "documented_human_reviews":validated,
        "approved_canonical_pairs":0,
        "official_contract_unchanged":True,
        "known_owner_rejections_active":True,
        "r2_blocked":True,"provider_calls":0,
        "official_mp4":False,"youtube_uploaded":False,
    }
    if sync:
        out=ep/RESULT
        if out.is_symlink():raise VideoForgeError("SEMANTIC_REVIEW_OUTPUT_SYMLINK")
        blob=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
        if not out.exists() or out.read_text(encoding="utf-8")!=blob:
            out.write_text(blob,encoding="utf-8")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--sync",action="store_true")
    args=parser.parse_args()
    v=verify(sync=args.sync)
    print("SEMANTIC_REVIEW",json.dumps({
        "candidates":v["candidate_count"],
        "documented":v["documented_human_reviews"],
        "canonical_pairs":0,"r2_blocked":True,
    }))

if __name__=="__main__":
    main()
