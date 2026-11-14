/**
 * C12 technical mesh compositor: TRUE THREE.JS triangulated per-part sprites.
 *
 * Reads real SOURCE-derived RGBA sprites and their real underlay background
 * when those files are imported. Never animates the RGB mother as a plate.
 * This is an isolated technical draft, NOT the 37-shot official component.
 */
import React from 'react';
import {AbsoluteFill,Img,Sequence,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {DeformableSprite} from './rig-three-scene';
import type {LayerSpec,MeshType} from './rig-three-math';

export type C12TechnicalShot={
  id:'C12-P02'|'C12-P03';
  sourceOriginalSha256:string;
  backgroundFile:string;
  backgroundSha256:string;
  layers:Array<LayerSpec & {mesh:NonNullable<LayerSpec['mesh']> & {kind:MeshType}}>;
};
export type C12TechnicalProps={
  schema:'videoforge/c12-technical-three-mesh-preview/v1';
  fps:30;
  sourceCanvas:{width:941;height:1672};
  width:720;height:1280;
  totalFrames:240;
  expectedMeshTriangles:512;
  status:'TECHNICAL_NO_HUMAN_APPROVAL';
  sourceOriginalsArchived:true;
  officialVideoApproved:false;
  imageGenerationCalls:0;
  shots:[C12TechnicalShot,C12TechnicalShot];
};

const SHA=/^[0-9a-f]{64}$/;
const SAFE=/^vf-cinema\/alchemy-lab\/mmorpg-conquiste-a-princesa-ep01\/assets\/planos\/C12-P0[23]\//;

const KNOWN=new Map<string,string[]>([
  ['C12-P02',['kael-cape-loose-fold']],
  ['C12-P03',[
    'elara-left-face-hair-lock','elara-back-hair-fall',
    'elara-earring-pendant','elara-sleeve-lower-fabric',
  ]],
]);

export const validateC12TechnicalProps=(props:C12TechnicalProps):void=>{
  if(!props ||
    props.schema!=='videoforge/c12-technical-three-mesh-preview/v1' ||
    props.fps!==30 ||
    props.sourceCanvas?.width!==941 ||props.sourceCanvas.height!==1672 ||
    props.width!==720||props.height!==1280||props.totalFrames!==240||
    props.expectedMeshTriangles!==512||
    props.status!=='TECHNICAL_NO_HUMAN_APPROVAL'||
    props.sourceOriginalsArchived!==true||
    props.officialVideoApproved!==false||
    props.imageGenerationCalls!==0||
    !Array.isArray(props.shots)||props.shots.length!==2||
    props.shots[0]?.id!=='C12-P02'||props.shots[1]?.id!=='C12-P03')
    throw new Error('C12_TECHNICAL_SOURCE_ASSETS_AND_DRAFT_STATUS_REQUIRED');

  let totalTriangles=0;
  for(const shot of props.shots){
    if(!SHA.test(shot.sourceOriginalSha256)||
      !SHA.test(shot.backgroundSha256)||
      typeof shot.backgroundFile!=='string'||
      !shot.backgroundFile.startsWith('vf-cinema/alchemy-lab/mmorpg-conquiste-a-princesa-ep01/assets/planos/'+shot.id+'/')||
      !shot.backgroundFile.endsWith('.png')||
      !SAFE.test(shot.backgroundFile))
      throw new Error('C12_TECHNICAL_BACKGROUND_NOT_FROM_ORIGINAL_SHOT');
    const expected=KNOWN.get(shot.id)!;
    if(shot.layers.length!==expected.length||
      new Set(shot.layers.map(layer=>layer.id)).size!==expected.length ||
      expected.some(id=>!shot.layers.find(l=>l.id===id)))
      throw new Error('C12_TECHNICAL_REQUIRED_INDEPENDENT_MESH_PART_MISSING');
    for(const l of shot.layers){
      if(!l.mesh || !l.mesh.kind || !SHA.test(l.sha256)||
        !l.file.startsWith('vf-cinema/alchemy-lab/mmorpg-conquiste-a-princesa-ep01/assets/planos/'+shot.id+'/') ||
        !l.file.endsWith('.png') ||!SAFE.test(l.file)||
        !Array.isArray(l.bbox) || l.bbox.length!==4 ||
        !l.bbox.every(Number.isSafeInteger)||
        l.bbox[0]<0||l.bbox[1]<0||l.bbox[2]<1||l.bbox[3]<1||
        l.bbox[0]+l.bbox[2]>941||l.bbox[1]+l.bbox[3]>1672 ||
        !Number.isFinite(l.z)||
        l.mesh.columns<4||l.mesh.rows<8||
        l.mesh.pinnedRows.length!==1||l.mesh.pinnedRows[0]!==0||
        l.mesh.amplitudePx<=0||l.mesh.amplitudePx>12)
        throw new Error('C12_TECHNICAL_PART_INVALID_SHA_BBOX_OR_MESH');
      if(l.id==='elara-earring-pendant'){
        if(l.mesh.kind!=='earring'||!l.mesh.pivotPx||
           l.mesh.pivotPx[0]!==690||l.mesh.pivotPx[1]!==547)
          throw new Error('C12_TECHNICAL_EARRING_BONE_PIVOT_REQUIRED');
      }
      totalTriangles+=2*l.mesh.columns*l.mesh.rows;
    }
  }
  if(totalTriangles!==512)
    throw new Error('C12_TECHNICAL_MESH_TRIANGLES_MISMATCH');
};

const DraftShot:React.FC<{shot:C12TechnicalShot}>=({shot})=>{
  const frame=useCurrentFrame();
  const {width,height,fps}=useVideoConfig();
  const canvas={width:941,height:1672};
  const scale=Math.max(width/canvas.width,height/canvas.height);
  return <AbsoluteFill style={{overflow:'hidden',backgroundColor:'#0b0712'}}>
    <Img src={staticFile(shot.backgroundFile)}
      style={{position:'absolute',inset:0,width:'100%',height:'100%',
        objectFit:'cover'}}/>
    <ThreeCanvas width={width} height={height} orthographic
      camera={{position:[0,0,100],zoom:1}}
      gl={{alpha:true,antialias:true,preserveDrawingBuffer:true}}
      style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
      <group scale={[scale,scale,1]}>
        {shot.layers.map(layer=><DeformableSprite
          key={layer.id} layer={layer} canvas={canvas}
          kind={layer.mesh.kind}
          motion={{frame,fps,duration:120,blinkFrames:[]}}/>)}
      </group>
    </ThreeCanvas>
    <div style={{position:'absolute',left:18,right:18,top:25,
      padding:12,background:'rgba(20,10,30,.84)',
      fontFamily:'sans-serif',color:'#fff',fontSize:22,textAlign:'center',
      fontWeight:800}}>
      {'TESTE DE MALHA THREE.JS — SEM QA HUMANO · '+shot.id}
    </div>
  </AbsoluteFill>;
};

export const C12TechnicalMeshPreview:React.FC<C12TechnicalProps>=props=>{
  validateC12TechnicalProps(props);
  return <AbsoluteFill style={{backgroundColor:'#050308'}}>
    {props.shots.map((shot,index)=>
      <Sequence key={shot.id} from={index*120} durationInFrames={120}>
        <DraftShot shot={shot}/>
      </Sequence>
    )}
  </AbsoluteFill>;
};
