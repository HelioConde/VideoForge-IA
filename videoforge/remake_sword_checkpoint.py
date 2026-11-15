"""Persist REAL C01-P02 technical preview evidence; never approve art or publish.

The GitHub host lacks FFmpeg: the Remotion container writes video QA;
this host rehashes bytes and persists only the verified manifests.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import sys

from .remake_autopilot import ROOT,EPISODE
from .errors import VideoForgeError
from .remake_sword_preview import read_json

SHA=lambda blob:hashlib.sha256(blob).hexdigest()
BEGIN="<!-- REMAKE-C01-P02-START -->"
END="<!-- REMAKE-C01-P02-END -->"
QA_NAME="QA-C01-P02-REMAKE-V2.json"

def persist(output:Path,root:Path=ROOT)->dict:
    files=("c01-p02-three-sword-technical.mp4","preview.qa.json",
           "stage.qa.json","props.json")
    if any((output/f).is_symlink() or not (output/f).is_file()
           for f in files):
        raise VideoForgeError("REMAKE_SWORD_RENDER_ARTIFACT_INCOMPLETE")
    mp4=(output/files[0]).read_bytes()
    qa=read_json(output/files[1])
    stage=read_json(output/files[2])
    props=read_json(output/files[3])
    run=os.environ.get("GITHUB_RUN_ID","")
    if not run.isdigit() or int(run)<=0:
        raise VideoForgeError("REMAKE_SWORD_GITHUB_RUN_ID_REQUIRED")
    if (qa.get("schema")!="videoforge/remake-sword-preview-qa/v1"
        or qa.get("shot")!="C01-P02"
        or qa.get("technical_preview_only") is not True
        or qa.get("official_video_approved") is not False
        or qa.get("human_visual_approved") is not False
        or qa.get("youtube_uploaded") is not False
        or qa.get("fps")!=30 or qa.get("frames")!=90
        or qa.get("mp4_sha256")!=SHA(mp4)
        or qa.get("source_run_id")!=stage.get("source_run_id")
        or qa.get("source_artifact")!=stage.get("source_artifact")
        or qa.get("neutral_mae_rgb")!=stage.get("neutral_mae_rgb")
        or qa.get("source_mother_sha256")!=stage.get("hashes",{}).get("scene-mother")
        or qa.get("anchor_sha256")!=stage.get("anchor_sha256")
        or stage.get("render_ready") is not True
        or stage.get("human_visual_approved") is not False
        or stage.get("official_video_approved") is not False
        or stage.get("youtube_uploaded") is not False
        or props.get("officialVideoApproved") is not False
        or props.get("youtubeUploaded") is not False
        or props.get("rig",{}).get("humanVisualReview") is not False
        or props.get("rig",{}).get("motherSha256")!=qa.get("source_mother_sha256")):
        raise VideoForgeError("REMAKE_SWORD_ARTIFACT_QA_OR_SHA_INVALID")
    ep=Path(root)/EPISODE
    planpath=ep/"remake-ep01-planos.json"
    statepath=ep/"estado-atual.json"
    master=ep/"ESTADO-ATUAL.md"
    history=ep/"HISTORICO-DESENVOLVIMENTO.md"
    plan=read_json(planpath)
    shots=[x for x in plan.get("shots",[]) if x.get("shot_id")=="C01-P02"]
    if len(shots)!=1 or shots[0].get("frame_start")!=60 or shots[0].get("frame_end_exclusive")!=150:
        raise VideoForgeError("REMAKE_SWORD_SHOT_REGISTRY_CHANGED")
    shot=shots[0]
    state=read_json(statepath)
    if state.get("locks",{}).get("no_youtube_upload") is not True:
        raise VideoForgeError("REMAKE_SWORD_PUBLICATION_LOCK_MISSING")
    recorded={
      **qa,
      "github_run_id":int(run),
      "artifact_name":"vf-remake-c01-p02-three-preview-"+run,
      "artifact_retention_days":90,
      "mp4_committed_to_git":False,
      "image_generation_calls":0,
    }
    qapath=ep/QA_NAME
    if qapath.is_file():
        if read_json(qapath)==recorded:
            return recorded
        raise VideoForgeError("REMAKE_SWORD_QA_ALREADY_RECORDED_DO_NOT_OVERWRITE")
    shot["technical_preview_sha256"]=qa["mp4_sha256"]
    shot["technical_preview_artifact"]=recorded["artifact_name"]
    shot["technical_preview_qa_path"]=QA_NAME
    shot["asset_status"]="technical_shot_candidate_artifact_pending_art_review"
    shot["human_visual_approved"]=False
    shot["motion_qa_passed"]=False
    shot["qa_approved"]=False
    shot["publishable"]=False
    shot["mp4_created"]=True # isolated TECHNICAL preview, not episode
    state["c01_p02_sword_preview_v2"]={
      "status":"technical_3s_articulated_preview_only",
      "run_id":int(run),"source_art_run_id":qa["source_run_id"],
      "artifact":recorded["artifact_name"],
      "mother_sha256":qa["source_mother_sha256"],
      "anchor_sha256":qa["anchor_sha256"],
      "mp4_sha256":qa["mp4_sha256"],
      "technical_neutral_roundtrip_mae_rgb":qa["neutral_mae_rgb"],
      "human_visual_approved":False,"publishable":False,
      "full_episode_mp4":False,"youtube_uploaded":False,
      "next_step":"Review source identity, seams, hand/steel motion and persistent art; do not publish"
    }
    state["next_action"]=state["c01_p02_sword_preview_v2"]["next_step"]
    msg=(BEGIN+"\n### C01-P02 — primeira prévia articulada Three.js (QA técnico)\n"
      f"- MP4 ThreeCanvas técnico no artifact \`{recorded['artifact_name']}\` do run \`{run}\`; "
      f"SHA256 \`{qa['mp4_sha256']}\`, 90 frames/3s, 1080×1920/30fps.\n"
      f"- Arte real de origem: run \`{qa['source_run_id']}\`, artifact "
      f"\`{qa['source_artifact']}\`, cena-mãe SHA \`{qa['source_mother_sha256']}\`.\n"
      f"- QA neutro MAE \`{qa['neutral_mae_rgb']}\`. Lâmina, mão e bainha "
      "independentes; ainda requer revisão humana de costuras/contato e identidade.\n"
      f"- Evidência versionada: \`{QA_NAME}\`; PNGs/MP4 apenas nos artifacts (90 dias).\n"
      "- **Não é render oficial, não é aprovação artística, não é episódio "
      "completo e não foi publicado no YouTube.**\n"+END)
    text=master.read_text(encoding="utf-8")
    if (BEGIN in text)!=(END in text):
        raise VideoForgeError("REMAKE_SWORD_MASTER_MARKERS_INVALID")
    if BEGIN in text:
        a=text.index(BEGIN);b=text.index(END,a)+len(END)
        text=text[:a]+msg+text[b:]
    else:
        text=text.replace("\n","\n\n"+msg+"\n\n",1)
    qapath.write_text(json.dumps(recorded,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    planpath.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    master.write_text(text,encoding="utf-8")
    when=datetime.now(timezone.utc).isoformat()
    with history.open("a",encoding="utf-8") as f:
        f.write(f"\n## {when} C01-P02 — QA Three.js 90 frames com fonte original\n\n"
          f"- Run \`{run}\`, artifact \`{recorded['artifact_name']}\`, SHA MP4 "
          f"\`{qa['mp4_sha256']}\`, source run \`{qa['source_run_id']}\`, "
          f"MAE neutro \`{qa['neutral_mae_rgb']}\`.\n"
          "- Apenas prévia técnica; aprovação visual false, sem vídeo completo "
          "nem publicação. Próximo: inspeção artística e continuação C01-P03.\n")
    return recorded

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,type=Path)
    args=ap.parse_args()
    try:
        print("REMAKE_SWORD_CHECKPOINT",json.dumps(persist(args.input),ensure_ascii=False))
        return 0
    except (ValueError,OSError,VideoForgeError,KeyError) as exc:
        print("REMAKE_SWORD_CHECKPOINT_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
