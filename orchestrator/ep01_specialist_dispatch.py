"""Six bounded, real EP01 technical executors with independent Agent-12 QA.

Roles 02/05/06/08/09/11 perform actual versioned source-bound work.
01 assigns via a transactional Store; 12 reviews output bytes independently.
No Astra billing, no image generation, no approval of visual sprites, no final
episode, no YouTube. Work is persisted in a SEPARATE GitHub CAS file.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from .agent_bus import ROLES, fingerprint
from .runtime import ROOT, EP, instructions, report as runtime_report, source, write_report
from .runtime_store import Store, Conflict

STATE = "runtime/ep01-six-specialist-technical-v1.json"
CONTRACT = "ep01-six-real-source-executors-v1"
SPECS = {
    "02": ("narrative_shots", (EP / "CONTINUIDADE-C07-C08-V2.json",)),
    "05": ("proxy_image_provenance", (EP / "PROPOSTA-MOVIMENTO-C07-C08-V1.json",
                                      Path("videoforge/ep01_c08_proxy_composite.py"))),
    "06": ("independent_layer_composite", (Path("videoforge/ep01_c08_proxy_composite.py"),
                                          EP / "PROPOSTA-MOVIMENTO-C07-C08-V1.json")),
    "08": ("cart_240_frame_animation_readiness", (EP / "PROPOSTA-MOVIMENTO-C07-C08-V1.json",
                                                Path("videoforge/ep01_cart_kinematics.py"))),
    "09": ("camera_42_shot_edit_decisions", (EP / "CONTINUIDADE-C07-C08-V2.json",
                                            Path("videoforge/ep01_camera_batch.py"))),
    "11": ("technical_review_mp4", (Path("videoforge/ep01_c08_proxy_composite.py"),
                                   Path("videoforge/ep01_camera_batch.py"))),
}
RUN_SEQUENCE = ("02", "05", "06", "08", "09", "11")
PRIORITIES = {"02": 0, "05": 0, "06": 1, "08": 1, "09": 1, "11": 2}
REQUIRES = {"06": "05", "11": "06"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def seed(store: Store, *, root=ROOT) -> list[str]:
    root = Path(root)
    created=[]
    for role in RUN_SEQUENCE:
        operation, inputs=SPECS[role]
        input_refs={}
        for ref in inputs:
            label=ref.as_posix()
            _bytes,digest=source(root,label)
            input_refs[label]=digest
        # Version key changes only when source or specialist instructions change.
        ins={a:instructions(root,a)[1] for a in ("01",role,"12")}
        version=fingerprint({"contract":CONTRACT,"role":role,
                             "references":input_refs,"instructions":ins})[:16]
        task={
            "task_id":f"EP01-REAL-TECH-AG{role}-{version}",
            "source_task_id":f"EP01-TECH-AG{role}",
            "owner":role, "reviewer":"12",
            "operation":"read_only_analysis", "mode":"deterministic",
            "input_refs":input_refs, "instructions_shas":ins,
            "priority":PRIORITIES[role], "max_attempts":1,
            "stop_on_review_rejection":True,
            "human_visual_approval":False,
            "source_scope":CONTRACT,
            "technical_executed_not_a_model_call":True,
        }
        if store.enqueue(task):
            created.append(task["task_id"])
    return created


def safe_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",
                    encoding="utf-8")


def produce(role: str, output: Path, *, root=ROOT) -> dict:
    """Create concrete role artifact files, never modify episode source assets."""
    root=Path(root)
    dest=Path(output)
    if dest.is_symlink() or dest.resolve().is_relative_to(root.resolve()):
        raise ValueError("Outputs must be outside source tree")
    dest.mkdir(parents=True,exist_ok=True)
    produced={}
    if role=="02":
        from videoforge.ep01_continuity_v2 import read_plan
        plan=read_plan(root)
        shots=plan["shots"]
        if len(shots)!=9 or [x["id"] for x in shots]!=[
             "C07-P01","C07-P02","C07-P03","C07-P04","C08-P01",
             "C08-P02","C08-P03","C08-P04","C08-P05"]:
            raise ValueError("Unexpected nine-shot narrative")
        audit={
            "kind":"approved_story_plan_readback_not_new_creative_script",
            "shot_count":len(shots),"total_episode_shots":42,
            "beats":[{"id":x["id"],"beat":x["beat"],
                      "start_frame":x["start_frame"],
                      "end_exclusive":x["end_exclusive"]}
                     for x in shots],
            "flee_direction":plan["rules"]["screen_flee_direction"],
            "cart_action":plan["rules"]["cart_action"],
            "story_visual_continuity_approved":False,
            "new_script_generated_by_astra":False,
        }
        if (audit["flee_direction"]!="left_to_right"
                or audit["cart_action"]!="only_kael_pushes"):
            raise ValueError("Narrative contradicts approved continuity rules")
        safe_json(dest/"02-narrative-9-shots.json",audit)
        produced["narrative_audit"]=audit["shot_count"]
    elif role=="05":
        from videoforge.ep01_c08_proxy_composite import verified_sources, RECORDS
        originals=verified_sources(root)
        sources={}
        for k,v in originals.items():
            entry=RECORDS[k]
            if sha(v["path"])!=entry["sha256"]:
                raise ValueError("Generated source SHA changed")
            sources[k]={"path":str(v["path"].relative_to(root)),
                        "sha256":entry["sha256"],
                        "source_run_id":entry["run_id"],
                        "method":"proxy_generated_separate_image",
                        "visual_approved":False}
        if len(sources)!=3:
            raise ValueError("All three real independent proxy files required")
        safe_json(dest/"05-real-proxy-generation-inventory.json",{
            "sources":sources,"new_proxy_calls":0,
            "model_inference_in_this_step":False,
            "candidate_assets_only":True,"images_generated_now":0})
        produced["verified_generated_sources"]=len(sources)
    elif role=="06":
        from videoforge.ep01_c08_proxy_composite import build
        result=build(root,dest/"06-recomposition")
        if (result["source_pngs_SHA_verified"]!=3
                or result["human_visual_approval"] is not False
                or result["rig_ready"] is not False
                or result["new_proxy_calls"]!=0):
            raise ValueError("Source composition QA failed")
        produced["real_generated_layers_composed"]=3
        produced["composite_preview"]=True
    elif role=="08":
        from videoforge.ep01_continuity_motion import read
        from videoforge.ep01_cart_kinematics import build_poses, validate_poses
        poses=build_poses(read(root))
        qa=validate_poses(poses)
        if (qa["frames_checked"]!=240 or qa["continuous_cut"] is not True
                or qa["rig_with_real_assets_approved"] is not False):
            raise ValueError("Cart timeline/technical gate failed")
        safe_json(dest/"08-cart-240-kinematic-frames.json",{
            "frames":[asdict(x) for x in poses],
            "frame_count":240,"actual_character_rig_approved":False,
            "animated_video_rendered":False})
        safe_json(dest/"08-kinematic-contact-qa.json",qa)
        produced["deterministic_frames_validated"]=240
    elif role=="09":
        from videoforge.ep01_camera_batch import build_plan
        plan=build_plan(root,"continuity-v2")
        shots=plan["shots"]
        if len(shots)!=42 or sum(x["duration_frames"] for x in shots)!=4890:
            raise ValueError("EP01 is not 42 shots / 163 seconds")
        edl={
            "kind":"camera_only_edit_decision_list_not_final_montage",
            "fps":30,"shots":[{
                "id":x["id"],"start_frame":x["start_frame"],
                "duration_frames":x["duration_frames"],
                "direction_reviewed":x.get("direction_reviewed",False),
                "source_sha256":(x.get("source") or {}).get("sha256"),
                "camera_mode":x.get("camera",{}).get("mode","unverified"),
            } for x in shots],
            "camera_and_creative_approval":False,
            "rig_frames_generated":0,
        }
        safe_json(dest/"09-camera-42-shots-edl.json",edl)
        produced["shots_indexed"]=42
    elif role=="11":
        from videoforge.ep01_camera_batch import build_plan
        plan=build_plan(root,"continuity-v2")
        if len(plan["shots"])!=42:
            raise ValueError("Final EDL count drift")
        # Build a visibly labeled 3-second TECHNICAL preview from a pre-existing
        # composite. No new illustration, rig, soundtrack or final episode.
        from videoforge.ep01_c08_proxy_composite import build
        existing=dest/"11-composite-source"
        result=build(root,existing)
        picture=existing/result["composite_preview"]
        target=dest/"11-c08-p02-tech-preview-NOT-FINAL.mp4"
        subprocess.run([
            "ffmpeg","-hide_banner","-loglevel","error","-y",
            "-loop","1","-framerate","30","-i",str(picture),
            "-t","3","-an","-c:v","libx264","-pix_fmt","yuv420p",
            "-r","30","-frames:v","90",str(target)
        ],check=True,timeout=120)
        check=subprocess.check_output([
            "ffprobe","-v","error","-select_streams","v:0",
            "-show_entries","stream=nb_frames,codec_name,avg_frame_rate",
            "-of","json",str(target)],text=True,timeout=20)
        stream=json.loads(check)["streams"][0]
        if (stream["codec_name"]!="h264" or int(stream["nb_frames"])!=90
                or stream["avg_frame_rate"]!="30/1"):
            raise ValueError("Technical preview MP4 integrity failure")
        safe_json(dest/"11-media-technical-preview-QA.json",{
            "fps":30,"frames":90,"duration_seconds":3,
            "codec":"h264","audio_included":False,
            "source_pngs_verified":3,
            "source_image_composite_approved":False,
            "camera_animation":False,
            "rig_animation":False,"final_episode":False,
            "youtube_published":False,
            "media_sha256":sha(target),
        })
        produced["technical_mp4_frames"]=90
        produced["technical_mp4_only"]=True
    else:
        raise ValueError("No allowlisted role executor")
    files={str(p.relative_to(dest)):sha(p) for p in sorted(dest.rglob("*"))
           if p.is_file()}
    if not files:
        raise ValueError("Specialist produced no evidence files")
    return {
        "kind":"ep01_specialist_execution_evidence", "role_id":role,
        "operation":SPECS[role][0],"outputs_sha256":files,
        "outcome":produced,"new_model_calls":0,
        "new_generated_image_calls":0,
        "human_visual_approval":False,"rig_ready":False,
        "final_episode_ready":False,"youtube_publication":False,
    }


def independent_qa(result: dict, output: Path, role: str, *, root=ROOT) -> bool:
    """Agent 12: source provenance + output-byte validation; NOT visual judgment."""
    if (result.get("role_id")!=role or result.get("operation")!=SPECS[role][0]
            or result.get("human_visual_approval") is not False
            or result.get("rig_ready") is not False
            or result.get("final_episode_ready") is not False
            or result.get("youtube_publication") is not False
            or result.get("new_model_calls")!=0
            or result.get("new_generated_image_calls")!=0):
        return False
    hashes=result.get("outputs_sha256",{})
    if not isinstance(hashes,dict) or not hashes:
        return False
    dest=Path(output).resolve()
    for rel,digest in hashes.items():
        p=(dest/rel).resolve()
        if (not p.is_relative_to(dest) or not p.is_file() or p.is_symlink()
                or sha(p)!=digest):
            return False
    if role=="05":
        from videoforge.ep01_c08_proxy_composite import verified_sources
        if len(verified_sources(root))!=3:
            return False
    elif role=="06":
        qa=json.loads((dest/"06-recomposition"/"composite-qa.json").read_text())
        if (qa["source_pngs_SHA_verified"]!=3
                or qa["human_visual_approval"] is not False
                or qa["cart_independent_wheel_layers_generated"] is not False):
            return False
    elif role=="08":
        qa=json.loads((dest/"08-kinematic-contact-qa.json").read_text())
        if qa["frames_checked"]!=240 or qa["rig_with_real_assets_approved"] is not False:
            return False
    elif role=="09":
        edl=json.loads((dest/"09-camera-42-shots-edl.json").read_text())
        if len(edl["shots"])!=42 or edl["camera_and_creative_approval"] is not False:
            return False
    elif role=="11":
        qa=json.loads((dest/"11-media-technical-preview-QA.json").read_text())
        mp4=dest/"11-c08-p02-tech-preview-NOT-FINAL.mp4"
        if (qa["final_episode"] is not False or qa["rig_animation"] is not False
                or qa["youtube_published"] is not False
                or qa["media_sha256"]!=sha(mp4)):
            return False
    elif role=="02":
        data=json.loads((dest/"02-narrative-9-shots.json").read_text())
        if len(data["beats"])!=9 or data["story_visual_continuity_approved"] is not False:
            return False
    return True


def worker_step(store: Store, output_dir: Path, *, root=ROOT):
    task=store.claim(mode="deterministic")
    if task is None:
        return None
    role=task["owner"]
    output=Path(output_dir)/task["task_id"]
    try:
        if (role not in SPECS or task.get("source_scope")!=CONTRACT
                or task["reviewer"]!="12"):
            raise ValueError("Unrecognized specialist assignment")
        for src,digest in task["input_refs"].items():
            source(root,src,digest)
        if task["phase"]=="produce":
            needed=REQUIRES.get(role)
            if needed:
                prerequisite=next(
                    (x for x in store.export_snapshot()["tables"]["tasks"]
                     if json.loads(x["payload"]).get("owner")==needed),None)
                if (not prerequisite or
                        json.loads(prerequisite["payload"])["status"]!="completed"):
                    raise ValueError("Cannot start without preceding source specialist QA")
            evidence=produce(role,output,root=root)
            store.deliver(task["task_id"],task["attempt_id"],task["revision"],{
                "agent_id":role,"input_refs":task["input_refs"],
                "source_task_id":task["source_task_id"],
                "execution_mode":"bounded_real_tool_no_model_call",
                "evidence":evidence,"evidence_sha256":fingerprint(evidence),
                "origin_run_id":os.getenv("GITHUB_RUN_ID",""),
                "human_visual_approval":False,"youtube_publication":False,
            })
        else:
            result=store.result(task["task_id"])
            passed=(result.get("agent_id")==role
                    and result.get("input_refs")==task["input_refs"]
                    and result.get("evidence_sha256")==fingerprint(result["evidence"])
                    and independent_qa(result["evidence"],output,role,root=root))
            store.review(task["task_id"],task["attempt_id"],task["revision"],{
                "agent_id":"12","reviewed_result_sha256":task["result_sha256"],
                "technical_passed":bool(passed),"human_visual_approval":False,
                "scope":"independent_source_and_artifact_byte_qa_not_visual_approval",
                "visual_frames_inspected":0,
                "media_publish_authorized":False,
            })
    except Conflict:
        raise
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError,RuntimeError) as exc:
        store.fail(task["task_id"],task["attempt_id"],task["revision"],
                   type(exc).__name__,retry=False)
    return store.get(task["task_id"])


def run(store: Store, output_dir: Path, *, root=ROOT) -> dict:
    created=seed(store,root=root)
    recovered=store.recover()
    steps=[]
    for _ in range(12):
        row=worker_step(store,output_dir,root=root)
        if row is None:
            break
        steps.append({"task_id":row["task_id"],"phase":row.get("phase"),
                      "status":row.get("status")})
    result=runtime_report(store,root=root)
    role_state={t["owner"]:t["status"] for t in result["tasks"]}
    result["specialist_dispatch"]={
        "contract":CONTRACT,"new_task_ids":created,"steps":steps,
        "recovered":recovered,"safe_roles":list(RUN_SEQUENCE),
        "technical_completed":sum(t["status"]=="completed" for t in result["tasks"]),
        "completed_roles":sorted(r for r,s in role_state.items() if s=="completed"),
        "model_calls":0,"new_images":0,"youtube_publications":0,
        "human_visual_approval":False,
        "real_image_sources_reused":True,
        "technical_preview_only":True,
        "blocked_task_ids":[t["task_id"] for t in result["tasks"]
                            if t["status"] in ("blocked","dead_letter")],
    }
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--github-state",action="store_true")
    p.add_argument("--initialize-store",action="store_true")
    args=p.parse_args()
    if args.initialize_store and not args.github_state:
        p.error("initialize-store requires github-state")
    if not args.db and not args.github_state:
        p.error("db required for local mode")
    tmp=None
    if args.github_state:
        from .github_state import GitHubState
        remote=GitHubState(path=STATE,initialize=args.initialize_store)
        snapshot=remote.load()
        tmp=tempfile.TemporaryDirectory(prefix="vf-6-agents-")
        store=Store(Path(tmp.name)/"six.sqlite")
        if snapshot:
            store.import_snapshot(snapshot)
        store.persist_callback=remote.save
    else:
        store=Store(args.db)
    try:
        result=run(store,args.output_dir)
        write_report(args.output,result)
        summary=result["specialist_dispatch"]
        print(json.dumps({"completed_roles":summary["completed_roles"],
                          "technical_completed":summary["technical_completed"],
                          "blocked":len(summary["blocked_task_ids"]),
                          "new_ai_calls":0,"new_image_calls":0,
                          "youtube_publications":0}))
        if summary["blocked_task_ids"] or summary["technical_completed"]!=6:
            raise SystemExit("Six-agent technical dispatch not fully verified")
    finally:
        store.close()
        if tmp:
            tmp.cleanup()

if __name__=="__main__":
    main()
