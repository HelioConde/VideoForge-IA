"""Generate one versioned C07/C08 continuity mother per GitHub Action.
Never replace historical images, do not approve art, rigs or YouTube.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from .errors import VideoForgeError
from .image_generation_policy import assert_image_generation_allowed
from .production_art import archived_reference
from .scene_layers import png_info
from . import proxy_images

ROOT = Path(__file__).resolve().parents[1]
EP = Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
PLAN = "CONTINUIDADE-C07-C08-V2.json"
PRODUCER = "production-continuity-v2-mother"


def read_plan(root=ROOT):
    doc = json.loads((Path(root) / EP / PLAN).read_text(encoding="utf-8"))
    shots = doc["shots"]
    expected = [
        "C07-P01", "C07-P02", "C07-P03", "C07-P04", "C08-P01",
        "C08-P02", "C08-P03", "C08-P04", "C08-P05"
    ]
    if (doc["schema"] != "videoforge/ep01-c07c08-continuity-v2"
            or doc["editorial_original"]["shots"] != 40
            or doc["editorial_v2"]["shots"] != 42
            or doc["rules"]["auto_youtube_upload"] is not False
            or doc["rules"]["maximum_paid_calls_per_child_run"] != 1
            or [s["id"] for s in shots] != expected):
        raise ValueError("CONTINUITY_V2_PLAN_INVALID")
    t = 2070
    for item in shots:
        if item["start_frame"] != t or item["end_exclusive"] <= t:
            raise ValueError("CONTINUITY_V2_BAD_TIMELINE")
        t = item["end_exclusive"]
        if item["scene_mother_approved"] is not False or item["rig_approved"] is not False:
            raise ValueError("CONTINUITY_V2_FALSE_APPROVAL")
        if item["source_policy"] == "generate":
            ids = item["reference_asset_ids"]
            if not 1 <= len(ids) <= 8 or len(set(ids)) != len(ids):
                raise ValueError("CONTINUITY_V2_BAD_BIBLE_REFS")
    if t != 2940 or sum(s["source_policy"] == "generate" for s in shots) != 7:
        raise ValueError("CONTINUITY_V2_COUNT_INVALID")
    return doc


def name(shot_id):
    if not re.fullmatch(r"C0[78]-P0[1-5]", shot_id):
        raise ValueError("CONTINUITY_V2_BAD_SHOT")
    return shot_id.lower() + "-continuity-v2-scene-mother.png"


def archived(shot_id, root=ROOT):
    folder = Path(root) / EP / "assets" / "geracoes" / PRODUCER
    if not folder.exists():
        return None
    if folder.is_symlink():
        raise ValueError("CONTINUITY_V2_BAD_ARCHIVE")
    found = []
    for run in folder.iterdir():
        if run.is_symlink():
            raise ValueError("CONTINUITY_V2_BAD_ARCHIVE")
        if not run.is_dir() or not run.name.isdigit():
            continue
        image = run / name(shot_id)
        manifest = run / "manifesto-geracoes.json"
        if image.is_symlink() or manifest.is_symlink():
            raise ValueError("CONTINUITY_V2_BAD_ARCHIVE")
        if not image.exists():
            continue
        if not manifest.is_file():
            raise ValueError("CONTINUITY_V2_INCOMPLETE_ARCHIVE")
        doc = json.loads(manifest.read_text(encoding="utf-8"))
        match = [m for m in doc.get("images", []) if m.get("file") == image.name]
        if (doc.get("schema") != "videoforge/permanent-generated-image-archive/v1"
                or doc.get("producer") != PRODUCER
                or doc.get("channel") != "alchemy-lab"
                or doc.get("video_id") != "mmorpg-conquiste-a-princesa-ep01"
                or doc.get("github_run_id") != int(run.name)
                or len(match) != 1):
            raise ValueError("CONTINUITY_V2_INVALID_MANIFEST")
        data = image.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != match[0]["sha256"]:
            raise ValueError("CONTINUITY_V2_SHA_MISMATCH")
        info = png_info(data, require_alpha=False)
        found.append({
            "file": str(image.relative_to(Path(root))).replace("\\", "/"),
            "sha256": digest,
            "dimensions": [info["width"], info["height"]],
            "human_visual_approval": False,
            "source_status": "versioned_candidate_pending_review",
            "run_id": int(run.name),
        })
    return max(found, key=lambda x: x["run_id"]) if found else None


def prepare(shot_id, root=ROOT):
    plan = read_plan(root)
    shot = next((x for x in plan["shots"] if x["id"] == shot_id), None)
    if shot is None or shot["source_policy"] != "generate":
        raise ValueError("CONTINUITY_V2_NOT_REQUESTED")
    if archived(shot_id, root):
        raise ValueError("CONTINUITY_V2_ALREADY_GENERATED")
    originals = []
    refs = []
    for asset_id in shot["reference_asset_ids"]:
        candidate = archived_reference("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", asset_id, root)
        if candidate is None:
            raise ValueError("CONTINUITY_V2_BIBLE_MISSING " + asset_id)
        path = Path(root) / EP / candidate["path"]
        if (path.is_symlink() or not path.is_file()
                or not path.resolve().is_relative_to((Path(root) / EP).resolve())):
            raise ValueError("CONTINUITY_V2_INVALID_REFERENCE")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != candidate["sha256"]:
            raise ValueError("CONTINUITY_V2_REFERENCE_SHA_MISMATCH")
        originals.append(data)
        refs.append({"asset_id": asset_id, "sha256": candidate["sha256"]})
    prompt = (
        "CRIE UMA UNICA CENA-MAE 2D anime/manhwa semirrealista cinematografica 9:16 "
        "de dorama fantasia medieval. Use as imagens verdadeiras anexadas da Biblia "
        "Visual para manter arquitetura de Arken, trajes, pessoas, cartografia e carrinho "
        "IDENTICOS entre tomadas. Nao crie quadrinhos ou uma montagem, nem texto ou HUD. "
        "A continuidade espacial e obrigatoria: Elara FOGE para DIREITA DA TELA; "
        "perseguidores sempre atras, chegando da ESQUERDA. Carrinho estaciona "
        "junto a parede DIREITA ate KAEL, SOZINHO, empurrar a carroca para atravesar "
        "o beco. Soldados NUNCA ajudam Kael ou seguram o carrinho. "
        "Barricada separa perseguidores (esquerda) dos fugitivos (direita). "
        "Maos integradas naturalmente ao gesto, NAO gerar maos separadas, "
        "membros duplicados ou outras pessoas no quadro. "
        f"TOMADA {shot_id}: {shot['beat']}. "
        f"DESCRICAO VISUAL: {shot['visual_prompt']}. "
        "Uma ilustracao unica de instante congelado, com perspectiva plausivel, "
        "luz dourada-violeta consistente e proporcoes humanas. Sem violencia grafica. "
        "Resultado candidato, pendente de aprovacao humana. NAO publicar."
    )
    return shot, originals, refs, prompt


def generate(shot_id, url, root=ROOT):
    assert_image_generation_allowed("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", Path(root))
    shot, originals, refs, prompt = prepare(shot_id, root)
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt, "size": "1024x1536",
        "n": 1, "background": "opaque", "output_format": "png",
        "response_format": "b64_json", "stream": False,
        "images": [
            {"image_url": "data:image/png;base64," + base64.b64encode(data).decode("ascii")}
            for data in originals
        ],
    }
    result = proxy_images.call_proxy(
        url, "/v1/images/edits", os.getenv("CODEX_PROXY_API_KEY", ""), payload
    )
    binary, extension = proxy_images.decode_image(result)
    if extension != ".png":
        raise ValueError("CONTINUITY_V2_NOT_PNG")
    info = png_info(binary, require_alpha=False)
    if not 512 <= info["width"] <= 2048 or not 512 <= info["height"] <= 3072:
        raise ValueError("CONTINUITY_V2_BAD_DIMENSIONS")
    if info["width"] >= info["height"]:
        raise ValueError("CONTINUITY_V2_NOT_VERTICAL")
    out = Path(root) / "output" / "alchemy-lab" / "videos" / "mmorpg-conquiste-a-princesa-ep01" / "imagens"
    out.mkdir(parents=True, exist_ok=True)
    path = out / name(shot_id)
    if path.exists():
        raise ValueError("CONTINUITY_V2_DUPLICATE_OUTPUT")
    path.write_bytes(binary)
    sha = hashlib.sha256(binary).hexdigest()
    path.with_suffix(".production.json").write_text(json.dumps({
        "schema": "videoforge/continuity-candidate/v2",
        "channel": "alchemy-lab", "video_id": "mmorpg-conquiste-a-princesa-ep01",
        "asset_id": path.stem, "candidate_scene_shot_id": shot_id,
        "source_originals_sha_verified": [{"id": x["asset_id"], "sha256": x["sha256"]} for x in refs],
        "shot_id": shot_id,
        "sha256": sha, "source_references": refs,
        "human_visual_approval": False, "rig_ready": False,
        "official_mp4": False, "youtube_uploaded": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"shot": shot_id, "sha256": sha, "new_png": path.name, "human_visual_approval": False}


def revised_camera_plan(old_plan, root=ROOT, require_generated=True):
    revision = read_plan(root)
    original = {s["id"]: s for s in old_plan["shots"]}
    region = []
    for shot in revision["shots"]:
        row = dict(original.get(shot["id"], original["C07-P03"]))
        row.update({
            "id": shot["id"],
            "narrative_beat": shot["beat"],
            "start_frame": shot["start_frame"],
            "duration_frames": shot["end_exclusive"] - shot["start_frame"],
            "approval_status": "pending_human_review",
            "rig": {"enabled": False, "independent_hands": False, "required_components": []},
            "camera": {
                "mode": "continuity_v2_review", "start": {"zoom": 1, "x": 50, "y": 50},
                "end": {"zoom": 1.015, "x": 50, "y": 50}, "dolly": 0, "true_parallax": False
            },
            "lighting": {"exposure_start": 1, "exposure_end": 1, "warm_glow": 0},
            "focus": {"mode": "original_painted_focus", "blur_start_px": 0, "blur_end_px": 0},
            "direction_reviewed": False, "revision": "continuity-v2",
        })
        # A camera-only preview must disclose unsolved blocking/physical motion.
        # These labels are not rig or visual approvals and never move entire PNGs.
        from .ep01_continuity_motion import preview_gate
        gate = preview_gate(shot["id"], root)
        if gate:
            row["continuity_gate"] = gate
            row["qa_required"] = list(dict.fromkeys(
                row.get("qa_required", []) + ["independent_C07_C08_temporal_rig_and_axis_review"]))
        if shot["source_policy"].startswith("reuse:"):
            old_id = shot["source_policy"].split(":", 1)[1]
            row["source"] = original[old_id]["source"]
        else:
            row["source"] = archived(shot["id"], root)
            if row["source"] is None and require_generated:
                raise ValueError("CONTINUITY_V2_MOTHER_PENDING " + shot["id"])
        region.append(row)
    final = []
    for shot in old_plan["shots"]:
        if shot["id"] == "C07-P01":
            final.extend(region)
        if shot["id"].startswith("C07-") or shot["id"].startswith("C08-"):
            continue
        final.append(shot)
    if len(final) != 42 or sum(s["duration_frames"] for s in final) != 4890:
        raise ValueError("CONTINUITY_V2_TIMELINE_INCONSISTENT")
    copy = dict(old_plan)
    copy["shots"] = final
    copy["revision"] = "continuity-v2"
    return copy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shot-id")
    parser.add_argument("--url")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        print(json.dumps({"shots": len(read_plan()["shots"]), "new_candidates": 7, "approved": 0}))
        return 0
    if not args.shot_id or not args.url:
        parser.error("Need --shot-id and --url")
    try:
        print(json.dumps(generate(args.shot_id, args.url), ensure_ascii=False))
        return 0
    except (ValueError, OSError, VideoForgeError, proxy_images.ProxyImageError) as exc:
        print("CONTINUITY_V2_STOP", str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
