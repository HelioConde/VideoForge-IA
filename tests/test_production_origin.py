"""Regra nº 1: nenhum render isolado pode virar vídeo oficial por nome."""
import copy
from pathlib import Path
import unittest

from videoforge.production_origin import (
    ProvenanceError,
    audit_repo,
    validate_editorial_origin,
)

ROOT = Path(__file__).resolve().parents[1]


class ProductionOriginTests(unittest.TestCase):
    def test_auditoria_de_todos_os_registros(self):
        self.assertGreaterEqual(audit_repo(ROOT), 1)

    def test_preview_spy_family_nao_e_video_oficial(self):
        import json
        f=ROOT/"canal"/"otaku-br"/"videos"/"spy-x-family-familia-de-mentira"/"editorial.json"
        record=json.loads(f.read_text(encoding="utf-8"))
        self.assertFalse(validate_editorial_origin(record))
        self.assertNotEqual(record["producao"]["classificacao"], "producao_oficial")
        self.assertFalse(record["producao"]["video_oficial_do_programa"])
        self.assertIn(record["status"], ("assets_pendentes", "renderizado"))
        self.assertFalse(record["producao"].get("rig_animado_aplicado", False))

    def test_preview_nao_pode_mentir_com_tipo_oficial(self):
        obj={"producao":{"classificacao":"producao_oficial",
                         "video_oficial_do_programa":False}}
        with self.assertRaisesRegex(ProvenanceError,"MISLABELED"):
            validate_editorial_origin(obj)

    def test_workflow_experimental_nunca_pode_ser_oficial(self):
        import json
        f=ROOT/"canal"/"otaku-br"/"videos"/"spy-x-family-familia-de-mentira"/"editorial.json"
        obj=json.loads(f.read_text(encoding="utf-8"))
        obj["producao"]["classificacao"]="producao_oficial"
        obj["producao"]["video_oficial_do_programa"]=True
        # O cadastro editorial evolui; o teste deve injetar um workflow
        # experimental de propósito, não depender do nome atual do episódio.
        obj["producao"]["workflow_arquivo"]=".github/workflows/spy-family-animated.yml"
        with self.assertRaisesRegex(ProvenanceError,"EXPERIMENTAL_WORKFLOW"):
            validate_editorial_origin(obj)

    def test_render_necessita_comprovacao_de_cada_etapa(self):
        obj={"producao":{
            "classificacao":"producao_oficial",
            "video_oficial_do_programa":True,
            "programa_origem":"HelioConde/VideoForge-IA",
            "workflow_arquivo":".github/workflows/video-producao.yml",
            "github_actions_run_id":1,
            "workflow_url":"https://github.com/HelioConde/VideoForge-IA/actions/runs/1",
            "artefato_url":"https://github.com/HelioConde/VideoForge-IA/actions/runs/1/artifacts/2",
            "sha256":"a"*64,"etapas_comprovadas":{},
        }}
        with self.assertRaisesRegex(ProvenanceError,"STAGES_NOT_PROVEN"):
            validate_editorial_origin(obj)

    def test_official_must_have_original_scene_and_real_part_rig(self):
        from videoforge.production_origin import MANDATORY_STAGES
        link="https://github.com/HelioConde/VideoForge-IA/actions/runs/98765"
        data={"producao":{
            "classificacao":"producao_oficial",
            "video_oficial_do_programa":True,
            "programa_origem":"HelioConde/VideoForge-IA",
            "workflow_arquivo":".github/workflows/render-integrado.yml",
            "github_actions_run_id":98765,
            "workflow_url":link,
            "artefato_url":link+"/artifacts/2",
            "sha256":"a"*64,
            "etapas_comprovadas":{x:{"status":"verified","evidence_url":link}
                                 for x in MANDATORY_STAGES},
        },
        "qa":{"aprovado_tecnicamente":True,"aprovado_editorialmente":True},
        "arte":{"consistencia_verificada":True},
        "roteiro":{"cenas_previstas":["gancho-anya"]}}
        with self.assertRaisesRegex(ProvenanceError,"ACTUAL_LAYERED_RIG_REQUIRED"):
            validate_editorial_origin(data)
        data["producao"].update({"rig_animado_aplicado":True,
            "animacao_motor":"remotion-rig-rgba-scene-mother"})
        with self.assertRaisesRegex(ProvenanceError,"SCENE_MOTHER_COVERAGE_INCOMPLETE"):
            validate_editorial_origin(data)
        data["producao"]["cenas_animadas_verificadas"]=[{
            "scene":"gancho-anya",
            "scene_mother_sha256":"1"*64,
            "background_sha256":"2"*64,
            "characters_rgba_sha256":"3"*64,
            "individual_character_parts_verified":False,
            "all_movable_objects_separated":False,
            "seam_and_opaque_face_qa":False,
            "rig_motion_qa":False,
            "human_visual_approval":False}]
        with self.assertRaisesRegex(ProvenanceError,"SCENE_MOTHER_RIG_EVIDENCE_INCOMPLETE"):
            validate_editorial_origin(data)

    def test_fake_repositorio_nao_pode_ser_origem(self):
        obj={"producao":{"classificacao":"producao_oficial",
                         "video_oficial_do_programa":True,
                         "programa_origem":"outro/projeto"}}
        with self.assertRaisesRegex(ProvenanceError,"REQUIRES_VIDEOFORGE_REPO"):
            validate_editorial_origin(obj)


if __name__ == "__main__":
    unittest.main()
