const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Module=require('node:module');
const ts=require('typescript');
const filename=path.join(__dirname,'../src/blink-motion-sync.ts');
const loaded=new Module(filename,module);
loaded.filename=filename;
loaded.paths=Module._nodeModulePaths(path.dirname(filename));
loaded._compile(ts.transpileModule(fs.readFileSync(filename,'utf8'),{
  compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020},
  fileName:filename,
}).outputText,filename);
const {blinkNeutralWeightAtFrame,synchronizedPoseAtFrame,subtleHeadPoseAtFrame}=loaded.exports;
const centers=[90,188];

test('entire open/closed exchange is geometrically identical, including one frame before and after',()=>{
  for(const center of centers){
    for(let frame=center-3;frame<=center+3;frame++){
      const body=synchronizedPoseAtFrame(
        {translateX:.45,translateY:1.7,rotateDeg:.19},frame,centers);
      const head=subtleHeadPoseAtFrame(frame,30,centers);
      const camera=blinkNeutralWeightAtFrame(frame,centers);
      assert.deepEqual(body,{translateX:0,translateY:0,rotateDeg:0});
      assert.deepEqual(head,{translateX:0,translateY:0,rotateDeg:0});
      assert.equal(camera,0);
    }
  }
});
test('motion eases into and out of neutral without snapping',()=>{
  for(let f=1;f<250;f++){
    const a=blinkNeutralWeightAtFrame(f-1,centers);
    const b=blinkNeutralWeightAtFrame(f,centers);
    assert.ok(Math.abs(a-b)<=.127,'weight jump at frame '+f+' = '+Math.abs(a-b));
    for(const value of Object.values(subtleHeadPoseAtFrame(f,30,centers))){
      assert.ok(Math.abs(value)<=.56,'head pose exceeded natural range');
    }
  }
});
test('first/last scene poses neutral even with no blinks',()=>{
  assert.equal(blinkNeutralWeightAtFrame(0,[]),1);
  assert.equal(blinkNeutralWeightAtFrame(99,[]),1);
  assert.deepEqual(synchronizedPoseAtFrame(
    {translateX:0,translateY:0,rotateDeg:0},99,centers),
    {translateX:0,translateY:0,rotateDeg:0});
});
test('invalid timings rejected, never generate random pose at swap',()=>{
  assert.throws(()=>blinkNeutralWeightAtFrame(90,[-1]));
  assert.throws(()=>blinkNeutralWeightAtFrame(90,centers,1,12));
  assert.throws(()=>subtleHeadPoseAtFrame(90,0,centers));
});
