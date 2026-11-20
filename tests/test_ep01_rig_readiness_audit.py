"""Zero-provider safety and classification tests for EP01 rig-readiness audit."""
import unittest

from scripts import ep01_rig_readiness_audit as audit


def meta(**kwargs):
    row={
        "schema":"videoforge/ep01-proxy-separate-part/v1",
        "candidate_scene_shot_id":"C05-P02",
        "component":"character-kael",
        "generation_method":"proxy_generated_separate_image",
        "source_mother_sha256":"a"*64,
        "technical_qa":"candidate_proxy_generated_separate_image",
        "human_visual_approval":False,"rig_ready":False,
        "youtube_uploaded":False,
    }
    row.update(kwargs)
    return row


class ReadinessTests(unittest.TestCase):
    def check(self,record=None,dimensions=(941,1672),mode="RGBA",alpha=(0,255)):
        return audit.policy_checks(
            meta() if record is None else record,"a"*64,
            "C05-P02","character-kael",(941,1672),dimensions,mode,alpha)

    def test_geometrically_compatible_candidate_is_not_an_approved_rig(self):
        self.assertEqual(self.check(),[])

    def test_native_canvas_mismatch_is_not_silently_resized(self):
        self.assertIn("native_canvas_alignment_required",
                      self.check(dimensions=(941,1671)))

    def test_rejected_archive_never_ready(self):
        self.assertIn("archived_candidate_rejected",
                      self.check(meta(technical_qa="rejected_canvas_mismatch_no_pixel_resizing")))

    def test_alpha_is_required_for_characters(self):
        self.assertIn("rgba_transparency_invalid_or_empty",
                      self.check(mode="RGB",alpha=None))
        self.assertIn("rgba_transparency_invalid_or_empty",
                      self.check(alpha=(255,255)))

    def test_wrong_mother_sha_blocks(self):
        self.assertIn("wrong_scene_mother_sha",
                      self.check(meta(source_mother_sha256="b"*64)))

    def test_never_promote_visual_approval_from_provider_metadata(self):
        errors=self.check(meta(human_visual_approval=True,rig_ready=True))
        self.assertIn("unexpected_approval_or_rig_flag",errors)

    def test_no_youtube_publish_flags(self):
        self.assertIn("unexpected_publish_flag",self.check(meta(youtube_uploaded=True)))

    def test_report_is_honest_about_passing_geometry(self):
        report={
          "component_counts":{"geometry_candidate_only":1,"needs_technical_review":2},
          "shots":[{"shot_id":"C05-P02","expected_parts":3,"candidate_geometry_passed":1,
                    "flags":["canvas_or_reference_qa_needed"]}],
        }
        md=audit.to_markdown(report)
        self.assertIn("Nenhuma",md)
        self.assertIn("C05-P02",md)
        self.assertIn("canvas_or_reference_qa_needed",md)


if __name__ == "__main__":
    unittest.main()
