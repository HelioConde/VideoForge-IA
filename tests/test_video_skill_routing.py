"""Static regression checks for the six VideoForge skill disciplines.

No media generation, network/API calls, agent spawning or render.
"""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLROOT = ROOT / ".agents" / "skills"
ROLE_SKILLS = {
    "arte_e_camadas": ["videoforge-animation-parts"],
    "rig_e_animacao": ["videoforge-rig-2d-three", "videoforge-character-acting"],
    "qa_independente": ["videoforge-qa-and-checkpoint"],
    "direcao_tomadas": ["videoforge-shot-direction"],
    "audio_montagem": ["videoforge-audio-editing"],
    "pesquisa_tecnica": ["videoforge-technical-research"],
}
COORDINATOR = "videoforge-dorama-remake"


class VideoForgeSkillRoutingTests(unittest.TestCase):
    def test_all_eight_skills_have_discoverable_frontmatter(self):
        expected = {COORDINATOR} | {s for values in ROLE_SKILLS.values() for s in values}
        installed = {p.parent.name for p in SKILLROOT.glob("*/SKILL.md")}
        self.assertEqual(installed, expected)
        for ident in sorted(expected):
            with self.subTest(skill=ident):
                path = SKILLROOT / ident / "SKILL.md"
                data = path.read_text(encoding="utf-8")
                self.assertTrue(data.startswith("---\n"), ident)
                front = data.split("---", 2)[1]
                self.assertIn("name: " + ident, front)
                self.assertRegex(front, r"(?m)^description: .+")

    def test_routing_links_are_real_and_local(self):
        source = (SKILLROOT / COORDINATOR / "SKILL.md").read_text(encoding="utf-8")
        for skills in ROLE_SKILLS.values():
            for ident in skills:
                with self.subTest(skill=ident):
                    self.assertIn("../" + ident + "/SKILL.md", source)
                    self.assertTrue((SKILLROOT / ident / "SKILL.md").is_file())

    def test_proxy_and_remotion_constraints_are_explicit(self):
        parts = (SKILLROOT / "videoforge-animation-parts" / "SKILL.md").read_text()
        rig = (SKILLROOT / "videoforge-rig-2d-three" / "SKILL.md").read_text()
        research = (SKILLROOT / "videoforge-technical-research" / "SKILL.md").read_text()
        coord = (SKILLROOT / COORDINATOR / "SKILL.md").read_text()
        self.assertIn("proxy_generated_separate_image", parts)
        self.assertIn("useCurrentFrame", rig + research)
        self.assertIn("useFrame()", research)
        self.assertIn("não criar a arte animável por recortes locais", coord.lower())
        self.assertIn("AGPL-3.0", research)
        self.assertIn("apenas", research.lower())

    def test_technical_catalog_and_roles_documented(self):
        doc=(ROOT/"docs"/"BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md").read_text()
        self.assertIn("Atualização de skills por especialidade", doc)
        for ident in {COORDINATOR} | {i for xs in ROLE_SKILLS.values() for i in xs}:
            self.assertIn(ident, doc)


if __name__ == "__main__":
    unittest.main()
