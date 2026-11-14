"""Testes de integridade da seleção de assets C01, sem gerar imagens."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import unittest

BASE=Path(__file__).resolve().parents[1]/"canal"/"alchemy-lab"/"videos"/"mmorpg-conquiste-a-princesa-ep01"

def png_fields(path:Path):
    raw=path.read_bytes()
    if raw[:8]!=bytes((137,80,78,71,13,10,26,10)) or raw[12:16]!=b"IHDR":
        raise ValueError("not PNG")
    return hashlib.sha256(raw).hexdigest(), struct.unpack(">II",raw[16:24])

class AlchemyAssetSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((BASE/"rig-selecao-artes-c01.json").read_text(encoding="utf8"))

    def test_lock_and_status(self):
        doc=self.doc
        self.assertEqual(doc["schema"],"videoforge/alchemy-episode-scene1-preferred-assets/v1")
        self.assertTrue((BASE/doc["noImageGenerationLock"]).is_file())
        self.assertEqual(doc["newImageGenerationCallsThisStage"],0)
        self.assertFalse(doc["productionGates"]["renderOfficialAllowed"])
        self.assertFalse(doc["productionGates"]["visualQA"])
        self.assertFalse(doc["productionGates"]["hiddenAnatomyReconstructed"])

    def test_source_and_preferred_sprites_match_exact_sha(self):
        chosen=self.doc["preferredAssets"]
        items=[self.doc["sourceMother"], chosen["kael"], chosen["aldric"]]
        items+=chosen["guards"]+chosen["spears"]
        self.assertEqual(len(items),7)
        for item in items:
            with self.subTest(path=item["path"]):
                rel=item["path"]
                self.assertFalse(Path(rel).is_absolute())
                self.assertNotIn("..",Path(rel).parts)
                p=BASE/rel
                self.assertTrue(p.is_file())
                self.assertFalse(p.is_symlink())
                sha, size=png_fields(p)
                self.assertEqual(sha,item["sha256"])
                self.assertEqual(size,(1024,1536))

    def test_legacy_kael_and_rejected_groups_not_primary(self):
        chosen=self.doc["preferredAssets"]
        deprecated={x["path"] for x in self.doc["deprecated"]}
        self.assertNotIn(chosen["kael"]["path"],deprecated)
        self.assertNotIn(chosen["aldric"]["path"],deprecated)
        for name in ("kael","aldric"):
            self.assertFalse(chosen[name]["approval"])
        self.assertTrue(all(not guard["rigReady"] for guard in chosen["guards"]))
        self.assertTrue(all(not spear["underlaysReady"] for spear in chosen["spears"]))

    def test_variants_derive_from_existing_pixels(self):
        for g in self.doc["preferredAssets"]["guards"]:
            with self.subTest(guard=g["id"]):
                p=BASE/g["withoutSpearVariant"]
                self.assertEqual(png_fields(p)[0],g["withoutSpearSHA256"])
                self.assertEqual(g["sourceRGB"] if "sourceRGB" in g else g["colors"],
                                 "pixel_from_mother_RGB")

if __name__=="__main__":
    unittest.main()
