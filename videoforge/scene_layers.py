"""Separacao GENERATIVA de uma cena existente via Codex Proxy.

Edicoes de imagem nao sao segmentacao perfeita. QA tecnico verifica PNG,
dimensoes, integridade e transparencia, mas nao garante alinhamento visual.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import zlib

from . import proxy_images as proxy
from .paths import _check_symlinks

SCHEMA = "videoforge/scene-layers/v1"
MAX_PNG = 32 * 1024 * 1024
MAX_PIXELS = 4_000_000

# z-index sugerido; a montagem final ainda nao foi implementada.
COMPONENTS = {
    "background": (0, False, "Retire completamente o aventureiro. Reconstrua naturalmente cenario oculto atras dele, telhados e paisagem. Preserve cidade, castelo, ceu, perspectiva, iluminacao e enquadramento. O resultado deve ser somente um background preenchido, sem personagem."),
    "character-main": (20, True, "Isole somente o aventureiro, na exata mesma pose, escala e posicao da imagem. Preserve rosto, cabelo castanho, capa vermelha, vestuario e espada. Remova tudo ao redor, deixando alfa transparente de verdade, nao quadriculado nem branco."),
    "foreground-roof": (50, True, "Isole apenas os elementos de telhado/borda que estao NA FRENTE do aventureiro, mantendo coordenadas e perspectiva. Remova personagem, ceu e castelo. Fora do objeto, alfa inteiramente transparente."),
    "cape": (28, True, "Isole somente a capa vermelha do personagem, mesma silhueta, tecido, dobras e posicao. Nao desenhe corpo nem fundo. Fundo totalmente transparente."),
    "hair": (31, True, "Isole somente cabelo/franja do aventureiro, mesmas proporcoes, cor e posicao; nao desenhe rosto ou fundo. Restante transparente."),
    "sword": (32, True, "Isole a espada e bainha visiveis, mantendo escala, detalhes e coordenadas; nao desenhe corpo ou cenario. Fundo transparente."),
    "flag": (10, True, "Isole apenas o estandarte vermelho da torre, no local exato da referencia. Nao invente bandeiras. Fora do objeto, transparencia real."),
    "waterfall": (9, True, "Isole apenas a cachoeira visivel proxima ao castelo, nas mesmas proporcoes e posicao. Nao invente outra. Fora do objeto, alfa transparente."),
}
BASIC = ("background", "character-main")
ADVANCED = ("foreground-roof", "cape", "hair", "sword", "flag", "waterfall")


class LayerError(ValueError):
    pass


def output_dir(channel: str, video_id: str, scene: str) -> Path:
    proxy.destination(channel, video_id, scene)
    folder = proxy.ROOT / "output" / channel / "videos" / video_id / "assets" / scene
    _check_symlinks(folder, stop_at=proxy.ROOT)
    return folder


def _read_png(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or not 50 <= path.stat().st_size <= MAX_PNG:
        raise LayerError("PNG de origem ausente, inseguro ou grande demais")
    return path.read_bytes()


def png_info(data: bytes, *, require_alpha: bool | None = None,
             min_visible_fraction: float = .005) -> dict:
    """PNG RGB8/RGBA8, nao interlacado, com CRC e alfa realmente decodificado."""
    if len(data) > MAX_PNG or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise LayerError("Arquivo PNG invalido ou grande demais")
    pos, idat, ihdr, finished = 8, [], None, False
    while pos + 12 <= len(data):
        length = int.from_bytes(data[pos:pos + 4], "big")
        tag = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data) or length > MAX_PNG:
            raise LayerError("PNG truncado ou chunk invalido")
        payload = data[pos + 8:pos + 8 + length]
        crc = int.from_bytes(data[pos + 8 + length:end], "big")
        if zlib.crc32(tag + payload) & 0xffffffff != crc:
            raise LayerError("CRC PNG nao confere")
        if pos == 8 and tag != b"IHDR":
            raise LayerError("PNG sem IHDR inicial")
        if tag == b"IHDR":
            if ihdr is not None or length != 13:
                raise LayerError("IHDR invalido")
            ihdr = struct.unpack(">IIBBBBB", payload)
        elif tag == b"IDAT":
            idat.append(payload)
        elif tag == b"IEND":
            if length or end != len(data):
                raise LayerError("IEND PNG incorreto")
            finished = True
            break
        pos = end
    if not (finished and ihdr and idat):
        raise LayerError("PNG incompleto")
    width, height, depth, kind, comp, flt, inter = ihdr
    if width * height > MAX_PIXELS or not (0 < width <= 4096 and 0 < height <= 4096):
        raise LayerError("Imagem excede limite de resolucao")
    if (depth, kind, comp, flt, inter) not in ((8, 2, 0, 0, 0), (8, 6, 0, 0, 0)):
        raise LayerError("PNG requer RGB8/RGBA8 nao interlacado")
    info = {"width": width, "height": height, "color_type": kind, "has_alpha": kind == 6}
    if require_alpha is None:
        return info
    if not (0 < min_visible_fraction < 1):
        raise LayerError("Fracao minima de alfa invalida")
    if require_alpha and kind != 6:
        raise LayerError("Camada precisa ser PNG RGBA8 com canal alfa real")
    if kind == 2:
        zero = 0
        visible = width * height
    else:
        channels, n = 4, width * 4
        expected = (n + 1) * height
        dec = zlib.decompressobj()
        rows = dec.decompress(b"".join(idat), expected + 1)
        if len(rows) != expected or not dec.eof or dec.unconsumed_tail:
            raise LayerError("Dados RGBA invalidos ou excessivos")
        prev = bytearray(n)
        zero = visible = 0
        p = 0
        for _ in range(height):
            filt = rows[p]
            p += 1
            row = bytearray(rows[p:p + n])
            p += n
            if filt > 4:
                raise LayerError("Filtro PNG invalido")
            for i in range(n):
                left = row[i - channels] if i >= channels else 0
                above = prev[i]
                corner = prev[i - channels] if i >= channels else 0
                if filt == 1:
                    predict = left
                elif filt == 2:
                    predict = above
                elif filt == 3:
                    predict = (left + above) // 2
                elif filt == 4:
                    v = left + above - corner
                    a, b, c = abs(v - left), abs(v - above), abs(v - corner)
                    predict = left if a <= b and a <= c else above if b <= c else corner
                else:
                    predict = 0
                row[i] = (row[i] + predict) & 255
            alpha = row[3::4]
            zero += alpha.count(0)
            visible += sum(a > 0 for a in alpha)
            prev = row
    count = width * height
    info["alpha_zero_fraction"] = round(zero / count, 4)
    info["alpha_visible_fraction"] = round(visible / count, 4)
    if require_alpha is True and (zero / count < .01 or visible / count < min_visible_fraction):
        raise LayerError("PNG sem transparencia real ou objeto visivel")
    if require_alpha is False and visible / count < .99:
        raise LayerError("Background nao preenche o quadro")
    return info


def _read_manifest(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 120_000:
        raise LayerError("Manifesto ausente ou inseguro")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError) as exc:
        raise LayerError("Manifesto nao e JSON valido") from exc
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
        raise LayerError("Schema de manifesto incorreto")
    return obj


def _write_manifest(folder: Path, data: dict) -> None:
    tmp = folder / ".manifest.tmp"
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(folder / "manifest.json")


def initialize(channel: str, video_id: str, scene: str, source: Path) -> Path:
    folder = output_dir(channel, video_id, scene)
    if folder.exists():
        raise LayerError("Destino ja existe; nao sobrescrever")
    blob = _read_png(source)
    info = png_info(blob)
    folder.mkdir(parents=True)
    (folder / "cena-base.png").write_bytes(blob)
    _write_manifest(folder, {
        "schema": SCHEMA, "channel": channel, "video_id": video_id, "scene": scene,
        "source": {"file": "cena-base.png", "sha256": hashlib.sha256(blob).hexdigest(), **info},
        "layers": {}, "human_visual_approval": False,
        "pixel_alignment_verified": False, "animation_implemented": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    return folder


def resume(channel: str, video_id: str, scene: str, incoming: Path) -> Path:
    folder = output_dir(channel, video_id, scene)
    if folder.exists():
        raise LayerError("Destino ja existe; nao sobrescrever")
    manifest = _read_manifest(incoming / "manifest.json")
    if (manifest.get("channel"), manifest.get("video_id"), manifest.get("scene")) != (channel, video_id, scene):
        raise LayerError("Artifact de outro canal/video/cena")
    layers = manifest.get("layers")
    if not isinstance(layers, dict) or set(layers) - set(COMPONENTS):
        raise LayerError("Manifesto com camadas invalidas")
    for name in ("background", "character-main"):
        if layers.get(name, {}).get("technical_status") != "verified":
            raise LayerError("Camadas basicas nao verificadas")
    files = {"cena-base.png": manifest.get("source", {}).get("sha256")}
    for name, item in layers.items():
        if not isinstance(item, dict) or item.get("file") != name + ".png":
            raise LayerError("Dados de componente invalidos")
        files[item["file"]] = item.get("sha256")
    for name, checksum in files.items():
        if hashlib.sha256(_read_png(incoming / name)).hexdigest() != checksum:
            raise LayerError("Hash de artifact alterado")
    source = _read_png(incoming / "cena-base.png")
    if (png_info(source)["width"], png_info(source)["height"]) != (
        manifest["source"]["width"], manifest["source"]["height"]
    ):
        raise LayerError("Resolucao de origem alterada")
    folder.mkdir(parents=True)
    for name in files:
        shutil.copyfile(incoming / name, folder / name)
    shutil.copyfile(incoming / "manifest.json", folder / "manifest.json")
    return folder


def generate_layer(folder: Path, name: str, url: str, key: str, model: str) -> Path:
    if name not in COMPONENTS or model not in proxy.IMAGE_MODELS:
        raise LayerError("Modelo ou componente invalido")
    manifest = _read_manifest(folder / "manifest.json")
    target = folder / (name + ".png")
    _check_symlinks(target, stop_at=proxy.ROOT)
    if target.exists() or name in manifest["layers"]:
        raise LayerError("Camada ja gerada; nao repetir")
    source = _read_png(folder / "cena-base.png")
    if hashlib.sha256(source).hexdigest() != manifest["source"]["sha256"]:
        raise LayerError("Imagem de referencia alterada")
    width, height = manifest["source"]["width"], manifest["source"]["height"]
    z, transparent, description = COMPONENTS[name]
    prompt = (
        "EDITE A IMAGEM FORNECIDA, nao crie nova composicao. " + description +
        f" Preserve canvas {width}x{height}, coordenadas, escala, iluminacao e identidade visual. "
        "Nao acrescente letras ou objetos inexistentes. Se for recorte, use transparencia alfa "
        "real fora do objeto, nunca fundo preto, branco nem xadrez."
    )
    response = proxy.call_proxy(url, "/v1/images/edits", key, {
        "model": model, "prompt": prompt, "n": 1, "size": f"{width}x{height}",
        "background": "transparent" if transparent else "opaque",
        "output_format": "png", "response_format": "b64_json", "stream": False,
        "input_fidelity": "high",
        "images": [{"image_url": "data:image/png;base64," + base64.b64encode(source).decode("ascii")}],
    })
    try:
        blob, extension = proxy.decode_image(response)
    except proxy.ProxyImageError as exc:
        raise LayerError("Resposta do proxy nao contem imagem valida") from exc
    if extension != ".png":
        raise LayerError("Edicao precisa produzir PNG")
    target.write_bytes(blob)
    record = {
        "file": target.name, "sha256": hashlib.sha256(blob).hexdigest(),
        "z_index": z, "requires_alpha": transparent, "technical_status": "pending",
        "human_visual_review": "pending", "model": model,
    }
    try:
        info = png_info(blob, require_alpha=transparent)
        if (info["width"], info["height"]) != (width, height):
            raise LayerError("Edicao nao preservou tamanho da cena-base")
        record.update(info)
        record["technical_status"] = "verified"
    except LayerError:
        record["technical_status"] = "rejected"
        manifest["layers"][name] = record
        _write_manifest(folder, manifest)
        raise
    manifest["layers"][name] = record
    _write_manifest(folder, manifest)
    print("Camada salva:", name, "| RGBA:", info["has_alpha"])
    return target


def run_stage(folder: Path, stage: str, selection: str, url: str, key: str, model: str) -> None:
    if stage == "basic":
        names = BASIC
    elif stage == "advanced":
        names = ("foreground-roof", "cape") if selection == "pair" else (selection,)
        if any(name not in ADVANCED for name in names):
            raise LayerError("Componente avancado nao permitido")
        layers = _read_manifest(folder / "manifest.json")["layers"]
        if any(layers.get(n, {}).get("technical_status") != "verified" for n in BASIC):
            raise LayerError("Teste 1 precisa estar aprovado antes do Teste 2")
    else:
        raise LayerError("Etapa invalida")
    for name in names:
        generate_layer(folder, name, url, key, model)


def main() -> int:
    ap = argparse.ArgumentParser(description="Separacao manual de camadas por Codex Proxy")
    ap.add_argument("action", choices=("init", "resume", "generate"))
    ap.add_argument("--channel", required=True)
    ap.add_argument("--video-id", required=True)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--source", type=Path)
    ap.add_argument("--input-dir", type=Path)
    ap.add_argument("--stage", choices=("basic", "advanced"))
    ap.add_argument("--component", default="pair")
    ap.add_argument("--url")
    ap.add_argument("--model", default="gpt-image-2")
    args = ap.parse_args()
    try:
        if args.action == "init":
            if args.source is None:
                raise LayerError("Indique --source")
            target = initialize(args.channel, args.video_id, args.scene, args.source)
        elif args.action == "resume":
            if args.input_dir is None:
                raise LayerError("Indique --input-dir")
            target = resume(args.channel, args.video_id, args.scene, args.input_dir)
        else:
            target = output_dir(args.channel, args.video_id, args.scene)
            if not args.stage or not args.url:
                raise LayerError("Indique --stage e --url")
            run_stage(target, args.stage, args.component, args.url, os.getenv("CODEX_PROXY_API_KEY", ""), args.model)
        print("Diretorio do teste:", target.relative_to(proxy.ROOT))
        return 0
    except (LayerError, proxy.ProxyImageError) as exc:
        print("TESTE REPROVADO:", str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
