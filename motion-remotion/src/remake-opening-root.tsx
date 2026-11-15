import React from 'react';
import {Composition} from 'remotion';
import {RemakeBlackOpening,type RemakeOpeningProps} from './remake-opening';

const blocked={
  schema:'videoforge/remake-black-opening/v1',
  shotId:'C01-P01',
  audioSha256:'',
  durationFrames:60,
  renderOfficialApproved:false,
  youtubeUploaded:false,
} as RemakeOpeningProps;

export const VideoForgeRemakeOpeningRoot:React.FC=()=>(
  <Composition id="VideoForgeRemakeBlackOpening"
    component={RemakeBlackOpening}
    fps={30} durationInFrames={60} width={1080} height={1920}
    defaultProps={blocked}/>
);
