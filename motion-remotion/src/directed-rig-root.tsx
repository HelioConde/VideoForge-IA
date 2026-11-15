import React from 'react';
import {Composition} from 'remotion';
import {VideoForgeDirectedRigScene} from './directed-rig-scene';
import {validateDirectedProps,type DirectedRigProps} from './directed-rig-math';

// No sample art or implicit approval. Rendering requires prepared props.
const requiredProps:DirectedRigProps={schema:'videoforge/directed-rig-preview/v1',
  mode:'technical_draft',channel:'input-required',videoId:'input-required',id:'input-required',
  width:1080,height:1920,fps:30,startFrame:0,durationFrames:1,shots:[],warnings:[],
  humanVisualReview:false,publishable:false};
export const VideoForgeDirectedRigRoot:React.FC=()=><Composition
  id="VideoForgeDirectedRigScene" component={VideoForgeDirectedRigScene}
  durationInFrames={1} fps={30} width={1080} height={1920} defaultProps={requiredProps}
  calculateMetadata={({props})=>{
    validateDirectedProps(props);
    return {durationInFrames:props.durationFrames,fps:props.fps,
      width:props.width,height:props.height};
  }}/>
;
