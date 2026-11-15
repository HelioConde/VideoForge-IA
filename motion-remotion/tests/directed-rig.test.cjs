const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const Module=require('node:module');
const ts=require('typescript');
Module._extensions['.ts']=(m,filename)=>m._compile(ts.transpileModule(
  fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,
  target:ts.ScriptTarget.ES2020},fileName:filename}).outputText,filename);
const {validateDirectedProps,shotAtFrame,trackAtFrame,nodeTransformAtFrame,
  transformSourcePoint,inverseTransformSourcePoint,directedMeshAtFrame,cameraAtFrame,sourceWorldScale,upperBackDeltaAtFrame}=
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
  assert.equal(nodeTransformAtFrame(props.shots[0],'kael.cabeca',239).rotationZ,-0.08);
});


test('C01 P03 V4 breathes subtly while right arm/boot, king and spears stay source-locked',()=>{
  const path=require('node:path');
  const base=path.join(__dirname,'../../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01');
  const direction=JSON.parse(fs.readFileSync(path.join(base,'direcao-rig-remotion.json'),'utf8'));
  const bindings=JSON.parse(fs.readFileSync(path.join(base,'direcao-bindings-c01-draft.json'),'utf8'));
  const s=direction.scenes.flatMap(x=>x.shots).find(x=>x.id==='C01-P03');
  const b=bindings.shots[s.id];
  const shot={...s,canvas:b.canvas,background:b.background.file,
    nodes:b.nodes,tracks:s.rigKeyframes};
  assert.equal(shot.tracks.length,2,'No artificial gestures to force high pixel-change QA');
  assert.equal(shot.camera.move,'locked');
  assert.ok(shot.camera.keyframes.every(k=>k.z===14&&k.fovDeg===30));
  assert.equal(b.backgroundMode,'original-mother-static-context-with-kael-cutout/v1');
  const forbidden=new Set([
    'kael.punhos','kael.braco-direito','kael.antebraco','kael.braco-esquerdo',
    'kael.perna-direita','kael.bota-direita','guarda-esquerdo','guarda-direito',
    'aldric','lanca-contexto-0','lanca-contexto-1']);
  assert.ok(shot.tracks.every(t=>!forbidden.has(t.target)));
  const n=Object.fromEntries(shot.nodes.map(n=>[n.id,n]));
  assert.equal(n['kael.braco-direito'].parent,null);
  assert.equal(n['kael.braco-esquerdo'].parent,null);
  assert.equal(n['kael.antebraco'].parent,'kael.braco-direito');
  assert.equal(n['kael.punhos'].parent,'kael.antebraco');
  assert.equal(n['kael.bota-direita'].parent,'kael.perna-direita');
  assert.equal(n['kael.perna-direita'].parent,null);
  const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
  const wrist=[610,1048], boot=[570,1310], crown=[530,320];
  for(const frame of [150,167,180,191,210,220,239]){
    assert.ok(distance(transformSourcePoint(shot,'kael.punhos',wrist,frame),wrist)<1e-7,
      'Right hand must keep contact on knee, frame '+frame);
    assert.ok(distance(transformSourcePoint(shot,'kael.bota-direita',boot,frame),boot)<1e-7,
      'Right boot cannot split apart, frame '+frame);
    assert.ok(distance(transformSourcePoint(shot,'kael.braco-direito',[540,880],frame),[540,880])<1e-7);
    assert.deepEqual(transformSourcePoint(shot,'aldric',crown,frame),crown);
    assert.deepEqual(transformSourcePoint(shot,'lanca-contexto-0',[381,751],frame),[381,751]);
  }
  const head=shot.tracks.find(t=>t.target==='kael.cabeca');
  assert.ok(head.keyframes.every(k=>Math.abs(k.value)<=0.5));
  const breathe=shot.tracks.find(t=>t.target==='kael.ombros');
  assert.ok(breathe.keyframes.some(k=>k.value<-1));
  assert.ok(breathe.keyframes.every(k=>Math.abs(k.value)<=2));
  assert.equal(n['kael.cabelo'].mesh.amplitudePx,0.45);
  assert.equal(n['kael.jaqueta'].mesh.amplitudePx,0.55);
  assert.equal(n['kael.costura-gola-pixel-original'].parent,'kael.ombros');
  assert.deepEqual(n['kael.costura-gola-pixel-original'].onlyCoveredBy,
     ['kael.jaqueta']);
  assert.equal(n['kael.costura-gola-pixel-original'].sha256,b.sourceMother.sha256);
  const allShots=direction.scenes.flatMap(x=>x.shots);
  assert.equal(allShots.reduce((acc,x)=>acc+x.rigKeyframes.length,0),106);
  validateDirectedProps({...fixture(),...direction.format,id:shot.id,startFrame:shot.startFrame,
    durationFrames:90,shots:[shot]});
});

test('C01 P03 V5 localized upper-back mesh really breathes, leaving neck, wrists and waist pinned',()=>{
  const path=require('node:path');
  const root=path.join(__dirname,'../../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01');
  const direction=JSON.parse(fs.readFileSync(path.join(root,'direcao-rig-remotion.json'),'utf8'));
  const bindings=JSON.parse(fs.readFileSync(path.join(root,'direcao-bindings-c01-draft.json'),'utf8'));
  const s=direction.scenes.flatMap(x=>x.shots).find(x=>x.id==='C01-P03');
  const shot={...s,canvas:bindings.shots[s.id].canvas,
    background:bindings.shots[s.id].background.file,
    nodes:bindings.shots[s.id].nodes,tracks:s.rigKeyframes};
  const jacket=shot.nodes.find(n=>n.id==='kael.jaqueta');
  const back=jacket.mesh.backBreath;
  assert.deepEqual(back,{kind:'upper-back-source-mesh',sourceTopY:857,
    sourcePeakY:898,sourceBottomY:947,expansionPx:1.05,liftPx:0.6,
    driverTarget:'kael.ombros',driverTransform:'translateY',driverPeakAbsPx:1.25});
  const noBack={...jacket,mesh:{...jacket.mesh}};
  delete noBack.mesh.backBreath;
  const idx=(row,col)=>(row*(jacket.mesh.columns+1)+col)*3;
  const baseline=directedMeshAtFrame(jacket,shot,150,30);
  const baselineNoBack=directedMeshAtFrame(noBack,shot,150,30);
  assert.deepEqual(baseline.positions,baselineNoBack.positions);
  const atPeak=directedMeshAtFrame(jacket,shot,185,30);
  const withoutBack=directedMeshAtFrame(noBack,shot,185,30);
  const center=idx(3,3); // upper back near source y897
  const dx=atPeak.positions[center]-withoutBack.positions[center];
  const dy=atPeak.positions[center+1]-withoutBack.positions[center+1];
  assert.ok(Math.abs(dx)>0.1 && Math.abs(dx)<0.6,'back X expansion '+dx);
  assert.ok(dy>0.25 && dy<0.7,'upper back breathing lift '+dy);
  assert.deepEqual(atPeak.uvs,withoutBack.uvs);
  assert.deepEqual(atPeak.indices,withoutBack.indices);
  for(const row of [0,1,3,5,9]){
    for(const col of [0,jacket.mesh.columns]){
      const i=idx(row,col);
      for(let k=0;k<3;k++)
        assert.equal(atPeak.positions[i+k],withoutBack.positions[i+k],
          'side seams must stay source pinned at row '+row+' col '+col);
    }
  }
  for(const row of [0,1,5,6,7,8,9]){
    for(let col=0;col<=jacket.mesh.columns;col++){
      const i=idx(row,col);
      for(let k=0;k<3;k++)
        assert.equal(atPeak.positions[i+k],withoutBack.positions[i+k],
          'neck/waist pixels remain anchored row '+row+' col '+col);
    }
  }
  assert.deepEqual(directedMeshAtFrame(jacket,shot,185,30),atPeak,
    'V5 breathing must be deterministic for repeated Remotion frames');
  assert.deepEqual(upperBackDeltaAtFrame(jacket,shot,456,898,150),[0,0]);
  assert.equal(upperBackDeltaAtFrame(jacket,shot,456,898,185)[1],-0.6);
  for(const f of [150,167,185,199,220,239]){
    const wrist=[610,1048],boot=[570,1310];
    assert.deepEqual(transformSourcePoint(shot,'kael.punhos',wrist,f),wrist);
    assert.deepEqual(transformSourcePoint(shot,'kael.bota-direita',boot,f),boot);
  }
  const props={...fixture(),...direction.format,id:shot.id,startFrame:150,
    durationFrames:90,shots:[shot]};
  validateDirectedProps(props);
  const wrong=JSON.parse(JSON.stringify(props));
  wrong.shots[0].nodes.find(n=>n.id==='kael.jaqueta').mesh.backBreath.sourceBottomY=980;
  assert.throws(()=>validateDirectedProps(wrong),/UPPER_BACK_BREATH_SOURCE_GEOMETRY_INVALID/);
  const badDriver=JSON.parse(JSON.stringify(props));
  badDriver.shots[0].tracks.find(t=>t.target==='kael.ombros').keyframes[2].value=-5;
  assert.throws(()=>validateDirectedProps(badDriver),/UPPER_BACK_BREATH_DRIVER_TRACK_INVALID/);
});

test('waist seam stays in source position while shoulders breathe at every frame',()=>{
  const s=shot('waist',150,240);
  s.nodes=[node('shoulders',null,[472,1068]),{
    ...node('jacket','shoulders',[472,1068]),file:'jacket.png',bbox:[336,809,240,264],
    mesh:{kind:'cloth',columns:7,rows:9,pinnedRows:[0],amplitudePx:.8,
      sourcePin:{startY:950,endY:985}},
  }];
  s.tracks=[{target:'shoulders',transform:'translateY',unit:'pixels_source_canvas',
    easing:'easeInOutCubic',keyframes:[{frame:150,value:0},{frame:214,value:-2},{frame:239,value:-2}]}];
  const jacket=s.nodes[1];
  const source=directedMeshAtFrame(jacket,s,150,30);
  for(let frame=150;frame<240;frame++){
    const mesh=directedMeshAtFrame(jacket,s,frame,30);
    for(let row=6;row<=9;row++)for(let col=0;col<=7;col++){
      const i=(row*8+col)*3;
      const local=[mesh.positions[i]+512,768-mesh.positions[i+1]];
      const world=transformSourcePoint(s,jacket.id,local,frame);
      assert.ok(Math.abs(world[0]-(source.positions[i]+512))<1e-9);
      assert.ok(Math.abs(world[1]-(768-source.positions[i+1]))<1e-9,
        `waist opened at absolute frame ${frame}, row ${row}`);
    }
  }
  const moving=directedMeshAtFrame(jacket,s,214,30);
  const shoulder=transformSourcePoint(s,jacket.id,[moving.positions[0]+512,768-moving.positions[1]],214);
  assert.equal(shoulder[1],807); // Shoulders still rise by the directed 2px.
});

test('source pin undoes rotated/scaled ancestors and refuses noninvertible scale',()=>{
  const s=shot('pinned',0,10);
  s.nodes[1]={...s.nodes[1],file:'cloth.png',bbox:[100,100,100,100],
    mesh:{kind:'cloth',columns:7,rows:9,pinnedRows:[0],amplitudePx:1,
      sourcePin:{startY:110,endY:150}}};
  s.tracks=[track,{target:'arm',transform:'scaleX',unit:'ratio',easing:'linear',keyframes:[{frame:0,value:1.5}]},
    {target:'hand',transform:'translateY',unit:'pixels_source_canvas',easing:'linear',keyframes:[{frame:0,value:-4}]}];
  const source=[130,190];
  const roundtrip=inverseTransformSourcePoint(s,'hand',transformSourcePoint(s,'hand',source,8),8);
  assert.ok(Math.abs(source[0]-roundtrip[0])<1e-10&&Math.abs(source[1]-roundtrip[1])<1e-10);
  const mesh=directedMeshAtFrame(s.nodes[1],s,8,30);
  const i=mesh.positions.length-3;
  const point=transformSourcePoint(s,'hand',[mesh.positions[i]+512,768-mesh.positions[i+1]],8);
  assert.ok(Math.abs(point[0]-200)<1e-10&&Math.abs(point[1]-200)<1e-10);
  const props={...fixture(),durationFrames:10,shots:[s]};
  validateDirectedProps(props);
  s.tracks[1].keyframes[0].value=0;
  assert.throws(()=>validateDirectedProps(props),/NOT_INVERTIBLE/);
});
