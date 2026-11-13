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
const {blinkClosureAtFrame,headAngleAtFrame,capeMeshAtFrame,affineFromTriangles}=loaded.exports;
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
