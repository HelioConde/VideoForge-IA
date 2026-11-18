"""Explicit Issue checkpoint publication with durable intent and reconciliation.

An ambiguous POST is never repeated automatically. Issues are a projection, not
the transactional task database. Caller must use the GitHub CAS-backed Store.
"""
import json
from .github_state import GitHubState, GitHubStateError
from .agent_bus import fingerprint


def publish(store, issue_number, client=None):
    if store.persist_callback is None:
        raise ValueError('Publishing requires durable remote outbox')
    if type(issue_number) is not int or issue_number <= 0:
        raise ValueError('Invalid Issue number')
    client = client or GitHubState()
    url = f'{client.API}/repos/{client.repo}/issues/{issue_number}'
    code, issue = client._request('GET', url)
    if code != 200 or issue.get('pull_request') or issue.get('state') != 'open':
        raise GitHubStateError('Checkpoint target must be an open Issue')
    comments = []
    for page in range(1, 101):
        code, batch = client._request('GET', url+f'/comments?per_page=100&page={page}')
        if code != 200 or not isinstance(batch,list):
            raise GitHubStateError('Cannot reconcile checkpoint comments')
        comments.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise GitHubStateError('Issue comment reconciliation bound exceeded')
    outcomes = []
    for row in store.export_snapshot()['tables']['checkpoints']:
        checkpoint = json.loads(row['content'])
        if fingerprint(checkpoint) != row['sha256']:
            raise ValueError('Corrupt checkpoint')
        marker = '<!-- videoforge-runtime:'+row['sha256']+' -->'
        key = f'issue:{issue_number}:{row["sha256"]}'
        existing = [c for c in comments if marker in (c.get('body') or '')]
        if len(existing) > 1:
            raise GitHubStateError('Duplicated checkpoint comments need manual review')
        if existing:
            with store.transaction():
                store.db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (key,json.dumps({'state':'published','comment_id':existing[0]['id']})))
            outcomes.append({'checkpoint':row['sha256'],'status':'reconciled'})
            continue
        with store.transaction():
            prior = store.db.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
            if prior:
                outcomes.append({'checkpoint':row['sha256'],'status':'pending_manual_reconciliation'})
                continue
            store.db.execute('INSERT INTO meta VALUES (?,?)',(key,json.dumps({'state':'posting_intent'})))
        # The transaction's remote CAS has completed. No second writer can reserve this intent.
        body = (marker+'\n## Checkpoint técnico do runtime\n'
                f'- Tarefa de auditoria: `{row["task_id"]}`\n'
                f'- SHA-256: `{row["sha256"]}`\n'
                '- Revisão técnica independente concluída. Não é aprovação visual ou humana.\n'
                '- Nenhum asset alterado, render ou publicação de vídeo executado.\n')
        code, result = client._request('POST',url+'/comments',{'body':body})
        if code != 201 or not isinstance(result.get('id'),int):
            raise GitHubStateError('Checkpoint POST not confirmed; intent retained, no automatic replay')
        with store.transaction():
            store.db.execute('UPDATE meta SET value=? WHERE key=?',(json.dumps({'state':'published','comment_id':result['id']}),key))
        comments.append(result)
        outcomes.append({'checkpoint':row['sha256'],'status':'published','comment_id':result['id']})
    return outcomes
