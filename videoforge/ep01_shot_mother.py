"""Cena-mãe real do dorama EP01: referências da Bíblia -> edição no proxy.

Uma chamada de imagem por execução. Não gera pose isolada, camada inventada,
rig fictício ou MP4. Persiste o PNG + proveniência, sujeitos a revisão visual.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from .errors import VideoForgeError
from . import image_generation_policy, proxy_images
from .layered_shot_plan import CHANNEL, VIDEO, REL, ROOT, validate as validate_layer_plan
from .production_art import archived_reference
from .scene_layers import png_info

SCHEMA = "videoforge/episode-layered-shot-references/v1"
ASSET_NAME = re.compile(r"^biblia-[a-z0-9-]{2,90}$")
SHOT_NAME = re.compile(r"^C[0-9]{2}-P[0-9]{2}$")
ARCHIVE_PRODUCER = "production-scene-mother-v2"
MAX_REFERENCE_PNGS_PER_REQUEST = 8  # Only a wire-payload bound, NOT a limit of scenes/images
MAX_REFERENCE_BYTES = 35_000_000


def read_refs(root: Path = ROOT) -> dict:
    path = Path(root) / REL / "REFERENCIAS-CENAS-MAE-EP01.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100_000:
        raise VideoForgeError("EP01_MOTHER_REFERENCE_PLAN_MISSING")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise VideoForgeError("EP01_MOTHER_REFERENCE_PLAN_INVALID") from exc
    if (doc.get("schema") != SCHEMA
            or doc.get("channel") != CHANNEL or doc.get("video_id") != VIDEO
            or doc.get("shots_count") != 40
            or doc.get("scene_mothers_to_generate") != 39
            or doc.get("max_chargeable_calls_per_run") != 1
            or doc.get("youtube_upload") is not False
            or doc.get("auto_visual_approval") is not False):
        raise VideoForgeError("EP01_MOTHER_REFERENCE_PLAN_SCOPE_INVALID")
    items = doc.get("shots")
    if not isinstance(items, list) or len(items) != 40:
        raise VideoForgeError("EP01_MOTHER_REFERENCE_PLAN_COVERAGE_INVALID")
    ids = [row.get("id") if isinstance(row, dict) else None for row in items]
    if len(set(ids)) != 40 or not all(isinstance(x, str) and SHOT_NAME.fullmatch(x) for x in ids):
        raise VideoForgeError("EP01_MOTHER_REFERENCE_PLAN_IDS_INVALID")
    if next(item for item in items if item["id"] == "C01-P01").get("reference_asset_ids") != []:
        raise VideoForgeError("EP01_MOTHER_BLACK_FRAME_REFERENCES_FORBIDDEN")
    for row in items:
        ids = row.get("reference_asset_ids")
        if row["id"] == "C01-P01":
            continue
        if (not isinstance(ids, list) or not 1 <= len(ids) <= MAX_REFERENCE_PNGS_PER_REQUEST
                or len(ids) != len(set(ids))
                or any(not isinstance(x, str) or not ASSET_NAME.fullmatch(x) for x in ids)
                or row.get("portrait_v1_rejected_never_attached") is not True):
            raise VideoForgeError("EP01_MOTHER_REFERENCE_IDS_OR_SAFETY_INVALID")
        if any(x in ids for x in (
            "biblia-lanca-guarda-completa-v1", "biblia-carrasco-base-v1",
            "biblia-mascarado-1-base-v1", "biblia-mascarado-2-base-v1",
            "biblia-figurantes-base-v1", "biblia-mascarados-base-v1",
            "biblia-kael-casual-antes-v1",
        )):
            raise VideoForgeError("EP01_MOTHER_REJECTED_V1_REFERENCE_FORBIDDEN")
    return doc


def existing_mother(shot_id: str, root: Path = ROOT) -> dict | None:
    """Treat even an incomplete archive as a blocker against a second paid call."""
    episode = Path(root) / REL
    archive = episode / "assets" / "geracoes" / ARCHIVE_PRODUCER
    name = shot_id.lower() + "-scene-mother.png"
    if archive.is_symlink():
        raise VideoForgeError("EP01_MOTHER_ARCHIVE_SYMLINK")
    if not archive.exists():
        return None
    found = []
    for run in archive.iterdir():
        if run.is_symlink():
            raise VideoForgeError("EP01_MOTHER_ARCHIVE_RUN_SYMLINK")
        if not run.is_dir() or not run.name.isdecimal():
            continue
        png = run / name
        manifest = run / "manifesto-geracoes.json"
        if png.is_symlink() or manifest.is_symlink():
            raise VideoForgeError("EP01_MOTHER_ARCHIVE_FILE_SYMLINK")
        if not png.exists():
            continue
        if not png.is_file() or not manifest.is_file():
            raise VideoForgeError("EP01_MOTHER_INCOMPLETE_ARCHIVE_STOP")
        try:
            obj = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError) as exc:
            raise VideoForgeError("EP01_MOTHER_MANIFEST_INVALID") from exc
        entries = [x for x in obj.get("images", [])
                   if isinstance(x, dict) and x.get("file") == name]
        if (obj.get("schema") != "videoforge/permanent-generated-image-archive/v1"
                or obj.get("channel") != CHANNEL or obj.get("video_id") != VIDEO
                or obj.get("producer") != ARCHIVE_PRODUCER
                or obj.get("github_run_id") != int(run.name)
                or len(entries) != 1):
            raise VideoForgeError("EP01_MOTHER_ARCHIVE_PROVENANCE_INVALID")
        binary = png.read_bytes()
        digest = hashlib.sha256(binary).hexdigest()
        if digest != entries[0].get("sha256"):
            raise VideoForgeError("EP01_MOTHER_ARCHIVE_SHA_MISMATCH")
        found.append({"shot_id": shot_id, "run_id": int(run.name), "sha256": digest})
    return max(found, key=lambda x: x["run_id"]) if found else None


def prepare(shot_id: str, root: Path = ROOT):
    root = Path(root)
    result = validate_layer_plan(root)
    refs = read_refs(root)
    if not isinstance(shot_id, str) or not SHOT_NAME.fullmatch(shot_id):
        raise VideoForgeError("EP01_MOTHER_SHOT_ID_INVALID")
    if shot_id == "C01-P01":
        raise VideoForgeError("EP01_MOTHER_BLACK_FRAME_NO_PAID_IMAGE")
    row = next((x for x in refs["shots"] if x["id"] == shot_id), None)
    timeline = json.loads((root / REL / "PLANO-CAMADAS-CAMERA-EP01.json").read_text(encoding="utf-8"))
    shot = next((x for x in timeline["shots"] if x["id"] == shot_id), None)
    if row is None or shot is None or shot.get("scene_status") != "planned_pending_real_assets":
        raise VideoForgeError("EP01_MOTHER_SHOT_NOT_IN_VALID_PLAN")
    if existing_mother(shot_id, root):
        raise VideoForgeError("EP01_MOTHER_ALREADY_ARCHIVED_SHA_NO_REPEAT")
    provenance, image_bytes = [], []
    for asset_id in row["reference_asset_ids"]:
        item = archived_reference(CHANNEL, VIDEO, asset_id, root)
        if item is None:
            raise VideoForgeError("EP01_MOTHER_REFERENCE_NOT_ARCHIVED " + asset_id)
        rel = Path(item["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise VideoForgeError("EP01_MOTHER_REFERENCE_PATH_INVALID")
        origin = root / REL / rel
        if origin.is_symlink() or not origin.is_file() or origin.stat().st_size > MAX_REFERENCE_BYTES:
            raise VideoForgeError("EP01_MOTHER_REFERENCE_PNG_INVALID")
        data = origin.read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise VideoForgeError("EP01_MOTHER_REFERENCE_SHA_TAMPERED")
        image_bytes.append(data)
        provenance.append({"id": asset_id, "sha256": item["sha256"],
                           "path": str((REL / rel).as_posix()),
                           "source_role": "visual_identity_or_environment_not_pose",
                           "visual_approval_pending": True})
    camera = shot["camera"]
    actors = [x["id"] for x in shot["images"].get("characters", [])]
    objects = [x["id"] for x in shot["images"].get("objects", [])]
    unique = ", ".join(row["reference_asset_ids"])
    prompt = (
        "GERAR APENAS UMA IMAGEM-MÃE DA TOMADA, COMO UM FRAME ÚNICO ANIMÁVEL DE "
        "DORAMA FANTASIA ANIME 2D SEMIRREALISTA CINEMATOGRÁFICO. "
        "As imagens ORIGINAIS da Bíblia Visual estão realmente anexadas. "
        "Personagens, roupas, proporções, cores, objetos e cenário devem manter "
        "as identidades e geometria desses PNGs fonte; NÃO juntar as imagens "
        "como colagem, turnaround, character sheet ou poses alternativas. "
        f"TOMADA {shot_id}; beat: {shot['editorial_beat']}. "
        f"DIREÇÃO VISUAL: {shot['visual_prompt']}. "
        f"CÂMERA: tipo {camera['shot_type']}, lente cinematográfica {camera['lens_mm']}mm, "
        f"FOCO PRINCIPAL {camera['primary_focus']}; movimento posterior em Remotion "
        f"'{camera['virtual_motion']}' (NÃO pintar trilhas de movimento). "
        f"ELENCO PERMITIDO SOMENTE SE VISÍVEL NESTE ENQUADRAMENTO: {', '.join(actors) or 'nenhum'}. "
        f"OBJETOS DA CENA/REFERÊNCIA QUANDO DE FATO VISÍVEIS: {', '.join(objects) or 'nenhum'}. "
        f"REFERÊNCIAS: {unique}. "
        "Após aprovação desta cena-mãe, o proxy deverá GERAR NOVAS IMAGENS "
        "INDEPENDENTES para background vazio, cada personagem, cada objeto móvel e "
        "partes de rig em PNG RGBA transparente, usando este frame e a Bíblia como "
        "REFERÊNCIAS. NÃO extrair sprites por crop, máscara, segmentação ou recorte "
        "de pixels do quadro. O fundo vazio deve preencher geometria oculta sem "
        "alterar o ângulo, a iluminação ou a perspectiva. "
        "Luz, sombras e escala consistentes. Não gerar texto, HUD, logotipo, "
        "quadrinhos, painéis múltiplos nem personagens ausentes; foco protegido. "
        "Composição vertical para vídeo 9:16, margem segura para crop sem esticar o frame. "
        "Lanças palacianas, se presentes, DEVEM ser seguradas pelo TERÇO INFERIOR perto "
        "DA BASE de cada haste, dedos e polegar fechados REALMENTE ao redor da madeira, "
        "punho conectado ao antebraço. Pontas cruzadas EM X ALTO, nunca mãos cruzadas "
        "nem lança flutuante; usar lança portátil V2 fina, NÃO a antiga V1 tipo pedestal. "
        "NUNCA reutilizar a cena C01-P04 V3/V4 como referência anatômica. "
        "Sem violência gráfica. Esta é imagem candidata; NÃO aprovar automaticamente."
    )
    if len(prompt) > 5000:
        raise VideoForgeError("EP01_MOTHER_PROMPT_TOO_LONG")
    if not 1 <= len(image_bytes) <= MAX_REFERENCE_PNGS_PER_REQUEST:
        raise VideoForgeError("EP01_MOTHER_IMAGE_INPUT_COUNT_INVALID")
    return {
        "shot_id": shot_id, "shot": shot, "references": provenance, "blobs": image_bytes,
        "prompt": prompt, "technical_preflight": result,
    }


def generate(shot_id: str, url: str, model: str = "gpt-image-2", root: Path = ROOT) -> dict:
    image_generation_policy.assert_image_generation_allowed(CHANNEL, VIDEO, root)
    if model != "gpt-image-2":
        raise VideoForgeError("EP01_MOTHER_MODEL_INVALID")
    spec = prepare(shot_id, root)
    asset_id = shot_id.lower() + "-scene-mother"
    output = Path(root) / "output" / CHANNEL / "videos" / VIDEO / "imagens"
    image = output / (asset_id + ".png")
    metadata = output / (asset_id + ".production.json")
    if image.is_symlink() or metadata.is_symlink() or image.exists() or metadata.exists():
        raise VideoForgeError("EP01_MOTHER_OUTPUT_ALREADY_EXISTS")
    payload = {
        "model": model, "prompt": spec["prompt"], "size": "1024x1536",
        "n": 1, "background": "opaque", "output_format": "png",
        "response_format": "b64_json", "stream": False,
        "images": [
            {"image_url": "data:image/png;base64," + base64.b64encode(data).decode("ascii")}
            for data in spec["blobs"]
        ],
    }
    result = proxy_images.call_proxy(
        url, "/v1/images/edits", os.getenv("CODEX_PROXY_API_KEY", ""), payload)
    blob, ext = proxy_images.decode_image(result)
    if ext != ".png":
        raise VideoForgeError("EP01_MOTHER_OUTPUT_NOT_PNG")
    info = png_info(blob, require_alpha=False)
    if (not 512 <= info["width"] <= 2048 or not 512 <= info["height"] <= 3072
            or info["width"] >= info["height"]):
        raise VideoForgeError("EP01_MOTHER_OUTPUT_DIMENSIONS_INVALID")
    output.mkdir(parents=True, exist_ok=True)
    image.write_bytes(blob)
    digest = hashlib.sha256(blob).hexdigest()
    report = {
        "schema": "videoforge/ep01-shot-mother-result/v1",
        "channel": CHANNEL, "video_id": VIDEO, "asset_id": asset_id,
        "candidate_scene_shot_id": shot_id,
        "file": str(image.relative_to(Path(root)).as_posix()),
        "sha256": digest, "bytes": len(blob), "width": info["width"],
        "height": info["height"], "model": model, "size": "1024x1536",
        "source_originals_sha_verified": spec["references"],
        "source_images_attached_to_request": len(spec["references"]),
        "technical_qa": "valid_png_source_refs_sha_verified",
        "human_visual_approval": False,
        "scene_complete": False, "background_generated": False,
        "characters_rgba_generated": False, "rig_generated": False,
        "camera_plan_registered": True, "mp4_generated": False,
        "youtube_uploaded": False,
    }
    metadata.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--model", default="gpt-image-2")
    args = parser.parse_args()
    try:
        result = generate(args.shot_id, args.url, args.model)
        print("EP01_MOTHER_GENERATED", json.dumps({
            "shot_id": result["candidate_scene_shot_id"],
            "sha256": result["sha256"], "image_inputs": result["source_images_attached_to_request"],
            "human_approved": False, "youtube_uploaded": False
        }, ensure_ascii=False))
        return 0
    except (OSError, ValueError, VideoForgeError, proxy_images.ProxyImageError) as exc:
        print("EP01_MOTHER_BLOCKED", str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
