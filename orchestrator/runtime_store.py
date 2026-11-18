"""Transactional task/message store. No model, filesystem production or network tools."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sqlite3
import time
import uuid

from .agent_bus import ROLES, fingerprint
from .task_leases import claim as lease_claim, checkpoint as lease_checkpoint, recover as lease_recover

KINDS = {'task_assigned', 'task_started', 'progress_update', 'review_requested',
         'review_approved', 'review_rejected', 'revision_requested', 'task_completed',
         'task_failed', 'task_blocked'}
TABLES = ('tasks', 'attempts', 'events', 'results', 'checkpoints', 'usage', 'meta')


class Conflict(ValueError):
    pass


class BudgetBlocked(ValueError):
    pass


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def validate_message(message):
    required = {'id', 'task_id', 'sender', 'recipient', 'type', 'content', 'timestamp',
                'version', 'input_references', 'content_hash', 'correlation_id', 'processing_state'}
    if set(message) != required or message['version'] != 1:
        raise ValueError('Invalid message schema')
    if message['sender'] not in ROLES or message['recipient'] not in ROLES or message['type'] not in KINDS:
        raise ValueError('Invalid route or message type')
    if not isinstance(message['content'], dict) or not isinstance(message['input_references'], dict):
        raise ValueError('Structured content and references required')
    if message['processing_state'] not in {'pending', 'processed'} or message['content_hash'] != fingerprint(message['content']):
        raise ValueError('Invalid processing state or content hash')
    if not all(isinstance(message[k], str) and message[k] for k in ['id', 'task_id', 'correlation_id', 'timestamp']):
        raise ValueError('Missing message identity')
    datetime.fromisoformat(message['timestamp'])
    expected_id = fingerprint({k:v for k,v in message.items() if k not in {'id','timestamp','processing_state'}})
    if message['id'] != expected_id:
        raise ValueError('Message identity/hash mismatch')


class Store:
    def __init__(self, path, persist_callback=None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path), timeout=15, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.persist_callback = persist_callback
        self.poisoned = False
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS tasks(task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, revision INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id), phase TEXT NOT NULL, worker TEXT NOT NULL, status TEXT NOT NULL, started INTEGER NOT NULL, expires INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE NOT NULL, envelope TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS results(attempt_id TEXT PRIMARY KEY REFERENCES attempts(id), task_id TEXT NOT NULL, content TEXT NOT NULL, sha256 TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS checkpoints(task_id TEXT PRIMARY KEY REFERENCES tasks(task_id), content TEXT NOT NULL, sha256 TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS usage(call_id TEXT PRIMARY KEY, attempt_id TEXT NOT NULL REFERENCES attempts(id), provider TEXT NOT NULL, reserved_tokens INTEGER NOT NULL, reserved_usd REAL NOT NULL, state TEXT NOT NULL, actual_input INTEGER, actual_output INTEGER, actual_usd REAL);
          CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        ''')

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        if self.poisoned:
            raise Conflict('Store needs reload after failed persistence')
        self.db.execute('BEGIN IMMEDIATE')
        before = self.db.total_changes
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise
        if self.persist_callback and self.db.total_changes != before:
            try:
                # Each remote CAS must finish BEFORE returning a lease/reservation to the worker.
                self.persist_callback(self.export_snapshot())
            except BaseException:
                self.poisoned = True
                raise

    def _event(self, task, sender, recipient, kind, content, correlation, now, pending=False):
        body = {'task_id': task['task_id'], 'sender': sender, 'recipient': recipient,
                'type': kind, 'content': content, 'timestamp': datetime.fromtimestamp(now, timezone.utc).isoformat(),
                'version': 1, 'input_references': task['input_refs'], 'content_hash': fingerprint(content),
                'correlation_id': correlation, 'processing_state': 'pending' if pending else 'processed'}
        body['id'] = fingerprint({k: v for k, v in body.items() if k not in {'timestamp', 'processing_state'}})
        validate_message(body)
        self.db.execute('INSERT OR IGNORE INTO events(event_id,envelope) VALUES (?,?)', (body['id'], encode(body)))

    def get(self, task_id):
        row = self.db.execute('SELECT * FROM tasks WHERE task_id=?', (task_id,)).fetchone()
        if not row:
            raise ValueError('Unknown task')
        task = json.loads(row['payload'])
        task['revision'] = row['revision']
        return task

    def _save(self, task, expected):
        task = dict(task)
        task.pop('revision', None)
        cursor = self.db.execute('UPDATE tasks SET payload=?,revision=revision+1 WHERE task_id=? AND revision=?',
                                 (encode(task), task['task_id'], expected))
        if cursor.rowcount != 1:
            raise Conflict('Task revision conflict')

    def enqueue(self, task, now=None):
        now = int(time.time()) if now is None else now
        if task.get('owner') not in ROLES or task.get('reviewer') not in ROLES or task['owner'] == task['reviewer']:
            raise ValueError('Invalid owner or independent reviewer')
        if task.get('operation') not in {'continuity_audit', 'reference_audit', 'read_only_analysis'}:
            raise ValueError('Production operations are disabled')
        if task.get('human_visual_approval', False) or not task.get('input_refs') or not 1 <= task.get('max_attempts', 3) <= 3:
            raise ValueError('Invalid task safety or attempt contract')
        if any(not isinstance(v, str) or len(v) != 64 or any(c not in '0123456789abcdef' for c in v) for v in task['input_refs'].values()):
            raise ValueError('SHA-256 input references required')
        task = dict(task, status='ready', lease=None, available_at=now)
        task['definition_hash'] = fingerprint({k: v for k, v in task.items() if k not in {'status', 'lease', 'available_at'}})
        with self.transaction():
            existing = self.db.execute('SELECT task_id FROM tasks WHERE task_id=?', (task['task_id'],)).fetchone()
            if existing:
                if self.get(task['task_id'])['definition_hash'] != task['definition_hash']:
                    raise Conflict('Task identity already has different inputs or instructions')
                return False
            self.db.execute('INSERT INTO tasks VALUES (?,?,0)', (task['task_id'], encode(task)))
            self._event(task, '01', task['owner'], 'task_assigned', {'operation': task['operation']}, task['task_id'], now, True)
        return True

    def claim(self, now=None, ttl=900, max_concurrency=2, mode=None):
        now = int(time.time()) if now is None else now
        if not 1 <= max_concurrency <= 12 or not 60 <= ttl <= 3600:
            raise ValueError('Invalid lease/concurrency bound')
        with self.transaction():
            if self.db.execute("SELECT count(*) FROM attempts WHERE status='running' AND expires>?", (now,)).fetchone()[0] >= max_concurrency:
                return None
            rows = [self.get(r[0]) for r in self.db.execute('SELECT task_id FROM tasks ORDER BY task_id')]
            rows.sort(key=lambda t: (t['status'] != 'needs_review', t.get('priority', 9), t['task_id']))
            for task in rows:
                if mode is not None and task.get('mode') != mode:
                    continue
                if task['status'] not in {'ready', 'needs_review'} or task['available_at'] > now:
                    continue
                phase = 'review' if task['status'] == 'needs_review' else 'produce'
                worker = task['reviewer'] if phase == 'review' else task['owner']
                count = self.db.execute('SELECT count(*) FROM attempts WHERE task_id=? AND phase=?', (task['task_id'], phase)).fetchone()[0]
                if count >= task.get('max_attempts', 3):
                    continue
                leased = lease_claim({'task_id': task['task_id'], 'owner': ROLES[worker], 'status': 'ready', 'attempts': count, 'input_shas': task['input_refs']}, ROLES[worker], now, ttl)
                token = uuid.uuid4().hex
                leased['lease']['lease_key'] = token
                task.update(status='reviewing' if phase == 'review' else 'running', lease=leased['lease'], phase=phase, attempt_id=token)
                self._save(task, task['revision'])
                self.db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?)', (token, task['task_id'], phase, worker, 'running', now, now+ttl))
                # Acknowledge the queued route in the same transaction as the claim.
                for row in self.db.execute('SELECT event_id,envelope FROM events').fetchall():
                    event = json.loads(row['envelope'])
                    if event['task_id'] == task['task_id'] and event['recipient'] == worker and event['processing_state'] == 'pending':
                        event['processing_state'] = 'processed'
                        self.db.execute('UPDATE events SET envelope=? WHERE event_id=?', (encode(event), row['event_id']))
                self._event(task, worker, '01', 'task_started', {'phase': phase, 'attempt': count+1}, token, now)
                return self.get(task['task_id'])
        return None

    def _fence(self, task_id, token, expected, now, phase):
        task = self.get(task_id)
        if task['revision'] != expected or task.get('attempt_id') != token or task.get('phase') != phase:
            raise Conflict('Stale attempt or revision')
        lease = task.get('lease') or {}
        if task['status'] not in {'running', 'reviewing'} or lease.get('lease_key') != token or not lease.get('claimed_at', now+1) <= now < lease.get('expires_at', 0):
            raise Conflict('Expired or missing lease')
        return task

    def deliver(self, task_id, token, expected, report, now=None):
        now = int(time.time()) if now is None else now
        if report.get('human_visual_approval') is not False or report.get('youtube_publication') is not False:
            raise ValueError('Report may not approve or publish production')
        with self.transaction():
            task = self._fence(task_id, token, expected, now, 'produce')
            if report.get('agent_id') != task['owner'] or report.get('input_refs') != task['input_refs']:
                raise ValueError('Report attribution/source mismatch')
            digest = fingerprint(report)
            legacy = dict(task, status='running')
            lease_checkpoint(legacy, ROLES[task['owner']], token, {'artifact_sha256': digest}, now)
            self.db.execute('INSERT INTO results VALUES (?,?,?,?)', (token, task_id, encode(report), digest))
            task.update(status='needs_review', lease=None, result_attempt=token, result_sha256=digest, available_at=now)
            self._save(task, expected)
            self.db.execute("UPDATE attempts SET status='delivered' WHERE id=?", (token,))
            self._event(task, task['owner'], task['reviewer'], 'review_requested', {'result_sha256': digest}, token, now, True)

    def result(self, task_id):
        task = self.get(task_id)
        row = self.db.execute('SELECT * FROM results WHERE attempt_id=?', (task.get('result_attempt'),)).fetchone()
        if not row or fingerprint(json.loads(row['content'])) != row['sha256'] or row['sha256'] != task['result_sha256']:
            raise Conflict('Result evidence missing or corrupt')
        return json.loads(row['content'])

    def review(self, task_id, token, expected, decision, now=None):
        now = int(time.time()) if now is None else now
        with self.transaction():
            task = self._fence(task_id, token, expected, now, 'review')
            if decision.get('agent_id') != task['reviewer'] or task['reviewer'] == task['owner']:
                raise ValueError('Independent reviewer required')
            if type(decision.get('technical_passed')) is not bool or decision.get('human_visual_approval') is not False or decision.get('reviewed_result_sha256') != task['result_sha256']:
                raise ValueError('Invalid review evidence')
            self.result(task_id)
            self.db.execute("UPDATE attempts SET status='reviewed' WHERE id=?", (token,))
            passed = decision['technical_passed']
            self._event(task, task['reviewer'], '01', 'review_approved' if passed else 'review_rejected', decision, token, now)
            if passed:
                task.update(status='completed', lease=None, completed_at=now)
                checkpoint = {'task_id': task_id, 'result_sha256': task['result_sha256'], 'review': decision, 'coordinator': '01',
                              'input_refs': task['input_refs'], 'scope': 'read_only_technical_audit', 'human_visual_approval': False, 'youtube_publication': False}
                self.db.execute('INSERT INTO checkpoints VALUES (?,?,?)', (task_id, encode(checkpoint), fingerprint(checkpoint)))
                self._event(task, '01', task['owner'], 'task_completed', {'checkpoint_sha256': fingerprint(checkpoint)}, token, now)
            else:
                attempts = self.db.execute("SELECT count(*) FROM attempts WHERE task_id=? AND phase='produce'", (task_id,)).fetchone()[0]
                task.update(status='dead_letter' if attempts >= task.get('max_attempts', 3) else 'ready', lease=None, available_at=now+min(60, 5*2**attempts))
                self._event(task, '01', task['owner'], 'task_failed' if task['status'] == 'dead_letter' else 'revision_requested', {'reason': 'independent_review_rejected'}, token, now)
            self._save(task, expected)

    def fail(self, task_id, token, expected, reason, retry=False, now=None):
        now = int(time.time()) if now is None else now
        with self.transaction():
            phase = self.get(task_id)['phase']
            task = self._fence(task_id, token, expected, now, phase)
            attempts = self.db.execute('SELECT count(*) FROM attempts WHERE task_id=? AND phase=?', (task_id, phase)).fetchone()[0]
            uncertain = self.db.execute("SELECT count(*) FROM usage WHERE attempt_id=?", (token,)).fetchone()[0]
            task.update(status=('dead_letter' if attempts >= task.get('max_attempts', 3) else ('needs_review' if phase == 'review' else 'ready')) if retry and not uncertain else 'blocked', lease=None, available_at=now+min(60, 5*2**attempts), blocked_reason=reason)
            self._save(task, expected)
            self.db.execute("UPDATE attempts SET status='failed' WHERE id=?", (token,))
            self.db.execute("UPDATE usage SET state='unknown' WHERE attempt_id=? AND state='reserved'", (token,))
            self._event(task, '01', task['owner'], 'task_blocked' if task['status'] == 'blocked' else 'task_failed', {'reason': reason}, token, now)

    def recover(self, now=None):
        now = int(time.time()) if now is None else now
        recovered = []
        with self.transaction():
            for row in self.db.execute("SELECT * FROM attempts WHERE status='running' AND expires<=?", (now,)).fetchall():
                task = self.get(row['task_id'])
                if task.get('attempt_id') != row['id']:
                    continue
                count = self.db.execute('SELECT count(*) FROM attempts WHERE task_id=? AND phase=?', (task['task_id'], row['phase'])).fetchone()[0]
                legacy = lease_recover(dict(task, status='running', attempts=count), now)
                # Even a settled paid response may not have been durably delivered.
                # Never buy it again after a crash; reconcile the attempt manually.
                uncertain = self.db.execute("SELECT count(*) FROM usage WHERE attempt_id=?", (row['id'],)).fetchone()[0]
                task.update(status='blocked' if uncertain else ('dead_letter' if legacy['status'] == 'failed' or count >= task.get('max_attempts',3) else ('needs_review' if row['phase'] == 'review' else 'ready')), lease=None, available_at=now+min(60,5*2**count))
                if uncertain:
                    task['blocked_reason'] = 'provider_outcome_unknown_manual_reconciliation_required'
                    self.db.execute("UPDATE usage SET state='unknown' WHERE attempt_id=? AND state='reserved'", (row['id'],))
                self._save(task, task['revision'])
                self.db.execute("UPDATE attempts SET status='expired' WHERE id=?", (row['id'],))
                self._event(task, '01', task['owner'], 'task_blocked' if uncertain else 'task_failed', {'reason': 'lease_expired', 'next_state': task['status']}, row['id'], now)
                recovered.append(task['task_id'])
        return recovered

    def reserve(self, task_id, token, revision, provider, tokens, usd, limits, now=None):
        now = int(time.time()) if now is None else now
        if type(tokens) is not int or tokens <= 0 or not 0 < usd < float('inf'):
            raise BudgetBlocked('Invalid conservative reservation')
        if (set(limits) != {'usd','tokens','calls'} or type(limits['tokens']) is not int or type(limits['calls']) is not int
                or limits['tokens'] <= 0 or limits['calls'] <= 0 or type(limits['usd']) not in {int,float}
                or not math.isfinite(limits['usd']) or limits['usd'] <= 0):
            raise BudgetBlocked('Positive finite budget limits required')
        with self.transaction():
            task = self.get(task_id)
            self._fence(task_id, token, revision, now, task['phase'])
            policy = self.db.execute("SELECT value FROM meta WHERE key='budget_policy'").fetchone()
            if policy and policy[0] != encode(limits):
                raise BudgetBlocked('Budget policy differs from durable budget')
            counts = self.db.execute('SELECT count(*),coalesce(sum(reserved_tokens),0),coalesce(sum(reserved_usd),0) FROM usage').fetchone()
            if counts[0]+1 > limits['calls'] or counts[1]+tokens > limits['tokens'] or counts[2]+usd > limits['usd']:
                raise BudgetBlocked('Durable budget exhausted')
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('budget_policy',?)", (encode(limits),))
            call_id = uuid.uuid4().hex
            self.db.execute('INSERT INTO usage VALUES (?,?,?,?,?,?,NULL,NULL,NULL)', (call_id, token, provider, tokens, usd, 'reserved'))
            return call_id

    def settle(self, call_id, input_tokens=None, output_tokens=None, actual_usd=None):
        with self.transaction():
            row = self.db.execute("SELECT state FROM usage WHERE call_id=?", (call_id,)).fetchone()
            if not row or row[0] != 'reserved':
                raise Conflict('Unknown or settled call')
            self.db.execute('UPDATE usage SET state=?,actual_input=?,actual_output=?,actual_usd=? WHERE call_id=?',
                            ('settled' if input_tokens is not None and output_tokens is not None else 'unknown', input_tokens, output_tokens, actual_usd, call_id))

    def export_snapshot(self):
        return {'schema_version': 1, 'tables': {table: [dict(row) for row in self.db.execute('SELECT * FROM '+table)] for table in TABLES}}

    def import_snapshot(self, snapshot):
        if snapshot.get('schema_version') != 1 or set(snapshot.get('tables', {})) != set(TABLES):
            raise ValueError('Invalid store snapshot')
        if any(self.db.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in TABLES):
            raise Conflict('Import requires empty local store')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            for table in TABLES:
                columns = [r[1] for r in self.db.execute('PRAGMA table_info('+table+')')]
                for row in snapshot['tables'][table]:
                    if set(row) != set(columns):
                        raise ValueError('Snapshot row schema mismatch')
                    self.db.execute('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in columns)+')', [row[c] for c in columns])
            for row in self.db.execute('SELECT envelope FROM events'):
                validate_message(json.loads(row[0]))
            for row in self.db.execute('SELECT * FROM tasks'):
                task = json.loads(row['payload'])
                if (task.get('task_id') != row['task_id'] or row['revision'] < 0
                        or task.get('owner') not in ROLES or task.get('reviewer') not in ROLES or task['owner'] == task['reviewer']
                        or task.get('status') not in {'ready','running','needs_review','reviewing','completed','blocked','dead_letter'}
                        or task.get('operation') not in {'continuity_audit','reference_audit','read_only_analysis'}
                        or task.get('human_visual_approval') is not False):
                    raise ValueError('Unsafe task snapshot')
            for table in ('results', 'checkpoints'):
                for row in self.db.execute('SELECT content,sha256 FROM '+table):
                    if fingerprint(json.loads(row[0])) != row[1]:
                        raise ValueError('Corrupt evidence snapshot')
            tasks = {row[0]:self.get(row[0]) for row in self.db.execute('SELECT task_id FROM tasks')}
            attempts = {row['id']:dict(row) for row in self.db.execute('SELECT * FROM attempts')}
            for task in tasks.values():
                if not task.get('input_refs') or any(len(v)!=64 or any(c not in '0123456789abcdef' for c in v) for v in task['input_refs'].values()):
                    raise ValueError('Invalid snapshot input hashes')
                if task['status'] in {'running','reviewing'}:
                    attempt = attempts.get(task.get('attempt_id'))
                    lease = task.get('lease') or {}
                    if (not attempt or attempt['task_id']!=task['task_id'] or attempt['status']!='running'
                            or attempt['phase'] != task.get('phase') or attempt['expires'] != lease.get('expires_at')
                            or lease.get('lease_key') != attempt['id'] or ROLES[attempt['worker']] != lease.get('worker')):
                        raise ValueError('Invalid active lease snapshot')
                elif task.get('lease'):
                    raise ValueError('Inactive task has a lease')
                if task.get('result_attempt'):
                    self.result(task['task_id'])
                if task['status'] == 'completed':
                    row = self.db.execute('SELECT content FROM checkpoints WHERE task_id=?',(task['task_id'],)).fetchone()
                    if not row or not task.get('result_attempt'):
                        raise ValueError('Completed task without durable evidence')
                    check = json.loads(row[0])
                    if check.get('human_visual_approval') is not False or check.get('result_sha256') != task.get('result_sha256') or check.get('input_refs') != task['input_refs']:
                        raise ValueError('Invalid checkpoint provenance')
            for attempt in attempts.values():
                task = tasks[attempt['task_id']]
                expected_worker = task['owner'] if attempt['phase']=='produce' else task['reviewer']
                if attempt['phase'] not in {'produce','review'} or attempt['worker']!=expected_worker or attempt['expires']<=attempt['started'] or attempt['status'] not in {'running','delivered','reviewed','failed','expired'}:
                    raise ValueError('Invalid attempt snapshot')
                if attempt['status']=='running' and task.get('attempt_id')!=attempt['id']:
                    raise ValueError('Orphan active attempt')
            for row in self.db.execute('SELECT * FROM usage'):
                if row['reserved_tokens']<=0 or not math.isfinite(row['reserved_usd']) or row['reserved_usd']<=0 or row['state'] not in {'reserved','settled','unknown'}:
                    raise ValueError('Invalid usage ledger')
            for row in self.db.execute('SELECT envelope FROM events'):
                if json.loads(row[0])['task_id'] not in tasks:
                    raise ValueError('Orphan message')
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
