"""Gera mestres da Bíblia editando referências reais SHA-verificadas.

A fonte C01-P04 V3 só é permitida como referência de arquitetura/estilo;
a pose rejeitada dos guardas jamais é aprovada nem reutilizada como ação.
"""
from __future__ import annotations
import base64
from pathlib import Path

from .dorama_continuity import reference as group_reference
from .grounded_identity import inputs as character_references
from .errors import VideoForgeError
from .visual_bible import _index
from .remake_autopilot import ROOT

MODE = "dorama-visual-bible-edit-v1"
STYLE_SHA = "605ccd361ad9a867eb8b92948010fdbb7d87a031d8b3601c663d815917b1b6cc"


def edit_payload(asset: dict, prompt: str, model: str, size: str, root: Path = ROOT):
    if (asset.get("source_mode") != MODE or model != "gpt-image-2"
            or size != "1024x1536"
            or not isinstance(prompt, str) or len(prompt) < 200):
        raise VideoForgeError("BIBLE_MASTER_REQUEST_INVALID")
    if asset.get("youtube_upload") is not False or asset.get("human_visual_approval_required") is not True:
        raise VideoForgeError("BIBLE_MASTER_APPROVAL_FLAG_INVALID")
    cat, item_id = asset.get("biblia_categoria"), asset.get("biblia_item_id")
    index = _index("alchemy-lab", Path(root) / "canal/alchemy-lab/biblia-visual")
    if cat not in index["categorias"] or not any(x.get("id") == item_id for x in index["categorias"][cat]):
        raise VideoForgeError("BIBLE_MASTER_ITEM_NOT_REGISTERED")
    approved_style, source = group_reference(root)
    if approved_style.get("sha256") != STYLE_SHA or asset.get("required_source_sha256") != STYLE_SHA:
        raise VideoForgeError("BIBLE_MASTER_STYLE_SHA_MISMATCH")
    # Para interações, NUNCA anexar a V3 de guardas com lanças mal seguradas:
    # usar somente mestres independentes, revisados por humano e SHA-verificados.
    mode = asset.get("reference_mode", "style_scene")
    if mode not in ("style_scene", "style_scene_kael", "style_scene_elara", "approved_masters_only", "identity_face_only_kael"):
        raise VideoForgeError("BIBLE_MASTER_UNSUPPORTED_REFERENCE_MODE")
    # Correção de figurino: ao criar Kael moderno, anexar SÓ o close facial
    # original. A imagem medieval inteira contaminou a primeira versão com capa.
    if mode == "identity_face_only_kael" and (cat, item_id) != ("personagens", "kael"):
        raise VideoForgeError("BIBLE_FACE_ONLY_CHARACTER_INVALID")
    if mode in ("approved_masters_only", "identity_face_only_kael"):
        references, blobs = [], []
    else:
        references = [{
            "actor": "estilo_do_palacio",
            "id": "approved-visual-reference",
            "path": approved_style["image_path"],
            "sha256": STYLE_SHA,
            "source_style_approved": True,
            "source_spear_pose_rejected": True
        }]
        blobs = [source]
    # Later character masters may attach a second ORIGINAL SHA face reference.
    if mode in ("style_scene_kael", "style_scene_elara", "identity_face_only_kael"):
        who = "kael" if mode == "identity_face_only_kael" else mode.removeprefix("style_scene_")
        matching = [x for x in character_references(root) if x["actor"] == who]
        if len(matching) != 1:
            raise VideoForgeError("BIBLE_MASTER_CHARACTER_SOURCE_MISSING")
        original = matching[0]
        blobs.append(original["bytes"])
        references.append({k: original[k] for k in ("actor", "id", "path", "sha256")})
    # Variantes reutilizam PNGs reais dos mestres já arquivados, com SHA verificado.
    # A aprovação humana não é inferida: continuam sendo candidatas para QA.
    extras = asset.get("additional_master_asset_ids", [])
    if not isinstance(extras, list) or len(extras) > 3 or len(extras) != len(set(map(str, extras))):
        raise VideoForgeError("BIBLE_MASTER_EXTRA_REFERENCES_INVALID")
    if mode == "identity_face_only_kael" and extras:
        raise VideoForgeError("BIBLE_FACE_ONLY_CANNOT_ATTACH_MEDIEVAL_BODY")
    if mode == "approved_masters_only" and not extras:
        raise VideoForgeError("BIBLE_INTERACTION_MASTERS_REQUIRED")
    if extras:
        import hashlib
        from .production_art import archived_reference
        from .visual_bible import _review
        human_reviews = _review("alchemy-lab", Path(root) / "canal/alchemy-lab/biblia-visual")
        episode = Path(root) / "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
        for dep in extras:
            if (not isinstance(dep, str) or not dep.startswith("biblia-")
                    or dep == asset.get("id")):
                raise VideoForgeError("BIBLE_MASTER_EXTRA_REFERENCE_ID_INVALID")
            found = archived_reference("alchemy-lab", "mmorpg-conquiste-a-princesa-ep01", dep, root)
            if not found:
                raise VideoForgeError("BIBLE_MASTER_EXTRA_SOURCE_NOT_ARCHIVED")
            if mode == "approved_masters_only":
                approval = human_reviews.get(found["sha256"], {})
                if (approval.get("status") != "aprovado"
                        or not approval.get("revisor") or not approval.get("evidencia")):
                    raise VideoForgeError("BIBLE_INTERACTION_SOURCE_NOT_HUMAN_APPROVED")
            path = episode / found["path"]
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 35_000_000:
                raise VideoForgeError("BIBLE_MASTER_EXTRA_SOURCE_INVALID")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != found["sha256"]:
                raise VideoForgeError("BIBLE_MASTER_EXTRA_SOURCE_SHA_MISMATCH")
            blobs.append(raw)
            references.append({
                "actor": "biblia_mestre",
                "id": dep,
                "path": str(path.relative_to(Path(root))).replace("\\", "/"),
                "sha256": found["sha256"],
                "source_spear_pose_rejected": False,
                "human_visual_approval_pending": mode != "approved_masters_only",
            })
    payload = {
        "model": model, "prompt": prompt, "size": size, "n": 1,
        "background": "opaque", "output_format": "png",
        "response_format": "b64_json", "stream": False,
        "images": [{"image_url": "data:image/png;base64," +
                    base64.b64encode(blob).decode("ascii")} for blob in blobs]
    }
    return payload, references
