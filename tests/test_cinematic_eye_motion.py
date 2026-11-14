"""Independent eyes QA; all "approved" data below are in-memory fixtures only.

No real source art is created, no images generated and no rig is approved.
"""
from __future__ import annotations
import copy
from pathlib import Path
import unittest

from videoforge.cinematic_eye_motion import (
    check_eye_performance,validate_draft_plan,EXPECTED_PUPILS,
    EXPECTED_LIDS,QA_FLAGS,EYE_LAYER_IDS,
)
from videoforge.errors import VideoForgeError

EP=Path(__file__).resolve().parents[1]/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"

def synthetic_candidate():
    eye={
        "actorId":"kael","pupilLayerIds":["pupil-left","pupil-right"],
        "eyelidLayerIds":["eyelid-left","eyelid-right"],
        "eyeUnderlaysVerified":True,"pupilMasksVerified":True,
        "noDuplicatePaintedPupilsInHead":True,
        "rotationOrTranslationClippingQA":True,
        "gazePupilMaxPx":12,"eyelidMaxPx":1,
        "humanVisualApproved":True,
    }
    r={
        "performance":{
            "mode":"pupils_only_locked_head","actorId":"kael",
            "pupilKeyframes":copy.deepcopy(EXPECTED_PUPILS),
            "eyelidKeyframes":copy.deepcopy(EXPECTED_LIDS),
            "headRotationDeg":0,"bodyMotionEnabled":False,
            "cameraLocked":True,"humanMotionApproved":True,
        },
        "actors":[{"id":"kael","rig":{
            "headMaxRotationDeg":0,"blinkFrames":[],
            "eyeRig":eye,
            "layers":[{"id":i} for i in sorted(EYE_LAYER_IDS)],
        }}],
    }
    qa={k:True for k in QA_FLAGS}
    qa["qa_frames"]=[3990,3994,4076,4109]
    return r,qa

class IndependentPupilTests(unittest.TestCase):
    def test_real_plan_is_draft_and_unapproved(self):
        data=validate_draft_plan(EP)
        self.assertFalse(data["performance"]["humanMotionApproved"])
        self.assertFalse(data["qa_required"]["human_visual_approved"])
        self.assertFalse(data["production_gates"]["official_render_allowed"])
        self.assertEqual(data["frames"]["global_start"],3990)
        self.assertEqual(data["frames"]["global_end_exclusive"],4110)

    def test_fully_approved_synthetic_contract_is_structurally_valid(self):
        rig,qa=synthetic_candidate()
        self.assertEqual(check_eye_performance("C12-P01",rig,qa),rig["performance"])

    def test_wrong_pupil_distance_cannot_pass(self):
        rig,qa=synthetic_candidate()
        rig["performance"]["pupilKeyframes"][2]["value"]=14
        with self.assertRaisesRegex(VideoForgeError,"DIRECTION_MISMATCH"):
            check_eye_performance("C12-P01",rig,qa)

    def test_unmeasured_underlay_and_unpainted_sclera_block(self):
        rig,qa=synthetic_candidate()
        rig["actors"][0]["rig"]["eyeRig"]["eyeUnderlaysVerified"]=False
        with self.assertRaisesRegex(VideoForgeError,"EYE_RIG_QA_INVALID"):
            check_eye_performance("C12-P01",rig,qa)
        rig,qa=synthetic_candidate()
        qa["no_duplicate_pupils_in_head_verified"]=False
        with self.assertRaisesRegex(VideoForgeError,"HUMAN_EYE_QA_MISSING"):
            check_eye_performance("C12-P01",rig,qa)

    def test_any_head_rotation_or_blink_invalid(self):
        rig,qa=synthetic_candidate()
        rig["actors"][0]["rig"]["headMaxRotationDeg"]=1
        with self.assertRaisesRegex(VideoForgeError,"HEAD_OR_BLINK_NOT_FROZEN"):
            check_eye_performance("C12-P01",rig,qa)
        rig,qa=synthetic_candidate()
        rig["actors"][0]["rig"]["blinkFrames"]=[30]
        with self.assertRaisesRegex(VideoForgeError,"HEAD_OR_BLINK_NOT_FROZEN"):
            check_eye_performance("C12-P01",rig,qa)

    def test_missing_pupil_or_review_frame_rejected(self):
        rig,qa=synthetic_candidate()
        rig["actors"][0]["rig"]["layers"].pop()
        with self.assertRaisesRegex(VideoForgeError,"INDEPENDENT_PUPILS_MISSING"):
            check_eye_performance("C12-P01",rig,qa)
        rig,qa=synthetic_candidate()
        qa["qa_frames"]=[3990,4109]
        with self.assertRaisesRegex(VideoForgeError,"KEYFRAME_QA_MISSING"):
            check_eye_performance("C12-P01",rig,qa)

if __name__=="__main__":
    unittest.main()
