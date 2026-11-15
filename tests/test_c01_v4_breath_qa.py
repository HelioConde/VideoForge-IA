"""Regression: approved mother restores king+spears, only Kael breathes.

Tests use in-memory synthetic pixels and do not create or regenerate art.
"""
import copy
import unittest

from videoforge.directed_rig import (
    DirectedRigError, _static_mother_with_kael_cutout,
)
from videoforge.c01_v4_breath_qa import (
    C01BreathQAError, validate_c01_v4_pose,
    changed_pixels_in_source_region,
)


W,H=1024,1536


def joint(id,parent=None,mesh=None):
    node={"id":id,"parent":parent,"role":"part" if mesh else "joint","z":0}
    if mesh is not None:
        node["mesh"]={"amplitudePx":mesh}
    return node


def shot_fixture():
    nodes=[
        joint("kael.ombros"),joint("kael.cabeca","kael.ombros"),
        joint("kael.braco-direito"),joint("kael.antebraco","kael.braco-direito"),
        joint("kael.punhos","kael.antebraco"),
        joint("kael.braco-esquerdo"),joint("kael.perna-direita"),
        joint("kael.bota-direita","kael.perna-direita"),
        joint("kael.cabelo","kael.cabeca",.45),
        joint("kael.jaqueta","kael.ombros",.55),
    ]
    tracks=[
        {"target":"kael.ombros","transform":"translateY",
         "keyframes":[{"frame":150,"value":0},{"frame":180,"value":-1.25}]},
        {"target":"kael.cabeca","transform":"rotationZ",
         "keyframes":[{"frame":150,"value":0},{"frame":180,"value":-.32}]},
    ]
    return {"id":"C01-P03","canvas":{"width":W,"height":H},
      "nodes":nodes,"tracks":tracks,
      "camera":{"type":"perspective_3d","move":"locked",
        "keyframes":[{"frame":150,"z":14,"fovDeg":30,"lookAt":[0,0,0]}]}}


def static_fixture():
    return {"schema":"videoforge/c01-static-context-original-mother/v1",
       "king_and_spears":{k:{"changed_from_original":0}
       for k in ("aldric_crown_face","left_spear_upper","right_spear_upper")}}


class C01V4PoseTest(unittest.TestCase):
    def test_breathing_v4_locks_all_contacts(self):
        r=validate_c01_v4_pose(shot_fixture(),static_fixture())
        self.assertEqual(r["animated_tracks"],2)
        self.assertTrue(r["right_leg_boot_fixed"])
        self.assertFalse(r["human_visual_approved"])

    def test_wrong_arm_parent_rejected_even_without_arm_tracks(self):
        s=shot_fixture()
        next(n for n in s["nodes"] if n["id"]=="kael.braco-direito")["parent"]="kael.ombros"
        with self.assertRaisesRegex(C01BreathQAError,"WORLD_ANCHORED"):
            validate_c01_v4_pose(s,static_fixture())

    def test_wrist_or_boot_motion_rejected(self):
        for target in ("kael.punhos","kael.bota-direita"):
            s=shot_fixture()
            s["tracks"].append({"target":target,"transform":"rotationZ",
                                "keyframes":[{"frame":150,"value":0}]})
            with self.subTest(target=target),self.assertRaisesRegex(
                    C01BreathQAError,"ONLY_SHOULDER_BREATH"):
                validate_c01_v4_pose(s,static_fixture())

    def test_excessive_head_and_duplicate_spears_rejected(self):
        s=shot_fixture()
        s["tracks"][1]["keyframes"][1]["value"]=2.0
        with self.assertRaisesRegex(C01BreathQAError,"EXCESS_BREATHING"):
            validate_c01_v4_pose(s,static_fixture())
        s=shot_fixture()
        s["nodes"].append({"id":"lanca-contexto-0","role":"static-context"})
        with self.assertRaisesRegex(C01BreathQAError,"STATIC_CANDIDATES"):
            validate_c01_v4_pose(s,static_fixture())

    def test_rejected_broken_original_crown(self):
        c=static_fixture()
        c["king_and_spears"]["aldric_crown_face"]["changed_from_original"]=12
        with self.assertRaisesRegex(C01BreathQAError,"KING_SPEARS"):
            validate_c01_v4_pose(shot_fixture(),c)


class C01V4OriginalMotherTest(unittest.TestCase):
    def test_only_actor_region_replaced_and_entire_king_original(self):
        mother=bytearray(bytes([110,40,45,255])*(W*H))
        other=bytearray(bytes([4,5,6,255])*(W*H))
        nodes=[]
        pixels={}
        for idx in range(10):
            x,y=410+idx*6,925
            id=f"kael.part-{idx}"
            nodes.append({"id":id,"role":"part","file":f"part-{idx}.png",
                          "bbox":[x,y,5,5]})
            b=bytearray(W*H*4)
            for yy in range(y,y+5):
                for xx in range(x,x+5):
                    i=4*(yy*W+xx)
                    b[i:i+4]=bytes([110,40,45,255])
            pixels[id]=b
        result,report=_static_mother_with_kael_cutout(
            mother,other,{"width":W,"height":H},nodes,pixels,radius=3)
        self.assertEqual(result[4*(319*W+530):4*(319*W+530)+4],
                         mother[4*(319*W+530):4*(319*W+530)+4])
        self.assertEqual(result[4*(927*W+412):4*(927*W+412)+4],
                         other[4*(927*W+412):4*(927*W+412)+4])
        self.assertEqual(report["new_pixels_generated"],0)
        self.assertEqual(report["king_and_spears"]["aldric_crown_face"]["changed_from_original"],0)
        self.assertEqual(report["source_actor_layers"],10)

    def test_crown_actor_mask_overlap_is_forbidden(self):
        mother=bytearray(bytes([110,40,45,255])*(W*H))
        other=bytearray(bytes([4,5,6,255])*(W*H))
        nodes=[]
        pixels={}
        for idx in range(10):
            x,y=500+idx*5,310
            id=f"kael.part-{idx}"
            nodes.append({"id":id,"role":"part","file":"pixel.png",
                          "bbox":[x,y,4,4]})
            b=bytearray(W*H*4)
            b[4*(y*W+x)+3]=255
            pixels[id]=b
        with self.assertRaisesRegex(DirectedRigError,"KING_OR_SPEAR_OVERLAP"):
            _static_mother_with_kael_cutout(
                mother,other,{"width":W,"height":H},nodes,pixels,radius=3)

    def test_static_region_h264_frame_pixel_delta(self):
        s=shot_fixture()
        a=bytearray(W*H*4)
        b=bytearray(a)
        x,y=530,300
        b[(y*W+x)*4:(y*W+x)*4+4]=bytes([80,0,0,255])
        count=changed_pixels_in_source_region(a,b,s,W,H,
                    (458,260,131,140),rgb_delta=24)
        self.assertGreater(count,0)


if __name__ == "__main__":
    unittest.main()
