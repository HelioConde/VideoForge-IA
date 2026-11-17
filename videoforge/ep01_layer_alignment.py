"""Alinhar por preenchimento EXATO de borda um background 2 px menor.

Não regenera imagens, não escala a arte, não aprova rig nem publica vídeo.
Preserva integralmente os pixels do PNG bruto do proxy e liga ambos por SHA.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from . import ep01_shot_layers as layers

ALIGNED_ASSET="c01-p02-background-aligned"
ALIGNMENT_PRODUCER="production-shot-alignment-v2"


def align(root: Path = ROOT) -> dict:
    from PIL import Image
    root=Path(root)
    plan,mother,original=layers.mother_source(root)
    bg=layers.archived_layer("background-clean",root)
    if bg is None:
        raise VideoForgeError("EP01_BG_ALIGNMENT_SOURCE_NOT_ARCHIVED")
    archive=root/REL/"assets"/"geracoes"/layers.PRODUCER/str(bg["run_id"])
    file=archive/"c01-p02-background-clean.png"
    meta=archive/"c01-p02-background-clean.production.json"
    if any(f.is_symlink() or not f.is_file() for f in (file,meta)):
        raise VideoForgeError("EP01_BG_ALIGNMENT_SOURCE_OR_META_MISSING")
    try:
        details=json.loads(meta.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError) as exc:
        raise VideoForgeError("EP01_BG_ALIGNMENT_META_INVALID") from exc
    if (details.get("source_mother_sha256")!=plan["mother_sha256"]
        or details.get("sha256")!=bg["sha256"]
        or details.get("asset_id")!="c01-p02-background-clean"
        or details.get("technical_qa")!="rejected_canvas_mismatch"):
        raise VideoForgeError("EP01_BG_ALIGNMENT_SOURCE_NOT_ELIGIBLE")
    with Image.open(file) as source:
        if source.format!="PNG":
            raise VideoForgeError("EP01_BG_ALIGNMENT_SOURCE_NOT_PNG")
        native=source.convert("RGB")
    goal=(original["width"],original["height"])
    # Pad right/bottom edges only, no stretching/cropping/translation.
    delta_y=goal[1]-native.height
    if (native.width!=goal[0] or not 1<=delta_y<=2):
        raise VideoForgeError("EP01_BG_ALIGNMENT_DIFFERENCE_TOO_LARGE")
    out=Image.new("RGB",goal)
    out.paste(native,(0,0))
    row=native.crop((0,native.height-1,native.width,native.height))
    for i in range(delta_y):
        out.paste(row,(0,native.height+i))
    folder=root/"output"/CHANNEL/"videos"/VIDEO/"imagens"
    folder.mkdir(parents=True,exist_ok=True)
    final=folder/(ALIGNED_ASSET+".png")
    report=folder/(ALIGNED_ASSET+".production.json")
    if final.is_symlink() or report.is_symlink() or final.exists() or report.exists():
        raise VideoForgeError("EP01_BG_ALIGNMENT_OUTPUT_EXISTS")
    out.save(final,"PNG",optimize=True)
    blob=final.read_bytes()
    metadata={
      "schema":"videoforge/ep01-background-alignment/v1",
      "channel":CHANNEL,"video_id":VIDEO,"asset_id":ALIGNED_ASSET,
      "candidate_scene_shot_id":"C01-P02",
      "sha256":hashlib.sha256(blob).hexdigest(),
      "source_mother_sha256":plan["mother_sha256"],
      "source_originals_sha_verified":[{
        "id":"c01-p02-background-clean","sha256":bg["sha256"],
        "path":str((REL/"assets"/"geracoes"/layers.PRODUCER/str(bg["run_id"])/
                    "c01-p02-background-clean.png").as_posix())
      }],
      "technical_qa":"canvas_aligned_lossless_original_pixels_plus_2_edge_rows",
      "alignment":{"operation":"replicate_last_row_at_bottom","pixels_added":delta_y,
                   "source_canvas":[native.width,native.height],
                   "target_canvas":[out.width,out.height],
                   "source_pixels_resampled":False,"source_pixels_shifted":False},
      "human_visual_approval":False,"recomposition_review":"pending",
      "rig_approved":False,"youtube_uploaded":False,"mp4_generated":False,
      "image_provider_calls":0,
    }
    report.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_BACKGROUND_ALIGNED_NO_PAID_RETRY",
          json.dumps({"sha256":metadata["sha256"],"delta_y":delta_y,"pixels_resampled":False}))
    return metadata


if __name__=="__main__":
    try:
        align()
    except (ValueError,OSError,VideoForgeError) as exc:
        print("EP01_BACKGROUND_ALIGNMENT_BLOCKED",str(exc),file=sys.stderr)
        raise SystemExit(2)
