"""Contrato C12-P01: só pupilas 12px e pálpebras 1px, sem cabeça/câmera.

O plano JSON não é arte nem autorização: a verificação separada de QA
obriga underlay real de esclerótica, remoção de pupilas pintadas no rosto
e conformidade dos PNGs RGBA com a mesma mãe do shot. Sem gerar imagens.
"""
from __future__ import annotations
import json
from pathlib import Path
from .errors import VideoForgeError

SHOT_ID="C12-P01"
EXPECTED_PUPILS=[
    {"frame":0,"value":0},{"frame":4,"value":0},
    {"frame":86,"value":12},{"frame":119,"value":12},
]
EXPECTED_LIDS=[
    {"frame":0,"value":0},{"frame":7,"value":0},
    {"frame":86,"value":1},{"frame":119,"value":1},
]
EYE_LAYER_IDS={
    "pupil-left","pupil-right","eyelid-left","eyelid-right",
}
QA_FLAGS=(
    "pupil_motion_approved",
    "eyelid_motion_approved",
    "head_stability_approved",
    "eye_mask_no_bleed_verified",
    "eye_sclera_underlays_verified",
    "no_duplicate_pupils_in_head_verified",
)

def check_eye_performance(shot_id:str,rig:dict,qa:dict)->dict:
    if shot_id!=SHOT_ID:
        raise VideoForgeError("CINEMATIC_GAZE_SHOT_NOT_C12_P01")
    performance=rig.get("performance")
    if not isinstance(performance,dict):
        raise VideoForgeError("CINEMATIC_GAZE_PERFORMANCE_MISSING")
    required={
        "mode":"pupils_only_locked_head","actorId":"kael",
        "pupilKeyframes":EXPECTED_PUPILS,
        "eyelidKeyframes":EXPECTED_LIDS,
        "headRotationDeg":0,"bodyMotionEnabled":False,
        "cameraLocked":True,"humanMotionApproved":True,
    }
    if any(performance.get(key)!=value for key,value in required.items()):
        raise VideoForgeError("CINEMATIC_GAZE_DIRECTION_MISMATCH")
    if any(qa.get(key) is not True for key in QA_FLAGS):
        raise VideoForgeError("CINEMATIC_GAZE_HUMAN_EYE_QA_MISSING")
    frames=qa.get("qa_frames")
    if not isinstance(frames,list) or not {3990,3994,4076,4109}.issubset(set(frames)):
        raise VideoForgeError("CINEMATIC_GAZE_KEYFRAME_QA_MISSING")
    actors=rig.get("actors")
    if not isinstance(actors,list) or len(actors)!=1 or actors[0].get("id")!="kael":
        raise VideoForgeError("CINEMATIC_GAZE_KAEL_ONLY")
    face=actors[0].get("rig",{})
    if not isinstance(face,dict):
        raise VideoForgeError("CINEMATIC_GAZE_FACE_RIG_INVALID")
    eyes=face.get("eyeRig")
    if not isinstance(eyes,dict):
        raise VideoForgeError("CINEMATIC_GAZE_EYE_RIG_MISSING")
    eye_fields={
        "actorId":"kael",
        "pupilLayerIds":["pupil-left","pupil-right"],
        "eyelidLayerIds":["eyelid-left","eyelid-right"],
        "eyeUnderlaysVerified":True,
        "pupilMasksVerified":True,
        "noDuplicatePaintedPupilsInHead":True,
        "rotationOrTranslationClippingQA":True,
        "gazePupilMaxPx":12,"eyelidMaxPx":1,
        "humanVisualApproved":True,
    }
    if any(eyes.get(key)!=value for key,value in eye_fields.items()):
        raise VideoForgeError("CINEMATIC_GAZE_EYE_RIG_QA_INVALID")
    layers=face.get("layers")
    if not isinstance(layers,list):
        raise VideoForgeError("CINEMATIC_GAZE_RIG_LAYERS_MISSING")
    names={layer.get("id") for layer in layers if isinstance(layer,dict)}
    if not EYE_LAYER_IDS.issubset(names):
        raise VideoForgeError("CINEMATIC_GAZE_INDEPENDENT_PUPILS_MISSING")
    if face.get("headMaxRotationDeg")!=0 or face.get("blinkFrames")!=[]:
        raise VideoForgeError("CINEMATIC_GAZE_HEAD_OR_BLINK_NOT_FROZEN")
    return dict(required)

def validate_draft_plan(episode:Path)->dict:
    f=episode/"rig-olhar-kael-c12-p01.json"
    if f.is_symlink() or not f.is_file():
        raise VideoForgeError("CINEMATIC_GAZE_DRAFT_PLAN_MISSING")
    p=json.loads(f.read_text(encoding="utf8"))
    if (p.get("schema")!="videoforge/independent-pupil-motion-plan/v1"
            or p.get("shot")!=SHOT_ID or p.get("actor")!="kael"
            or p.get("status")!="DRAFT_ASSETS_AND_ANATOMY_MISSING"
            or p.get("frames",{}).get("global_start")!=3990
            or p.get("frames",{}).get("global_end_exclusive")!=4110):
        raise VideoForgeError("CINEMATIC_GAZE_DRAFT_DIRECTION_INVALID")
    draft=p.get("performance",{})
    if draft.get("humanMotionApproved") is not False:
        raise VideoForgeError("CINEMATIC_GAZE_DRAFT_FALSELY_APPROVED")
    expected={
        "mode":"pupils_only_locked_head","actorId":"kael",
        "pupilKeyframes":EXPECTED_PUPILS,
        "eyelidKeyframes":EXPECTED_LIDS,"headRotationDeg":0,
        "bodyMotionEnabled":False,"cameraLocked":True,
    }
    if any(draft.get(k)!=v for k,v in expected.items()):
        raise VideoForgeError("CINEMATIC_GAZE_DRAFT_FRAMES_INVALID")
    return p
