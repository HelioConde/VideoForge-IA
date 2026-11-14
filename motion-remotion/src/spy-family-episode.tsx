/** Otaku BR Spy Family: Short completo com 1 rig vetorial por cena e voz pt-BR. */
import React from 'react';
import {AbsoluteFill,Audio,Series,staticFile} from 'remotion';
import {SpyFamilyRigScene,SpySceneProps} from './spy-family-rig';

export type SpyEpisodeScene={
  id:string;
  card:string;
  focus:SpySceneProps['focus'];
  setting:SpySceneProps['setting'];
  durationFrames:number;
  audio:string;
};
export type SpyEpisodeProps={
  channel:string;
  videoId:string;
  scenes:SpyEpisodeScene[];
  totalFrames:number;
  draftPreview:boolean;
};
export const SpyFamilyEpisode:React.FC<SpyEpisodeProps>=({channel,videoId,scenes,draftPreview})=>{
  if(channel!=='otaku-br'||videoId!=='spy-x-family-familia-de-mentira')
    throw new Error('SPY_EPISODE_INVALID_CHANNEL');
  return <AbsoluteFill style={{background:'#0d1727'}}>
    <Series>
      {scenes.map((scene,i)=>
        <Series.Sequence key={i} durationInFrames={scene.durationFrames}
          name={'Cena '+String(i+1)+' / '+scene.id}>
          <SpyFamilyRigScene
            id={scene.id} card={scene.card}
            focus={scene.focus} setting={scene.setting}
            durationFrames={scene.durationFrames}
            draftPreview={draftPreview}/>
          <Audio src={staticFile(scene.audio)} volume={1}/>
        </Series.Sequence>
      )}
    </Series>
  </AbsoluteFill>;
};
