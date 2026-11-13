/**
 * Rig 2D deterministico para sprites RGBA em coordenadas da cena original.
 * Sem WebGL, timers, random, interpolacao por tempo real ou dependencias extras.
 * SVG aplica transformacao afim a cada triangulo da malha da capa (warp real).
 *
 * IMPORTANTE: body nao contem cabeca/capa; head nao contem olhos.
 * So ativar depois de revisar recortes e partes reconstruidas.
 */
import React, {useId} from 'react';
import {Img,staticFile} from 'remotion';

export type Point={x:number;y:number};
export type CapeBounds={x:number;y:number;width:number;height:number};
/** Parametros fisicamente plausiveis em unidades de malha, nao pixels de tela. */
export type CapeWind={
  direction:-1|1;
  baseStrength:number;
  gustStrength:number;
  flutterStrength:number;
  tipLagSeconds:number;
  liftStrength:number;
};
export type RigManifest={
  schema:'videoforge/mesh-rig/v1';
  canvas:{width:number;height:number};
  layers:{body:string;head:string;eyesOpen:string;eyesClosed:string;cape:string;capeFront?:string;headOpen?:string;headClosed?:string;seamUnderlay?:string};
  neckPivot:Point;
  headMaxDeg:number;
  blinkFrames:number[];
  capeMesh:{bounds:CapeBounds;columns:number;rows:number;amplitudePx:number;wind?:CapeWind};
};
export type Triangle={
  source:[Point,Point,Point];
  destination:[Point,Point,Point];
  /** SVG matrix(a b c d e f) mapeando coordenadas de origem para destino. */
  matrix:[number,number,number,number,number,number];
};
const clamp=(v:number,lo:number,hi:number)=>Math.max(lo,Math.min(hi,v));
const smooth=(v:number)=>{const t=clamp(v,0,1);return t*t*(3-2*t);};
const envelope=(frame:number,duration:number)=>{
  if(duration<=1||frame<=0||frame>=duration-1)return 0;
  const t=frame/(duration-1);
  return smooth(t/.10)*smooth((1-t)/.10);
};

/** Angulo discreto em graus, pivot fixo no pescoco. */
export const headAngleAtFrame=(frame:number,fps:number,duration:number,maxDeg:number):number=>{
  if(fps<=0||duration<=1)return 0;
  return maxDeg*Math.sin(2*Math.PI*.23*frame/fps)*envelope(frame,duration);
};

/** Piscar: olhos fechados nos quadros centro-1, centro e centro+1. */
/** A cabeca aberta e sempre base solida; a fechada nunca substitui sua opacidade. */
export const headOpacitiesAtFrame=(frame:number,centers:readonly number[])=>({
  open:1,
  closed:blinkClosureAtFrame(frame,centers),
});

export const blinkClosureAtFrame=(frame:number,centers:readonly number[]):number=>{
  let closure=0;
  for(const center of centers){
    const distance=Math.abs(frame-center);
    if(distance<=1)closure=1;
    else if(distance<=2)closure=Math.max(closure,.5);
  }
  return closure;
};

export const affineFromTriangles=(
  source:[Point,Point,Point],destination:[Point,Point,Point]
):Triangle['matrix']=>{
  const [s0,s1,s2]=source;
  const [d0,d1,d2]=destination;
  const sx1=s1.x-s0.x,sy1=s1.y-s0.y,sx2=s2.x-s0.x,sy2=s2.y-s0.y;
  const det=sx1*sy2-sx2*sy1;
  if(Math.abs(det)<1e-8)throw new Error('RIG_DEGENERATE_TRIANGLE');
  const dx1=d1.x-d0.x,dy1=d1.y-d0.y,dx2=d2.x-d0.x,dy2=d2.y-d0.y;
  const a=(dx1*sy2-dx2*sy1)/det;
  const b=(dy1*sy2-dy2*sy1)/det;
  const c=(sx1*dx2-sx2*dx1)/det;
  const d=(sx1*dy2-sx2*dy1)/det;
  return [a,b,c,d,d0.x-a*s0.x-c*s0.y,d0.y-b*s0.x-d*s0.y];
};

/**
 * Pseudotecido 2D: vento deterministico com rajadas nao uniformes.
 *
 * - costura do ombro inteiramente fixa (v=0)
 * - atraso progressivo do meio/ponta (v=0..1)
 * - velocidade de onda e flutter diferentes; sem loop repetido mecanicamente
 * - pequenas rajadas em tempos relativos ao clipe, com ataque/cauda suaves
 * - camada frontal responde menos, preservando sobreposicao no peito
 * Nao e uma simulacao fisica de colisao de tecido nem IK.
 */
const gustPulse=(time:number,center:number,attack:number,decay:number):number=>{
  if(time<=center-attack||time>=center+decay)return 0;
  return smooth((time-center+attack)/attack)*
    smooth((center+decay-time)/decay);
};
export const windEnergyAtTime=(time:number,durationSeconds:number,wind:CapeWind):number=>{
  const base=wind.baseStrength*(
    .52+.14*Math.sin(2*Math.PI*.17*time+.45)+
    .09*Math.sin(2*Math.PI*.37*time+1.35)
  );
  const gust=wind.gustStrength*(
    .90*gustPulse(time,durationSeconds*.23,.40,.95)+
    .62*gustPulse(time,durationSeconds*.53,.32,.75)+
    1.08*gustPulse(time,durationSeconds*.79,.38,.85)
  );
  return Math.max(0,base+gust);
};
export const capeVertexAtFrame=(args:{
  x:number;y:number;frame:number;fps:number;duration:number;
  bounds:CapeBounds;amplitudePx:number;
  wind?:CapeWind;layer?:'cape'|'capeFront';
}):Point=>{
  const {x,y,frame,fps,duration,bounds,amplitudePx,wind,layer='cape'}=args;
  if(fps<=0)return {x,y};
  const u=clamp((x-bounds.x)/bounds.width,0,1);
  const v=clamp((y-bounds.y)/bounds.height,0,1);
  const t=frame/fps;
  if(!wind){
    // Compativel com renders anteriores: comportamento exatamente igual.
    const strength=Math.pow(v,1.65)*envelope(frame,duration);
    const wave=Math.sin(2*Math.PI*.42*t-1.9*v+1.3*u)-
      Math.sin(-1.9*v+1.3*u);
    const vertical=Math.sin(2*Math.PI*.31*t+1.4*u-v)-
      Math.sin(1.4*u-v);
    return {
      x:x+amplitudePx*strength*(.75+.25*u)*wave*.5,
      y:y+amplitudePx*strength*.22*vertical,
    };
  }
  if(v===0)return {x,y}; // vertice de costura nunca desloca
  // O broche/peito nao deve se soltar: animar so a barra livre da capa frontal.
  const frontPin=layer==='capeFront' ? smooth((v-.30)/.30) : 1;
  const layerStrength=(layer==='capeFront'?.64:1)*frontPin;
  const layerDelay=layer==='capeFront'?.085:0;
  const lag=wind.tipLagSeconds*Math.pow(v,1.1)+layerDelay;
  const localTime=t-lag;
  const durationSeconds=duration/fps;
  const energy=windEnergyAtTime(localTime,durationSeconds,wind);
  const strength=Math.pow(v,1.38)*envelope(frame,duration)*layerStrength;
  const wavePhase=2*Math.PI*.64*localTime-2.8*v+1.6*u;
  const flutterPhase=2*Math.PI*1.21*localTime-5.3*v+2.2*u+.45;
  const slowBend=Math.sin(wavePhase);
  const ripple=Math.sin(flutterPhase);
  const sideways=amplitudePx*strength*(
    .85*energy+.55*slowBend+.38*wind.flutterStrength*ripple
  );
  const rise=amplitudePx*strength*(
    wind.liftStrength*(.30*energy+.23*Math.max(0,slowBend))-
    .14*wind.flutterStrength*ripple
  );
  return {
    x:x+wind.direction*sideways,
    y:y-rise,
  };
};

/** Triangulacao regular do retangulo da capa; apenas pixels RGBA da capa aparecem. */
export const capeMeshAtFrame=(rig:RigManifest,frame:number,fps:number,duration:number,layer:'cape'|'capeFront'='cape'):Triangle[]=>{
  const {bounds,columns,rows,amplitudePx}=rig.capeMesh;
  const at=(col:number,row:number):Point=>{
    const x=bounds.x+bounds.width*col/columns;
    const y=bounds.y+bounds.height*row/rows;
    return {x,y};
  };
  const tris:Triangle[]=[];
  const append=(p:[Point,Point,Point])=>{
    const dest=p.map(s=>capeVertexAtFrame({
      ...s,frame,fps,duration,bounds,amplitudePx,wind:rig.capeMesh.wind,layer,
    })) as [Point,Point,Point];
    tris.push({source:p,destination:dest,matrix:affineFromTriangles(p,dest)});
  };
  for(let row=0;row<rows;row++){
    for(let col=0;col<columns;col++){
      const tl=at(col,row),tr=at(col+1,row);
      const bl=at(col,row+1),br=at(col+1,row+1);
      append([tl,tr,br]);
      append([tl,br,bl]);
    }
  }
  return tris;
};

/** Sobrepoe 2 px nos clips de triangulos adjacentes para fechar
 * fendas de antialias do Chromium; a textura RGBA ainda limita a silhueta. */
export const expandedClip=(points:[Point,Point,Point],overlapPx=2.0):Point[]=>{
  const cx=(points[0].x+points[1].x+points[2].x)/3;
  const cy=(points[0].y+points[1].y+points[2].y)/3;
  return points.map(p=>{
    const dx=p.x-cx,dy=p.y-cy;
    const length=Math.hypot(dx,dy)||1;
    return {x:p.x+dx*overlapPx/length,y:p.y+dy*overlapPx/length};
  });
};

const pointText=(p:Point)=>`${p.x.toFixed(4)},${p.y.toFixed(4)}`;
const matrixText=(m:Triangle['matrix'])=>`matrix(${m.map(v=>v.toFixed(7)).join(' ')})`;

const WarpedCape:React.FC<{
  rig:RigManifest;frame:number;fps:number;duration:number;layer:'cape'|'capeFront';
}>=({rig,frame,fps,duration,layer})=>{
  const id=useId().replace(/:/g,'');
  const triangles=capeMeshAtFrame(rig,frame,fps,duration,layer);
  const {width,height}=rig.canvas;
  const source=staticFile(rig.layers[layer] ?? rig.layers.cape);
  return <g>
    <defs>
      <image id={`${id}-source`} href={source} x={0} y={0}
        width={width} height={height} preserveAspectRatio="none"/>
      {triangles.map((tri,i)=><clipPath key={i} id={`${id}-clip-${i}`}
        clipPathUnits="userSpaceOnUse">
        <polygon points={expandedClip(tri.destination).map(pointText).join(' ')}/>
      </clipPath>)}
    </defs>
    {triangles.map((tri,i)=><g key={i} clipPath={`url(#${id}-clip-${i})`}>
      <use href={`#${id}-source`} transform={matrixText(tri.matrix)}/>
    </g>)}
  </g>;
};

export const RiggedCharacter:React.FC<{
  rig:RigManifest;frame:number;fps:number;duration:number;
}>=({rig,frame,fps,duration})=>{
  const {width,height}=rig.canvas;
  const angle=headAngleAtFrame(frame,fps,duration,rig.headMaxDeg);
  const blink=headOpacitiesAtFrame(frame,rig.blinkFrames);
  const image=(path:string,opacity=1)=><image href={staticFile(path)}
    x={0} y={0} width={width} height={height} opacity={opacity}
    preserveAspectRatio="none"/>;
  return <>
    {/* Remotion espera o carregamento de todos os PNGs antes de capturar o frame.
        SVG <image>/<use> sozinho nao participa do delayRender do <Img>. */}
    {Object.values(rig.layers).map(path=><Img key={path} src={staticFile(path)}
      style={{position:'absolute',width:1,height:1,opacity:0,pointerEvents:'none'}}/>)}
    <svg aria-label="Personagem 2D com malha de capa"
    viewBox={`0 0 ${width} ${height}`}
    preserveAspectRatio="xMidYMid meet"
    style={{position:'absolute',inset:0,width:'100%',height:'100%',overflow:'visible',
      pointerEvents:'none',zIndex:20}}>
    {/* Protecao do pescoco/ombro: recorte ORIGINAL limitado a uma zona de costura.
        Fica ATRAS da malha e do corpo, sem cobrir olhos nem duplicar capa livre. */}
    {rig.layers.seamUnderlay ? image(rig.layers.seamUnderlay) : null}
    {/* Capa fica atras do torso. Nunca renderizar character-main inteiro neste modo. */}
    <WarpedCape rig={rig} frame={frame} fps={fps} duration={duration} layer="cape"/>
    {image(rig.layers.body)}
    {rig.layers.capeFront ? <WarpedCape rig={rig} frame={frame} fps={fps}
      duration={duration} layer="capeFront"/> : null}
    <g transform={`rotate(${angle.toFixed(5)} ${rig.neckPivot.x} ${rig.neckPivot.y})`}>
      {rig.layers.headOpen && rig.layers.headClosed ? <>
        {/* A imagem do OLHO FECHADO e uma edicao com referencia original.
            A cabeca inteira e igual fora dos dois pequenos masks. */}
        {/* A cabeca original e a base 100% presente em TODOS os quadros.
            So o desenho fechado entra como overlay; dois PNGs com opacity=.5
            resultavam em alpha .75 e deixavam o fundo atravessar o rosto. */}
        {image(rig.layers.headOpen)}
        {image(rig.layers.headClosed,blink.closed)}
      </> : rig.layers.headOpen ? <>
        {image(rig.layers.headOpen)}
        {image(rig.layers.head,blink.closed)}
        {image(rig.layers.eyesClosed,blink.closed)}
      </> : <>
        {image(rig.layers.head)}
        {image(rig.layers.eyesOpen,1-blink.closed)}
        {image(rig.layers.eyesClosed,blink.closed)}
      </>}
    </g>
    </svg>
  </>;
};
