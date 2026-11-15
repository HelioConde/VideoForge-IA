"""C12 contract tests which pass without inventing missing PNGs."""
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from videoforge import c12_technical_preview as preview
from videoforge.c12_technical_preview import (
    AssetGateError, EP, PART_SHAS, SHOT_PARTS,
    bbox, plan, policy, required_files,
)

class C12TechnicalTest(unittest.TestCase):
    def test_failed_preflight_invalidates_previous_render_props(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out/'props.json').write_text('{"sourceOriginalsArchived":true}')
            with patch.object(preview, 'policy', side_effect=AssetGateError('MISSING_SOURCE')):
                self.assertEqual(preview.prepare(out), 2)
            self.assertFalse((out/'props.json').exists())
            report = json.loads((out/'preflight.qa.json').read_text(encoding='utf8'))
            self.assertEqual(report['status'], 'ASSETS_PENDING')
            self.assertFalse(report['official_video_approved'])

    def test_exact_five_meshes_with_512_triangles(self):
        p=plan()
        self.assertEqual({m["id"] for m in p["meshParts"]},set(PART_SHAS))
        self.assertEqual(sum(2*m["rows"]*m["columns"] for m in p["meshParts"]),512)
        self.assertEqual(len(SHOT_PARTS["C12-P03"]),4)

    def test_native_crop_bounds(self):
        for m in plan()["meshParts"]:
            x,y,w,h=bbox(m["polygon"])
            self.assertGreater(w,0)
            self.assertGreater(h,0)
            self.assertLessEqual(x+w,941)
            self.assertLessEqual(y+h,1672)

    def test_two_mothers_two_underlays_five_rgba_exact_sources(self):
        entries=required_files(plan())
        self.assertEqual(len(entries),9)
        self.assertEqual(len({item[-1] for item in entries}),9)
        self.assertTrue(all(str(path).startswith(str(EP)) and len(sha)==64
                            for path,sha,*_ in entries))

    def test_unapproved_status_and_no_new_images(self):
        policy()
        p=plan()
        self.assertFalse(p["official_render_allowed"])
        self.assertFalse(p["three_js_remotion_full_rig_ready"])
        self.assertEqual(p["external_image_generation_calls"],0)

    def test_invalid_crop_fails_closed(self):
        with self.assertRaises(AssetGateError):
            bbox([[0,0],[950,25]])

if __name__=="__main__":
    unittest.main()
