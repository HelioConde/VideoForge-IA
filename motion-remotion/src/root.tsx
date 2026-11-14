import React from 'react';
import {Composition} from 'remotion';
import {VideoForgeLayerScene,LayerSceneProps} from './scene-layer-preview';
import {SpyFamilyEpisode,SpyEpisodeProps} from './spy-family-episode';
import {sceneFocus,sceneSetting} from './spy-family-rig';

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

const spyDefaultProps:SpyEpisodeProps={
  channel:'otaku-br',videoId:'spy-x-family-familia-de-mentira',
  scenes:[{id:'gancho-anya',card:'ANYA SABE O SEGREDO',
    focus:sceneFocus('gancho-anya'),setting:sceneSetting('gancho-anya'),
    durationFrames:120,audio:'vf-spy/cena-01.wav'}],
  totalFrames:120,draftPreview:true,
};
export const VideoForgeRoot:React.FC=()=>(
  <>
  <Composition
    id="VideoForgeLayerScene"
    component={VideoForgeLayerScene}
    durationInFrames={240}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={defaultProps}
    calculateMetadata={({props})=>({
      durationInFrames:Math.max(1,props.durationFrames||240),
    })}
  />
  <Composition
    id="SpyFamilyEpisodePreview"
    component={SpyFamilyEpisode}
    durationInFrames={120}
    fps={30}
    width={540}
    height={960}
    defaultProps={spyDefaultProps}
    calculateMetadata={({props})=>({
      durationInFrames:Math.max(1,props.totalFrames||120),
    })}
  />
  </>
);
