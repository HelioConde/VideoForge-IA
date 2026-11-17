"""Bíblia Visual: sincroniza TODOS os PNGs de arquivo permanente por canal.

Usa apenas manifestos e PNGs reais SHA-verificados. Nunca gera imagens,
promove arte por heurísticas ou substitui versões existentes. O arquivador
chama sync ANTES do commit para que PNG e registro sejam atômicos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from .errors import VideoForgeError
from .paths import CHANNEL_IDS, IDENTIFIER
from .persist_generated_assets import _png_info
from .remake_autopilot import ROOT

INDEX_SCHEMA = "videoforge/visual-bible-index/v1"
REGISTRY_SCHEMA = "videoforge/visual-bible-generation-registry/v1"
REVIEW_SCHEMA = "videoforge/visual-bible-reviews/v1"
ITEM_SCHEMA = "videoforge/visual-bible-item/v1"
STATUS_SCHEMA = "videoforge/visual-bible-item-status/v1"
VALID_STATES = {"planejado", "gerado", "em_revisao", "aprovado", "rejeitado", "substituido"}
SHA = re.compile(r"^[a-f0-9]{64}$")
BIBLE_ID = re.compile(r"^[a-z][a-z0-9_-]*$")
SHOT = re.compile(r"(c[0-9]{2}-p[0-9]{2})", re.I)


def _read(path: Path, default=None):
    if not path.exists():
        if default is None:
            raise VideoForgeError("BIBLE_REQUIRED_FILE_MISSING")
        return default
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 5_000_000:
        raise VideoForgeError("BIBLE_UNSAFE_JSON")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError) as exc:
        raise VideoForgeError("BIBLE_JSON_INVALID") from exc


def _write(path: Path, content: str) -> bool:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise VideoForgeError("BIBLE_OUTPUT_SYMLINK")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _dump(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def _index(channel: str, bible: Path):
    default = {"schema": INDEX_SCHEMA, "channel": channel,
               "categorias": {k: [] for k in ("personagens", "cenarios", "objetos", "interacoes")}}
    data = _read(bible / "INDEX-BIBLIA.json", default=default)
    if data.get("schema") != INDEX_SCHEMA or data.get("channel") != channel:
        raise VideoForgeError("BIBLE_INDEX_WRONG_CHANNEL")
    cats = data.get("categorias")
    if not isinstance(cats, dict) or set(cats) != set(default["categorias"]):
        raise VideoForgeError("BIBLE_INDEX_CATEGORIES_INVALID")
    seen = set()
    for cat, entries in cats.items():
        if not isinstance(entries, list):
            raise VideoForgeError("BIBLE_INDEX_ITEMS_INVALID")
        for item in entries:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise VideoForgeError("BIBLE_INDEX_ITEM_INVALID")
            item_id = item["id"]
            if not BIBLE_ID.fullmatch(item_id) or (cat, item_id) in seen:
                raise VideoForgeError("BIBLE_INDEX_DUPLICATE")
            seen.add((cat, item_id))
            if item.get("status") not in VALID_STATES:
                raise VideoForgeError("BIBLE_INDEX_STATUS_INVALID")
    return data


def _review(channel: str, bible: Path):
    obj = _read(bible / "REVISOES-MANUAIS.json",
                default={"schema": REVIEW_SCHEMA, "channel": channel, "by_sha256": {}})
    if obj.get("schema") != REVIEW_SCHEMA or obj.get("channel") != channel:
        raise VideoForgeError("BIBLE_REVIEW_CHANNEL_INVALID")
    overrides = obj.get("by_sha256")
    if not isinstance(overrides, dict):
        raise VideoForgeError("BIBLE_REVIEWS_INVALID")
    for sha, row in overrides.items():
        if not SHA.fullmatch(sha) or not isinstance(row, dict) or row.get("status") not in VALID_STATES:
            raise VideoForgeError("BIBLE_REVIEW_INVALID")
        if row["status"] == "aprovado":
            if (not isinstance(row.get("revisor"), str) or not row["revisor"].strip()
                    or not isinstance(row.get("evidencia"), str) or not row["evidencia"].strip()):
                raise VideoForgeError("BIBLE_APPROVAL_REQUIRES_HUMAN_EVIDENCE")
    return overrides


def _verified_images(root: Path, channel: str):
    folder = root / "canal" / channel / "videos"
    if not folder.is_dir() or folder.is_symlink():
        return []
    images = []
    for manifest in sorted(folder.glob("*/assets/geracoes/*/*/manifesto-geracoes.json")):
        if any(x.is_symlink() for x in (manifest, *manifest.parents) if x != root):
            raise VideoForgeError("BIBLE_ARCHIVE_SYMLINK")
        video_id = manifest.parents[4].name  # .../<video>/assets/geracoes/<producer>/<run>/
        producer = manifest.parent.parent.name
        run = manifest.parent.name
        if (not IDENTIFIER.fullmatch(video_id)
                or not IDENTIFIER.fullmatch(producer)
                or not run.isdecimal()):
            raise VideoForgeError("BIBLE_ARCHIVE_SCOPE_INVALID")
        obj = _read(manifest)
        if (obj.get("schema") != "videoforge/permanent-generated-image-archive/v1"
                or obj.get("channel") != channel or obj.get("video_id") != video_id
                or obj.get("producer") != producer or obj.get("github_run_id") != int(run)
                or not isinstance(obj.get("images"), list)
                or not 1 <= len(obj["images"]) <= 64):
            raise VideoForgeError("BIBLE_ARCHIVE_MANIFEST_INVALID")
        for entry in obj["images"]:
            if not isinstance(entry, dict):
                raise VideoForgeError("BIBLE_ARCHIVE_ENTRY_INVALID")
            filename = entry.get("file")
            if not isinstance(filename, str) or not filename or "\\" in filename:
                raise VideoForgeError("BIBLE_ARCHIVE_FILENAME_INVALID")
            sub = Path(filename)
            if sub.is_absolute() or ".." in sub.parts or sub.suffix.lower() != ".png":
                raise VideoForgeError("BIBLE_ARCHIVE_FILENAME_INVALID")
            path = manifest.parent / sub
            if (path.is_symlink() or not path.is_file()
                    or path.stat().st_size > 35_000_000
                    or not path.resolve().is_relative_to(manifest.parent.resolve())):
                raise VideoForgeError("BIBLE_ARCHIVED_PNG_MISSING_OR_UNSAFE")
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            width, height = _png_info(data)
            if (not SHA.fullmatch(str(entry.get("sha256", ""))) or entry["sha256"] != digest
                    or entry.get("bytes") != len(data)
                    or entry.get("width") != width or entry.get("height") != height):
                raise VideoForgeError("BIBLE_ARCHIVED_IMAGE_SHA_OR_SIZE_MISMATCH")
            meta = path.with_suffix(".production.json")
            origin = {}
            if meta.exists():
                origin = _read(meta)
                if (origin.get("sha256") != digest or origin.get("channel") != channel
                        or origin.get("video_id") != video_id):
                    raise VideoForgeError("BIBLE_PRODUCTION_ORIGIN_MISMATCH")
            name = path.stem
            shot = origin.get("candidate_scene_shot_id") or (
                SHOT.search(name).group(1).upper() if SHOT.search(name) else None)
            biblia_item = origin.get("biblia_item_id")
            if biblia_item is not None and (
                not isinstance(biblia_item, str) or not BIBLE_ID.fullmatch(biblia_item)
            ):
                raise VideoForgeError("BIBLE_ITEM_ID_INVALID")
            images.append({
                "id": f"{video_id}:{producer}:{run}:{filename}",
                "channel": channel,
                "video_id": video_id,
                "asset": origin.get("asset_id", name),
                "shot": shot,
                "tipo": "cena" if shot else "referencia_ou_camada",
                "biblia_item_id": biblia_item,
                "producer": producer,
                "github_run_id": int(run),
                "arquivo": path.relative_to(root).as_posix(),
                "sha256": digest, "bytes": len(data),
                "width": width, "height": height,
                "referencias_usadas": [
                    {"id": s.get("id"), "sha256": s.get("sha256"), "path": s.get("path")}
                    for s in origin.get("source_originals_sha_verified", [])
                    if isinstance(s, dict)
                ],
                "status": "gerado",
                "aprovacao_automatica": False,
                "youtube_uploaded": False
            })
    ids = [r["id"] for r in images]
    if len(ids) != len(set(ids)):
        raise VideoForgeError("BIBLE_DUPLICATE_IMAGE_ID")
    return images


def build(channel: str, root: Path = ROOT):
    if channel not in CHANNEL_IDS:
        raise VideoForgeError("BIBLE_CHANNEL_INVALID")
    root = Path(root)
    bible = root / "canal" / channel / "biblia-visual"
    index = _index(channel, bible)
    reviews = _review(channel, bible)
    previous = _read(bible / "REGISTRO-GERACOES.json",
                     default={"schema": REGISTRY_SCHEMA, "channel": channel, "geracoes": []})
    if (previous.get("schema") != REGISTRY_SCHEMA
            or previous.get("channel") != channel
            or not isinstance(previous.get("geracoes"), list)):
        raise VideoForgeError("BIBLE_REGISTRY_INVALID")
    old_by_id = {}
    for row in previous["geracoes"]:
        if not isinstance(row, dict) or row.get("id") in old_by_id:
            raise VideoForgeError("BIBLE_DUPLICATE_OLD_REGISTRY_ID")
        old_by_id[row.get("id")] = row
    results = []
    for fresh in _verified_images(root, channel):
        old = old_by_id.pop(fresh["id"], None)
        if old is not None:
            for key in ("arquivo", "sha256", "bytes", "width", "height", "github_run_id"):
                if old.get(key) != fresh[key]:
                    raise VideoForgeError("BIBLE_IMMUTABLE_RECORD_TAMPERED")
            fresh["status"] = old.get("status", "gerado")
            if fresh["status"] not in VALID_STATES:
                raise VideoForgeError("BIBLE_REGISTRY_STATUS_INVALID")
        review = reviews.get(fresh["sha256"])
        if review:
            fresh["status"] = review["status"]
            fresh["motivo_revisao"] = review.get("motivo")
            fresh["escopo_permitido"] = review.get("escopo_permitido", [])
            fresh["escopo_proibido"] = review.get("escopo_proibido", [])
            fresh["evidencia"] = review.get("evidencia")
        elif fresh["status"] == "aprovado":
            raise VideoForgeError("BIBLE_APPROVAL_WITHOUT_MANUAL_REVIEW")
        results.append(fresh)
    if old_by_id:
        raise VideoForgeError("BIBLE_PREVIOUS_IMAGE_DISAPPEARED")
    results.sort(key=lambda x: (x["video_id"], x["github_run_id"], x["producer"], x["arquivo"]))
    registry = {"schema": REGISTRY_SCHEMA, "channel": channel,
                "total_arquivadas": len(results),
                "geracoes": results,
                "sem_promocao_automatica": True,
                "fonte": "PNG original + manifesto-geracoes.json + SHA256"}
    return index, registry


def _markdown(data: dict):
    lines = [f"# Registro de gerações — {data['channel']}", "",
             f"**{data['total_arquivadas']} PNGs reais arquivados e SHA-verificados.** "
             "Planejados não contam como gerados. Estado NÃO aprova arte automaticamente.", "",
             "| Imagem / tomada | Status | Canal / episódio | SHA-256 | GitHub Action |",
             "|---|---|---|---|---|"]
    for row in data["geracoes"]:
        name = Path(row["arquivo"]).name
        url = "https://github.com/HelioConde/VideoForge-IA/blob/main/" + row["arquivo"]
        action = f"https://github.com/HelioConde/VideoForge-IA/actions/runs/{row['github_run_id']}"
        lines.append(
            f"| [{name}]({url}) / {row['shot'] or 'referência'} | {row['status']} "
            f"| {row['channel']}/{row['video_id']} | \`{row['sha256'][:12]}…\` "
            f"| [#{row['github_run_id']}]({action}) |"
        )
    lines.extend(["", "## Regras de consulta", "",
                  "Arquivo original nunca é reescrito. Revisões humanas ficam em "
                  "\`REVISOES-MANUAIS.json\`; histórico é sincronizado após cada PNG. "
                  "Imagens rejeitadas permanecem acessíveis, mas não podem ser usadas "
                  "como referência canônica para o escopo rejeitado.", ""])
    return "\n".join(lines)


def sync(channel: str, root: Path = ROOT):
    root = Path(root)
    index, registry = build(channel, root)
    bible = root / "canal" / channel / "biblia-visual"
    changed = []
    for path, obj in ((bible / "INDEX-BIBLIA.json", index),
                      (bible / "REGISTRO-GERACOES.json", registry)):
        if _write(path, _dump(obj)):
            changed.append(path)
    md = bible / "REGISTRO-GERACOES.md"
    if _write(md, _markdown(registry)):
        changed.append(md)
    for category, items in index["categorias"].items():
        for item in items:
            folder = bible / category / item["id"]
            statefile = folder / "status.json"
            sheetfile = folder / "ficha.json"
            ficha = {"schema": ITEM_SCHEMA, "categoria": category,
                     "id": item["id"], "nome": item.get("nome"),
                     "descricao": item.get("descricao", ""),
                     "variantes": item.get("variantes", ["base"]),
                     "referencias_aprovadas": [],
                     "fonte": "INDEX-BIBLIA.json",
                     "aviso": "Não inventar imagem ou aprovação."}
            if not sheetfile.exists() and _write(sheetfile, _dump(ficha)):
                changed.append(sheetfile)
            status = _read(statefile,
                           default={"schema": STATUS_SCHEMA, "categoria": category,
                                    "id": item["id"], "status": item["status"],
                                    "ultima_geracao": None, "ultimo_arquivo": None,
                                    "aprovacao_mestra": False, "historico_de_versoes": []})
            if (status.get("schema") != STATUS_SCHEMA or
                    status.get("id") != item["id"] or status.get("categoria") != category or
                    status.get("status") not in VALID_STATES):
                raise VideoForgeError("BIBLE_ITEM_STATUS_INVALID")
            related = [x for x in registry["geracoes"] if x.get("biblia_item_id") == item["id"]]
            if related:
                newest = related[-1]
                status["ultima_geracao"] = newest["github_run_id"]
                status["ultimo_arquivo"] = newest["arquivo"]
                status["historico_de_versoes"] = [x["id"] for x in related]
                if status["status"] == "planejado":
                    status["status"] = "gerado"
                # Never change to aprovado from an image archive.
            if _write(statefile, _dump(status)):
                changed.append(statefile)
    return {"channel": channel, "items": sum(map(len, index["categorias"].values())),
            "images": registry["total_arquivadas"], "changed_files": len(changed)}


def main():
    p = argparse.ArgumentParser(description="Atualizar registro da Bíblia Visual sem chamadas de IA")
    choice = p.add_mutually_exclusive_group(required=True)
    choice.add_argument("--channel", choices=sorted(CHANNEL_IDS))
    choice.add_argument("--all-channels", action="store_true")
    args = p.parse_args()
    channels = sorted(CHANNEL_IDS) if args.all_channels else [args.channel]
    for channel in channels:
        print("VISUAL_BIBLE_SYNC", json.dumps(sync(channel), ensure_ascii=False))


if __name__ == "__main__":
    main()
