"""Archive images generated in GitHub Actions PERMANENTLY in their channel/video.

Copy only verified local PNG bytes and bounded source JSON. No AI calls.
Content remains attached to the source producer/run ID to avoid overwrites.
Approval of an archived file NEVER authorizes an official video render.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import zlib

from .errors import VideoForgeError
from .paths import CHANNEL_IDS, IDENTIFIER

ROOT=Path(__file__).resolve().parents[1]
PNG_MAGIC=b"\x89PNG\r\n\x1a\n"
PRODUCER=re.compile(r"^[a-z][a-z0-9-]{1,64}$")
MAX_PNG_BYTES=35_000_000
MAX_JSON_BYTES=512_000
MAX_FILES=64
MAX_TOTAL_BYTES=160_000_000
METADATA_NAMES=("production.json","meta.json","qa.json","manifest.json")
SENSITIVE=re.compile(r"(?:api[_-]?key|secret|access[_-]?token|refresh[_-]?token|password|authorization)",re.I)

def _digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def _png_info(content:bytes)->tuple[int,int]:
    if (not 64<=len(content)<=MAX_PNG_BYTES or
            content[:8]!=PNG_MAGIC or content[12:16]!=b"IHDR" or
            struct.unpack(">I",content[8:12])[0]!=13):
        raise VideoForgeError("IMAGE_ARCHIVE_PNG_INVALID")
    width,height=struct.unpack(">II",content[16:24])
    if (not 1<=width<=4096 or not 1<=height<=4096 or
            content[24] not in (8,16) or content[25] not in (0,2,4,6) or
            content[26:29]!=b"\x00\x00\x00" or
            (zlib.crc32(content[12:29])&0xffffffff)!=struct.unpack(">I",content[29:33])[0]):
        raise VideoForgeError("IMAGE_ARCHIVE_PNG_IHDR_INVALID")
    if content[-8:-4]!=b"IEND":
        raise VideoForgeError("IMAGE_ARCHIVE_PNG_IEND_INVALID")
    return width,height

def _metadata(obj:object)->None:
    if isinstance(obj,dict):
        for k,v in obj.items():
            if not isinstance(k,str) or SENSITIVE.search(k):
                raise VideoForgeError("IMAGE_ARCHIVE_SENSITIVE_METADATA_REFUSED")
            _metadata(v)
    elif isinstance(obj,list):
        for v in obj: _metadata(v)

def archive(channel:str,video_id:str,input_rel:str,run_id:int,
            producer:str,root:Path=ROOT)->dict:
    if (channel not in CHANNEL_IDS or
            not isinstance(video_id,str) or not IDENTIFIER.fullmatch(video_id) or
            not isinstance(run_id,int) or isinstance(run_id,bool) or run_id<1 or
            not isinstance(producer,str) or not PRODUCER.fullmatch(producer)):
        raise VideoForgeError("IMAGE_ARCHIVE_IDENTIFIERS_INVALID")
    if (not isinstance(input_rel,str) or
            "\\" in input_rel or Path(input_rel).is_absolute() or
            ".." in Path(input_rel).parts):
        raise VideoForgeError("IMAGE_ARCHIVE_SOURCE_PATH_UNSAFE")
    source_root=root/"output"/channel/"videos"/video_id
    src=root/input_rel
    if (src.is_symlink() or not src.is_dir()
            or source_root not in src.parents
            or not src.resolve().is_relative_to(source_root.resolve())):
        raise VideoForgeError("IMAGE_ARCHIVE_SOURCE_WRONG_CHANNEL_OR_VIDEO")
    dest=root/"canal"/channel/"videos"/video_id/"assets"/"geracoes"/producer/str(run_id)
    if dest.is_symlink() or any(p.is_symlink() for p in dest.parents):
        raise VideoForgeError("IMAGE_ARCHIVE_DESTINATION_SYMLINK")
    files=sorted(p for p in src.rglob("*") if p.is_file() or p.is_symlink())
    if len(files)>MAX_FILES:
        raise VideoForgeError("IMAGE_ARCHIVE_TOO_MANY_FILES")
    pngs=[]
    metadata=[]
    for f in files:
        if f.is_symlink() or not f.resolve().is_relative_to(src.resolve()):
            raise VideoForgeError("IMAGE_ARCHIVE_SOURCE_SYMLINK")
        rel=f.relative_to(src)
        if f.suffix.lower()==".png":
            data=f.read_bytes()
            width,height=_png_info(data)
            pngs.append((rel,data,{"width":width,"height":height,
                                    "sha256":_digest(data),"bytes":len(data)}))
        elif f.suffix.lower()==".json":
            if (f.stat().st_size>MAX_JSON_BYTES or not
                    (f.name.endswith(METADATA_NAMES) or f.name=="manifest.json")):
                raise VideoForgeError("IMAGE_ARCHIVE_UNSUPPORTED_METADATA")
            data=f.read_bytes()
            try:
                obj=json.loads(data.decode("utf-8"))
            except (ValueError,UnicodeError) as exc:
                raise VideoForgeError("IMAGE_ARCHIVE_METADATA_INVALID") from exc
            _metadata(obj)
            metadata.append((rel,data,obj))
        else:
            raise VideoForgeError("IMAGE_ARCHIVE_UNSUPPORTED_FILE_TYPE")
    if not pngs:
        raise VideoForgeError("IMAGE_ARCHIVE_NO_PNG_TO_PERSIST")
    if sum(len(t[1]) for t in pngs+metadata)>MAX_TOTAL_BYTES:
        raise VideoForgeError("IMAGE_ARCHIVE_TOO_LARGE")
    for rel,_,obj in metadata:
        if not rel.name.endswith(".production.json"):
            continue
        matched=[i for i in pngs if i[0].with_suffix(".png").stem==rel.name.removesuffix(".production.json")]
        if matched:
            expected=obj.get("sha256") or obj.get("output_sha256")
            if expected is not None and expected!=matched[0][2]["sha256"]:
                raise VideoForgeError("IMAGE_ARCHIVE_PRODUCTION_SHA_MISMATCH")
    report={
        "schema":"videoforge/permanent-generated-image-archive/v1",
        "channel":channel,"video_id":video_id,"producer":producer,
        "github_run_id":run_id,
        "source_output_dir":input_rel,
        "images":[{"file":p.as_posix(),**info,"human_visual_approval":False}
                  for p,_,info in pngs],
        "production_approved":False,
        "youtube_uploaded":False,
        "generated_in_this_archiver":False,
        "archived_image_count":len(pngs),
    }
    manifest=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    staged=[(p,data) for p,data,_ in pngs]
    staged.extend((p,data) for p,data,_ in metadata)
    staged.append((Path("manifesto-geracoes.json"),manifest.encode("utf8")))
    # Verify all would-be writes before touching any target.
    for rel,data in staged:
        target=dest/rel
        if any(p.is_symlink() for p in (target,*target.parents)):
            raise VideoForgeError("IMAGE_ARCHIVE_TARGET_SYMLINK")
        if target.exists() and target.read_bytes()!=data:
            raise VideoForgeError("IMAGE_ARCHIVE_WOULD_OVERWRITE_EXISTING")
    for rel,data in staged:
        target=dest/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        if _digest(target.read_bytes())!=_digest(data):
            raise VideoForgeError("IMAGE_ARCHIVE_POST_WRITE_SHA_MISMATCH")
    return report

def main()->int:
    parser=argparse.ArgumentParser(description="Copy existing GH Action PNGs to durable per-channel storage, no AI")
    parser.add_argument("--channel",required=True)
    parser.add_argument("--video-id",required=True)
    parser.add_argument("--input",required=True)
    parser.add_argument("--run-id",required=True,type=int)
    parser.add_argument("--producer",required=True)
    args=parser.parse_args()
    try:
        report=archive(args.channel,args.video_id,args.input,args.run_id,args.producer)
        print("PERMANENT_IMAGE_ARCHIVE_READY",json.dumps({
            "channel":report["channel"],"video_id":report["video_id"],
            "images":report["archived_image_count"],
            "producer":report["producer"],"run_id":report["github_run_id"],
        },ensure_ascii=False))
        return 0
    except (OSError,ValueError,VideoForgeError) as exc:
        print("PERMANENT_IMAGE_ARCHIVE_BLOCKED",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
