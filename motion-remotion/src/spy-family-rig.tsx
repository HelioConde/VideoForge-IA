/**
 * SPY x FAMILY — animatico 2D original em SVG (nao sao artes finais licenciadas).
 *
 * Mesmos principios validados no piloto Otaku BR: torso e roupa em camadas,
 * cabeca/pele SEMPRE opacas, olhos somente trocam formas, cabelo unido pela raiz,
 * sobras de tecido abaixo da frente para impedir frestas, movimentos presos
 * aos ombros e determinismo por frame sem Math.random/timers.
 */
import React from 'react';
import {AbsoluteFill,useCurrentFrame,useVideoConfig} from 'remotion';
import {characterPoseAtFrame} from './character-idle';
import {motionAtFrame} from './cinematic-motion';
import {blinkClosureAtFrame,headAngleAtFrame,windEnergyAtTime,CapeWind} from './mesh-rig';

export type SpySceneProps={
  id:string;
  card:string;
  focus:'anya'|'loid'|'yor'|'family';
  setting:'home'|'academy'|'office';
  durationFrames:number;
  draftPreview:boolean;
};
const wind:CapeWind={
  direction:1,baseStrength:.70,gustStrength:.80,flutterStrength:.55,
  tipLagSeconds:.26,liftStrength:.55,
};
export const sceneFocus=(id:string):SpySceneProps['focus']=>{
  if(/yor/.test(id))return 'yor';
  if(/loid|operacao|academia|damian/.test(id))return 'loid';
  if(/anya|telepatia|poder|adocao|escolha/.test(id))return 'anya';
  return 'family';
};
export const sceneSetting=(id:string):SpySceneProps['setting']=>{
  if(/academia|damian|adocao/.test(id))return 'academy';
  if(/operacao|identidade/.test(id))return 'office';
  return 'home';
};
export const blinkGeometry=(frame:number)=>{
  const closure=blinkClosureAtFrame(frame,[35,91]);
  return {open:1-closure,closed:closure,headOpacity:1};
};
export const coatSway=(frame:number,fps:number,duration:number,front=false)=>{
  const v=Math.sin(Math.PI*Math.min(1,Math.max(0,frame/(duration-1))));
  const e=v*v;
  const power=windEnergyAtTime(frame/fps,duration/fps,wind);
  // Front sempre acompanha o peito; cauda se move com atraso e amplitude menor.
  return e*(front?2.5:5.3)*Math.sin(frame/fps*3.4+(front?.1:.7))*(.45+power*.2);
};
const Eyes:React.FC<{frame:number,color?:string}>=({frame,color='#202934'})=>{
  const b=blinkGeometry(frame);
  return <g fill={color}>
    <g opacity={b.open}>
      <ellipse cx="-16" cy="100" rx="6.1" ry="8.2"/>
      <ellipse cx="16" cy="100" rx="6.1" ry="8.2"/>
      <circle cx="-18" cy="97" r="1.8" fill="white"/>
      <circle cx="14" cy="97" r="1.8" fill="white"/>
    </g>
    <g opacity={b.closed} stroke={color} strokeWidth="3.4" strokeLinecap="round">
      <path d="M-24 100 Q-16 105 -8 100 M8 100 Q16 105 24 100" fill="none"/>
    </g>
  </g>;
};
type Person='loid'|'yor'|'anya';
const animeFeatures:Record<Person,{shirt:string;hair:string;skin:string}>={
  loid:{shirt:'#557b6d',hair:'#e7cf83',skin:'#f0c4a6'},
  yor:{shirt:'#352a46',hair:'#211e33',skin:'#f1c6b0'},
  anya:{shirt:'#212e3e',hair:'#eaa4ca',skin:'#f5c7b4'},
};
const PersonFigure:React.FC<{who:Person;x:number;y:number;scale:number;frame:number;fps:number;duration:number;dimmed?:boolean}>=
  ({who,x,y,scale,frame,fps,duration,dimmed})=>{
    const c=animeFeatures[who];
    const pose=characterPoseAtFrame({
      role:'front_character',id:who,coverage:.18,contactRisk:.07,heroRisk:0,
      heightFraction:.42,frame,sceneStart:0,sceneEnd:duration-1,fps,
      preset:'equilibrado',enabled:true,
    });
    const head=headAngleAtFrame(frame,fps,duration,who==='anya'?.8:1.15);
    const flutter=coatSway(frame,fps,duration,false);
    const secondary=coatSway(frame,fps,duration,true);
    const hairMove=coatSway(frame,fps,duration,true)*.38;
    return <g transform={'translate('+x+' '+y+') scale('+scale+')'}
      opacity={dimmed?0.58:1}>
      {/* Corpo e abrigo visual sempre presentes: recorte sobrepoe o tecido
          original do ombro. Nenhum fundo pode aparecer em frestas. */}
      <g transform={'translate('+pose.translateX.toFixed(2)+' '+pose.translateY.toFixed(2)+
        ') rotate('+pose.rotateDeg.toFixed(3)+' 0 230)'}>
        <ellipse cx="0" cy="395" rx="107" ry="19" fill="rgba(22,20,36,.2)"/>
        <path d="M-58 213 Q-100 220 -112 289 L-103 388 Q-80 408 -55 382
                 L0 335 L51 388 Q83 410 111 386 L107 280 Q95 218 53 213Z"
          fill={c.shirt} stroke="#212735" strokeWidth="4"/>
        {/* Do tecido traseiro para frente: nenhuma borda e um recorte
            complementar exato. A sobreposicao permanece sob o peito. */}
        <g transform={'rotate('+flutter.toFixed(2)+' -58 217)'}>
          <path d="M-63 220 Q-95 238 -102 301 L-116 388 Q-86 404 -67 375
                   L-54 238Z" fill={who==='yor'?'#432a48':'#345c55'}
            stroke="#27323d" strokeWidth="3"/>
          <path d="M-63 223 L-66 367 Q-90 391 -104 387 L-96 328 Q-86 270 -63 223"
            fill="#5b786c" opacity=".25"/>
        </g>
        <g transform={'rotate('+(-secondary).toFixed(2)+' 57 217)'}>
          <path d="M56 224 Q89 244 102 300 L114 383 Q90 399 65 371 L54 240Z"
            fill={who==='yor'?'#4f334d':who==='anya'?'#273f51':'#467263'}
            stroke="#27323d" strokeWidth="3"/>
        </g>
        {/* Camada frontal cobre JUNCOES e sobras das duas mangas. */}
        <path d="M-54 209 L-65 236 Q-48 278 -43 349 L43 349
                 Q49 270 64 238 L53 209Z" fill={c.shirt}
          stroke="#27323d" strokeWidth="3.5"/>
        {who==='loid' && <g>
          <path d="M-32 225 L0 286 L31 225 L9 219 L0 256 L-9 220Z" fill="#fbf4e1"/>
          <path d="M0 247 L-8 275 L0 308 L8 275Z" fill="#ba5056"/>
          <path d="M-58 220 L-28 272 L-2 225 M54 220 L28 271 L3 225"
            fill="none" stroke="#b9cebe" strokeWidth="5"/>
        </g>}
        {who==='yor' && <g>
          <path d="M-25 214 Q0 250 25 214 L15 262 L-16 262Z" fill="#eee5dd"/>
          <path d="M-20 252 L0 273 L20 252" stroke="#ad5366" fill="none" strokeWidth="7"/>
          <circle cx="0" cy="288" r="5" fill="#b8ac8b"/>
          <circle cx="0" cy="325" r="5" fill="#b8ac8b"/>
        </g>}
        {who==='anya' && <g>
          <path d="M-25 220 L0 252 L25 220" fill="#faf4ea" stroke="#e0c5ab" strokeWidth="4"/>
          <path d="M-22 232 L0 246 L22 232" fill="none" stroke="#e2ba60" strokeWidth="6"/>
          <circle cx="0" cy="290" r="5" fill="#e4ce88"/>
        </g>}
        {/* Pescoço e cabeca como forma SOLIDA independente da piscada. */}
        <rect x="-18" y="170" width="36" height="58" rx="15"
          fill={c.skin} stroke="#c79580" strokeWidth="3"/>
        <g transform={'rotate('+head.toFixed(2)+' 0 190)'}>
          {who==='yor' && <g>
            <path d="M-67 64 Q-91 142 -69 249 L-52 255 L-38 163Z" fill={c.hair}/>
            <path d="M60 63 Q81 147 68 246 L52 260 L36 166Z" fill={c.hair}/>
          </g>}
          <path d="M-54 79 Q-54 28 0 28 Q54 28 54 79 L51 145
                   Q39 182 0 190 Q-42 179 -51 145Z"
            fill={c.skin} stroke="#b9897b" strokeWidth="3.3"/>
          <ellipse cx="-55" cy="117" rx="9" ry="17" fill={c.skin}/>
          <ellipse cx="55" cy="117" rx="9" ry="17" fill={c.skin}/>
          {who==='loid' && <g fill={c.hair} stroke="#96794b" strokeWidth="2.4">
            <path d="M-61 95 L-65 46 L-48 21 L-39 35 L-29 10 L-12 29
                     L8 6 L18 27 L42 12 L42 38 L62 46 L50 98
                     Q41 73 26 72 Q1 84 -18 62 Q-36 92 -61 95Z"/>
            <path d="M-38 42 L-20 85 L-3 49 M14 28 L20 72 L39 47"
              fill="none" stroke="#f9e3ab" strokeWidth="4"/>
          </g>}
          {who==='yor' && <g fill={c.hair} stroke="#13152a" strokeWidth="3">
            <path d="M-62 105 Q-75 22 -18 13 Q49 4 66 77 L53 112
                   L45 59 Q6 81 -18 51 Q-27 88 -62 105Z"/>
            <path d="M-47 40 Q-12 62 25 38" fill="none" stroke="#a75860" strokeWidth="8"/>
            <path d="M-21 18 Q-26 7 -36 12 M21 17 Q29 7 39 12"
              stroke="#c8787e" strokeWidth="4"/>
          </g>}
          {who==='anya' && <g fill={c.hair} stroke="#ac729a" strokeWidth="2.8">
            <path d="M-61 114 Q-70 49 -44 26 Q0 -1 46 24 Q76 53 63 114
                     L47 82 Q20 92 10 70 L-5 90 L-24 72 L-50 100Z"/>
            <path d="M-38 48 Q-46 14 -68 12 L-75 55 L-48 68Z" fill="#22283a"/>
            <path d="M41 48 Q45 15 70 12 L78 55 L50 68Z" fill="#22283a"/>
            <path d="M-32 54 L-22 84 L-8 59 M12 51 L20 80 L32 59"
              fill="none" stroke="#f8c1d8" strokeWidth="5"/>
            {/* Raiz cobre a articulacao das pontas; somente a cauda se mexe */}
            <g transform={'rotate('+hairMove.toFixed(2)+' 45 112)'}>
              <path d="M48 102 L70 159 L59 183 L43 130Z"
                fill={c.hair} stroke="#ac729a" strokeWidth="2"/>
            </g>
          </g>}
          {/* olhos nunca removem a face: piscada muda SOMENTE os desenhos */}
          <Eyes frame={frame} color={who==='anya'?'#315d5c':'#30303a'}/>
          <path d="M-4 116 Q0 125 4 115" stroke="#b78380" strokeWidth="2" fill="none"/>
          <path d={who==='anya'?"M-9 143 Q0 154 9 143":"M-11 144 Q0 148 11 143"}
            fill="none" stroke="#b66b6a" strokeLinecap="round" strokeWidth="2.8"/>
          {who==='anya'&&<g fill="#e6a4a3" opacity=".60">
            <ellipse cx="-37" cy="134" rx="13" ry="6"/>
            <ellipse cx="37" cy="134" rx="13" ry="6"/>
          </g>}
        </g>
      </g>
    </g>;
  };
const Background:React.FC<{setting:SpySceneProps['setting'];frame:number}>=({setting,frame})=>{
  const shift=Math.sin(frame*.033)*3;
  if(setting==='academy')return <g>
    <rect width="540" height="960" fill="#ccc5b2"/>
    <rect y="0" width="540" height="480" fill="#8999aa"/>
    <path d="M0 485 L540 485 L540 960 L0 960" fill="#877f83"/>
    <path d="M0 780 L540 730 M0 910 L540 830" stroke="#ababb0" strokeWidth="13" opacity=".6"/>
    {[75,270,465].map((x,i)=><g key={i}>
      <path d={'M'+(x-70)+' 110 Q'+x+' 14 '+(x+70)+' 110 L'+(x+70)+' 420 L'+(x-70)+' 420Z'}
        fill="#435f73" stroke="#d8cab5" strokeWidth="15"/>
      <path d={'M'+x+' 50 L'+x+' 420'} stroke="#c5ced0" strokeWidth="6"/>
    </g>)}
    <rect y="445" width="540" height="50" fill="#ddc9a9"/>
    <text x="270" y="560" textAnchor="middle" fontSize="34" fill="#3f5369" fontWeight="bold">ACADEMIA</text>
  </g>;
  if(setting==='office')return <g>
    <rect width="540" height="960" fill="#202b3c"/>
    <rect y="0" width="540" height="580" fill="#30485a"/>
    <rect x="50" y="145" width="440" height="305" rx="15" fill="#d9cfae" stroke="#172c3c" strokeWidth="12"/>
    <path d="M80 255 Q210 195 300 290 T462 245 M80 365 L430 228"
      stroke="#ad9775" strokeWidth="6" fill="none" strokeDasharray="8 10"/>
    <circle cx="295" cy="280" r="28" fill="#bc5960" opacity=".6"/>
    <rect x="0" y="672" width="540" height="288" fill="#37445b"/>
    <rect x="0" y="652" width="540" height="33" fill="#c4ac7d"/>
  </g>;
  return <g>
    <rect width="540" height="960" fill="#d1bbaf"/>
    <rect y="0" width="540" height="615" fill="#c5d4cd"/>
    <rect x="55" y="108" width="190" height="280" rx="12" fill="#e9dfcb" stroke="#84797b" strokeWidth="13"/>
    <rect x="67" y="120" width="165" height="250" fill="#8facb4"/>
    <path d="M149 120 L149 370 M67 248 L232 248" stroke="#e2ddd5" strokeWidth="10"/>
    <path d={'M76 365 L'+(76+shift)+' 220 Q110 190 130 198 L129 378Z'} fill="#b77e85" opacity=".58"/>
    <path d={'M228 365 L'+(228-shift)+' 220 Q188 190 171 198 L169 378Z'} fill="#b77e85" opacity=".58"/>
    <rect x="286" y="195" width="203" height="145" rx="12" fill="#c3b89b" stroke="#877b72" strokeWidth="13"/>
    <path d="M295 315 L460 219 M340 340 L470 265" stroke="#a0b1aa" strokeWidth="10" opacity=".6"/>
    <rect x="24" y="575" width="495" height="230" rx="40" fill="#a98e85"/>
    <rect x="35" y="585" width="470" height="155" rx="24" fill="#ccb2a2"/>
    <path d="M0 785 L540 785 L540 960 L0 960" fill="#9e8376"/>
    <path d="M35 895 Q270 852 505 895" stroke="#c8b8ac" strokeWidth="10" fill="none"/>
  </g>;
};
export const SpyFamilyRigScene:React.FC<SpySceneProps>=({id,card,focus,setting,durationFrames,draftPreview})=>{
  const frame=useCurrentFrame();
  const {fps}=useVideoConfig();
  const camera=motionAtFrame(frame,0,durationFrames,'reaction',id,'cinematica');
  const figures:Person[]=focus==='family'?['loid','anya','yor']:
    focus==='anya'?['loid','yor','anya']:
    focus==='loid'?['anya','yor','loid']:['loid','anya','yor'];
  const role=figures.map(who=>{
    if(focus==='family')return {
      who,x:who==='loid'?129:who==='anya'?272:415,y:who==='anya'?417:305,
      scale:who==='anya'?.65:.73,dimmed:false
    };
    const isHero=who===focus;
    return {who,x:isHero?267:who==='loid'?95:who==='yor'?446:95,
      y:isHero?(who==='anya'?340:240):(who==='anya'?490:345),
      scale:isHero?(who==='anya'?.92:1.06):(who==='anya'?.47:.59),
      dimmed:!isHero};
  });
  return <AbsoluteFill style={{background:'#0d1727',overflow:'hidden',fontFamily:'DejaVu Sans, sans-serif'}}>
    <svg viewBox="0 0 540 960" width="100%" height="100%"
      preserveAspectRatio="xMidYMid slice">
      <defs>
        <linearGradient id="shade" x1="0" x2="1" y1="0" y2="1">
          <stop stopColor="#182c46"/><stop offset="1" stopColor="#1a132b"/>
        </linearGradient>
      </defs>
      <g transform={'translate('+camera.panX+' '+camera.panY+') scale('+camera.zoom+')'}>
        <Background setting={setting} frame={frame}/>
        <path d="M0 0 L540 0 L540 960 L0 960Z" fill="#161a2c" opacity=".10"/>
        {role.map(p=><PersonFigure key={p.who} {...p} frame={frame} fps={fps} duration={durationFrames}/>)}
        <rect x="0" y="715" width="540" height="245" fill="url(#shade)" opacity=".96"/>
        <rect x="26" y="734" width="490" height="3" fill="#d3a966"/>
        <text x="270" y="769" fontSize="17" textAnchor="middle" fontWeight="bold"
          fill="#d1b98f" letterSpacing="3">OTAKU MULTICENA • SPY x FAMILY</text>
        <foreignObject x="39" y="787" width="462" height="87">
          <div style={{
            color:'#fff6e6',textAlign:'center',fontWeight:800,
            fontSize:30,lineHeight:1.16,width:'100%',
            textShadow:'0 2px 3px #0008',
            overflowWrap:'break-word',
          }}>{card}</div>
        </foreignObject>
        <text x="270" y="920" fontSize="14" textAnchor="middle" fill="#d6c0a9">
          PRÉVIA VETORIAL 2D — ARTE DEFINITIVA PENDENTE
        </text>
      </g>
    </svg>
    {draftPreview && <div style={{position:'absolute',top:13,left:22,right:22,
      color:'#fff',fontSize:15,fontWeight:700,letterSpacing:2,
      background:'rgba(26,29,45,.72)',padding:8,textAlign:'center'}}>
        TESTE DE RIG • SEM PUBLICAÇÃO
      </div>}
  </AbsoluteFill>;
};
