"""Canonical user research manual must be the highest animation rule."""
import json
import shutil
import tempfile
from pathlib import Path
import unittest

from videoforge.animation_manual import ROOT,MANUAL_REL,enforce_animation_manual
from videoforge.errors import VideoForgeError
from videoforge.rig_three_art import load_plan,PARTS


class AnimationManualTests(unittest.TestCase):
    def test_real_repo_and_priority(self):
        result=enforce_animation_manual()
        self.assertEqual(result["manual"],MANUAL_REL)
        self.assertFalse(result["allows_flat_png_as_official"])
        self.assertTrue(result["user_visual_review_required"])

    def test_actual_channel_art_plan_uses_same_original_and_limited_edits(self):
        d=load_plan("otaku-br","spy-x-family-familia-de-mentira")
        self.assertEqual([x["id"] for x in d["steps"]],list(PARTS))
        self.assertEqual(d["max_new_image_calls"],2)
        self.assertEqual(d["reference_file"],"character-main.png")
        self.assertFalse(d["retry_on_429"])
        self.assertTrue(all("mesma" in x["prompt"].lower() or
                            "imagem" in x["prompt"].lower() for x in d["steps"]))
        self.assertFalse(d["humanReview"]["roundTripComposition"])

    def test_missing_manual_is_fatal(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(VideoForgeError,"ANIMATION_MANUAL_MISSING"):
                enforce_animation_manual(Path(td))

    def test_cannot_mark_pending_rig_as_operational(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            (folder/"docs").mkdir()
            (folder/"modelos"/"camadas-animadas").mkdir(parents=True)
            shutil.copy(ROOT/MANUAL_REL,folder/MANUAL_REL)
            for name in ("AGENTS.md","README.md"):
                (folder/name).write_text(MANUAL_REL,encoding="utf-8")
            m=json.loads((ROOT/"modelos/camadas-animadas/modelo.json").read_text(encoding="utf-8"))
            m["operacional"]=True
            (folder/"modelos/camadas-animadas/modelo.json").write_text(json.dumps(m),encoding="utf-8")
            with self.assertRaisesRegex(VideoForgeError,"ANIMATION_MANUAL_MODEL_POLICY_INVALID"):
                enforce_animation_manual(folder)


if __name__=="__main__":
    unittest.main()
