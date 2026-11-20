"""Resumable, camera-only EP01 previews. Never generates art or approves a rig."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EP = Path('canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01')
OUT = Path('output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/previews/camera-batch-v1')
SCHEMA = 'videoforge/ep01-camera-batch/v1'
P03 = 'assets/geracoes/production-scene-mother-orientation-v3/44151964491/c01-p03-scene-mother-facing-throne-v3.png'
P03_SHA = 'e668f713456dd5a41e312885f66c10e2cc033c3aed69ffb7bb577a7d62f79b3d'
DEFAULT = ['C01-P01', 'C01-P02', 'C01-P03', 'C01-P04']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, doc):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_source(root, source):
    path = root / source['file']
    if path.is_symlink() or not path.resolve().is_relative_to((root / EP).resolve()):
        raise ValueError('Source outside episode or symlink')
    if sha(path) != source['sha256']:
        raise ValueError('Source SHA mismatch: ' + source['file'])
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Source is not PNG')
    size = list(struct.unpack('>II', raw[16:24]))
    if size != source['dimensions']:
        raise ValueError('Source dimensions mismatch')
    return path


def build_plan(root=ROOT, revision='legacy'):
    if revision == 'continuity-v3':
        from .ep01_continuity_v3 import revised_camera_plan
        return revised_camera_plan(build_plan(root, 'continuity-v2'), root, require_generated=True)
    if revision == 'continuity-v2':
        from .ep01_continuity_v2 import revised_camera_plan
        return revised_camera_plan(build_plan(root, 'legacy'), root, require_generated=True)
    if revision != 'legacy':
        raise ValueError('Invalid continuity revision')

    """Join the real inventory to editorial timecodes; old missing counts are ignored."""
    ep = root / EP
    inventory = read(ep / 'CHECKPOINT-IMAGENS-EP01-AUTO.json')['original_mothers']
    editorial = read(ep / 'PLANO-CAMADAS-CAMERA-EP01.json')['shots']
    story = read(ep / 'roteiro.json')
    approvals = read(ep / 'APROVACOES-VISUAIS-C01-V3.json')
    policy = read(ep / 'POLITICA-SEM-MAOS-INDEPENDENTES-C01-P04.json')
    if policy['status'] != 'active' or approvals['approval_scope'] != 'individual_exact_sha_only':
        raise ValueError('Approval/hand policy changed; review required')
    approved = [a for a in approvals['approvals'] if a.get('approved_for_visual_reference') is True and a.get('visual_status') == 'approved_by_creator']
    p04 = next(a for a in approved if a.get('shot_id', a.get('shot')) == 'C01-P04')
    shots = []
    previous_end = 0
    for entry in editorial:
        sid = entry['id']
        timing = entry['timecode_frames']
        start, end = timing['start'], timing['end_exclusive']
        if start != previous_end or end <= start:
            raise ValueError('Non-contiguous editorial timeline')
        previous_end = end
        source = None if sid == 'C01-P01' else dict(inventory[sid])
        # Reuse the exact individually approved mother, without editing its pixels.
        if sid == 'C01-P04':
            source = {'file': p04['file'], 'sha256': p04['sha256'], 'dimensions': p04['native_dimensions']}
        if sid == 'C01-P03':
            source = {'file': (EP / P03).as_posix(), 'sha256': P03_SHA, 'dimensions': [941, 1672]}
        if source:
            checked_source(root, source)
        evidence = [a for a in approved if a.get('shot_id', a.get('shot')) == sid and source and a['sha256'] == source['sha256']]
        # Imported evidence only; no human-approval field is written or promoted here.
        status = 'exact_sha_approval_record_exists' if evidence else ('not_applicable_black' if not source else 'pending_human_review')
        camera = {'mode': 'static', 'start': {'zoom': 1, 'x': 50, 'y': 50}, 'end': {'zoom': 1, 'x': 50, 'y': 50}, 'dolly': 0, 'true_parallax': False}
        focus = {'mode': 'original_painted_focus', 'blur_start_px': 0, 'blur_end_px': 0}
        light = {'exposure_start': 1, 'exposure_end': 1, 'warm_glow': 0}
        limitations = ['No approved same-shot rig selected; all characters and contacts remain integrated.', 'Anatomy, continuity and cinematic approval require human review.']
        needs = []
        if sid == 'C01-P02':
            camera.update(mode='digital_detail_reveal', start={'zoom': 1.06, 'x': 47, 'y': 47}, end={'zoom': 1.015, 'x': 50, 'y': 50})
            light = {'exposure_start': 0, 'exposure_end': 1, 'warm_glow': 0.06}
            limitations += ['No physical unsheathing: sword and scabbard are one painted image.', 'Original lower glove/scabbard contact rejected in REVISAO-ERRO-PAINEIS-C01-P02.json; diagnostic preview only, not repaired.']
            status = 'diagnostic_only_contact_rejected'
            needs = ['Approved integrated arm/grip/sword assembly, scabbard and reconstructed background; no standalone hands.']
        elif sid == 'C01-P03':
            camera.update(mode='digital_reveal_kael_to_throne', start={'zoom': 1.12, 'x': 40, 'y': 66}, end={'zoom': 1, 'x': 50, 'y': 50})
            focus = {'mode': 'global_optical_simulation_not_depth_focus', 'blur_start_px': 0.7, 'blur_end_px': 0}
            limitations += ['V3 candidate faces the king; king standing differs from seated-king continuity in P04. Camera cannot fix that staging.', 'No reflection or axis reversal applied; V3 is not individually approved.']
            needs = ['Same-V3 approved hair/cape with reconstructed underlays before any mesh rig.']
        elif sid == 'C01-P04':
            camera.update(mode='digital_establishing_reveal', start={'zoom': 1.075, 'x': 50, 'y': 50})
            light['warm_glow'] = 0.055
            limitations += ['Preserve integrated guard/spear grip; no R3/W3 pieces.']
        shots.append({'id': sid, 'narrative_beat': entry['editorial_beat'], 'start_frame': start, 'duration_frames': end-start, 'fps': 30,
                      'source': source, 'approval_status': status, 'camera': camera, 'focus': focus, 'lighting': light,
                      'points_of_interest': [entry['camera']['primary_focus']],
                      'allowed_motion': ['digital_camera', 'global_light', 'global_focus'] if source else [],
                      'transitions': {'in': 'exposure_reveal' if sid == 'C01-P02' else 'cut', 'out': 'cut'},
                      'rig': {'enabled': False, 'independent_hands': False, 'required_components': needs},
                      'qa_required': ['source_sha', 'codec_frames_fps_duration', 'decode_every_frame', 'unexpected_black', 'representative_contact_sheet', 'human_anatomy_axis_continuity_review'],
                      'limitations': limitations, 'direction_reviewed': sid in DEFAULT})
    if len(shots) != 40 or len(inventory) != 39 or previous_end != story['format']['duration_frames']:
        raise ValueError('Inventory/editorial/story mismatch')
    return {'schema': SCHEMA, 'technical_preview_only': True, 'official_episode_approved': False, 'youtube_upload': False,
            'image_provider_calls': 0, 'audio_status': 'not_included_not_approved', 'shots': shots}


def fingerprint(root, props):
    deps = ['videoforge/ep01_camera_batch.py', 'motion-remotion/src/ep01-camera-batch.tsx', 'motion-remotion/package-lock.json']
    deps += [(EP / name).as_posix() for name in ['APROVACOES-VISUAIS-C01-V3.json', 'POLITICA-SEM-MAOS-INDEPENDENTES-C01-P04.json', 'REVISAO-ERRO-PAINEIS-C01-P02.json']]
    if props.get('revision') == 'continuity-v3':
        deps += [(EP / 'CORRECAO-CENARIOS-TRONO-V3.json').as_posix(),
                 'videoforge/ep01_continuity_v3.py']
    if props.get('revision') == 'continuity-v2':
        deps += [(EP / 'CONTINUIDADE-C07-C08-V2.json').as_posix(),
                 (EP / 'PROPOSTA-MOVIMENTO-C07-C08-V1.json').as_posix(),
                 'videoforge/ep01_continuity_v2.py',
                 'videoforge/ep01_continuity_motion.py']
    payload = {'props': props, 'code_and_policies': {p: sha(root / p) for p in deps}}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def prepare(root=ROOT, selected=None, revision='legacy'):
    plan = build_plan(root, revision)
    write(root / OUT / ('execution-plan-42-continuity-v3.json' if revision == 'continuity-v3' else 'execution-plan-42-continuity-v2.json' if revision == 'continuity-v2' else 'execution-plan-40.json'), plan)
    selected = DEFAULT if selected is None else selected
    known = {s['id'] for s in plan['shots']}
    if not selected or len(set(selected)) != len(selected) or not set(selected) <= known:
        raise ValueError('Unknown, duplicate or empty shot selection')
    shots = [s for s in plan['shots'] if s['id'] in selected]
    props = {k: v for k, v in plan.items() if k != 'shots'}
    props['shots'] = shots
    props['durationFrames'] = sum(s['duration_frames'] for s in shots)
    for shot in shots:
        if shot['source']:
            src = checked_source(root, shot['source'])
            public = 'vf-ep01-camera-batch/' + shot['source']['sha256'] + '.png'
            dest = root / 'motion-remotion/public' / public
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists() or sha(dest) != shot['source']['sha256']:
                shutil.copyfile(src, dest)
            shot['sourceFile'] = public
    return props


def verify_video(path, frames, black_ranges=()):
    """Decode EVERY frame, check metadata and unexpected near-black pictures."""
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(path)], text=True))['streams'][0]
    if (probe['codec_name'], probe['width'], probe['height'], probe['avg_frame_rate'], int(probe['nb_frames'])) != ('h264', 540, 960, '30/1', frames):
        raise ValueError('Video metadata mismatch')
    if abs(float(probe['duration']) - frames / 30) > 1/30:
        raise ValueError('Video duration mismatch')
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path), '-vf', 'scale=32:32,format=gray', '-f', 'rawvideo', '-'], check=True, capture_output=True).stdout
    if len(raw) != frames * 1024:
        raise ValueError('Decoded frame count mismatch')
    black = []
    for f in range(frames):
        # Ignore bottom watermark region; assess picture rather than its label.
        picture = raw[f*1024:f*1024+28*32]
        if max(picture) <= 12 and sum(picture) / len(picture) < 10:
            black.append(f)
    unexpected = [f for f in black if not any(a <= f < b for a, b in black_ranges)]
    if unexpected:
        raise ValueError('Unexpected black frames: ' + str(unexpected[:20]))
    return {'frames_verified': frames, 'all_frames_decoded': True, 'black_frames': black, 'unexpected_black_frames': [],
            'duration_seconds': float(probe['duration']), 'resolution': [540, 960], 'codec': 'h264', 'fps': 30, 'mp4_sha256': sha(path), 'mp4_bytes': path.stat().st_size}


def black_ranges(props):
    offset, ranges = 0, []
    for shot in props['shots']:
        if not shot['source']:
            ranges.append((offset, offset + shot['duration_frames']))
        elif shot['id'] == 'C01-P02':
            ranges.append((offset, offset + 8))
        offset += shot['duration_frames']
    return ranges


def cache_valid(root, folder, props):
    report, video = folder / 'qa.json', folder / 'preview.mp4'
    if not report.exists() or not video.exists():
        return False
    try:
        old = read(report)
        return (old['input_fingerprint'] == fingerprint(root, props) and old['mp4_sha256'] == sha(video)
                and old['technical_qa_passed'] is True and old['all_frames_decoded'] is True)
    except (ValueError, KeyError, OSError):
        return False


def render_one(root, name, props):
    folder = root / OUT / name
    if cache_valid(root, folder, props):
        print('SKIP_VALIDATED ' + name, flush=True)
        return read(folder / 'qa.json')
    write(folder / 'props.json', props)
    executable = root / 'motion-remotion/node_modules/.bin' / ('remotion.cmd' if os.name == 'nt' else 'remotion')
    subprocess.run([str(executable), 'render', 'src/ep01-camera-batch.tsx', 'EP01CameraBatch', str(folder / 'preview.mp4'),
                    '--props=' + str(folder / 'props.json'), '--codec=h264', '--concurrency=2', '--log=error'], cwd=root / 'motion-remotion', check=True)
    result = verify_video(folder / 'preview.mp4', props['durationFrames'], black_ranges(props))
    result.update(input_fingerprint=fingerprint(root, props), technical_qa_passed=True, technical_preview_only=True,
                  human_visual_review='pending', character_rig_approved=False, official_episode_approved=False, youtube_upload=False,
                  image_provider_calls=0, audio_status='not_included', source_sha256={s['id']: s['source']['sha256'] if s['source'] else None for s in props['shots']})
    # Nine temporally spaced frames in a compact review sheet (not a substitute for watching).
    step = max(1, (props['durationFrames'] - 1) // 8)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(folder/'preview.mp4'), '-vf',
                    f'select=not(mod(n\\,{step})),scale=180:320,tile=3x3', '-frames:v', '1', str(folder/'contact-sheet.jpg')], check=True)
    write(folder / 'qa.json', result)
    return result


def run(root=ROOT, selected=None, revision='legacy'):
    props = prepare(root, selected, revision)
    reports = {}
    # Preserve validated progress across different selections, not only this invocation.
    plan = build_plan(root, revision)
    for shot in plan['shots']:
        if shot['source']:
            shot['sourceFile'] = 'vf-ep01-camera-batch/' + shot['source']['sha256'] + '.png'
        one = dict(props, shots=[shot], durationFrames=shot['duration_frames'])
        folder = root / OUT / shot['id']
        if cache_valid(root, folder, one):
            reports[shot['id']] = read(folder / 'qa.json')
    checkpoint = {'schema': SCHEMA, 'official_episode_approved': False, 'youtube_upload': False, 'shots': reports}
    for shot in props['shots']:
        one = dict(props, shots=[shot], durationFrames=shot['duration_frames'])
        reports[shot['id']] = render_one(root, shot['id'], one)
        checkpoint['next_task'] = next((s['id'] for s in build_plan(root, revision)['shots'] if s['id'] not in reports), 'review_contact_continuity_and_human_approval')
        write(root / OUT / 'checkpoint.json', checkpoint)
    ids = '-'.join(s['id'] for s in props['shots'])
    montage_id = 'montage-' + (ids if len(props['shots']) <= 4 else hashlib.sha256(ids.encode()).hexdigest()[:16])
    checkpoint['montage'] = render_one(root, montage_id, props)
    checkpoint['selected_shots'] = [s['id'] for s in props['shots']]
    checkpoint['human_review_priority'] = ['C01-P02 rejected contact', 'C01-P03 standing/seated king continuity', 'C01-P04 camera motion']
    if revision == 'continuity-v3':
        checkpoint['human_review_priority'] = ['C07 meeting must use different market background', 'C08 cart must block alone with no guards', 'C08 escape uses different stairs', 'C01-P03/C01-P05 king seated consistently with approved C01-P04', 'C09 upper courtyard matches escape']

    checkpoint['visual_shots_pending_individual_approval'] = sum(s['source'] is not None and s['approval_status'] != 'exact_sha_approval_record_exists' for s in build_plan(root, revision)['shots'])
    write(root / OUT / 'checkpoint.json', checkpoint)
    print(json.dumps({'validated': list(reports), 'montage': montage_id, 'next_task': checkpoint['next_task']}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'render'])
    parser.add_argument('--shots', default=','.join(DEFAULT), help='Comma-separated shot IDs or all')
    parser.add_argument('--revision', choices=['legacy', 'continuity-v2', 'continuity-v3'], default='legacy')
    args = parser.parse_args()
    selected = [s['id'] for s in build_plan(revision=args.revision)['shots']] if args.shots == 'all' else args.shots.split(',')
    if args.action == 'prepare':
        props = prepare(selected=selected, revision=args.revision)
        write(ROOT / OUT / 'selected-props.json', props)
        print(json.dumps({'shots_planned': len(build_plan(revision=args.revision)['shots']), 'selected': selected, 'no_image_calls': True}))
    else:
        run(selected=selected, revision=args.revision)


if __name__ == '__main__':
    main()
