/**
 * VideoForge multi-shot cinematic Remotion composition.
 * Independent shot sources and approved mesh rigs ONLY. No poster zoom/pan.
 * Synchronized exclusively by Remotion's frame clock (30 fps).
 */
import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {CharacterParts} from './rig-three-scene';
import {
  shotDurationFrames,validateCinematicRender,
  type CinematicEpisodeProps,type CinematicShot,
} from './cinematic-timeline';

const hudStyle:React.CSSProperties={
  position:'absolute',
  left:'8%',right:'8%',bottom:'11%',
  padding:20,borderRadius:12,
  backgroundColor:'rgba(7,18,45,0.85)',
  color:'#eef6ff',
  fontFamily:'sans-serif',
  fontWeight:700,fontSize:34,
  border:'2px solid rgba(127,196,255,.75)',
  textShadow:'0 2px 5px rgba(0,0,0,.75)',
};

const ShotFrame:React.FC<{shot:CinematicShot}>=({shot})=>{
  // Inside <Sequence>, this clock is local to the individual shot.
  const frame=useCurrentFrame();
  const {fps,width,height}=useVideoConfig();
  if(shot.type==='black'){
    return <AbsoluteFill style={{backgroundColor:'#000000'}}/>;
  }
  // All mandatory artifacts and approval gates were already validated
  // before the component mounted. Never use a missing-rig fallback.
  const duration=shotDurationFrames(shot);
  const rigs=shot.actors??[];
  return <AbsoluteFill style={{
    overflow:'hidden',backgroundColor:'#05070d',
  }}>
    <Img src={staticFile(shot.backgroundFile!)}
      style={{position:'absolute',inset:0,width:'100%',height:'100%',
        objectFit:'cover'}}/>
    {rigs.length>0?<ThreeCanvas
      width={width} height={height} orthographic
      camera={{position:[0,0,100],zoom:1}}
      gl={{alpha:true,antialias:true,preserveDrawingBuffer:true}}
      style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
      {rigs.map(actor=>{
        // Source canvas 1024x1536 => 1080x1920 via 1.25x and crop 100px
        // from each side. Maintain aspect; do not stretch a face.
        const scale=Math.max(
          width/actor.rig.canvas.width,
          height/actor.rig.canvas.height,
        );
        return <group key={actor.id} scale={[scale,scale,1]}>
          <CharacterParts rig={actor.rig} motion={{
            frame,fps,duration,blinkFrames:actor.rig.blinkFrames,
          }}/>
        </group>;
      })}
    </ThreeCanvas>:null}
    {shot.hudPolicy==='remotion_overlay' && shot.hud ?
      <div style={hudStyle}>
        {shot.hud.heading}
        {shot.hud.detail?<div style={{fontSize:24,fontWeight:400,marginTop:10}}>
          {shot.hud.detail}
        </div>:null}
      </div>:null}
    {shot.audioFile?<Audio src={staticFile(shot.audioFile)}/>:null}
  </AbsoluteFill>;
};

/** There is no preview fallback. Rendering fails if ANY visual shot is pending. */
export const VideoForgeCinematicEpisode:React.FC<CinematicEpisodeProps>=props=>{
  validateCinematicRender(props);
  return <AbsoluteFill style={{backgroundColor:'#000'}}>
    {props.shots.map(shot=>
      <Sequence key={shot.id}
        name={shot.id+' '+shot.type}
        from={shot.startFrame}
        durationInFrames={shotDurationFrames(shot)}>
        <ShotFrame shot={shot}/>
      </Sequence>
    )}
  </AbsoluteFill>;
};
