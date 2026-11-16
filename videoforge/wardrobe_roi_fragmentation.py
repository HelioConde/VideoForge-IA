"""Auditoria de fragmentacao das 8 mascaras RGBA V3 ja arquivadas.

Componentes conectados por 8 vizinhos; informa ilhas e bordas, sem retirar
pixels. Fragmentacao nao prova erro semantico e nunca promove figurinos.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from .errors import VideoForgeError
from .remake_autopilot import ROOT, EPISODE
from .wardrobe_roi_archive import audit as audit_archive

INPUT="QA-ROI-EXCLUSOES-V3.json"
OUTPUT="QA-ROI-FRAGMENTACAO-V3.json"
LIMIT=4_000_000


def component_stats(mask):
    """Retorna componentes 8-conectados em pixels alfa >0 (sem resize)."""
    if mask.mode!="L" or mask.width*mask.height>LIMIT:
        raise VideoForgeError("ROI_COMPONENT_MASK_INVALID")
    w,h=mask.size
    data=mask.tobytes()
    seen=bytearray(w*h)
    areas=[]
    bounds=[]
    selected=0
    for pos,pixel in enumerate(data):
        if not pixel:
            continue
        selected+=1
        if seen[pos]:
            continue
        todo=[pos]
        seen[pos]=1
        size=0
        minx=w;maxx=0;miny=h;maxy=0
        while todo:
            q=todo.pop()
            x=q%w;y=q//w
            size+=1
            if x<minx:minx=x
            if x>maxx:maxx=x
            if y<miny:miny=y
            if y>maxy:maxy=y
            for yy in range(max(0,y-1),min(h,y+2)):
                for xx in range(max(0,x-1),min(w,x+2)):
                    index=yy*w+xx
                    if not seen[index] and data[index]:
                        seen[index]=1
                        todo.append(index)
        areas.append(size)
        bounds.append((minx,miny,maxx+1,maxy+1))
    ordering=sorted(range(len(areas)),key=lambda k:areas[k],reverse=True)
    largest=areas[ordering[0]] if ordering else 0
    return {
        "selected_pixels":selected,
        "connected_components":len(areas),
        "largest_component_pixels":largest,
        "largest_component_share_percent":round(largest*100/selected,2) if selected else 0,
        "single_pixel_islands":sum(n==1 for n in areas),
        "small_components_under_5px":sum(n<5 for n in areas),
        "small_components_under_20px":sum(n<20 for n in areas),
        "components_touching_crop_edge":sum(
            x0==0 or y0==0 or x1==w or y1==h for x0,y0,x1,y1 in bounds),
        "top_5_component_boxes_xyxy":[list(bounds[k]) for k in ordering[:5]],
        "top_5_component_pixels":[areas[k] for k in ordering[:5]],
    }


def run(root:Path=ROOT,sync=False):
    from PIL import Image
    ep=Path(root)/EPISODE
    verified=audit_archive(root)
    r=ep/INPUT
    if r.is_symlink() or not r.is_file():
        raise VideoForgeError("ROI_COMPONENT_SOURCE_MISSING")
    manifest=json.loads(r.read_text(encoding="utf-8"))
    rows=[]
    for original,audited in zip(manifest["results"],verified["rows"]):
        if any(original[k]!=audited[k] for k in ("actor","region","side")):
            raise VideoForgeError("ROI_COMPONENT_INPUT_MISMATCH")
        rel=original["cleaned_candidate_path"]
        target=ep/rel
        if (".." in Path(rel).parts or not rel.startswith("assets/qa-roi-exclusions-v3/")
                or target.is_symlink() or not target.is_file()):
            raise VideoForgeError("ROI_COMPONENT_UNSAFE_FILE")
        raw=target.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=audited["sha256"]:
            raise VideoForgeError("ROI_COMPONENT_SHA_MISMATCH")
        with Image.open(target) as im:
            if im.format!="PNG" or im.mode!="RGBA":
                raise VideoForgeError("ROI_COMPONENT_FORMAT_INVALID")
            alpha=im.getchannel("A")
            if alpha.width*alpha.height>LIMIT:
                raise VideoForgeError("ROI_COMPONENT_MASK_TOO_LARGE")
            stats=component_stats(alpha)
        if stats["selected_pixels"]!=original["candidate_exclusion"]["after"]:
            raise VideoForgeError("ROI_COMPONENT_COUNT_MISMATCH")
        # Diagnostic only. No "pass" on anatomy from components alone.
        rows.append({
            "actor":original["actor"],"region":original["region"],
            "side":original["side"],"source_sha256":audited["source_sha256"],
            "archived_mask_sha256":audited["sha256"],"pixel_fragmentation":stats,
            "review_priority":("HIGH_FRAGMENTATION_CANDIDATE"
                if stats["connected_components"]>=15 and
                    stats["largest_component_share_percent"]<80
                else "VISUAL_INSPECTION_REQUIRED"),
            "semantic_verification":False,"official_art_usable":False,
        })
    output={
        "schema":"videoforge/wardrobe-v3-fragmentation/v1",
        "status":"PIXEL_TOPOLOGY_ONLY_NOT_SEMANTIC_CERTIFICATION",
        "masks_analyzed":8,"rows":rows,
        "no_pixels_modified":True,
        "semantic_masks_approved":0,"canonical_pairs_ready":0,
        "owner_rejections_preserved":True,"r2_blocked":True,
        "provider_calls":0,"official_mp4":False,"youtube_uploaded":False,
    }
    if sync:
        out=ep/OUTPUT
        if out.is_symlink():raise VideoForgeError("ROI_COMPONENT_UNSAFE_OUTPUT")
        content=json.dumps(output,ensure_ascii=False,indent=2)+"\n"
        if not out.exists() or out.read_text(encoding="utf-8")!=content:
            out.write_text(content,encoding="utf-8")
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sync",action="store_true")
    args=p.parse_args()
    o=run(sync=args.sync)
    print("ROI_FRAGMENTATION",json.dumps({
        "masks":o["masks_analyzed"],
        "suspected_fragmentation":sum(r["review_priority"]=="HIGH_FRAGMENTATION_CANDIDATE" for r in o["rows"]),
        "semantic_approved":0,"r2_blocked":True,
    }))


if __name__=="__main__":
    main()
