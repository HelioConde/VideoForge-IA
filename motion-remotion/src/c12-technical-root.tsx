import React from 'react';
import {Composition} from 'remotion';
import {C12TechnicalMeshPreview} from './c12-mesh-technical';
import {validateC12TechnicalProps,type C12TechnicalProps} from './c12-mesh-technical-contract';

// Deliberately invalid until the Python importer verifies committed original bytes.
const requiredProps={schema:'videoforge/c12-technical-three-mesh-preview/v1',
  sourceOriginalsArchived:false,officialVideoApproved:false,shots:[]} as unknown as C12TechnicalProps;
export const C12TechnicalRoot:React.FC=()=><Composition
  id="C12TechnicalMeshPreview" component={C12TechnicalMeshPreview}
  durationInFrames={240} fps={30} width={720} height={1280} defaultProps={requiredProps}
  calculateMetadata={({props})=>{validateC12TechnicalProps(props);return {};}}
/>;
