"""Kael alinhado pixel-a-pixel à cena-mãe, sem gerar arte nova.

Usa alfa do antigo recorte conjunto somente como guia geométrico;
todos os canais RGB vêm da cena-mãe original. Compara com o candidato
desalinhado anterior e impede aprovação tácita de rig.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image

from .refine_existing_guards import BASE, MOTHER_SHA, GROUP_SHA, MaskError, verified_image, isolate_guard

OLD_KAEL_SHA = "f910f2df550062267efb17cde99a950c1afa47e1216179372fd963a26b864f41"
OUT_REL = "assets/cena-01/rig-drafts/kael-alinhado-original"

def run(root: Path=BASE) -> dict:
    output=root/OUT_REL
    if output.exists() or output.is_symlink():
        raise MaskError("KAEL_ALIGNED_ALREADY_EXISTS_NO_OVERWRITE")
    mother=verified_image(root/"assets/cenas-mae/cena-01.png",MOTHER_SHA,"RGB")
    guide=verified_image(root/"assets/cena-01/candidatos/character-group-REJECTED.png",GROUP_SHA,"RGBA")
    previous=verified_image(root/"assets/cena-01/candidatos/kael-rgba-candidate.png",OLD_KAEL_SHA,"RGBA")
    source=np.asarray(mother)
    seg=np.asarray(guide.getchannel("A"))
    definition={"id":"kael","rect":(292,738,669,1410),"seed":(500,1050)}
    candidate,alpha,metrics=isolate_guard(source,seg,definition)
    old_alpha=np.asarray(previous.getchannel("A"))>=190
    aligned=alpha>=190
    intersection=int(np.count_nonzero(aligned & old_alpha))
    union=int(np.count_nonzero(aligned | old_alpha))
    iou=(intersection/union) if union else 0
    if not (110_000 <= metrics["componentPixelCount"] <= 160_000):
        raise MaskError("KAEL_ALPHA_COMPONENT_BAD_AREA")
    if not 0 < iou < 0.5:
        raise MaskError("OLD_ALIGNMENT_ASSUMPTION_CHANGED")
    output.mkdir(parents=True)
    file=output/"kael-alinhado-mesma-cena-mae-CANDIDATO.png"
    Image.fromarray(candidate,"RGBA").save(file,optimize=True)
    sha256=hashlib.sha256(file.read_bytes()).hexdigest()
    report={"schema":"videoforge/kael-source-alignment-qa/v1",
            "channel":"alchemy-lab",
            "video_id":"mmorpg-conquiste-a-princesa-ep01",
            "scene":"cena-01",
            "sourceMotherSHA256":MOTHER_SHA,
            "maskOnlyFromPreviousGroupSHA256":GROUP_SHA,
            "previousCandidateSHA256":OLD_KAEL_SHA,
            "output":file.name,"outputSHA256":sha256,
            "sourceRGBCopiedWithoutModification":True,
            "imageGenerationCalls":0,
            "alignment":{"oldCandidateIouVsOriginalMother":round(iou,5),
                         "maskPixelOverlap":intersection,
                         "oldCandidateNotAligned":True,
                         "sourceBbox":metrics["bbox"],
                         "pixelCount":metrics["componentPixelCount"]},
            "status":"candidate_aligned_needs_visual_QA",
            "humanReview":False,"facialRig":False,
            "hairMesh":False,"underlayReconstructed":False,
            "partSplittingComplete":False,"officialVideo":False,
            "youtubeUploaded":False,
            "notes":[
              "O Kael RGBA anterior está em escala distinta da mãe; não usar suas coordenadas para rig",
              "Nova cor e silhueta derivadas exclusivamente dos pixels da cena original",
              "Áreas antes escondidas ainda não existem: mãos, cabelo e ombros não podem girar sem underlays",
              "O antigo groupRGBA contém trono e fundo, foi usado SOMENTE para obter máscara do Kael"
            ]}
    (output/"qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("KAEL_MOTHER_ALIGNED",json.dumps({"bbox":metrics["bbox"],"iouOld":iou,"sha":sha256}))
    return report

def main()->int:
    try:
        run()
        return 0
    except (MaskError, ValueError,OSError,cv2.error) as err:
        print("KAEL_MOTHER_ALIGNMENT_BLOCKED",str(err),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
