import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, interpolate, registerRoot, staticFile, useCurrentFrame} from 'remotion';

type View = {zoom:number;x:number;y:number};
type Shot = {id:string;duration_frames:number;source:unknown;sourceFile?:string;approval_status:string;
  camera:{mode:string;start:View;end:View;dolly:number;true_parallax:boolean};
  focus:{blur_start_px:number;blur_end_px:number};lighting:{exposure_start:number;exposure_end:number;warm_glow:number};
  rig:{enabled:boolean;independent_hands:boolean};
  continuity_gate?:{status:string;qa_notice:string;not_an_art_approval:boolean;animated_motion_verified:boolean}};
type Props = {schema:string;technical_preview_only:boolean;official_episode_approved:boolean;youtube_upload:boolean;image_provider_calls:number;durationFrames:number;shots:Shot[]};

const Picture:React.FC<{shot:Shot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const t = Math.min(1, Math.max(0, frame/(shot.duration_frames-1)));
  const smooth = t*t*(3-2*t);
  const lerp = (a:number,b:number) => a+(b-a)*smooth;
  if (shot.rig.enabled || shot.rig.independent_hands || shot.camera.true_parallax || shot.camera.dolly !== 0) throw new Error('Camera-only contract violated');
  if (!shot.source) return <AbsoluteFill style={{backgroundColor:'black'}}/>;
  if (!shot.sourceFile?.startsWith('vf-ep01-camera-batch/')) throw new Error('Missing verified static source');
  const zoom = lerp(shot.camera.start.zoom,shot.camera.end.zoom);
  if (zoom<1 || zoom>1.15) throw new Error('Unsafe camera scale');
  // Transform origin remains inside the canvas; scale >= 1 cannot reveal empty borders.
  // Brightness reveal is global: it does not invent a moving sword or depth layers.
  const exposure = interpolate(frame,[0,Math.max(1,Math.floor(shot.duration_frames*.4))],
    [shot.lighting.exposure_start,shot.lighting.exposure_end],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  return <AbsoluteFill style={{backgroundColor:'black',overflow:'hidden'}}>
    <Img src={staticFile(shot.sourceFile)} style={{width:'100%',height:'100%',objectFit:'cover',
      transform:`scale(${zoom})`,transformOrigin:`${lerp(shot.camera.start.x,shot.camera.end.x)}% ${lerp(shot.camera.start.y,shot.camera.end.y)}%`,
      filter:`brightness(${exposure}) blur(${lerp(shot.focus.blur_start_px,shot.focus.blur_end_px)}px)`}}/>
    <AbsoluteFill style={{background:'linear-gradient(120deg,transparent 35%,#ffc36b 65%,transparent 90%)',opacity:shot.lighting.warm_glow*exposure}}/>
    {shot.continuity_gate?.status === 'blocked_pending_visual_rig' && <div style={{
      position:'absolute',top:16,left:12,right:12,padding:10,
      background:'rgba(14,19,28,0.88)',color:'#fff',fontFamily:'sans-serif',
      fontSize:17,fontWeight:700,textAlign:'center',lineHeight:1.3}}>
      QA PENDENTE — {shot.continuity_gate.qa_notice}
    </div>}
    <div style={{position:'absolute',bottom:10,left:10,right:10,padding:7,background:'#000b',color:'white',fontFamily:'sans-serif',fontSize:13,textAlign:'center'}}>
      {shot.id} · PRÉVIA TÉCNICA · CÂMERA 2D / SEM RIG<br/>
      {shot.approval_status==='diagnostic_only_contact_rejected'?'CONTATO REJEITADO — SOMENTE DIAGNÓSTICO':shot.approval_status==='exact_sha_approval_record_exists'?'FONTE APROVADA · MOVIMENTO EM REVISÃO':'ARTE E MOVIMENTO EM REVISÃO'}
    </div>
  </AbsoluteFill>;
};

export const CameraBatch:React.FC<Props> = (props) => {
  if (props.schema!=='videoforge/ep01-camera-batch/v1' || !props.technical_preview_only || props.official_episode_approved || props.youtube_upload || props.image_provider_calls!==0) throw new Error('Preview gates violated');
  if (!props.shots.length || props.shots.reduce((n,s)=>n+s.duration_frames,0)!==props.durationFrames) throw new Error('Invalid timeline');
  let offset=0;
  return <AbsoluteFill style={{backgroundColor:'black'}}>{props.shots.map(shot=>{
    const from=offset; offset+=shot.duration_frames;
    return <Sequence key={shot.id} from={from} durationInFrames={shot.duration_frames}><Picture shot={shot}/></Sequence>;
  })}</AbsoluteFill>;
};

const defaults:Props={schema:'videoforge/ep01-camera-batch/v1',technical_preview_only:true,official_episode_approved:false,youtube_upload:false,image_provider_calls:0,durationFrames:1,shots:[]};
const Root:React.FC=()=> <Composition id="EP01CameraBatch" component={CameraBatch} width={540} height={960} fps={30} durationInFrames={1}
  defaultProps={defaults} calculateMetadata={({props})=>({durationInFrames:props.durationFrames})}/>;
registerRoot(Root);
