import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from orchestrator import runtime
from orchestrator.runtime_store import Store, Conflict


class RuntimeTests(unittest.TestCase):
    def test_end_to_end_mock_reopen_no_duplicate_and_protected_sources(self):
        protected = [runtime.ROOT/runtime.MANIFEST, runtime.ROOT/runtime.EP/'APROVACOES-VISUAIS-C01-V3.json']
        hashes = [runtime.file_sha(p) for p in protected]
        with tempfile.TemporaryDirectory() as tmp:
            db, output = Path(tmp)/'db.sqlite', Path(tmp)/'report.json'
            command = [sys.executable,'-m','orchestrator.runtime','--db',str(db),'--output',str(output),'--mode','mock','--max-tasks','2']
            subprocess.run(command,cwd=runtime.ROOT,check=True,capture_output=True)
            first = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(len(first['checkpoints']),2)
            self.assertEqual(first['usage'],[])
            self.assertTrue(all(c['human_visual_approval'] is False for c in first['checkpoints']))
            subprocess.run(command,cwd=runtime.ROOT,check=True,capture_output=True)
            second = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(first['state_sha256'],second['state_sha256'])
            self.assertEqual(len(second['agents']),12)
            self.assertTrue(all(a['status']=='idle' for a in second['agents']))
            routes = {(e['sender'],e['recipient']) for e in second['events']}
            self.assertTrue({('01','03'),('03','12'),('12','01')} <= routes)
        self.assertEqual(hashes,[runtime.file_sha(p) for p in protected])

    def test_independent_qa_rejects_fabricated_timing(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp)/'db.sqlite')
            runtime.seed(store)
            claim = store.claim()
            context = runtime.read_context(runtime.ROOT,claim)
            report = {'agent_id':claim['owner'],'input_refs':claim['input_refs'],'human_visual_approval':False,'youtube_publication':False,'audit':runtime.audit(claim,context)}
            self.assertTrue(runtime.independently_verify(runtime.ROOT,claim,report)['technical_passed'])
            report['audit']['facts']['frame_bounds'][0][0] = -1
            self.assertFalse(runtime.independently_verify(runtime.ROOT,claim,report)['technical_passed'])
            store.close()

    def test_real_mode_disabled_records_block_not_mock_success(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ',{'AI_ENABLED':'false','PAID_CALLS_ENABLED':'false'}):
            store = Store(Path(tmp)/'db.sqlite')
            runtime.seed(store,mode='openai')
            result = runtime.step(store,mode='openai')
            self.assertEqual(result['status'],'blocked')
            self.assertEqual(store.export_snapshot()['tables']['usage'],[])
            self.assertEqual(store.export_snapshot()['tables']['results'],[])
            store.close()

    def test_all_twelve_instructions_loaded_and_source_changes_fenced(self):
        agents = runtime.registry()
        self.assertEqual({a['id'] for a in agents},set(runtime.ROLES))
        self.assertTrue(all(len(a['instructions_sha256'])==64 for a in agents))
        with self.assertRaises(Conflict):
            runtime.source(runtime.ROOT,runtime.MANIFEST,'0'*64)
        with self.assertRaises(ValueError):
            runtime.source(runtime.ROOT,'README.md')
        with self.assertRaises(ValueError):
            runtime.write_report(runtime.ROOT/runtime.EP/'forbidden-runtime-test.json',{})

    def test_executor_mode_does_not_claim_other_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp)/'db.sqlite')
            runtime.seed(store,mode='mock')
            before = store.export_snapshot()
            self.assertIsNone(runtime.step(store,mode='openai'))
            self.assertEqual(before,store.export_snapshot())
            store.close()

    def test_parent_symlink_cannot_exfiltrate_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, outside = Path(tmp)/'repo', Path(tmp)/'outside'
            outside.mkdir()
            (outside/'secret.json').write_text('{}')
            parent = root/runtime.EP
            parent.parent.mkdir(parents=True)
            try:
                parent.symlink_to(outside,target_is_directory=True)
            except OSError:
                self.skipTest('OS requires permission to create symlink')
            with self.assertRaises(ValueError):
                runtime.source(root,runtime.EP/'secret.json')

    def test_all_twelve_roles_route_mock_work_with_distinct_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp)/'db.sqlite')
            refs = {runtime.MANIFEST.as_posix():runtime.file_sha(runtime.ROOT/runtime.MANIFEST)}
            for owner in runtime.ROLES:
                reviewer = '01' if owner=='12' else '12'
                store.enqueue({'task_id':'ROLE-'+owner,'owner':owner,'reviewer':reviewer,'input_refs':refs,
                    'mode':'mock','operation':'read_only_analysis','human_visual_approval':False,'max_attempts':3,
                    'instructions_shas':{a:runtime.instructions(runtime.ROOT,a)[1] for a in {owner,reviewer,'01'}}})
            for _ in range(24):
                runtime.step(store)
            data = runtime.report(store)
            self.assertEqual(len(data['checkpoints']),12)
            self.assertEqual(data['usage'],[])
            self.assertTrue(all(c['review']['agent_id'] != store.get(c['task_id'])['owner'] for c in data['checkpoints']))
            store.close()


if __name__ == '__main__':
    unittest.main()
