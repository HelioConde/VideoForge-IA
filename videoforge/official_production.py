"""Diagnóstico fail-closed do fluxo oficial VideoForge-IA.

Não gera placeholders, não marca previews como vídeo oficial,
não consulta/secreta credenciais e não gasta chamadas de IA.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from .errors import VideoForgeError
from .paths import CHANNEL_IDS, IDENTIFIER

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_STAGES = (
    "pesquisa", "roteiro", "geracao_arte", "separacao_camadas",
    "animacao", "narracao", "edicao", "qa_tecnico", "qa_visual",
)


def preflight(channel: str, video_id: str, *, root: Path = ROOT,
              env: dict[str, str] | None = None) -> dict:
    """Confere viabilidade antes de iniciar produção oficial no Actions."""
    if channel not in CHANNEL_IDS or (not isinstance(video_id, str)
        or len(video_id) > 64 or IDENTIFIER.fullmatch(video_id) is None):
        raise VideoForgeError("OFFICIAL_CHANNEL_OR_VIDEO_ID_INVALID")
    environment = os.environ if env is None else env
    root = Path(root)
    directory = root / "canal" / channel / "videos" / video_id
    report = {"schema": "videoforge/official-production-preflight/v1",
              "repository": "HelioConde/VideoForge-IA",
              "channel": channel, "video_id": video_id,
              "requested_mode": "official_program_only",
              "youtube_upload": False, "official_mp4_created": False,
              "scene_limit": None, "blockers": [], "checks": {},
              "required_stages": list(REQUIRED_STAGES)}
    blockers = report["blockers"]
    def check(name: str, ok: bool, code: str) -> None:
        report["checks"][name] = bool(ok)
        if not ok:
            blockers.append(code)

    def load(path: Path) -> dict | None:
        if (path.is_symlink() or not path.is_file()
                or path.stat().st_size > 200_000):
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except (OSError, ValueError, UnicodeError):
            return None

    editorial = load(directory / "editorial.json")
    story = load(directory / "roteiro.json")
    manifest = load(directory / "video.json")
    check("editorial_exists", editorial is not None,
          "EDITORIAL_RECORD_MISSING")
    check("storyboard_exists", story is not None,
          "STORYBOARD_MISSING")
    check("manifest_exists", manifest is not None,
          "VIDEO_MANIFEST_MISSING")
    if manifest is not None:
        check("channel_bound", manifest.get("channel") == channel
              and manifest.get("youtube_upload") is False,
              "MANIFEST_CHANNEL_OR_UPLOAD_INVALID")
    if story is not None and manifest is not None:
        scenes = story.get("scenes", [])
        media = manifest.get("scenes", [])
        same = (isinstance(scenes, list) and bool(scenes)
                and isinstance(media, list) and len(scenes) == len(media)
                and all(isinstance(x, dict) and isinstance(y, dict)
                        and x.get("image") == y.get("image")
                        and x.get("audio") == y.get("audio")
                        for x, y in zip(scenes, media)))
        check("scene_contract", same, "STORYBOARD_MEDIA_MISMATCH")
        if same:
            report["scene_count"] = len(scenes)
    if editorial is not None:
        check("correct_video_id", editorial.get("video_id") == video_id
              and editorial.get("canal_id") == channel,
              "EDITORIAL_CHANNEL_OR_ID_INVALID")
        # Nunca confundir relatório de preview com progresso de arte final.
        production = editorial.get("producao", {})
        check("not_using_experimental_as_official",
              isinstance(production, dict)
              and production.get("video_oficial_do_programa") is False,
              "EXPERIMENTAL_RENDER_CANNOT_BE_USED_AS_OFFICIAL")

    model = load(root / "modelos" / "camadas-animadas" / "modelo.json")
    check("layered_animation_model_operational",
          model is not None and model.get("operacional") is True,
          "LAYERED_ANIMATION_MODEL_NOT_OPERATIONAL")
    # O MVP atual só aceita o modelo de imagens estáticas fornecidas.
    from .paths import SUPPORTED_RENDER_MODELS
    check("official_renderer_supports_layered_model",
          "camadas-animadas" in SUPPORTED_RENDER_MODELS,
          "OFFICIAL_RENDERER_HAS_NO_LAYERED_PIPELINE")
    # O programa atual tem scripts de prévias, mas não orquestra agentes,
    # geração de artes, camadas e QA como uma produção integrada.
    agents_dir = root / "agentes"
    check("operational_agents_integrated",
          agents_dir.is_dir() and (agents_dir / "pipeline.json").is_file(),
          "OFFICIAL_AGENTS_NOT_INTEGRATED")
    check("original_anime_art_generator_integrated",
          (root / "geradores" / "anime" / "pipeline.json").is_file(),
          "SCENE_ART_GENERATOR_NOT_INTEGRATED")
    # Só indica presença de config, nunca imprime chaves/URL e não chama proxy.
    proxy = (bool(environment.get("CODEX_PROXY_API_KEY"))
             and (bool(environment.get("CODEX_PROXY_BASE_URL"))
                  or bool(environment.get("CODEX_PROXY_ACCOUNTS_JSON"))))
    check("image_provider_configured", proxy, "CODEX_PROXY_CONFIG_NOT_READY")
    # Assets de trabalho precisam ser originais do run atual e auditáveis,
    # nunca substituídos por arte vetorial ou MP4 de preview legado.
    check("approved_source_art_available",
          False, "SCENE_ART_AND_RGBA_LAYERS_NOT_GENERATED")
    report["ready"] = len(blockers) == 0
    report["state"] = "ready" if report["ready"] else "pipeline_pendente"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="VideoForge official production preflight")
    parser.add_argument("--channel", default="otaku-br")
    parser.add_argument("--video-id", required=True)
    arguments = parser.parse_args()
    result = preflight(arguments.channel, arguments.video_id)
    output = (ROOT / "output" / arguments.channel / "videos"
              / arguments.video_id / "official-preflight.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    result["checked_at_utc"] = datetime.now(timezone.utc).isoformat()
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("VIDEOFORGE_OFFICIAL_PREFLIGHT", result["state"])
    print("scene_count:", result.get("scene_count"))
    for b in result["blockers"]:
        print("BLOCKER:", b)
    print("Report:", output.relative_to(ROOT))
    return 0 if result["ready"] else 2


if __name__ == "__main__":
    sys.exit(main())
