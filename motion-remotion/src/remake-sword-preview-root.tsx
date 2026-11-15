import React from 'react';
import {Composition} from 'remotion';
import {RemakeSwordTechnicalPreview,type SwordDraftProps} from './remake-sword-preview';

/** No sample approved artwork or phantom rig in defaultProps. */
const blocked={
  schema:'videoforge/remake-sword-technical-preview/v1',
  shotId:'C01-P02',durationFrames:90,
  sourceRealArtworkVerified:false,
  officialVideoApproved:false,youtubeUploaded:false,rig:null,
} as unknown as SwordDraftProps;

export const RemakeSwordPreviewRoot:React.FC=()=>(
  <Composition id="VideoForgeC01P02SwordTechnical"
    component={RemakeSwordTechnicalPreview}
    durationInFrames={90} fps={30} width={1080} height={1920}
    defaultProps={blocked}/>
);
