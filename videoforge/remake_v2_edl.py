"""Generate the 40-shot V2 editorial EDL without mutating the 37-shot legacy EDL.

No media, image generation, rigs, proxy calls or YouTube. This file is an
EDITORIAL plan, not approved Remotion render props. The official full-episode
renderer MUST still reject nonapproved sources and unverified audio bytes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .cinematic_direction import load_active_remake_plan,REQUIRES_OVERLAY
from .errors import VideoForgeError
from .remake_autopilot import ROOT,EPISODE

SCHEMA="videoforge/remake-v2-cinematic-edl/v1"
NAME="remake-v2-cinematic-edl.json"
OPENING_WAV="vf-remake/c01-p01/sword-original.wav"


def build(root:Path=ROOT)->dict:
    base=Path(root)/EPISODE
    plan=load_active_remake_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",root)
    if plan is None:
        raise VideoForgeError("REMAKE_V2_EDL_ACTIVE_MANIFEST_REQUIRED")
    if (len(plan["shots"])!=40 or plan["plan"]["scenes"]!=14
            or plan["plan"]["art_required"]!=39
            or plan["format"]["total_frames"]!=4890):
        raise VideoForgeError("REMAKE_V2_EDL_EXPECTED_40_SHOTS")
    story=json.loads((base/"roteiro.json").read_text(encoding="utf-8"))
    spoken={item["shot_id"]:item["spoken"]
            for scene in story["scenes"] for item in scene["shots"]}
    if len(spoken)!=40 or set(spoken)!={s["shot_id"] for s in plan["shots"]}:
        raise VideoForgeError("REMAKE_V2_EDL_STORY_DIVERGED")
    source_qa=json.loads((base/"QA-C01-P01-REMAKE-V2.json").read_text(encoding="utf-8"))
    first=plan["shots"][0]
    if (first["shot_id"]!="C01-P01"
        or first["frame_start"]!=0 or first["frame_end_exclusive"]!=60
        or source_qa.get("schema")!="videoforge/remake-opening-technical-qa/v1"
        or source_qa.get("shot")!="C01-P01"
        or source_qa.get("audio_sha256")!=first.get("original_audio_sha256")
        or source_qa.get("technical_preview_only") is not True
        or source_qa.get("official_video_approved") is not False
        or source_qa.get("youtube_uploaded") is not False):
        raise VideoForgeError("REMAKE_V2_EDL_OPENING_PROOF_INVALID")
    shots=[]
    for s in plan["shots"]:
        sid=s["shot_id"]
        black=s["shot_type"]=="black"
        src=s["asset_directory"]
        entry={
          "id":sid,
          "scene":s["scene_id"],
          "startFrame":s["frame_start"],
          "endFrameExclusive":s["frame_end_exclusive"],
          "durationFrames":s["frame_end_exclusive"]-s["frame_start"],
          "type":s["shot_type"],
          "characters":s["cast"],
          "focus":s["focus"],
          "emotion":s["emotion"],
          "camera":s["camera"],
          "direction":s.get("rig_notes",""),
          "spokenOrSfx":spoken[sid],
          "hudPolicy":"remotion_overlay" if sid in REQUIRES_OVERLAY else "none",
          "status":"black_no_art_required" if black else "shot_art_or_rig_pending",
          "renderAllowed":black,
          "humanVisualApproved":False,
          "assetPaths":None if black else {
            "mother":src+"scene-mother.png",
            "background":src+"background-reconstructed.png",
            "rig":src+"rig.json",
            "qa":src+"qa.json",
          },
        }
        if black:
            entry["audioFile"]=OPENING_WAV
            entry["audioSha256"]=source_qa["audio_sha256"]
            entry["audioOriginStatus"]="original_wav_audited_in_actions_not_yet_materialized_for_official_episode"
            entry["technicalPreviewArtifact"]=source_qa["artifact_name"]
        shots.append(entry)
    if any(s["humanVisualApproved"] or (s["renderAllowed"] and
                s["type"]!="black") for s in shots):
        raise VideoForgeError("REMAKE_V2_EDL_UNVERIFIED_ASSETS_MUST_STAY_LOCKED")
    return {
      "schema":SCHEMA,
      "channel":"alchemy-lab",
      "video_id":"mmorpg-conquiste-a-princesa-ep01",
      "activeRemakeVersion":plan["version"],
      "source":"remake-ep01-planos.json",
      "sourceStory":"roteiro.json",
      "format":{
        "fps":plan["format"]["fps"],"width":plan["format"]["width"],
        "height":plan["format"]["height"],
        "totalFrames":plan["format"]["total_frames"],
        "durationSeconds":plan["format"]["duration_seconds"],
      },
      "scenes":14,
      "shotCount":40,
      "blackShots":1,
      "artRequiredShots":39,
      "unapprovedShots":39,
      "renderOfficialAllowed":False,
      "youtubeUploaded":False,
      "legacy37ShotEdlUntouched":"timeline-cinematografica.json",
      "audioRequiresShaVerifiedBytesBeforeOfficialRender":True,
      "status":"editorial_40_shots_art_and_audio_staging_pending",
      "shots":shots,
    }


def main()->int:
    parser=argparse.ArgumentParser()
    choices=parser.add_mutually_exclusive_group(required=True)
    choices.add_argument("--check",action="store_true")
    choices.add_argument("--write",action="store_true")
    args=parser.parse_args()
    try:
        expected=build()
        p=ROOT/EPISODE/NAME
        if args.check:
            if not p.is_file() or p.is_symlink():
                raise VideoForgeError("REMAKE_V2_EDL_SNAPSHOT_MISSING")
            if json.loads(p.read_text(encoding="utf-8"))!=expected:
                raise VideoForgeError("REMAKE_V2_EDL_SNAPSHOT_OUT_OF_SYNC")
            print("REMAKE_V2_EDL_VALIDATED",expected["shotCount"],
                  "shots",expected["artRequiredShots"],"visual",
                  expected["format"]["totalFrames"],"frames","no_render")
        else:
            if p.is_symlink():
                raise VideoForgeError("REMAKE_V2_EDL_SYMLINK_FORBIDDEN")
            p.write_text(json.dumps(expected,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print("REMAKE_V2_EDL_WRITTEN",str(p))
        return 0
    except (OSError,KeyError,ValueError,VideoForgeError) as exc:
        print("REMAKE_V2_EDL_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
