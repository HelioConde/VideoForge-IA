"""Fail-closed 40-shot articulated motion direction contract.

This JSON is a STORYBOARD, not real measured geometry or a render-ready rig.
It must stay aligned to canonical story/manifest before autonomous task planning.
"""
from __future__ import annotations

import json
from pathlib import Path
from .cinematic_direction import load_active_remake_plan
from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE

NAME="remake-v2-motion-directions.json"
SCHEMA="videoforge/remake-v2-motion-directions/v1"
STAGES=("establish","anticipate","articulate","resolve")
SPECIAL={
 "C01-P05":(310,360),
 "C08-P04":(2880,2940),
 "C12-P04":(4290,4350),
}
SWORD_PARTS=("underlay","sheath","blade","hand")


def validate_motion_directions(data:dict,root:Path=ROOT)->dict:
    base=Path(root)/EPISODE
    plan=load_active_remake_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",root)
    if plan is None:
        raise VideoForgeError("REMAKE_MOTION_ACTIVE_PLAN_MISSING")
    story=json.loads((base/"roteiro.json").read_text(encoding="utf-8"))
    spoken={s["shot_id"]:s["spoken"]
            for scene in story["scenes"] for s in scene["shots"]}
    if (not isinstance(data,dict)
            or data.get("schema")!=SCHEMA
            or data.get("video_id")!=plan["video_id"]
            or data.get("channel")!=plan["channel"]
            or data.get("version")!=plan["version"]
            or data.get("source_story")!="roteiro.json"
            or data.get("source_plan")!="remake-ep01-planos.json"
            or data.get("status")!="editorial_direction_not_measured_or_rendered"
            or data.get("scenes")!=14 or data.get("shot_count")!=40
            or data.get("visual_shots")!=39
            or data.get("total_frames")!=4890 or data.get("fps")!=30
            or data.get("steps_per_shot")!=4
            or data.get("source_geometry_calibration_required") is not True
            or data.get("paid_provider_calls_authorized") is not False
            or data.get("official_video_approved") is not False
            or data.get("youtube_uploaded") is not False):
        raise VideoForgeError("REMAKE_MOTION_ROOT_OR_POLICY_INVALID")
    shots=data.get("shots")
    if not isinstance(shots,list) or len(shots)!=40:
        raise VideoForgeError("REMAKE_MOTION_SHOT_COUNT_INVALID")
    all_ids=set()
    for expected,cue in zip(plan["shots"],shots):
        sid=expected["shot_id"]
        duration=expected["frame_end_exclusive"]-expected["frame_start"]
        if (not isinstance(cue,dict) or cue.get("shot_id")!=sid
                or cue.get("scene_id")!=expected["scene_id"]
                or cue.get("order")!=expected["order"]
                or cue.get("type")!=expected["shot_type"]
                or cue.get("cast")!=expected["cast"]
                or cue.get("focus")!=expected["focus"]
                or cue.get("emotion")!=expected["emotion"]
                or cue.get("spoken_or_sfx")!=spoken[sid]
                or cue.get("frames")!={"global_start":expected["frame_start"],
                     "global_end_exclusive":expected["frame_end_exclusive"],
                     "local_duration":duration}
                or sid in all_ids):
            raise VideoForgeError("REMAKE_MOTION_SHOT_MISMATCH:"+sid)
        all_ids.add(sid)
        cam=cue.get("camera",{})
        official=expected["camera"]
        if (not isinstance(cam,dict)
            or cam.get("lens_mm")!=official["lens_mm"]
            or cam.get("framing")!=official["description"]
            or cam.get("axis")!=official["position_and_intent"]
            or cam.get("depth_of_field")!=official["depth_of_field"]
            or cam.get("movement_rule") not in (
              "tracking_only_with_separate_character_and_environment_layers",
              "locked_or_parallax_only_if_separate_verified_layers")):
            raise VideoForgeError("REMAKE_MOTION_CAMERA_MISMATCH:"+sid)
        parts=cue.get("independent_rgba_parts")
        if not isinstance(parts,list) or not all(
                isinstance(s,str) and len(s)>=3 for s in parts):
            raise VideoForgeError("REMAKE_MOTION_RIG_PARTS_MISSING:"+sid)
        if (sid=="C01-P01" and parts!=[]) or (sid!="C01-P01" and not parts):
            raise VideoForgeError("REMAKE_MOTION_RIG_PARTS_INVALID:"+sid)
        if sid=="C01-P02" and parts!=list(SWORD_PARTS):
            raise VideoForgeError("REMAKE_MOTION_SWORD_PARTS_INVALID")
        phases=cue.get("stages")
        if not isinstance(phases,list) or len(phases)!=4:
            raise VideoForgeError("REMAKE_MOTION_FOUR_PHASES_REQUIRED:"+sid)
        last=-1
        for k,beat in zip(STAGES,phases):
            if (not isinstance(beat,dict) or beat.get("stage")!=k
                or type(beat.get("local_frame")) is not int
                or not last<beat["local_frame"]<duration
                or beat.get("global_frame")!=expected["frame_start"]+beat["local_frame"]
                or not isinstance(beat.get("direction"),str)
                or len(beat["direction"])<35):
                raise VideoForgeError("REMAKE_MOTION_PHASE_TIMING_OR_DIRECTION_INVALID:"+sid)
            last=beat["local_frame"]
        if phases[0]["local_frame"]!=0 or phases[-1]["local_frame"]!=duration-1:
            raise VideoForgeError("REMAKE_MOTION_PHASE_COVERAGE_INVALID:"+sid)
        if sid=="C01-P02" and [s["local_frame"] for s in phases]!=[0,7,72,89]:
            raise VideoForgeError("REMAKE_MOTION_SWORD_TIMING_CHANGED")
        if sid=="C12-P01" and [s["local_frame"] for s in phases]!=[0,4,86,119]:
            raise VideoForgeError("REMAKE_MOTION_C12_EYES_TIMING_CHANGED")
        src=cue.get("source_contract")
        if (not isinstance(src,dict) or
            src.get("own_shot_mother_required")!=(sid!="C01-P01")
            or src.get("expected_asset_directory")!=expected["asset_directory"]
            or src.get("human_visual_approved") is not False
            or src.get("pivots_measured_from_real_art") is not False
            or src.get("technically_calibrated") is not False
            or cue.get("rig_configuration_status")!="needs_true_asset_pixel_measurement"
            or cue.get("automatic_paid_calls_allowed") is not False
            or cue.get("approved_for_final_render") is not False
            or cue.get("youtube_uploaded") is not False):
            raise VideoForgeError("REMAKE_MOTION_FAKE_ASSET_APPROVAL:"+sid)
        qa=cue.get("qa_requirements")
        if not isinstance(qa,list) or not all(
             isinstance(s,str) and len(s)>12 for s in qa):
            raise VideoForgeError("REMAKE_MOTION_QA_MISSING:"+sid)
    by_id={s["shot_id"]:s for s in shots}
    for sid,span in SPECIAL.items():
        s=by_id.get(sid)
        if not s or (s["frames"]["global_start"],
                      s["frames"]["global_end_exclusive"])!=span:
            raise VideoForgeError("REMAKE_MOTION_NEW_INSERT_INVALID:"+sid)
    if "elara" in by_id["C01-P05"]["cast"]:
        raise VideoForgeError("REMAKE_MOTION_EARLY_PRINCESS_REVEAL")
    return {"shots":40,"stages":160,"frames":4890,"visual_shots":39,
            "rig_geometry_calibrated":False,"full_video_render_approved":False}


def load_motion_directions(root:Path=ROOT)->dict:
    path=Path(root)/EPISODE/NAME
    if path.is_symlink() or not path.is_file() or path.stat().st_size>300_000:
        raise VideoForgeError("REMAKE_MOTION_SOURCE_MISSING_OR_UNSAFE")
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,UnicodeError,OSError) as exc:
        raise VideoForgeError("REMAKE_MOTION_SOURCE_INVALID_JSON") from exc
    validate_motion_directions(data,root)
    return data


def main()->int:
    try:
        doc=load_motion_directions()
        print("REMAKE_MOTION_40_VALIDATED",len(doc["shots"]),"shots",
              sum(len(shot["stages"]) for shot in doc["shots"]),"keyed stages",
              "no art/no rig/no paid API/no YouTube")
        return 0
    except (OSError,KeyError,ValueError,VideoForgeError) as exc:
        import sys
        print("REMAKE_MOTION_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
