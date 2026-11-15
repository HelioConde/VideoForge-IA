import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from videoforge import directed_rig as rig
from videoforge.rig_candidate import _image, _write_png


class DirectedRigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dp, self.bp = self.root/'direction.json', self.root/'bindings.json'
        pixels = bytearray([20, 30, 40, 255] * 16)
        _write_png(self.root/'mother.png', pixels, 4, 4)
        _write_png(self.root/'sprite.png', pixels, 4, 4)
        def source(name):
            return {'file': name, 'sha256': hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
        track = {'target': 'actor.head', 'transform': 'rotationZ', 'unit': 'degrees', 'easing': 'easeInOutCubic',
                 'keyframes': [{'frame': 0, 'value': 0}, {'frame': 9, 'value': 1}]}
        self.direction = {'schema': 'videoforge/direcao-rig-remotion/v1', 'channel': 'test', 'video_id': 'episode',
                          'format': {'width': 1080, 'height': 1920, 'fps': 30, 'durationInFrames': 10},
                          'scenes': [{'id': 'C01', 'shots': [{'id': 'C01-P01', 'startFrame': 0,
                                      'endFrameExclusive': 10, 'rigKeyframes': [track], 'camera': {}}]}]}
        node = {'id': 'actor.head', 'parent': None, 'pivot': [2, 2], 'role': 'head',
                'z': 1, 'bbox': [1, 1, 2, 2], **source('sprite.png')}
        self.bindings = {'schema': 'videoforge/direction-bindings/v1', 'channel': 'test', 'video_id': 'episode',
                         'shots': {'C01-P01': {'canvas': {'width': 4, 'height': 4},
                                    'sourceMother': source('mother.png'), 'background': source('mother.png'),
                                    'nodes': [node], 'warnings': ['unapproved artwork']}}}

    def save(self):
        self.dp.write_text(json.dumps(self.direction), encoding='utf-8')
        self.bp.write_text(json.dumps(self.bindings), encoding='utf-8')

    def check_rejected(self):
        self.save()
        with self.assertRaises(rig.DirectedRigError):
            rig.inspect(self.dp, self.bp)

    def test_coverage_missing_mapping_and_targets(self):
        self.bindings['shots'] = {}
        self.save()
        result = rig.inspect(self.dp, self.bp)
        self.assertEqual(result['shotCount'], 1)
        self.assertEqual(result['trackCount'], 1)
        self.assertFalse(result['approval'])
        self.assertIn('missing_shot_binding', result['shots'][0]['blockers'])

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for existing PNG decoder')
    def test_prepare_pixels_flags_and_provenance(self):
        self.save()
        (self.root/'out').mkdir()
        (self.root/'out'/'coverage.json').write_text('{}')
        path = rig.prepare(self.dp, self.bp, 'C01-P01', self.root/'out', self.root/'public')
        props = json.loads(path.read_text())
        self.assertFalse(props['humanVisualReview'])
        self.assertFalse(props['publishable'])
        self.assertEqual(props['mode'], 'technical_draft')
        node = props['shots'][0]['nodes'][0]
        self.assertNotIn('sha256', node)
        self.assertEqual(_image(self.root/'public'/node['file'], 2, 2), bytearray([20, 30, 40, 255]*4))
        sources = json.loads((path.parent/'source-hashes.json').read_text())
        self.assertEqual(sources['sources']['sourceMother']['sha256'], self.bindings['shots']['C01-P01']['sourceMother']['sha256'])
        self.assertEqual(sources['manifests']['direction'], hashlib.sha256(self.dp.read_bytes()).hexdigest())
        with self.assertRaises(rig.DirectedRigError):
            rig.prepare(self.dp, self.bp, 'C01-P01', self.root/'out', self.root/'another-public')

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for existing PNG decoder')
    def test_uncovered_sprite_recovers_only_original_pixels(self):
        # One transparent pixel in the reference is the only place the new
        # patch may retain alpha; all overlapping RGB and alpha become zero.
        reference = bytearray([11, 12, 13, 255] * 16)
        reference[(2*4+2)*4:(2*4+2)*4+4] = b'\x0b\x0c\x0d\x00'
        _write_png(self.root/'reference.png', reference, 4, 4)
        patch = bytearray()
        for i in range(16):
            patch.extend((80+i, 90+i, 100+i, 255))
        _write_png(self.root/'patch.png', patch, 4, 4)
        def source(name):
            return {'file': name, 'sha256': hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
        self.bindings['shots']['C01-P01']['nodes'][0].update(**source('reference.png'))
        self.bindings['shots']['C01-P01']['nodes'].append({
            'id': 'actor.waist-patch', 'parent': None, 'pivot': [2, 2], 'role': 'diagnostic-patch',
            'z': 2, 'bbox': [1, 1, 2, 2], **source('patch.png'),
            'onlyUncoveredBy': ['actor.head'],
        })
        self.save()
        (self.root/'out').mkdir()
        props_path = rig.prepare(self.dp, self.bp, 'C01-P01', self.root/'out', self.root/'public')
        props = json.loads(props_path.read_text())
        nodes = {node['id']: node for node in props['shots'][0]['nodes']}
        packaged = nodes['actor.waist-patch']
        self.assertNotIn('onlyUncoveredBy', packaged)
        result = _image(self.root/'public'/packaged['file'], 2, 2)
        expected = bytearray(4 * 4)
        expected[:] = b'\0' * len(expected)
        expected[12:16] = patch[(2*4+2)*4:(2*4+2)*4+4]
        self.assertEqual(result, expected)
        self.assertEqual(props['pixelRecovery'], [{
            'nodeId': 'actor.waist-patch', 'sourceFile': 'patch.png',
            'sourceSha256': hashlib.sha256((self.root/'patch.png').read_bytes()).hexdigest(),
            'onlyUncoveredBy': ['actor.head'], 'uncoveredAlphaPixelsInBbox': 1,
        }])

    def test_original_mother_pixel_holdout_uses_only_existing_alpha_coverage(self):
        mother = bytearray([50, 60, 70, 255,
                            51, 61, 71, 255,
                            52, 62, 72, 255,
                            53, 63, 73, 255])
        ref = bytearray([7, 8, 9, 0, 10, 11, 12, 255,
                         13, 14, 15, 0, 16, 17, 18, 255])
        result,kept=rig._mask_only_original_covered_pixels(mother,[ref])
        self.assertEqual(kept,2)
        self.assertEqual(result[:4],b"\0\0\0\0")
        self.assertEqual(result[4:8],mother[4:8])
        self.assertEqual(result[8:12],b"\0\0\0\0")
        self.assertEqual(result[12:16],mother[12:16])
        self.assertEqual(mother[:4],bytearray([50,60,70,255]))
        with self.assertRaisesRegex(rig.DirectedRigError,"REFERENCE_CANVAS_MISMATCH"):
            rig._mask_only_original_covered_pixels(mother,[bytes(3)])

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for real PNG crops')
    def test_holdout_source_pixels_do_not_overwrite_or_generate_art(self):
        # Only real source/mother bytes can be used. A technical holdout sits
        # underneath the original head/jacket as a source-visible seam.
        original=copy.deepcopy(self.bindings)
        s=self.bindings['shots']['C01-P01']
        s['nodes'].append({
            'id':'actor.existing-cloth-holdout',
            'parent':None,'pivot':[2,2],
            'role':'existing-pixel-underlay','z':0,
            'bbox':[1,1,2,2], **s['sourceMother'],
            'onlyCoveredBy':['actor.head'],
        })
        self.save()
        (self.root/'out').mkdir()
        props_path=rig.prepare(self.dp,self.bp,'C01-P01',
                               self.root/'out',self.root/'public')
        props=json.loads(props_path.read_text())
        nodes={n['id']:n for n in props['shots'][0]['nodes']}
        layer=nodes['actor.existing-cloth-holdout']
        self.assertNotIn('onlyCoveredBy',layer)
        self.assertEqual(_image(self.root/'public'/layer['file'],2,2),
                         bytearray([20,30,40,255]*4))
        item=props['pixelRecovery'][0]
        self.assertEqual(item['role'],'existing-pixel-underlay')
        self.assertEqual(item['sourceMotherPixelsKeptInBbox'],4)
        self.assertEqual(item['sourceSha256'],s['sourceMother']['sha256'])
        self.assertEqual(item['inventedPixels'],0)
        self.bindings=original

    def test_holdout_rejects_forged_original_or_foreground_layer(self):
        original=copy.deepcopy(self.bindings)
        for problem in ('wrong_role','wrong_sha','invalid_ref','on_top','no_coverage','nested_patch'):
            with self.subTest(problem=problem):
                self.bindings=copy.deepcopy(original)
                s=self.bindings['shots']['C01-P01']
                patch={'id':'actor.existing-cloth-holdout','parent':None,
                       'pivot':[2,2],'role':'existing-pixel-underlay',
                       'z':0,'bbox':[1,1,2,2],
                       **s['sourceMother'],'onlyCoveredBy':['actor.head']}
                if problem=='wrong_role': patch['role']='ordinary-sprite'
                if problem=='wrong_sha': patch['sha256']='0'*64
                if problem=='invalid_ref': patch['onlyCoveredBy']=['missing']
                if problem=='on_top': patch['z']=3
                if problem=='no_coverage': patch['onlyCoveredBy']=[]
                if problem=='nested_patch': patch['onlyUncoveredBy']=['actor.head']
                s['nodes'].append(patch)
                self.check_rejected()
        self.bindings=original

    def test_uncovered_mask_preserves_only_uncovered_rgba_without_mutation(self):
        source = bytearray([1, 2, 3, 255, 4, 5, 6, 0])
        reference = bytes([7, 8, 9, 255, 10, 11, 12, 0])
        result, count = rig._mask_uncovered(source, [reference])
        self.assertEqual(result, bytearray([0, 0, 0, 0, 4, 5, 6, 0]))
        self.assertEqual(count, 0)
        self.assertEqual(source, bytearray([1, 2, 3, 255, 4, 5, 6, 0]))
        with self.assertRaisesRegex(rig.DirectedRigError, 'CANVAS_MISMATCH'):
            rig._mask_uncovered(source, [bytes(4)])

    def test_uncovered_references_fail_closed(self):
        original = copy.deepcopy(self.bindings)
        self.bindings['shots']['C01-P01']['nodes'].append({
            'id': 'actor.recovery', 'parent': None, 'pivot': [2, 2], 'role': 'patch',
            'z': 2, 'bbox': [1, 1, 2, 2], **{
                'file': 'sprite.png', 'sha256': hashlib.sha256((self.root/'sprite.png').read_bytes()).hexdigest()},
            'onlyUncoveredBy': ['actor.head'],
        })
        cases = {
            'empty': [], 'duplicate': ['actor.head', 'actor.head'],
            'self': ['actor.recovery'], 'missing': ['missing.sprite'],
            'group': ['actor.group'],
        }
        self.bindings['shots']['C01-P01']['nodes'].append({
            'id': 'actor.group', 'parent': None, 'pivot': [0, 0], 'role': 'group', 'z': 0,
        })
        for case, references in cases.items():
            with self.subTest(case=case):
                self.bindings = copy.deepcopy(original)
                self.bindings['shots']['C01-P01']['nodes'].append({
                    'id': 'actor.recovery', 'parent': None, 'pivot': [2, 2], 'role': 'patch',
                    'z': 2, 'bbox': [1, 1, 2, 2],
                    'file': 'sprite.png', 'sha256': hashlib.sha256((self.root/'sprite.png').read_bytes()).hexdigest(),
                    'onlyUncoveredBy': references,
                })
                if case == 'group':
                    self.bindings['shots']['C01-P01']['nodes'].append({
                        'id': 'actor.group', 'parent': None, 'pivot': [0, 0], 'role': 'group', 'z': 0,
                    })
                self.check_rejected()
        self.bindings = copy.deepcopy(original)
        self.bindings['shots']['C01-P01']['nodes'][0]['onlyUncoveredBy'] = ['actor.recovery']
        self.bindings['shots']['C01-P01']['nodes'].append({
            'id': 'actor.recovery', 'parent': None, 'pivot': [2, 2], 'role': 'patch',
            'z': 2, 'bbox': [1, 1, 2, 2], 'file': 'sprite.png',
            'sha256': hashlib.sha256((self.root/'sprite.png').read_bytes()).hexdigest(),
            'onlyUncoveredBy': ['actor.head'],
        })
        self.check_rejected()

    def test_source_hash_and_path_escape(self):
        original = copy.deepcopy(self.bindings)
        self.bindings['shots']['C01-P01']['sourceMother']['sha256'] = '0'*64
        self.check_rejected()
        self.bindings = original
        self.bindings['shots']['C01-P01']['sourceMother']['file'] = '../mother.png'
        self.check_rejected()

    def test_cross_channel(self):
        self.bindings['channel'] = 'other'
        self.check_rejected()

    def test_mesh_validation_and_json_finitude(self):
        node = self.bindings['shots']['C01-P01']['nodes'][0]
        node['mesh'] = {'kind': 'hair-back', 'columns': 7, 'rows': 9,
                        'pinnedRows': [0], 'amplitudePx': 0.8}
        self.save()
        self.assertEqual(rig.inspect(self.dp, self.bp)['shotCount'], 1)
        node['mesh']['pinnedRows'] = [1]
        self.check_rejected()
        node.pop('mesh')
        self.direction['scenes'][0]['shots'][0]['camera'] = {'type': 'perspective_3d', 'z': float('inf')}
        self.check_rejected()

    def test_symlink_source_rejected(self):
        link = self.root/'link.png'
        try:
            link.symlink_to(self.root/'mother.png')
        except (OSError, NotImplementedError):
            self.skipTest('Symlink privilege unavailable')
        self.bindings['shots']['C01-P01']['sourceMother']['file'] = 'link.png'
        self.check_rejected()

    def test_missing_target_blocks_prepare(self):
        self.bindings['shots']['C01-P01']['nodes'] = []
        self.save()
        self.assertEqual(rig.inspect(self.dp, self.bp)['shots'][0]['missingTargets'], ['actor.head'])
        with self.assertRaisesRegex(rig.DirectedRigError, 'MISSING_TARGETS'):
            rig.prepare(self.dp, self.bp, 'C01-P01', self.root/'out', self.root/'public')
        self.assertFalse((self.root/'out').exists())

    def test_invalid_dag_duplicate_and_bbox(self):
        original = copy.deepcopy(self.bindings)
        for change in ('cycle', 'missing_parent', 'duplicate', 'bbox'):
            with self.subTest(change=change):
                self.bindings = copy.deepcopy(original)
                nodes = self.bindings['shots']['C01-P01']['nodes']
                if change == 'cycle':
                    nodes[0]['parent'] = nodes[0]['id']
                elif change == 'missing_parent':
                    nodes[0]['parent'] = 'missing'
                elif change == 'duplicate':
                    nodes.append(copy.deepcopy(nodes[0]))
                else:
                    nodes[0]['bbox'] = [1, 1, 8, 8]
                self.check_rejected()

    def test_timeline_and_track_fail_closed(self):
        original = copy.deepcopy(self.direction)
        for change in ('nan', 'unordered', 'outside', 'transform', 'gap'):
            with self.subTest(change=change):
                self.direction = copy.deepcopy(original)
                shot = self.direction['scenes'][0]['shots'][0]
                track = shot['rigKeyframes'][0]
                if change == 'nan':
                    track['keyframes'][0]['value'] = float('nan')
                elif change == 'unordered':
                    track['keyframes'].reverse()
                elif change == 'outside':
                    track['keyframes'][-1]['frame'] = 10
                elif change == 'transform':
                    track['transform'] = 'unknown'
                else:
                    shot['startFrame'] = 1
                self.check_rejected()

    def test_json_duplicate_key_rejected(self):
        self.save()
        self.bp.write_text('{"schema": 1, "schema": 2}')
        with self.assertRaisesRegex(rig.DirectedRigError, 'DUPLICATE_JSON_KEY'):
            rig.inspect(self.dp, self.bp)

    def test_schema_units_scale_and_camera(self):
        original = copy.deepcopy(self.direction)
        for change in ('schema', 'unit', 'scale', 'camera'):
            with self.subTest(change=change):
                self.direction = copy.deepcopy(original)
                shot = self.direction['scenes'][0]['shots'][0]
                if change == 'schema':
                    self.direction['schema'] = 'other/v1'
                elif change == 'unit':
                    shot['rigKeyframes'][0]['unit'] = 'ratio'
                elif change == 'scale':
                    track = shot['rigKeyframes'][0]
                    track.update(transform='scaleX', unit='ratio')
                    track['keyframes'][0]['value'] = -1
                else:
                    shot['camera'] = {'type': 'perspective_3d', 'keyframes': [
                        {'frame': 0, 'z': 0, 'fovDeg': 30, 'lookAt': [0, 0, 0]},
                        {'frame': 9, 'z': 14, 'fovDeg': 30, 'lookAt': [0, 0, 0]}]}
                self.check_rejected()

    def test_existing_direction_covers_37_shots(self):
        path = Path(__file__).resolve().parents[1]/'canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/direcao-rig-remotion.json'
        data = rig._load(path)
        self.assertEqual(len(rig._direction(data)), 37)

    def test_source_pin_bounds_and_invertibility(self):
        node = self.bindings['shots']['C01-P01']['nodes'][0]
        node['mesh'] = {'kind': 'cloth', 'columns': 7, 'rows': 9,
                        'pinnedRows': [0], 'amplitudePx': .8,
                        'sourcePin': {'startY': 2, 'endY': 3}}
        self.save()
        rig.inspect(self.dp, self.bp)
        node['mesh']['sourcePin']['endY'] = 1
        self.check_rejected()
        node['mesh']['sourcePin']['endY'] = 3
        track = self.direction['scenes'][0]['shots'][0]['rigKeyframes'][0]
        track.update(transform='scaleX', unit='ratio')
        track['keyframes'][0]['value'] = 0
        self.check_rejected()


if __name__ == '__main__':
    unittest.main()
