"""Orquestra a geração de imagens-mãe faltantes do EP01 via workflows isolados.

Cada chamada paga ocorre NO workflow filho ep01-scene-mother-by-request.yml
(1 imagem por execução). Este controlador não chama o proxy diretamente.
Interrompe ao primeiro erro, sem retries de cobrança, sem aprovação humana falsa.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

CHANNEL = "alchemy-lab"
VIDEO = "mmorpg-conquiste-a-princesa-ep01"
REL = f"canal/{CHANNEL}/videos/{VIDEO}"
CHECKPOINT = f"{REL}/CHECKPOINT-IMAGENS-EP01-AUTO.json"
REQUEST = Path(REL) / "PEDIDO-LOTE-MAES-EP01.json"
WORKFLOW = "ep01-scene-mother-by-request.yml"
SCHEMA = "videoforge/ep01-mother-fill-queue/v1"


def command(*args: str, capture: bool = False) -> str:
    cmd = list(args)
    result = subprocess.run(
        cmd, text=True, check=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=None,
    )
    return result.stdout if capture else ""


def gh_json(*args: str):
    return json.loads(command("gh", *args, capture=True))


def current_inventory() -> dict:
    command("git", "fetch", "--quiet", "origin", "main")
    raw = command("git", "show", f"origin/main:{CHECKPOINT}", capture=True)
    obj = json.loads(raw)
    if (obj.get("schema") != "videoforge/ep01-image-inventory-auto/v1"
            or obj.get("channel") != CHANNEL
            or obj.get("video_id") != VIDEO
            or obj.get("visual_shots") != 39
            or obj.get("counts_are_generated_not_approved") is not True):
        raise RuntimeError("EP01_QUEUE_INVALID_CHECKPOINT")
    missing = obj.get("missing_original_mother_shot_ids")
    if not isinstance(missing, list) or len(missing) != obj.get(
            "visual_shots_missing_original_mother"):
        raise RuntimeError("EP01_QUEUE_INCONSISTENT_CHECKPOINT")
    return obj


def current_runs() -> list[dict]:
    rows = gh_json("run", "list", "--workflow", WORKFLOW,
                   "--event", "workflow_dispatch", "--limit", "100",
                   "--json", "databaseId,displayTitle,status,conclusion,createdAt")
    if not isinstance(rows, list):
        raise RuntimeError("EP01_QUEUE_INVALID_RUN_LIST")
    return rows


def dispatch_one(shot_id: str) -> int:
    before = {str(x["databaseId"]) for x in current_runs()}
    print("EP01_QUEUE_DISPATCH", shot_id, flush=True)
    command("gh", "workflow", "run", WORKFLOW, "--ref", "main",
            "-f", f"shot_id={shot_id}")
    deadline = time.monotonic() + 180
    expected_title = f"EP01 cena-mãe {shot_id}"
    while time.monotonic() < deadline:
        matches = [
            x for x in current_runs()
            if str(x.get("databaseId")) not in before
            and x.get("displayTitle") == expected_title
        ]
        if matches:
            run_id = int(max(matches, key=lambda x: x["databaseId"])["databaseId"])
            print("EP01_QUEUE_CHILD_RUN", shot_id, run_id, flush=True)
            return run_id
        time.sleep(10)
    raise RuntimeError(f"EP01_QUEUE_CHILD_NOT_VISIBLE {shot_id}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max-shots", type=int, default=39)
    args = p.parse_args()
    if not os.environ.get("GH_TOKEN"):
        raise RuntimeError("EP01_QUEUE_GH_TOKEN_MISSING")
    config = json.loads(REQUEST.read_text(encoding="utf-8"))
    if (config.get("schema") != SCHEMA
            or config.get("channel") != CHANNEL
            or config.get("video_id") != VIDEO
            or config.get("allow_automatic_proxy_calls") is not True
            or config.get("single_paid_image_per_child_workflow") is not True
            or config.get("retry_on_failure") is not False
            or config.get("youtube_upload") is not False
            or config.get("approved_for_final_render") is not False):
        raise RuntimeError("EP01_QUEUE_REQUEST_INVALID")
    quota = config.get("max_new_images")
    if (type(quota) is not int or not 1 <= quota <= 39
            or not 1 <= args.max_shots <= 39):
        raise RuntimeError("EP01_QUEUE_MAX_INVALID")
    max_shots = min(quota, args.max_shots)
    completed = []
    for _ in range(max_shots):
        inv = current_inventory()
        missing = inv["missing_original_mother_shot_ids"]
        if not missing:
            print("EP01_QUEUE_ALL_MOTHERS_ARCHIVED", flush=True)
            break
        shot_id = missing[0]
        # Prepare must verify the actual SHA-archived sources BEFORE spending.
        command("git", "reset", "--hard", "origin/main")
        from videoforge.ep01_shot_mother import prepare
        preflight = prepare(shot_id)
        print("EP01_QUEUE_PREFLIGHT", shot_id,
              len(preflight["references"]), "refs", flush=True)
        child = dispatch_one(shot_id)
        # '--exit-status' fails the controller if the child fails; no retry.
        command("gh", "run", "watch", str(child), "--exit-status", "--interval", "15")
        for _ in range(6):
            next_inv = current_inventory()
            if shot_id not in next_inv["missing_original_mother_shot_ids"]:
                break
            time.sleep(5)
        else:
            raise RuntimeError(f"EP01_QUEUE_CHILD_NO_ARCHIVE {shot_id} {child}")
        completed.append({"shot_id": shot_id, "workflow_run_id": child})
        print("EP01_QUEUE_ARCHIVED", shot_id, "run", child,
              "done", len(completed), "remaining",
              next_inv["visual_shots_missing_original_mother"], flush=True)
    print("EP01_QUEUE_SUMMARY", json.dumps({
        "generated_in_this_queue": completed,
        "latest_checkpoint": current_inventory()["visual_shots_with_original_mother"],
        "human_visual_approval": False,
        "rig_ready": False,
        "mp4_generated": False,
        "youtube_uploaded": False,
    }, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("EP01_QUEUE_STOP_NO_RETRY", repr(exc), file=sys.stderr, flush=True)
        sys.exit(2)
