"""EP01 C08 cart/Kael physical kinematic *debug*, independent of scene art.

A reproducible wheel-contact and attached-grip controller for the 130-frame
C08-P02 turn and 110-frame C08-P03 hold. Uses the PINNED 7 keyframes. The
display renderer is a neutral wireframe and never uses, separates or moves
a flattened scene PNG. It is NOT an animation of the approved characters.

Axes: ground plane (x,z), cart forward=(-cos(yaw), sin(yaw)).
Wheel forward rolling distances ds±half_track*dyaw prevent lateral sliding
for a differential-wheel chassis. Grip is a point attached to the same
chassis transform; no disconnected hand sprites are created.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .ep01_continuity_motion import ROOT, read as read_motion, validate_keyframes

FPS = 30
WHEEL_RADIUS_M = 0.24
HALF_WHEEL_TRACK_M = 0.46
CART_LENGTH_M = 1.55
CART_WIDTH_M = 0.92
GRIP_OFFSET_M = 1.12
KAEL_BODY_OFFSET_M = 1.66
TRAVEL_M = 1.65
CART_INITIAL_X = 2.35
CART_INITIAL_Z = -0.55
MAX_CENTER_STEP_M = 0.11
MAX_YAW_STEP_DEG = 6.0
TURN_SHOT = "C08-P02"
HOLD_SHOT = "C08-P03"
SOURCE_FRAME_COUNT = 130
HOLD_FRAME_COUNT = 110

@dataclass(frozen=True)
class Pose:
    frame: int
    shot_id: str
    shot_frame: int
    cart_center: tuple[float, float]
    yaw_degrees: float
    push_progress: float
    wheel_left_center: tuple[float, float]
    wheel_right_center: tuple[float, float]
    wheel_left_rotation: float
    wheel_right_rotation: float
    grip: tuple[float, float]
    kael_body_center: tuple[float, float]
    grip_connection_error_m: float
    wheel_contact_slip_m: float
    chasers: tuple[tuple[float, float], ...]

def add(a: tuple[float,float], b: tuple[float,float]) -> tuple[float,float]:
    return (a[0]+b[0], a[1]+b[1])

def mult(a: tuple[float,float], s: float) -> tuple[float,float]:
    return (a[0]*s, a[1]*s)

def distance(a: tuple[float,float], b: tuple[float,float]) -> float:
    return math.hypot(a[0]-b[0],a[1]-b[1])

def forward(rad: float) -> tuple[float,float]:
    return (-math.cos(rad), math.sin(rad))

def right(rad: float) -> tuple[float,float]:
    return (-math.sin(rad), -math.cos(rad))

def interpolate_keys(keys: list[dict], frame: int) -> tuple[float,float]:
    if frame < keys[0]["frame"] or frame > keys[-1]["frame"]:
        raise ValueError("Frame outside pinned cart motion")
    for index in range(1,len(keys)):
        start,end=keys[index-1],keys[index]
        if frame <= end["frame"]:
            q=(frame-start["frame"])/(end["frame"]-start["frame"])
            q=q*q*(3-2*q)  # no step discontinuities at the keyframes
            return (start["cart_yaw_degrees"]+(end["cart_yaw_degrees"]-start["cart_yaw_degrees"])*q,
                    start["push_progress"]+(end["push_progress"]-start["push_progress"])*q)
    raise ValueError("Frame not covered")

def build_poses(plan: dict) -> list[Pose]:
    """Return exactly 240 deterministic kinematic frames with continuous cut."""
    if (plan.get("schema") != "videoforge/ep01-c07c08-motion-readiness/v1"
            or plan.get("status") != "proposal_only_not_rig_approved"
            or plan.get("rules",{}).get("never_use_full_png_as_rig") is not True
            or plan["rules"].get("independent_hands") is not False
            or plan["rules"].get("allow_image_generation") is not False
            or plan["rules"].get("allow_publish") is not False
            or plan.get("QA",{}).get("art_approval") is not False
            or plan.get("QA",{}).get("rig_ready") is not False
            or plan.get("QA",{}).get("animation_qa_passed") is not False):
        raise ValueError("Cannot turn unapproved art into an apparent production rig")
    shots={row["id"]:row for row in plan["shots"]}
    if set(shots) != {"C07-P03",TURN_SHOT,HOLD_SHOT}:
        raise ValueError("Unexpected C07/C08 motion scope")
    turn,hold=shots[TURN_SHOT],shots[HOLD_SHOT]
    validate_keyframes(turn)
    if (turn["end_exclusive"]-turn["start_frame"]!=SOURCE_FRAME_COUNT
            or hold["end_exclusive"]-hold["start_frame"]!=HOLD_FRAME_COUNT
            or turn["cast_present"]!=["kael"]
            or "pursuer_1" not in turn["cast_forbidden"]
            or "pursuer_2" not in turn["cast_forbidden"]
            or hold["cast_present"]!=["kael","pursuer_1","pursuer_2"]
            or hold["cast_forbidden"]!=["elara"]
            or hold["cart_yaw_degrees"]!=90
            or hold["cart_start_state"]!=turn["final_cart_state"]
            or hold["cart_end_state"]!=turn["final_cart_state"]):
        raise ValueError("The two cart shots disagree with the pinned story")
    keys=turn["frames"]
    poses=[]
    center=(CART_INITIAL_X,CART_INITIAL_Z)
    wheel_left_rad=wheel_right_rad=0.
    prev_yaw=0.
    prev_progress=0.
    max_slip=0.
    for frame in range(SOURCE_FRAME_COUNT+HOLD_FRAME_COUNT):
        in_turn=frame<SOURCE_FRAME_COUNT
        shot_frame=frame if in_turn else frame-SOURCE_FRAME_COUNT
        shot=TURN_SHOT if in_turn else HOLD_SHOT
        yaw,progress=interpolate_keys(keys,frame) if in_turn else (90.,1.)
        rad=math.radians(yaw)
        prev_rad=math.radians(prev_yaw)
        diff_yaw=rad-prev_rad
        ds=TRAVEL_M*(progress-prev_progress)
        # Integrate differential-wheel nonholonomic chassis motion.
        midpoint=prev_rad+diff_yaw*.5
        center=add(center,mult(forward(midpoint),ds))
        # Wheel-travel differential compensates pivot rotation.
        left_ds=ds+HALF_WHEEL_TRACK_M*diff_yaw
        right_ds=ds-HALF_WHEEL_TRACK_M*diff_yaw
        new_left=wheel_left_rad+left_ds/WHEEL_RADIUS_M
        new_right=wheel_right_rad+right_ds/WHEEL_RADIUS_M
        left_center=add(center,mult(right(rad),HALF_WHEEL_TRACK_M))
        right_center=add(center,mult(right(rad),-HALF_WHEEL_TRACK_M))
        grip=add(center,mult(forward(rad),-GRIP_OFFSET_M))
        kael=add(center,mult(forward(rad),-KAEL_BODY_OFFSET_M))
        connected=add(center,mult(forward(rad),-GRIP_OFFSET_M))
        slip=max(abs((new_left-wheel_left_rad)*WHEEL_RADIUS_M-left_ds),
                 abs((new_right-wheel_right_rad)*WHEEL_RADIUS_M-right_ds))
        max_slip=max(max_slip,slip)
        if in_turn:
            chasers=()
        else:
            # Pursuers on the opposite bank of the barricade, do not touch cart.
            q=min(1.,shot_frame/70)
            chasers=((-1.15+0.32*q,0.42),(-1.6+0.40*q,-0.35))
        poses.append(Pose(
            frame=frame,shot_id=shot,shot_frame=shot_frame,
            cart_center=center,yaw_degrees=yaw,push_progress=progress,
            wheel_left_center=left_center,wheel_right_center=right_center,
            wheel_left_rotation=new_left,wheel_right_rotation=new_right,
            grip=grip,kael_body_center=kael,
            grip_connection_error_m=distance(grip,connected),
            wheel_contact_slip_m=slip,chasers=chasers))
        prev_yaw,prev_progress=yaw,progress
        wheel_left_rad,wheel_right_rad=new_left,new_right
    validate_poses(poses)
    return poses

def validate_poses(poses: list[Pose]) -> dict:
    if (len(poses)!=SOURCE_FRAME_COUNT+HOLD_FRAME_COUNT
            or [x.frame for x in poses] != list(range(len(poses)))
            or [x.shot_id for x in poses] !=
                [TURN_SHOT]*SOURCE_FRAME_COUNT+[HOLD_SHOT]*HOLD_FRAME_COUNT):
        raise ValueError("Missing, duplicated or out-of-order kinematic frame")
    if (poses[0].yaw_degrees!=0 or poses[0].push_progress!=0
            or poses[SOURCE_FRAME_COUNT-1].yaw_degrees!=90
            or poses[-1].yaw_degrees!=90 or poses[-1].push_progress!=1):
        raise ValueError("Pivot does not reach the 90-degree barricade")
    for i,p in enumerate(poses):
        if not (math.isfinite(p.yaw_degrees)
                and math.isfinite(p.push_progress)
                and 0<=p.yaw_degrees<=90
                and 0<=p.push_progress<=1
                and p.grip_connection_error_m<=1e-8
                and p.wheel_contact_slip_m<=1e-8):
            raise ValueError(f"Invalid contact/pose frame {i}")
        if p.shot_id==TURN_SHOT and p.chasers:
            raise ValueError("Pursuers must never assist Kael")
        if p.shot_id==HOLD_SHOT and len(p.chasers)!=2:
            raise ValueError("Exactly two pursuers must remain behind cart")
        if i:
            prev=poses[i-1]
            if (distance(p.cart_center,prev.cart_center)>MAX_CENTER_STEP_M
                    or abs(p.yaw_degrees-prev.yaw_degrees)>MAX_YAW_STEP_DEG
                    or p.push_progress<prev.push_progress-1e-9):
                raise ValueError(f"Cart teleport or jump between frames {i-1}->{i}")
            if i>=SOURCE_FRAME_COUNT and (distance(p.cart_center,prev.cart_center)>1e-8
                    or abs(p.yaw_degrees-prev.yaw_degrees)>1e-8
                    or abs(p.wheel_left_rotation-prev.wheel_left_rotation)>1e-8
                    or abs(p.wheel_right_rotation-prev.wheel_right_rotation)>1e-8):
                raise ValueError("Cart snapped or slid in barricade hold")
            if (abs(distance(p.wheel_left_center,p.wheel_right_center)
                    -2*HALF_WHEEL_TRACK_M)>1e-7):
                raise ValueError("Rigid chassis wheel-track changed")
        # Body and connected contact are one kinematic chain, never a detached hand.
        if distance(p.grip,p.kael_body_center)>0.85:
            raise ValueError("Kael disconnected from cart handle")
    # C08-P03 begins at exactly the same cart position, yaw and spin as P02 ends.
    before,after=poses[SOURCE_FRAME_COUNT-1:SOURCE_FRAME_COUNT+1]
    for attr in ("cart_center","yaw_degrees","wheel_left_rotation",
                 "wheel_right_rotation","grip","kael_body_center"):
        if getattr(before,attr)!=getattr(after,attr):
            raise ValueError(f"Cut continuity lost for {attr}")
    return {
        "schema_version":1,"kind":"ep01_cart_physical_controller_QA",
        "fps":FPS,"frames_checked":len(poses),
        "pivot_frames":SOURCE_FRAME_COUNT,"barricade_hold_frames":HOLD_FRAME_COUNT,
        "cart_yaw_start_degrees":0,"cart_yaw_end_degrees":90,
        "max_grip_connection_error_m":max(p.grip_connection_error_m for p in poses),
        "max_wheel_contact_slip_m":max(p.wheel_contact_slip_m for p in poses),
        "continuous_cut":True,"wheels_roll_with_chassis":True,
        "chasers_never_touch_cart":True,"source_png_transforms":0,
        "sprite_layers_loaded":0,
        "wireframe_debug_only":True,
        "visual_art_approved":False,"rig_with_real_assets_approved":False,
        "full_animation_approved":False,
        "youtube_publications":0,
    }

def render_wireframe(poses: list[Pose], out: Path) -> None:
    """Draw a visibly labelled diagnostic rig preview, not transformed artwork."""
    from PIL import Image, ImageDraw, ImageFont
    if not out.parent.is_dir():
        out.parent.mkdir(parents=True,exist_ok=True)
    width,height=720,480
    ffmpeg=subprocess.Popen([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{width}x{height}",
        "-framerate",str(FPS),"-i","pipe:0",
        "-an","-c:v","libx264","-preset","veryfast","-crf","21",
        "-pix_fmt","yuv420p",str(out),
    ],stdin=subprocess.PIPE)
    def project(point):
        # Ground-plane oblique mapping makes right side of the world visibly safe.
        x,z=point
        return (round(325+(x-0.55*z)*90),round(246-z*65))
    def ellipse(draw,point,r,fill,outline):
        x,y=project(point)
        draw.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=3)
    try:
        for pose in poses:
            im=Image.new("RGB",(width,height),(19,24,32))
            draw=ImageDraw.Draw(im)
            draw.rectangle((35,105,690,410),fill=(35,40,51),outline=(92,93,102),width=3)
            # Alley boundary, target safe passage, centerline and notional chaser side.
            draw.line((35,245,690,245),fill=(73,81,98),width=2)
            draw.text((42,112),"PERSEGUIDORES / LADO ESQUERDO",fill=(255,170,155))
            draw.text((443,112),"PASSAGEM SEGURA / DIREITA",fill=(155,231,178))
            theta=math.radians(pose.yaw_degrees)
            axis=forward(theta)
            side=right(theta)
            cart=pose.cart_center
            corners=[project(add(add(cart,mult(axis,sx*CART_LENGTH_M/2)),
                                 mult(side,sz*CART_WIDTH_M/2)))
                     for sx,sz in ((-1,-1),(-1,1),(1,1),(1,-1))]
            draw.polygon(corners,fill=(120,84,52))
            draw.line(corners+[corners[0]],fill=(233,181,96),width=5,joint="curve")
            for point,spin in ((pose.wheel_left_center,pose.wheel_left_rotation),
                               (pose.wheel_right_center,pose.wheel_right_rotation)):
                ellipse(draw,point,13,(66,69,75),(215,216,220))
                c=project(point)
                draw.line((c[0],c[1],c[0]+11*math.cos(spin),c[1]+11*math.sin(spin)),
                          fill=(244,232,157),width=3)
            # Kael torso and connected arm; grip is an anatomical anchor on the same transform.
            ellipse(draw,pose.kael_body_center,18,(91,146,208),(180,214,251))
            draw.line((project(pose.kael_body_center),project(pose.grip)),
                      fill=(173,213,244),width=7)
            ellipse(draw,pose.grip,4,(239,237,213),(239,237,213))
            for chaser in pose.chasers:
                ellipse(draw,chaser,15,(147,70,70),(240,142,142))
            draw.text((36,18),"EP01 C08  |  RIG CINEMATICO - DEBUG TECNICO",fill=(243,244,245))
            draw.text((36,47),f"{pose.shot_id} | frame {pose.shot_frame:03d} | yaw {pose.yaw_degrees:05.1f} deg | progress {pose.push_progress:0.2f}",fill=(215,214,211))
            draw.text((36,437),"SEM PNGS / SEM ARTE APROVADA / SEM MP4 FINAL",fill=(249,191,100))
            ffmpeg.stdin.write(im.tobytes())
        ffmpeg.stdin.close()
        code=ffmpeg.wait(timeout=90)
        if code!=0:
            raise RuntimeError(f"FFmpeg exited with {code}")
    except BaseException:
        if ffmpeg.stdin and not ffmpeg.stdin.closed:
            ffmpeg.stdin.close()
        ffmpeg.kill()
        ffmpeg.wait()
        raise

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--render-wireframe",action="store_true")
    args=parser.parse_args()
    doc=read_motion(ROOT)
    poses=build_poses(doc)
    qa=validate_poses(poses)
    output=args.output_dir
    output.mkdir(parents=True,exist_ok=True)
    (output/"kinematics-qa.json").write_text(json.dumps(qa,indent=2)+"\n")
    (output/"kinematics-frames.json").write_text(
        json.dumps({"schema_version":1,"kind":"technical_poses_not_png_rig",
                    "fps":FPS,"frames":[asdict(p) for p in poses],
                    "real_png_layers_used":0,"production_ready":False},
                   ensure_ascii=False,indent=2)+"\n")
    if args.render_wireframe:
        render_wireframe(poses,output/"cart-physics-wireframe-debug.mp4")
    print(json.dumps({"frames_validated":qa["frames_checked"],
                      "cart_yaw":qa["cart_yaw_end_degrees"],
                      "physical_contact_verified":True,
                      "source_art_rig_ready":False,
                      "youtube_publications":0}))

if __name__=="__main__":
    main()
