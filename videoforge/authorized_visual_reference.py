"""Read the user's canonical art direction without granting render approval."""
import hashlib
import json
from pathlib import Path
from .errors import VideoForgeError
from .scene_layers import png_info

CHANNEL = 'alchemy-lab'
VIDEO = 'mmorpg-conquiste-a-princesa-ep01'
CONTRACT = 'autorizacao-visual-2026-11-15.json'


def load_reference(root: Path, channel: str, video: str):
    if (channel, video) != (CHANNEL, VIDEO):
        return None
    base = root / 'canal' / channel / 'videos' / video
    contract = json.loads((base / CONTRACT).read_text(encoding='utf8'))
    if (contract.get('schema') != 'videoforge/user-visual-authorization/v1'
            or contract.get('channel') != channel or contract.get('video_id') != video
            or contract.get('new_images_and_parts_authorized') is not True
            or contract.get('reference_role') != 'canonical_visual_style_and_identity'):
        raise VideoForgeError('VISUAL_AUTHORIZATION_INVALID')
    def verified(key, digest, limit):
        rel = contract[key]
        if not isinstance(rel, str) or '\\' in rel or ':' in rel or '..' in Path(rel).parts:
            raise VideoForgeError('VISUAL_REFERENCE_PATH_INVALID')
        file = base / rel
        if (not file.resolve().is_relative_to(base.resolve()) or not file.is_file()
                or any(p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction())
                       for p in (file, *file.parents)) or file.stat().st_size > limit):
            raise VideoForgeError('VISUAL_REFERENCE_FILE_INVALID')
        raw = file.read_bytes()
        if hashlib.sha256(raw).hexdigest() != contract[digest]:
            raise VideoForgeError('VISUAL_REFERENCE_SHA_MISMATCH')
        return raw
    prompt = verified('prompt_file', 'prompt_sha256', 12000).decode('utf8').strip()
    source = verified('reference_file', 'reference_sha256', 32000000)
    info = png_info(source, require_alpha=False)
    if [info['width'], info['height']] != contract['reference_size']:
        raise VideoForgeError('VISUAL_REFERENCE_DIMENSIONS_MISMATCH')
    return {'contract':contract, 'prompt':prompt, 'source':source}
