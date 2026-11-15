"""Strict physical acting constraints for C01 breathing-only visual direction.

The user rejected detached wrist/boot motions, duplicate guard spears and a
cropped king. Technical gates use source pixels and actual decoded MP4.
Never turns a passing technical report into visual approval.
"""
from __future__ import annotations


class C01BreathQAError(ValueError):
    pass


LOCKED_SOURCE_BBOXES = {
    "aldric_crown_face": (458, 260, 131, 140),
    "left_spear_upper": (220, 350, 120, 215),
    "right_spear_upper": (680, 350, 120, 215),
    "right_boot": (535, 1280, 72, 70),
}


def validate_c01_v4_pose(shot: dict, static_context: dict | None) -> dict:
    nodes = {n["id"]: n for n in shot["nodes"]}
    if not static_context or static_context.get("schema") != (
            "videoforge/c01-static-context-original-mother/v1"):
        raise C01BreathQAError("C01_V4_ORIGINAL_MOTHER_CONTEXT_REQUIRED")
    source_parts = nodes.get("kael.braco-direito", {})
    left_arm = nodes.get("kael.braco-esquerdo", {})
    if (source_parts.get("parent") is not None
        or left_arm.get("parent") is not None
        or nodes.get("kael.antebraco", {}).get("parent") != "kael.braco-direito"
        or nodes.get("kael.punhos", {}).get("parent") != "kael.antebraco"
        or nodes.get("kael.bota-direita", {}).get("parent") != "kael.perna-direita"
        or nodes.get("kael.perna-direita", {}).get("parent") is not None):
        raise C01BreathQAError("C01_V4_CONTACT_JOINTS_MUST_BE_WORLD_ANCHORED")
    if any(n.get("role") == "static-context" for n in shot["nodes"]):
        raise C01BreathQAError("C01_V4_STATIC_CANDIDATES_DUPLICATE_OR_CUT_KING_SPEARS")
    tracks = {(t["target"], t["transform"]): t for t in shot["tracks"]}
    if set(tracks) != {
        ("kael.ombros", "translateY"), ("kael.cabeca", "rotationZ")}:
        raise C01BreathQAError("C01_V4_ONLY_SHOULDER_BREATH_AND_TINY_HEAD_TILT")
    if (not tracks[("kael.ombros", "translateY")]["keyframes"]
        or not tracks[("kael.cabeca", "rotationZ")]["keyframes"]
        or any(abs(k["value"]) > 2
               for k in tracks[("kael.ombros", "translateY")]["keyframes"])
        or any(abs(k["value"]) > 0.5
               for k in tracks[("kael.cabeca", "rotationZ")]["keyframes"])):
        raise C01BreathQAError("C01_V4_EXCESS_BREATHING_OR_HEAD_ROTATION")
    if (nodes.get("kael.cabelo", {}).get("mesh", {}).get("amplitudePx", 999) > 1
        or nodes.get("kael.jaqueta", {}).get("mesh", {}).get("amplitudePx", 999) > 1):
        raise C01BreathQAError("C01_V4_CLOTH_HAIR_NOT_SUBTLE")
    if shot["camera"]["move"] != "locked" or any(
        k["z"] != 14 or k["fovDeg"] != 30 or k["lookAt"] != [0, 0, 0]
        for k in shot["camera"]["keyframes"]
    ):
        raise C01BreathQAError("C01_V4_NO_CAMERA_MOTION")
    if not all(x["changed_from_original"] == 0
               for x in static_context["king_and_spears"].values()):
        raise C01BreathQAError("C01_V4_ORIGINAL_KING_SPEARS_MUST_BE_INTACT")
    return {
        "schema": "videoforge/c01-v4-subtle-acting-contract/v1",
        "right_arm_hand_parent_world_locked": True,
        "right_leg_boot_fixed": True,
        "guard_spear_king_source_pixels_original": True,
        "animated_tracks": len(tracks),
        "max_head_degrees": .5,
        "maximum_shoulder_source_pixels": 2,
        "human_visual_approved": False,
    }


def validate_c01_v5_back_breath(shot: dict, static_context: dict | None) -> dict:
    """V5 adds a real localized upper-back jacket mesh, retaining V4 contacts."""
    original = validate_c01_v4_pose(shot, static_context)
    jacket = next((n for n in shot["nodes"] if n["id"]=="kael.jaqueta"), None)
    mesh = (jacket or {}).get("mesh", {})
    back = mesh.get("backBreath")
    if (not isinstance(back,dict)
        or back.get("kind") != "upper-back-source-mesh"
        or back.get("driverTarget") != "kael.ombros"
        or back.get("driverTransform") != "translateY"
        or jacket.get("parent") != "kael.ombros"
        or not (back.get("sourceTopY")==857
                and back.get("sourcePeakY")==898
                and back.get("sourceBottomY")==947)
        or not (0 < back.get("expansionPx",0) <= 1.5
                and 0 < back.get("liftPx",0) <= 1)
        or back.get("driverPeakAbsPx") != 1.25
        or not mesh.get("sourcePin")
        or back["sourceBottomY"] >= mesh["sourcePin"]["startY"]):
        raise C01BreathQAError("C01_V5_SOURCE_PINNED_BACK_MESH_INVALID")
    shoulder = next(t for t in shot["tracks"]
                    if t["target"]=="kael.ombros" and t["transform"]=="translateY")
    head = next(t for t in shot["tracks"]
                if t["target"]=="kael.cabeca" and t["transform"]=="rotationZ")
    if (not any(k["value"]==-back["driverPeakAbsPx"] for k in shoulder["keyframes"])
        or any(k["value"]>0 or k["value"] < -back["driverPeakAbsPx"]
               for k in shoulder["keyframes"])
        or any(abs(k["value"])>.5 for k in head["keyframes"])
        or not any(abs(k["value"])>=.2 for k in head["keyframes"])):
        raise C01BreathQAError("C01_V5_BACK_BREATH_DRIVER_OR_HEAD_INVALID")
    return {
        "schema":"videoforge/c01-v5-source-back-breath-contract/v1",
        "v4_pose":original,
        "back":back,
        "source_patch":"kael.jaqueta original RGBA; no new image layers",
        "back_source_roi":[405,870,85,65],
        "head_still_moves_a_little":True,
        "jacket_waist_and_outer_seams_pinned":True,
        "hand_and_boot_remain_fixed":True,
        "no_new_generated_pixels":True,
        "human_visual_approved":False
    }



def _source_rect_to_video(shot: dict, region: tuple, width: int, height: int):
    """Projection of the locked C01 30° camera and native 1024x1536 canvas."""
    sw, sh = shot["canvas"]["width"], shot["canvas"]["height"]
    scale = height / min(sh, sw / (width / height))
    dx, dy = (width - sw * scale) / 2, (height - sh * scale) / 2
    x, y, rw, rh = region
    x0 = max(0, round(dx + scale*x))
    x1 = min(width, round(dx + scale*(x+rw)))
    y0 = max(0, round(dy + scale*y))
    y1 = min(height, round(dy + scale*(y+rh)))
    if x1 <= x0 or y1 <= y0:
        raise C01BreathQAError("C01_V4_SOURCE_REGION_OUTSIDE_OUTPUT")
    return (x0, y0, x1, y1)


def changed_pixels_in_source_region(
    frame0: bytes | bytearray,
    nextframe: bytes | bytearray,
    shot: dict,
    width: int,
    height: int,
    region: tuple[int, int, int, int],
    *,
    rgb_delta: int = 16,
) -> int:
    if (len(frame0) != 4*width*height or len(nextframe) != len(frame0)
            or width <= 0 or height <= 0 or rgb_delta < 1 or rgb_delta > 255):
        raise C01BreathQAError("C01_V4_RGBA_FRAME_OR_THRESHOLD_INVALID")
    x0,y0,x1,y1 = _source_rect_to_video(shot,region,width,height)
    changed=0
    for y in range(y0,y1):
        for x in range(x0,x1):
            i = (y*width + x)*4
            changed += max(abs(frame0[i+c]-nextframe[i+c]) for c in range(3)) >= rgb_delta
    return changed


def static_region_video_report(
    frame0: bytes | bytearray,
    later: bytes | bytearray,
    shot: dict,
    width: int,
    height: int,
) -> dict:
    # Frame-to-frame stability of real H.264 at a threshold above codec noise.
    regions={}
    for name,roi in LOCKED_SOURCE_BBOXES.items():
        changed=changed_pixels_in_source_region(
            frame0,later,shot,width,height,roi,rgb_delta=24)
        regions[name]={"changed_pixels":changed,"max_allowed":60 if name=="right_boot" else 40}
    return {
        "source": "real decoded H264 frames, no camera movement",
        "regions":regions,
        "static_props_pass":all(v["changed_pixels"]<=v["max_allowed"]
                                for v in regions.values()),
        "visual_approved":False,
    }
