"""Render de depuracao (com marca d'agua) para sprites de rig NAO aprovados.

Conversa tecnica: permite observar cabeca, olhos e capa sem passar na
validacao de producao. NAO cria approval, NAO publica YouTube.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from . import animate_layers, mesh_rig, mvp, proxy_images, remotion_preview, scene_layers
from .errors import VideoForgeError
from .paths import _check_symlinks


class DraftPreviewError(VideoForgeError):
    pass


def _dir(channel: str, video_id: str, scene: str) -> Path:
    proxy_images.destination(channel,video_id,scene)
    folder=(proxy_images.ROOT/"output"/channel/"videos"/video_id/
            "rig-draft-previews"/scene)
    _check_symlinks(folder,stop_at=proxy_images.ROOT)
    return folder


def _json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>200_000:
        raise DraftPreviewError("DRAFT_JSON_MISSING_OR_UNSAFE")
    try:
        o=json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError,ValueError,OSError) as exc:
        raise DraftPreviewError("DRAFT_JSON_INVALID") from exc
    if not isinstance(o,dict):
        raise DraftPreviewError("DRAFT_JSON_NOT_OBJECT")
    return o


def prepare(original_dir: Path, candidate_dir: Path, *,
            channel: str, video_id: str, scene: str, duration: int=8) -> Path:
    if duration != 8:
        raise DraftPreviewError("DRAFT_DURATION_FIXED_TO_8_SECONDS")
    dest=_dir(channel,video_id,scene)
    public=proxy_images.ROOT/"motion-remotion/public/vf-scene"
    _check_symlinks(public,stop_at=proxy_images.ROOT)
    if dest.exists() or public.exists():
        raise DraftPreviewError("DRAFT_OUTPUT_ALREADY_EXISTS")
    if candidate_dir.is_symlink() or not candidate_dir.is_dir():
        raise DraftPreviewError("DRAFT_CANDIDATE_MISSING")
    rig=_json(candidate_dir/"rig.json")
    qa=_json(candidate_dir/"candidate.qa.json")
    origin=_json(candidate_dir/"asset-provenance.json")
    if (rig.get("schema")!=mesh_rig.SCHEMA or rig.get("candidate_only") is not True or
        any(rig.get("human_review",{}).get(k) is not False for k in (
            "no_duplicate_parts","pixel_alignment","occlusion_order")) or
        qa.get("status")!="draft_unapproved" or
        qa.get("rig_ready_for_remotion") is not False or
        qa.get("human_visual_approval") is not False or
        origin.get("human_review") is not False or
        origin.get("model_calls")!=0):
        raise DraftPreviewError("DRAFT_NOT_VERIFIED_UNAPPROVED")
    if (rig.get("channel"),rig.get("video_id"),rig.get("scene"))!=(channel,video_id,scene):
        raise DraftPreviewError("DRAFT_CROSS_CHANNEL")
    allowed=set(mesh_rig.ASSET_NAMES.values())|{"cape-front.png"}
    if set(rig.get("assets",{}))!=allowed:
        raise DraftPreviewError("DRAFT_SIX_PIECES_REQUIRED")
    # Copia e verifica camadas da origem, com o contrato do sistema existente.
    source,manifest=animate_layers._trusted_assets(
        original_dir,channel,video_id,scene)
    ref=manifest["source"]
    if (rig.get("source_sha256")!=ref["sha256"] or
        origin.get("source_scene_sha256")!=ref["sha256"] or
        rig.get("canvas")!={"width":ref["width"],"height":ref["height"]}):
        raise DraftPreviewError("DRAFT_SOURCE_HASH_OR_CANVAS_MISMATCH")
    for name in sorted(allowed):
        png=candidate_dir/name
        data=scene_layers._read_png(png)
        if hashlib.sha256(data).hexdigest()!=rig["assets"][name]:
            raise DraftPreviewError("DRAFT_PNG_HASH_MISMATCH")
        info=scene_layers.png_info(
            data,require_alpha=True,
            min_visible_fraction=.00001 if name.startswith("eyes-") else .005)
        if (info["width"],info["height"])!=(ref["width"],ref["height"]):
            raise DraftPreviewError("DRAFT_PNG_DIMENSIONS_MISMATCH")
    if rig.get("head_max_deg",0)>2.0 or len(rig.get("blink_frames",[]))>10:
        raise DraftPreviewError("DRAFT_ANIMATION_OUT_OF_RANGE")
    layers={key:"vf-scene/rig/"+name for key,name in mesh_rig.ASSET_NAMES.items()}
    layers["capeFront"]="vf-scene/rig/cape-front.png"
    rig_props={
        "schema":mesh_rig.RIG_SCHEMA,"canvas":rig["canvas"],
        "layers":layers,"neckPivot":rig["neck_pivot"],
        "headMaxDeg":rig["head_max_deg"],"blinkFrames":rig["blink_frames"],
        "capeMesh":{
            "bounds":rig["cape_mesh"]["bounds"],
            "rows":rig["cape_mesh"]["rows"],
            "columns":rig["cape_mesh"]["columns"],
            "amplitudePx":rig["cape_mesh"]["amplitude_px"],
        },
    }
    dest.mkdir(parents=True)
    (public/"rig").mkdir(parents=True)
    for name in remotion_preview.FILES:
        shutil.copyfile(source/name,public/name)
    for name in sorted(allowed):
        shutil.copyfile(candidate_dir/name,public/"rig"/name)
    mvp._command(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                  "-f","lavfi","-i","anullsrc=r=48000:cl=stereo",
                  "-t","8","-c:a","pcm_s16le",str(public/"silence.wav")],timeout=60)
    props=remotion_preview.make_props(channel=channel,video_id=video_id,
        scene=scene,duration=duration,preset="ultrassutil",
        source_sha=ref["sha256"],rig=rig_props)
    props["draftPreview"]=True
    props["youtubeUpload"]=False
    props["candidate_only"]=True
    (dest/"draft-props.json").write_text(
        json.dumps(props,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return dest


def verify(channel: str, video_id: str, scene: str) -> dict:
    dest=_dir(channel,video_id,scene)
    props=_json(dest/"draft-props.json")
    video=dest/"rig-draft-preview.mp4"
    if (props.get("draftPreview") is not True or
        props.get("candidate_only") is not True or
        props.get("youtubeUpload") is not False or
        not video.is_file() or video.is_symlink() or video.stat().st_size<20_000):
        raise DraftPreviewError("DRAFT_MP4_INVALID_OR_UNMARKED")
    qa=mvp._verify_mp4(video,expected=8.0,minimum=7.5,maximum=8.5)
    f1=animate_layers._frame_md5(video,1.0)
    f2=animate_layers._frame_md5(video,5.0)
    if not f1.startswith("MD5=") or f1==f2:
        raise DraftPreviewError("DRAFT_MOTION_NOT_DETECTED")
    qa.update({
        "schema":"videoforge/rig-draft-video-qa/v1",
        "source_sha256":props["layerSourceHash"],"visual_review":"pending",
        "asset_human_approval":False,"body_inpainting_completed":False,
        "technical_mesh_rig_preview":True,"watermark":True,
        "publishable":False,"youtube_uploaded":False,"audio_is_silent":True,
        "motion_detected":True,
    })
    (dest/"draft-video.qa.json").write_text(json.dumps(
        qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return qa


def main() -> int:
    parser=argparse.ArgumentParser(description="Remotion DRAFT com marca d'agua")
    parser.add_argument("action",choices=("prepare","verify"))
    parser.add_argument("--source-dir",type=Path)
    parser.add_argument("--candidate-dir",type=Path)
    parser.add_argument("--channel",required=True)
    parser.add_argument("--video-id",required=True)
    parser.add_argument("--scene",required=True)
    args=parser.parse_args()
    try:
        if args.action=="prepare":
            if not args.source_dir or not args.candidate_dir:
                raise DraftPreviewError("DRAFT_INPUTS_REQUIRED")
            report=prepare(args.source_dir,args.candidate_dir,
                channel=args.channel,video_id=args.video_id,scene=args.scene)
            print("Rascunho preparado:",report)
        else:
            print(json.dumps(verify(args.channel,args.video_id,args.scene)))
        return 0
    except (VideoForgeError,scene_layers.LayerError,
            proxy_images.ProxyImageError) as exc:
        print("DRAFT_BLOCKED:",exc,file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
