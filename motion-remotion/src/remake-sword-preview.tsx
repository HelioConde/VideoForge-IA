/**
 * C01-P02 preview of ONLY verified layer-specific PNG sprites.
 * Separate Three.js pivots; never animate or zoom the whole mother PNG.
 * Visible watermark, NO publishable/official composition.
 */
import React from 'react';
import {AbsoluteFill,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {RemakeSwordRig,type RemakeSwordRigSpec} from './remake-sword-rig';

export type SwordDraftProps={
  schema:'videoforge/remake-sword-technical-preview/v1';
  shotId:'C01-P02';
  durationFrames:90;
  sourceRealArtworkVerified:true;
  officialVideoApproved:false;
  youtubeUploaded:false;
  rig:RemakeSwordRigSpec;
};

export const RemakeSwordTechnicalPreview:React.FC<SwordDraftProps>=props=>{
  if(props.schema!=='videoforge/remake-sword-technical-preview/v1'||
    props.shotId!=='C01-P02'||props.durationFrames!==90||
    props.sourceRealArtworkVerified!==true||
    props.officialVideoApproved!==false||
    props.youtubeUploaded!==false||
    !props.rig||props.rig.technicalDraftOnly!==true||
    props.rig.humanVisualReview!==false||
    props.rig.neutralRoundtripQaPassed!==true)
      throw new Error('REMAKE_C01_P02_REAL_SOURCE_AND_TECHNICAL_QA_REQUIRED');
  const {width,height}=useVideoConfig();
  const scale=Math.max(width/props.rig.canvas.width,height/props.rig.canvas.height);
  return <AbsoluteFill style={{overflow:'hidden',backgroundColor:'#09090a'}}>
    <ThreeCanvas width={width} height={height} orthographic
      camera={{position:[0,0,100],zoom:1}}
      gl={{alpha:true,antialias:true,preserveDrawingBuffer:true}}
      style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
      <group scale={[scale,scale,1]}>
        <RemakeSwordRig rig={props.rig} shotDurationFrames={props.durationFrames}/>
      </group>
    </ThreeCanvas>
    <div style={{
      position:'absolute',top:40,left:18,right:18,zIndex:99,
      padding:'10px 14px',backgroundColor:'rgba(0,0,0,.84)',
      color:'#fafafa',fontFamily:'sans-serif',fontSize:23,
      fontWeight:700,textAlign:'center',
    }}>PRÉVIA TÉCNICA C01-P02 • ARTE NÃO APROVADA</div>
  </AbsoluteFill>;
};
