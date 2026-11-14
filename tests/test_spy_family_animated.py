"""Contrato do render animado de Spy x Family sem limite fixo de cenas."""
import copy
import unittest

from videoforge import spy_family_animated as animated
from videoforge import spy_family_pilot as pilot
from videoforge.errors import VideoForgeError


class SpyFamilyAnimatedTests(unittest.TestCase):
    def test_prepare_props_from_all_storyboard_scenes(self):
        story=pilot.load_storyboard()
        count=len(story["scenes"])
        props=animated.props_from_storyboard(story,[6.5]*count)
        self.assertEqual(len(props["scenes"]),count)
        self.assertEqual(props["totalFrames"],count*195)
        self.assertTrue(props["draftPreview"])
        self.assertEqual(props["channel"],"otaku-br")
        self.assertEqual(props["scenes"][0]["focus"],"anya")
        self.assertEqual(props["scenes"][1]["setting"],"office")

    def test_animation_storyboard_accepts_many_scenes(self):
        original=pilot.load_storyboard()
        story=copy.deepcopy(original)
        story["scenes"]=[]
        for i in range(80):
            scene=copy.deepcopy(original["scenes"][i%len(original["scenes"])])
            scene["id"]=f"micro-cena-{i:02d}"
            scene["number"]=i+1
            story["scenes"].append(scene)
        props=animated.props_from_storyboard(story,[1.2]*80)
        self.assertEqual(len(props["scenes"]),80)
        self.assertEqual(props["totalFrames"],80*36)

    def test_zero_negative_durations_rejected(self):
        story=pilot.load_storyboard()
        with self.assertRaisesRegex(VideoForgeError,"SPY_ANIMATED_DURATION_INVALID"):
            animated.props_from_storyboard(story,[0.0]*len(story["scenes"]))

    def test_missing_durations_rejected(self):
        story=pilot.load_storyboard()
        with self.assertRaisesRegex(VideoForgeError,"SPY_ANIMATED_DURATION_MISMATCH"):
            animated.props_from_storyboard(story,[5.0])

if __name__=="__main__":
    unittest.main()
