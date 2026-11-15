import React from 'react';
import {Composition} from 'remotion';
import {C12TechnicalMeshPreview} from './c12-mesh-technical';
import type {C12TechnicalProps} from './c12-mesh-technical-contract';

/** Default fails closed: never preview missing PNGs with made-up art. */
const blocked = {
  schema:'videoforge/c12-technical-three-mesh-preview/v1',
  fps:30, sourceCanvas:{width:941,height:1672},
  width:720,height:1280,totalFrames:240,expectedMeshTriangles:512,
  status:'TECHNICAL_NO_HUMAN_APPROVAL',sourceOriginalsArchived:false,
  officialVideoApproved:false,imageGenerationCalls:0,shots:[],
} as unknown as C12TechnicalProps;

export const VideoForgeC12TechnicalRoot:React.FC=()=>(
  <Composition
    id="VideoForgeC12MeshDraftQA"
    component={C12TechnicalMeshPreview}
    durationInFrames={240}
    fps={30}
    width={720}
    height={1280}
    defaultProps={blocked}
  />
);
