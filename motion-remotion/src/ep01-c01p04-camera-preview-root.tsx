import React from 'react';
import {Composition} from 'remotion';
import {C01P04CameraOnlyPreview,type C01P04CameraPreviewProps}
  from './ep01-c01p04-camera-preview';

const blocked={
  schema:'videoforge/ep01-c01p04-static-camera-preview/v1',
  shotId:'C01-P04',durationFrames:70,
  sourceFile:'vf-ep01-c01p04-camera/scene-mother-approved-aligned.png',
  approvedOriginalSha256:'',alignedTechnicalSha256:'',
  approvedOriginalVerified:false,alignedSourceVerified:false,
  cameraOnly:false,separateHandParts:true,
  characterRigApproved:false,officialEpisodeApproved:false,youtubeUpload:false,
} as unknown as C01P04CameraPreviewProps;

export const C01P04CameraPreviewRoot:React.FC=()=><Composition
  id="C01P04CameraOnlyTechnicalPreview"
  component={C01P04CameraOnlyPreview}
  fps={30} durationInFrames={70} width={540} height={960}
  defaultProps={blocked}
/>;
