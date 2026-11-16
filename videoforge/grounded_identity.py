"""Build a character-bible edit request from approved ORIGINAL PNG bytes.

Fixes the earlier TEXT-ONLY generated sheet: all image bytes are SHA-validated
and actually attached to /v1/images/edits. No HTTP, files, or provider calls
inside this module. The resulting art is still NOT automatically approved.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from .cinematic_chat_references import reference_status
from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE

ASSET_ID="character-bible-grounded"
EXPECTED={
    "kael":("ref-kael-close-c12",
            "assets/referencias/chat-aprovadas/kael-close-salao.png",
            "edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f"),
    "elara":("ref-elara-close-c12",
             "assets/referencias/chat-aprovadas/elara-close-trono.png",
             "bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a"),
}


def inputs(root:Path=ROOT)->list[dict]:
    root=Path(root)
    base=root/EPISODE
    status=reference_status(root)
    if status["original_source_files_sha_verified"]!=2:
        raise VideoForgeError("GROUNDED_IDENTITY_APPROVED_ORIGINALS_MISSING")
    rows={r.get("id"):r for r in status["samples"]}
    if len(rows)!=2 or set(rows)!={x[0] for x in EXPECTED.values()}:
        raise VideoForgeError("GROUNDED_IDENTITY_SOURCE_MANIFEST_INVALID")
    found=[]
    for actor,(source_id,rel,known_sha) in EXPECTED.items():
        row=rows[source_id]
        if (row.get("expected_repo_path")!=rel or
                row.get("expected_sha256")!=known_sha or
                row.get("source_original_verified") is not True):
            raise VideoForgeError("GROUNDED_IDENTITY_SOURCE_NOT_SHA_VERIFIED")
        path=base/rel
        if path.is_symlink() or not path.is_file() or path.stat().st_size>12_000_000:
            raise VideoForgeError("GROUNDED_IDENTITY_ORIGINAL_PATH_INVALID")
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=known_sha:
            raise VideoForgeError("GROUNDED_IDENTITY_ORIGINAL_SHA_CHANGED")
        # Integrity, dimensions and PNG color mode were already checked by
        # reference_status. Recheck signature to fail closed on changed bytes.
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise VideoForgeError("GROUNDED_IDENTITY_ORIGINAL_NOT_PNG")
        found.append({"actor":actor,"id":source_id,"path":rel,
                      "sha256":known_sha,"bytes":raw})
    return found


def edit_payload(prompt:str,model:str,size:str,
                 root:Path=ROOT)->tuple[dict,list[dict]]:
    if model!="gpt-image-2" or size!="1024x1536":
        raise VideoForgeError("GROUNDED_IDENTITY_MODEL_OR_SIZE_INVALID")
    if not isinstance(prompt,str) or not 150<=len(prompt)<=5000:
        raise VideoForgeError("GROUNDED_IDENTITY_PROMPT_INVALID")
    source=inputs(root)
    payload={
        "model":model,"prompt":prompt,
        "size":size,"n":1,"background":"opaque",
        "output_format":"png","response_format":"b64_json","stream":False,
        # gpt-image-2 does not accept input_fidelity in the official API.
        "images":[{"image_url":"data:image/png;base64,"+
                   base64.b64encode(s["bytes"]).decode("ascii")}
                  for s in source],
    }
    provenance=[{key:entry[key] for key in ("actor","id","path","sha256")}
                for entry in source]
    return payload,provenance
