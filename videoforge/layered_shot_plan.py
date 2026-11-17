"""Contrato da produção por cena-mãe + camadas + rig/câmera do EP01.

Arquivo de planejamento, NÃO gera imagens. A direção de câmera já existe
e complementa a sequência de 40 tomadas, sem precisar de poses prévias.
"""
from __future__ import annotations
import json
from pathlib import Path
from .errors import VideoForgeError
from .remake_autopilot import ROOT

CHANNEL="alchemy-lab"
VIDEO="mmorpg-conquiste-a-princesa-ep01"
REL=Path("canal")/CHANNEL/"videos"/VIDEO
SCHEMA="videoforge/layered-shot-camera-plan/v1"
CAMERA_TYPES={"black","insert","low_angle","wide","close_up",
              "extreme_close_up","match_cut","over_shoulder","medium",
              "tracking","two_shot","action"}
# The broad scene queue can list objects that are deliberately NOT shown in a
# tighter shot. C01-P03 must not reveal guards' spears or the executioner's sword;
# those belong to later shots, notably C01-P04.
EXPLICITLY_HIDDEN_SCENE_PROPS={"C01-P03":{"lanca-guarda","espada-carrasco"}}
REQUIRED_MOVES={"none","micro_push_and_focus_shift","slow_dolly_out_with_parallax",
                "slow_tilt_up","subtle_push_in","subtle_focus_shift",
                "lateral_drift","occlusion_reveal","subject_follow",
                "gentle_lateral_travel","action_follow","matched_focal_cut"}


def _read(path: Path, limit: int = 300_000):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise VideoForgeError("LAYERED_PLAN_SOURCE_MISSING")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as e:
        raise VideoForgeError("LAYERED_PLAN_JSON_INVALID") from e


def validate(root: Path = ROOT) -> dict:
    root=Path(root)
    plan=_read(root/REL/"PLANO-CAMADAS-CAMERA-EP01.json")
    story=_read(root/REL/"roteiro.json")
    queue=_read(root/"canal"/CHANNEL/"biblia-visual"/"FILA-EP01.json")
    director=_read(root/REL/"direcao-cinematografica-planos.json")
    if (plan.get("schema")!=SCHEMA or plan.get("channel")!=CHANNEL
        or plan.get("video_id")!=VIDEO or
        plan.get("pose_images_as_prerequisite") is not False
        or plan.get("legacy_pose_queue")!="deprecated_archive_only_no_paid_calls"
        or plan.get("images_requested_by_shot_not_yet_generated") is not True):
        raise VideoForgeError("LAYERED_PLAN_ORIGIN_OR_POLICY_INVALID")
    separation = plan.get("asset_generation_contract", {})
    if (separation.get("schema") != "videoforge/proxy-generated-separate-assets/v1"
            or separation.get("generation_method") != "proxy_generated_separate_image"
            or separation.get("prohibit_final_sprites_from_local_segmentation") is not True
            or separation.get("local_masks_allowed_for_QA_only") is not True
            or separation.get("rig_requires_human_visual_approval") is not True
            or "proxy" not in plan.get("production_strategy", "")):
        raise VideoForgeError("LAYERED_PLAN_PROXY_ASSET_CONTRACT_MISSING")
    if (plan.get("frame_size")!=
            {"width":1080,"height":1920,"fps":30,"aspect_ratio":"9:16"}
        or plan.get("completion",{}).get("shots_generated_by_this_plan")!=0
        or plan.get("completion",{}).get("youtube_uploaded") is not False):
        raise VideoForgeError("LAYERED_PLAN_RENDER_NOT_ALLOWED")
    if (queue.get("total_tomadas")!=40
        or not isinstance(plan.get("shots"),list)
        or len(plan["shots"])!=40
        or not isinstance(story.get("scenes"),list)):
        raise VideoForgeError("LAYERED_PLAN_SHOT_COUNT_MISMATCH")
    canonical={x["shot_id"]:(s,x) for s in story["scenes"] for x in s["shots"]}
    item_by_id={x["id"]:x for x in queue["tomadas"]}
    directed={x["id"]:x for x in director["shots"]}
    if (len(canonical)!=40 or len(item_by_id)!=40
        or len(set(s["id"] for s in plan["shots"]))!=40
        or set(canonical)!=set(item_by_id)
        or set(canonical)!={s["id"] for s in plan["shots"]}
        or len(directed)!=37):
        raise VideoForgeError("LAYERED_PLAN_COVERAGE_INVALID")
    previous_end=0
    supplements=[]
    by_type={}
    for shot in plan["shots"]:
        ident=shot["id"]
        scene,screenplay=canonical[ident]
        queued=item_by_id[ident]
        frames=shot.get("timecode_frames",{})
        if (shot.get("scene")!=scene["scene_id"] or
            shot.get("scene")!=queued["cena"] or
            frames!={"start":screenplay["start_frame"],
                     "end_exclusive":screenplay["end_exclusive"]} or
            frames["start"]!=previous_end or
            frames["end_exclusive"]<=frames["start"]):
            raise VideoForgeError("LAYERED_PLAN_CUTS_NOT_CONTIGUOUS "+ident)
        previous_end=frames["end_exclusive"]
        camera=shot.get("camera",{})
        typ=camera.get("shot_type")
        if (typ not in CAMERA_TYPES or
            camera.get("virtual_motion") not in REQUIRED_MOVES or
            not isinstance(camera.get("primary_focus"),str) or
            not camera["primary_focus"] or
            camera.get("format")!="vertical_9_16" or
            camera.get("prevent_nonuniform_stretch") is not True or
            camera.get("preserve_subject_visibility") is not True):
            raise VideoForgeError("LAYERED_PLAN_CAMERA_INVALID "+ident)
        by_type[typ]=by_type.get(typ,0)+1
        if ident in directed:
            original=directed[ident]
            if (typ!=original["shot_type"] or
                camera.get("lens_mm")!=original["lens_mm"] or
                camera.get("primary_focus")!=original["primary_focus"]):
                raise VideoForgeError("LAYERED_PLAN_DIRECTOR_DRIFT "+ident)
        else:
            supplements.append(ident)
            if shot.get("source_plan")!="roteiro.json (complemento editorial)":
                raise VideoForgeError("LAYERED_PLAN_SUPPLEMENT_SOURCE_MISMATCH")
        images=shot.get("images",{})
        if ident=="C01-P01":
            if (typ!="black" or images.get("no_generation") is not True
                or images.get("required")!=[]):
                raise VideoForgeError("LAYERED_PLAN_BLACK_REQUIRES_NO_IMAGE")
            continue
        if (images.get("composite",{}).get("id")!="scene-mother"
            or images.get("background",{}).get("source")!="scene-mother"
            or images.get("background",{}).get("alpha")!="opaque"
            or shot.get("rig",{}).get("independent_pose_image_required") is not False):
            raise VideoForgeError("LAYERED_PLAN_MOTHER_FIRST_INVALID "+ident)
        if (images.get("asset_source_method") != "proxy_generated_separate_image"
            or images.get("local_segmentation_policy") != "QA_only_never_final_source"
            or images.get("mother_figure_is_visual_reference_not_cutout_source") is not True
            or images.get("rig_parts_policy") != "request_additional_transparent_png_per_actual_animated_part_from_proxy_no_pixel_cutout"
            or shot.get("rig",{}).get("no_pixel_mask_derived_final_layers") is not True
            or shot.get("qa",{}).get("reject_cutout_or_segmentation_final_sprites") is not True):
            raise VideoForgeError("LAYERED_PLAN_REQUIRES_PROXY_GENERATED_LAYERS " + ident)
        requested = images.get("proxy_generation_requests")
        if not isinstance(requested,list):
            raise VideoForgeError("LAYERED_PLAN_PROXY_REQUESTS_MISSING " + ident)
        expected = {"background-clean"} | {
            "character-" + x["id"] for x in images.get("characters",[])
        } | {
            "object-" + x["id"] for x in images.get("objects",[])
            if x.get("transparent_rgba") is True
        }
        if ({x.get("id") for x in requested if isinstance(x,dict)} != expected
            or len(requested)!=len(expected)
            or any(x.get("method")!="proxy_generated_separate_image"
                   for x in requested if isinstance(x,dict))):
            raise VideoForgeError("LAYERED_PLAN_PROXY_ASSET_IDS_INCONSISTENT "+ident)
        if (images.get("background",{}).get("generation_method")!="proxy_generated_separate_image"
            or any(x.get("generation_method")!="proxy_generated_separate_image"
                   for x in images.get("characters",[]))
            or any(x.get("generation_method")!="proxy_generated_separate_image"
                   for x in images.get("objects",[]) if x.get("transparent_rgba") is True)):
            raise VideoForgeError("LAYERED_PLAN_PROXY_GENERATION_METHOD_INVALID "+ident)
        actors={x["id"] for x in images.get("characters",[])}
        if not set(queued["personagens"])<=actors:
            raise VideoForgeError("LAYERED_PLAN_MISSING_CHARACTERS "+ident)
        animated={x["id"] for x in images.get("objects",[])}
        hidden=EXPLICITLY_HIDDEN_SCENE_PROPS.get(ident,set())
        if (not set(queued["objetos"])-hidden <= animated or
            hidden & animated or
            set(shot.get("qa",{}).get("explicitly_hidden_scene_props",[])) != hidden):
            raise VideoForgeError("LAYERED_PLAN_MISSING_OR_UNEXPECTED_PROPS "+ident)
        if (not images.get("required") or
            shot.get("qa",{}).get("source_sha256_required") is not True or
            shot.get("qa",{}).get("compare_composite_to_alpha_recomposition") is not True or
            shot.get("qa",{}).get("youtube_upload") is not False):
            raise VideoForgeError("LAYERED_PLAN_QA_NOT_FAIL_CLOSED "+ident)
    if (previous_end!=story["format"]["duration_frames"] or
        set(supplements)!={"C01-P05","C08-P04","C12-P04"} or
        by_type.get("wide",0)<3 or
        sum(by_type.get(x,0) for x in ("close_up","extreme_close_up"))<10 or
        len({s["camera"]["primary_focus"] for s in plan["shots"]})<8):
        raise VideoForgeError("LAYERED_PLAN_CINEMATIC_COVERAGE_INVALID")
    return {"shot_count":40,"shot_mothers_to_generate":39,
            "predefined_camera_shots":37,"additional_camera_shots":sorted(supplements),
            "camera_type_distribution":by_type,
            "pose_images_required":False,"separated_assets_from_proxy":True,
            "local_cutout_for_rig_allowed":False,"image_provider_calls":0,
            "youtube_uploaded":False}


def main():
    result=validate()
    print("LAYERED_SHOTS_VALIDATED",json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
