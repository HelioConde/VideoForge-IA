'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const src=(name)=>fs.readFileSync(path.join(__dirname,'../src',name),'utf8');

test('Remotion shot has a dedicated fail-closed entrypoint; the full episode remains blocked',()=>{
  const index=src('remake-sword-preview-index.ts');
  const root=src('remake-sword-preview-root.tsx');
  const scene=src('remake-sword-preview.tsx');
  assert.match(index,/registerRoot\(RemakeSwordPreviewRoot\)/);
  assert.match(root,/sourceRealArtworkVerified:false/);
  assert.match(root,/rig:null/);
  assert.match(scene,/sourceRealArtworkVerified!==true/);
  assert.match(scene,/ThreeCanvas/);
  assert.match(scene,/ARTE NÃO APROVADA/);
  assert.match(scene,/RemakeSwordRig/);
  assert.doesNotMatch(scene,/useFrame\(|requestAnimationFrame|Math\.random\(/);
  assert.doesNotMatch(scene,/<Img/);
});
test('actual sword rig never accepts paper approved-art inputs and uses four parts',()=>{
  const s=src('remake-sword-rig.tsx');
  assert.match(s,/technicalDraftOnly:true/);
  assert.match(s,/humanVisualReview:false/);
  assert.match(s,/neutralRoundtripQaPassed:true/);
  assert.match(s,/anchorSha256/);
  assert.match(s,/sourceRunId/);
  assert.match(s,/layers\.sheath/);
  assert.match(s,/layers\.blade/);
  assert.match(s,/layers\.hand/);
  assert.match(s,/layers\.underlay/);
  assert.match(s,/wristPivot/);
  assert.match(s,/vf-remake\/c01-p02/);
  assert.doesNotMatch(s,/rig\.humanVisualReview!==true/);
});
