/**
 * Animador Remotion - VideoForge IA.
 *
 * Reutiliza o motor autoral do AutoEditorVideo (Remotion 4):
 * characterPoseAtFrame, motionAtFrame, videoForgeMotionAtFrame.
 * Somente imagens RGBA existentes, verificadas pelo Python.
 *
 * Modo legado: personagem inteiro, sem sobrepor capa duplicada.
 * Modo rig opcional: sprites sem duplicacao, cabeca/piscada e capa em malha SVG.
 */
import React from 'react';
import {AbsoluteFill,Audio,Img,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {characterPoseAtFrame,CharacterPreset} from './character-idle';
import {motionAtFrame} from './cinematic-motion';
import {videoForgeMotionAtFrame} from './videoforge-motion';
import {RiggedCharacter,RigManifest} from './mesh-rig';

export type LayerSceneProps={
  id:string;
  scene:string;
  durationFrames:number;
  preset:CharacterPreset;
  background:string;
  character:string;
  foreground?:string;
  silence:string;
  layerSourceHash:string;
  /** Ativado somente com sprites RGBA verificados, sem partes duplicadas. */
  rig?:RigManifest|null;
  /** Marca d'agua obrigatoria para visualizacao de candidato NAO aprovado. */
  draftPreview?:boolean;
};

const imgStyle:React.CSSProperties={
  position:'absolute',inset:0,width:'100%',height:'100%',
  objectFit:'contain',userSelect:'none',pointerEvents:'none',
};

export const VideoForgeLayerScene:React.FC<LayerSceneProps>=({
  id,scene,durationFrames,preset,background,character,foreground,silence,rig,draftPreview,
})=>{
  const frame=useCurrentFrame();
  const {fps}=useVideoConfig();
  const camera=motionAtFrame(frame,0,durationFrames,'establish',id,'cinematica');
  const characterPose=characterPoseAtFrame({
    role:'front_character',id:id,coverage:0.3815,
    contactRisk:.12,heroRisk:0,heightFraction:.72,
    frame,sceneStart:0,sceneEnd:durationFrames,fps,preset,enabled:true,
  });
  // A engine anterior aplica cues deterministas por frame a cada PNG.
  const roofMotion=videoForgeMotionAtFrame(
    [{id:'foreground-roof',motion:'idle',start:0.04,end:.96,distance:16}],
    frame,0,durationFrames
  );
  // Camera condividida para composicao, movimento proprio para personagem
  // e primeiro plano. Nada de Math.random ou sprites substitutos.
  const cameraTransform='translate('+
    camera.panX.toFixed(3)+'px,'+camera.panY.toFixed(3)+
    'px) scale('+camera.zoom.toFixed(5)+')';
  const characterTransform='translate('+
    characterPose.translateX.toFixed(3)+'px,'+
    characterPose.translateY.toFixed(3)+'px) rotate('+
    characterPose.rotateDeg.toFixed(4)+'deg)';
  const cameraGlow=Math.max(0,Math.min(.045,camera.fill));
  return <AbsoluteFill style={{overflow:'hidden',backgroundColor:'#100e1c'}}>
    {/* A imagem 2:3 permanece completa, com extensão desfocada apenas
        nas margens da tela Shorts 9:16. Sem crop do rosto. */}
    <Img src={staticFile(background)} style={{
      position:'absolute',inset:0,width:'100%',height:'100%',
      objectFit:'cover',filter:'blur(38px) brightness(.52)',
      transform:'scale(1.16)',
    }}/>
    <div style={{
      position:'absolute',inset:0,width:'100%',height:'100%',
      overflow:'hidden',transform:cameraTransform,transformOrigin:'50% 50%',
    }}>
      <Img src={staticFile(background)} style={{
        ...imgStyle,zIndex:0,
      }}/>
      {rig ? <RiggedCharacter rig={rig} frame={frame} fps={fps}
        duration={durationFrames}/> : <Img src={staticFile(character)} style={{
        ...imgStyle,zIndex:20,transform:characterTransform,
        transformOrigin:'50% 85%',
      }}/>}
      {foreground && <Img src={staticFile(foreground)} style={{
        ...imgStyle,zIndex:50,
        transform:roofMotion.transform,
        transformOrigin:'50% 90%',
        opacity:roofMotion.opacity,
      }}/>}
    </div>
    <AbsoluteFill style={{
      zIndex:90,pointerEvents:'none',opacity:cameraGlow,
      background:'linear-gradient(145deg,rgba(255,182,109,.26),transparent 70%)',
    }}/>
    {/* Trilha vinculada ao manifesto: silencio tecnico OU narracao real revisavel. */}
    <Audio src={staticFile(silence)} />
    {draftPreview && <div style={{
      position:'absolute',zIndex:110,left:25,right:25,top:46,
      borderRadius:16,textAlign:'center',fontFamily:'sans-serif',
      fontSize:30,fontWeight:800,letterSpacing:1.5,
      color:'#fff',background:'rgba(95,13,13,.83)',padding:'20px 10px',
      textShadow:'0 2px 2px rgba(0,0,0,.8)',
      pointerEvents:'none',
    }}>RASCUNHO — RIG ARTICULADO PENDENTE</div>}
  </AbsoluteFill>;
};
