const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const Module=require('node:module');
const ts=require('typescript');
Module._extensions['.ts']=(m,filename)=>m._compile(ts.transpileModule(
  fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,
  target:ts.ScriptTarget.ES2020},fileName:filename}).outputText,filename);
const {validateDirectedProps,shotAtFrame,trackAtFrame,nodeTransformAtFrame,
  transformSourcePoint,directedMeshAtFrame,cameraAtFrame,sourceWorldScale}=
  require('../src/directed-rig-math.ts');
const node=(id,parent=null,pivot=[100,100])=>({id,parent,pivot,role:'joint',z:1});
const shot=(id,start,end)=>({id,startFrame:start,endFrameExclusive:end,
  canvas:{width:1024,height:1536},background:null,
  nodes:[node('arm'),node('hand','arm',[150,100])],tracks:[],
  camera:{type:'perspective_3d',move:'locked',keyframes:[
    {frame:start,z:14,lookAt:[0,0,0],fovDeg:30}]}});
const fixture=()=>({schema:'videoforge/directed-rig-preview/v1',mode:'technical_draft',
  channel:'alchemy-lab',videoId:'fixture',id:'fixture',width:1080,height:1920,fps:30,
  startFrame:0,durationFrames:20,shots:[shot('one',0,10),shot('two',10,20)],
  warnings:[],humanVisualReview:false,publishable:false});
const track={target:'arm',transform:'rotationZ',unit:'degrees',easing:'easeInOutCubic',
  keyframes:[{frame:0,value:0},{frame:8,value:90}]};

test('clamped absolute-frame interpolation and cubic easing',()=>{
  assert.equal(trackAtFrame(track,-10),0);
  assert.equal(trackAtFrame(track,4),45);
  assert.equal(trackAtFrame(track,2),5.625);
  assert.equal(trackAtFrame(track,100),90);
  assert.equal(trackAtFrame({...track,easing:'linear'},2),22.5);
});
test('shot limits use start inclusive/end exclusive and reject missing frames',()=>{
  const props=fixture();validateDirectedProps(props);
  assert.equal(shotAtFrame(props.shots,9).id,'one');
  assert.equal(shotAtFrame(props.shots,10).id,'two');
  assert.throws(()=>shotAtFrame(props.shots,20));
  props.shots[1].startFrame=11;
  assert.throws(()=>validateDirectedProps(props));
});
test('child inherits rotation around measured parent pivot without double translation',()=>{
  const s=shot('one',0,10);s.tracks=[track];
  const pivot=transformSourcePoint(s,'arm',[100,100],8);
  assert.deepEqual(pivot,[100,100]);
  const child=transformSourcePoint(s,'hand',[150,100],8);
  assert.ok(Math.abs(child[0]-100)<1e-10);
  assert.ok(Math.abs(child[1]-150)<1e-10);
  s.tracks.push({target:'hand',transform:'rotationZ',unit:'degrees',easing:'linear',
    keyframes:[{frame:0,value:35}]});
  assert.deepEqual(transformSourcePoint(s,'hand',[150,100],8),child);
});
test('random access frames yield identical transforms and fixed-root meshes',()=>{
  const s=shot('one',0,240);s.tracks=[track];
  const hair={...node('hair'),file:'hair.png',bbox:[90,90,30,70],
    mesh:{kind:'hair-front',columns:7,rows:9,pinnedRows:[0],amplitudePx:4}};
  const first=directedMeshAtFrame(hair,s,111,30);
  for(const frame of [239,0,74,30,111]){
    directedMeshAtFrame(hair,s,frame,30);nodeTransformAtFrame(s,'arm',frame);
  }
  assert.deepEqual(first,directedMeshAtFrame(hair,s,111,30));
  const zero=directedMeshAtFrame(hair,s,0,30);
  assert.deepEqual(first.positions.slice(0,24),zero.positions.slice(0,24));
  assert.notDeepEqual(first.positions.slice(24),zero.positions.slice(24));
});
test('perspective baseline covers source uniformly and camera keys clamp',()=>{
  const s=shot('one',0,20);
  const scale=sourceWorldScale(s.canvas,1080,1920);
  assert.ok(Math.abs(1536*scale-2*14*Math.tan(Math.PI/12))<1e-12);
  assert.equal(cameraAtFrame(s,19).z,14);
  s.camera.keyframes.push({frame:19,z:7,lookAt:[1,2,0],fovDeg:40});
  assert.equal(cameraAtFrame(s,9.5).z,10.5);
});
test('invalid approval/schema, missing targets/parents and cycles fail closed',()=>{
  for(const patch of [{publishable:true},{humanVisualReview:true},{schema:'other'}])
    assert.throws(()=>validateDirectedProps({...fixture(),...patch}));
  const missing=fixture();missing.shots[0].tracks=[{...track,target:'missing'}];
  assert.throws(()=>validateDirectedProps(missing));
  const parent=fixture();parent.shots[0].nodes[0].parent='missing';
  assert.throws(()=>validateDirectedProps(parent));
  const cycle=fixture();cycle.shots[0].nodes[0].parent='hand';
  assert.throws(()=>validateDirectedProps(cycle));
});
test('existing C01-P03 bindings and absolute direction match the renderer contract',()=>{
  const path=require('node:path');
  const base=path.join(__dirname,'../../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01');
  const direction=JSON.parse(fs.readFileSync(path.join(base,'direcao-rig-remotion.json'),'utf8'));
  const bindings=JSON.parse(fs.readFileSync(path.join(base,'direcao-bindings-c01-draft.json'),'utf8'));
  const actual=direction.scenes.flatMap(s=>s.shots).find(s=>s.id==='C01-P03');
  const bound=bindings.shots[actual.id];
  const props={...fixture(),...direction.format,id:actual.id,startFrame:actual.startFrame,
    durationFrames:actual.endFrameExclusive-actual.startFrame,
    shots:[{...actual,canvas:bound.canvas,background:bound.background.file,
      nodes:bound.nodes,tracks:actual.rigKeyframes}]};
  validateDirectedProps(props);
  assert.equal(shotAtFrame(props.shots,150).id,'C01-P03');
  assert.equal(nodeTransformAtFrame(props.shots[0],'kael.cabeca',239).rotationZ,-.6);
});
