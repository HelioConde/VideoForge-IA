/* Guardar limite de micro movimento e determinismo no motor do VideoForge. */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Module=require('node:module');
const ts=require('typescript');
const filename=path.join(__dirname,'../src/character-idle.ts');
const transpiled=ts.transpileModule(fs.readFileSync(filename,'utf8'),{
  compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020},
  fileName:filename,
});
const loaded=new Module(filename,module);
loaded.filename=filename;
loaded.paths=Module._nodeModulePaths(path.dirname(filename));
loaded._compile(transpiled.outputText,filename);
const {characterPoseAtFrame,presetNames}=loaded.exports;

test('movimento vertical max 2.8px, sem flutuacao artificial',()=>{
  for(const preset of presetNames){
    for(const id of ['anya-grande','loid','yor','objeto-sprite','protagonista']){
      for(let frame=0;frame<300;frame++){
        const args={role:'front_character',id,coverage:.3815,contactRisk:.12,
          heroRisk:0,heightFraction:.72,frame,sceneStart:0,sceneEnd:300,
          fps:30,preset,enabled:true};
        const p=characterPoseAtFrame(args);
        assert.ok(Math.abs(p.translateY)<=2.80001,preset+'/'+id+' bob='+p.translateY);
        assert.ok(Math.abs(p.translateX)<=1.00001);
        assert.ok(Math.abs(p.rotateDeg)<=.25001);
        assert.equal(p.scaleX,1);assert.equal(p.scaleY,1);
        assert.deepEqual(p,characterPoseAtFrame(args));
      }
    }
  }
});
test('cortes neutros e personagem ligado a objeto seguem seguranca',()=>{
  const args={role:'front_character',id:'anya',coverage:.3815,contactRisk:.12,
    heroRisk:0,heightFraction:.72,frame:0,sceneStart:0,sceneEnd:240,
    fps:30,preset:'equilibrado',enabled:true};
  assert.equal(characterPoseAtFrame(args).translateY,0);
  assert.equal(characterPoseAtFrame({...args,frame:240}).translateY,0);
  assert.equal(characterPoseAtFrame({...args,frame:120,heroRisk:.20}).enabled,false);
});
