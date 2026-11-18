"""Deterministic full-frame kinematic QA; never claim debug rig is real art."""
import copy
import math
import unittest
from dataclasses import replace

from videoforge.ep01_continuity_motion import read
from videoforge.ep01_cart_kinematics import (
    CART_WIDTH_M, FPS, HALF_WHEEL_TRACK_M, HOLD_FRAME_COUNT, SOURCE_FRAME_COUNT,
    WHEEL_RADIUS_M, build_poses, validate_poses, distance, interpolate_keys,
)


class CartKinematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read()

    def test_240_frames_real_contact_and_continuous_90_degree_cut(self):
        frames = build_poses(self.plan)
        self.assertEqual(len(frames), 240)
        self.assertEqual([f.frame for f in frames], list(range(240)))
        self.assertEqual(frames[0].yaw_degrees, 0)
        self.assertEqual(frames[129].yaw_degrees, 90)
        self.assertEqual(frames[130].yaw_degrees, 90)
        self.assertEqual(frames[239].yaw_degrees, 90)
        self.assertEqual(frames[129].cart_center, frames[130].cart_center)
        self.assertEqual(frames[129].grip, frames[130].grip)
        self.assertEqual(frames[129].wheel_left_rotation, frames[130].wheel_left_rotation)
        self.assertEqual(frames[129].wheel_right_rotation, frames[130].wheel_right_rotation)
        self.assertGreater(distance(frames[0].cart_center,frames[129].cart_center),0.65)
        qa = validate_poses(frames)
        self.assertEqual(qa["frames_checked"],240)
        self.assertTrue(qa["continuous_cut"])
        self.assertEqual(qa["source_png_transforms"],0)
        self.assertEqual(qa["sprite_layers_loaded"],0)
        self.assertFalse(qa["visual_art_approved"])
        self.assertFalse(qa["rig_with_real_assets_approved"])
        self.assertFalse(qa["full_animation_approved"])
        self.assertEqual(qa["youtube_publications"],0)

    def test_kael_contact_and_both_wheels_are_connected_every_frame(self):
        frames = build_poses(self.plan)
        for p in frames:
            with self.subTest(frame=p.frame):
                self.assertLess(p.grip_connection_error_m,1e-8)
                self.assertLess(p.wheel_contact_slip_m,1e-8)
                self.assertAlmostEqual(
                    distance(p.wheel_left_center,p.wheel_right_center),
                    2*HALF_WHEEL_TRACK_M,places=7)
                self.assertLess(distance(p.grip,p.kael_body_center),0.85)
                if p.shot_id=="C08-P02":
                    self.assertFalse(p.chasers)
                else:
                    self.assertEqual(len(p.chasers),2)

    def test_pivot_and_wheels_have_true_differential_rotation(self):
        frames = build_poses(self.plan)
        a,b=frames[0],frames[129]
        self.assertGreater(b.wheel_left_rotation,0)
        self.assertNotAlmostEqual(b.wheel_left_rotation,b.wheel_right_rotation)
        self.assertAlmostEqual(
            (b.wheel_left_rotation-b.wheel_right_rotation)*WHEEL_RADIUS_M,
            2*HALF_WHEEL_TRACK_M*math.radians(90),places=5)
        self.assertEqual(frames[130].wheel_left_rotation,frames[239].wheel_left_rotation)
        self.assertEqual(frames[130].wheel_right_rotation,frames[239].wheel_right_rotation)

    def test_unapproved_art_must_not_be_silently_promoted(self):
        mutations=[
            lambda p: p["QA"].update(rig_ready=True),
            lambda p: p["QA"].update(art_approval=True),
            lambda p: p["rules"].update(never_use_full_png_as_rig=False),
            lambda p: p["rules"].update(independent_hands=True),
            lambda p: p["rules"].update(allow_image_generation=True),
            lambda p: p["rules"].update(allow_publish=True),
            lambda p: p["shots"][1].update(cast_present=["kael","pursuer_1"]),
            lambda p: p["shots"][2].update(cart_yaw_degrees=0),
        ]
        for i,mutation in enumerate(mutations):
            plan=copy.deepcopy(self.plan)
            mutation(plan)
            with self.subTest(i=i),self.assertRaises(ValueError):
                build_poses(plan)

    def test_source_keyframes_change_without_approval_is_rejected(self):
        plan=copy.deepcopy(self.plan)
        plan["shots"][1]["frames"][-1]["cart_yaw_degrees"]=35
        with self.assertRaises(ValueError):
            build_poses(plan)

    def test_frame_teleport_and_floating_contact_are_detected(self):
        frames=build_poses(self.plan)
        relocated=list(frames)
        relocated[63]=replace(relocated[63],cart_center=(100.0,100.0))
        with self.assertRaises(ValueError):
            validate_poses(relocated)
        detached=list(frames)
        detached[84]=replace(detached[84],grip_connection_error_m=0.2)
        with self.assertRaises(ValueError):
            validate_poses(detached)
        snap=list(frames)
        snap[130]=replace(snap[130],yaw_degrees=80.)
        with self.assertRaises(ValueError):
            validate_poses(snap)
        chaser=list(frames)
        chaser[6]=replace(chaser[6],chasers=((-1.0,0.1),))
        with self.assertRaises(ValueError):
            validate_poses(chaser)

    def test_no_shot_before_or_after_pivot_can_be_faked(self):
        keys=self.plan["shots"][1]["frames"]
        for frame in (-1, SOURCE_FRAME_COUNT):
            with self.assertRaises(ValueError):
                interpolate_keys(keys,frame)


if __name__=="__main__":
    unittest.main()
