"""QA do recortador de pixels existentes: nenhum modelo de imagem utilizado."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = ImageDraw = None
from videoforge.split_existing_png_parts import split_existing, SplitError

@unittest.skipUnless(Image is not None, "Pillow não instalado neste runner de testes")
class ExistingPixelSplitTests(unittest.TestCase):
    def setup_fixture(self, folder):
        source=folder/"source.png"
        src=Image.new("RGB",(1024,1536),(18,23,38))
        d=ImageDraw.Draw(src)
        d.line([(810,330),(60,1100)],fill=(225,206,177),width=11)
        d.line([(210,330),(990,1110)],fill=(185,184,192),width=12)
        src.save(source)
        doc={
            "schema":"videoforge/existing-pixel-partition/v1",
            "channel":"alchemy-lab",
            "video_id":"mmorpg-conquiste-a-princesa-ep01",
            "scene":"cena-01",
            "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "no_generation":True,
            "human_visual_approval":False,
            "allow_opaque_scene_mother":True,
            "layers":[
                {"id":"lanca-l","kind":"stroke",
                 "points":[[810,330],[510,645],[60,1100]],"width_px":11,
                 "head_polygon":[[810,310],[825,340],[792,350]],
                 "pivot_xy":[385,760]},
                {"id":"lanca-r","kind":"stroke",
                 "points":[[210,330],[515,650],[990,1110]],"width_px":11,
                 "butt_polygon":[[990,1110],[970,1100],[980,1092]],
                 "pivot_xy":[640,760]},
                {"id":"resto-REJECTED","kind":"remainder","qa_status":"rejected"}
            ]
        }
        plan=folder/"plan.json"
        plan.write_text(json.dumps(doc),encoding="utf8")
        return source,plan

    def test_rgb_cena_mae_split_exact_no_generated_pixels(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source,plan=self.setup_fixture(root)
            dst=root/"sprites"
            qa=split_existing(source,plan,dst)
            self.assertEqual(qa["piece_count"],3)
            self.assertTrue(qa["neutral_roundtrip_pixel_exact"])
            self.assertEqual(qa["source_pixels_created_or_painted"],0)
            self.assertFalse(qa["human_visual_approval"])
            self.assertEqual(qa["actual_rig"],"pending")
            for name in ("lanca-l.png","lanca-r.png","resto-REJECTED.png"):
                result=Image.open(dst/name)
                self.assertEqual(result.mode,"RGBA")
                self.assertEqual(result.size,(1024,1536))
                self.assertIsNotNone(result.getbbox())

    def test_source_sha_mismatch_blocks_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);src,plan=self.setup_fixture(root)
            doc=json.loads(plan.read_text());doc["source_sha256"]="0"*64
            plan.write_text(json.dumps(doc))
            with self.assertRaisesRegex(SplitError,"SOURCE_SHA_MISMATCH"):
                split_existing(src,plan,root/"no-out")
            self.assertFalse((root/"no-out").exists())

if __name__=="__main__":
    unittest.main()
