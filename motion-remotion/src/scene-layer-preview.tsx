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
import {RiggedCharacter,RigManifest,blinkClosureAtFrame} from './mesh-rig';
import {blinkNeutralWeightAtFrame,synchronizedPoseAtFrame,subtleHeadPoseAtFrame} from './blink-motion-sync';

export type LayerSceneProps={
  id:string;
  scene:string;
  durationFrames:number;
  preset:CharacterPreset;
  background:string;
  character:string;
  foreground?:string|null;
  /** Somente sprite RGBA de PALPEBRAS FECHADAS vindo da mesma cena-mae. */
  /** Nova piscada: segunda versao da imagem COMPLETA do mesmo personagem. */
  characterEyesClosed?:string|null;
  eyesClosed?:string|null;
  /** Franja derivada do personagem ORIGINAL, sobreposta DEPOIS da piscada. */
  hairForeground?:string|null;
  /** Centros de piscada em quadros, sem tocar na opacidade do rosto. */
  blinkFrames?:number[];
  /** Somente objetos extraidos e com remocao da base comprovada. */
  animatedObjects?:Array<{src:string;approvedNoDuplicate:boolean;attachedToCharacter?:boolean}>;
  /** Opt-in: requires genuine RGBA body with NO head and separate open/closed heads. */
  articulatedHead?:{
    bodyNoHead:string;headOpen:string;headClosed:string;
    neckPivot:{x:number;y:number};sourceMatched:boolean;
  }|null;
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
  id,scene,durationFrames,preset,background,character,foreground,
  characterEyesClosed,eyesClosed,hairForeground,blinkFrames,animatedObjects,
  articulatedHead,silence,rig,draftPreview,
})=>{
  const frame=useCurrentFrame();
  const {fps}=useVideoConfig();
  const camera=motionAtFrame(frame,0,durationFrames,'establish',id,'cinematica');
  const centers=blinkFrames??[Math.round(fps*2.8),Math.round(fps*6.0)];
  // Neutralize gradually BEFORE the image swap, never snap at the swap frame.
  // All attached character parts share this neutral frame and the same pivot.
  const neutral=blinkNeutralWeightAtFrame(frame,
    characterEyesClosed||articulatedHead ? centers : []);
  const cameraTransform='translate('+(camera.panX*.30*neutral).toFixed(3)+'px,'+
    (camera.panY*.25*neutral).toFixed(3)+'px) scale('+
    (1+(camera.zoom-1)*.30*neutral).toFixed(5)+')';
  const characterPose=characterPoseAtFrame({
    role:'front_character',id:id,coverage:0.3815,
    contactRisk:.12,heroRisk:0,heightFraction:.72,
    frame,sceneStart:0,sceneEnd:durationFrames,fps,preset,enabled:true,
  });
  // A engine anterior aplica cues deterministas por frame a cada PNG.
  const roofMotion=videoForgeMotionAtFrame(
    [{id:'foreground-real',motion:'idle',start:0.04,end:.96,distance:1.5}],
    frame,0,durationFrames
  );
  // Camera condividida para composicao, movimento proprio para personagem
  // e primeiro plano. Nada de Math.random ou sprites substitutos.
  const syncedPose=synchronizedPoseAtFrame(characterPose,frame,
    characterEyesClosed||articulatedHead ? centers : []);
  const characterTransform='translate('+
    syncedPose.translateX.toFixed(3)+'px,'+
    syncedPose.translateY.toFixed(3)+'px) rotate('+
    syncedPose.rotateDeg.toFixed(4)+'deg)';
  // Nada de opacidade no rosto. A camada de olhos FECHADOS e sobreposta
  // apenas por 3-5 frames, nunca usada em crossfade com a face-base.
  if(characterEyesClosed && (eyesClosed || hairForeground || rig || articulatedHead)){
    throw new Error('BLINK_CANNOT_MIX_FULL_CHARACTER_SWAP_WITH_EYELID_OVERLAYS');
  }
  if(eyesClosed && !rig && !hairForeground){
    throw new Error('BLINK_REQUIRES_HAIR_FOREGROUND_TO_AVOID_BANGS_OVERPAINT');
  }
  if(articulatedHead && (rig || eyesClosed || hairForeground || !articulatedHead.sourceMatched)){
    throw new Error('ARTICULATED_HEAD_REQUIRES_SEPARATE_VERIFIED_PARTS');
  }
  const blink=eyesClosed ? blinkClosureAtFrame(frame,centers) : 0;
  // Faz troca de frame, nao sobrepoe uma faixa de pele nos fios da franja.
  // O PNG fechado tem exatos mesmos pixels da base fora dos olhos.
  const showFullClosed=Boolean((characterEyesClosed || articulatedHead) && !rig &&
    centers.some(center=>Math.abs(frame-center)<=1));
  const headPose=subtleHeadPoseAtFrame(frame,fps,centers);
  const headTransform='translate('+
    headPose.translateX.toFixed(3)+'px,'+
    headPose.translateY.toFixed(3)+'px) rotate('+
    headPose.rotateDeg.toFixed(4)+'deg)';
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
        duration={durationFrames}/> : articulatedHead ? <div style={{
          position:'absolute',inset:0,zIndex:20,
          transform:characterTransform,transformOrigin:'50% 85%',
        }}>
          <Img src={staticFile(articulatedHead.bodyNoHead)} style={imgStyle}/>
          <Img src={staticFile(showFullClosed ? articulatedHead.headClosed : articulatedHead.headOpen)} style={{
            ...imgStyle,transform:headTransform,
            transformOrigin:(articulatedHead.neckPivot.x/1024*100).toFixed(4)+'% '+
              (articulatedHead.neckPivot.y/1536*100).toFixed(4)+'%',
          }}/>
        </div> : <Img src={staticFile(showFullClosed ? characterEyesClosed! : character)} style={{
        ...imgStyle,zIndex:20,transform:characterTransform,
        transformOrigin:'50% 85%',
      }/>}
      {eyesClosed && !rig && blink>0 && <Img src={staticFile(eyesClosed)} style={{
        ...imgStyle,zIndex:25,
        transform:characterTransform,transformOrigin:'50% 85%',
        opacity:blink,
      }}/>} 
      {/* Render order: base person -> eyelids -> ORIGINAL hair strands.
          Same pivot avoids drifting seams; independent hair motion requires an underlay. */}
      {hairForeground && !rig && <Img src={staticFile(hairForeground)} style={{
        ...imgStyle,zIndex:30,transform:characterTransform,
        transformOrigin:'50% 85%',
      }}/>} 
      {(animatedObjects??[]).filter(x=>x.approvedNoDuplicate).map((obj,i)=><Img
        key={i} src={staticFile(obj.src)} style={{
          ...imgStyle,zIndex:40+i,
          transform:obj.attachedToCharacter?characterTransform:roofMotion.transform,
          transformOrigin:obj.attachedToCharacter?'50% 85%':'50% 90%',
        }}/>) }
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
