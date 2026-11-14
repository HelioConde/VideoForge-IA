import React from 'react';
import {Composition} from 'remotion';
import {VideoForgeCinematicEpisode} from './cinematic-episode';
import type {CinematicEpisodeProps} from './cinematic-timeline';

/**
 * Explicit opt-in entrypoint. Without an approved per-shot inputProps JSON,
 * rendering FAILS. Do not insert sample shots/placeholder art.
 */
const blockedDefaults={
  schema:'videoforge/cinematic-remotion-episode/v1',
  channel:'alchemy-lab',
  videoId:'mmorpg-conquiste-a-princesa-ep01',
  fps:30,
  width:1080,
  height:1920,
  totalFrames:4890,
  renderApproved:false,
  shots:[],
} as unknown as CinematicEpisodeProps;

export const VideoForgeCinematicRoot:React.FC=()=>(
  <Composition
    id="VideoForgeCinematicEpisode"
    component={VideoForgeCinematicEpisode}
    durationInFrames={4890}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={blockedDefaults}
    calculateMetadata={({props})=>({
      // The component itself validates every shot before the first frame.
      durationInFrames:props.totalFrames,
    })}
  />
);
