"""Arquiva SOMENTE PNGs já existentes em artifacts GitHub Actions da obra.

Nunca chama modelos de imagem. Preserva SHA e origem, aplica aprovação
visual separada de QA técnico; não declara rig nem vídeo final.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import sys

CHANNEL = "alchemy-lab"
VIDEO = "mmorpg-conquiste-a-princesa-ep01"
BASE = Path("canal") / CHANNEL / "videos" / VIDEO
ASSETS = BASE / "assets"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_PNG_BYTES = 35_000_000

class ArchiveError(ValueError):
    pass

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def valid_png(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ArchiveError(f"SOURCE_NOT_SAFE: {path}")
    data = path.read_bytes()
    if not 80 <= len(data) < MAX_PNG_BYTES or not data.startswith(PNG_MAGIC):
        raise ArchiveError(f"INVALID_PNG: {path}")
    if data[12:16] != b"IHDR":
        raise ArchiveError(f"MISSING_IHDR: {path}")
    width, height = struct.unpack(">II", data[16:24])
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise ArchiveError(f"INVALID_DIMENSIONS: {path}")
    return {"sha256": sha(data), "bytes": len(data), "width": width, "height": height}

def jsonfile(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 300_000:
        raise ArchiveError(f"INVALID_META: {path}")
    meta = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(meta, dict):
        raise ArchiveError(f"INVALID_JSON: {path}")
    return meta

def save_existing(source: Path, target: Path, check_meta: dict | None = None) -> dict:
    info = valid_png(source)
    if check_meta is not None and check_meta.get("sha256") != info["sha256"]:
        raise ArchiveError(f"SHA_MISMATCH: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.is_symlink() or sha(target.read_bytes()) != info["sha256"]:
            raise ArchiveError(f"WOULD_OVERWRITE_DIFFERENT_ASSET: {target}")
    else:
        target.write_bytes(source.read_bytes())
    return {"path": str(target), **info}

def save_meta(source: Path, target: Path) -> None:
    payload = jsonfile(source)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf8") != encoded:
        raise ArchiveError(f"WOULD_OVERWRITE_META: {target}")
    target.write_text(encoded, encoding="utf8")

def archive(input_root: Path, repo_root: Path = Path(".")) -> dict:
    import os
    cwd = Path.cwd()
    os.chdir(repo_root)
    try:
        return _archive(input_root.resolve())
    finally:
        os.chdir(cwd)

def _archive(inp: Path) -> dict:
    if not inp.is_dir():
        raise ArchiveError("INPUT_ARTIFACT_FOLDER_MISSING")
    entries = []

    # Prancha aprovada apenas tecnicamente, NÃO artisticamente.
    ref = inp / "reference" / "character-bible.png"
    ref_meta = inp / "reference" / "character-bible.production.json"
    ref_report = jsonfile(ref_meta)
    if (ref_report.get("channel"),ref_report.get("video_id"),ref_report.get("asset_id")) != (CHANNEL, VIDEO, "character-bible"):
        raise ArchiveError("REFERENCE_ORIGIN_MISMATCH")
    entry = save_existing(ref, ASSETS / "referencias" / "character-bible.png", ref_report)
    entry.update(kind="visual_character_reference", source_run_id=43590930215,
                 qa_status="pending_human_visual_review")
    entries.append(entry)
    save_meta(ref_meta, ASSETS / "proveniencia" / "character-bible.production.json")

    for n in range(1,15):
        if n == 1:
            folder = inp / "first"
            run_id = 43591342058
        else:
            # Os artifacts do lote ficam cada qual numa pasta chamada
            # vf-real-batch-scene-alchemy-lab-...-{number}-{run_id}
            matches = list((inp / "batch").glob(f"vf-real-batch-scene-{CHANNEL}-{VIDEO}-{n}-43591745279"))
            if len(matches) != 1:
                raise ArchiveError(f"SCENE_BATCH_ARTIFACT_MISSING: {n}")
            folder = matches[0]
            run_id = 43591745279
        file = folder / f"cena-{n:02d}.png"
        report_file = folder / f"cena-{n:02d}.production.json"
        report = jsonfile(report_file)
        if (report.get("channel"),report.get("video_id"),report.get("number")) != (CHANNEL, VIDEO, n):
            raise ArchiveError(f"SCENE_ORIGIN_MISMATCH: {n}")
        entry = save_existing(file, ASSETS / "cenas-mae" / f"cena-{n:02d}.png", report)
        entry.update(kind="scene_mother", scene_number=n, scene_id=report.get("scene"),
                     source_run_id=run_id, qa_status=("rejected_visual" if n in (2,3)
                     else "pending_human_visual_review"))
        entries.append(entry)
        save_meta(report_file, ASSETS / "proveniencia" / f"cena-{n:02d}.production.json")

    # A camada conjunta foi tecnicamente RGBA, mas visualmente REPROVADA.
    layer_folder = inp / "layers"
    manifest = jsonfile(layer_folder / "manifest.json")
    recovery = jsonfile(layer_folder / "recovery.qa.json")
    if (manifest.get("channel"),manifest.get("video_id")) != (CHANNEL, VIDEO):
        raise ArchiveError("LAYER_ORIGIN_MISMATCH")
    mother_sha = next(e["sha256"] for e in entries if e.get("scene_number") == 1)
    if manifest.get("source",{}).get("sha256") != mother_sha:
        raise ArchiveError("LAYER_MOTHER_SHA_MISMATCH")
    if recovery.get("source_sha256") != mother_sha:
        raise ArchiveError("RECOVERY_MOTHER_SHA_MISMATCH")
    for layer, status, kind in [
        ("background","pending_roundtrip_alignment","reconstructed_background"),
        ("character-main","rejected_visual_trono_duplicado","group_candidate_rejected"),
    ]:
        meta = manifest.get("layers",{}).get(layer)
        if not isinstance(meta,dict):
            raise ArchiveError(f"LAYER_META_MISSING: {layer}")
        dest_name = ("background-reconstructed.png" if layer=="background"
                     else "character-group-REJECTED.png")
        entry = save_existing(layer_folder / f"{layer}.png",
                              ASSETS/"cena-01"/"candidatos"/dest_name,
                              {"sha256":meta.get("sha256")})
        entry.update(kind=kind, source_run_id=43592098806, qa_status=status)
        entries.append(entry)
    save_meta(layer_folder/"manifest.json",ASSETS/"proveniencia"/"cena-01-layer.manifest.json")
    save_meta(layer_folder/"recovery.qa.json",ASSETS/"proveniencia"/"cena-01-recovery.qa.json")

    kael_folder = inp / "kael"
    qa = jsonfile(kael_folder / "kael.qa.json")
    if (qa.get("channel"),qa.get("video_id"),qa.get("part_id")) != (CHANNEL,VIDEO,"kael"):
        raise ArchiveError("KAEL_ORIGIN_MISMATCH")
    if qa.get("scene_mother_sha256") != mother_sha:
        raise ArchiveError("KAEL_MOTHER_SHA_MISMATCH")
    entry = save_existing(kael_folder / "kael.png",
                          ASSETS/"cena-01"/"candidatos"/"kael-rgba-candidate.png",
                          {"sha256":qa.get("output_sha256")})
    entry.update(kind="independent_character_candidate",source_run_id=43592844393,
                 qa_status="pending_halo_and_rig_roundtrip_correction")
    entries.append(entry)
    save_meta(kael_folder/"kael.qa.json",ASSETS/"proveniencia"/"cena-01-kael.qa.json")

    report = {"schema":"videoforge/archived-existing-assets/v1",
              "channel":CHANNEL,"video_id":VIDEO,
              "source":"PREEXISTING GitHub Actions artifacts (NO image generation)",
              "archived_png_count":len(entries), "source_reference_run":43590930215,
              "scene_mother_count":14,"visual_qa_approved":False,
              "rig_applied":False,"mp4_official":False,"youtube_uploaded":False,
              "notes":[
                "14 imagens-mãe são tecnicamente PNGs, NÃO 14 cenas visualmente aprovadas",
                "Cenas 02 e 03 reprovadas por revelar Elara antecipadamente",
                "character-group contém trono e está reprovado",
                "Kael RGBA mantém halo/contaminação e não é rig aprovado",
                "O modelo de imagens NÃO foi chamado neste arquivamento",
                "Assets externos produzidos fora do Actions devem ser importados por pacote separado",
              ],
              "entries":entries}
    path = ASSETS / "manifesto-arquivo.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n",encoding="utf8")
    print("ARCHIVE_OK",len(entries),"PNGs",sum(e["bytes"] for e in entries),"bytes")
    return report

if __name__ == "__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Uso: python -m videoforge.archive_existing_episode ./_inputs/")
    try:
        archive(Path(sys.argv[1]))
    except (ArchiveError, ValueError, OSError) as err:
        print("ARCHIVE_BLOCKED",str(err),file=sys.stderr)
        raise SystemExit(2)
