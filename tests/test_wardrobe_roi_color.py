"""Validated region comparisons may REJECT but must never auto-approve."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from videoforge.wardrobe_roi_color import pair_result, run
from videoforge.errors import VideoForgeError

class SemanticROIColorTests(unittest.TestCase):
    def test_four_real_pairs_need_validated_masks_and_stay_unapproved(self):
        result=run()
        self.assertEqual(len(result["pairs"]),4)
        self.assertEqual(result["unverified_pairs"],4)
        self.assertEqual(result["automatic_approved_art_count"],0)
        self.assertTrue(result["known_owner_rejections_still_active"])
        self.assertEqual(result["provider_calls"],0)
        self.assertTrue(all(x["status"]=="EVIDENCIA_INSUFICIENTE" for x in result["pairs"]))
    def test_synthetic_verified_red_to_black_region_is_auto_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            for name,color in (("a.png",(205,20,24)),("b.png",(12,16,18))):
                Image.new("RGB",(96,96),color).save(folder/name)
            def source(name):
                file=folder/name
                return {"path":name,"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                        "pose_verified":True,"semantic_polygon_verified":True,
                        "polygon":[[20,20],[64,20],[64,64],[20,64]]}
            record={"actor":"aldric","semantic_region":"tecido_externo",
                    "source_a":source("a.png"),"source_b":source("b.png")}
            result=pair_result(folder,record)
            self.assertEqual(result["status"],"REPROVADO_POR_DIVERGENCIA_CROMATICA")
            self.assertGreater(result["deltas_percentage_points"]["red"],80)
            self.assertFalse(result["auto_approved"])
            record["source_b"]["semantic_polygon_verified"]=False
            self.assertEqual(pair_result(folder,record)["status"],"EVIDENCIA_INSUFICIENTE")
    def test_untrusted_source_hash_is_blocked(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            for name in ("a.png","b.png"):
                Image.new("RGB",(96,96),(200,20,20)).save(folder/name)
            polygon=[[20,20],[64,20],[64,64],[20,64]]
            record={"actor":"elara","semantic_region":"corpete_roxo_palacio",
                    "source_a":{"path":"a.png","sha256":"0"*64,"pose_verified":True,
                                "semantic_polygon_verified":True,"polygon":polygon},
                    "source_b":{"path":"b.png","sha256":hashlib.sha256((folder/"b.png").read_bytes()).hexdigest(),
                                "pose_verified":True,"semantic_polygon_verified":True,"polygon":polygon}}
            with self.assertRaisesRegex(VideoForgeError,"SOURCE_SHA_MISMATCH"):
                pair_result(folder,record)

if __name__=="__main__":
    unittest.main()
