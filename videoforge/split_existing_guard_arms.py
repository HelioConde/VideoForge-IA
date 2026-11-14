"""Separa braços dos guardas usando exclusivamente pixels RGBA já arquivados.

Não invoca IA. Particiona pixels existentes em body, upper-arm,
forearm e gripping-hand, preservando todas as cores/alpha da fonte
e verificando roundtrip EXATO de pixels visíveis. Não reconstrói
regiões ocultas nem libera movimento de rig.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
EPISODE = ROOT / "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
OUTPUT = EPISODE / "assets/cena-01/rig-drafts/guard-arm-parts"
SOURCE_MANIFEST = EPISODE / "rig-selecao-artes-c01.json"
EXPECTED_SIZE = (1024, 1536)

# Coordenadas na mesma arte-mãe. Não são rigs já aprovados.
PLAN = {
    "guarda-esquerdo": {
        "parts": [
            ("upper-arm", [(249,551),(294,586),(321,637),(322,678),
                           (288,700),(255,679),(230,633),(216,584)],
             [254,572]),
            ("forearm", [(290,641),(328,659),(373,707),(383,731),
                         (357,753),(317,720),(289,708)],
             [303,670]),
            ("gripping-hand", [(351,719),(379,715),(416,736),
                               (416,766),(379,789),(353,762)],
             [360,730]),
        ],
        "spear": "lanca-guarda-esquerdo-CANDIDATE",
        "contactPoint": [381,751],
        "shoulder": [254,572],
        "elbow": [303,670],
        "wrist": [360,730],
    },
    "guarda-direito": {
        "parts": [
            ("upper-arm", [(775,553),(736,588),(710,645),(705,675),
                           (741,701),(773,671),(795,628),(810,582)],
             [773,573]),
            ("forearm", [(710,647),(739,669),(720,712),(671,744),
                         (647,757),(635,729),(671,690)],
             [722,670]),
            ("gripping-hand", [(671,715),(642,716),(609,733),
                               (605,766),(638,789),(674,762)],
             [666,732]),
        ],
        "spear": "lanca-guarda-direito-CANDIDATE",
        "contactPoint": [644,749],
        "shoulder": [773,573],
        "elbow": [722,670],
        "wrist": [666,732],
    },
}

class GuardArmError(ValueError):
    pass

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_source(path: Path, expected: str) -> Image.Image:
    if path.is_symlink() or not path.is_file():
        raise GuardArmError("SOURCE_MISSING: " + str(path))
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise GuardArmError("SOURCE_SHA_MISMATCH: " + str(path))
    im = Image.open(path)
    if im.mode != "RGBA" or im.size != EXPECTED_SIZE:
        raise GuardArmError("SOURCE_MUST_BE_RGBA_1024x1536")
    im.load()
    return im

def binary_mask(points: list, canvas: tuple[int,int]) -> Image.Image:
    mask = Image.new("L", canvas, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask

def split_one(name: str, source: Image.Image, spear: Image.Image,
              output: Path, plan: dict) -> dict:
    alpha = source.getchannel("A")
    spear_alpha = spear.getchannel("A")
    accumulated = Image.new("L", EXPECTED_SIZE, 0)
    split = []
    records = []
    for part_name, points, pivot in plan["parts"]:
        polygon = binary_mask(points, EXPECTED_SIZE)
        # Impede que uma luva/antebraço apareça em duas camadas.
        exclusive = ImageChops.subtract(polygon, accumulated)
        accumulated = ImageChops.lighter(accumulated, exclusive)
        sub_alpha = ImageChops.multiply(alpha, exclusive)
        if not sub_alpha.getbbox():
            raise GuardArmError("EMPTY_PART: "+name+"/"+part_name)
        img = source.copy()
        img.putalpha(sub_alpha)
        pixels = sum(sub_alpha.histogram()[1:])
        if pixels < 500:
            raise GuardArmError("PART_AREA_TOO_SMALL: "+name+"/"+part_name)
        overlap = ImageChops.multiply(
            sub_alpha.point(lambda x:255 if x>=128 else 0),
            spear_alpha.point(lambda x:255 if x>=128 else 0),
        )
        total_overlap = sum(overlap.histogram()[1:])
        filename = name + "-" + part_name + "-DRAFT.png"
        img.save(output/filename,optimize=True)
        records.append({
            "id":part_name,
            "path":filename,
            "sha256":digest((output/filename).read_bytes()),
            "bboxXYXY":list(sub_alpha.getbbox()),
            "sourceOpaquePixels":sum(sub_alpha.histogram()[128:]),
            "alphaOverlapWithSpearPixels":total_overlap,
            "pivotProvisionalXY":pivot,
            "underlayAvailable":False,
            "poseMotionEnabled":False,
            "reviewStatus":"DRAFT_UNDERLAY_REQUIRED",
        })
        split.append((exclusive,img))
    body_mask = ImageChops.invert(accumulated)
    body = source.copy()
    body.putalpha(ImageChops.multiply(alpha, body_mask))
    filename = name+"-body-remainder-DRAFT.png"
    body.save(output/filename,optimize=True)
    records.insert(0,{
        "id":"body-remainder",
        "path":filename,
        "sha256":digest((output/filename).read_bytes()),
        "bboxXYXY":list(body.getchannel("A").getbbox()),
        "sourceOpaquePixels":sum(body.getchannel("A").histogram()[128:]),
        "alphaOverlapWithSpearPixels":None,
        "pivotProvisionalXY":None,
        "underlayAvailable":False,
        "poseMotionEnabled":False,
        "reviewStatus":"DRAFT_ARMS_MASKED_OUT",
    })
    # Comprova pixel por pixel que nenhuma cor/alpha visível foi inventada
    # ou perdida; reconstituir NÃO equivale a anatomia oculta preenchida.
    recomposed=body
    for mask,img in split:
        recomposed=Image.composite(img,recomposed,mask)
    visible_error=ImageChops.difference(source,recomposed)
    if visible_error.getbbox() is not None:
        raise GuardArmError("GUARD_VISIBLE_PIXEL_ROUNDTRIP_FAILED:"+name)
    if sum(x["sourceOpaquePixels"] for x in records) < 100_000:
        raise GuardArmError("GUARD_VISIBLE_AREA_TOO_SMALL")
    return {
        "id":name,
        "source":name+"-origem-rgb-candidato.png",
        "sourceOpaquePixelCount":sum(alpha.histogram()[128:]),
        "roundtripExact":True,
        "sourcePixelColorsModified":False,
        "armament":plan["spear"],
        "contactPointSourceXY":plan["contactPoint"],
        "jointCandidateSourceXY":{key:plan[key] for key in ("shoulder","elbow","wrist")},
        "jointsMeasuredAndApproved":False,
        "underlaysReconstructed":False,
        "handAlreadyOverlappedBySpearInSource":True,
        "parts":records,
    }

def run(root: Path=EPISODE, output: Path=OUTPUT) -> dict:
    if output.exists() or output.is_symlink():
        raise GuardArmError("OUTPUT_EXISTS_NO_OVERWRITE")
    if not (root/"SEM-GERACAO-NOVAS-IMAGENS.lock").is_file():
        raise GuardArmError("USER_NO_IMAGE_GENERATION_LOCK_MISSING")
    inventory=json.loads((root/"rig-selecao-artes-c01.json").read_text(encoding="utf-8"))
    if inventory.get("schema")!="videoforge/alchemy-episode-scene1-preferred-assets/v1":
        raise GuardArmError("SOURCE_INVENTORY_INVALID")
    prefs=inventory["preferredAssets"]
    guards={g["id"]:g for g in prefs["guards"]}
    spears={s["id"]:s for s in prefs["spears"]}
    if set(guards)!=set(PLAN):
        raise GuardArmError("GUARD_CAST_MISMATCH")
    # Valida todas as fontes antes de escrever.
    inputs=[]
    for name,definition in PLAN.items():
        guard=guards[name]
        spear=spears[definition["spear"]]
        inputs.append((name,
           read_source(root/guard["path"],guard["sha256"]),
           read_source(root/spear["path"],spear["sha256"]),
           definition))
    output.mkdir(parents=True)
    result=[split_one(name,g,s,output,defn) for name,g,s,defn in inputs]
    report={
       "schema":"videoforge/existing-guard-arm-partition-qa/v1",
       "channel":"alchemy-lab",
       "video_id":"mmorpg-conquiste-a-princesa-ep01",
       "scene":"C01","canvas":[1024,1536],
       "method":"exclusive binary polygon partition of existing RGBA",
       "sourceRigInventory":"rig-selecao-artes-c01.json",
       "guardCount":2,
       "candidatePartPNGCount":sum(len(x["parts"]) for x in result),
       "pixelsLostOrDrawn":0,
       "newImageGenerationCalls":0,
       "roundtripExact":all(x["roundtripExact"] for x in result),
       "humanVisualApproval":False,
       "realJointMotionReady":False,
       "officialRemotionRenderReady":False,
       "youtubeUploaded":False,
       "knownBlockers":[
           "Part joint cuts can have seams if any rotation is applied",
           "Hands were drawn overlapping spear shafts; missing glove pixels cannot be reconstructed by pixel extraction",
           "No background/arm anatomy is available behind moved shoulders",
           "Pivots are provisional scene-image coordinates, not measured with a rig review",
           "Do not animate the whole PNG as replacement for articulations",
       ],
       "guards":result,
    }
    (output/"qa.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("GUARD_ARM_PARTS_DRAFT_OK",report["candidatePartPNGCount"],
          "parts; roundtrip",report["roundtripExact"],
          "generative calls",report["newImageGenerationCalls"])
    return report

def main() -> int:
    try:
        run()
        return 0
    except (GuardArmError,KeyError,TypeError,OSError,ValueError) as e:
        print("GUARD_ARM_SPLIT_BLOCKED",str(e),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
