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
const container={exports:{}};
new Function('module','exports',compiled)(container,container.exports);
const {validateCinematicRender,cinematicShotAtFrame,shotDurationFrames}=
  container.exports;
const sha='a'.repeat(64);
const other='b'.repeat(64);
const edlPath=path.join(__dirname,
  '../../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/timeline-cinematografica.json');
const realEdl=JSON.parse(fs.readFileSync(edlPath,'utf8'));

/** All fake media are internal validation fixtures; no PNG files are made. */
function rigFor(id){
  const p='assets/planos/'+id+'/';
  return {
    schema:'videoforge/rig-three/v1',
    rigType:'independent-parts-and-deformable-mesh',
    canvas:{width:1024,height:1536},sceneMotherSha256:sha,
    technicalAssetsVerified:true,humanVisualReview:true,youtubeUploaded:false,
    neckPivot:[500,650],headMaxRotationDeg:2,blinkFrames:[30],
    layers:[
      {id:'body-no-head',file:p+'body.png',bbox:[10,10,200,250],sha256:other,z:2},
      {id:'head-open',file:p+'head.png',bbox:[10,10,200,250],sha256:other,z:3},
      {id:'head-closed',file:p+'closed.png',bbox:[10,10,200,250],sha256:other,z:3},
      {id:'hair-front',file:p+'hair.png',bbox:[10,10,200,250],sha256:other,z:4,
       mesh:{columns:6,rows:6,pinnedRows:[0],amplitudePx:3}},
    ],
  };
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
      actors:[{id:'fixture-character',rig:rigFor(s.id),
               motherSha256:sha,approvedForShot:true}],
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
