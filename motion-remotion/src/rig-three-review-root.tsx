import React from 'react';
import {Composition} from 'remotion';
import {AnyaDraftReviewScene, type AnyaDraftReviewProps} from './rig-three-review-scene';

/** No default actual art or human approval; CLI must supply hashed props. */
const missingArt:AnyaDraftReviewProps={
  reviewOnly:true,
  youtubeUpload:false,
  durationFrames:240,
  background:'vf-scene/background.png',
  otherCharacters:'vf-scene/other-characters-static.png',
  rig:null,
};
export const VideoForgeAnyaReviewRoot:React.FC=()=>(
  <Composition
    id="VideoForgeAnyaRigDraftQA"
    component={AnyaDraftReviewScene}
    durationInFrames={240}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={missingArt}
    calculateMetadata={({props})=>({
      durationInFrames:Math.max(1,props.durationFrames||240)
    })}
  />
);
