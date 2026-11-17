"""Create small human-review JPEG of an archived, SHA-checked grip guide."""
from __future__ import annotations
from hashlib import sha256
import json
from io import BytesIO
from PIL import Image, ImageOps
from videoforge.layered_shot_plan import ROOT,REL,CHANNEL,VIDEO

RUN=44183662671
SHA="eaeafebd244b9059006b7cfe74dcc4ebeeecf3471102283f883c52ad8032e16c"
ROOT_NAME="QA-C01-P04-V3-GUIA-PEGADA-V1"
SOURCE=REL/"assets"/"geracoes"/"production-c01p04-v3-canonical-grip-guide-v1"/str(RUN)/"c01-p04-v3-left-grip-with-real-spear-reference-v1.png"

def main():
    p=ROOT/SOURCE
    proof=p.with_suffix(".production.json")
    if any(x.is_symlink() or not x.is_file() for x in (p,proof)):
        raise ValueError("EP01_GRIP_GUIDE_QA_MISSING_SOURCE")
    raw=p.read_bytes()
    record=json.loads(proof.read_text(encoding="utf-8"))
    if (sha256(raw).hexdigest()!=SHA or record.get("sha256")!=SHA
        or record.get("schema")!="videoforge/ep01-c01p04-grip-topology-guide/v1"
        or record.get("human_visual_approval") is not False
        or record.get("rig_ready") is not False):
        raise ValueError("EP01_GRIP_GUIDE_QA_PROVENANCE_INVALID")
    with Image.open(BytesIO(raw)) as i:
        if i.format!="PNG":raise ValueError("EP01_GRIP_GUIDE_QA_IMAGE_BAD_FORMAT")
        art=ImageOps.contain(i.convert("RGB"),(740,1010),Image.Resampling.LANCZOS)
    out=ROOT/REL/(ROOT_NAME+"-PREVIEW.jpg")
    art.save(out,"JPEG",quality=72,optimize=True)
    result={
        "schema":"videoforge/ep01-c01p04-grip-guide-human-review/v1",
        "channel":CHANNEL,"video_id":VIDEO,"shot_id":"C01-P04",
        "source_file":SOURCE.as_posix(),"source_sha256":SHA,
        "preview_file":out.name,"preview_sha256":sha256(out.read_bytes()).hexdigest(),
        "source_is_independent_ai_reference_not_rig":True,
        "human_visual_review_checks":[
            "wooden_spear_passes_through_palm_center",
            "fingers_thumb_wrap_around_real_shaft",
            "spear_base_extends_below_grip",
            "wrist_and_fingers_match_approved_mother_closeup",
            "no_floating_spear_or_extra_fingers",
        ],
        "human_visual_approval":False,"hand_contact_verified":False,
        "rig_ready":False,"mp4_generated":False,"youtube_uploaded":False,
        "image_provider_calls":0
    }
    (ROOT/REL/(ROOT_NAME+".json")).write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EP01_GRIP_GUIDE_QA",json.dumps({
        "preview":out.name,"preview_sha256":result["preview_sha256"],
        "human_visual_approval":False,"rig_ready":False},ensure_ascii=False))

if __name__=="__main__":
    main()
