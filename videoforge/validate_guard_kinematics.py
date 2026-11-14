"""QA fail-closed do pré-rig dos guardas (SEM gerar imagens).

Verifica PNG/SHA, hierarquia de ossos, contato das mãos com as duas
lanças, alfa nos cruzamentos e exige bloqueio das rotações enquanto
faltarem áreas ocultas, QA visual ou pivôs medidos.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"
SOURCE=BASE/"rig-guardas-articulacoes-c01.json"
REPORT=BASE/"qa-guardas-articulacoes-c01.json"
ALPHA_THRESHOLD=128

class GuardRigValidationError(ValueError): pass

def count_contact(img_a:Image.Image,img_b:Image.Image)->int:
    a=img_a.getchannel("A").point(lambda x:255 if x>=ALPHA_THRESHOLD else 0)
    b=img_b.getchannel("A").point(lambda x:255 if x>=ALPHA_THRESHOLD else 0)
    overlap=ImageChops.multiply(a,b)
    return overlap.histogram()[255]

def verified_rgba(relative:str,expected_sha:str)->Image.Image:
    p=Path(relative)
    if not relative or p.suffix!=".png" or p.is_absolute() or ".." in p.parts:
        raise GuardRigValidationError("BAD_RELATIVE_PNG_PATH")
    target=BASE/p
    if not target.is_file() or target.is_symlink():
        raise GuardRigValidationError("PNG_NOT_FOUND:"+relative)
    raw=target.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha:
        raise GuardRigValidationError("PNG_SOURCE_SHA_MISMATCH:"+relative)
    if not raw.startswith(bytes((137,80,78,71,13,10,26,10))) or raw[12:16]!=b"IHDR":
        raise GuardRigValidationError("BAD_PNG_HEADER")
    if struct.unpack(">II",raw[16:24])!=(1024,1536) or raw[25]!=6:
        raise GuardRigValidationError("PNG_NOT_1024_1536_RGBA")
    with Image.open(target) as image:
        if image.mode!="RGBA":
            raise GuardRigValidationError("PNG_NOT_RGBA")
        return image.copy()

def audit()->dict:
    if REPORT.exists():
        raise GuardRigValidationError("QA_REPORT_ALREADY_EXISTS")
    if not (BASE/"SEM-GERACAO-NOVAS-IMAGENS.lock").is_file():
        raise GuardRigValidationError("USER_IMAGE_GENERATION_LOCK_MISSING")
    doc=json.loads(SOURCE.read_text(encoding="utf8"))
    if doc.get("schema")!="videoforge/guard-rig-draft-kinematics/v1" or doc.get("status")!="DRAFT_BLOCKED":
        raise GuardRigValidationError("GUARD_RIG_SCHEMA_OR_STATUS_INVALID")
    if doc.get("generativeImageCalls")!=0 or doc.get("fps")!=30 or doc.get("range")!=[240,360]:
        raise GuardRigValidationError("GUARD_RIG_TIME_AND_POLICY_INVALID")
    if doc.get("worldToRender",{}).get("scale")!=1.25 or doc.get("worldToRender",{}).get("cropX")!=100:
        raise GuardRigValidationError("GUARD_RIG_COORDINATES_INVALID")
    if not doc["hardGates"].get("animation_or_render_allowed") is False:
        raise GuardRigValidationError("GUARD_RIG_UNSAFE_RENDER_ENABLED")
    expected_parts=("body-remainder","upper-arm","forearm","gripping-hand")
    records=[]
    names=set()
    for guard in doc.get("rigRoots",[]):
        name=guard.get("id")
        if name in names or name not in ("guarda-esquerdo","guarda-direito"):
            raise GuardRigValidationError("INVALID_GUARD_NAME")
        names.add(name)
        parts=guard.get("parts",[])
        if tuple(x.get("id") for x in parts)!=expected_parts:
            raise GuardRigValidationError("UNEXPECTED_GUARD_PART_HIERARCHY:"+name)
        constraints=guard.get("parentHierarchy",[])
        if len(constraints)!=5 or constraints[-1].get("node")!=guard["weapon"]["id"]:
            raise GuardRigValidationError("MISSING_SPEAR_HAND_ATTACHMENT:"+name)
        if guard["weapon"].get("allowedIndependentRotation") is not False:
            raise GuardRigValidationError("ILLEGAL_SPEAR_INDEPENDENT_ROTATION")
        if guard["weapon"].get("underlaysReady") is True or guard["flags"].get("armMotionReady") is True:
            raise GuardRigValidationError("UNVERIFIED_ARM_MOTION_READY")
        loaded={}
        for part in parts:
            if part.get("motionMinDegrees")!=0 or part.get("motionMaxDegrees")!=0 or part.get("pivotApproved") is not False:
                raise GuardRigValidationError("UNAPPROVED_JOINT_MOVEMENT_ENABLED")
            loaded[part["id"]]=verified_rgba(part["png"],part["sha256"])
        spear=verified_rgba(guard["weapon"]["png"],guard["weapon"]["sha256"])
        counts={}
        for segment in ("upper-arm","forearm","gripping-hand"):
            detected=count_contact(loaded[segment],spear)
            defined=next(p["spearOverlapPixels"] for p in parts if p["id"]==segment)
            if defined!=detected:
                raise GuardRigValidationError("SPEAR_CONTACT_MISMATCH:"+name+"/"+segment)
            counts[segment]=detected
        if guard["weapon"]["sourceOverlapAtHand"]!=counts["gripping-hand"]:
            raise GuardRigValidationError("HAND_CONTACT_NOT_BOUND_TO_SPEAR:"+name)
        if counts["gripping-hand"]<=0:
            raise GuardRigValidationError("SPEAR_GRIP_DOES_NOT_OVERLAP_HAND:"+name)
        records.append({"id":name,
                        "partCount":len(parts),
                        "shaValidatedPNGCount":len(parts)+1,
                        "handSpearOverlapPixels":counts["gripping-hand"],
                        "forearmSpearOverlapPixels":counts["forearm"],
                        "neutralPoseVerifiedBySourceQA":guard["flags"]["neutralSourcePixelRoundtrip"],
                        "shoulder":guard["jointCoordinates"]["shoulder"],
                        "elbow":guard["jointCoordinates"]["elbow"],
                        "wrist":guard["jointCoordinates"]["wrist"],
                        "spearGrip":guard["jointCoordinates"]["handContact"],
                        "allMotionDisabled":True,
                        "underlaysRequired":True})
    if names!={"guarda-esquerdo","guarda-direito"}:
        raise GuardRigValidationError("MISSING_GUARD_RIG")
    report={
        "schema":"videoforge/guard-rig-readiness-audit/v1",
        "channel":"alchemy-lab",
        "video_id":"mmorpg-conquiste-a-princesa-ep01",
        "shot":"C01-P04",
        "fps":30,
        "sourceScenePose":"spears_already_crossed",
        "verifiedPNGCount":sum(x["shaValidatedPNGCount"] for x in records),
        "motionFrames":[240,245,280,326,359],
        "spearContacts":records,
        "artGenerationCalls":0,
        "visualHumanApproved":False,
        "underlaysReconstructed":False,
        "pivotMeasured":False,
        "guardArmsPhysicallyRigged":False,
        "rigReady":False,
        "officialRenderAllowed":False,
        "youtubeUploaded":False,
        "blocker":"Mãos e lanças têm pixels ocluídos; início do plano requer armas não cruzadas, enquanto a imagem-mãe mostra armas cruzadas.",
        "next":"Revisar máscara de luvas sob hastes e resolver pose inicial sem inventar partes ocultas; não habilitar rotações sem QA.",
    }
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("GUARD_RIG_QA_OK",report["verifiedPNGCount"],"sha checked,",
          "hand overlaps",*[x["handSpearOverlapPixels"] for x in records],
          "animations BLOCKED; no images generated")
    return report

if __name__=="__main__":
    try:audit()
    except (GuardRigValidationError,ValueError,KeyError,OSError) as e:
        print("GUARD_RIG_QA_BLOCKED",str(e),file=sys.stderr)
        raise SystemExit(2)
