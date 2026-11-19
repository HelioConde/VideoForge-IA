"""Assemble a technical review cut from the contiguous prefix of verified camera artifacts."""
import argparse
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from scripts import ep01_action_production_queue as queue
from videoforge import ep01_camera_batch as camera


def validate_clip(folder, shot):
    props = camera.read(folder / "props.json")
    qa = camera.read(folder / "qa.json")
    expected = dict(shot)
    if shot["source"]:
        expected["sourceFile"] = "vf-ep01-camera-batch/" + shot["source"]["sha256"] + ".png"
    if (props["shots"] != [expected] or props["durationFrames"] != shot["duration_frames"]
            or qa.get("technical_qa_passed") is not True or qa.get("all_frames_decoded") is not True
            or qa.get("technical_preview_only") is not True or qa.get("official_episode_approved") is not False
            or qa.get("character_rig_approved") is not False or qa.get("audio_status") != "not_included"
            or qa.get("mp4_sha256") != camera.sha(folder / "preview.mp4")):
        raise ValueError("Stale or unverified camera clip: " + shot["id"])
    return qa["mp4_sha256"]


def assemble(destination):
    ledger = queue.gh("api", "repos/HelioConde/VideoForge-IA/contents/" + queue.STATE_PATH +
                      "?ref=state/multi-agent-runtime", "-H", "Accept: application/vnd.github.raw+json", json_out=True)
    queue.QueueRemote._validate_snapshot(ledger)
    shots = camera.build_plan(revision="continuity-v2")["shots"]
    clips = []
    used = []
    with TemporaryDirectory() as tmp:
        staging = Path(tmp)
        for shot in shots:
            src = shot["source"]["sha256"] if shot["source"] else queue.digest(queue.ROOT / queue.PLAN)
            task = queue.id_for("camera_preview", shot["id"], None, src)
            attempt = ledger["attempts"].get(task, {})
            if attempt.get("status") != "preview_complete":
                break
            run = attempt["child_run_id"]
            name = f"ep01-camera-batch-{run}"
            artifacts = queue.gh("api", f"repos/HelioConde/VideoForge-IA/actions/runs/{run}/artifacts", json_out=True)
            if not any(a["id"] == attempt["artifact_id"] and a["name"] == name and not a["expired"]
                       for a in artifacts["artifacts"]):
                raise ValueError(f"Artifact unavailable for {shot['id']}")
            folder = staging / str(run)
            queue.gh("run","download",str(run),"-n",name,"-D",str(folder))
            clip = folder / shot["id"]
            sha = validate_clip(clip, shot)
            used.append({"shot_id":shot["id"], "run_id":run, "artifact_id":attempt["artifact_id"], "mp4_sha256":sha})
            clips.append(clip / "preview.mp4")
        if not clips:
            raise ValueError("No verified opening shot")
        destination.mkdir(parents=True, exist_ok=True)
        concat = staging / "clips.ffconcat"
        concat.write_text("".join(f"file '{p.relative_to(staging).as_posix()}'\n" for p in clips), encoding="utf8")
        output = destination / "EP01-previa-parcial-de-camera.mp4"
        subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-y","-f","concat","-safe","1","-i",str(concat),
                        "-vf","setpts=N/(30*TB)","-r","30","-c:v","libx264","-crf","17","-an","-movflags","+faststart",
                        str(output)], check=True)
    selected = shots[:len(used)]
    qa = camera.verify_video(output, sum(s["duration_frames"] for s in selected), camera.black_ranges({"shots":selected}))
    camera.write(destination/"qa.json",dict(qa, shots=used, source_revision="continuity-v2",
                 technical_camera_only=True, audio_included=False, rig_approved=False, final_episode=False))
    return qa


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    print(json.dumps(assemble(parser.parse_args().output)))
