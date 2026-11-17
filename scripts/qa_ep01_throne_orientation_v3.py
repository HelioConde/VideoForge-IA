"""QA comparator: C01 V2 originals vs generated V3 throne-facing proposals.

Only reads SHA-verified original PNGs. Contact-sheet resizing is for review,
not an animation sprite or an automatic visual approval.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from videoforge.layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from videoforge.ep01_throne_orientation_v3 import SOURCE_SHOTS, PRODUCER, archived, safe_png

OUT = "QA-C01-EIXO-TRONO-V3"

def font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()

def get_image(blob):
    with Image.open(BytesIO(blob)) as src:
        if src.format != "PNG":
            raise ValueError("QA_ORIENTATION_NOT_PNG")
        return src.convert("RGB").copy()

def main():
    names = ["C01-P03","C01-P04","C01-P04-ALT"]
    approvals_path = ROOT / REL / "APROVACOES-VISUAIS-C01-V3.json"
    approvals_doc = json.loads(approvals_path.read_text(encoding="utf-8"))
    if (approvals_doc.get("schema") != "videoforge/ep01-shot-mother-visual-approvals/v1"
            or approvals_doc.get("video_id") != VIDEO
            or approvals_doc.get("channel") != CHANNEL):
        raise ValueError("QA_ORIENTATION_INVALID_APPROVAL_MANIFEST")
    approvals = {row["variant"]: row for row in approvals_doc["approvals"]}
    result = []
    sheet = Image.new("RGB",(1250,2810),"#ecebe7")
    d=ImageDraw.Draw(sheet)
    d.text((32,22),"DORAMA EP01 | V2 x V3 - KAEL OLHANDO PARA O TRONO",
           font=font(24),fill="#1e1e1e")
    d.text((32,61),"APROVADA PELO CRIADOR: C01-P04 V3. OUTRAS: revisão pendente. SEM RIG.",
           font=font(15),fill="#a12e26")
    for index,target in enumerate(names):
        obj = SOURCE_SHOTS[target]
        built = archived(target)
        if built is None:
            raise ValueError("QA_ORIENTATION_MISSING_V3 " + target)
        source = get_image(safe_png(obj["source"],obj["sha256"],ROOT))
        dest_rel = (Path("assets")/"geracoes"/PRODUCER/str(built["run_id"])/(obj["asset"]+".png"))
        candidate = get_image(safe_png(dest_rel.as_posix(),built["sha256"],ROOT))
        approval = approvals.get(target)
        approved = False
        if approval is not None:
            if (approval.get("shot_id") != obj["shot"]
                    or approval.get("sha256") != built["sha256"]
                    or approval.get("source_run_id") != built["run_id"]
                    or approval.get("file") != (REL / dest_rel).as_posix()
                    or approval.get("visual_status") != "approved_by_creator"):
                raise ValueError("QA_ORIENTATION_APPROVAL_PROVENANCE_MISMATCH " + target)
            approved = True
        y=105+index*900
        for col,(img,label) in enumerate([(source,"V2 fonte, preservar arquivo"),(candidate,"V3 candidata, verificar orientacao")]):
            x=24+col*608
            d.rounded_rectangle((x,y,x+594,y+857),radius=9,fill="#ffffff")
            d.text((x+19,y+12),target+" | "+label,font=font(18),fill="#242424")
            thumb=ImageOps.contain(img,(450,794),Image.Resampling.LANCZOS)
            sheet.paste(thumb,(x+(594-thumb.width)//2,y+43))
        result.append({
            "target":target,"shot_id":obj["shot"],
            "source_sha256":obj["sha256"],
            "original_source_path":(REL/obj["source"]).as_posix(),
            "new_sha256":built["sha256"],
            "new_run_id":built["run_id"],
            "new_path":(REL/dest_rel).as_posix(),
            "approved":approved, "visual_approval_record":(approvals_path.relative_to(ROOT)).as_posix() if approved else None,
        })
    base=ROOT/REL
    board=base/(OUT+".jpg")
    sheet.save(board,"JPEG",quality=88,optimize=True)
    report={
        "schema":"videoforge/ep01-throne-orientation-review-v3/v1",
        "channel":CHANNEL,"video_id":VIDEO,
        "comparison_image":board.name,
        "comparison_sha256":sha256(board.read_bytes()).hexdigest(),
        "shots":result,
        "checks_needing_human_review":[
            "Kael faces the king and throne physically, not only with head",
            "Knee planted, hip and chest orientation consistent with gaze",
            "C01-P03: king standing, no guards/spears/sword",
            "C01-P04: king seated and two guards with spears crossed high",
            "Hands wrap spear lower/base and shafts not floating",
            "Outfits/identities and camera/light continuity",
        ],
        "human_visual_approval":False, "visual_approval_scope":"individual_only",
        "approved_visual_count":sum(1 for row in result if row["approved"]),
        "approval_record":approvals_path.relative_to(ROOT).as_posix(),
        "rig_ready":False,
        "mp4_generated":False,"youtube_uploaded":False,
        "no_paid_provider_calls":True,"no_sprite_cutout_for_rig":True,
    }
    (base/(OUT+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_THRONE_V3_QA_READY",json.dumps(
        {"candidates":len(result),"sha256":report["comparison_sha256"],
         "human_visual_approval":False},ensure_ascii=False))

if __name__=="__main__":
    main()
