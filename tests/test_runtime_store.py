import copy
import json
import multiprocessing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from orchestrator.runtime_store import Store, Conflict, BudgetBlocked, validate_message
from orchestrator.agent_bus import fingerprint


def task(identifier='audit', owner='03', reviewer='12'):
    return {'task_id':identifier,'owner':owner,'reviewer':reviewer,'input_refs':{'test.json':'a'*64},
            'mode':'mock','operation':'continuity_audit','human_visual_approval':False,'max_attempts':3}


def delivery(claim):
    return {'agent_id':claim['owner'],'input_refs':claim['input_refs'],'human_visual_approval':False,'youtube_publication':False}


def contender(database, event, results):
    store = Store(database)
    event.wait(10)
    claimed = store.claim(now=10)
    if claimed and claimed['phase'] == 'produce':
        store.deliver(claimed['task_id'],claimed['attempt_id'],claimed['revision'],delivery(claimed),now=11)
    results.put(claimed['phase'] if claimed else None)
    store.close()


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'runtime.sqlite'
        self.store = Store(self.path)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_duplicate_and_conflicting_input(self):
        self.assertTrue(self.store.enqueue(task(),now=0))
        self.assertFalse(self.store.enqueue(task(),now=1))
        changed = task()
        changed['input_refs']['test.json'] = 'b'*64
        with self.assertRaises(Conflict):
            self.store.enqueue(changed,now=2)
        self.assertEqual(len(self.store.export_snapshot()['tables']['events']),1)

    def test_independent_review_and_persistent_checkpoint(self):
        self.store.enqueue(task(),now=0)
        claim = self.store.claim(now=1)
        self.store.deliver('audit',claim['attempt_id'],claim['revision'],delivery(claim),now=2)
        reviewer = self.store.claim(now=3)
        decision = {'agent_id':'03','technical_passed':True,'human_visual_approval':False,'reviewed_result_sha256':fingerprint(delivery(claim))}
        with self.assertRaises(ValueError):
            self.store.review('audit',reviewer['attempt_id'],reviewer['revision'],decision,now=4)
        decision['agent_id'] = '12'
        self.store.review('audit',reviewer['attempt_id'],reviewer['revision'],decision,now=4)
        self.store.close()
        self.store = Store(self.path)
        self.assertEqual(self.store.get('audit')['status'],'completed')
        self.assertIsNone(self.store.claim(now=5))
        self.assertEqual(len(self.store.export_snapshot()['tables']['checkpoints']),1)

    def test_expired_worker_fenced_and_retry_dead_letter(self):
        self.store.enqueue(task(),now=0)
        first = self.store.claim(now=1,ttl=60)
        self.store.recover(now=61)
        with self.assertRaises(Conflict):
            self.store.deliver('audit',first['attempt_id'],first['revision'],delivery(first),now=62)
        second = self.store.claim(now=72,ttl=60)
        self.assertNotEqual(first['attempt_id'],second['attempt_id'])
        self.store.recover(now=132)
        third = self.store.claim(now=153,ttl=60)
        self.store.recover(now=213)
        self.assertEqual(self.store.get('audit')['status'],'dead_letter')
        self.assertIsNone(self.store.claim(now=999))

    def test_budget_survives_reload_and_unknown_call_is_never_replayed(self):
        self.store.enqueue(task(),now=0)
        claim = self.store.claim(now=1,ttl=60)
        limits = {'usd':1,'tokens':1000,'calls':1}
        self.store.reserve('audit',claim['attempt_id'],claim['revision'],'openai',100,.01,limits,now=2)
        with self.assertRaises(BudgetBlocked):
            self.store.reserve('audit',claim['attempt_id'],claim['revision'],'openai',100,.01,limits,now=3)
        self.store.close()
        self.store = Store(self.path)
        self.store.recover(now=61)
        self.assertEqual(self.store.get('audit')['status'],'blocked')
        self.assertIsNone(self.store.claim(now=1000))
        self.assertEqual(self.store.export_snapshot()['tables']['usage'][0]['state'],'unknown')

    def test_failed_remote_cas_returns_no_lease_and_poisoned_store(self):
        self.store.enqueue(task(),now=0)
        def fail(_):
            raise Conflict('remote state changed')
        self.store.persist_callback = fail
        with self.assertRaises(Conflict):
            self.store.claim(now=1)
        with self.assertRaises(Conflict):
            self.store.claim(now=2)

    def test_settled_paid_call_without_delivery_is_not_replayed(self):
        self.store.enqueue(task(),now=0)
        claim = self.store.claim(now=1,ttl=60)
        call = self.store.reserve('audit',claim['attempt_id'],claim['revision'],'openai',100,.01,{'usd':1,'tokens':1000,'calls':3},now=2)
        self.store.settle(call,10,10,.001)
        self.store.recover(now=61)
        self.assertEqual(self.store.get('audit')['status'],'blocked')
        self.assertIsNone(self.store.claim(now=999))

    def test_uncapped_money_still_enforces_durable_token_and_call_limits(self):
        self.store.enqueue(task(), now=0)
        claim = self.store.claim(now=1, ttl=120)
        call_id = self.store.reserve(
            'audit', claim['attempt_id'], claim['revision'], 'codex_proxy', 500,
            None, {'usd': None, 'tokens': 1000, 'calls': 4}, now=2,
            agent_id='03', model='gpt-6-astra')
        response = {'agent_id': '03', 'status': 'complete',
                    'human_visual_approval': False, 'findings': []}
        request_digest = 'a' * 64
        instructions_digest = 'c' * 64
        provider_digest = 'd' * 64
        self.store.settle(call_id, 70, 12, None, agent_id='03',
                          model='gpt-6-astra', response_id='resp_test',
                          report_sha256=fingerprint(response), response=response,
                          recipient='12', runtime_stage='specialist',
                          request_sha256=request_digest,
                          instructions_sha256=instructions_digest,
                          provider_response_sha256=provider_digest, now=3)
        row = self.store.export_snapshot()['tables']['usage'][0]
        self.assertEqual(row['call_id'], call_id)
        self.assertEqual(row['agent_id'], '03')
        self.assertEqual(row['model'], 'gpt-6-astra')
        self.assertEqual(row['response_id'], 'resp_test')
        self.assertEqual(row['report_sha256'], fingerprint(response))
        self.assertIsNone(row['reserved_usd'])
        self.assertIsNone(row['actual_usd'])
        self.assertEqual((row['actual_input'], row['actual_output']), (70, 12))
        messages = self.store.invocation_responses('audit')
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['sender'], '03')
        self.assertEqual(messages[0]['recipient'], '12')
        self.assertEqual(messages[0]['content']['call_id'], call_id)
        self.assertEqual(messages[0]['content']['runtime_stage'], 'specialist')
        self.assertEqual(messages[0]['content']['request_sha256'], request_digest)
        self.assertEqual(messages[0]['content']['instructions_sha256'], instructions_digest)
        self.assertEqual(messages[0]['content']['provider_response_sha256'], provider_digest)
        self.assertEqual(messages[0]['content']['response'], response)

    def test_expired_worker_resumes_only_from_persisted_response_without_replay(self):
        strict = task()
        strict['max_attempts'] = 1
        self.store.enqueue(strict, now=0)
        first = self.store.claim(now=1, ttl=60)
        call_id = self.store.reserve(
            'audit', first['attempt_id'], first['revision'], 'codex_proxy', 500,
            None, {'usd': None, 'tokens': 2000, 'calls': 4}, now=2,
            agent_id='01', model='gpt-6-astra')
        response = {'agent_id': '01', 'target_agent': '03',
                    'human_visual_approval': False}
        self.store.settle(
            call_id, 40, 10, None, agent_id='01', model='gpt-6-astra',
            response_id='resp_first', response=response, recipient='03',
            runtime_stage='dispatch', request_sha256='a' * 64,
            instructions_sha256='b' * 64, provider_response_sha256='c' * 64,
            now=3)
        first_attempt = first['attempt_id']
        remote_snapshot = self.store.export_snapshot()
        self.store.close()
        self.store = Store(Path(self.tmp.name) / 'reopened-cas-snapshot.sqlite')
        self.store.import_snapshot(remote_snapshot)
        self.assertEqual(self.store.recover(now=61), ['audit'])
        resumed_task = self.store.get('audit')
        self.assertEqual(resumed_task['status'], 'ready')
        self.assertEqual(resumed_task['resume_from_attempts'], [first_attempt])
        resumed = self.store.claim(now=72)
        self.assertNotEqual(resumed['attempt_id'], first_attempt)
        journal = self.store.invocation_responses(
            'audit', attempt_ids=resumed['resume_from_attempts'])
        self.assertEqual(len(journal), 1)
        self.assertEqual(journal[0]['content']['call_id'], call_id)
        self.assertEqual(len(self.store.export_snapshot()['tables']['usage']), 1)

    def test_expired_worker_with_unknown_call_outcome_stays_blocked(self):
        strict = task()
        strict['max_attempts'] = 1
        self.store.enqueue(strict, now=0)
        first = self.store.claim(now=1, ttl=60)
        self.store.reserve('audit', first['attempt_id'], first['revision'],
                           'codex_proxy', 500, None,
                           {'usd': None, 'tokens': 2000, 'calls': 4}, now=2,
                           agent_id='01', model='gpt-6-astra')
        self.store.close()
        self.store = Store(self.path)
        self.store.recover(now=61)
        self.assertEqual(self.store.get('audit')['status'], 'blocked')
        self.assertIsNone(self.store.claim(now=62))
        self.assertEqual(self.store.export_snapshot()['tables']['usage'][0]['state'], 'unknown')

    def test_unknown_cost_cannot_use_finite_usd_budget(self):
        self.store.enqueue(task(), now=0)
        claim = self.store.claim(now=1)
        with self.assertRaises(BudgetBlocked):
            self.store.reserve('audit', claim['attempt_id'], claim['revision'],
                               'codex_proxy', 500, None,
                               {'usd': 1.0, 'tokens': 1000, 'calls': 4}, now=2)

    def test_old_snapshot_usage_rows_load_with_empty_provenance(self):
        self.store.enqueue(task(), now=0)
        claim = self.store.claim(now=1)
        self.store.reserve('audit', claim['attempt_id'], claim['revision'],
                           'openai', 100, .01,
                           {'usd': 1, 'tokens': 1000, 'calls': 3}, now=2)
        snapshot = self.store.export_snapshot()
        for row in snapshot['tables']['usage']:
            for key in ('agent_id', 'model', 'response_id', 'report_sha256'):
                row.pop(key)
        other = Store(Path(self.tmp.name) / 'legacy-remote-state.sqlite')
        other.import_snapshot(snapshot)
        loaded = other.export_snapshot()['tables']['usage'][0]
        self.assertIsNone(loaded['agent_id'])
        self.assertIsNone(loaded['model'])
        other.close()

    def test_old_sqlite_usage_table_is_rebuilt_with_nullable_reservation(self):
        legacy_path = Path(self.tmp.name) / 'legacy.sqlite'
        connection = sqlite3.connect(legacy_path)
        connection.execute('CREATE TABLE attempts(id TEXT PRIMARY KEY)')
        connection.execute('''CREATE TABLE usage(call_id TEXT PRIMARY KEY,
            attempt_id TEXT NOT NULL REFERENCES attempts(id), provider TEXT NOT NULL,
            reserved_tokens INTEGER NOT NULL, reserved_usd REAL NOT NULL,
            state TEXT NOT NULL, actual_input INTEGER, actual_output INTEGER, actual_usd REAL)''')
        connection.commit()
        connection.close()
        legacy = Store(legacy_path)
        reserved_usd = next(row[3] for row in legacy.db.execute('PRAGMA table_info(usage)')
                            if row[1] == 'reserved_usd')
        self.assertEqual(reserved_usd, 0)
        legacy.close()

    def test_review_rejection_can_block_without_automatic_retry(self):
        strict = task()
        strict.update(stop_on_review_rejection=True, max_attempts=1)
        self.store.enqueue(strict, now=0)
        producer = self.store.claim(now=1)
        self.store.deliver('audit', producer['attempt_id'], producer['revision'],
                           delivery(producer), now=2)
        reviewer = self.store.claim(now=3)
        decision = {'agent_id': '12', 'technical_passed': False,
                    'human_visual_approval': False,
                    'reviewed_result_sha256': self.store.get('audit')['result_sha256'],
                    'findings': []}
        self.store.review('audit', reviewer['attempt_id'], reviewer['revision'],
                          decision, now=4)
        self.assertEqual(self.store.get('audit')['status'], 'blocked')
        self.assertIsNone(self.store.claim(now=100))
        self.assertEqual(len(self.store.export_snapshot()['tables']['checkpoints']), 1)
        events = [json.loads(row['envelope']) for row in self.store.export_snapshot()['tables']['events']]
        self.assertIn('task_blocked', [event['type'] for event in events])

    def test_non_finite_budget_and_completed_snapshot_without_evidence_rejected(self):
        self.store.enqueue(task(),now=0)
        claim = self.store.claim(now=1)
        with self.assertRaises(BudgetBlocked):
            self.store.reserve('audit',claim['attempt_id'],claim['revision'],'openai',100,.01,{'usd':float('nan'),'tokens':1000,'calls':3},now=2)
        snapshot = self.store.export_snapshot()
        payload = json.loads(snapshot['tables']['tasks'][0]['payload'])
        payload.update(status='completed',lease=None)
        snapshot['tables']['tasks'][0]['payload'] = json.dumps(payload)
        other = Store(Path(self.tmp.name)/'forged.sqlite')
        with self.assertRaises(ValueError):
            other.import_snapshot(snapshot)
        other.close()

    def test_message_schema_hash_and_production_gate(self):
        self.store.enqueue(task(),now=0)
        envelope = json.loads(self.store.export_snapshot()['tables']['events'][0]['envelope'])
        validate_message(envelope)
        envelope['content']['operation'] = 'youtube_publish'
        with self.assertRaises(ValueError):
            validate_message(envelope)
        for operation in ['image_generation','render','youtube_publish']:
            forbidden = dict(task(operation),operation=operation)
            with self.assertRaises(ValueError):
                self.store.enqueue(forbidden,now=0)
        with self.assertRaises(ValueError):
            self.store.enqueue(task('self','12','12'),now=0)

    def test_snapshot_roundtrip_and_corrupt_evidence(self):
        self.store.enqueue(task(),now=0)
        claim = self.store.claim(now=1)
        self.store.deliver('audit',claim['attempt_id'],claim['revision'],delivery(claim),now=2)
        snapshot = self.store.export_snapshot()
        other = Store(Path(self.tmp.name)/'restored.sqlite')
        other.import_snapshot(snapshot)
        self.assertEqual(self.store.result('audit'),other.result('audit'))
        other.close()
        snapshot['tables']['results'][0]['sha256'] = '0'*64
        other = Store(Path(self.tmp.name)/'corrupt.sqlite')
        with self.assertRaises(ValueError):
            other.import_snapshot(snapshot)
        other.close()

    def test_multiprocess_claims_do_not_duplicate_production(self):
        self.store.enqueue(task(),now=0)
        ctx = multiprocessing.get_context('spawn')
        event, results = ctx.Event(), ctx.Queue()
        workers = [ctx.Process(target=contender,args=(str(self.path),event,results)) for _ in range(2)]
        for worker in workers:
            worker.start()
        event.set()
        for worker in workers:
            worker.join(15)
            self.assertEqual(worker.exitcode,0)
        phases = [results.get(timeout=2) for _ in workers]
        self.assertEqual(phases.count('produce'),1)
        self.assertEqual(len(self.store.export_snapshot()['tables']['results']),1)


if __name__ == '__main__':
    unittest.main()
