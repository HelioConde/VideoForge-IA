'use strict';
/**
 * Test the pure TypeScript production gate without rendering WebGL or
 * generating art. Approved fixtures live ONLY in memory in this test.
 */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ts=require('typescript');

const source=fs.readFileSync(
  path.join(__dirname,'../src/cinematic-timeline.ts'),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{
  module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,
}}).outputText;
const gazeSource=fs.readFileSync(
  path.join(__dirname,'../src/eye-gaze-timeline.ts'),'utf8');
const gazeCompiled=ts.transpileModule(gazeSource,{compilerOptions:{
  module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,
}}).outputText;
const gazeModule={exports:{}};
new Function('module','exports',gazeCompiled)(gazeModule,gazeModule.exports);
const container={exports:{}};
new Function('module','exports','require',compiled)(
  container,container.exports,id=>{
    if(id==='./eye-gaze-timeline')return gazeModule.exports;
    throw new Error('UNEXPECTED_REQUIRE '+id);
  }
);
const {validateCinematicRender,cinematicShotAtFrame,shotDurationFrames}=
  container.exports;
const {evaluateGaze,validatePupilPerformance}=gazeModule.exports;
const sha='a'.repeat(64);
const other='b'.repeat(64);
const edlPath=path.join(__dirname,
  '../../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/timeline-cinematografica.json');
const realEdl=JSON.parse(fs.readFileSync(edlPath,'utf8'));

/** All fake media are internal validation fixtures; no PNG files are made. */
function rigFor(id){
  const p='assets/planos/'+id+'/';
  const eyeClose=id==='C12-P01';
  const result={
    schema:'videoforge/rig-three/v1',
    rigType:'independent-parts-and-deformable-mesh',
    canvas:{width:1024,height:1536},sceneMotherSha256:sha,
    technicalAssetsVerified:true,humanVisualReview:true,youtubeUploaded:false,
    neckPivot:[500,650],headMaxRotationDeg:eyeClose?0:2,
    blinkFrames:eyeClose?[]:[30],
    layers:[
      {id:'body-no-head',file:p+'body.png',bbox:[10,10,200,250],sha256:other,z:2},
      {id:'head-open',file:p+'head.png',bbox:[10,10,200,250],sha256:other,z:3},
      {id:'head-closed',file:p+'closed.png',bbox:[10,10,200,250],sha256:other,z:3},
      {id:'hair-front',file:p+'hair.png',bbox:[10,10,200,250],sha256:other,z:4,
       mesh:{columns:6,rows:6,pinnedRows:[0],amplitudePx:3}},
    ],
  };
  if(eyeClose){
    result.eyeRig={
      actorId:'kael',
      pupilLayerIds:['pupil-left','pupil-right'],
      eyelidLayerIds:['eyelid-left','eyelid-right'],
      eyeUnderlaysVerified:true,pupilMasksVerified:true,
      noDuplicatePaintedPupilsInHead:true,
      rotationOrTranslationClippingQA:true,
      gazePupilMaxPx:12,eyelidMaxPx:1,humanVisualApproved:true,
    };
    for(const eye of ['pupil-left','pupil-right','eyelid-left','eyelid-right']){
      result.layers.push({id:eye,file:p+eye+'.png',
        bbox:[10,10,20,20],sha256:other,z:5});
    }
  }
  return result;
}
function syntheticApprovedManifest(){
  const shots=realEdl.shots.map((s,i)=>{
    const base={
      id:s.id,scene:s.scene,startFrame:s.startFrame,
      endFrameExclusive:s.endFrameExclusive,type:s.type,
      characters:s.characters,hudPolicy:s.hudPolicy,
      renderAllowed:true,
    };
    if(i===0)return {...base,status:'black_no_art_required'};
    const p='assets/planos/'+s.id+'/';
    return {
      ...base,status:'ready_for_render',
      sourceMotherSha256:sha,backgroundSha256:other,
      backgroundFile:p+'background-reconstructed.png',
      actors:[{id:s.id==='C12-P01'?'kael':'fixture-character',
               rig:rigFor(s.id),
               motherSha256:sha,approvedForShot:true}],
      ...(s.id==='C12-P01'?{
        performance:{
          mode:'pupils_only_locked_head',actorId:'kael',
          pupilKeyframes:[
            {frame:0,value:0},{frame:4,value:0},
            {frame:86,value:12},{frame:119,value:12}],
          eyelidKeyframes:[
            {frame:0,value:0},{frame:7,value:0},
            {frame:86,value:1},{frame:119,value:1}],
          headRotationDeg:0,bodyMotionEnabled:false,
          cameraLocked:true,humanMotionApproved:true,
        },
      }:{}),
      humanVisualApproved:true,originShaVerified:true,
      hud:s.hudPolicy==='remotion_overlay'?
        {heading:'Approved fixture, not production text'}:null,
    };
  });
  return {
    schema:'videoforge/cinematic-remotion-episode/v1',
    channel:'alchemy-lab',videoId:'mmorpg-conquiste-a-princesa-ep01',
    fps:30,width:1080,height:1920,totalFrames:4890,
    renderApproved:true,shots,
  };
}
const deepCopy=x=>JSON.parse(JSON.stringify(x));

test('37 individually approved shots are continuous 0..4890 and frame-bound',()=>{
  const doc=syntheticApprovedManifest();
  assert.doesNotThrow(()=>validateCinematicRender(doc));
  assert.equal(shotDurationFrames(doc.shots[0]),60);
  assert.equal(cinematicShotAtFrame(doc.shots,0).id,'C01-P01');
  assert.equal(cinematicShotAtFrame(doc.shots,59).id,'C01-P01');
  assert.equal(cinematicShotAtFrame(doc.shots,60).id,'C01-P02');
  assert.equal(cinematicShotAtFrame(doc.shots,4889).id,'C14-P03');
  assert.throws(()=>cinematicShotAtFrame(doc.shots,4890),/OUT_OF_RANGE/);
});
test('current EDL is correctly denied: 36 visual shots are NOT approved',()=>{
  assert.equal(realEdl.renderOfficialAllowed,false);
  assert.equal(realEdl.unapprovedShots,36);
  assert.equal(realEdl.format.totalFrames,4890);
  assert.throws(()=>validateCinematicRender(realEdl),/APPROVED_EDL_REQUIRED/);
});
test('missing or malicious reference blocks entire video',()=>{
  const d=syntheticApprovedManifest();d.renderApproved=false;
  assert.throws(()=>validateCinematicRender(d),/APPROVED_EDL_REQUIRED/);
  const d2=syntheticApprovedManifest();d2.shots.splice(4,1);
  assert.throws(()=>validateCinematicRender(d2),/APPROVED_EDL_REQUIRED/);
});
test('a close cannot use the wide poster or have missing independent rig',()=>{
  const d=syntheticApprovedManifest();
  const close=d.shots.find(s=>s.type==='close_up');
  close.backgroundFile='assets/cena-01/scene-mother.png';
  assert.throws(()=>validateCinematicRender(d),/BACKGROUND_NOT_OWN_SHOT/);
  const e=syntheticApprovedManifest();
  const close2=e.shots.find(s=>s.type==='close_up');
  close2.actors=[];
  assert.throws(()=>validateCinematicRender(e),/SUBJECT_MUST_HAVE_REAL_RIG/);
});
test('bad SHA, unverified rig or omitted approved HUD blocks',()=>{
  const d=syntheticApprovedManifest();
  d.shots[1].sourceMotherSha256='UNVERIFIED';
  assert.throws(()=>validateCinematicRender(d),/QA_OR_ORIGIN/);
  const e=syntheticApprovedManifest();
  e.shots[1].actors[0].rig.humanVisualReview=false;
  assert.throws(()=>validateCinematicRender(e),/RIG_NOT_VERIFIED/);
  const f=syntheticApprovedManifest();
  const hud=f.shots.find(s=>s.hudPolicy==='remotion_overlay');
  hud.hud=null;
  assert.throws(()=>validateCinematicRender(f),/HUD_REMOTION_OVERLAY_REQUIRED/);
});
test('cut gaps and source origins from other angle are refused',()=>{
  const d=syntheticApprovedManifest();
  d.shots[1].startFrame++;
  assert.throws(()=>validateCinematicRender(d),/FRAME_OR_APPROVAL/);
  const e=syntheticApprovedManifest();
  e.shots[1].actors[0].rig.layers[0].file='assets/planos/C01-P04/other.png';
  assert.throws(()=>validateCinematicRender(e),/RIG_NOT_VERIFIED_FOR_SHOT/);
});


test('C12-P01 pupil gaze uses local frame easing, with zero movement at onset',()=>{
  const shot=syntheticApprovedManifest().shots.find(s=>s.id==='C12-P01');
  validatePupilPerformance(shot.performance,'C12-P01',120);
  const pupil=shot.performance.pupilKeyframes;
  const lid=shot.performance.eyelidKeyframes;
  assert.equal(evaluateGaze(pupil,0,120,12),0);
  assert.equal(evaluateGaze(pupil,4,120,12),0);
  assert.ok(evaluateGaze(pupil,45,120,12)>0);
  assert.ok(evaluateGaze(pupil,45,120,12)<12);
  assert.equal(evaluateGaze(pupil,86,120,12),12);
  assert.equal(evaluateGaze(pupil,119,120,12),12);
  assert.equal(evaluateGaze(lid,7,120,1),0);
  assert.equal(evaluateGaze(lid,86,120,1),1);
  assert.throws(()=>evaluateGaze(pupil,120,120,12),/FRAME_INVALID/);
});
test('C12-P01 cannot move head or omit its four pupil and eyelid assets',()=>{
  const e=syntheticApprovedManifest();
  const shot=e.shots.find(s=>s.id==='C12-P01');
  delete shot.performance;
  assert.throws(()=>validateCinematicRender(e),/PUPIL_PERFORMANCE_REQUIRED/);
  const f=syntheticApprovedManifest();
  const face=f.shots.find(s=>s.id==='C12-P01');
  face.actors[0].rig.headMaxRotationDeg=2;
  assert.throws(()=>validateCinematicRender(f),/INDEPENDENT_EYES_AND_UNDERLAYS/);
  const g=syntheticApprovedManifest();
  const face2=g.shots.find(s=>s.id==='C12-P01');
  face2.actors[0].rig.layers=face2.actors[0].rig.layers.filter(x=>x.id!=='pupil-left');
  assert.throws(()=>validateCinematicRender(g),/INDEPENDENT_EYES_AND_UNDERLAYS/);
  const h=syntheticApprovedManifest();
  const face3=h.shots.find(s=>s.id==='C12-P01');
  face3.actors[0].rig.eyeRig.eyeUnderlaysVerified=false;
  assert.throws(()=>validateCinematicRender(h),/INDEPENDENT_EYES_AND_UNDERLAYS/);
});
test('C12 gaze cannot be assigned to another shot or change keyframe targets',()=>{
  const e=syntheticApprovedManifest();
  const other=e.shots.find(s=>s.id==='C02-P01');
  other.performance=e.shots.find(s=>s.id==='C12-P01').performance;
  assert.throws(()=>validateCinematicRender(e),/UNEXPECTED_GAZE_PERFORMANCE/);
  const f=syntheticApprovedManifest();
  const gaze=f.shots.find(s=>s.id==='C12-P01').performance;
  gaze.pupilKeyframes[2].value=15;
  assert.throws(()=>validateCinematicRender(f),/KEYFRAMES_MISMATCH/);
});
