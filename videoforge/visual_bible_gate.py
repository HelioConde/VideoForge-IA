"""Barreira de geração: cena nova só usa mestres canônicos da Bíblia.

Um item planejado/gerado ou um PNG de estilo aprovado parcialmente NÃO
pode ser usado como personagem, prop ou interação física pronta.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from .errors import VideoForgeError
from .paths import CHANNEL_IDS, IDENTIFIER
from .remake_autopilot import ROOT
from .visual_bible import _index, _read, VALID_STATES, SHA

SHOT = re.compile(r"^C[0-9]{2}-P[0-9]{2}$")
QUEUES = {"alchemy-lab": "mmorpg-conquiste-a-princesa-ep01"}


def require_ready(channel: str, video_id: str, shot_id: str, root: Path = ROOT):
    if (channel not in CHANNEL_IDS or not isinstance(video_id, str)
            or not IDENTIFIER.fullmatch(video_id)
            or not isinstance(shot_id, str) or not SHOT.fullmatch(shot_id)):
        raise VideoForgeError("BIBLE_SCENE_SCOPE_INVALID")
    if QUEUES.get(channel) != video_id:
        return {"checked": False, "reason": "no_episode_bible_queue_defined"}
    root = Path(root)
    bible = root / "canal" / channel / "biblia-visual"
    index = _index(channel, bible)
    queue = _read(bible / "FILA-EP01.json")
    if (queue.get("schema") != "videoforge/visual-bible-episode-queue/v1"
            or queue.get("episode") != video_id or not isinstance(queue.get("tomadas"), list)):
        raise VideoForgeError("BIBLE_SCENE_QUEUE_INVALID")
    rows = [x for x in queue["tomadas"] if x.get("id") == shot_id]
    if len(rows) != 1:
        raise VideoForgeError("BIBLE_SCENE_SHOT_NOT_IN_QUEUE")
    shot = rows[0]
    if shot_id == "C01-P01" and shot.get("status") == "tela_preta_sem_png":
        return {"checked": True, "ready": True, "source": "black_screen_no_image"}
    if queue.get("hold") is True or index.get("hold_novas_cenas") is True:
        raise VideoForgeError("BIBLE_SCENE_PRODUCTION_HOLD_ACTIVE")
    requirements = [
        ("personagens", x) for x in shot.get("personagens", [])
    ] + [("cenarios", shot.get("cenario"))] + [
        ("objetos", x) for x in shot.get("objetos", [])
    ] + [("interacoes", x) for x in shot.get("interacoes", [])]
    if not requirements or any(not isinstance(x, str) or not x for _, x in requirements):
        raise VideoForgeError("BIBLE_SCENE_MISSING_DEPENDENCIES")
    verified = []
    for category, item_id in requirements:
        if category not in index["categorias"]:
            raise VideoForgeError("BIBLE_SCENE_CATEGORY_INVALID")
        found = [x for x in index["categorias"][category] if x.get("id") == item_id]
        if len(found) != 1:
            raise VideoForgeError("BIBLE_SCENE_UNKNOWN_ITEM")
        item = found[0]
        if item.get("status") != "aprovado":
            raise VideoForgeError("BIBLE_SCENE_MASTER_NOT_APPROVED")
        key = item.get("imagem_canonica")
        if (not isinstance(key, dict)
                or not isinstance(key.get("arquivo"), str)
                or not SHA.fullmatch(str(key.get("sha256", "")))):
            raise VideoForgeError("BIBLE_SCENE_CANONICAL_SOURCE_REQUIRED")
        path = Path(key["arquivo"])
        if path.is_absolute() or ".." in path.parts or "\\" in key["arquivo"]:
            raise VideoForgeError("BIBLE_SCENE_CANONICAL_PATH_INVALID")
        image = root / path
        if image.is_symlink() or not image.is_file() or image.stat().st_size > 35_000_000:
            raise VideoForgeError("BIBLE_SCENE_CANONICAL_IMAGE_MISSING")
        if hashlib.sha256(image.read_bytes()).hexdigest() != key["sha256"]:
            raise VideoForgeError("BIBLE_SCENE_CANONICAL_SHA_CHANGED")
        status_path = bible / category / item_id / "status.json"
        state = _read(status_path)
        if state.get("status") != "aprovado" or state.get("aprovacao_mestra") is not True:
            raise VideoForgeError("BIBLE_SCENE_APPROVAL_RECORD_MISSING")
        verified.append({"categoria": category, "id": item_id, "sha256": key["sha256"]})
    return {"checked": True, "ready": True, "shot": shot_id, "referencias": verified}


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--channel", required=True)
    p.add_argument("--video-id", required=True)
    p.add_argument("--shot", required=True)
    a = p.parse_args()
    print("BIBLE_SCENE_PREFLIGHT", json.dumps(require_ready(a.channel, a.video_id, a.shot)))


if __name__ == "__main__":
    main()
