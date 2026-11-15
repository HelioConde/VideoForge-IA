"""Reusable EP01 production queue built from existing VideoForge/Remotion code.

No image service, no render, no fake approval. A deterministic shot-by-shot
queue for GitHub agents and the existing producer workflows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .cinematic_direction import load_active_remake_plan
from .remake_autopilot import EPISODE, ROOT, choose_next, verified_asset
from .errors import VideoForgeError

SCHEMA="videoforge/remake-shot-production-queue/v1"
SKILL="videoforge-dorama-remake"
SUPPORTED={
 "black":("black-and-original-sfx",["sound-design"]),
 "insert":("prop-pivots-three",["prop","hand","background","underlay"]),
 "low_angle":("character-parts-three",["body-no-head","head-open","head-closed","hair-front","background"]),
 "wide":("multi-actor-three",["background","characters-separate","props-separate"]),
 "close_up":("facial-eye-three",["body-no-head","head-open","head-closed","hair-front","neck-underlay"]),
 "extreme_close_up":("eye-pupil-three",["eye-pupils","eyelids","sclera-underlay","head"]),
 "match_cut":("source-to-source-cut",["source-before","source-after"]),
 "over_shoulder":("foreground-and-focus-three",["foreground","background","focal-actor"]),
 "medium":("character-parts-three",["body-no-head","head-open","head-closed","hair","arms"]),
 "tracking":("foot-contact-three",["body","arms","legs","hair-mesh","layered-background"]),
 "two_shot":("two-actor-three",["actor-a","actor-b","arms","hand-contact"]),
 "action":("prop-kinematics-three",["prop","hands","independent-actors","ground-contact"])
}
REUSE={
 "animation_engine":"remotion@4 + @remotion/three/ThreeCanvas + three + @react-three/fiber",
 "rig_component":"motion-remotion/src/rig-three-scene.tsx",
 "mesh_math":"motion-remotion/src/rig-three-math.ts",
 "sword_math":"motion-remotion/src/remake-sword-motion.ts",
 "sword_component":"motion-remotion/src/remake-sword-rig.tsx",
 "official_timeline":"motion-remotion/src/cinematic-timeline.ts",
 "official_skills":"https://github.com/remotion-dev/skills",
 "project_skills":[
  ".agents/skills/videoforge-dorama-remake/SKILL.md",
  ".agents/skills/videoforge-rig-2d-three/SKILL.md",
  ".agents/skills/videoforge-qa-and-checkpoint/SKILL.md",
 ],
}


def work_queue(root:Path=ROOT)->dict:
    base=Path(root)/EPISODE
    plan=load_active_remake_plan("alchemy-lab","mmorpg-conquiste-a-princesa-ep01",root)
    if plan is None:
        raise VideoForgeError("REMAKE_STARTER_ACTIVE_PLAN_MISSING")
    policy=json.loads((base/"autonomy-policy.json").read_text(encoding="utf-8"))
    if policy.get("scope")!="alchemy-lab/mmorpg-conquiste-a-princesa-ep01":
        raise VideoForgeError("REMAKE_STARTER_COST_SCOPE_INVALID")
    stage=choose_next(root)
    anchors=plan["identity_anchors"]
    if not anchors or anchors[0].get("id")!="character-bible":
        raise VideoForgeError("REMAKE_STARTER_FIRST_ANCHOR_INVALID")
    anchor=anchors[0]
    approved_anchor=(anchor.get("human_approved") is True and
                     anchor.get("status")=="approved" and
                     verified_asset(base,anchor.get("path"),anchor.get("sha256")))
    paid=(policy.get("paid_provider_calls_approved") is True and
          type(policy.get("max_chargeable_calls_per_run")) is int and
          policy["max_chargeable_calls_per_run"]>0)
    work=[]
    for item in plan["shots"]:
        sid=item["shot_id"]
        typ=item["shot_type"]
        if typ not in SUPPORTED:
            raise VideoForgeError("REMAKE_STARTER_SHOT_TYPE_NOT_SUPPORTED")
        profile,parts=SUPPORTED[typ]
        if sid=="C01-P02":
            # This insert is an executioner's sword, not a generic hand prop.
            # The specialized Three.js component demands these exact RGBA pieces.
            profile,parts="sword-draw-three",["underlay","sheath","blade","hand"]
        if typ=="black":
            # Trust a run-ID-backed QA manifest, not merely asserted flags.
            # Media is an Actions artifact, not in git (ignores wav/mp4).
            qa_file=base/"QA-C01-P01-REMAKE-V2.json"
            archived=False
            if qa_file.is_file() and not qa_file.is_symlink():
                try:
                    proof=json.loads(qa_file.read_text(encoding="utf-8"))
                    archived=(proof.get("schema")=="videoforge/remake-opening-technical-qa/v1"
                              and proof.get("shot")=="C01-P01"
                              and type(proof.get("github_run_id")) is int
                              and proof["github_run_id"]>0
                              and proof.get("mp4_sha256")==item.get("technical_preview_sha256")
                              and proof.get("audio_sha256")==item.get("original_audio_sha256")
                              and proof.get("black_pixels_verified") is True
                              and proof.get("audio_original_sfx_verified") is True
                              and proof.get("official_video_approved") is False
                              and proof.get("youtube_uploaded") is False)
                except (OSError,ValueError):
                    archived=False
            if archived:
                status="opening_technical_preview_in_actions_pending_review"
                next_work="review_and_preserve_original_sfx_action_artifact"
                deps=["artifact_available_before_retention_expiry","editorial_sfx_review"]
                workflow=None
            else:
                status="audio_and_sfx_pending"
                next_work="produce_original_sword_unsheathing_sfx_no_image"
                deps=["original_licensed_audio","C01-P01_black_at_frames_0_59"]
                workflow="remake-opening-preview.yml"
        else:
            folder="assets/remake-v2/"+sid+"/"
            source_ok=verified_asset(base,folder+"scene-mother.png",item.get("art_mother_sha256"))
            background_ok=verified_asset(base,folder+"background-reconstructed.png",item.get("background_sha256"))
            approved=item.get("human_visual_approved") is True
            if not approved_anchor:
                status="blocked_canonical_reference"
                next_work="produce_review_and_approve_character_bible_anchor"
                workflow="production-art-by-request.yml"
                deps=["character_bible_sha_verified","human_visual_reference_approved"]
            elif not source_ok:
                status="blocked_cost" if not paid else "ready_for_image_workflow"
                next_work="generate_shot_specific_mother_with_existing_workflow"
                workflow="production-scene-by-request.yml"
                deps=["canonical_anchor_sha_verified","provider_call_authorized"]
            elif not background_ok:
                status="scene_layers_needed"
                next_work="separate_rgba_assets_from_own_shot_mother"
                workflow="production-rgba-part-by-request.yml"
                deps=["scene_mother_sha_verified","same_canvas_rgba"]
            elif not item.get("motion_qa_passed"):
                status="rig_and_mesh_qa_needed"
                next_work="build_real_articulated_three_rig_and_roundtrip_qa"
                workflow="production-rig-three-art-candidate.yml"
                deps=["background_sha_verified","layer_rgba_sha","underlay_and_seam_qa"]
            elif not approved:
                status="human_visual_review_needed"
                next_work="review_technical_mp4_and_identity"
                workflow=None
                deps=["qa_articulated_motion","human_approval"]
            else:
                status="candidate_for_final_assembly_not_auto_publishable"
                next_work="verify_complete_audio_and_video_manifest"
                workflow=None
                deps=["full_episode_audio_qa","render_contract_all_shots"]
        direction={
            "camera":item["camera"]["position_and_intent"],
            "description":item["camera"]["description"],
            "dramatic_direction":item["camera"]["dramatic_direction"],
            "emotion":item["emotion"],
            "cast":item["cast"],
            "focus":item["focus"],
        }
        task_input={"shot_id":sid,"frames":[item["frame_start"],item["frame_end_exclusive"]],
                    "profile":profile,"source_sha":item.get("art_mother_sha256"),"stage":status,
                    "anchor_sha":anchor.get("sha256") if approved_anchor else None}
        task_sha=hashlib.sha256(json.dumps(task_input,sort_keys=True,
                            ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest()
        work.append({
            "shot_id":sid,"scene_id":item["scene_id"],
            "order":item["order"],
            "start_frame":item["frame_start"],
            "end_frame_exclusive":item["frame_end_exclusive"],
            "duration_frames":item["frame_end_exclusive"]-item["frame_start"],
            "shot_type":typ,
            "profile":profile,"required_parts":parts,
            "direction":direction,"status":status,"next_action":next_work,
            "candidate_workflow":workflow,"dependencies":deps,
            "dispatch_permitted":False, # A queue is NOT a dispatch ticket
            "automated_visual_approval":False,"render_approved":False,
            "task_fingerprint":task_sha,
        })
    return {
      "schema":SCHEMA,"scope":"alchemy-lab/mmorpg-conquiste-a-princesa-ep01",
      "source":"remake-ep01-planos.json",
      "source_checkpoint":"ESTADO-ATUAL.md",
      "generated_by":"videoforge.remake_starter",
      "source_is_real_artwork":False,"created_images":0,"created_video":False,
      "youtube_uploaded":False,
      "approval_or_paid_calls_granted":False,
      "format":plan["format"],
      "shot_count":len(work),"visual_shot_count":sum(i["shot_type"]!="black" for i in work),
      "reuse":REUSE,
      "autopilot":{k:stage.get(k) for k in ("stage","target","blocker","dispatch_allowed")},
      "current_blocker":stage.get("blocker"),
      "production_queue":work,
    }


def main()->int:
    p=argparse.ArgumentParser(description="Compile the current V2 shots into safe reusable GitHub work units")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=work_queue()
    contents=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(contents,encoding="utf-8")
    print("REMAKE_QUEUE_CREATED",
          "shots",report["shot_count"],
          "visual",report["visual_shot_count"],
          "blocker",report["current_blocker"],
          "images",0,"video",False)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
