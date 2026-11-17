#!/usr/bin/env python3
"""Comparar situação antiga com bainha à frente da roupa, usando pixels SHA.

Não publica MP4 e não concede aprovação humana.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageChops

from videoforge.ep01_layer_stack import measure
from videoforge.layered_shot_plan import ROOT, REL


def main():
    original,old,fixed,report=measure()
    # Zoom na área de contato de bainha, roupa e mão inferior.
    crop=(380,815,900,1640)
    panels=[
      ("01 / IMAGEM-MÃE CORRETA",original.convert("RGB")),
      ("02 / ANTES: BAINHA SOB A ROUPA",old.convert("RGB")),
      ("03 / AGORA: BAINHA SOBRE A ROUPA",fixed.convert("RGB")),
      ("04 / ORIGINAL: CONTATO AMPLIADO",original.convert("RGB").crop(crop)),
      ("05 / ANTES: CONTATO AMPLIADO",old.convert("RGB").crop(crop)),
      ("06 / AGORA: CONTATO AMPLIADO",fixed.convert("RGB").crop(crop)),
    ]
    width,height=3*395+24,2*710+70
    sheet=Image.new("RGB",(width,height),"#eeeeee")
    pen=ImageDraw.Draw(sheet)
    pen.text((15,8),"C01-P02 / BAINHA NA FRENTE DA ROUPA, LUVA NA FRENTE DA BAINHA",fill="#222222")
    for i,(name,img) in enumerate(panels):
        x=12+(i%3)*395
        y=35+(i//3)*710
        pen.text((x,y),name,fill="#292929")
        view=ImageOps.contain(img,(365,650),Image.Resampling.LANCZOS)
        sheet.paste(view,(x+(365-view.width)//2,y+28))
    pen.text((15,sheet.height-25),
        f"RGB médio: antigo {report['old_mean_rgb_difference']}/255 | novo {report['corrected_mean_rgb_difference']}/255. Revisão pendente.",
        fill="#8d2020")
    out=ROOT/REL/"QA-C01-P02-BAINHA-FRENTE-ROUPA.jpg"
    sheet.save(out,"JPEG",quality=84,optimize=True)
    report["source_cropped_roi_for_visual_review"]=list(crop)
    report["jpg_sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
    report["comparison_type"]="corrected_depth_order_no_redraw_no_pose"
    report["visual_approval"]=False
    (ROOT/REL/"QA-C01-P02-BAINHA-FRENTE-ROUPA.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_SHEATH_IN_FRONT_OF_COAT_QA",json.dumps({
        "old_rgb_diff":report["old_mean_rgb_difference"],
        "new_rgb_diff":report["corrected_mean_rgb_difference"],
        "coat_overlap":report["sheath_coat_overlap_pixels_exact"],
        "approved":False,"paid_image_calls":0},ensure_ascii=False))


if __name__=="__main__":
    main()
