"""EP01 ten-lot production campaign: reuse the existing guarded queue, no new paid-call path.

10 * 60 minutes is planning capacity, not a promise of ten elapsed hours.
A stage delegates to the existing workflow, verifies its completed artifact
and reports actual image/preview actions. An empty batch stops later stages.
No direct image generation, no rig approval, no YouTube publishing.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/FILA-PRODUCAO-10-HORAS.json"
REPO = "HelioConde/VideoForge-IA"
WORKFLOW = "ep01-image-animation-action-queue.yml"
SCHEMA = "videoforge/ep01-ten-hour-production-campaign/v1"


def load_plan() -> dict:
    raw = json.loads(CONFIG.read_text(encoding="utf-8"))
    safe = raw["safe_dispatch"]
    stages = raw["stages"]
    if (raw.get("schema") != SCHEMA or raw.get("estimated_work_minutes") != 600
            or raw.get("stage_count") != 10
            or raw.get("stage_work_budget_minutes") != 60
            or len(stages) != 10
            or [x["slot"] for x in stages] != list(range(1, 11))
            or sum(x["planned_minutes"] for x in stages) != 600
            or any(x["planned_minutes"] != 60 for x in stages)
            or safe["max_images_per_stage"] != 2
            or safe["max_camera_previews_per_stage"] != 4
            or safe["max_paid_image_requests_if_all_stages_run"] != 20
            or safe["max_camera_preview_dispatches_if_all_stages_run"] != 40
            or safe["one_billable_call_max_per_child"] is not True
            or safe["reuse_remote_CAS_ledger"] is not True
            or safe["no_paid_retries"] is not True
            or safe["halt_on_uncertain_external_state"] is not True
            or safe["never_mark_art_approved"] is not True
            or safe["never_mark_rig_approved"] is not True
            or safe["never_publish_youtube"] is not True
            or safe["stop_if_queue_empty"] is not True
            or safe["shot_count"] != 42):
        raise ValueError("EP01_10H_INVALID_PLAN_OR_SAFETY")
    if any(x["max_images"] != 2 or x["max_previews"] != 4
           or x["human_visual_review"] is not False
           or x["dependent_on_previous"] != (None if i == 0 else i)
           for i, x in enumerate(stages)):
        raise ValueError("EP01_10H_INVALID_STAGE")
    return raw


def gh(*args: str, parse_json: bool = False):
    completed = subprocess.run(
        ["gh", *args], capture_output=True, text=True, timeout=150, check=True,
    )
    return json.loads(completed.stdout) if parse_json else completed.stdout


def run_ids() -> set[int]:
    result = gh(
        "run", "list", "--workflow", WORKFLOW,
        "--event", "workflow_dispatch", "--branch", "main",
        "--limit", "100", "--json", "databaseId", parse_json=True,
    )
    if not isinstance(result, list):
        raise ValueError("EP01_10H_BAD_RUN_LIST")
    return {int(x["databaseId"]) for x in result}


def require_main():
    if (os.environ.get("GITHUB_REPOSITORY") != REPO
            or os.environ.get("GITHUB_REF") != "refs/heads/main"
            or not os.environ.get("GH_TOKEN")
            or not os.environ.get("GITHUB_RUN_ID")):
        raise ValueError("EP01_10H_GITHUB_MAIN_ONLY")


def read_execution(run_id: int, target: Path) -> tuple[int, dict]:
    item = gh(
        "api", "repos/" + REPO + "/actions/runs/" + str(run_id),
        parse_json=True,
    )
    if (item.get("conclusion") != "success"
            or item.get("event") != "workflow_dispatch"
            or item.get("head_branch") != "main"
            or not str(item.get("path", "")).endswith("/" + WORKFLOW)):
        raise RuntimeError("EP01_10H_CHILD_NOT_VERIFIED")
    artifact_name = "ep01-image-animation-action-queue-" + str(run_id)
    data = gh("api", f"repos/{REPO}/actions/runs/{run_id}/artifacts", parse_json=True)
    matches = [a for a in data.get("artifacts", [])
               if a.get("name") == artifact_name
               and not a.get("expired") and a.get("size_in_bytes", 0) > 0]
    if len(matches) != 1:
        raise RuntimeError("EP01_10H_CHILD_ARTIFACT_MISSING")
    dest = target / "child"
    dest.mkdir(parents=True, exist_ok=True)
    gh("run", "download", str(run_id), "-n", artifact_name, "-D", str(dest))
    execution = dest / "ep01-production-queue-execution.json"
    if not execution.is_file():
        raise RuntimeError("EP01_10H_CHILD_REPORT_MISSING")
    result = json.loads(execution.read_text(encoding="utf-8"))
    queue = result.get("queue", {})
    event = result.get("execution", {})
    if (queue.get("shots") != 42 or queue.get("total_tasks") != 276
            or queue.get("per_child_paid_image_cap") != 1
            or queue.get("youtube_publication") is not False
            or event.get("human_visual_approval") is not False
            or event.get("rig_ready") is not False
            or event.get("youtube_publications") != 0):
        raise RuntimeError("EP01_10H_CHILD_CONTRACT_INVALID")
    images = event.get("processed_images")
    previews = event.get("processed_camera_previews")
    if (type(images) is not int or not 0 <= images <= 2
            or type(previews) is not int or not 0 <= previews <= 4):
        raise RuntimeError("EP01_10H_CHILD_BUDGET_EXCEEDED")
    return int(matches[0]["id"]), result


def run_stage(slot: int, output: Path) -> dict:
    plan = load_plan()
    require_main()
    if not 1 <= slot <= 10:
        raise ValueError("EP01_10H_SLOT_OUT_OF_RANGE")
    original = run_ids()
    print("EP01_10H_DISPATCH_INTENT", slot, "up_to_2_images_4_previews", flush=True)
    gh("workflow", "run", WORKFLOW, "--ref", "main",
       "-f", "mode=run", "-f", "max_images=2", "-f", "max_previews=4")
    child_id = None
    for _ in range(30):
        added = run_ids() - original
        if len(added) > 1:
            raise RuntimeError("EP01_10H_AMBIGUOUS_CHILD_NO_RETRY")
        if len(added) == 1:
            child_id = next(iter(added))
            break
        time.sleep(6)
    if child_id is None:
        raise RuntimeError("EP01_10H_CHILD_NOT_VISIBLE_NO_RETRY")
    print("EP01_10H_CHILD_RUN", slot, child_id, flush=True)
    subprocess.run(
        ["gh", "run", "watch", str(child_id), "--exit-status", "--interval", "15"],
        check=True,
    )
    artifact, payload = read_execution(child_id, output.parent)
    executed = payload["execution"]
    counts = {
        "images": executed["processed_images"],
        "camera_previews": executed["processed_camera_previews"],
    }
    report = {
        "schema": "videoforge/ep01-ten-hour-production-receipt/v1",
        "slot": slot,
        "total_planned_slots": 10,
        "budget_minutes_per_slot": 60,
        "actual_elapsed_time_not_guaranteed": True,
        "controller_run_id": child_id,
        "controller_artifact_id": artifact,
        "controller_url": f"https://github.com/{REPO}/actions/runs/{child_id}",
        "verified_execution": counts,
        "executed_tasks": executed.get("executed", []),
        "has_more": any(counts.values()),
        "human_visual_approval": False,
        "rig_approved": False,
        "youtube_uploaded": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(
                f"### EP01 / lote {slot:02d} de 10\n\n"
                f"Executadas **{counts['images']} imagens** e "
                f"**{counts['camera_previews']} prévias de câmera**.\n\n"
                f"[Execução controladora #{child_id}]({report['controller_url']}). "
                "Rigs e aprovação visual continuam bloqueados.\n\n"
            )
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write("has_more=" + ("true" if report["has_more"] else "false") + "\n")
    print("EP01_10H_STAGE_VERIFIED", json.dumps(report, ensure_ascii=False), flush=True)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["validate", "run"], required=True)
    p.add_argument("--slot", type=int)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    if args.mode == "validate":
        plan = load_plan()
        print(json.dumps({
            "campaign": plan["id"], "slots": len(plan["stages"]),
            "planned_work_minutes": plan["estimated_work_minutes"],
            "max_paid_image_children": 20, "max_camera_previews": 40,
            "human_visual_approval": False, "youtube_uploaded": False,
        }))
    else:
        if args.slot is None or args.output is None:
            p.error("--slot and --output are required")
        run_stage(args.slot, args.output)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as error:
        print("EP01_10H_ABORT_NO_RETRY", type(error).__name__, str(error),
              file=sys.stderr, flush=True)
        raise SystemExit(2)
