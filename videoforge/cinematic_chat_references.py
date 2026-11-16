"""Verify user-liked cinematic Kael and Elara source PNGs, without creating art.

The approved chat images are 941x1672 RGB, not the old 1024x1536
scene mothers. Matching their SHA only verifies source integrity; it never
approves rigs, underlays, continuity in all 37 shots, or a final render.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

from .cinematic_direction import ROOT
from .errors import VideoForgeError

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"
MANIFEST="referencias-cinematograficas-aprovadas-no-chat.json"
QA_OUTPUT="qa-referencias-chat-cinematograficas.json"
PNG_SIGNATURE=b"\x89PNG\r\n\x1a\n"
HEX64=re.compile(r"^[0-9a-f]{64}$")
SOURCE_DIR="assets/referencias/chat-aprovadas/"

def check_png_source(data:bytes,width:int,height:int,expected_sha:str,
                     expected_length:int)->list[str]:
    """PNG/header/SHA verification, pure bytes; no Pillow, no writing files."""
    errors=[]
    if not isinstance(data,bytes):
        raise VideoForgeError("CINEMATIC_REFERENCE_NOT_BYTES")
    if len(data)!=expected_length or len(data)>15_000_000:
        errors.append("UNEXPECTED_FILE_SIZE")
    if not HEX64.fullmatch(expected_sha) or hashlib.sha256(data).hexdigest()!=expected_sha:
        errors.append("SHA256_MISMATCH")
    # IDHR chunk is the first chunk in PNG.
    if (len(data)<45 or data[:8]!=PNG_SIGNATURE
            or data[12:16]!=b"IHDR"
            or int.from_bytes(data[8:12],"big")!=13):
        errors.append("NOT_PNG_IHDR")
        return errors
    dims=[int.from_bytes(data[16:20],"big"),int.from_bytes(data[20:24],"big")]
    if dims!=[width,height]:
        errors.append("DIMENSIONS_MISMATCH")
    if data[24]!=8 or data[25]!=2:  # RGB (not RGBA / indexed)
        errors.append("PNG_COLOR_MODE_MISMATCH")
    if data[26]!=0 or data[27]!=0 or data[28]!=0:
        errors.append("PNG_IHDR_METHOD_MISMATCH")
    if (zlib.crc32(data[12:29]) & 0xffffffff)!=int.from_bytes(data[29:33],"big"):
        errors.append("PNG_IHDR_CRC_MISMATCH")
    if data[-8:-4]!=b"IEND" or len(data[-12:])!=12:
        errors.append("PNG_IEND_MISSING")
    return errors

def camera_candidate_status(base:Path)->dict:
    """Third shot candidate is not a canonical character reference or rig."""
    spec=base/"candidato-camera-c12-p02.json"
    if spec.is_symlink() or not spec.is_file():
        raise VideoForgeError("CINEMATIC_C12_CAMERA_CANDIDATE_MANIFEST_MISSING")
    d=json.loads(spec.read_text(encoding="utf8"))
    rel=d.get("expected_repo_path")
    if (d.get("shot_id")!="C12-P02" or
            rel!="assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png" or
            d.get("source_sha256")!="01eb7c127b0699d2e502d29dacec0bb39c0e1e23bf8205fdcf6fb70976e70535"):
        raise VideoForgeError("CINEMATIC_C12_CAMERA_MANIFEST_MISMATCH")
    path=base/rel
    if any(parent.is_symlink() for parent in (path,*path.parents) if parent!=base.parent):
        raise VideoForgeError("CINEMATIC_C12_CAMERA_SOURCE_SYMLINK")
    if path.is_file():
        data=path.read_bytes()
        errors=check_png_source(data,d["original_width_px"],
                                d["original_height_px"],
                                d["source_sha256"],d["original_bytes"])
        state="EXACT_SOURCE_ARCHIVED" if not errors else "INVALID_SOURCE_BYTES"
    else:
        errors=["SOURCE_FILE_NOT_UPLOADED"]
        state="UPLOAD_PENDING"
    return {
        "shot_id":"C12-P02",
        "status":state,
        "expected_repo_path":rel,
        "expected_sha256":d["source_sha256"],
        "source_verified":state=="EXACT_SOURCE_ARCHIVED",
        "human_shot_approval":False,
        "shot_mother_approval":False,
        "rig_approved":False,
        "issues":errors,
    }

def reference_status(root:Path=ROOT)->dict:
    base=root/"canal"/CHANNEL/"videos"/VIDEO
    manifest_file=base/MANIFEST
    if manifest_file.is_symlink() or not manifest_file.is_file():
        raise VideoForgeError("CINEMATIC_CHAT_REFERENCE_MANIFEST_MISSING")
    if manifest_file.stat().st_size>80_000:
        raise VideoForgeError("CINEMATIC_CHAT_REFERENCE_MANIFEST_OVERSIZE")
    doc=json.loads(manifest_file.read_text(encoding="utf8"))
    if (doc.get("schema")!="videoforge/chat-approved-cinematic-style-reference/v1"
            or doc.get("channel")!=CHANNEL or doc.get("video_id")!=VIDEO
            or doc.get("image_generation_allowed") is not False):
        raise VideoForgeError("CINEMATIC_CHAT_REFERENCE_MANIFEST_INVALID")
    samples=doc.get("approved_samples")
    if (not isinstance(samples,list) or len(samples)!=2
            or {x.get("id") for x in samples}!={"ref-kael-close-c12","ref-elara-close-c12"}):
        raise VideoForgeError("CINEMATIC_CHAT_REFERENCE_EXPECTED_TWO_SAMPLES")
    # The historic 2026-11-14 image-generation lock was archived for EP01 V2.
    # This source-import QA never calls a generator; it MUST NOT resurrect that
    # obsolete lock or mistake a style-reference-only v1 flag for v2 policy.
    state_file=base/"estado-atual.json"
    policy_file=base/"autonomy-policy.json"
    historic=base/"REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md"
    if (any(p.is_symlink() or not p.is_file()
            for p in (state_file,policy_file,historic)) or
            (base/"SEM-GERACAO-NOVAS-IMAGENS.lock").exists()):
        raise VideoForgeError("CINEMATIC_REFERENCE_ACTIVE_POLICY_OR_HISTORY_INVALID")
    state=json.loads(state_file.read_text(encoding="utf8"))
    policy=json.loads(policy_file.read_text(encoding="utf8"))
    if (state.get("active_production_version")!="remake-v2-20261115"
            or state.get("locks",{}).get("no_new_image_generation") is not False
            or state.get("locks",{}).get("no_youtube_upload") is not True
            or policy.get("scope")!="alchemy-lab/mmorpg-conquiste-a-princesa-ep01"
            or policy.get("standing_user_authorization",{}).get("per_call_reapproval_required") is not False
            or policy.get("auto_publish_youtube") is not False):
        raise VideoForgeError("CINEMATIC_REFERENCE_ACTIVE_REMAKE_V2_POLICY_INVALID")
    rows=[]
    seen=set()
    for item in samples:
        rel=item["expected_repo_path"]
        if (not isinstance(rel,str) or not rel.startswith(SOURCE_DIR)
                or "\\" in rel or ".." in Path(rel).parts
                or Path(rel).is_absolute() or not rel.endswith(".png")
                or rel in seen):
            raise VideoForgeError("CINEMATIC_CHAT_REFERENCE_UNSAFE_OR_DUPLICATE_PATH")
        seen.add(rel)
        path=base/rel
        for ancestor in (path,*path.parents):
            if ancestor.is_symlink():
                raise VideoForgeError("CINEMATIC_CHAT_REFERENCE_SYMLINK_BLOCKED")
            if ancestor==base:
                break
        if path.is_file():
            size=path.stat().st_size
            if size>15_000_000:
                issues=["FILE_TOO_LARGE"]
            else:
                issues=check_png_source(
                    path.read_bytes(),*item["dimensions_px"],
                    item["original_sha256"],item["expected_bytes"]
                )
            status="ORIGINAL_EXACT_SHA_VERIFIED" if not issues else "WRONG_ORIGINAL_BYTES"
        else:
            issues=["SOURCE_FILE_NOT_UPLOADED"]
            status="UPLOAD_PENDING"
        rows.append({
            "id":item["id"],
            "expected_repo_path":rel,
            "expected_sha256":item["original_sha256"],
            "expected_bytes":item["expected_bytes"],
            "expected_dimensions_px":item["dimensions_px"],
            "status":status,
            "issues":issues,
            "source_original_verified":status=="ORIGINAL_EXACT_SHA_VERIFIED",
            "approved_for_shot_mother":False,
            "approved_as_rig":False,
        })
    verified=sum(x["source_original_verified"] for x in rows)
    if any(x["status"]=="WRONG_ORIGINAL_BYTES" for x in rows):
        result="BLOCKED_INVALID_REFERENCE_BYTES"
    elif verified==2:
        result="TWO_CHAT_STYLE_SOURCES_ARCHIVED"
    elif verified==1:
        result="ONE_SOURCE_PENDING"
    else:
        result="BOTH_SOURCE_FILES_PENDING_UPLOAD"
    return {
        "schema":"videoforge/chat-approved-cinematic-source-readiness/v1",
        "channel":CHANNEL,
        "video_id":VIDEO,
        "feedback":"O estilo visual mostrado no chat recebeu aprovação estética; não significa aprovação de rigs.",
        "import_read_only":True,
        "legacy_image_generation_lock_archived":True,
        "active_remake_version":"remake-v2-20261115",
        "active_remake_standing_generation_policy_unchanged":True,
        "status":result,
        "preferred_style_confirmed":True,
        "original_source_files_sha_verified":verified,
        "original_source_files_total":2,
        "source_has_final_9_16_aspect_not_old_2_3":True,
        "new_image_generation_calls":0,
        "generated_or_modified_pixels":0,
        "official_character_bible_updated":False,
        "official_37_shots_approved":False,
        "shot_independent_mothers_approved":False,
        "render_official_allowed":False,
        "youtube_uploaded":False,
        "samples":rows,
        "camera_candidate_C12_P02":camera_candidate_status(base),
        "next_action":(
            "Comparar visualmente Kael e Elara com a prancha V2 arquivada; "
            "verificar Aldric em fonte separada. SHA correto NAO aprova identidade/rig."
            if verified==2 and camera_candidate_status(base)["source_verified"]
            else "Importar PNGs originais exatos por SHA; nenhuma aprovacao automatica."
        ),
    }

def main()->int:
    p=argparse.ArgumentParser(description="Verificar 2 imagens aprovadas do chat por SHA, sem gerar PNG")
    p.add_argument("--report",action="store_true")
    a=p.parse_args()
    try:
        doc=reference_status()
        content=json.dumps(doc,ensure_ascii=False,indent=2)+"\n"
        if a.report:
            dest=ROOT/"canal"/CHANNEL/"videos"/VIDEO/QA_OUTPUT
            if dest.is_symlink():
                raise VideoForgeError("CINEMATIC_REFERENCE_REPORT_SYMLINK")
            if not dest.exists() or dest.read_text(encoding="utf8")!=content:
                dest.write_text(content,encoding="utf8")
        print("CINEMATIC_CHAT_REFERENCE_QA",json.dumps({
            "status":doc["status"],"verified":doc["original_source_files_sha_verified"],
            "images_generated":0,"official_render_allowed":False
        },ensure_ascii=False))
        return 2 if doc["status"]=="BLOCKED_INVALID_REFERENCE_BYTES" else 0
    except (VideoForgeError,OSError,ValueError,KeyError,TypeError) as exc:
        print("CINEMATIC_CHAT_REFERENCE_QA_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
