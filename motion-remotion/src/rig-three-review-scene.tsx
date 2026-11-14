/** Strictly non-official ThreeCanvas visual QA for existing scene-mother art.
 * Production validation in rig_three_contract.py is NEVER bypassed.
 * The only purpose is discovering seams and movements that neutral 2D QA
 * cannot catch. Art review, official MP4, and YouTube remain blocked.
 */
import React from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {CharacterParts, type CharacterRigParts, type CharacterMotion} from './rig-three-scene';

export type AnyaDraftReviewProps={
  reviewOnly:true;
  youtubeUpload:false;
  durationFrames:number;
  background:string;
  otherCharacters:string;
  rig:(CharacterRigParts&{
    schema:'videoforge/rig-three/v1';
    channel:'otaku-br';
    video_id:'spy-x-family-familia-de-mentira';
    scene:'cena-01';
    provisional:true;
    humanReview:Record<string,boolean>;
  })|null;
};

/** This composition is deliberately separate from official VideoForgeMeshRigScene. */
export const AnyaDraftReviewScene:React.FC<AnyaDraftReviewProps>=({
  reviewOnly,youtubeUpload,durationFrames,background,otherCharacters,rig,
})=>{
  const frame=useCurrentFrame();
  const {fps,width,height}=useVideoConfig();
  if(reviewOnly!==true || youtubeUpload!==false ||
     rig?.schema!=='videoforge/rig-three/v1' ||
     rig.channel!=='otaku-br' ||
     rig.video_id!=='spy-x-family-familia-de-mentira' ||
     rig.scene!=='cena-01' || rig.provisional!==true ||
     !rig.humanReview || Object.values(rig.humanReview).some(Boolean) ||
     rig.layers.length!==6 ||
     !(['body-no-head','head-open','head-closed','hair-front-left',
        'hair-front-right','hand'].every(id=>rig.layers.some(l=>l.id===id))) ||
     !rig.layers.find(l=>l.id==='hair-front-left')?.mesh ||
     !rig.layers.find(l=>l.id==='hair-front-right')?.mesh){
    throw new Error('ANYA_DRAFT_REVIEW_MUST_USE_UNAPPROVED_ART_AND_ALL_6_LAYERS');
  }
  const scale=Math.min(width/rig.canvas.width,height/rig.canvas.height);
  const motion:CharacterMotion={frame,fps,duration:durationFrames,
    blinkFrames:rig.blinkFrames};
  return <AbsoluteFill style={{background:'#10131c',overflow:'hidden'}}>
    <Img src={staticFile(background)} style={{
      width:'100%',height:'100%',objectFit:'contain',position:'absolute',inset:0
    }}/>
    <Img src={staticFile(otherCharacters)} style={{
      width:'100%',height:'100%',objectFit:'contain',position:'absolute',inset:0
    }}/>
    <ThreeCanvas width={width} height={height} orthographic
      camera={{position:[0,0,100],zoom:1}}
      gl={{alpha:true,antialias:true,preserveDrawingBuffer:true}}
      style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
      <group scale={[scale,scale,1]}>
        <CharacterParts rig={rig} motion={motion}/>
      </group>
    </ThreeCanvas>
    <div style={{
      position:'absolute',left:12,right:12,top:12,
      background:'rgba(35,3,9,.94)',padding:14,color:'#fff',
      fontFamily:'sans-serif',fontWeight:700,fontSize:19,textAlign:'center'
    }}>PRÉVIA TÉCNICA / ARTES NÃO APROVADAS / NÃO PUBLICAR</div>
  </AbsoluteFill>;
};
