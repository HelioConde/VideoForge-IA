"""Build a source-verified, read-only C07/C08 documentary QA report.

Reuses the four historical Astra usage records and the two accepted agent
outputs. This never calls a model or changes task status/production assets.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from .agent_bus import fingerprint
from .chain_recovery import assess, STATE_PATH, MODEL
from .runtime import (
    ROOT, CHAIN_FACETS, _validate_chain_stage, read_context, write_report,
)
from .runtime_store import Store


def validated_shot_timeline(shots: object) -> list[dict]:
    """Reject overlaps, missing frames, duplicate IDs and malformed shot records."""
    if not isinstance(shots, list) or not shots:
        raise ValueError("Missing pinned shot list")
    timeline = []
    prev = None
    seen = set()
    for shot in shots:
        if not isinstance(shot, dict):
            raise ValueError("Invalid shot record")
        start, end = shot.get('start_frame'), shot.get('end_exclusive')
        shot_id, beat = shot.get('id'), shot.get('beat')
        if (type(start) is not int or type(end) is not int or start >= end
                or (prev is not None and start != prev)
                or not isinstance(shot_id, str) or not shot_id or shot_id in seen
                or not isinstance(beat, str) or not beat):
            raise ValueError("Pinned manifest shot timeline has overlap, gap or duplicate")
        seen.add(shot_id)
        timeline.append({
            'id': shot_id, 'beat': beat,
            'start_frame': start, 'end_exclusive': end,
        })
        prev = end
    return timeline


def build_evidence(store: Store, root=ROOT) -> dict:
    tasks = [row['task_id'] for row in store.db.execute("SELECT task_id FROM tasks")]
    if len(tasks) != 1:
        raise ValueError("Only a single pinned C07/C08 task can be audited")
    task_id = tasks[0]
    recovery = assess(store, task_id)
    task = store.get(task_id)
    checkpoint = store.db.execute(
        "SELECT content,sha256 FROM checkpoints WHERE task_id=?", (task_id,)).fetchone()
    if checkpoint is None:
        raise ValueError("Missing blocked provenance checkpoint")
    saved_checkpoint = json.loads(checkpoint['content'])
    if (fingerprint(saved_checkpoint) != checkpoint['sha256']
            or saved_checkpoint.get('scope') != recovery['scope']
            or saved_checkpoint.get('status') != 'blocked'
            or saved_checkpoint.get('calls') != recovery['calls']):
        raise ValueError("Blocked checkpoint does not match settled historical calls")

    # Enforce the exact hash pinned to the original model prompt. If the
    # manifest changes, fail closed; do not quietly audit a newer revision.
    context = read_context(root, task)
    source_ref, = task['input_refs']
    manifest = json.loads(context[source_ref])
    producer = store.result(task_id)
    if (producer.get('agent_id') != '03'
            or producer.get('human_visual_approval') is not False
            or producer.get('execution_mode') != 'codex_proxy'):
        raise ValueError("Unexpected specialist report")
    analysis = producer.get('analysis', {}).get('response', {})
    if analysis.get('agent_id') != '03' or analysis.get('human_visual_approval') is not False:
        raise ValueError("Specialist response identity/approval is invalid")

    qa_events = []
    for row in store.db.execute("SELECT envelope FROM events ORDER BY seq"):
        event = json.loads(row['envelope'])
        if (event.get('task_id') == task_id and event.get('type') == 'progress_update'
                and event.get('content', {}).get('runtime_stage') == 'independent_qa_review'):
            qa_events.append(event)
    if len(qa_events) != 1:
        raise ValueError("Expected exactly one independent QA response")
    qa_event = qa_events[0]
    qa_response = qa_event['content'].get('response', {})
    if (qa_response.get('agent_id') != '12'
            or qa_response.get('human_visual_approval') is not False):
        raise ValueError("Independent reviewer identity/approval is invalid")

    # Recheck facet coverage, IDs, source paths, JSON Pointers and each
    # underlying source value SHA. No model output may supply its own source.
    _validate_chain_stage(root, task, {}, '03', 'scene_continuity_analysis', analysis)
    _validate_chain_stage(
        root, task, {'producer_report': producer}, '12',
        'independent_qa_review', qa_response,
    )
    produced = {finding['facet']: finding for finding in analysis['findings']}
    reviewed = {finding['facet']: finding for finding in qa_response['findings']}
    if set(produced) != set(CHAIN_FACETS) or set(reviewed) != set(CHAIN_FACETS):
        raise ValueError("Missing or duplicate audit facets")
    facets = []
    for facet in CHAIN_FACETS:
        a, b = produced[facet], reviewed[facet]
        facets.append({
            'facet': facet,
            'finding_id': a['id'],
            'claim': a['claim'],
            'recommendation': a['recommendation'],
            'evidence': a['evidence'],
            'qa_decision': b['decision'],
            'qa_rationale': b['rationale'],
            'qa_reviewed_finding_ids': b['reviewed_finding_ids'],
            'qa_evidence': b['evidence'],
            'review_scope': 'documentary_manifest_only',
        })

    timeline = validated_shot_timeline(manifest.get('shots'))

    usage = [dict(row) for row in store.db.execute(
        """SELECT usage.* FROM usage JOIN attempts ON usage.attempt_id = attempts.id
           WHERE attempts.task_id=? ORDER BY usage.rowid""", (task_id,))]
    return {
        'schema_version': 1,
        'kind': 'historical_astra_documentary_qa_evidence',
        'task_id': task_id,
        'task_status': 'blocked',
        'checkpoint_scope': recovery['scope'],
        'checkpoint_sha256': checkpoint['sha256'],
        'pinned_manifest_ref': source_ref,
        'pinned_manifest_sha256': task['input_refs'][source_ref],
        'model': MODEL,
        'agent_route': ['01', '03', '12', '01'],
        'live_calls_previously_recorded': len(usage),
        'input_tokens_previously_recorded': sum(x['actual_input'] for x in usage),
        'output_tokens_previously_recorded': sum(x['actual_output'] for x in usage),
        'usd_billing_status': 'unknown',
        'additional_inference_requests': 0,
        'documentary_qa_all_supported': all(x['qa_decision'] == 'supported' for x in facets),
        'final_director_consolidation_accepted': False,
        'final_director_response_available': recovery['final_output_journaled'],
        'visual_frames_inspected': 0,
        'human_visual_approval': False,
        'youtube_publications': 0,
        'production_files_modified': False,
        'creator_feedback': manifest.get('creator_feedback'),
        'continuity_rules': manifest.get('rules'),
        'editorial_shot_plan': timeline,
        'facets': facets,
        'next_required_review': [
            'Inspect generated images and rendered transitions against the pinned shot plan',
            'Reconcile the missing historical Director 01 final response only from authentic evidence',
            'Obtain human approval before modifying or publishing production scenes',
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--snapshot', type=Path,
                       help='Read an already-downloaded snapshot JSON, no network')
    group.add_argument('--github-state', action='store_true',
                       help='Read GitHub state branch (GET only, no mutation)')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.github_state:
        from .github_state import GitHubState
        snapshot = GitHubState(path=STATE_PATH, initialize=False).load()
        if snapshot is None:
            parser.error('State branch lacks the pinned audit')
    else:
        snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))

    with tempfile.TemporaryDirectory(prefix='vf-documentary-evidence-') as tmp:
        store = Store(Path(tmp) / 'history.sqlite')
        try:
            store.import_snapshot(snapshot)
            result = build_evidence(store)
        finally:
            store.close()
    write_report(args.output, result)
    print(json.dumps({
        'task_status': result['task_status'],
        'facet_count': len(result['facets']),
        'documentary_qa_all_supported': result['documentary_qa_all_supported'],
        'final_director_consolidation_accepted': False,
        'new_inference': 0,
        'youtube_publications': 0,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
