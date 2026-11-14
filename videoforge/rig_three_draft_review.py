"""Stage an unapproved Anya ThreeCanvas *technical review*, never official.

Production's validate_rig_folder() still refuses this candidate. Only this
fixed, source-hashed scene can be rendered in an isolated REVIEW composition.
No AI inference, no generic arbitrary rig, no upload, no approval flags.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .animation_manual import enforce_animation_manual
from .errors import VideoForgeError
from .rig_three_contract import ThreeRigError, validate_rig_folder
from .rig_three_hand_split import sha, unique
from .rig_three_hair_draft import SOURCE_SHA
from .scene_layers import png_info

ROOT=Path(__file__).resolve().parents[1]
CHANNEL="otaku-br"
VIDEO_ID="spy-x-family-familia-de-mentira"
SCENE="cena-01"
MOTHER_SHA="ed190024abb3bd35bd79c40b1c6c5b4925486cbedd2213404afa73faac199dd8"
EXPECTED_PARTS={
    "head-open","head-closed","body-no-head",
    "hair-front-left","hair-front-right","hand"
}
FRAMES=[0,30,74,76,173,175,239]


def _checked(path:Path,hash_value:str)->Path:
    if path.is_symlink() or not path.is_file() or sha(path)!=hash_value:
        raise VideoForgeError("ANYA_DRAFT_SOURCE_SHA_MISMATCH_"+path.name)
    return path


def prepare(original_dir:Path,corrected_dir:Path,
            candidate_dir:Path,output:Path)->dict:
    enforce_animation_manual()
    source_manifest=json.loads(
        _checked(original_dir/"manifest.json",sha(original_dir/"manifest.json"))
        .read_text(encoding="utf-8"))
    if (source_manifest.get("channel"),source_manifest.get("video_id"),
        source_manifest.get("scene"))!=(CHANNEL,VIDEO_ID,SCENE):
        raise VideoForgeError("ANYA_DRAFT_SOURCE_PROVENANCE_MISMATCH")
    if source_manifest.get("source",{}).get("sha256")!=MOTHER_SHA:
        raise VideoForgeError("ANYA_DRAFT_SCENE_MOTHER_MISMATCH")
    background=_checked(original_dir/"background.png",
      source_manifest.get("layers",{}).get("background",{}).get("sha256",""))
    source=_checked(original_dir/"character-main.png",SOURCE_SHA)
    if (png_info(background.read_bytes())["width"],
        png_info(background.read_bytes())["height"])!=(1024,1536):
        raise VideoForgeError("ANYA_DRAFT_BACKGROUND_DIMENSIONS_INVALID")
    if (png_info(source.read_bytes(),require_alpha=True)["width"],
        png_info(source.read_bytes(),require_alpha=True)["height"])!=(1024,1536):
        raise VideoForgeError("ANYA_DRAFT_SOURCE_DIMENSIONS_INVALID")
    corrected_report=json.loads(unique(corrected_dir,"qa.json").read_text(
        encoding="utf-8"))
    if (corrected_report.get("source_original_sha256")!=SOURCE_SHA or
        corrected_report.get("original_partition_alpha_differences_after_correction")!=0
        or corrected_report.get("human_visual_approval") is not False or
        corrected_report.get("neutral_open_roundtrip_status")!=
           "pixel_qa_passed_visual_review_pending"):
        raise VideoForgeError("ANYA_DRAFT_STATIC_OTHERS_QA_FAILED")
    static_other=unique(corrected_dir,
                        "other-characters-without-anya-candidate.png")
    _checked(static_other,corrected_report.get("files",{}).get(
        static_other.name,""))
    p=png_info(static_other.read_bytes(),require_alpha=True)
    if (p["width"],p["height"])!=(1024,1536):
        raise VideoForgeError("ANYA_DRAFT_STATIC_OTHERS_DIMENSIONS_INVALID")
    pack=candidate_dir/"rig-candidate"
    qa=json.loads((pack/"pack.qa.json").read_text(encoding="utf-8"))
    prep=json.loads((candidate_dir/"qa.json").read_text(encoding="utf-8"))
    if (qa.get("source_character_sha256")!=SOURCE_SHA or
        qa.get("scene_mother_sha256")!=MOTHER_SHA or
        qa.get("rig_production_validation")!=
          "EXPECTED_REJECTION_HUMAN_REVIEW_REQUIRED" or
        qa.get("human_visual_approval") is not False or
        qa.get("layers_cropped")!=6 or
        qa.get("deformable_side_hair_meshes")!=2 or
        prep.get("actually_opaque_underlay_pixel_count",0)<10000 or
        prep.get("human_visual_approval") is not False or
        prep.get("real_threecanvas_render_passed") is not False):
        raise VideoForgeError("ANYA_DRAFT_CANDIDATE_SOURCE_QA_REJECTED")
    manifest=json.loads((pack/"rig.json").read_text(encoding="utf-8"))
    if (manifest.get("channel"),manifest.get("video_id"),
        manifest.get("scene"))!=(CHANNEL,VIDEO_ID,SCENE):
        raise VideoForgeError("ANYA_DRAFT_RIG_PROVENANCE_INVALID")
    if (manifest.get("provisional") is not True or
        set(x.get("id") for x in manifest.get("layers",[]))!=EXPECTED_PARTS or
        manifest.get("sceneMotherSha256")!=MOTHER_SHA or
        manifest.get("canvas")!={"width":1024,"height":1536} or
        any(value is not False for value in
            manifest.get("humanReview",{}).values()) or
        len(manifest.get("humanReview",{}))!=5):
        raise VideoForgeError("ANYA_DRAFT_RIG_NOT_IN_REVIEW_STATE")
    try:
        validate_rig_folder(pack,channel=CHANNEL,video_id=VIDEO_ID,
                            scene=SCENE,scene_mother_sha256=MOTHER_SHA,
                            frames=240)
    except ThreeRigError as err:
        if str(err)!="THREE_RIG_HUMAN_REVIEW_REQUIRED":
            raise
    else:
        raise VideoForgeError("ANYA_DRAFT_PRODUCTION_GATE_INCORRECTLY_OPEN")
    for layer in manifest["layers"]:
        name=layer["file"]
        if (name not in qa["files"] or
            layer["sha256"]!=qa["files"][name] or
            layer["id"]+".png"!=name):
            raise VideoForgeError("ANYA_DRAFT_MANIFEST_HASH_CONTRACT_INVALID")
        asset=_checked(pack/name,layer["sha256"])
        info=png_info(asset.read_bytes(),require_alpha=True)
        if (info["width"],info["height"])!=tuple(layer["bbox"][2:]):
            raise VideoForgeError("ANYA_DRAFT_CROPPED_BBOX_INVALID")
    if output.exists():
        raise VideoForgeError("ANYA_DRAFT_OUTPUT_EXISTS")
    public=ROOT/"motion-remotion"/"public"/"vf-scene"
    if public.exists():
        raise VideoForgeError("ANYA_DRAFT_PUBLIC_ASSETS_ALREADY_EXIST")
    (public/"rig-three").mkdir(parents=True)
    shutil.copyfile(background,public/"background.png")
    shutil.copyfile(static_other,public/"other-characters-static.png")
    for layer in manifest["layers"]:
        shutil.copyfile(pack/layer["file"],public/"rig-three"/layer["file"])
        layer["file"]="vf-scene/rig-three/"+layer["file"]
    output.mkdir(parents=True)
    props={
        "reviewOnly":True,
        "youtubeUpload":False,
        "durationFrames":240,
        "background":"vf-scene/background.png",
        "otherCharacters":"vf-scene/other-characters-static.png",
        "rig":manifest,
    }
    (output/"props.json").write_text(json.dumps(props,ensure_ascii=False,
                                          indent=2)+"\n",encoding="utf-8")
    result={
      "schema":"videoforge/rig-three-anya-draft-visual-qa/v1",
      "channel":CHANNEL,"video_id":VIDEO_ID,"scene":SCENE,
      "source_character_sha256":SOURCE_SHA,
      "source_scene_mother_sha256":MOTHER_SHA,
      "other_characters_source_sha256":sha(static_other),
      "rig_sprites_count":6,
      "deformable_hair_meshes":2,
      "real_threecanvas_review":True,
      "frames_requested":FRAMES,
      "source_artifact_run":43598536256,
      "static_others_run":43591918632,
      "rig_art_reapproved":False,
      "human_visual_approval":False,
      "official_rig_validator":"blocked_as_designed",
      "video_official":False,"youtube_uploaded":False,
    }
    (output/"stage.qa.json").write_text(json.dumps(result,ensure_ascii=False,
                                              indent=2)+"\n",encoding="utf-8")
    print("ANYA_THREE_DRAFT_VISUAL_QA_STAGE",json.dumps(result))
    return result


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--corrected",type=Path,required=True)
    p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--dest",type=Path,required=True)
    a=p.parse_args()
    try:
        prepare(a.original,a.corrected,a.candidate,a.dest)
        return 0
    except (VideoForgeError,ThreeRigError,OSError,ValueError,KeyError,
            TypeError) as exc:
        print("ANYA_THREE_DRAFT_VISUAL_QA_BLOCKED",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
