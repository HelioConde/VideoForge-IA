"""Checks rápidos do piloto Spy x Family sem gerar mídia."""
import unittest
import copy
import json
import tempfile
from unittest.mock import patch
from pathlib import Path

from videoforge import spy_family_pilot as pilot


class SpyFamilyPilotTests(unittest.TestCase):
    def test_storyboard_scene_count_is_story_driven_and_channel_safe(self):
        story = pilot.load_storyboard()
        self.assertEqual(story["channel"], "otaku-br")
        self.assertGreater(len(story["scenes"]), 10)
        self.assertEqual([x["number"] for x in story["scenes"]], list(range(1,len(story["scenes"])+1)))
        self.assertFalse(story["youtube_upload"])
        self.assertEqual(story["source"]["item_id"], "5027-spy-x-family")

    def test_narration_has_meaningful_ptbr_story_not_a_stub(self):
        data = pilot.load_storyboard()
        text = " ".join(x["narration"] for x in data["scenes"]).lower()
        for marker in ("loid", "yor", "anya", "família", "segredo"):
            self.assertIn(marker, text)
        self.assertGreaterEqual(len(text.split()), 180)
        self.assertLessEqual(len(text.split()), 450)

    def test_storyboard_accepts_30_scenes_without_fixed_limit(self):
        source = pilot.load_storyboard()
        with tempfile.TemporaryDirectory() as tmp:
            draft = copy.deepcopy(source)
            draft["scenes"] = []
            manifest = {"schema": "videoforge/mvp/v1", "channel": "otaku-br",
                        "modelo": "imagem-estatica", "youtube_upload": False,
                        "scenes": []}
            for i in range(1, 31):
                item = copy.deepcopy(source["scenes"][(i-1) % len(source["scenes"])])
                item.update(number=i, id=f"scene-{i}",
                            image=f"imagens/cena-{i:02d}.png",
                            audio=f"voz/cena-{i:02d}.wav")
                draft["scenes"].append(item)
                manifest["scenes"].append({
                    "image": item["image"], "audio": item["audio"],
                    "caption": item["caption"]})
            path = Path(tmp)
            (path / "story.json").write_text(json.dumps(draft),encoding="utf-8")
            (path / "video.json").write_text(json.dumps(manifest),encoding="utf-8")
            with patch.object(pilot, "STORYBOARD", path / "story.json"), \
                 patch.object(pilot, "MANIFEST", path / "video.json"):
                result = pilot.load_storyboard()
            self.assertEqual(len(result["scenes"]), 30)

    def test_assets_are_channel_local_and_nonexisting_in_git(self):
        data = pilot.load_storyboard()
        for scene in data["scenes"]:
            for key, stem in (("image", "imagens/"), ("audio", "voz/")):
                self.assertTrue(scene[key].startswith(stem))
                self.assertNotIn("..", Path(scene[key]).parts)
                self.assertFalse((pilot.FOLDER / scene[key]).is_file())


if __name__ == "__main__":
    unittest.main()
