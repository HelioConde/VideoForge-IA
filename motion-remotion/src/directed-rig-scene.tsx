/** Reusable draft renderer: independent source-space pivots, meshes and real perspective. */
import React,{useEffect,useLayoutEffect,useMemo} from 'react';
import {AbsoluteFill,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useLoader,useThree} from '@react-three/fiber';
import {BufferGeometry,DoubleSide,Float32BufferAttribute,PerspectiveCamera,
  SRGBColorSpace,TextureLoader} from 'three';
import {cameraAtFrame,directedMeshAtFrame,nodeTransformAtFrame,shotAtFrame,
  sourceWorldScale,validateDirectedProps,type DirectedNode,type DirectedRigProps,
  type DirectedShot} from './directed-rig-math';

const useTexture=(file:string)=>{
  const texture=useLoader(TextureLoader,staticFile(file));
  texture.colorSpace=SRGBColorSpace;
  return texture;
};
const Camera:React.FC<{shot:DirectedShot;frame:number}>=({shot,frame})=>{
  const camera=useThree(state=>state.camera);
  const {z,fovDeg,lookAt}=cameraAtFrame(shot,frame);
  useLayoutEffect(()=>{
    if(!(camera instanceof PerspectiveCamera))throw new Error('DIRECTED_RIG_PERSPECTIVE_REQUIRED');
    camera.position.set(0,0,z);camera.fov=fovDeg;
    camera.lookAt(...lookAt);camera.updateProjectionMatrix();camera.updateMatrixWorld();
  },[camera,z,fovDeg,lookAt[0],lookAt[1],lookAt[2]]);
  return null;
};
const Material:React.FC<{file:string}>=({file})=>{
  const texture=useTexture(file);
  return <meshBasicMaterial map={texture} transparent depthWrite={false}
    depthTest={false} side={DoubleSide} toneMapped={false}/>;
};
const Sprite:React.FC<{node:DirectedNode;shot:DirectedShot;frame:number;fps:number}>=({node,shot,frame,fps})=>{
  const geometry=useMemo(()=>{
    if(!node.mesh)return null;
    const data=directedMeshAtFrame(node,shot,frame,fps);
    // Existing mesh math emits canvas-centred vertices. This node's local
    // origin is its measured pivot, and all ancestors operate on that origin.
    const px=node.pivot[0]-shot.canvas.width/2;
    const py=shot.canvas.height/2-node.pivot[1];
    const positions=data.positions.map((v,i)=>i%3===0?v-px:i%3===1?v-py:v);
    const g=new BufferGeometry();
    g.setAttribute('position',new Float32BufferAttribute(positions,3));
    g.setAttribute('uv',new Float32BufferAttribute(data.uvs,2));
    g.setIndex(data.indices);g.computeVertexNormals();
    return g;
  },[node,shot,frame,fps]);
  useEffect(()=>()=>{geometry?.dispose();},[geometry]);
  if(!node.file||!node.bbox)return null;
  const [x,y,w,h]=node.bbox;
  if(geometry)return <mesh geometry={geometry} renderOrder={node.z}>
    <Material file={node.file}/>
  </mesh>;
  return <mesh position={[x+w/2-node.pivot[0],node.pivot[1]-y-h/2,0]}
    renderOrder={node.z}>
    <planeGeometry args={[w,h]}/><Material file={node.file}/>
  </mesh>;
};
const RigNode:React.FC<{node:DirectedNode;shot:DirectedShot;frame:number;fps:number}>=({node,shot,frame,fps})=>{
  const parent=node.parent===null?null:shot.nodes.find(n=>n.id===node.parent)!;
  const origin=parent?.pivot??[shot.canvas.width/2,shot.canvas.height/2];
  const t=nodeTransformAtFrame(shot,node.id,frame);
  return <group position={[node.pivot[0]-origin[0]+t.translateX,
    origin[1]-node.pivot[1]-t.translateY,0]}
    rotation={[0,0,-t.rotationZ*Math.PI/180]} scale={[t.scaleX,t.scaleY,1]}>
    <Sprite node={node} shot={shot} frame={frame} fps={fps}/>
    {shot.nodes.filter(n=>n.parent===node.id).map(child=><RigNode key={child.id}
      node={child} shot={shot} frame={frame} fps={fps}/>)}
  </group>;
};
const Background:React.FC<{shot:DirectedShot}>=({shot})=>shot.background?
  <mesh renderOrder={-1000000}>
    <planeGeometry args={[shot.canvas.width,shot.canvas.height]}/>
    <Material file={shot.background}/>
  </mesh>:null;

export const VideoForgeDirectedRigScene:React.FC<DirectedRigProps>=(props)=>{
  const frame=useCurrentFrame()+props.startFrame;
  const {width,height,fps}=useVideoConfig();
  validateDirectedProps(props);
  if(width!==props.width||height!==props.height||fps!==props.fps)
    throw new Error('DIRECTED_RIG_COMPOSITION_METADATA_MISMATCH');
  const shot=shotAtFrame(props.shots,frame);
  const scale=sourceWorldScale(shot.canvas,width,height);
  const camera=cameraAtFrame(shot,frame);
  return <AbsoluteFill style={{backgroundColor:'#000',overflow:'hidden'}}>
    <ThreeCanvas width={width} height={height}
      camera={{position:[0,0,camera.z],fov:camera.fovDeg,near:.01,far:1000}}
      gl={{alpha:true,antialias:true,preserveDrawingBuffer:true}}
      style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
      <Camera shot={shot} frame={frame}/>
      <group scale={[scale,scale,1]}>
        <Background shot={shot}/>
        {shot.nodes.filter(n=>n.parent===null).map(n=><RigNode key={shot.id+'/'+n.id}
          node={n} shot={shot} frame={frame} fps={fps}/>)}
      </group>
    </ThreeCanvas>
    <div style={{position:'absolute',left:12,right:12,top:12,padding:14,
      color:'#fff',background:'rgba(80,0,0,.88)',fontFamily:'sans-serif',
      fontSize:25,fontWeight:800,textAlign:'center'}}>
      RASCUNHO TÉCNICO — NÃO PUBLICÁVEL
    </div>
    <div style={{position:'absolute',left:12,right:12,bottom:12,padding:12,
      color:'#fff',background:'rgba(0,0,0,.85)',fontFamily:'sans-serif',fontSize:18}}>
      <div>{shot.id+' · quadro absoluto '+frame+' · '+props.channel+'/'+props.videoId}</div>
      <div>Pivôs provisórios · underlays e recomposição pendentes de revisão</div>
      {props.warnings.slice(0,3).map((warning,i)=><div key={i}>{warning}</div>)}
      {props.warnings.length>3?<div>{'Mais '+(props.warnings.length-3)+' avisos no relatório QA.'}</div>:null}
    </div>
  </AbsoluteFill>;
};
