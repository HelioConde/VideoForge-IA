"""Política de geração por canal/vídeo, aplicada nos pontos de entrada.

Regra expressa do usuário: NÃO gerar imagens novas para Alchemy Lab EP01.
O veto vale para uso manual, Python direto ou GitHub Actions, mesmo se o
workflow não receber CHANNEL/VIDEO_ID como variável de ambiente. Para
reativar este episódio no futuro será preciso autorização explícita e
revisão consciente desta política além do arquivo lock.
"""
from __future__ import annotations

from .errors import VideoForgeError

BLOCKED_CHANNEL="alchemy-lab"
BLOCKED_VIDEO_ID="mmorpg-conquiste-a-princesa-ep01"

def assert_image_generation_allowed(channel: str, video_id: str) -> None:
    if channel == BLOCKED_CHANNEL and video_id == BLOCKED_VIDEO_ID:
        raise VideoForgeError(
            "IMAGE_GENERATION_DENIED_ALCHEMY_EP01: "
            "o usuario proibiu novas imagens para este episodio; "
            "usar somente PNGs existentes no canal/alchemy-lab"
        )
