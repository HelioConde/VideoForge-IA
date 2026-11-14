"""Fingerprint the three approved *existing* references, without image output.

Does NOT generate/resize/save images. The 188x334 thumbnail exists only in
memory. SHA-256 remains the hard integrity gate; palette and dHash are
descriptive and never grant character/shot/rig approval.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import sys

from .cinematic_direction import ROOT
from .errors import VideoForgeError

EPISODE="canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
BASELINE="fingerprints-visuais-referencias.json"
REPORT="qa-fingerprints-referencias.json"
HEX=re.compile(r"^[0-9a-f]{64}$")
HEX16=re.compile(r"^[0-9a-f]{16}$")
EXPECTED_IDS={"kael","elara","c12-p02"}

def get_manifest(root:Path=ROOT)->dict:
    p=root/EPISODE/BASELINE
    if not p.is_file() or p.is_symlink() or p.stat().st_size>32_000:
        raise VideoForgeError("CINEMATIC_FINGERPRINT_BASELINE_MISSING")
    d=json.loads(p.read_text(encoding="utf8"))
    sources=d.get("originals")
    if (d.get("schema")!="videoforge/cinematic-reference-visual-signature/v1"
            or not isinstance(sources,list) or len(sources)!=3
            or {x.get("id") for x in sources}!=EXPECTED_IDS
            or d.get("art_generated") is not False):
        raise VideoForgeError("CINEMATIC_FINGERPRINT_BASELINE_INVALID")
    for s in sources:
        if (s.get("dimensions")!=[941,1672]
                or s.get("mode")!="RGB"
                or not isinstance(s.get("sha256"),str)
                or not HEX.fullmatch(s["sha256"])
                or not isinstance(s.get("dhash64"),str)
                or not HEX16.fullmatch(s["dhash64"])):
            raise VideoForgeError("CINEMATIC_FINGERPRINT_RECORD_INVALID")
    return d

def dhash_rgb(original_bytes:bytes)->dict:
    """Read source bytes and compute visual metrics on tiny in-memory sample."""
    try:
        from PIL import Image
    except ImportError as exc:
        raise VideoForgeError("CINEMATIC_FINGERPRINT_PILLOW_REQUIRED") from exc
    try:
        with Image.open(io.BytesIO(original_bytes)) as image:
            image.load()
            if image.format!="PNG" or image.mode!="RGB":
                raise VideoForgeError("CINEMATIC_FINGERPRINT_EXPECTED_RGB_PNG")
            width,height=image.size
            thumb=image.convert("L").resize((9,8),Image.Resampling.BOX)
            px=list(thumb.getdata())
            bitset=0
            for y in range(8):
                for x in range(8):
                    bitset=(bitset<<1)|int(px[y*9+x]>px[y*9+x+1])
            small=image.resize((188,334),Image.Resampling.BOX)
            values=small.convert("L").histogram()
            n=sum(values)
            return {
                "dimensions":[width,height],
                "mode":"RGB",
                "dhash64":f"{bitset:016x}",
                "darkPercent":round(100*sum(values[:52])/n,1),
                "brightPercent":round(100*sum(values[205:])/n,1),
            }
    except OSError as exc:
        raise VideoForgeError("CINEMATIC_FINGERPRINT_UNREADABLE_PNG") from exc

def audit(root:Path=ROOT)->dict:
    baseline=get_manifest(root)
    base=root/EPISODE
    entries=[]
    for item in baseline["originals"]:
        rel=item["file"]
        if (not isinstance(rel,str)
                or not rel.startswith("assets/referencias/chat-aprovadas/")
                or "\\" in rel or ".." in Path(rel).parts
                or Path(rel).is_absolute() or not rel.endswith(".png")):
            raise VideoForgeError("CINEMATIC_FINGERPRINT_UNSAFE_SOURCE_PATH")
        candidate=base/rel
        if any(p.is_symlink() for p in (candidate,*candidate.parents) if p!=base.parent):
            raise VideoForgeError("CINEMATIC_FINGERPRINT_SYMLINK_BLOCKED")
        if not candidate.is_file():
            entries.append({
                "id":item["id"],"path":rel,
                "status":"ORIGINAL_NOT_IN_GITHUB",
                "sha256Verified":False,
                "dhashMeasured":False,
                "productionRigApproved":False,
            })
            continue
        if candidate.stat().st_size>10_000_000:
            raise VideoForgeError("CINEMATIC_FINGERPRINT_SOURCE_OVERSIZE")
        original=candidate.read_bytes()
        if sha256(original).hexdigest()!=item["sha256"]:
            raise VideoForgeError("CINEMATIC_FINGERPRINT_ORIGINAL_SHA_INVALID:"+item["id"])
        found=dhash_rgb(original)
        if found["dimensions"]!=item["dimensions"]:
            raise VideoForgeError("CINEMATIC_FINGERPRINT_DIMENSIONS_CHANGED")
        # Perceptual signature is an advisory cross-check only. SHA is exact.
        distance=(int(found["dhash64"],16)^int(item["dhash64"],16)).bit_count()
        entries.append({
            "id":item["id"],"path":rel,
            "status":"EXACT_ORIGINAL_SHA_CONFIRMED",
            "sha256Verified":True,
            "dhashMeasured":True,
            "dhash64":found["dhash64"],
            "distanceFromBaseline":distance,
            "darkPercent":found["darkPercent"],
            "brightPercent":found["brightPercent"],
            "productionRigApproved":False,
        })
    return {
        "schema":"videoforge/cinematic-reference-visual-readiness/v1",
        "channel":"alchemy-lab","video_id":"mmorpg-conquiste-a-princesa-ep01",
        "baseline":BASELINE,
        "originalCount":3,
        "exactShaVerifiedCount":sum(x["sha256Verified"] for x in entries),
        "imageGenerationCalls":0,"newImageFilesCreated":0,
        "originalPixelsModified":False,
        "referenceStyleRecorded":True,
        "rigOrShotHumanApproved":False,
        "officialRenderAllowed":False,
        "status":"THREE_ORIGINALS_ARCHIVED" if all(x["sha256Verified"] for x in entries)
            else "AWAITING_ORIGINAL_BINARY_TRANSFER",
        "notes":[
            "dHash/palette do NOT recognize the actor's identity and cannot substitute human QA",
            "Original RGB photographs cannot themselves provide transparent eye/face rigs",
            "Source must match exact SHA-256; converting/resizing a picture changes its original",
        ],
        "entries":entries,
    }

def main()->int:
    parser=argparse.ArgumentParser(description="Fingerprint originals read-only; no generated images")
    parser.add_argument("--report",action="store_true")
    opts=parser.parse_args()
    try:
        result=audit()
        if opts.report:
            out=ROOT/EPISODE/REPORT
            if out.is_symlink():
                raise VideoForgeError("CINEMATIC_FINGERPRINT_REPORT_SYMLINK_BLOCKED")
            payload=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
            if not out.exists() or out.read_text(encoding="utf8")!=payload:
                out.write_text(payload,encoding="utf8")
        print("CINEMATIC_FINGERPRINT_AUDIT",json.dumps({
            "status":result["status"],
            "exactShaVerified":result["exactShaVerifiedCount"],
            "imageGenerationCalls":0,
        }))
        return 0
    except (OSError,ValueError,KeyError,TypeError,VideoForgeError) as err:
        print("CINEMATIC_FINGERPRINT_BLOCKED",str(err),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
