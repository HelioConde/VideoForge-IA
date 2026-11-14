"""Importar um ZIP de PNGs JÁ gerados no chat, sem criar imagem alguma.

Requer upload manual do ZIP (8 imagens) ao repositório. Preserva bytes exatos,
SHA e status não aprovado. Não utiliza proxy, IA, Remotion ou publicação.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zipfile

BASE=Path("canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01")
DEST=BASE/"assets/cena-01/variacoes-geradas-na-conversa"
EXPECTED={
    "rei-aldric-v1.png","guarda-esquerdo-v1.png","guarda-direito-v1.png",
    "lanca-esquerda-v1.png","lanca-direita-v1.png",
    "guarda-esquerdo-v2.png","guarda-direito-v2.png",
    "trono-ornamental-v1.png",
}
class ImportErrorSafe(ValueError): pass

def sha(blob:bytes)->str:return hashlib.sha256(blob).hexdigest()

def import_bundle(archive:Path)->dict:
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_size>30_000_000:
        raise ImportErrorSafe("BUNDLE_MISSING_OR_OVERSIZED")
    if DEST.exists():
        raise ImportErrorSafe("DEST_EXISTS_FAIL_CLOSED")
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist())!=9 or any(info.file_size>9_000_000 for info in z.infolist()):
            raise ImportErrorSafe("UNEXPECTED_ZIP_CONTENT")
        if "manifesto.json" not in z.namelist():
            raise ImportErrorSafe("MANIFEST_MISSING")
        manifest=json.loads(z.read("manifesto.json"))
        if (manifest.get("schema")!="videoforge/external-chat-assets/v1"
            or manifest.get("channel")!="alchemy-lab"
            or manifest.get("video_id")!=BASE.name
            or manifest.get("new_image_generation_calls")!=0):
            raise ImportErrorSafe("EXTERNAL_PROVENANCE_INVALID")
        rows=manifest.get("assets",[])
        names={x.get("file") for x in rows if isinstance(x,dict)}
        if names!=EXPECTED or len(rows)!=len(EXPECTED):
            raise ImportErrorSafe("EXTERNAL_ASSET_LIST_MISMATCH")
        if set(z.namelist())!={"manifesto.json"}|{"imagens/"+n for n in EXPECTED}:
            raise ImportErrorSafe("ZIP_PATHS_INVALID")
        checked=[]
        for meta in rows:
            name=meta["file"]
            if not re.fullmatch(r"[a-z0-9-]{2,80}\.png",name):
                raise ImportErrorSafe("BAD_FILENAME")
            blob=z.read("imagens/"+name)
            if not 150<=len(blob)<9_000_000 or sha(blob)!=meta.get("sha256"):
                raise ImportErrorSafe("HASH_MISMATCH_"+name)
            if not blob.startswith(b"\x89PNG\r\n\x1a\n") or blob[12:16]!=b"IHDR":
                raise ImportErrorSafe("INVALID_PNG_"+name)
            w,h=struct.unpack(">II",blob[16:24])
            if (w,h)!=(meta["width"],meta["height"]) or (w,h)!=(1086,1448):
                raise ImportErrorSafe("IMAGE_CANVAS_MISMATCH_"+name)
            checked.append((name,blob,meta))
        DEST.mkdir(parents=True)
        entries=[]
        for name,blob,meta in checked:
            (DEST/name).write_bytes(blob)
            entries.append({"file":name,"sha256":sha(blob),"bytes":len(blob),
                            "source":"chat_imagegen_previously_existing",
                            "shape":[meta["width"],meta["height"]],
                            "alignment_with_original_scene":"NOT_VERIFIED",
                            "source_sha_match":"NOT_ESTABLISHED",
                            "human_visual_approval":False,"rig_ready":False})
        report={"schema":"videoforge/external-image-import-qa/v1",
                "source":"uploaded_preexisting_chat_images",
                "new_image_generation_calls":0,
                "channel":"alchemy-lab","video_id":BASE.name,
                "assets":entries,"count":len(entries),
                "visual_qa":"pending","rig_ready":False,"youtube_uploaded":False,
                "important":"Candidatos de 1086x1448; NAO sao partes extraidas pixel a pixel da mae de 1024x1536"}
        (DEST/"catalogo.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        print("CHAT_PNG_ARCHIVE_IMPORTED",len(entries),"assets, no image generated")
        return report

def main()->int:
    if len(sys.argv)!=2:raise SystemExit("Uso: python -m videoforge.import_external_alchemy_bundle ZIP")
    try:
        import_bundle(Path(sys.argv[1]))
        return 0
    except (ImportErrorSafe,zipfile.BadZipFile,ValueError,OSError,KeyError) as exc:
        print("CHAT_PNG_IMPORT_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":raise SystemExit(main())
