/**
 * Future C01-P02 assembly: no generated artwork or automatic render approval.
 * Compose ONLY independently cut layers from the same approved shot mother.
 * Uses the existing Three.js + React Three Fiber + Remotion ThreeCanvas engine.
 */
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {RigidSprite} from './rig-three-scene';
import {swordPoseAtFrame,type SwordDrawTuning} from './remake-sword-motion';
import type {LayerSpec} from './rig-three-math';

export type RemakeSwordRigSpec={
  schema:'videoforge/remake-sword-rig/v1';
  shotId:'C01-P02';
  canvas:{width:number;height:number};
  motherSha256:string;
  anchorSha256:string;
  sourceRunId:number;
  technicalDraftOnly:true;
  technicalAssetsVerified:true;
  neutralRoundtripQaPassed:true;
  humanVisualReview:false;
  youtubeUploaded:false;
  wristPivot:[number,number];
  draw:SwordDrawTuning;
  layers:{
    underlay:LayerSpec;
    sheath:LayerSpec;
    blade:LayerSpec;
    hand:LayerSpec;
  };
};

export const RemakeSwordRig:React.FC<{
  rig:RemakeSwordRigSpec;
  shotDurationFrames:number;
}>=({rig,shotDurationFrames})=>{
  const frame=useCurrentFrame();
  const sha=/^[a-f0-9]{64}$/;
  if(rig.schema!=='videoforge/remake-sword-rig/v1'||
     rig.shotId!=='C01-P02'||rig.canvas.width!==1024||
     rig.canvas.height!==1536||!sha.test(rig.motherSha256)||
     !sha.test(rig.anchorSha256)||!Number.isSafeInteger(rig.sourceRunId)||
     rig.sourceRunId<=0||rig.technicalDraftOnly!==true||
     rig.technicalAssetsVerified!==true||
     rig.neutralRoundtripQaPassed!==true||
     rig.humanVisualReview!==false||
     rig.youtubeUploaded!==false||
     rig.wristPivot.length!==2||
     !rig.wristPivot.every(Number.isFinite)||
     rig.wristPivot[0]<0||rig.wristPivot[0]>rig.canvas.width||
     rig.wristPivot[1]<0||rig.wristPivot[1]>rig.canvas.height||
     shotDurationFrames!==90||
     Object.entries(rig.layers).some(([part,layer])=>
       !layer||layer.id!==part||!sha.test(layer.sha256)||
       layer.file!==`vf-remake/c01-p02/${part}.png`||
       !Array.isArray(layer.bbox)||layer.bbox.length!==4||
       layer.bbox.some((v,i)=>v!==[0,0,1024,1536][i])||
       !Number.isInteger(layer.z)
     ))
     throw new Error('REMAKE_SWORD_SOURCE_AND_VISUAL_QA_REQUIRED');

  const pose=swordPoseAtFrame(frame,shotDurationFrames,rig.draw);
  const {canvas,layers}=rig;
  const pivot:[number,number,number]=[
    rig.wristPivot[0]-canvas.width/2,
    canvas.height/2-rig.wristPivot[1],0,
  ];
  return <group>
    {/* Original mother underpaint: required before moving the hand/blade. */}
    <RigidSprite layer={layers.underlay} canvas={canvas}/>
    {/* Sheath stays anchored as the steel actually leaves it. */}
    <RigidSprite layer={layers.sheath} canvas={canvas}/>
    <group position={[pose.bladeDx,-pose.bladeDy,0]}>
      <RigidSprite layer={layers.blade} canvas={canvas}/>
    </group>
    {/* Independent hand motion, rotating about its true wrist joint. */}
    <group position={[pivot[0]+pose.handDx,pivot[1]-pose.handDy,0]}
      rotation={[0,0,pose.handAngleDeg*Math.PI/180]}>
      <group position={[-pivot[0],-pivot[1],0]}>
        <RigidSprite layer={layers.hand} canvas={canvas}/>
      </group>
    </group>
  </group>;
};
