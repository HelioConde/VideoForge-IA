#!/usr/bin/env python3
"""Monta galerias JPG de consulta a partir de PNGs reais da Bíblia Visual.

Não gera arte nova, não altera PNG de origem e nunca concede aprovação.
As imagens só entram na galeria após verificar SHA256/bytes/dimensões.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANNEL = "alchemy-lab"
EPISODE = "mmorpg-conquiste-a-princesa-ep01"
BIBLE = Path("canal") / CHANNEL / "biblia-visual"
SCHEMA = "videoforge/bible-master-queue/v1"


def assemble(root: Path = ROOT):
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    root = Path(root)
    bible = root / BIBLE
    registry = json.loads((bible / "REGISTRO-GERACOES.json").read_text(encoding="utf-8"))
    queue = json.loads((bible / "FILA-GERACAO-MESTRES.json").read_text(encoding="utf-8"))
    if registry.get("channel") != CHANNEL or queue.get("schema") != SCHEMA:
        raise ValueError("BIBLE_GALLERY_SCOPE_MISMATCH")
    if queue.get("channel") != CHANNEL or queue.get("video_id") != EPISODE:
        raise ValueError("BIBLE_GALLERY_EPISODE_INVALID")

    archived = {}
    for row in registry.get("geracoes", []):
        if row.get("video_id") != EPISODE or row.get("channel") != CHANNEL:
            continue
        if row.get("biblia_item_id") is None:
            continue
        asset_id = row["asset"]
        if asset_id in archived:
            raise ValueError("BIBLE_GALLERY_AMBIGUOUS_ASSET " + asset_id)
        archived[asset_id] = row

    independent = [x for x in queue["items"] if x["phase"] == "independent_master"]
    # Os reparos V2 ficam lado a lado com o arquivo original para QA.
    # Não confundir correções com a quantidade das 42 referências independentes.
    repair_file = bible / "FILA-REPAROS-EP01.json"
    repairs = []
    if repair_file.is_file():
        repair_queue = json.loads(repair_file.read_text(encoding="utf-8"))
        if (repair_queue.get("schema") != "videoforge/bible-correction-queue/v1"
                or repair_queue.get("channel") != CHANNEL
                or repair_queue.get("video_id") != EPISODE):
            raise ValueError("BIBLE_GALLERY_REPAIR_QUEUE_INVALID")
        repairs = repair_queue.get("items", [])
        if not isinstance(repairs, list):
            raise ValueError("BIBLE_GALLERY_REPAIR_ITEMS_INVALID")
    candidates = independent + repairs
    entries = []
    for entry in candidates:
        row = archived.get(entry["asset_id"])
        if not row:
            continue
        relative = Path(row["arquivo"])
        expected = Path("canal") / CHANNEL / "videos" / EPISODE / "assets" / "geracoes"
        if relative.is_absolute() or ".." in relative.parts or not relative.is_relative_to(expected):
            raise ValueError("BIBLE_GALLERY_UNSAFE_PNG_PATH")
        original = root / relative
        if original.is_symlink() or not original.is_file() or original.stat().st_size > 35_000_000:
            raise ValueError("BIBLE_GALLERY_MISSING_OR_LARGE_PNG")
        raw = original.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row["sha256"] or len(raw) != row["bytes"]:
            raise ValueError("BIBLE_GALLERY_SOURCE_SHA_MISMATCH")
        with Image.open(io.BytesIO(raw)) as img:
            if img.format != "PNG" or img.width != row["width"] or img.height != row["height"]:
                raise ValueError("BIBLE_GALLERY_IMAGE_METADATA_MISMATCH")
            thumb = ImageOps.contain(img.convert("RGB"), (296, 344), Image.Resampling.LANCZOS)
        entries.append((entry, row, thumb))

    out_dir = bible / "galeria"
    out_dir.mkdir(exist_ok=True)
    width, tile_w, tile_h, cols, rows_per_page = 1010, 318, 408, 3, 4
    per_page = cols * rows_per_page
    pages = []
    for start in range(0, len(entries), per_page):
        section = entries[start:start + per_page]
        sheet = Image.new("RGB", (width, 85 + tile_h * rows_per_page), "#f6f6f6")
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default()
        page = (start // per_page) + 1
        draw.text((20, 15), "BIBLIA VISUAL / EP01 / PREVIA PARA QA", font=font, fill="#222222")
        master_count = sum(1 for item in independent if item["asset_id"] in archived)
        repair_count = sum(1 for item in repairs if item["asset_id"] in archived)
        draw.text((20, 37), f"Pagina {page} - {master_count}/{len(independent)} mestres + {repair_count}/{len(repairs)} reparos - NAO APROVADOS AUTOMATICAMENTE",
                  font=font, fill="#555555")
        for offset, (item, row, thumb) in enumerate(section):
            col, line = offset % cols, offset // cols
            left, top = 20 + col * (tile_w + 11), 76 + line * tile_h
            draw.rectangle((left, top, left + tile_w - 8, top + tile_h - 9), fill="#ffffff", outline="#c4c4c4")
            x = left + (tile_w - 8 - thumb.width) // 2
            sheet.paste(thumb, (x, top + 7))
            label = item["asset_id"].removeprefix("biblia-")
            draw.text((left + 8, top + 357), label[:42], font=font, fill="#202020")
            draw.text((left + 8, top + 373), f"{row['status']} / run {row['github_run_id']}", font=font, fill="#575757")
        image_name = f"PREVIA-{page:02d}.jpg"
        target = out_dir / image_name
        buf = io.BytesIO()
        sheet.save(buf, "JPEG", quality=83, optimize=True, subsampling=1)
        jpeg = buf.getvalue()
        if not target.is_file() or target.read_bytes() != jpeg:
            target.write_bytes(jpeg)
        pages.append(image_name)

    # Nunca apagar o histórico das artes originais; JPGs só são miniaturas derivadas.
    lines = [
        "# Galeria visual de revisão — EP01", "",
        f"**{master_count} de {len(independent)} referências-mestre** arquivadas e verificadas por SHA256.",
        f"**{repair_count} de {len(repairs)} reparos V2** gerados; são candidatos separados e não substituem os PNGs V1.",
        "**Nenhuma miniatura substitui o original. Gerado não significa aprovado.**",
        "Esta galeria é atualizada pelo GitHub Actions após cada lote, sem nova geração de IA.", "",
    ]
    for image_name in pages:
        lines.extend([f"![Prancha de revisão {image_name}](galeria/{image_name})", ""])
    lines.extend(["## Arquivos originais e proveniência", "",
                  "| Referência | Estado visual | SHA-256 | Workflow |",
                  "|---|---|---|---|"])
    for item, row, _ in entries:
        png_relative = Path(row["arquivo"]).relative_to(Path("canal") / CHANNEL)
        relative_link = "../" + png_relative.as_posix()
        lines.append(
            f"| [{item['asset_id']}]({relative_link}) | {row['status']} (não aprovado automaticamente) "
            f"| " + chr(96) + row["sha256"][:16] + "…" + chr(96) +
            f" | [#{row['github_run_id']}](https://github.com/HelioConde/VideoForge-IA/actions/runs/{row['github_run_id']}) |"
        )
    missing = [item["asset_id"] for item in independent if item["asset_id"] not in archived]
    lines.extend(["", "## Pendentes de geração", ""])
    if missing:
        lines.extend(["- " + ident for ident in missing])
    else:
        lines.append("As 42 referências individuais possuem arquivos no registro.")
    repair_missing = [item["asset_id"] for item in repairs if item["asset_id"] not in archived]
    lines.extend(["", "## Correções V2 (sem promoção automática)", ""])
    if repair_missing:
        lines.extend(["- Pendente: " + ident for ident in repair_missing])
    else:
        lines.append("Todos os reparos V2 estão arquivados; ainda requerem revisão visual humana.")
    lines.extend(["", "## Travamentos preservados", "",
                  "- As 12 poses/interações dependem de referências aprovadas por humano; a pose V3/V4 de lança está rejeitada.",
                  "- As tomadas do EP01 e a publicação no YouTube permanecem bloqueadas.",
                  "- Aprovação visual exige decisão humana registrada em REVISOES-MANUAIS.json.", ""])
    md = "\n".join(lines)
    md_path = bible / "GALERIA-EP01.md"
    if not md_path.exists() or md_path.read_text(encoding="utf-8") != md:
        md_path.write_text(md, encoding="utf-8")
    return {"review_sheets": len(pages), "archived_individual_masters": master_count,
            "planned_individual_masters": len(independent), "missing_masters": len(missing),
            "archived_repairs": repair_count, "planned_repairs": len(repairs)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = assemble(args.root)
    print("BIBLE_GALLERY_REAL_SHA_VERIFIED", json.dumps(result))


if __name__ == "__main__":
    main()
