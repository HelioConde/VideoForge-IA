'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ts=require('typescript');

const file=path.join(__dirname,'../src/remake-sword-motion.ts');
const compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{
  module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,
}}).outputText;
const moduleObject={exports:{}};
new Function('module','exports',compiled)(moduleObject,moduleObject.exports);
const {swordPoseAtFrame}=moduleObject.exports;
const tuning={
  beginFrame:7,finishFrame:72,
  travelPx:170,axisDeg:36,
  handFollow:.9,handRotationDeg:4,
};
test('C01-P02 independent sword blade and wrist rig is deterministic',()=>{
  const first=swordPoseAtFrame(0,90,tuning);
  const firstAgain=swordPoseAtFrame(0,90,tuning);
  assert.deepEqual(first,firstAgain);
  assert.equal(first.progress,0);
  assert.equal(first.bladeDx,0);
  const half=swordPoseAtFrame(35,90,tuning);
  assert.ok(half.progress>0&&half.progress<1);
  assert.ok(half.bladeDx>0&&half.bladeDy>0);
  assert.ok(half.handDx>0&&half.handDx<half.bladeDx);
  assert.ok(half.handAngleDeg>0&&half.handAngleDeg<=4);
  const after=swordPoseAtFrame(89,90,tuning);
  assert.equal(after.progress,1);
  assert.ok(Math.abs(Math.hypot(after.bladeDx,after.bladeDy)-170)<1e-9);
});
test('motion clamps only allowed frames and rejects unsafe movement',()=>{
  assert.throws(()=>swordPoseAtFrame(-1,90,tuning),/INVALID/);
  assert.throws(()=>swordPoseAtFrame(90,90,tuning),/INVALID/);
  assert.throws(()=>swordPoseAtFrame(40,90,{...tuning,travelPx:900}),/INVALID/);
  assert.throws(()=>swordPoseAtFrame(40,90,{...tuning,handRotationDeg:25}),/INVALID/);
  assert.throws(()=>swordPoseAtFrame(40,90,{...tuning,handFollow:2}),/INVALID/);
  assert.throws(()=>swordPoseAtFrame(40,90,{...tuning,finishFrame:7}),/INVALID/);
});
test('real scene uses three independently articulated PNG layers and reuses the existing engine',()=>{
  const rig=fs.readFileSync(path.join(__dirname,'../src/remake-sword-rig.tsx'),'utf8');
  const reusable=fs.readFileSync(path.join(__dirname,'../src/rig-three-scene.tsx'),'utf8');
  assert.match(rig,/RigidSprite/);
  assert.match(rig,/useCurrentFrame/);
  assert.match(rig,/neutralRoundtripQaPassed:true/);
  assert.match(rig,/humanVisualReview:false/);
  assert.match(rig,/technicalDraftOnly:true/);
  assert.match(rig,/layers\.sheath/);
  assert.match(rig,/layers\.blade/);
  assert.match(rig,/layers\.hand/);
  assert.match(rig,/wristPivot/);
  assert.match(reusable,/export const RigidSprite/);
  assert.doesNotMatch(rig,/useFrame\(|Date\.now\(|Math\.random\(/);
});
