#!/usr/bin/env python3
"""Execute real, read-only deterministic work by roles 01, 03 and 12.

This is NOT an LLM or visual-frame inspection. No network, paid API or publishing.
"""
import argparse
import hashlib
import json
from pathlib import Path
from agent_bus import make_message, append_message, safe_checkpoint
from task_leases import claim, checkpoint

TASK_ID = "EP01-C07-C08-V2-CONTINUITY-AUDIT"
EXPECTED_IDS = ["C07-P01","C07-P02","C07-P03","C07-P04",
                "C08-P01","C08-P02","C08-P03","C08-P04","C08-P05"]

def digest(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def run(queue_file, root):
    root = Path(root).resolve()
    queue = json.loads(Path(queue_file).read_text(encoding="utf-8"))
    task = next((x for x in queue["tasks"] if x["task_id"] == TASK_ID), None)
    if task is None or task["status"] != "ready" or task["owner"] != "diretor-cenas":
        raise ValueError("Agent 01: task not ready or owner mismatch")
    if task.get("blocked_by"):
        raise ValueError("Agent 01: task blocked")
    path = root / "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CONTINUIDADE-C07-C08-V2.json"
    if not path.is_file():
        raise ValueError("Continuity manifest missing")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    state = {}
    append_message(state, make_message(TASK_ID,"01","03","task_assigned",
                                       "Validar estrutura e continuidade declarada do manifesto V2",1))
    # Agent 03 actually checks the source manifest, not only a canned response.
    shots = manifest.get("shots", [])
    ids = [s.get("id") for s in shots]
    issues = []
    if ids != EXPECTED_IDS:
        issues.append("Shot sequence differs from expected 9-shot C07/C08 V2")
    if manifest.get("rules", {}).get("screen_flee_direction") != "left_to_right":
        issues.append("Escape axis is not left_to_right")
    if manifest.get("rules", {}).get("cart_action") != "only_kael_pushes":
        issues.append("Cart operator must be Kael alone")
    if manifest.get("rules", {}).get("human_visual_approval_required") is not True:
        issues.append("Human visual gate missing")
    if manifest.get("rules", {}).get("auto_youtube_upload") is not False:
        issues.append("Publication protection missing")
    for index, shot in enumerate(shots):
        if not isinstance(shot.get("start_frame"), int) or not isinstance(shot.get("end_exclusive"), int):
            issues.append(f"{shot.get('id')}: frame bounds invalid")
            continue
        if shot["end_exclusive"] <= shot["start_frame"]:
            issues.append(f"{shot.get('id')}: invalid duration")
        if index and shot["start_frame"] != shots[index-1].get("end_exclusive"):
            issues.append(f"{shot.get('id')}: discontinuous frame boundary")
    if shots and (shots[0]["start_frame"] != 2070 or shots[-1]["end_exclusive"] != 2940):
        issues.append("Editorial frame range differs from V2")
    report03 = {"agent":"03", "task_id":TASK_ID, "scope":"manifest_structure_only",
                "shot_ids":ids, "issues":issues, "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                "visual_frames_inspected":0, "human_visual_approval":False}
    leased = claim(task,"diretor-cenas",100,900)
    delivered = checkpoint(leased,"diretor-cenas",leased["lease"]["lease_key"],
                           {"artifact_sha256":digest(report03)})
    append_message(state, make_message(TASK_ID,"03","12","review_requested",
                                       "Manifest audit delivered; independently verify the report",2))
    # Agent 12 independently checks the underlying manifest and reported evidence.
    checks = {
        "source_hash_matches":report03["source_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(),
        "report_hash_matches":delivered["checkpoint"]["evidence"]["artifact_sha256"] == digest(report03),
        "shot_count_nine":len(shots)==9,
        "shot_ids_match":ids==EXPECTED_IDS,
        "no_manifest_issues":not issues,
        "no_visual_approval":report03["human_visual_approval"] is False,
    }
    report12 = {"agent":"12", "task_id":TASK_ID, "scope":"technical_manifest_QA_only",
                "checks":checks, "passed":all(checks.values()),
                "visual_quality_approved":False, "human_review_required":True}
    append_message(state, make_message(TASK_ID,"12","01","qa_result",
                                       "Technical manifest QA finished; visual QA remains pending",3))
    result = {"schema_version":1,"mode":"deterministic_read_only_execution",
              "task_id":TASK_ID,"director_01":{"selected_task":TASK_ID,"dispatched_to":"03"},
              "scene_director_03":report03,"qa_12":report12,
              "task_checkpoint":delivered["checkpoint"],
              "messages":state["events"],"safety":safe_checkpoint(state["events"]),
              "agents_executed":["01","03","12"],"llm_agents_executed":[],
              "production_files_modified":False,"youtube_publications":0}
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root",default=".")
    parser.add_argument("--queue",default="orchestrator/tasks.json")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    result=run(args.queue,args.root)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"task_id":result["task_id"],"qa_passed":result["qa_12"]["passed"],
                      "visual_approval":False,"output":str(out)}))
    if not result["qa_12"]["passed"]:
        raise SystemExit("Technical QA failed; review artifact")

if __name__=="__main__":
    main()
