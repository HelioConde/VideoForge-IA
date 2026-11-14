import React from 'react';
import {Composition} from 'remotion';
import {VideoForgeMeshRigScene, type VideoForgeMeshRigProps} from './rig-three-scene';

/** Strictly separate bundle from old src/index.ts and its legacy runtime. */
const demoDisabled:VideoForgeMeshRigProps={
  id:'rig-manifest-required',
  scene:'cena-01',
  durationFrames:240,
  rig:null,
  background:'vf-scene/background.png',
  foreground:null,
  audio:null,
  draftPreview:true,
};
export const VideoForgeThreeRoot:React.FC=()=>(
  <Composition
    id="VideoForgeMeshRigScene"
    component={VideoForgeMeshRigScene}
    durationInFrames={240}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={demoDisabled}
    calculateMetadata={({props})=>({
      durationInFrames:Math.max(1,props.durationFrames||240),
    })}
  />
);
