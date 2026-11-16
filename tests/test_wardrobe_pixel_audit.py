"""Real pixel evidence is admissible only for alpha-isolated original layers."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from videoforge.wardrobe_pixel_audit import audit, group_color, measure
from videoforge.errors import VideoForgeError
from videoforge.remake_autopilot import ROOT, EPISODE

class WardrobePixelAuditTests(unittest.TestCase):
    def test_histogram_classifications_from_known_pixels(self):
        self.assertEqual(group_color(210,20,27),"red")
        self.assertEqual(group_color(12,16,20),"very_dark")
        self.assertEqual(group_color(113,31,173),"purple_or_magenta")
        self.assertEqual(group_color(224,224,228),"other")

    def test_real_sources_use_only_actual_alpha_isolation(self):
        d=audit()
        self.assertEqual(len(d["rows"]),6)
        self.assertFalse(d["beard_color_exactly_measured"])
        self.assertFalse(d["purple_bodice_exactly_measured"])
        self.assertFalse(d["red_outer_vs_black_center_measured"])
        self.assertEqual(d["approved_full_outfits"],0)
        self.assertFalse(d["canonical_identity_approved"])
        self.assertEqual(d["provider_calls"],0)
        elara=[x for x in d["rows"] if x["actor"]=="elara"]
        self.assertEqual(len(elara),2)
        self.assertTrue(all(x["status"]=="no_trusted_subject_mask"
                            and x["percent"] is None for x in elara))
        self.assertTrue(all(len(x["sha256"])==64 and not x["outfit_canonical"]
                            for x in d["rows"]))

    def test_unmodified_sha_and_repeatable_report(self):
        p=ROOT/EPISODE/"assets/cena-01/rig-drafts/aldric-partes/corpo-vestimenta-restante.png"
        before=hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(audit(),audit())
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),before)

    def test_wrong_sha_fails_closed(self):
        p=ROOT/EPISODE/"assets/referencias/chat-aprovadas/elara-close-trono.png"
        with self.assertRaisesRegex(VideoForgeError,"PIXEL_QA_SHA_MISMATCH"):
            measure(p,"0"*64)

    def test_synthetic_alpha_layer_measures_red_and_dark_only(self):
        with tempfile.TemporaryDirectory() as folder:
            image=Image.new("RGBA",(80,80),(0,0,0,0))
            for y in range(16,64):
                for x in range(16,64):
                    image.putpixel((x,y), (210,20,27,255) if x<40
                                   else (12,16,20,255))
            p=Path(folder)/"sample.png"
            image.save(p)
            result=measure(p,hashlib.sha256(p.read_bytes()).hexdigest())
            self.assertEqual(result["status"],"unlabeled_rgba_layer_measured")
            self.assertGreater(result["percent"]["red"],40)
            self.assertGreater(result["percent"]["very_dark"],40)

if __name__=="__main__":
    unittest.main()
