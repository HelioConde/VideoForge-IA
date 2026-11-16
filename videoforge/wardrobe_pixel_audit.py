"""Offline color statistics for isolated V1 layers; NO wardrobe approval.

RGB scenes are intentionally unmeasured: pixels cannot be assigned to a
character's beard or garment without a trusted semantic mask. Measured
transparent layers are still V1 candidates, not validated canonical outfits.
"""
from __future__ import annotations
import argparse
import colorsys
import hashlib
import json
from collections import Counter
from io import BytesIO
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE
from .wardrobe_inventory import inventory
from .wardrobe_review import owner_review, source_readiness

REPORT = "QA-CORES-PIXELS-FIGURINO-V2.json"
DOC = "REVISAR-CORES-MEDIDAS-FIGURINO-V2.md"
SOURCES = (
    ("aldric", "roupa_mista",
     "assets/cena-01/rig-drafts/aldric-partes/corpo-vestimenta-restante.png"),
    ("aldric", "cabeca_coroa_cabelo_mistos",
     "assets/cena-01/rig-drafts/aldric-partes/coroa-cabelo-rosto.png"),
    ("aldric", "manto_esquerdo",
     "assets/cena-01/rig-drafts/aldric-partes/manto-esquerdo.png"),
    ("aldric", "manto_direito",
     "assets/cena-01/rig-drafts/aldric-partes/manto-direito.png"),
    ("elara", "close_rgb_sem_mascara",
     "assets/referencias/chat-aprovadas/elara-close-trono.png"),
    ("elara", "c12_rgb_multiplos_personagens",
     "assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png"),
)

def group_color(red, green, blue):
    hue, sat, val = colorsys.rgb_to_hsv(red/255, green/255, blue/255)
    h = hue * 360
    if val < .255:
        return "very_dark"
    if sat >= .35 and val >= .18 and (h < 20 or h >= 345):
        return "red"
    if sat >= .28 and val >= .16 and 255 <= h < 325:
        return "purple_or_magenta"
    return "other"

def measure(path: Path, expected_sha: str):
    if (path.is_symlink() or not path.is_file()
            or not 50 <= path.stat().st_size <= 15_000_000):
        raise VideoForgeError("PIXEL_QA_UNSAFE_SOURCE")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise VideoForgeError("PIXEL_QA_SHA_MISMATCH")
    try:
        from PIL import Image
    except ImportError as exc:
        raise VideoForgeError("PIXEL_QA_PILLOW_REQUIRED") from exc
    with Image.open(BytesIO(raw)) as source:
        source.load()
        if source.format != "PNG":
            raise VideoForgeError("PIXEL_QA_NOT_PNG")
        original_mode = source.mode
        dimensions = list(source.size)
        if original_mode != "RGBA":
            return dict(status="no_trusted_subject_mask", mode=original_mode,
                        dimensions=dimensions, percent=None, sampled_visible_pixels=0)
        img = source.copy()
    img.thumbnail((480, 720), resample=Image.Resampling.NEAREST)
    counts = Counter()
    visible = 0
    for r,g,b,a in img.getdata():
        if a < 224:
            continue
        visible += 1
        counts[group_color(r,g,b)] += 1
    coverage = visible / (img.width * img.height)
    if visible < 128 or coverage >= .94:
        return dict(status="alpha_mask_unusable", mode=original_mode,
                    dimensions=dimensions, percent=None,
                    sampled_visible_pixels=visible)
    ratios = {name: round(counts[name] * 100 / visible, 2)
              for name in ("red","very_dark","purple_or_magenta","other")}
    return dict(status="unlabeled_rgba_layer_measured", mode=original_mode,
                dimensions=dimensions, percent=ratios,
                sampled_visible_pixels=visible,
                alpha_coverage_percent=round(coverage*100, 2))

def audit(root: Path = ROOT, sync=False):
    root = Path(root)
    episode = root / EPISODE
    owner, _ = owner_review(root)
    approved = source_readiness(root)
    old = inventory(root)
    indexed = {x["path"]: x["sha256"] for x in old["candidates"]}
    rows = []
    for actor, region, relative in SOURCES:
        image = episode / relative
        if image.is_symlink() or not image.is_file():
            raise VideoForgeError("PIXEL_QA_SOURCE_NOT_FOUND")
        sha = indexed.get(relative, hashlib.sha256(image.read_bytes()).hexdigest())
        result = measure(image, sha)
        rows.append(dict(actor=actor, region=region, path=relative,
                         sha256=sha, **result,
                         validated_beard_roi=False, validated_bodice_roi=False,
                         validated_outer_and_center_roi=False,
                         outfit_canonical=False, source_pixels_unchanged=True))
    report = {
        "schema": "videoforge/wardrobe-pixel-audit/v1",
        "owner_rejection_sha256": owner["sha256"],
        "status": "partial_rgba_color_measurement_no_semantic_mask",
        "rows": rows,
        "measured_rgba_sources": sum(x["status"] == "unlabeled_rgba_layer_measured"
                                      for x in rows),
        "beard_color_exactly_measured": False,
        "purple_bodice_exactly_measured": False,
        "red_outer_vs_black_center_measured": False,
        "reason_for_abstention": "No trustworthy isolated beard, outer garment, garment center and purple bodice ROIs across both poses",
        "red_rule": "HSV saturation >= .35, value >= .18, hue <20 or >=345",
        "dark_rule": "HSV value < .255",
        "purple_rule": "HSV saturation >= .28, value >= .16, hue in [255,325)",
        "approved_full_outfits": approved["verified"],
        "required_full_outfits": approved["required"],
        "canonical_identity_approved": False,
        "provider_calls": 0,
        "new_character_art": False,
        "official_mp4": False, "youtube_uploaded": False,
    }
    if sync:
        p = episode / REPORT
        doc = episode / DOC
        if p.is_symlink() or doc.is_symlink():
            raise VideoForgeError("PIXEL_QA_OUTPUT_SYMLINK")
        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if not p.exists() or p.read_text(encoding="utf-8") != payload:
            p.write_text(payload, encoding="utf-8")
        lines = [
            "# EP01 V2 — cores medidas em pixels RGBA (QA offline)", "",
            "Aldric continua REPROVADO por inversão de cores e barba; Elara real continua REPROVADA pelo painel roxo, conforme relato do proprietário.", "",
            "As porcentagens abaixo medem apenas pixels **visíveis em camadas RGBA**. O algoritmo NÃO sabe quais pixels são especificamente da barba, do centro da roupa ou do corpete.", "",
            "| Personagem | Fonte | Tipo de medição | Vermelho | Muito escuro | Roxo ou magenta |",
            "|---|---|---|---:|---:|---:|",
        ]
        for x in rows:
            pct = x["percent"]
            f = (lambda name: str(pct[name]) + "%" if pct is not None else "não atribuível")
            lines.append("| "+x["actor"]+" | "+x["region"]+" | "+x["status"]+" | "+
                         f("red")+" | "+f("very_dark")+" | "+f("purple_or_magenta")+" |")
        lines += [
            "", "## O que estes valores NÃO demonstram", "",
            "- A máscara da roupa é um recorte V1 misto, não uma máscara separada de EXTERIOR versus CENTRO e nem um par sentado versus em pé.",
            "- A máscara da cabeça inclui cabelo, rosto e coroa: não oferece uma medida EXCLUSIVA da barba.",
            "- As fontes de Elara são RGB e incluem fundo/pessoas; sem máscara do corpete, contar roxo seria enganoso.",
            "- A imagem reprovada permanece reprovada, com ou sem percentuais. SHA e histogramas não são prova de fidelidade visual.", "",
            "## Para habilitar reprovação por pixels", "",
            "- [ ] Máscaras individuais de barba, roupa exterior e centro do rei em ambas as poses",
            "- [ ] Máscaras de peitoral do traje real de Elara nas duas imagens",
            "- [ ] Mesma variante, registro de cada SHA e verificação das áreas semânticas", "",
            "Fonte: [filtro e reprovações registrados](RELATORIO-APROVACAO-REPROVACAO-FIGURINO.md).",
            "Nenhuma imagem paga ou vídeo novo foi gerado nesta auditoria.", "",
        ]
        text = "\n".join(lines)
        if not doc.exists() or doc.read_text(encoding="utf-8") != text:
            doc.write_text(text, encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true")
    a = parser.parse_args()
    r = audit(sync=a.sync)
    print("PIXEL_WARDROBE_QA", json.dumps({
        "sources": len(r["rows"]),
        "rgba_measured": r["measured_rgba_sources"],
        "beard_isolated": False,
        "bodice_isolated": False,
        "provider_calls": 0
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
