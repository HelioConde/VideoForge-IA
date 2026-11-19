import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from scripts import ep01_action_production_queue as q
from scripts.ep01_layer_gallery import gallery


class GalleryTests(unittest.TestCase):
    def test_preview_requires_the_archived_bytes_and_preserves_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = q.EP / "assets" / "layer.png"
            (root/path).parent.mkdir(parents=True)
            Image.new("RGBA", (4, 4), (50, 40, 20, 120)).save(root/path)
            task = dict(task_id="one", kind="image", shot_id="C01-P05", owner="05",
                        part="guarda", status="ready_for_preflight")
            receipt = dict(status="rejected_archived", child_run_id=123, source_file=path.as_posix(),
                           technical_qa="rejected_canvas_mismatch_no_pixel_resizing",
                           sha256=q.digest(root/path))
            result = gallery([task], {"one":receipt}, root)
            self.assertIn("data:image/png;base64,", result)
            self.assertIn("rejected_canvas_mismatch", result)
            self.assertIn("/runs/123", result)
            receipt["sha256"] = "0"*64
            self.assertNotIn("data:image/png", gallery([task], {"one":receipt}, root))

    def test_public_dashboard_replaces_previous_active_child(self):
        body="<!-- videoforge-ep01-production-queue:v1 -->\n# EP01\n<!-- ep01-active-child -->old"
        observed=[]
        def fake_gh(*args, **kwargs):
            if args[0]=="api":
                return {"body":body,"state":"open"}
            observed.append(Path(args[-1]).read_text(encoding="utf8"))
        with patch.dict("os.environ", EP01_SHOW_ACTIVE_CHILD="true"), patch.object(q,"gh",side_effect=fake_gh):
            q.publish_active_child({"owner":"05","shot_id":"C01-P05","part":"guard"},123)
        self.assertEqual(observed[0].count("<!-- ep01-active-child -->"),1)
        self.assertIn("Agente 05",observed[0])
        self.assertIn("/actions/runs/123",observed[0])

    def test_success_cannot_credit_another_child_or_mother(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "123" / "layer.png"
            path.parent.mkdir()
            path.write_bytes(b"archived fixture")
            meta = dict(technical_qa="candidate_minor_edge_delta_requires_alignment_qa",
                        source_mother_sha256="a"*64)
            path.with_suffix(".production.json").write_text(json.dumps(meta))
            item = dict(file="123/layer.png", sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            task = dict(kind="image", shot_id="C01-P05", part="guard", source_sha256="a"*64)
            with patch.object(q, "ROOT", root), patch.object(q, "reload_main"), patch.object(q.parts, "existing_part", return_value=item):
                self.assertEqual(q.verify_child(task, 123)["status"], "archived")
                with self.assertRaises(ValueError):
                    q.verify_child(task, 124)
                with self.assertRaises(ValueError):
                    q.verify_child(dict(task,source_sha256="b"*64), 123)
