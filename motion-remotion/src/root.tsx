import React from 'react';
import {Composition} from 'remotion';
import {VideoForgeLayerScene,LayerSceneProps} from './scene-layer-preview';

const defaultProps:LayerSceneProps={
  id:'videoforge-test',
  durationFrames:240,
  preset:'equilibrado',
  background:'vf-scene/background.png',
  character:'vf-scene/character-main.png',
  foreground:'vf-scene/foreground-roof.png',
  silence:'vf-scene/silence.wav',
  layerSourceHash:'',
  scene:'cena-01',
};

export const VideoForgeRoot:React.FC=()=>(
  <Composition
    id="VideoForgeLayerScene"
    component={VideoForgeLayerScene}
    durationInFrames={240}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={defaultProps}
    calculateMetadata={({props})=>({
      durationInFrames:Math.max(120,Math.min(360,props.durationFrames||240)),
    })}
  />
);
