const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Module=require('node:module');
const ts=require('typescript');
Module._extensions['.ts']=(m,filename)=>{
  m._compile(ts.transpileModule(fs.readFileSync(filename,'utf8'),{
    compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020},
  }).outputText,filename);
};
const {validateC12TechnicalProps}=
  require('../src/c12-mesh-technical-contract.ts');
const dir='vf-cinema/alchemy-lab/mmorpg-conquiste-a-princesa-ep01/assets/planos/';
const source={
  'C12-P02':{
    mother:'01eb7c127b0699d2e502d29dacec0bb39c0e1e23bf8205fdcf6fb70976e70535',
    background:'846358dfc4d2e85961b33c78e0fdf73cbc500ff46ea53af6d2444bdbac7c07cd',
  },
  'C12-P03':{
    mother:'bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a',
    background:'a89125a1b5b6b46891d7f1306c015183e2e5c781605b3886143bf91cf16b2c15',
  },
};
const sha={
  'kael-cape-loose-fold':'d2db9bb4b9014dac97e8c73b1769b5062e4dd4992c592be43250c13e37e26841',
  'elara-left-face-hair-lock':'611638aa33b8fc72c3654bb141ce92ad59fea2adaced39fcf8b5e742e45d450f',
  'elara-back-hair-fall':'a7eb167c147b399840ccae377d498fce417efb88a5c05fe9e74f17f5fe0bb634',
  'elara-earring-pendant':'d5c73354209eafc11d4042fdef16c6138f5f8b16fe63e62b47c06b73d83e277d',
  'elara-sleeve-lower-fabric':'722b2a4ab6f7fc0f0b2413fd7ad2ce7d39c7165ca274159d386ad5791d9cdb78',
};

function layer(shot,id,kind,columns,rows,pivotPx){
  return {
    id,file:dir+shot+'/'+id+'.png',bbox:[50,90,30,70],sha256:sha[id],z:10,
    mesh:{kind,columns,rows,pinnedRows:[0],amplitudePx:5,
          ...(pivotPx?{pivotPx}:{}),},
  };
}
function valid(){
  return {
    schema:'videoforge/c12-technical-three-mesh-preview/v1',
    fps:30,width:720,height:1280,totalFrames:240,
    sourceCanvas:{width:941,height:1672},
    expectedMeshTriangles:512,
    status:'TECHNICAL_NO_HUMAN_APPROVAL',
    sourceOriginalsArchived:true,
    officialVideoApproved:false,imageGenerationCalls:0,
    shots:[
      {id:'C12-P02',sourceOriginalSha256:source['C12-P02'].mother,
        backgroundSha256:source['C12-P02'].background,
        backgroundFile:dir+'C12-P02/background-inpaint-technical.png',
        layers:[layer('C12-P02','kael-cape-loose-fold','cape',6,8)]},
      {id:'C12-P03',sourceOriginalSha256:source['C12-P03'].mother,
        backgroundSha256:source['C12-P03'].background,
        backgroundFile:dir+'C12-P03/background-inpaint-technical.png',
        layers:[
          layer('C12-P03','elara-left-face-hair-lock','hair-front-left',5,10),
          layer('C12-P03','elara-back-hair-fall','hair-back',6,12),
          layer('C12-P03','elara-earring-pendant','earring',4,9,[690,547]),
          layer('C12-P03','elara-sleeve-lower-fabric','cloth',5,10),
        ],
      },
    ],
  };
}
test('five original-source RGBA sprites, 512 triangles, 2 independent shots',()=>{
  assert.doesNotThrow(()=>validateC12TechnicalProps(valid()));
  assert.equal(valid().shots.reduce((total,shot)=>
    total+shot.layers.reduce((a,l)=>a+2*l.mesh.columns*l.mesh.rows,0),0),512);
});
test('source originals not imported cannot render through Remotion',()=>{
  const d=valid();
  d.sourceOriginalsArchived=false;
  assert.throws(()=>validateC12TechnicalProps(d),/SOURCE_ASSETS_AND_DRAFT_STATUS_REQUIRED/);
});
test('cannot mark draft as official even if all five meshes exist',()=>{
  const d=valid();
  d.officialVideoApproved=true;
  assert.throws(()=>validateC12TechnicalProps(d),/SOURCE_ASSETS_AND_DRAFT_STATUS_REQUIRED/);
});
test('missing RGBA part and source canvas variation are rejected',()=>{
  const d=valid();
  d.shots[1].layers.pop();
  assert.throws(()=>validateC12TechnicalProps(d),/REQUIRED_INDEPENDENT_MESH_PART_MISSING/);
  const d2=valid();
  d2.sourceCanvas.width=1024;
  assert.throws(()=>validateC12TechnicalProps(d2),/SOURCE_ASSETS_AND_DRAFT_STATUS_REQUIRED/);
});
test('reject mismatched mother origin and altered sprite files',()=>{
  const d=valid();
  d.shots[0].backgroundFile='../other-scene.png';
  assert.throws(()=>validateC12TechnicalProps(d),/BACKGROUND_NOT_FROM_ORIGINAL_SHOT/);
  const e=valid();
  e.shots[0].layers[0].sha256='0'.repeat(63);
  assert.throws(()=>validateC12TechnicalProps(e),/PART_INVALID_SHA_BBOX_OR_MESH/);
});
test('earring must pivot at its actual point on Elara face',()=>{
  const d=valid();
  d.shots[1].layers[2].mesh.pivotPx=[0,0];
  assert.throws(()=>validateC12TechnicalProps(d),/EARRING_BONE_PIVOT_REQUIRED/);
});
