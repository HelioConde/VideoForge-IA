"""Analyze per-actor alpha bbox and compare to PROVISIONAL screen-space regions.

This script does not approve any part; target ROIs are approximate editorial
hypotheses inferred from the visually approved C01-P04 V3 framing.
"""
from __future__ import annotations
from hashlib import sha256
import json
from PIL import Image,ImageDraw,ImageFont
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO
from scripts.qa_ep01_c01p04_v3_layers_board import verified_art
from videoforge.ep01_approved_v3_parts import aligned_source

BASENAME="QA-C01-P04-V3-ESCALA-PERSONAGENS"
EXPECTED={
 "character-aldric": {"roi":[380,155,705,530],"max_bbox_height":500,"max_bbox_width":360},
 "character-guarda_esquerdo":{"roi":[0,500,345,1360],"max_bbox_height":970,"max_bbox_width":410},
 "character-guarda_direito":{"roi":[605,500,941,1360],"max_bbox_height":970,"max_bbox_width":410},
 "character-kael":{"roi":[65,805,630,1520],"max_bbox_height":840,"max_bbox_width":650},
}
def font(n):
    try:return ImageFont.truetype("DejaVuSans.ttf",n)
    except OSError:return ImageFont.load_default()

def main():
    root=ROOT/REL
    expected_sha="b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d"
    ref=aligned_source()
    if ref["sha256"]!=expected_sha:
        raise ValueError("QA_SCALE_SOURCE_CHANGED")
    from io import BytesIO
    with Image.open(BytesIO(ref["blob"])) as im:
        mother=im.convert("RGB")
    board=Image.new("RGB",(941*2+80,1672+160),"#ededeb")
    board.paste(mother,(20,115));board.paste(mother,(961,115))
    pen=ImageDraw.Draw(board)
    pen.text((20,12),"C01-P04 V3 | ESCALA ALFA DAS PARTES INDEPENDENTES",font=font(24),fill="#1e1e1e")
    pen.text((20,49),"ESQUERDA: ROIs editoriais aproximadas / DIREITA: bboxes alfas nativos (so visual).",font=font(17),fill="#b03222")
    pen.text((20,75),"NENHUM ROI mede aprovacao de pose, contato, escala exata ou rig.",font=font(15),fill="#912c28")
    rows=[]
    colors=["#12b5ca","#faad1b","#d4459a","#53ac55"]
    for i,(part,policy) in enumerate(EXPECTED.items()):
        img,meta=verified_art(part)
        threshold=img.getchannel("A").point(lambda v:255 if v>=16 else 0)
        bbox=threshold.getbbox()
        if bbox is None:raise ValueError("QA_SCALE_EMPTY_ALPHA "+part)
        width=bbox[2]-bbox[0];height=bbox[3]-bbox[1]
        sw,sh=img.size
        color=colors[i]
        roi=policy["roi"]
        pen.rectangle((roi[0]+20,roi[1]+115,roi[2]+20,roi[3]+115),outline=color,width=5)
        # Native bbox on right pane: do not pretend it matches 941x1672.
        native_clip=[bbox[0]+961,bbox[1]+115,bbox[2]+961,bbox[3]+115]
        pen.rectangle(tuple(native_clip),outline=color,width=4)
        failed=(width>policy["max_bbox_width"] or height>policy["max_bbox_height"])
        rows.append({
            "part":part,"source_sha256":meta["sha256"],
            "native_dimensions":[sw,sh],
            "alpha_bbox_native":list(bbox),
            "alpha_bbox_width":width,"alpha_bbox_height":height,
            "editorial_roi_approx_xyxy":roi,
            "max_bbox_width_for_preflight":policy["max_bbox_width"],
            "max_bbox_height_for_preflight":policy["max_bbox_height"],
            "scale_outlier_warning":failed,
            "reference_roi_is_approximation_not_approved_placement":True,
            "human_visual_approval":False,
        })
        pen.text((40,1610+i*40),part+" / "+str(width)+"x"+str(height)+
                 (" / ALERTA" if failed else " / QA PENDENTE"),
                 font=font(17),fill=color)
    # label on board, not pixel assets
    path=root/(BASENAME+".jpg")
    board.save(path,"JPEG",quality=86,optimize=True)
    report={
        "schema":"videoforge/ep01-c01p04-v3-editorial-roi-scale-audit/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "approved_mother_sha256":"a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd",
        "aligned_mother_sha256":expected_sha,
        "board":path.name,"board_sha256":sha256(path.read_bytes()).hexdigest(),
        "roi_coordinates_are_provisional_editorial_guidance":True,
        "actor_results":rows,
        "model_calls":0,"human_visual_approval":False,"rig_ready":False,
        "remotion_ready":False,"youtube_uploaded":False,
        "next":"Use exact scene mother plus layout guides to regenerate wrong-scale figures independently; confirm silhouettes and grip visually",
    }
    (root/(BASENAME+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_C01_P04_SCALE_AUDIT",json.dumps(
        {"parts":[{"name":x["part"],"bbox":[x["alpha_bbox_width"],x["alpha_bbox_height"]],
                    "warning":x["scale_outlier_warning"]} for x in rows],
         "model_calls":0,"rig_ready":False}))
    return report

if __name__=="__main__":
    main()
