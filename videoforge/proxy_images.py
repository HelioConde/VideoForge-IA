"""Cliente mínimo do Codex Proxy para GitHub Actions; nenhuma dependência extra.

Somente o proxy configurado pode receber requisições; artefatos ficam isolados
em output/<channel>/videos/<video-id>/imagens/ e não são versionados.
"""
from __future__ import annotations

import argparse
import base64
import binascii
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from .paths import CHANNEL_IDS, IDENTIFIER, _check_symlinks

ROOT = Path(__file__).resolve().parents[1]
MAX_RESPONSE = 48 * 1024 * 1024
MAX_IMAGE = 32 * 1024 * 1024
IMAGE_MODELS = {"gpt-image-2", "gpt-image-1.5"}
IMAGE_SIZES = {"1024x1536", "1024x1024", "1536x1024"}


class ProxyImageError(Exception):
    """Mensagem sanitizada; nunca inclui URL remota, resposta ou tokens."""


def endpoint(base_url: str, route: str) -> str:
    parsed = urllib.parse.urlsplit(base_url.strip())
    if parsed.scheme == "https" and parsed.hostname:
        pass
    elif (parsed.scheme == "http" and parsed.hostname == "127.0.0.1"
          and parsed.port == 18080):
        pass
    else:
        raise ProxyImageError("Usar URL HTTPS do proxy persistente ou loopback fixo do job.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path.rstrip("/") not in ("", "/v1"):
        raise ProxyImageError("A URL do proxy deve conter apenas a origem (ou /v1).")
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]
    return base + route


def call_proxy(base_url: str, route: str, api_key: str, payload: dict | None = None) -> dict:
    if not api_key or len(api_key) < 20:
        raise ProxyImageError("CODEX_PROXY_API_KEY ausente ou curta demais.")
    address = endpoint(base_url, route)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        address,
        data=body,
        headers={
            "Authorization": "Bearer " + api_key,
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if body is not None else {}),
        },
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            raw = r.read(MAX_RESPONSE + 1)
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise ProxyImageError("Proxy limitou a chamada (HTTP 429). Verifique cotas, sem tentativas cegas.") from None
        raise ProxyImageError(f"Proxy retornou HTTP {exc.code}; corpo omitido por seguranca.") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ProxyImageError("Nao foi possivel comunicar com o proxy; detalhes privados omitidos.") from None
    if len(raw) > MAX_RESPONSE:
        raise ProxyImageError("Resposta da imagem excede limite de tamanho.")
    try:
        response = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ProxyImageError("Proxy nao retornou JSON valido.") from None
    if not isinstance(response, dict):
        raise ProxyImageError("Formato de resposta invalido.")
    return response


def health(base_url: str, api_key: str) -> None:
    result = call_proxy(base_url, "/health", api_key)
    if result.get("status") != "ok" or not isinstance(result.get("accounts"), int) or result["accounts"] < 1:
        raise ProxyImageError("Proxy acessivel, mas sem contas cadastradas; revise o servidor ou secret.")
    print("Health autenticado: ok; pelo menos uma conta cadastrada (disponibilidade/quotas nao testadas).")


def destination(channel: str, video_id: str, scene: str) -> Path:
    if channel not in CHANNEL_IDS:
        raise ProxyImageError("Canal nao reconhecido.")
    for value in (video_id, scene):
        if not isinstance(value, str) or len(value) > 64 or not IDENTIFIER.fullmatch(value):
            raise ProxyImageError("Identificador de video/cena invalido.")
    cfg = ROOT / "canal" / channel / "canal.json"
    try:
        if cfg.is_symlink() or json.loads(cfg.read_text(encoding="utf-8")).get("id") != channel:
            raise ValueError()
    except (OSError, ValueError, KeyError):
        raise ProxyImageError("Configuracao do canal invalida.") from None
    folder = ROOT / "output" / channel / "videos" / video_id / "imagens"
    _check_symlinks(folder, stop_at=ROOT)
    return folder / scene


def decode_image(data: dict) -> tuple[bytes, str]:
    records = data.get("data")
    if not isinstance(records, list) or len(records) != 1 or not isinstance(records[0], dict):
        raise ProxyImageError("Proxy nao retornou exatamente uma imagem.")
    item = records[0]
    raw = item.get("b64_json")
    if raw is None:
        raw = item.get("url")
    if not isinstance(raw, str):
        raise ProxyImageError("Sem imagem base64; URLs remotas nao sao baixadas.")
    if raw.startswith("data:image/"):
        if ";base64," not in raw:
            raise ProxyImageError("Data URL invalida.")
        raw = raw.split(";base64,", 1)[1]
    elif "://" in raw or raw.startswith("data:"):
        raise ProxyImageError("URLs remotas ou arquivos externos nao sao aceitos.")
    if len(raw) > (MAX_IMAGE * 4 // 3) + 128:
        raise ProxyImageError("Imagem excede limite de tamanho.")
    try:
        binary = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        raise ProxyImageError("Base64 da imagem invalido.") from None
    if len(binary) < 50 or len(binary) > MAX_IMAGE:
        raise ProxyImageError("Imagem vazia ou grande demais.")
    if binary.startswith(b"\x89PNG\r\n\x1a\n") and b"IEND" in binary[-20:]:
        return binary, ".png"
    if binary.startswith(b"\xff\xd8\xff") and binary.endswith(b"\xff\xd9"):
        return binary, ".jpg"
    if binary.startswith(b"RIFF") and binary[8:12] == b"WEBP" and int.from_bytes(binary[4:8], "little") + 8 == len(binary):
        return binary, ".webp"
    raise ProxyImageError("Imagem nao tem assinatura/terminador PNG, JPEG ou WebP valido.")


def generate(base_url: str, api_key: str, channel: str, video_id: str,
             scene: str, model: str, size: str, prompt: str) -> Path:
    target = destination(channel, video_id, scene)
    if model not in IMAGE_MODELS or size not in IMAGE_SIZES:
        raise ProxyImageError("Modelo ou tamanho fora da lista permitida.")
    if not isinstance(prompt, str) or not 10 <= len(prompt.strip()) <= 5000:
        raise ProxyImageError("Prompt obrigatorio entre 10 e 5000 caracteres.")
    response = call_proxy(
        base_url, "/v1/images/generations", api_key,
        {"model": model, "prompt": prompt, "size": size,
         "n": 1, "stream": False, "response_format": "b64_json"},
    )
    binary, extension = decode_image(response)
    target.parent.mkdir(parents=True, exist_ok=True)
    _check_symlinks(target.parent, stop_at=ROOT)
    final = target.with_suffix(extension)
    if final.exists():
        raise ProxyImageError("A imagem desta cena ja existe neste job; nao sobrescrever.")
    temp = final.with_name("." + final.name + ".tmp")
    temp.write_bytes(binary)
    temp.replace(final)
    report = {
        "schema": "videoforge/proxy-image/v1",
        "canal": channel,
        "video_id": video_id,
        "cena": scene,
        "modelo": model,
        "tamanho_solicitado": size,
        "arquivo": final.name,
        "bytes": len(binary),
        "sha256": hashlib.sha256(binary).hexdigest(),
        "criado_em_utc": datetime.now(timezone.utc).isoformat(),
        "publicado_youtube": False,
        "qa_visual": "pendente",
        "origem": "codex-proxy (modelo e disponibilidade dependem do upstream)",
    }
    final.with_suffix(".meta.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    return final


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex Proxy no VideoForge (sem expor segredos)")
    parser.add_argument("operation", choices=["health", "generate"])
    parser.add_argument("--url", required=True)
    parser.add_argument("--channel")
    parser.add_argument("--video-id")
    parser.add_argument("--scene")
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--size", default="1024x1536")
    args = parser.parse_args()
    try:
        key = os.getenv("CODEX_PROXY_API_KEY", "")
        if args.operation == "health":
            health(args.url, key)
        else:
            image = generate(
                args.url, key, args.channel, args.video_id, args.scene,
                args.model, args.size, os.getenv("IMAGE_PROMPT", ""),
            )
            print("Imagem salva em:", image.relative_to(ROOT))
            print("Arquivo apenas no artifact do workflow, nunca enviado ao YouTube.")
    except ProxyImageError as exc:
        print("ERRO:", exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
