"""40 tomadas têm cena-mãe única, RGBA e câmera, nunca fila de poses."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from videoforge.layered_shot_plan import REL, validate
from videoforge.errors import VideoForgeError


class LayeredCameraPlanTests(unittest.TestCase):
    def test_all_40_shots_and_three_camera_supplements(self):
        result = validate()
        self.assertEqual(result["shot_count"], 40)
        self.assertEqual(result["shot_mothers_to_generate"], 39)
        self.assertEqual(result["predefined_camera_shots"], 37)
        self.assertEqual(result["additional_camera_shots"],
                         ["C01-P05", "C08-P04", "C12-P04"])
        self.assertFalse(result["pose_images_required"])
        self.assertFalse(result["youtube_uploaded"])
        self.assertEqual(result["image_provider_calls"], 0)

    def test_all_nonblack_shots_share_mother_layer_source(self):
        from videoforge.layered_shot_plan import ROOT
        path = ROOT / REL / "PLANO-CAMADAS-CAMERA-EP01.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for shot in data["shots"]:
            if shot["id"] == "C01-P01":
                self.assertTrue(shot["images"]["no_generation"])
                continue
            with self.subTest(shot=shot["id"]):
                self.assertEqual(shot["images"]["background"]["source"], "scene-mother")
                self.assertTrue(all(x["source"] == "scene-mother"
                                    for x in shot["images"]["characters"]))
                self.assertTrue(all(x["source"] == "scene-mother"
                                    for x in shot["images"]["objects"]))
                self.assertFalse(shot["rig"]["independent_pose_image_required"])
                self.assertTrue(shot["qa"]["compare_composite_to_alpha_recomposition"])

    def test_reject_independent_pose_requirement(self):
        import copy
        from videoforge.layered_shot_plan import ROOT
        path = ROOT / REL / "PLANO-CAMADAS-CAMERA-EP01.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = copy.deepcopy(data)
        changed["shots"][3]["rig"]["independent_pose_image_required"] = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("PLANO-CAMADAS-CAMERA-EP01.json", "roteiro.json",
                         "direcao-cinematografica-planos.json"):
                src = ROOT / REL / name
                dest = root / REL / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(src.read_bytes())
            queue_src = ROOT / "canal/alchemy-lab/biblia-visual/FILA-EP01.json"
            queue_dest = root / "canal/alchemy-lab/biblia-visual/FILA-EP01.json"
            queue_dest.parent.mkdir(parents=True, exist_ok=True)
            queue_dest.write_bytes(queue_src.read_bytes())
            target = root / REL / "PLANO-CAMADAS-CAMERA-EP01.json"
            target.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"LAYERED_PLAN_MOTHER_FIRST_INVALID"):
                validate(root)

    def test_camera_focals_cover_multiple_subjects(self):
        from videoforge.layered_shot_plan import ROOT
        doc = json.loads((ROOT / REL / "PLANO-CAMADAS-CAMERA-EP01.json").read_text())
        self.assertGreaterEqual(len({s["camera"]["primary_focus"] for s in doc["shots"]}), 8)
        self.assertTrue(any(s["camera"]["virtual_motion"] == "occlusion_reveal" for s in doc["shots"]))
        self.assertTrue(any(s["camera"]["virtual_motion"] == "slow_dolly_out_with_parallax"
                            for s in doc["shots"]))


if __name__ == "__main__":
    unittest.main()
