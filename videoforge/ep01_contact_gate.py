"""Gate fail-closed da interação espada+bainha da tomada C01-P02.

Evita que a antiga camada feita pela IA (981x1602) ou versões
deslocadas sejam tratadas como aprovadas. Apenas lê dados reais GitHub.
Um teste de hashes NÃO é prova de contato anatômico/cena animável.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .errors import VideoForgeError
from .layered_shot_plan import ROOT, REL, CHANNEL, VIDEO
from .ep01_contact_cutouts import EXPECTED_MOTHER_SHA

REQUIRED={
    "c01-p02-object-bainha-source-visible",
    "c01-p02-object-espada-source-visible",
    "c01-p02-hand-upper-contact-occlusion",
    "c01-p02-hand-lower-contact-occlusion",
}
MAX_DELTA_RGB=6.0
FINAL_SCOPE="contato_espada_bainha_c01_p02"


def _read_json(path:Path,max_size:int=250000):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>max_size:
        raise VideoForgeError("EP01_CONTACT_QA_REPORT_MISSING")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError) as exc:
        raise VideoForgeError("EP01_CONTACT_QA_REPORT_INVALID") from exc


def audit(root:Path=ROOT)->dict:
    root=Path(root)
    registry=_read_json(root/"canal"/CHANNEL/"biblia-visual"/"REGISTRO-GERACOES.json",1000000)
    rows=registry.get("geracoes",[])
    proofs={}
    for asset in REQUIRED:
        entries=[x for x in rows if x.get("asset")==asset]
        if len(entries)!=1:
            raise VideoForgeError("EP01_CONTACT_SOURCE_REQUIRED "+asset)
        row=entries[0]
        path=Path(row.get("arquivo",""))
        if (path.is_absolute() or ".." in path.parts or
            not path.is_relative_to(REL/"assets"/"geracoes")):
            raise VideoForgeError("EP01_CONTACT_SOURCE_PATH_INVALID")
        file=root/path
        if file.is_symlink() or not file.is_file() or file.stat().st_size>35_000_000:
            raise VideoForgeError("EP01_CONTACT_SOURCE_BYTES_MISSING")
        digest=hashlib.sha256(file.read_bytes()).hexdigest()
        if digest!=row["sha256"] or [row["width"],row["height"]]!=[941,1672]:
            raise VideoForgeError("EP01_CONTACT_SOURCE_SHA_OR_CANVAS_TAMPERED")
        provenance=_read_json(file.with_suffix(".production.json"))
        if (provenance.get("source_mother_sha256")!=EXPECTED_MOTHER_SHA or
            provenance.get("sha256")!=digest or
            provenance.get("youtube_uploaded") is not False):
            raise VideoForgeError("EP01_CONTACT_SOURCE_PROVENANCE_INVALID")
        proofs[asset]=digest
    report=_read_json(root/REL/"QA-C01-P02-ESPADA-PIXELS.json")
    before=_read_json(root/REL/"QA-C01-P02-CONTATO-PIXELS.json")
    if (report.get("schema")!="videoforge/ep01-source-sword-comparison/v1"
        or before.get("schema")!="videoforge/ep01-source-contact-comparison/v1"
        or report.get("mother_sha256")!=EXPECTED_MOTHER_SHA
        or before.get("mother_sha256")!=EXPECTED_MOTHER_SHA
        or report.get("sword_source_sha256")!=proofs["c01-p02-object-espada-source-visible"]
        or report.get("hands_final_z_order") is not True
        or report.get("visual_approved") is not False
        or report.get("rig_authorized") is not False
        or before.get("human_visual_approval") is not False):
        raise VideoForgeError("EP01_CONTACT_QA_REPORT_INCONSISTENT")
    score=report.get("new_composite_mean_rgb_delta")
    old=report.get("old_composite_mean_rgb_delta")
    if (not isinstance(score,(float,int)) or isinstance(score,bool) or
        not isinstance(old,(float,int)) or isinstance(old,bool) or
        score<0 or old<0):
        raise VideoForgeError("EP01_CONTACT_QA_METRIC_INVALID")
    reasons=[]
    if score>MAX_DELTA_RGB:
        reasons.append("recomposition_rgb_diff_exceeds_review_threshold")
    approval_path=root/REL/"APROVACAO-CONTACTO-C01-P02.json"
    review=None
    if approval_path.exists():
        review=_read_json(approval_path)
        if (review.get("status")!="aprovado"
            or review.get("scope")!=FINAL_SCOPE
            or review.get("mother_sha256")!=EXPECTED_MOTHER_SHA
            or review.get("candidate_sha256")!=proofs
            or not review.get("revisor") or not review.get("evidencia")
            or review.get("contato_maos_espada_bainha_verificado") is not True):
            raise VideoForgeError("EP01_CONTACT_APPROVAL_INVALID_OR_INCOMPLETE")
    if review is None:
        reasons.append("human_contact_review_missing")
    return {
        "shot_id":"C01-P02",
        "source_sha256":EXPECTED_MOTHER_SHA,
        "candidate_sha256":proofs,
        "old_diff_rgb":old,
        "new_diff_rgb":score,
        "improved":score<old,
        "threshold":MAX_DELTA_RGB,
        "render_ready":len(reasons)==0,
        "blocking_reasons":reasons,
        "provider_calls":0,
        "mp4_claim":False,
    }


def require_ready(root:Path=ROOT)->dict:
    row=audit(root)
    if not row["render_ready"]:
        raise VideoForgeError("EP01_CONTACT_RIG_RENDER_BLOCKED: "+
                              ",".join(row["blocking_reasons"]))
    return row


def main()->None:
    import json
    report=audit()
    print("EP01_CONTACT_GATE",json.dumps(report,ensure_ascii=False))
    print("EP01_CONTACT_COMPOSITING_BLOCKED" if not report["render_ready"]
          else "EP01_CONTACT_REVIEW_READY")


if __name__=="__main__":
    main()
