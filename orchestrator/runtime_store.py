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
from .task_leases import claim as lease_claim, checkpoint as lease_checkpoint

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
          CREATE TABLE IF NOT EXISTS usage(call_id TEXT PRIMARY KEY, attempt_id TEXT NOT NULL REFERENCES attempts(id), provider TEXT NOT NULL, reserved_tokens INTEGER NOT NULL, reserved_usd REAL, state TEXT NOT NULL, actual_input INTEGER, actual_output INTEGER, actual_usd REAL, agent_id TEXT, model TEXT, response_id TEXT, report_sha256 TEXT);
          CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        ''')
        # Additive migration for snapshots created before provider response provenance.
        usage_columns = {row[1] for row in self.db.execute('PRAGMA table_info(usage)')}
        for name, declaration in (
                ('agent_id', 'TEXT'), ('model', 'TEXT'), ('response_id', 'TEXT'),
                ('report_sha256', 'TEXT')):
            if name not in usage_columns:
                self.db.execute(f'ALTER TABLE usage ADD COLUMN {name} {declaration}')
        reserved_usd_required = next(row[3] for row in self.db.execute('PRAGMA table_info(usage)')
                                     if row[1] == 'reserved_usd')
        if reserved_usd_required:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                self.db.execute('''CREATE TABLE usage_migrating(
                    call_id TEXT PRIMARY KEY,
                    attempt_id TEXT NOT NULL REFERENCES attempts(id),
                    provider TEXT NOT NULL,
                    reserved_tokens INTEGER NOT NULL,
                    reserved_usd REAL,
                    state TEXT NOT NULL,
                    actual_input INTEGER,
                    actual_output INTEGER,
                    actual_usd REAL,
                    agent_id TEXT,
                    model TEXT,
                    response_id TEXT,
                    report_sha256 TEXT)''')
                self.db.execute('''INSERT INTO usage_migrating
                    SELECT call_id,attempt_id,provider,reserved_tokens,reserved_usd,state,
                           actual_input,actual_output,actual_usd,agent_id,model,response_id,report_sha256
                    FROM usage''')
                self.db.execute('DROP TABLE usage')
                self.db.execute('ALTER TABLE usage_migrating RENAME TO usage')
                self.db.execute('COMMIT')
            except BaseException:
                if self.db.in_transaction:
                    self.db.execute('ROLLBACK')
                raise

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
        if 'stop_on_review_rejection' in task and type(task['stop_on_review_rejection']) is not bool:
            raise ValueError('stop_on_review_rejection must be boolean')
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
                if count >= task.get('max_attempts', 3) and not task.get('resume_from_attempts'):
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
            task.pop('resume_from_attempts', None)
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
                task.pop('resume_from_attempts', None)
                task.update(status='completed', lease=None, completed_at=now)
                checkpoint = {'task_id': task_id, 'result_sha256': task['result_sha256'], 'review': decision, 'coordinator': '01',
                              'input_refs': task['input_refs'], 'scope': 'read_only_technical_audit', 'human_visual_approval': False, 'youtube_publication': False}
                self.db.execute('INSERT INTO checkpoints VALUES (?,?,?)', (task_id, encode(checkpoint), fingerprint(checkpoint)))
                self._event(task, '01', task['owner'], 'task_completed', {'checkpoint_sha256': fingerprint(checkpoint)}, token, now)
            else:
                attempts = self.db.execute("SELECT count(*) FROM attempts WHERE task_id=? AND phase='produce'", (task_id,)).fetchone()[0]
                stop = task.get('stop_on_review_rejection', False)
                if type(stop) is not bool:
                    raise ValueError('stop_on_review_rejection must be boolean')
                status = 'blocked' if stop else ('dead_letter' if attempts >= task.get('max_attempts', 3) else 'ready')
                task.pop('resume_from_attempts', None)
                task.update(status=status, lease=None, available_at=now+min(60, 5*2**attempts))
                if stop:
                    task['blocked_reason'] = 'independent_review_rejected'
                event = 'task_blocked' if stop else ('task_failed' if status == 'dead_letter' else 'revision_requested')
                self._event(task, '01', task['owner'], event,
                            {'reason': 'independent_review_rejected'}, token, now)
                if stop:
                    checkpoint = {'task_id': task_id, 'result_sha256': task['result_sha256'],
                                  'review': decision, 'coordinator': '01',
                                  'input_refs': task['input_refs'],
                                  'scope': 'read_only_technical_audit',
                                  'status': 'blocked', 'blocked_reason': 'independent_review_rejected',
                                  'human_visual_approval': False, 'youtube_publication': False}
                    self.db.execute('INSERT INTO checkpoints VALUES (?,?,?)',
                                    (task_id, encode(checkpoint), fingerprint(checkpoint)))
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

    def _attempt_outputs_are_replayable(self, task_id, attempt_ids):
        placeholders = ','.join('?' for _ in attempt_ids)
        rows = self.db.execute(
            f'SELECT * FROM usage WHERE attempt_id IN ({placeholders})', attempt_ids).fetchall()
        if not rows:
            return True
        events = {}
        for row in self.db.execute('SELECT envelope FROM events'):
            event = json.loads(row['envelope'])
            content = event.get('content')
            if (event.get('task_id') == task_id and event.get('type') == 'progress_update'
                    and isinstance(content, dict) and isinstance(content.get('call_id'), str)):
                events[content['call_id']] = event
        for usage in rows:
            if usage['state'] != 'settled' or usage['report_sha256'] is None:
                return False
            event = events.get(usage['call_id'])
            if not event:
                return False
            content = event['content']
            response = content.get('response')
            if (content.get('validation_status') == 'rejected'
                    or content.get('attempt_id') != usage['attempt_id']
                    or content.get('agent_id') != usage['agent_id']
                    or event.get('sender') != usage['agent_id']
                    or content.get('recipient') != event.get('recipient')
                    or content.get('model') != usage['model']
                    or content.get('report_sha256') != usage['report_sha256']
                    or not isinstance(content.get('runtime_stage'), str)
                    or not isinstance(content.get('request_sha256'), str)
                    or not isinstance(content.get('instructions_sha256'), str)
                    or not isinstance(content.get('provider_response_sha256'), str)
                    or not isinstance(response, dict)
                    or response.get('agent_id') != usage['agent_id']
                    or response.get('human_visual_approval') is not False
                    or response.get('youtube_publication', False) is not False
                    or fingerprint(response) != usage['report_sha256']):
                return False
            for key in ('request_sha256', 'instructions_sha256', 'provider_response_sha256'):
                value = content[key]
                if len(value) != 64 or any(char not in '0123456789abcdef' for char in value):
                    return False
        return True

    def recover(self, now=None):
        now = int(time.time()) if now is None else now
        recovered = []
        with self.transaction():
            for row in self.db.execute("SELECT * FROM attempts WHERE status='running' AND expires<=?", (now,)).fetchall():
                task = self.get(row['task_id'])
                if task.get('attempt_id') != row['id']:
                    continue
                count = self.db.execute('SELECT count(*) FROM attempts WHERE task_id=? AND phase=?', (task['task_id'], row['phase'])).fetchone()[0]
                prior_resumes = task.get('resume_from_attempts', [])
                if not isinstance(prior_resumes, list) or any(not isinstance(value, str) for value in prior_resumes):
                    raise ValueError('Invalid resumable attempt journal')
                resume_attempts = list(dict.fromkeys([*prior_resumes, row['id']]))
                replayable = self._attempt_outputs_are_replayable(task['task_id'], resume_attempts)
                journaled = self.db.execute(
                    'SELECT count(*) FROM usage WHERE attempt_id IN (' +
                    ','.join('?' for _ in resume_attempts) + ')', resume_attempts).fetchone()[0]
                # A new lease may continue only from complete, hash-bound response
                # records. Unknown provider outcomes are permanently fenced.
                can_resume = replayable and (journaled > 0 or count < task.get('max_attempts', 3))
                status = ('blocked' if not replayable else
                          ('needs_review' if row['phase'] == 'review' else 'ready') if can_resume
                          else 'dead_letter')
                task.update(status=status, lease=None, available_at=now+min(60,5*2**count))
                if can_resume:
                    task['resume_from_attempts'] = resume_attempts
                elif not replayable:
                    task['blocked_reason'] = 'provider_outcome_unknown_manual_reconciliation_required'
                    self.db.execute("UPDATE usage SET state='unknown' WHERE attempt_id=? AND state='reserved'", (row['id'],))
                self._save(task, task['revision'])
                self.db.execute("UPDATE attempts SET status='expired' WHERE id=?", (row['id'],))
                event_type = ('task_blocked' if not replayable else
                              'progress_update' if can_resume else 'task_failed')
                reason = ('lease_expired_unknown_provider_outcome' if not replayable else
                          'safe_resume_from_persisted_responses' if can_resume else 'lease_expired_retry_limit_reached')
                self._event(task, '01', task['owner'], event_type, {'reason': reason, 'next_state': task['status']}, row['id'], now)
                recovered.append(task['task_id'])
        return recovered

    def reserve(self, task_id, token, revision, provider, tokens, usd, limits, now=None,
                agent_id=None, model=None):
        now = int(time.time()) if now is None else now
        if (type(tokens) is not int or tokens <= 0
                or (usd is not None and (type(usd) not in {int, float} or not math.isfinite(usd) or usd <= 0))):
            raise BudgetBlocked('Invalid conservative reservation')
        if (set(limits) != {'usd','tokens','calls'} or type(limits['tokens']) is not int or type(limits['calls']) is not int
                or limits['tokens'] <= 0 or limits['calls'] <= 0
                or (limits['usd'] is not None and (type(limits['usd']) not in {int,float}
                    or not math.isfinite(limits['usd']) or limits['usd'] <= 0))):
            raise BudgetBlocked('Positive token and call limits are required; USD may be explicitly uncapped')
        if usd is None and limits['usd'] is not None:
            raise BudgetBlocked('Unknown monetary cost cannot be reserved against a finite USD limit')
        if agent_id is not None and agent_id not in ROLES:
            raise ValueError('Unknown agent ID for usage provenance')
        if model is not None and (not isinstance(model, str) or not model.strip()):
            raise ValueError('Model provenance must be a nonempty string')
        with self.transaction():
            task = self.get(task_id)
            self._fence(task_id, token, revision, now, task['phase'])
            policy = self.db.execute("SELECT value FROM meta WHERE key='budget_policy'").fetchone()
            if policy and policy[0] != encode(limits):
                raise BudgetBlocked('Budget policy differs from durable budget')
            counts = self.db.execute('SELECT count(*),coalesce(sum(reserved_tokens),0),coalesce(sum(reserved_usd),0) FROM usage').fetchone()
            unknown_costs = self.db.execute('SELECT count(*) FROM usage WHERE reserved_usd IS NULL').fetchone()[0]
            cost_exceeded = False
            if limits['usd'] is not None:
                cost_exceeded = (unknown_costs > 0 or usd is None or counts[2]+usd > limits['usd'])
            if counts[0]+1 > limits['calls'] or counts[1]+tokens > limits['tokens'] or cost_exceeded:
                raise BudgetBlocked('Durable budget exhausted')
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('budget_policy',?)", (encode(limits),))
            call_id = uuid.uuid4().hex
            self.db.execute('''INSERT INTO usage
                (call_id,attempt_id,provider,reserved_tokens,reserved_usd,state,
                 actual_input,actual_output,actual_usd,agent_id,model,response_id,report_sha256)
                VALUES (?,?,?,?,?,?,NULL,NULL,NULL,?,?,NULL,NULL)''',
                (call_id, token, provider, tokens, usd, 'reserved', agent_id, model))
            return call_id

    def settle(self, call_id, input_tokens=None, output_tokens=None, actual_usd=None,
               agent_id=None, model=None, response_id=None, report_sha256=None,
               response=None, recipient=None, runtime_stage=None, request_sha256=None,
               instructions_sha256=None, provider_response_sha256=None,
               validation_error=None, now=None):
        now = int(time.time()) if now is None else now
        for value in (input_tokens, output_tokens):
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError('Observed token counts must be nonnegative integers')
        if actual_usd is not None and (type(actual_usd) not in {int, float} or not math.isfinite(actual_usd) or actual_usd < 0):
            raise ValueError('Observed USD amount must be finite and nonnegative')
        if agent_id is not None and agent_id not in ROLES:
            raise ValueError('Unknown agent ID for usage provenance')
        if model is not None and (not isinstance(model, str) or not model.strip()):
            raise ValueError('Model provenance must be a nonempty string')
        if response_id is not None and (not isinstance(response_id, str) or not response_id.strip()):
            raise ValueError('Provider response ID must be a nonempty string')
        if report_sha256 is not None and (not isinstance(report_sha256, str) or len(report_sha256) != 64
                                          or any(c not in '0123456789abcdef' for c in report_sha256)):
            raise ValueError('Report provenance must be a lowercase SHA-256 digest')
        if validation_error is not None:
            if (not isinstance(validation_error, str)
                    or not 1 <= len(validation_error) <= 160
                    or any(ord(c) in (10, 13) for c in validation_error)):
                raise ValueError('Invalid model response rejection code')
        if response is not None:
            if not isinstance(response, dict) or agent_id not in ROLES or not model:
                raise ValueError('Durable model response requires a structured object, agent ID and model')
            if response.get('agent_id') != agent_id:
                raise ValueError('Response agent attribution differs from invocation')
            if recipient is not None and recipient not in ROLES:
                raise ValueError('Unknown response recipient')
            if not isinstance(runtime_stage, str) or not runtime_stage.strip() or len(runtime_stage) > 80:
                raise ValueError('Invalid runtime stage')
            for name, digest in (('request_sha256', request_sha256),
                                 ('instructions_sha256', instructions_sha256),
                                 ('provider_response_sha256', provider_response_sha256)):
                if (not isinstance(digest, str) or len(digest) != 64
                        or any(char not in '0123456789abcdef' for char in digest)):
                    raise ValueError(f'{name} must be a lowercase SHA-256 digest')
            if response.get('human_visual_approval') is not False or response.get('youtube_publication', False) is not False:
                raise ValueError('Read-only model response may not approve or publish production')
            response_digest = fingerprint(response)
            if report_sha256 is not None and report_sha256 != response_digest:
                raise ValueError('Response digest differs from report provenance')
            report_sha256 = response_digest
            if len(encode(response).encode('utf-8')) > 1_000_000:
                raise ValueError('Structured model response exceeds persistence limit')
        with self.transaction():
            row = self.db.execute("SELECT state,agent_id,model,attempt_id FROM usage WHERE call_id=?", (call_id,)).fetchone()
            if not row or row[0] != 'reserved':
                raise Conflict('Unknown or settled call')
            if row['agent_id'] is not None and agent_id is not None and row['agent_id'] != agent_id:
                raise Conflict('Agent provenance differs from the reserved invocation')
            if row['model'] is not None and model is not None and row['model'] != model:
                raise Conflict('Model provenance differs from the reserved invocation')
            self.db.execute('''UPDATE usage SET state=?,actual_input=?,actual_output=?,actual_usd=?,
                               agent_id=coalesce(agent_id,?),model=coalesce(model,?),response_id=?,report_sha256=?
                               WHERE call_id=?''',
                            ('settled' if input_tokens is not None and output_tokens is not None else 'unknown',
                             input_tokens, output_tokens, actual_usd, agent_id, model, response_id, report_sha256, call_id))
            if response is not None or validation_error is not None:
                attempt = self.db.execute('SELECT task_id,worker FROM attempts WHERE id=?', (row['attempt_id'],)).fetchone()
                task = self.get(attempt['task_id'])
                sender = agent_id or row['agent_id'] or attempt['worker']
                target = recipient or '01'
                if model is None and row['model'] is None:
                    raise ValueError('Durable model response requires model provenance')
                content = {'call_id': call_id, 'attempt_id': row['attempt_id'],
                           'agent_id': sender, 'recipient': target,
                           'model': model or row['model'], 'response_id': response_id,
                           'runtime_stage': runtime_stage,
                           'request_sha256': request_sha256,
                           'instructions_sha256': instructions_sha256,
                           'provider_response_sha256': provider_response_sha256,
                           'report_sha256': report_sha256,
                           'validation_status': 'rejected' if validation_error else 'accepted'}
                if response is not None:
                    content['response'] = response
                if validation_error:
                    content['validation_error'] = validation_error
                self._event(task, sender, target, 'progress_update', content, call_id, now)

    def invocation_responses(self, task_id, attempt_ids=None):
        """Return durably recorded structured model outputs in event order."""
        self.get(task_id)  # Validate task existence before exposing its history.
        allowed_attempts = None if attempt_ids is None else set(attempt_ids)
        rows = self.db.execute('SELECT envelope FROM events ORDER BY seq').fetchall()
        responses = []
        for row in rows:
            event = json.loads(row['envelope'])
            content = event.get('content', {})
            if (event.get('task_id') == task_id and event['type'] == 'progress_update'
                    and isinstance(content, dict) and 'call_id' in content and 'response' in content
                    and content.get('validation_status') != 'rejected'
                    and (allowed_attempts is None or content.get('attempt_id') in allowed_attempts)):
                responses.append(event)
        return responses

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
                    row = dict(row)
                    if table == 'usage':
                        # Older canonical snapshots predate call provenance fields.
                        for field in ('agent_id', 'model', 'response_id', 'report_sha256'):
                            row.setdefault(field, None)
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
                reserved_usd = row['reserved_usd']
                actual_usd = row['actual_usd']
                if (row['reserved_tokens'] <= 0
                        or (reserved_usd is not None and (not math.isfinite(reserved_usd) or reserved_usd <= 0))
                        or (actual_usd is not None and (not math.isfinite(actual_usd) or actual_usd < 0))
                        or row['state'] not in {'reserved','settled','unknown'}):
                    raise ValueError('Invalid usage ledger')
                if row['agent_id'] is not None and row['agent_id'] not in ROLES:
                    raise ValueError('Invalid usage agent provenance')
                if row['model'] is not None and (not isinstance(row['model'], str) or not row['model'].strip()):
                    raise ValueError('Invalid usage model provenance')
                if row['response_id'] is not None and (not isinstance(row['response_id'], str) or not row['response_id'].strip()):
                    raise ValueError('Invalid provider response ID')
                if row['report_sha256'] is not None and (len(row['report_sha256']) != 64
                        or any(c not in '0123456789abcdef' for c in row['report_sha256'])):
                    raise ValueError('Invalid usage report digest')
            for row in self.db.execute('SELECT envelope FROM events'):
                if json.loads(row[0])['task_id'] not in tasks:
                    raise ValueError('Orphan message')
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
