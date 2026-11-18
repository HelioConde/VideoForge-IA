/** C01-P04 approved still -> editorial CAMERA-ONLY technical preview.
 * Preserves hands, spear and guards as one still source. No character rig.
 * This composition is never a substitute for the 40-shot official renderer.
 */
import React from 'react';
import {AbsoluteFill,Img,interpolate,staticFile,useCurrentFrame} from 'remotion';

export type C01P04CameraPreviewProps={
  schema:'videoforge/ep01-c01p04-static-camera-preview/v1';
  shotId:'C01-P04';
  durationFrames:70;
  sourceFile:'vf-ep01-c01p04-camera/scene-mother-approved-aligned.png';
  approvedOriginalSha256:string;
  alignedTechnicalSha256:string;
  approvedOriginalVerified:true;
  alignedSourceVerified:true;
  cameraOnly:true;
  separateHandParts:false;
  characterRigApproved:false;
  officialEpisodeApproved:false;
  youtubeUpload:false;
};

const ORIGINAL='a55a2beb23b9015c729ad2099e906fa6062ac76e1ce310b1ab8f4390be2dd1dd';
const ALIGNED='b439b45f3dcf789534b2787dc648ca521e8327d639f2b928bd42b932b1b20c7d';
const FILE='vf-ep01-c01p04-camera/scene-mother-approved-aligned.png';

export const C01P04CameraOnlyPreview:React.FC<C01P04CameraPreviewProps>=props=>{
  if(props.schema!=='videoforge/ep01-c01p04-static-camera-preview/v1'||
     props.shotId!=='C01-P04'||props.durationFrames!==70||
     props.sourceFile!==FILE||
     props.approvedOriginalSha256!==ORIGINAL||
     props.alignedTechnicalSha256!==ALIGNED||
     props.approvedOriginalVerified!==true||
     props.alignedSourceVerified!==true||
     props.cameraOnly!==true||props.separateHandParts!==false||
     props.characterRigApproved!==false||
     props.officialEpisodeApproved!==false||props.youtubeUpload!==false)
       throw new Error('EP01_C01P04_CAMERA_ONLY_REQUIRES_APPROVED_REAL_SOURCE');
  const frame=useCurrentFrame();
  // A single flat source cannot provide true parallax: zoom simulates only
  // a camera dolly-out. No character pixels change relative to the spear.
  const zoom=interpolate(frame,[0,69],[1.075,1],{
    extrapolateLeft:'clamp',extrapolateRight:'clamp',
  });
  const light=interpolate(frame,[0,35,69],[0.055,0.085,0.055],{
    extrapolateLeft:'clamp',extrapolateRight:'clamp',
  });
  return <AbsoluteFill style={{backgroundColor:'#09090c',overflow:'hidden'}}>
    <Img src={staticFile(FILE)} style={{
      position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover',
      transform:`scale(${zoom.toFixed(6)})`,transformOrigin:'center center',
    }}/>
    <AbsoluteFill style={{
      pointerEvents:'none',
      background:`linear-gradient(108deg, rgba(250,211,127,${light.toFixed(5)}) 0%, transparent 58%)`,
    }}/>
    <AbsoluteFill style={{
      pointerEvents:'none',
      background:'radial-gradient(ellipse at center, transparent 48%, rgba(0,0,0,0.19) 100%)',
    }}/>
    <div style={{
      position:'absolute',left:8,right:8,bottom:13,padding:'7px 10px',
      background:'rgba(0,0,0,.79)',color:'#ffffff',
      fontFamily:'sans-serif',fontSize:15,fontWeight:600,
      textAlign:'center',letterSpacing:.35,
    }}>C01-P04 • PRÉVIA TÉCNICA DE CÂMERA • SEM RIG DE MÃOS</div>
  </AbsoluteFill>;
};
