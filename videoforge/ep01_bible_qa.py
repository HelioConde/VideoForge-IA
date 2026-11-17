"""Laudo técnico determinístico da Bíblia Visual do EP01.

Leituras locais apenas; sem chamadas de IA, promoção de arte ou upload.
Diferencia geração real (SHA) de aprovação visual humana.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT
from .visual_bible import build

CHANNEL = "alchemy-lab"
EPISODE = "mmorpg-conquiste-a-princesa-ep01"
BIBLE = Path("canal") / CHANNEL / "biblia-visual"

# O valor 'approved-visual-reference' só é permitido para ESTILO da lança V2:
# a pegada das lanças na cena antiga continua rejeitada, não é fonte de rig.
SOURCE_IDS = {
    "biblia-kael-casual-antes-v2": ["ref-kael-close-c12"],
    "biblia-lanca-guarda-completa-v2": ["approved-visual-reference"],
    "biblia-lanca-guarda-base-v2": ["biblia-lanca-guarda-completa-v2"],
    "biblia-lanca-guarda-empunhadura-v2": ["biblia-lanca-guarda-completa-v2"],
    "biblia-carrasco-base-v2": ["biblia-sala-do-trono-vazio-v1"],
    "biblia-figurantes-base-v2": ["biblia-sala-do-trono-vazio-v1"],
    "biblia-mascarado-1-base-v2": ["biblia-sala-do-trono-vazio-v1"],
    "biblia-mascarado-2-base-v2": ["biblia-sala-do-trono-vazio-v1"],
    "biblia-mascarados-base-v2": [
        "biblia-mascarado-1-base-v2", "biblia-mascarado-2-base-v2"],
}
EXPECTED_ORIGINAL_SHAS = {
    "ref-kael-close-c12": "edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f",
    "approved-visual-reference": "605ccd361ad9a867eb8b92948010fdbb7d87a031d8b3601c663d815917b1b6cc",
}


def generate(root: Path = ROOT) -> dict:
    root = Path(root)
    bible = root / BIBLE
    queue = json.loads((bible / "FILA-GERACAO-MESTRES.json").read_text(encoding="utf-8"))
    corrections = json.loads((bible / "FILA-REPAROS-EP01.json").read_text(encoding="utf-8"))
    index, registry = build(CHANNEL, root)  # SHA + manifesto + PNG original reais
    if queue.get("schema") != "videoforge/bible-master-queue/v1":
        raise VideoForgeError("BIBLE_QA_QUEUE_SCHEMA_INVALID")
    if corrections.get("schema") != "videoforge/bible-correction-queue/v1":
        raise VideoForgeError("BIBLE_QA_REPAIR_SCHEMA_INVALID")
    masters = [x["asset_id"] for x in queue["items"] if x.get("phase") == "independent_master"]
    repairs = [x["asset_id"] for x in corrections["items"]]
    if (len(masters) != 42 or len(set(masters)) != 42 or
            len(repairs) != 9 or set(repairs) != set(SOURCE_IDS)):
        raise VideoForgeError("BIBLE_QA_ASSET_SET_MISMATCH")
    by_asset = {}
    for entry in registry["geracoes"]:
        asset = entry.get("asset")
        if not isinstance(asset, str):
            raise VideoForgeError("BIBLE_QA_INVALID_REGISTRY_ASSET")
        if asset in masters or asset in repairs:
            if asset in by_asset:
                raise VideoForgeError("BIBLE_QA_DUPLICATE_CANDIDATE")
            by_asset[asset] = entry
    master_count = sum(name in by_asset for name in masters)
    checks = []
    for asset in repairs:
        row = by_asset.get(asset)
        if row is None:
            checks.append({"asset": asset, "state": "aguardando_geracao", "sources": [], "row": None})
            continue
        if row.get("aprovacao_automatica") is not False or row.get("youtube_uploaded") is not False:
            raise VideoForgeError("BIBLE_QA_AUTOMATIC_PUBLICATION_FLAG_INVALID")
        refs = row.get("referencias_usadas")
        if not isinstance(refs, list):
            raise VideoForgeError("BIBLE_QA_PROVENANCE_REQUIRED")
        received = [r.get("id") if isinstance(r, dict) else None for r in refs]
        expected = SOURCE_IDS[asset]
        if received != expected:
            raise VideoForgeError("BIBLE_QA_UNEXPECTED_SOURCES " + asset)
        for ref in refs:
            key = ref["id"]
            expected_sha = EXPECTED_ORIGINAL_SHAS.get(key)
            if expected_sha is None:
                source = by_asset.get(key)
                if source is None and key == "biblia-sala-do-trono-vazio-v1":
                    source = next((x for x in registry["geracoes"] if x.get("asset") == key), None)
                if source is None:
                    raise VideoForgeError("BIBLE_QA_REFERENCE_NOT_ARCHIVED " + key)
                expected_sha = source["sha256"]
            if ref.get("sha256") != expected_sha:
                raise VideoForgeError("BIBLE_QA_SOURCE_SHA_CHANGED " + asset)
        state = "revisao_humana" if row.get("status") != "aprovado" else "aprovacao_registrada"
        checks.append({"asset": asset, "state": state,
                       "sources": received, "row": row})

    lines = [
        "# Laudo técnico da Bíblia Visual — EP01", "",
        "> Gerado pelo GitHub exclusivamente de PNGs originais e manifestos SHA-verificados. "
        "**Não avalia beleza, identidade facial, anatomia das mãos, pose nem consistência artística.** "
        "Não substitui a aprovação humana.", "",
        f"**Mestres arquivados:** {master_count}/{len(masters)}. "
        f"**Reparos V2 arquivados:** {sum(c['row'] is not None for c in checks)}/{len(checks)}. "
        f"**Histórico original:** {registry['total_arquivadas']} PNGs reais.", "",
        "| Reparação | Registro real | Proveniência / referência de entrada | Revisão |",
        "|---|---|---|---|",
    ]
    for check in checks:
        row = check["row"]
        if row is None:
            file_link = "Pendente de geração"
            review = "Não gerado"
        else:
            url = ("https://github.com/HelioConde/VideoForge-IA/blob/main/"
                   + row["arquivo"])
            file_link = f"[PNG #{row['github_run_id']}]({url}) / `{row['sha256'][:16]}…`"
            review = ("Aprovação humana registrada, conferir escopo"
                      if check["state"] == "aprovacao_registrada"
                      else "SHA válido; aprovação visual pendente")
        inputs = ", ".join("`" + x + "`" for x in check["sources"]) or "Aguardando fontes"
        lines.append(f"| `{check['asset']}` | {file_link} | {inputs} | {review} |")
    lines.extend(["", "## Bloqueios em vigor", "",
                  "- O quadro C01-P04 V3 é referência **somente de estilo** para a lança completa V2; a pose de mãos da cena antiga está rejeitada.",
                  "- Guardas devem segurar suas próprias lanças no **terço inferior/base**, com punho, dedos e antebraço fisicamente conectados.",
                  "- As **12 poses/interações físicas** continuam aguardando fontes mestras aprovadas por humano com evidência em REVISOES-MANUAIS.json.",
                  "- As **40 tomadas do EP01**, animação final e publicação YouTube permanecem suspensas. Nem a presença de 51 PNGs nem este relatório libera uma cena.",
                  "- Para comparação estética consultar [GALERIA-EP01.md](GALERIA-EP01.md) e [QA-VISUAL-CANDIDATOS.md](QA-VISUAL-CANDIDATOS.md).", ""])
    target = bible / "LAUDO-TECNICO-EP01.md"
    body = "\n".join(lines)
    if not target.is_file() or target.read_text(encoding="utf-8") != body:
        target.write_text(body, encoding="utf-8")
    return {"master_count": master_count, "master_total": len(masters),
            "repair_count": sum(c["row"] is not None for c in checks),
            "repair_total": len(checks), "verified_total": registry["total_arquivadas"],
            "scene_hold": True, "youtube_upload": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print("EP01_BIBLE_TECH_QA", json.dumps(generate(args.root), ensure_ascii=False))


if __name__ == "__main__":
    main()
