/**
 * VideoForge real-mesh math. No R3F lifecycle, wall clock, Math.random,
 * accumulated physics, or independent character-wide PNG bobbing.
 * All coordinates are measured in the original scene-mother canvas.
 */
import {blinkNeutralWeightAtFrame} from './blink-motion-sync';

export type Rect=[number,number,number,number];
export type Point={x:number;y:number};
export type MeshType='cape'|'hair-front'|'hair-front-left'|'hair-front-right'|'hair-back'|'cloth';
export type MeshSpec={columns:number;rows:number;pinnedRows:[0];amplitudePx:number};
export type LayerSpec={
  id:string;file:string;bbox:Rect;sha256:string;z:number;mesh?:MeshSpec;
};
export type ThreeRigManifest={
  schema:'videoforge/rig-three/v1';
  canvas:{width:number;height:number};
  sceneMotherSha256:string;
  layers:LayerSpec[];
  neckPivot:[number,number];
  headMaxRotationDeg:number;
  blinkFrames:number[];
  rigType:'independent-parts-and-deformable-mesh';
  technicalAssetsVerified:true;
  humanVisualReview:true;
  youtubeUploaded:false;
};

const clamp=(v:number,a:number,b:number)=>Math.max(a,Math.min(b,v));
const ease=(v:number)=>{const t=clamp(v,0,1);return t*t*(3-2*t);};
export const sceneEnvelope=(frame:number,duration:number):number=>{
  if(!Number.isFinite(frame)||!Number.isFinite(duration)||duration<=1)return 0;
  if(frame<=0||frame>=duration-1)return 0;
  const t=frame/(duration-1);
  return ease(t/.11)*ease((1-t)/.11);
};
export const sharedNeutralEnvelope=(
  frame:number,duration:number,centers:readonly number[]
):number=>sceneEnvelope(frame,duration)*blinkNeutralWeightAtFrame(frame,centers,3,12);

export const headRotationDegAtFrame=(
  frame:number,fps:number,duration:number,
  centers:readonly number[],maxDegrees=2
):number=>{
  if(!Number.isFinite(fps)||fps<=0||maxDegrees<0||maxDegrees>2)
    throw new Error('RIG_HEAD_MOTION_PARAMETERS_INVALID');
  const weight=sharedNeutralEnvelope(frame,duration,centers);
  if(weight===0)return 0;
  const t=frame/fps;
  const raw=.73*(Math.sin(t*.72)-Math.sin(0))+
    .27*(Math.sin(t*.31+1.1)-Math.sin(1.1));
  return clamp(maxDegrees*raw,-maxDegrees,maxDegrees)*weight;
};

export const bodyBreathAtFrame=(
  frame:number,fps:number,duration:number,centers:readonly number[]
):{scaleX:number;scaleY:number;translateY:number}=>{
  if(!Number.isFinite(fps)||fps<=0)throw new Error('RIG_BODY_FPS_INVALID');
  const neutral=sharedNeutralEnvelope(frame,duration,centers);
  if(neutral===0)return {scaleX:1,scaleY:1,translateY:0};
  const cyc=Math.sin(frame/fps*2*Math.PI*.21);
  return {
    scaleX:1+cyc*.0006*neutral,
    scaleY:1+cyc*.0008*neutral,
    translateY:cyc*.7*neutral,
  };
};

/** "Open / closed" means a complete edition of the SAME original head.
 * Never composite generated eyelids over hair. Each image shares neck pivot.
 */
export const isClosedAtFrame=(frame:number,centers:readonly number[]):boolean=>
  centers.some(c=>Math.abs(frame-c)<=1);

/**
 * Mesh point with physically anchored top vertices, gradual bending and a
 * deterministic follow-through; no stateful Verlet physics during rendering.
 */
export const meshVertexAtFrame=(args:{
  original:Point;
  uv:Point;
  kind:MeshType;
  amplitudePx:number;
  frame:number;fps:number;duration:number;
  blinkFrames:readonly number[];
}):Point=>{
  const {original,uv,kind,amplitudePx,frame,fps,duration,blinkFrames}=args;
  if(!Number.isFinite(fps)||fps<=0||amplitudePx<0||amplitudePx>12)
    throw new Error('RIG_MESH_PARAMETERS_INVALID');
  const v=clamp(uv.y,0,1),u=clamp(uv.x,0,1);
  if(v===0)return {...original}; // EXACT fixed seam, for every frame.
  const t=frame/fps;
  const pin=Math.pow(v,1.75)*sharedNeutralEnvelope(frame,duration,blinkFrames);
  const kindScale=kind.startsWith('hair')?.38:kind==='cloth'?.62:1;
  const delay=.24*v + (kind.startsWith('hair')?.11:0);
  const wave=Math.sin((t-delay)*1.92 -1.7*v +.65*u)-
    Math.sin(-delay*1.92 -1.7*v +.65*u);
  const detail=Math.sin((t-delay)*3.03 + .95*u -2.1*v)-
    Math.sin(-delay*3.03 + .95*u -2.1*v);
  const drift=Math.sin(t*.67-delay*.5)-Math.sin(-delay*.5);
  const dx=amplitudePx*kindScale*pin*(.53*wave+.22*detail+.18*drift);
  const dy=amplitudePx*kindScale*pin*.12*(
    Math.sin(t*1.30+.7*u-v)-Math.sin(.7*u-v)
  );
  return {x:original.x+dx,y:original.y+dy};
};

/** Deterministic triangles and UVs from the original art coordinates. */
export const meshGridAtFrame=(args:{
  bbox:Rect;canvas:{width:number;height:number};
  spec:MeshSpec;kind:MeshType;frame:number;fps:number;
  duration:number;blinkFrames:readonly number[];
})=>{
  const {bbox,canvas,spec,kind,frame,fps,duration,blinkFrames}=args;
  if(spec.columns<2||spec.rows<2||spec.pinnedRows.join(',')!=='0')
    throw new Error('RIG_MESH_NOT_SUBDIVIDED_OR_PINNED');
  const [bx,by,bw,bh]=bbox;
  const positions:number[]=[];
  const uvs:number[]=[];
  const indices:number[]=[];
  for(let row=0;row<=spec.rows;row++){
    for(let col=0;col<=spec.columns;col++){
      const u=col/spec.columns,v=row/spec.rows;
      const original={x:bx+bw*u,y:by+bh*v};
      const p=meshVertexAtFrame({original,uv:{x:u,y:v},kind,
        amplitudePx:spec.amplitudePx,frame,fps,duration,blinkFrames});
      positions.push(p.x-canvas.width/2,canvas.height/2-p.y,0);
      // PNGs in rig-three are cropped to bbox (not full-canvas PNGs).
      // Geometry is positioned in original canvas coordinates, but UV stays
      // local to that individual crop to avoid texture distortion.
      uvs.push(u,1-v);
    }
  }
  for(let row=0;row<spec.rows;row++){
    for(let col=0;col<spec.columns;col++){
      const a=row*(spec.columns+1)+col;
      const b=a+1,c=a+spec.columns+1,d=c+1;
      indices.push(a,c,b,b,c,d);
    }
  }
  return {positions,uvs,indices};
};
