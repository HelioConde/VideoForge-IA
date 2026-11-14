/**
 * True 2D mesh rendering with Three.js in Remotion 4.
 * Separate RGBA sprites AND validated rig required. No flat PNG bob fallback.
 * Deterministic vertex positions from useCurrentFrame(), not useFrame().
 */
import React, {useEffect,useMemo} from 'react';
import {AbsoluteFill,Audio,Img,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useLoader} from '@react-three/fiber';
import {BufferGeometry,DoubleSide,Float32BufferAttribute,SRGBColorSpace,TextureLoader} from 'three';
import {bodyBreathAtFrame,headRotationDegAtFrame,isClosedAtFrame,meshGridAtFrame,
  type LayerSpec,type MeshType,type ThreeRigManifest} from './rig-three-math';

type Canvas={width:number;height:number};
type Motion={frame:number;fps:number;duration:number;blinkFrames:number[]};
export type VideoForgeMeshRigProps={
  id:string;scene:string;durationFrames:number;rig:ThreeRigManifest;
  background:string;foreground?:string|null;audio?:string|null;draftPreview?:boolean;
};

const sourceCenter=(bbox:[number,number,number,number],canvas:Canvas):[number,number,number]=>[
  bbox[0]+bbox[2]/2-canvas.width/2,
  canvas.height/2-(bbox[1]+bbox[3]/2),0,
];
const sourcePoint=(point:[number,number],canvas:Canvas):[number,number,number]=>[
  point[0]-canvas.width/2,canvas.height/2-point[1],0,
];
const useRigTexture=(file:string)=>{
  const texture=useLoader(TextureLoader,staticFile(file));
  texture.colorSpace=SRGBColorSpace;
  return texture;
};
const RigidSprite:React.FC<{layer:LayerSpec;canvas:Canvas}>=({layer,canvas})=>{
  const texture=useRigTexture(layer.file);
  const [,,w,h]=layer.bbox;
  const position=sourceCenter(layer.bbox,canvas);
  position[2]=layer.z;
  return <mesh position={position} renderOrder={layer.z}>
    <planeGeometry args={[w,h]}/>
    <meshBasicMaterial map={texture} transparent depthWrite={false}
      depthTest={false} side={DoubleSide} toneMapped={false}/>
  </mesh>;
};
const DeformableSprite:React.FC<{layer:LayerSpec;canvas:Canvas;kind:MeshType;motion:Motion}>=({
  layer,canvas,kind,motion,
})=>{
  if(!layer.mesh)throw new Error('THREE_RIG_MESH_SPEC_MISSING');
  const texture=useRigTexture(layer.file);
  const {frame,fps,duration,blinkFrames}=motion;
  const geometry=useMemo(()=>{
    const data=meshGridAtFrame({
      bbox:layer.bbox,canvas,spec:layer.mesh!,kind,frame,fps,duration,blinkFrames,
    });
    const g=new BufferGeometry();
    g.setAttribute('position',new Float32BufferAttribute(data.positions,3));
    g.setAttribute('uv',new Float32BufferAttribute(data.uvs,2));
    g.setIndex(data.indices);
    g.computeVertexNormals();
    return g;
  },[layer,canvas.width,canvas.height,kind,frame,fps,duration,blinkFrames]);
  useEffect(()=>()=>{geometry.dispose();},[geometry]);
  return <mesh geometry={geometry}
    position={[0,0,layer.z]} renderOrder={layer.z}>
    <meshBasicMaterial map={texture} transparent depthWrite={false}
      depthTest={false} side={DoubleSide} toneMapped={false}/>
  </mesh>;
};
const Layer:React.FC<{layer:LayerSpec;canvas:Canvas;motion:Motion}>=({
  layer,canvas,motion,
})=>{
  if(layer.mesh){
    return <DeformableSprite layer={layer} canvas={canvas}
      kind={layer.id as MeshType} motion={motion}/>;
  }
  return <RigidSprite layer={layer} canvas={canvas}/>;
};
const CharacterParts:React.FC<{rig:ThreeRigManifest;motion:Motion}>=({rig,motion})=>{
  const {frame,fps,duration,blinkFrames}=motion;
  const canvas=rig.canvas;
  const find=(id:string)=>rig.layers.find(x=>x.id===id);
  const body=find('body-no-head');
  const headOpen=find('head-open');
  const headClosed=find('head-closed');
  if(!body||!headOpen||!headClosed)
    throw new Error('THREE_RIG_INDEPENDENT_BODY_HEAD_REQUIRED');
  const headAngle=headRotationDegAtFrame(frame,fps,duration,
    blinkFrames,rig.headMaxRotationDeg);
  const bodyMotion=bodyBreathAtFrame(frame,fps,duration,blinkFrames);
  const pivot=sourcePoint(rig.neckPivot,canvas);
  const selectedHead=isClosedAtFrame(frame,blinkFrames)?headClosed:headOpen;
  const hairBehind=rig.layers.filter(x=>x.id==='hair-back');
  const hairFront=rig.layers.filter(x=>x.id==='hair-front');
  const moving=rig.layers.filter(x=>x.id!=='body-no-head'&&
      x.id!=='head-open'&&x.id!=='head-closed'&&
      x.id!=='hair-back'&&x.id!=='hair-front');
  return <group position={[0,-bodyMotion.translateY,0]}
    scale={[bodyMotion.scaleX,bodyMotion.scaleY,1]}>
    {moving.map(layer=><Layer key={layer.id} layer={layer}
      canvas={canvas} motion={motion}/>)}
    <RigidSprite layer={body} canvas={canvas}/>
    {/* Head rotates about neck, not about centre of full PNG. */}
    <group position={pivot} rotation={[0,0,-headAngle*Math.PI/180]}>
      <group position={[-pivot[0],-pivot[1],0]}>
        {hairBehind.map(layer=><Layer key={layer.id} layer={layer}
          canvas={canvas} motion={motion}/>)}
        <RigidSprite layer={selectedHead} canvas={canvas}/>
        {hairFront.map(layer=><Layer key={layer.id} layer={layer}
          canvas={canvas} motion={motion}/>)}
      </group>
    </group>
  </group>;
};
/** Distinct official candidate composition; never replace legacy preview. */
export const VideoForgeMeshRigScene:React.FC<VideoForgeMeshRigProps>=({
  scene,durationFrames,rig,background,foreground,audio,draftPreview,
})=>{
  const frame=useCurrentFrame();
  const {fps,width,height}=useVideoConfig();
  if(rig?.schema!=='videoforge/rig-three/v1'||
    rig.rigType!=='independent-parts-and-deformable-mesh'||
    !rig.technicalAssetsVerified||!rig.humanVisualReview)
    throw new Error('THREE_RIG_VALIDATED_REAL_ASSETS_REQUIRED');
  if(rig.layers.length<3||!rig.layers.some(l=>Boolean(l.mesh)))
    throw new Error('THREE_RIG_ACTUAL_DEFORMABLE_MESH_REQUIRED');
  const contentScale=Math.min(width/rig.canvas.width,height/rig.canvas.height);
  const motion={frame,fps,duration:durationFrames,blinkFrames:rig.blinkFrames};
  return <AbsoluteFill style={{overflow:'hidden',backgroundColor:'#100e1c'}}>
    <Img src={staticFile(background)} style={{
      position:'absolute',inset:0,width:'100%',height:'100%',
      objectFit:'cover',transform:'scale(1.12)',
      filter:'blur(36px) brightness(.55)',
    }}/>
    <Img src={staticFile(background)} style={{
      position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'contain',
    }}/>
    <ThreeCanvas width={width} height={height} orthographic
      camera={{position:[0,0,100],zoom:1}}
      gl={{alpha:true,antialias:true,preserveDrawingBuffer:true}}
      style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
      <group scale={[contentScale,contentScale,1]}>
        <CharacterParts rig={rig} motion={motion}/>
      </group>
    </ThreeCanvas>
    {foreground ? <Img src={staticFile(foreground)} style={{
      position:'absolute',inset:0,width:'100%',height:'100%',
      objectFit:'contain',pointerEvents:'none',
    }}/> : null}
    {audio ? <Audio src={staticFile(audio)}/> : null}
    {draftPreview ? <div style={{
      position:'absolute',top:45,left:24,right:24,color:'#fff',
      background:'rgba(80,0,0,.80)',padding:18,fontSize:28,
      fontWeight:800,textAlign:'center',fontFamily:'sans-serif',
    }}>{'RIG 2D THREE — REVISAO PENDENTE · '+scene}</div> : null}
  </AbsoluteFill>;
};
