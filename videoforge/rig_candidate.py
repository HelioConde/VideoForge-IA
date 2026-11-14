"""VideoForge: preparar sprites CANDIDATOS para rig 2D a partir de pixels existentes.

Sem modelo de IA, sem "auto-approve" e sem alterar a cena-base. Os sprites
sao um RASCUNHO: regioes atras da capa/cabeca requerem pintura/inpainting
antes do render final. FFmpeg ja existe no container GHCR para decodificar PNG;
o encoder PNG e implementado com zlib da biblioteca padrao.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import zlib

from . import eye_refine, mesh_rig, proxy_images, scene_layers
from .errors import VideoForgeError
from .paths import _check_symlinks

PLAN_SCHEMA = "videoforge/rig-candidate-plan/v1"
QA_SCHEMA = "videoforge/rig-candidate-qa/v1"
REQUIRED = ("cena-base.png", "character-main.png", "cape.png",
            "background.png", "foreground-roof.png")


class CandidateError(ValueError):
    pass


def _load_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 120_000:
        raise CandidateError("RIG_JSON_MISSING_OR_UNSAFE")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError, OSError) as exc:
        raise CandidateError("RIG_JSON_INVALID") from exc
    if not isinstance(obj, dict):
        raise CandidateError("RIG_JSON_NOT_OBJECT")
    return obj


def _image(path: Path, width: int, height: int) -> bytearray:
    scene_layers.png_info(scene_layers._read_png(path))
    try:
        proc = subprocess.run([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-i", str(path), "-frames:v", "1", "-f", "rawvideo",
            "-pix_fmt", "rgba", "-",
        ], capture_output=True, timeout=40, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired) as exc:
        raise CandidateError("RIG_FFMPEG_PNG_DECODE_FAILED") from exc
    if len(proc.stdout) != width * height * 4:
        raise CandidateError("RIG_PNG_DECODE_DIMENSIONS_MISMATCH")
    return bytearray(proc.stdout)


def _write_png(path: Path, pixels: bytearray, width: int, height: int) -> None:
    if len(pixels) != width * height * 4:
        raise CandidateError("RIG_PNG_ENCODE_DIMENSIONS_MISMATCH")
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(
            ">I", zlib.crc32(name + data) & 0xffffffff)
    compressor = zlib.compressobj(6)
    row_size = width * 4
    compressed = bytearray()
    for y in range(height):
        start = y * row_size
        compressed.extend(compressor.compress(b"\0" + pixels[start:start + row_size]))
    compressed.extend(compressor.flush())
    blob = (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", bytes(compressed)) + chunk(b"IEND", b""))
    path.write_bytes(blob)


def _point(pair: object, width: int, height: int) -> tuple[int, int]:
    if (not isinstance(pair, list) or len(pair) != 2 or
            any(isinstance(v, bool) or not isinstance(v, int) for v in pair)):
        raise CandidateError("RIG_POLYGON_POINT_INVALID")
    x, y = pair
    if not (0 <= x < width and 0 <= y < height):
        raise CandidateError("RIG_POLYGON_POINT_OUTSIDE_CANVAS")
    return x, y


def _mask(polygons: object, width: int, height: int) -> bytearray:
    """Rasterizador scanline: cada poligono e um desenho proposto para revisao."""
    if not isinstance(polygons, list) or not 1 <= len(polygons) <= 8:
        raise CandidateError("RIG_POLYGON_LIST_INVALID")
    mask = bytearray(width * height)
    for p in polygons:
        if not isinstance(p, list) or not 3 <= len(p) <= 90:
            raise CandidateError("RIG_POLYGON_INVALID")
        points = [_point(x, width, height) for x in p]
        if len(set(points)) < 3:
            raise CandidateError("RIG_POLYGON_DEGENERATE")
        miny = max(0, min(pt[1] for pt in points))
        maxy = min(height - 1, max(pt[1] for pt in points))
        for y in range(miny, maxy + 1):
            scan = y + .5
            edges = []
            for a, b in zip(points, points[1:] + points[:1]):
                if (a[1] <= scan < b[1]) or (b[1] <= scan < a[1]):
                    edges.append(a[0] + (scan - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
            edges.sort()
            for x1, x2 in zip(edges[::2], edges[1::2]):
                left = max(0, math.ceil(x1 - .5))
                right = min(width, math.ceil(x2 - .5))
                if right > left:
                    mask[y * width + left:y * width + right] = b"\xff" * (right-left)
    if sum(1 for x in mask if x) < 12:
        raise CandidateError("RIG_POLYGON_EMPTY")
    return mask


def _cutout(src: bytearray, mask: bytearray) -> bytearray:
    out = bytearray(src)
    for i, value in enumerate(mask):
        p = i * 4
        out[p + 3] = out[p + 3] * value // 255
        if not out[p + 3]:
            out[p:p+4] = b"\0\0\0\0"
    return out


def _erase(src: bytearray, mask: bytearray) -> bytearray:
    out = bytearray(src)
    for i, value in enumerate(mask):
        p=4*i
        if value or not out[p+3]:
            out[p:p+4] = b"\0\0\0\0"
    return out


def _dilate_binary_mask(mask: bytearray, width: int, height: int,
                        radius: int) -> bytearray:
    """Dilata recorte por uma janela quadrada em O(width*height).

    Uma sobreposicao real de tecido evita que duas malhas animadas exponham
    buracos quando deixam de coincidir nas bordas do antigo recorte.
    """
    if len(mask) != width * height or not 0 <= radius <= 48:
        raise CandidateError("RIG_CAPE_OVERLAP_INVALID")
    if radius == 0:
        return bytearray(255 if value else 0 for value in mask)
    horizontal = bytearray(width * height)
    result = bytearray(width * height)
    for y in range(height):
        start = y * width
        active = sum(bool(mask[start + x]) for x in range(min(width, radius + 1)))
        for x in range(width):
            horizontal[start + x] = 255 if active else 0
            if x + radius + 1 < width:
                active += bool(mask[start + x + radius + 1])
            if x - radius >= 0:
                active -= bool(mask[start + x - radius])
    for x in range(width):
        active = sum(bool(horizontal[y * width + x])
                     for y in range(min(height, radius + 1)))
        for y in range(height):
            result[y * width + x] = 255 if active else 0
            if y + radius + 1 < height:
                active += bool(horizontal[(y + radius + 1) * width + x])
            if y - radius >= 0:
                active -= bool(horizontal[(y - radius) * width + x])
    return result


def _cape_split(src: bytearray, front_mask: bytearray,
                width: int | None = None, height: int | None = None,
                overlap_px: int = 0) -> tuple[bytearray, bytearray]:
    """Mantenha uma faixa DUPLA de tecido autentico ao longo da costura.

    A divisao complementar sem margem causa frestas quando a capa da frente
    e a de tras se movem com fases diferentes. Cada malha recebe uma
    margem do seu proprio tecido original, sem criar pixels novos.
    """
    if type(overlap_px) is not int or not 0 <= overlap_px <= 48:
        raise CandidateError("RIG_CAPE_OVERLAP_INVALID")
    if overlap_px:
        if not width or not height or len(src) != width * height * 4:
            raise CandidateError("RIG_CAPE_OVERLAP_DIMENSIONS")
        front_zone = _dilate_binary_mask(front_mask, width, height, overlap_px)
        inverse = bytearray(255 if not value else 0 for value in front_mask)
        back_zone = _dilate_binary_mask(inverse, width, height, overlap_px)
    else:
        front_zone = front_mask
        back_zone = bytearray(255 - value for value in front_mask)
    back, front = bytearray(src), bytearray(src)
    for i in range(len(front_mask)):
        idx = i * 4 + 3
        front[idx] = front[idx] * front_zone[i] // 255
        back[idx] = back[idx] * back_zone[i] // 255
        if not front[idx]:
            front[idx-3:idx+1] = b"\0\0\0\0"
        if not back[idx]:
            back[idx-3:idx+1] = b"\0\0\0\0"
    return back, front


def _make_seam_underlay(source: bytearray, polygons: object,
                        width: int, height: int, feather: int = 6
                        ) -> tuple[bytearray, int]:
    """Placa localizada do personagem ORIGINAL atras da gola/capa.

    Nao reconstrui anatomia invisivel: so impede que areas ja desenhadas
    fiquem transparentes quando a cabeca/capa se afastam alguns pixels.
    Nunca animar esta placa junto com a malha de tecido.
    """
    if type(feather) is not int or not 2 <= feather <= 12:
        raise CandidateError("RIG_SEAM_FEATHER_INVALID")
    mask = _mask([polygons], width, height)
    kept = 0
    out = bytearray(len(source))
    for i, value in enumerate(mask):
        if not value or source[4*i+3] == 0:
            continue
        y,x = divmod(i,width)
        # Alfa em degradê so perto do limite do poligono, sem nova arte.
        steps = feather
        for d in range(1, feather+1):
            if (x-d<0 or x+d>=width or y-d<0 or y+d>=height or
                not mask[i-d] or not mask[i+d] or
                not mask[i-d*width] or not mask[i+d*width]):
                steps = d-1
                break
        amount = min(255, round(255*(steps+.5)/feather))
        p=4*i
        out[p:p+3]=source[p:p+3]
        out[p+3]=round(source[p+3]*amount/255)
        kept+=1
    if kept < 100:
        raise CandidateError("RIG_SEAM_UNDERLAY_TOO_SMALL")
    return out,kept


def _eye_fill(head: bytearray, eye_masks: list[bytearray],
              samples: list[tuple[int, int]], width: int) -> None:
    """Cor proxima da pele, so para o draft; inpainting fino e posterior."""
    for mask, (x, y) in zip(eye_masks, samples):
        off = 4 * (y * width + x)
        color = head[off:off + 3]
        if head[off + 3] < 240:
            raise CandidateError("RIG_EYE_SKIN_SAMPLE_NOT_IN_HEAD")
        for i, flag in enumerate(mask):
            if flag:
                p = i * 4
                head[p:p + 3] = color


def _draw_dot(out: bytearray, x: int, y: int, radius: int,
              width: int, height: int, color: list[int]) -> None:
    for yy in range(max(0, y-radius), min(height, y+radius+1)):
        for xx in range(max(0, x-radius), min(width, x+radius+1)):
            if (xx-x)**2 + (yy-y)**2 <= radius*radius:
                p = 4 * (yy * width + xx)
                out[p:p+4] = bytes(color + [255])


def _eyelids(lines: object, width: int, height: int) -> bytearray:
    if not isinstance(lines, list) or not 1 <= len(lines) <= 4:
        raise CandidateError("RIG_EYELID_LINES_INVALID")
    out = bytearray(width * height * 4)
    for item in lines:
        if not isinstance(item, dict):
            raise CandidateError("RIG_EYELID_INVALID")
        points = item.get("points")
        if not isinstance(points, list) or not 2 <= len(points) <= 8:
            raise CandidateError("RIG_EYELID_POINTS_INVALID")
        coords = [_point(pt, width, height) for pt in points]
        color = item.get("color", [45, 27, 28])
        radius = item.get("radius", 2)
        if (not isinstance(color, list) or len(color) != 3 or
                any(type(n) is not int or not 0 <= n <= 255 for n in color) or
                type(radius) is not int or not 1 <= radius <= 3):
            raise CandidateError("RIG_EYELID_COLOR_OR_RADIUS_INVALID")
        for a, b in zip(coords, coords[1:]):
            steps = max(1, int(math.dist(a,b)*2))
            for n in range(steps+1):
                t = n/steps
                x = round(a[0] + t*(b[0]-a[0]))
                y = round(a[1] + t*(b[1]-a[1]))
                _draw_dot(out,x,y,radius,width,height,color)
    return out


def _composite(base: bytearray, top: bytearray) -> None:
    """Alfa-over em RGBA straight, composicao deterministica para QA."""
    for i in range(0,len(base),4):
        a=top[i+3]
        if not a:continue
        if a==255:
            base[i:i+4]=top[i:i+4]
            continue
        ba=base[i+3]
        den=a*255+ba*(255-a)
        if not den:continue
        for c in range(3):
            base[i+c]=(top[i+c]*a*255+base[i+c]*ba*(255-a)+den//2)//den
        base[i+3]=(den+127)//255


def _preview(src: bytearray, parts: list[bytearray], width: int,
             height: int, head: bytearray, eyes: bytearray,
             cape_front: bytearray, neck: list[int]) -> tuple[bytearray, dict]:
    joined=bytearray(width*height*4)
    for item in parts:
        _composite(joined,item)
    # Tiles reduzidos 1/2: original, recomposicao, mapa de diferenca, areas marcadas.
    w2,h2=width//2,height//2
    panel=bytearray(4*w2*h2*4) # total width 4*w2 height h2
    panel_w=4*w2
    err=0
    missing=0
    visible=0
    for y in range(h2):
        for x in range(w2):
            pi=((2*y)*width+2*x)*4
            orig_a=src[pi+3]
            orig_rgb=[(src[pi+c]*orig_a+85*(255-orig_a))//255 for c in range(3)]
            a=joined[pi+3]
            join_rgb=[(joined[pi+c]*a+85*(255-a))//255 for c in range(3)]
            delta=max(abs(orig_rgb[c]-join_rgb[c]) for c in range(3))
            if orig_a:
                visible+=1
                err+=sum((orig_rgb[c]-join_rgb[c])**2 for c in range(3))
                if a==0:missing+=1
            mark=[int(.50*orig_rgb[c]) for c in range(3)]
            if head[pi+3]:mark[2]=min(255,mark[2]+120)
            if eyes[pi+3]:mark[1]=min(255,mark[1]+150)
            if cape_front[pi+3]:mark[0]=min(255,mark[0]+130)
            if abs(2*x-neck[0])<4 or abs(2*y-neck[1])<4:
                if abs(2*x-neck[0])<22 and abs(2*y-neck[1])<22:
                    mark=[245,238,68]
            views=[orig_rgb,join_rgb,[min(255,delta*4),0,0],mark]
            for tile,color in enumerate(views):
                offset=(y*panel_w+tile*w2+x)*4
                panel[offset:offset+4]=bytes(color+[255])
    return panel, {"pixel_rmse_visible":round(math.sqrt(err/max(1,3*visible)),3),
                   "missing_alpha_sample_fraction":round(missing/max(1,visible),5),
                   "preview_downsample":2}


def prepare(source_dir: Path, plan_path: Path, output_dir: Path) -> dict:
    manifest=_load_json(source_dir/"manifest.json")
    plan=_load_json(plan_path)
    if manifest.get("schema") != scene_layers.SCHEMA or plan.get("schema") != PLAN_SCHEMA:
        raise CandidateError("RIG_SOURCE_OR_PLAN_SCHEMA_INVALID")
    channel, video_id, scene=(plan.get(k) for k in ("channel","video_id","scene"))
    if (channel,video_id,scene)!=(manifest.get("channel"),manifest.get("video_id"),manifest.get("scene")):
        raise CandidateError("RIG_CROSS_CHANNEL_OR_VIDEO")
    proxy_images.destination(channel,video_id,scene)
    source=manifest["source"]
    sha=source["sha256"]
    if plan.get("source_sha256") != sha:
        raise CandidateError("RIG_SOURCE_HASH_MISMATCH")
    width,height=source["width"],source["height"]
    if plan.get("canvas")!={"width":width,"height":height}:
        raise CandidateError("RIG_PLAN_CANVAS_MISMATCH")
    originals={}
    for name in REQUIRED:
        data=scene_layers._read_png(source_dir/name)
        record=(source if name=="cena-base.png" else
                manifest.get("layers",{}).get(name[:-4]))
        if not isinstance(record,dict) or hashlib.sha256(data).hexdigest()!=record.get("sha256"):
            raise CandidateError("RIG_INPUT_HASH_MISMATCH")
        if name!="cena-base.png" and record.get("technical_status")!="verified":
            raise CandidateError("RIG_INPUT_UNVERIFIED")
        info=scene_layers.png_info(data,require_alpha=(name not in ("background.png","cena-base.png")))
        if (info["width"],info["height"])!=(width,height):
            raise CandidateError("RIG_INPUT_DIMENSIONS_MISMATCH")
        originals[name]=_image(source_dir/name,width,height)
    output_dir = (output_dir if output_dir.is_absolute() else proxy_images.ROOT / output_dir)
    target = (proxy_images.ROOT / "output" / channel / "videos" / video_id
              / "rig-candidates" / scene)
    if output_dir != target or ".." in output_dir.parts:
        raise CandidateError("RIG_CANDIDATE_OUTPUT_CROSS_CHANNEL")
    if output_dir.exists() or output_dir.is_symlink():
        raise CandidateError("RIG_CANDIDATE_OUTPUT_ALREADY_EXISTS")
    _check_symlinks(output_dir, stop_at=proxy_images.ROOT)
    # Head rig must retain ALL original hair strands, not just face geometry.
    # Legacy plans still use head_polygon; fuller per-channel art has its own contour.
    full_head=plan.get("head_full_polygon",plan["head_polygon"])
    headmask=_mask([full_head],width,height)
    eye_shapes=plan["eye_polygons"]
    if not isinstance(eye_shapes,list) or not 1<=len(eye_shapes)<=2:
        raise CandidateError("RIG_EYES_ONE_OR_TWO_REQUIRED")
    eyes=[_mask([pts],width,height) for pts in eye_shapes]
    skin_points=plan["skin_samples"]
    if not isinstance(skin_points,list) or len(skin_points)!=len(eyes):
        raise CandidateError("RIG_SKIN_SAMPLE_COUNT_MISMATCH")
    skins=[_point(pt,width,height) for pt in skin_points]
    eye_union=bytearray(max(items) for items in zip(*eyes))
    if any(eye_union[i] and not headmask[i] for i in range(width*height)):
        raise CandidateError("RIG_EYE_NOT_INSIDE_HEAD")
    frontmask=_mask([plan["cape_front_polygon"]],width,height)
    char=originals["character-main.png"]
    hair_coverage=None
    if "head_full_polygon" in plan:
        bbox=plan.get("hair_guard_bbox")
        if not isinstance(bbox,list) or len(bbox)!=4 or any(
            type(v) is not int for v in bbox
        ):
            raise CandidateError("RIG_HAIR_GUARD_MISSING")
        x0,y0,x1,y1=bbox
        if not (0<=x0<x1<=width and 0<=y0<y1<=height
                and x1-x0>=10 and y1-y0>=10):
            raise CandidateError("RIG_HAIR_GUARD_BOUNDS")
        total=0
        lost=0
        for y in range(y0,y1):
            for x in range(x0,x1):
                i=y*width+x
                alpha=char[4*i+3]
                total+=alpha
                if not headmask[i]:
                    lost+=alpha
        if total<2550:
            raise CandidateError("RIG_HAIR_GUARD_EMPTY")
        hair_coverage=round(1-lost/total,7)
        if lost/total>0.0002:
            raise CandidateError("RIG_HAIR_CLIPPED_BY_HEAD_MASK")
    cape=originals["cape.png"]
    back,front=_cape_split(
        cape,frontmask,width,height,overlap_px=plan.get("cape_seam_overlap_px",0),
    )
    head=_cutout(char,headmask)
    head_open=bytearray(head)  # estado original INTACTO, antes de qualquer inpainting
    eye_open=_cutout(char,eye_union)
    if "eyelid_beziers" in plan:
        eye_closed, eye_report=eye_refine.create_natural_blink(
            head,char,eyes,skins,plan["eyelid_beziers"],width,height)
    else:
        _eye_fill(head,eyes,skins,width)
        eye_closed=_eyelids(plan["eyelid_lines"],width,height)
        eye_report={"technique":"legacy-blocky-line-art",
                    "human_review":"pending","eyes":len(eyes),"external_model_calls":0}
    cape_alpha=bytearray(255 if cape[4*i+3]>=16 else 0 for i in range(width*height))
    erased=bytearray(max(headmask[i],cape_alpha[i]) for i in range(width*height))
    body=_erase(char,erased)
    seam_underlay=None
    seam_pixels=0
    if "seam_underlay_polygon" in plan:
        seam_underlay,seam_pixels=_make_seam_underlay(
            char,plan["seam_underlay_polygon"],width,height,
            feather=plan.get("seam_underlay_feather",6),
        )
    to_save={
        "body-no-head-no-cape.png":body,
        "head-no-eyes.png":head,
        "head-open.png":head_open,
        "eyes-open.png":eye_open,
        "eyes-closed.png":eye_closed,
        "cape.png":back,
        "cape-front.png":front,
    }
    if seam_underlay is not None:
        to_save["seam-underlay.png"]=seam_underlay
    output_dir.mkdir(parents=True)
    # Arquivos de mascara para revisar o recorte antes de qualquer rig final.
    masks = {
        "head-mask.png": headmask,
        "eyes-mask.png": eye_union,
        "cape-front-mask.png": frontmask,
    }
    for filename, mask in masks.items():
        rgba=bytearray(width*height*4)
        for i, v in enumerate(mask):
            rgba[4*i:4*i+4]=bytes((v,v,v,255))
        _write_png(output_dir/filename,rgba,width,height)
    hashes={}
    for name,data in to_save.items():
        target=output_dir/name
        _write_png(target,data,width,height)
        hashes[name]=hashlib.sha256(target.read_bytes()).hexdigest()
    pivot=plan["neck_pivot"]
    if not isinstance(pivot,list):
        raise CandidateError("RIG_NECK_PIVOT_INVALID")
    _point(pivot,width,height)
    mesh=plan["cape_mesh"]
    blinks=plan["blink_frames"]
    angle=plan.get("head_max_deg",1.5)
    rig={
        "schema":mesh_rig.SCHEMA, "channel":channel, "video_id":video_id,
        "scene":scene, "source_sha256":sha,
        "canvas":{"width":width,"height":height},"assets":hashes,
        "neck_pivot":{"x":pivot[0],"y":pivot[1]},
        "head_max_deg":angle,"blink_frames":blinks,"cape_mesh":mesh,
        "human_review":{"no_duplicate_parts":False,
                        "pixel_alignment":False,"occlusion_order":False},
        "candidate_only":True,
    }
    (output_dir/"rig.json").write_text(
        json.dumps(rig,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    preview,metrics=_preview(char,[back,body,front,head,eye_open],
                           width,height,head,eye_open,front,pivot)
    _write_png(output_dir/"contact-sheet.png",preview,4*(width//2),height//2)
    source_alpha=sum(1 for i in range(width*height) if char[4*i+3]>0)
    erased_alpha=sum(1 for i in range(width*height)
                     if erased[i] and char[4*i+3]>0)
    report={
        "schema":QA_SCHEMA,"status":"draft_unapproved",
        "channel":channel,"video_id":video_id,"scene":scene,
        "source_sha256":sha,"source_artifact_manifest_verified":True,
        "asset_sha256":hashes,"metrics":metrics,
        "body_pixels_erased_without_inpainting":erased_alpha,
        "body_erased_fraction_of_character":round(erased_alpha/max(1,source_alpha),4),
        "needs_manual_reconstruction":True,
        "eyes_extracted_from_original":len(eyes),
        "head_open_original_pixels_preserved":True,
        "seam_underlay_original_pixels":seam_pixels,
        "seam_underlay_source":"character-main.png" if seam_pixels else None,
        "head_full_hair_guard_alpha_coverage":hair_coverage,
        "head_mask_variant":"head_full_polygon" if "head_full_polygon" in plan else "head_polygon_legacy",
        "natural_eyelids_preview":eye_report,
        "cape_front_back_split":True,\n        "cape_seam_overlap_px":plan.get("cape_seam_overlap_px",0),\n        "human_visual_approval":False,
        "rig_ready_for_remotion":False,"youtube_uploaded":False,
        "notes":[
            "Cabeca/olhos/capa extraidos de pixels existentes; recorte de cabelo integral verificado quando head_full_polygon existe",
            "Olhos fechados usam curvas antialias e pele emprestada da bochecha original; QA artistico ainda requerido",
            "Corpo atras de capa/cabeca nao reconstruido; a regiao apagada exige inpainting",
            "Placa localizada da gola copia APENAS pixels originais, sob a capa e o torso, sem inventar anatomia",
            "O artefato NAO pode receber nome de rig aprovado nem ser usado para publicar",
        ],
    }
    provenance={
        "schema":"videoforge/rig-asset-provenance/v1",
        "source_channel":channel,"source_video_id":video_id,"source_scene":scene,
        "source_scene_sha256":sha,
        "source_layers_sha256":{name:hashlib.sha256((source_dir/name).read_bytes()).hexdigest()
                                for name in REQUIRED},
        "plan_sha256":hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        "technique":"polygon masks + original pixels; natural eyelids/cheek-transfer; no model-driven inpainting",
        "model_calls":0,"human_review":False,
        "reconstruction_of_occluded_anatomy":"not_performed",
        "commercial_rights":"not_assessed",
    }
    (output_dir/"asset-provenance.json").write_text(
        json.dumps(provenance,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (output_dir/"candidate.qa.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description="Criar apenas candidatos RGBA para rig; sem IA")
    parser.add_argument("--source-dir",type=Path,required=True)
    parser.add_argument("--plan",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    try:
        report=prepare(args.source_dir,args.plan,args.output_dir)
    except (CandidateError,eye_refine.EyeRefineError,mesh_rig.RigAssetError,
            VideoForgeError,scene_layers.LayerError,proxy_images.ProxyImageError) as exc:
        print("RIG_CANDIDATE_BLOCKED:",exc,file=sys.stderr)
        return 2
    print(json.dumps(report,ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
