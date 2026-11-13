/* Testes numericos do warp SVG sem browser nem assets de IA. */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Module=require('node:module');
const ts=require('typescript');

const filename=path.join(__dirname,'../src/mesh-rig.tsx');
const transpiled=ts.transpileModule(fs.readFileSync(filename,'utf8'),{
  compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,target:ts.ScriptTarget.ES2020},
  fileName:filename,
});
const loaded=new Module(filename,module);
loaded.filename=filename;
loaded.paths=Module._nodeModulePaths(path.dirname(filename));
loaded._compile(transpiled.outputText,filename);
const {blinkClosureAtFrame,headAngleAtFrame,capeMeshAtFrame,affineFromTriangles,
  capeVertexAtFrame,windEnergyAtTime,expandedClip}=loaded.exports;
const rig={
  schema:'videoforge/mesh-rig/v1',
  canvas:{width:1024,height:1536},
  layers:{body:'vf-scene/rig/body-no-head-no-cape.png',
    head:'vf-scene/rig/head-no-eyes.png',eyesOpen:'vf-scene/rig/eyes-open.png',
    eyesClosed:'vf-scene/rig/eyes-closed.png',cape:'vf-scene/rig/cape.png'},
  neckPivot:{x:500,y:580},headMaxDeg:1.6,blinkFrames:[40,132],
  capeMesh:{bounds:{x:280,y:490,width:340,height:600},
    columns:4,rows:6,amplitudePx:7},
};
const close=(a,b)=>assert.ok(Math.abs(a-b)<.0001,`${a} != ${b}`);

test('blink exato em quadros definidos, sem timers',()=>{
  assert.equal(blinkClosureAtFrame(37,rig.blinkFrames),0);
  assert.equal(blinkClosureAtFrame(38,rig.blinkFrames),.5);
  for(const frame of [39,40,41])assert.equal(blinkClosureAtFrame(frame,rig.blinkFrames),1);
  assert.equal(blinkClosureAtFrame(42,rig.blinkFrames),.5);
  assert.equal(blinkClosureAtFrame(43,rig.blinkFrames),0);
});

test('cabeca usa amplitude limitada e zera nos cortes',()=>{
  close(headAngleAtFrame(0,30,240,1.6),0);
  close(headAngleAtFrame(239,30,240,1.6),0);
  for(let f=0;f<240;f++){
    assert.ok(Math.abs(headAngleAtFrame(f,30,240,1.6))<=1.60001);
  }
});

test('malha realmente deforma, ancora superior fixa, deterministica',()=>{
  const a=capeMeshAtFrame(rig,60,30,240);
  const b=capeMeshAtFrame(rig,60,30,240);
  assert.deepEqual(a,b);
  assert.equal(a.length,48);
  assert.deepEqual(capeMeshAtFrame(rig,0,30,240)[0].source,
                   capeMeshAtFrame(rig,0,30,240)[0].destination);
  assert.ok(a.some(t=>t.destination.some((p,i)=>Math.abs(p.x-t.source[i].x)>.1)));
  for(const tri of a){
    for(let i=0;i<3;i++){
      const src=tri.source[i],dst=tri.destination[i];
      if(src.y===rig.capeMesh.bounds.y){
        close(src.x,dst.x);close(src.y,dst.y);
      }
      const [ma,mb,mc,md,me,mf]=tri.matrix;
      close(ma*src.x+mc*src.y+me,dst.x);
      close(mb*src.x+md*src.y+mf,dst.y);
    }
  }
});

test('triangulo degenerado e rejeitado',()=>{
  assert.throws(()=>affineFromTriangles(
    [{x:0,y:0},{x:1,y:1},{x:2,y:2}],
    [{x:0,y:0},{x:1,y:1},{x:2,y:2}]
  ),/RIG_DEGENERATE_TRIANGLE/);
});

test('SVG mesh triangle clips overlap adjacent edges to avoid dark seams',()=>{
  const points=[{x:2,y:2},{x:20,y:2},{x:11,y:21}];
  const out=expandedClip(points,2);
  const cx=11,cy=25/3;
  for(let i=0;i<3;i++){
    const old=Math.hypot(points[i].x-cx,points[i].y-cy);
    const ext=Math.hypot(out[i].x-cx,out[i].y-cy);
    assert.ok(ext>old+1.9,'clip must expand by ~2px');
  }
});

const wind={direction:-1,baseStrength:.85,gustStrength:1.15,
  flutterStrength:.65,tipLagSeconds:.34,liftStrength:.62};
const windyRig={...rig,capeMesh:{...rig.capeMesh,amplitudePx:10.5,wind}};

test('cape wind: shoulder fully pinned and start/end neutral in BOTH layers',()=>{
  const b=windyRig.capeMesh.bounds;
  const at=(v,frame,layer='cape')=>capeVertexAtFrame({
    x:b.x+b.width*.5,y:b.y+b.height*v,frame,fps:30,duration:240,
    bounds:b,amplitudePx:10.5,wind,layer,
  });
  for(const layer of ['cape','capeFront']){
    for(const frame of [0,20,75,125,185,225,239]){
      assert.deepEqual(at(0,frame,layer),
        {x:b.x+b.width*.5,y:b.y},'Shoulder cannot detach from garment');
    }
    for(const v of [.1,.4,.7,1]){
      for(const frame of [0,239]){
        const x=b.x+b.width*.5,y=b.y+b.height*v;
        assert.deepEqual(at(v,frame,layer),{x,y},'Neutral frame avoids jump cuts');
      }
    }
  }
});

test('cape wind: gust grows and tip motion exceeds mid motion with delayed phase',()=>{
  const b=windyRig.capeMesh.bounds;
  const displacement=(v,frame,layer='cape')=>{
    const x=b.x+b.width*.6,y=b.y+b.height*v;
    const p=capeVertexAtFrame({
      x,y,frame,fps:30,duration:240,bounds:b,amplitudePx:10.5,wind,layer
    });
    return Math.hypot(p.x-x,p.y-y);
  };
  assert.ok(windEnergyAtTime(1.85,8,wind)>
            windEnergyAtTime(.20,8,wind)+.30,'wind must have real gusts');
  const tip=Math.max(...Array.from({length:239},(_,f)=>displacement(1,f)));
  const mid=Math.max(...Array.from({length:239},(_,f)=>displacement(.45,f)));
  const front=Math.max(...Array.from({length:239},(_,f)=>displacement(1,f,'capeFront')));
  assert.ok(tip>mid*1.7,`tip ${tip} must move more than mid ${mid}`);
  assert.ok(tip>8 && tip<45,`tip ${tip} should be visible, not flying away`);
  assert.ok(front<tip*.87,`front piece ${front} should stay closer to chest`);
  // Different depth => different phases, not a uniform sheet translation.
  const tipTime=Array.from({length:240},(_,f)=>displacement(1,f));
  const samples=[tipTime[35],tipTime[80],tipTime[125],tipTime[175],tipTime[215]];
  assert.ok(new Set(samples.map(x=>x.toFixed(2))).size>=4);
});

test('cape wind: deterministic mesh, no inverted or degenerate triangles',()=>{
  for(const layer of ['cape','capeFront']){
    for(const frame of [0,30,55,89,116,160,185,225,239]){
      const a=capeMeshAtFrame(windyRig,frame,30,240,layer);
      const b=capeMeshAtFrame(windyRig,frame,30,240,layer);
      assert.deepEqual(a,b);
      assert.equal(a.length,48);
      for(const tri of a){
        const [a,b,c]=tri.destination;
        const orient=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
        assert.ok(orient>25,`Fold/inverted triangle at frame ${frame}`);
      }
    }
  }
});

test('legacy cape remains opt-in and unchanged with absent wind profile',()=>{
  const legacy=capeVertexAtFrame({
    x:410,y:790,frame:90,fps:30,duration:240,
    bounds:rig.capeMesh.bounds,amplitudePx:rig.capeMesh.amplitudePx,
  });
  const neutral=capeVertexAtFrame({
    x:410,y:790,frame:90,fps:30,duration:240,
    bounds:rig.capeMesh.bounds,amplitudePx:rig.capeMesh.amplitudePx,
    layer:'capeFront',
  });
  assert.deepEqual(legacy,neutral);
  assert.notDeepEqual(capeMeshAtFrame(windyRig,90,30,240),
                      capeMeshAtFrame(rig,90,30,240));
});
