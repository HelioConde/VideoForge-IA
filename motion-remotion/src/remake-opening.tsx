/** C01-P01 ONLY: actual black video + original procedural steel sound.
 * Independent Remotion composition, never substitutes for official EP01 gate.
 */
import React from 'react';
import {AbsoluteFill,Audio,staticFile} from 'remotion';

export type RemakeOpeningProps={
  schema:'videoforge/remake-black-opening/v1';
  shotId:'C01-P01';
  audioSha256:string;
  durationFrames:60;
  renderOfficialApproved:false;
  youtubeUploaded:false;
};

export const RemakeBlackOpening:React.FC<RemakeOpeningProps>=props=>{
  if(props.schema!=='videoforge/remake-black-opening/v1'||
    props.shotId!=='C01-P01'||props.durationFrames!==60||
    !/^[a-f0-9]{64}$/.test(props.audioSha256)||
    props.renderOfficialApproved!==false||props.youtubeUploaded!==false)
    throw new Error('REMAKE_OPENING_REAL_AUDIO_SHA_AND_PREVIEW_ONLY_REQUIRED');
  return <AbsoluteFill style={{backgroundColor:'#000000'}}>
    <Audio src={staticFile('vf-remake/c01-p01/sword-original.wav')}/>
  </AbsoluteFill>;
};
