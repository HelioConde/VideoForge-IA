const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Module=require('node:module');
const ts=require('typescript');
Module._extensions['.ts']=(m,filename)=>{
  m._compile(ts.transpileModule(fs.readFileSync(filename,'utf8'),{
    compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020},
    fileName:filename,
  }).outputText,filename);
};
const {meshVertexAtFrame,meshGridAtFrame,sceneEnvelope,
       sharedNeutralEnvelope,headRotationDegAtFrame,bodyBreathAtFrame,
       isClosedAtFrame}=require('../src/rig-three-math.ts');
const blinks=[74,173];
const duration=240,fps=30,box=[100,120,500,700];
const args={bbox:box,canvas:{width:1024,height:1536},
            spec:{columns:7,rows:9,pinnedRows:[0],amplitudePx:7},
            kind:'cape',fps,duration,blinkFrames:blinks};

test('real mesh 7x9, original UV, anchored seam; changing non-root vertices',()=>{
  const zero=meshGridAtFrame({...args,frame:0});
  const mid=meshGridAtFrame({...args,frame:111});
  assert.equal(zero.positions.length,(7+1)*(9+1)*3);
  assert.equal(zero.indices.length,7*9*6);
  assert.deepEqual(zero.uvs.slice(0,2),[100/1024,1-120/1536]);
  const topCount=(7+1)*3;
  assert.deepEqual(mid.positions.slice(0,topCount),zero.positions.slice(0,topCount));
  assert.notDeepEqual(mid.positions.slice(topCount),zero.positions.slice(topCount));
});

test('head and cape angles are clamped, blink independent of global wall clock',()=>{
  for(let f=0;f<duration;f++){
    const deg=headRotationDegAtFrame(f,fps,duration,blinks,2);
    assert.ok(Math.abs(deg)<=2.000001);
    const body=bodyBreathAtFrame(f,fps,duration,blinks);
    assert.ok(Math.abs(body.translateY)<.701);
    if(blinks.some(center=>Math.abs(center-f)<=3)){
      assert.equal(deg,0);
      assert.deepEqual(body,{scaleX:1,scaleY:1,translateY:0});
      const pin=meshVertexAtFrame({original:{x:110,y:700},uv:{x:1,y:1},
        kind:'cape',amplitudePx:7,frame:f,fps,duration,blinkFrames:blinks});
      assert.deepEqual(pin,{x:110,y:700});
    }
    assert.equal(deg,headRotationDegAtFrame(f,fps,duration,blinks,2));
  }
  assert.equal(isClosedAtFrame(74,blinks),true);
  assert.equal(isClosedAtFrame(76,blinks),false);
});

test('mesh stays inside per-layer bounds, hair and cape non-identical',()=>{
  for(let f of [0,30,65,74,76,90,140,173,175,239]){
    const p=meshVertexAtFrame({original:{x:400,y:790},uv:{x:.5,y:1},
      kind:'cape',amplitudePx:7,frame:f,fps,duration,blinkFrames:blinks});
    const hair=meshVertexAtFrame({original:{x:400,y:790},uv:{x:.5,y:1},
      kind:'hair-front',amplitudePx:7,frame:f,fps,duration,blinkFrames:blinks});
    assert.ok(Math.abs(p.x-400)<12);
    assert.ok(Math.abs(p.y-790)<12);
    if(f===140)assert.notDeepEqual(p,hair);
  }
});

test('no accidental motion on first and last frame, or impossible time',()=>{
  assert.equal(sceneEnvelope(0,duration),0);
  assert.equal(sceneEnvelope(239,duration),0);
  assert.equal(sharedNeutralEnvelope(74,duration,blinks),0);
  assert.throws(()=>headRotationDegAtFrame(20,0,duration,blinks,2));
  assert.throws(()=>meshVertexAtFrame({original:{x:1,y:1},uv:{x:1,y:1},
    kind:'cape',amplitudePx:99,frame:20,fps,duration,blinkFrames:blinks}));
});
