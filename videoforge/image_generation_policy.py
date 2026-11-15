"""Política de geração por canal/vídeo, aplicada nos pontos de entrada.

Atualização 15/11/2026: o usuário autorizou novas imagens e peças com
referência e prompt próprios. O gate de execução permanece fechado até
definir o limite do primeiro lote e integrar o workflow com essa referência.
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
            "novas imagens autorizadas em autorizacao-visual-2026-11-15.json; "
            "execucao aguarda limite do lote e workflow com referencia canonica"
        )
