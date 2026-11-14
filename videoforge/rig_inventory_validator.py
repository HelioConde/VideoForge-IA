"""Validação fail-closed dos assets já existentes para rigs Three/Remotion.

Somente leitura. Não gera PNG, chama API de IA ou renderiza vídeo.
Retorna inventário íntegro mesmo quando o rig ainda é BLOQUEADO.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
EXPECTED_SCHEMA="videoforge/rig-assets-inventory/v1"
PNG_HEADER=b"\x89PNG\r\n\x1a\n"

class RigInventoryError(ValueError):
    pass

def validate_file(root: Path, rel_path: str, sha256: str, require_rgba: bool=True) -> dict:
    if not isinstance(rel_path,str) or not rel_path or "\" in rel_path:
        raise RigInventoryError("UNSAFE_ASSET_PATH")
    relative=Path(rel_path)
    if relative.is_absolute() or ".." in relative.parts or relative.suffix!=".png":
        raise RigInventoryError("UNSAFE_ASSET_PATH")
    filepath=root/BASE/relative
    if filepath.is_symlink() or not filepath.is_file():
        raise RigInventoryError("ASSET_FILE_MISSING: "+rel_path)
    data=filepath.read_bytes()
    if len(data)<40 or data[:8]!=PNG_HEADER or data[12:16]!=b"IHDR":
        raise RigInventoryError("PNG_HEADER_INVALID: "+rel_path)
    if hashlib.sha256(data).hexdigest()!=sha256:
        raise RigInventoryError("ASSET_SHA_MISMATCH: "+rel_path)
    width,height=struct.unpack(">II",data[16:24])
    color_type=data[25]
    if (width,height)!=(1024,1536):
        raise RigInventoryError("ASSET_CANVAS_INVALID: "+rel_path)
    if require_rgba and color_type != 6:
        raise RigInventoryError("ASSET_RGBA_REQUIRED: "+rel_path)
    return {"path":rel_path,"sha256":sha256,"bytes":len(data),
            "color_type":color_type,"canvas":[width,height]}

def validate(root:Path=ROOT, source:Path|None=None)->dict:
    source=source or root/BASE/"rig-inventario-c01.json"
    if not source.is_file() or source.is_symlink():
        raise RigInventoryError("RIG_INVENTORY_MISSING")
    doc=json.loads(source.read_text(encoding="utf8"))
    if (doc.get("schema")!=EXPECTED_SCHEMA or doc.get("channel")!="alchemy-lab"
            or doc.get("video_id")!="mmorpg-conquiste-a-princesa-ep01"
            or doc.get("scene_id")!="C01" or doc.get("status")!="incomplete_blocked"):
        raise RigInventoryError("RIG_INVENTORY_CONTRACT_INVALID")
    mapping=doc["assetCoordinateSystem"]
    if mapping.get("width")!=1024 or mapping.get("height")!=1536:
        raise RigInventoryError("CANVAS_CONTRACT_INVALID")
    remap=mapping.get("toRender",{})
    if (remap.get("width"),remap.get("height"),remap.get("scaleNumerator"),
            remap.get("scaleDenominator"),remap.get("cropX"),remap.get("cropY"))!=(1080,1920,5,4,100,0):
        raise RigInventoryError("RENDER_COVER_CONTRACT_INVALID")
    checked=[]
    checked.append(validate_file(root,doc["sourceMother"]["path"],doc["sourceMother"]["sha256"],False))
    checked.append(validate_file(root,doc["reconstructedBackground"]["path"],doc["reconstructedBackground"]["sha256"],False))
    checked.append(validate_file(root,doc["kaelSource"]["path"],doc["kaelSource"]["sha256"],True))
    seen={v["path"] for v in checked}
    pieces=doc.get("kaelParts",[])+doc.get("otherParts",[])
    if len(doc.get("kaelParts",[]))<9 or len(doc.get("otherParts",[]))<5:
        raise RigInventoryError("RIG_NOT_ENOUGH_CANDIDATES")
    for entry in pieces:
        if entry.get("stage")=="approved" or entry.get("animated") is True:
            raise RigInventoryError("UNVERIFIED_RIG_APPROVAL")
        rel=entry.get("path") or entry.get("source")
        if rel in seen:
            raise RigInventoryError("DUPLICATED_RIG_ASSET: "+str(rel))
        seen.add(rel)
        checked.append(validate_file(root,rel,entry["sha256"],True))
    expected_grips={"lanca-guarda-esquerdo-CANDIDATE":[381,751],
                    "lanca-guarda-direito-CANDIDATE":[644,749]}
    for part in doc["otherParts"]:
        if part["id"] in expected_grips and part.get("pivotProvisionalXY")!=expected_grips[part["id"]]:
            raise RigInventoryError("SPEAR_GRIP_PIVOT_MISMATCH")
    gates=doc.get("globalGates")
    if not isinstance(gates,dict):
        raise RigInventoryError("MISSING_GATES")
    prohibited=("underlaysReconstructed","pivotsMeasured","guardArmRigged",
                "kingSpriteApproved","humanReview","renderOfficialAllowed")
    if any(gates.get(x) is True for x in prohibited):
        raise RigInventoryError("UNVERIFIED_READINESS_GATE")
    return {"schema":"videoforge/rig-inventory-qa/v1",
            "channel":doc["channel"],"video_id":doc["video_id"],
            "sourceMotherSHA256":doc["sourceMother"]["sha256"],
            "filesValidated":len(checked),"sha256AllValid":True,
            "piecesCandidateCount":len(pieces),
            "piecesRejectedCount":sum(x.get("stage")=="rejected" for x in pieces),
            "artworkGeneratedDuringQA":False,
            "globalGates":gates,
            "rigReady":False,"renderOfficialAllowed":False,
            "humanVisualApproved":False,"files":checked}

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--write-report",type=Path)
    x=p.parse_args()
    try:
        report=validate()
        if x.write_report:
            x.write_report.parent.mkdir(parents=True,exist_ok=True)
            x.write_report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        print("RIG_INVENTORY_SHA_OK",report["filesValidated"],"PNGs checked; rig=BLOCKED, no images generated")
        return 0
    except (RigInventoryError,OSError,ValueError,TypeError,KeyError) as e:
        print("RIG_INVENTORY_INVALID",str(e),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
