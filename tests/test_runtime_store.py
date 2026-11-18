import copy
import json
import multiprocessing
from pathlib import Path
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
