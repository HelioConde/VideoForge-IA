"""Owner wardrobe decisions outrank technical SHA. Never approve rejected art.

New R2 calls require actual SHA-verified, owner-approved full costume PNGs for
Elara and Aldric before a provider request is constructed.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from .errors import VideoForgeError

ROOT=Path(__file__).resolve().parents[1]
EPISODE=Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
REJECTED_SHA="6ed16d498df46b59c38e9c34ab25127b5b032159ab3289c073ac0058fcda6fc3"
SCOPE="alchemy-lab/mmorpg-conquiste-a-princesa-ep01"


def _read(root:Path,name:str)->dict:
    path=Path(root)/EPISODE/name
    if path.is_symlink() or not path.is_file() or path.stat().st_size>100_000:
        raise VideoForgeError("WARDROBE_REVIEW_OR_CONTRACT_MISSING")
    try:
        d=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError):
        raise VideoForgeError("WARDROBE_REVIEW_JSON_INVALID") from None
    if not isinstance(d,dict):
        raise VideoForgeError("WARDROBE_REVIEW_JSON_INVALID")
    return d


def owner_review(root:Path=ROOT)->tuple[dict,dict]:
    owner=_read(root,"REVISAO-FIGURINO-V2.json")
    contract=_read(root,"CONTRATO-FIGURINO-V2.json")
    if (owner.get("schema")!="videoforge/human-wardrobe-review/v1"
            or owner.get("scope")!=SCOPE or owner.get("sha256")!=REJECTED_SHA
            or owner.get("asset_id")!="character-bible-grounded"
            or owner.get("decision")!="rejected_wardrobe_inconsistency"
            or owner.get("human_visual_approved") is not False
            or owner.get("canonical_identity_approved") is not False
            or contract.get("schema")!="videoforge/wardrobe-continuity-contract/v1"
            or contract.get("scope")!=SCOPE
            or contract.get("rejected_candidate_sha256")!=REJECTED_SHA
            or contract.get("decision")!="rejected_wardrobe_inconsistency"
            or contract.get("canonical_identity_approved") is not False):
        raise VideoForgeError("WARDROBE_OWNER_REJECTION_INVALID")
    issues={x.get("code") for x in owner.get("issues",[]) if isinstance(x,dict)}
    if not {"wardrobe_mismatch_aldric",
            "wardrobe_mismatch_elara_purple_bodice"}<=issues:
        raise VideoForgeError("WARDROBE_REJECTION_ISSUES_MISSING")
    refs=contract.get("required_full_wardrobe_reference_sources")
    if (not isinstance(refs,list) or len(refs)!=2
            or {x.get("actor") for x in refs if isinstance(x,dict)}!={"elara","aldric"}):
        raise VideoForgeError("WARDROBE_FULL_OUTFIT_SOURCES_INVALID")
    return owner,contract


def rejected_reference_sha(value:object,root:Path=ROOT)->bool:
    if not isinstance(value,str) or value!=REJECTED_SHA:
        return False
    owner_review(root)
    return True


def source_readiness(root:Path=ROOT)->dict:
    _,contract=owner_review(root)
    base=Path(root)/EPISODE
    rows=[]
    for spec in contract["required_full_wardrobe_reference_sources"]:
        path=spec.get("path")
        digest=spec.get("sha256")
        consent=spec.get("explicit_owner_approved") is True
        ok=False
        if (isinstance(path,str)
                and path.startswith("assets/referencias/figurinos-aprovados/")
                and "\\" not in path and ".." not in Path(path).parts
                and isinstance(digest,str) and len(digest)==64
                and all(x in "0123456789abcdef" for x in digest) and consent):
            file=base/path
            if file.is_file() and not file.is_symlink() and file.stat().st_size<=12_000_000:
                raw=file.read_bytes()
                ok=raw.startswith(b"\x89PNG\r\n\x1a\n") and hashlib.sha256(raw).hexdigest()==digest
        rows.append({"actor":spec.get("actor"),"path":path,"sha256":digest,
                     "explicit_owner_approved":consent,"sha_verified":ok})
    return {
        "schema":"videoforge/wardrobe-readiness/v1",
        "status":"ready_for_r2_request" if all(x["sha_verified"] for x in rows)
                else "awaiting_approved_full_wardrobe_sources",
        "stage":"collect_or_lock_better_wardrobe_references",
        "verified":sum(x["sha_verified"] for x in rows),
        "required":2,"sources":rows,
        "r2_ready":all(x["sha_verified"] for x in rows),
        "human_visual_approved":False,
        "provider_calls":0,
    }


def r2_edit_payload(prompt:str,model:str,size:str,root:Path=ROOT)->tuple[dict,list[dict]]:
    if (model!="gpt-image-2" or size!="1024x1536"
            or not isinstance(prompt,str) or not 150<=len(prompt)<=5000):
        raise VideoForgeError("WARDROBE_R2_MODEL_OR_PROMPT_INVALID")
    status=source_readiness(root)
    if not status["r2_ready"]:
        raise VideoForgeError("WARDROBE_R2_SOURCES_NOT_OWNER_APPROVED_AND_SHA_VERIFIED")
    from .grounded_identity import inputs
    sources=list(inputs(root))
    base=Path(root)/EPISODE
    for row in status["sources"]:
        raw=(base/row["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row["sha256"]:
            raise VideoForgeError("WARDROBE_R2_SOURCE_CHANGED")
        sources.append({
            "actor":row["actor"]+"_outfit",
            "id":row["actor"]+"_approved_full_outfit",
            "path":row["path"],"sha256":row["sha256"],"bytes":raw,
        })
    payload={
        "model":model,"prompt":prompt,"n":1,"size":size,
        "background":"opaque","output_format":"png",
        "response_format":"b64_json","stream":False,
        "images":[{"image_url":"data:image/png;base64,"+
                   base64.b64encode(x["bytes"]).decode("ascii")} for x in sources],
    }
    proof=[{k:row[k] for k in ("actor","id","path","sha256")} for row in sources]
    return payload,proof
