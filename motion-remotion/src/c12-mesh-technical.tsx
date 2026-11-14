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
import {validateC12TechnicalProps, type C12TechnicalShot, type C12TechnicalProps} from './c12-mesh-technical-contract';

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
