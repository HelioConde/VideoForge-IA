/** Absolute-frame directed rigs. Draft only; never grants visual approval. */
import {meshGridAtFrame,type MeshType,type Rect} from './rig-three-math';

export type DirectedTransform='rotationZ'|'translateX'|'translateY'|'scaleX'|'scaleY';
export type DirectedKey={frame:number;value:number};
export type DirectedTrack={target:string;transform:DirectedTransform;unit:string;
  easing:'linear'|'easeInOutCubic';keyframes:DirectedKey[]};
export type DirectedNode={id:string;parent:string|null;pivot:[number,number];
  role:string;file?:string;bbox?:Rect;z:number;mesh?:{
    kind:Exclude<MeshType,'hand'>;columns:number;rows:number;pinnedRows:[0];amplitudePx:number;
    sourcePin?:{startY:number;endY:number};
    /** Explicit deformation of APPROVED upper-back cloth, not a new sprite. */
    backBreath?:{kind:'upper-back-source-mesh';
      sourceTopY:number;sourcePeakY:number;sourceBottomY:number;
      expansionPx:number;liftPx:number;
      driverTarget:string;driverTransform:'translateY';driverPeakAbsPx:number}}};
export type CameraKey={frame:number;z:number;lookAt:[number,number,number];fovDeg:number};
export type DirectedShot={id:string;startFrame:number;endFrameExclusive:number;
  canvas:{width:number;height:number};background:string|null;nodes:DirectedNode[];
  tracks:DirectedTrack[];camera:{type:'none'|'perspective_3d';move:string;keyframes:CameraKey[]}};
export type DirectedRigProps={schema:'videoforge/directed-rig-preview/v1';
  mode:'technical_draft';channel:string;videoId:string;id:string;
  width:number;height:number;fps:number;startFrame:number;durationFrames:number;
  shots:DirectedShot[];warnings:string[];humanVisualReview:false;publishable:false};

const fail=(reason:string):never=>{throw new Error('DIRECTED_RIG_'+reason);};
const finite=(n:unknown):n is number=>typeof n==='number'&&Number.isFinite(n);
const positiveInt=(n:unknown)=>finite(n)&&Number.isInteger(n)&&n>0;
const safeFile=(f:unknown)=>typeof f==='string'&&f.length>0&&
  !f.startsWith('/')&&!f.includes('\\')&&!f.includes(':')&&
  f.split('/').every(p=>p!=='.'&&p!=='..'&&p.length>0);
const meshKinds=new Set(['cape','cloth','hair-back','hair-front','hair-front-left','hair-front-right']);
const transforms=new Set(['rotationZ','translateX','translateY','scaleX','scaleY']);

export function validateDirectedProps(p:DirectedRigProps):void{
  if(!p||p.schema!=='videoforge/directed-rig-preview/v1'||p.mode!=='technical_draft'||
    p.humanVisualReview!==false||p.publishable!==false)fail('DRAFT_FLAGS_REQUIRED');
  if(![p.channel,p.videoId,p.id].every(x=>typeof x==='string'&&x.length>0)||
    ![p.width,p.height,p.fps,p.durationFrames].every(positiveInt)||
    !Number.isInteger(p.startFrame)||p.startFrame<0||!Array.isArray(p.warnings)||
    !p.warnings.every(x=>typeof x==='string'))fail('METADATA_INVALID');
  if(!Array.isArray(p.shots)||p.shots.length===0)fail('SHOTS_REQUIRED');
  const ids=new Set<string>();
  let previousEnd:number|undefined;
  for(const s of p.shots){
    if(!s||typeof s.id!=='string'||ids.has(s.id)||!Number.isInteger(s.startFrame)||
      s.startFrame<0||!Number.isInteger(s.endFrameExclusive)||s.endFrameExclusive<=s.startFrame||
      (previousEnd!==undefined&&s.startFrame!==previousEnd))fail('SHOT_BOUNDARIES_INVALID');
    ids.add(s.id);previousEnd=s.endFrameExclusive;
    if(!s.canvas||![s.canvas.width,s.canvas.height].every(positiveInt)||
      (s.background!==null&&!safeFile(s.background))||
      !Array.isArray(s.nodes)||!Array.isArray(s.tracks))fail('SHOT_CONTENT_INVALID');
    const nodes=new Map<string,DirectedNode>();
    for(const n of s.nodes){
      if(!n||typeof n.id!=='string'||!n.id||nodes.has(n.id)||
        !(n.parent===null||typeof n.parent==='string')||typeof n.role!=='string'||
        !Array.isArray(n.pivot)||n.pivot.length!==2||!n.pivot.every(finite)||!finite(n.z))fail('NODE_INVALID');
      if(n.file!==undefined&&(!safeFile(n.file)||!Array.isArray(n.bbox)||n.bbox.length!==4||
        !n.bbox.every(finite)||n.bbox[2]<=0||n.bbox[3]<=0||
        n.bbox[0]<0||n.bbox[1]<0||n.bbox[0]+n.bbox[2]>s.canvas.width||
        n.bbox[1]+n.bbox[3]>s.canvas.height))fail('SPRITE_INVALID');
      if(n.mesh&&(!n.file||!meshKinds.has(n.mesh.kind)||
        !positiveInt(n.mesh.columns)||n.mesh.columns<2||n.mesh.columns>16||
        !positiveInt(n.mesh.rows)||n.mesh.rows<2||n.mesh.rows>20||
        !Array.isArray(n.mesh.pinnedRows)||n.mesh.pinnedRows.length!==1||n.mesh.pinnedRows[0]!==0||
        !finite(n.mesh.amplitudePx)||n.mesh.amplitudePx<0||n.mesh.amplitudePx>12))fail('MESH_INVALID');
      const pin=n.mesh?.sourcePin;
      if(pin&&(!finite(pin.startY)||!finite(pin.endY)||pin.startY<0||
        pin.endY<=pin.startY||pin.endY>s.canvas.height))fail('SOURCE_PIN_INVALID');
      const back=n.mesh?.backBreath;
      if(back){
        if(s.id!=='C01-P03'||n.id!=='kael.jaqueta'||n.mesh?.kind!=='cloth'||
          n.parent!=='kael.ombros'||!n.bbox||!pin||
          back.kind!=='upper-back-source-mesh'||
          back.driverTarget!=='kael.ombros'||back.driverTransform!=='translateY'||
          ![back.sourceTopY,back.sourcePeakY,back.sourceBottomY,
            back.expansionPx,back.liftPx,back.driverPeakAbsPx].every(finite)||
          back.sourceTopY<n.bbox[1]||back.sourceTopY>=back.sourcePeakY||
          back.sourcePeakY>=back.sourceBottomY||
          back.sourceBottomY>=pin.startY||
          back.expansionPx<=0||back.expansionPx>1.5||
          back.liftPx<=0||back.liftPx>1||
          back.driverPeakAbsPx<=0||back.driverPeakAbsPx>2)
            fail('UPPER_BACK_BREATH_SOURCE_GEOMETRY_INVALID');
      }
      nodes.set(n.id,n);
    }
    for(const n of s.nodes){
      const visited=new Set([n.id]);let parent=n.parent;
      while(parent!==null){
        const ancestor=nodes.get(parent)??fail('PARENT_MISSING');
        if(visited.has(parent))fail('PARENT_CYCLE');
        visited.add(parent);parent=ancestor.parent;
      }
    }
    const used=new Set<string>();
    for(const t of s.tracks){
      const key=t.target+'/'+t.transform;
      if(!nodes.has(t.target)||!transforms.has(t.transform)||used.has(key)||
        !['linear','easeInOutCubic'].includes(t.easing)||
        t.unit!==(t.transform==='rotationZ'?'degrees':t.transform.startsWith('scale')?'ratio':'pixels_source_canvas')||
        !Array.isArray(t.keyframes)||t.keyframes.length===0)fail('TRACK_INVALID');
      used.add(key);
      let last=-Infinity;
      for(const k of t.keyframes){
        if(!Number.isInteger(k.frame)||k.frame<s.startFrame||k.frame>=s.endFrameExclusive||
          k.frame<=last||!finite(k.value)||
          (t.transform.startsWith('scale')&&k.value<0))fail('KEYFRAME_INVALID');
        last=k.frame;
      }
    }
    for(const n of s.nodes.filter(v=>v.mesh?.backBreath)){
      const breath=n.mesh!.backBreath!;
      if(s.tracks.filter(t=>t.target===breath.driverTarget&&
        t.transform===breath.driverTransform).length!==1 ||
        s.tracks.find(t=>t.target===breath.driverTarget&&
        t.transform===breath.driverTransform)!.keyframes.some(k=>
          k.value>0||k.value< -breath.driverPeakAbsPx))
          fail('UPPER_BACK_BREATH_DRIVER_TRACK_INVALID');
    }
    for(const n of s.nodes.filter(v=>v.mesh?.sourcePin)){
      let current:DirectedNode|undefined=n;
      while(current){
        if(s.tracks.some(t=>t.target===current!.id&&t.transform.startsWith('scale')&&
          t.keyframes.some(k=>k.value<=1e-6)))fail('SOURCE_PIN_SCALE_NOT_INVERTIBLE');
        current=current.parent===null?undefined:nodes.get(current.parent);
      }
    }
    if(!s.camera||!['none','perspective_3d'].includes(s.camera.type)||
      !Array.isArray(s.camera.keyframes)||
      (s.camera.type==='perspective_3d'&&s.camera.keyframes.length===0))fail('CAMERA_INVALID');
    let last=-Infinity;
    for(const k of s.camera.keyframes){
      if(!Number.isInteger(k.frame)||k.frame< s.startFrame||k.frame>=s.endFrameExclusive||k.frame<=last||
        !finite(k.z)||k.z<=0||!finite(k.fovDeg)||k.fovDeg<=0||k.fovDeg>=180||
        !Array.isArray(k.lookAt)||k.lookAt.length!==3||!k.lookAt.every(finite))fail('CAMERA_KEY_INVALID');
      last=k.frame;
    }
  }
  if(p.startFrame<p.shots[0].startFrame||
    p.startFrame+p.durationFrames>p.shots[p.shots.length-1].endFrameExclusive)fail('RENDER_RANGE_INVALID');
}

export function shotAtFrame(shots:DirectedShot[],frame:number):DirectedShot{
  const shot=shots.find(s=>frame>=s.startFrame&&frame<s.endFrameExclusive);
  return shot??fail('FRAME_OUTSIDE_SHOTS');
}
const clamp01=(v:number)=>Math.max(0,Math.min(1,v));
export function trackAtFrame(track:DirectedTrack,frame:number):number{
  const keys=track.keyframes;
  if(!keys.length||!finite(frame))return fail('TRACK_FRAME_INVALID');
  if(frame<=keys[0].frame)return keys[0].value;
  for(let i=1;i<keys.length;i++)if(frame<=keys[i].frame){
    const a=keys[i-1],b=keys[i];let t=clamp01((frame-a.frame)/(b.frame-a.frame));
    if(track.easing==='easeInOutCubic')t=t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
    return a.value+(b.value-a.value)*t;
  }
  return keys[keys.length-1].value;
}
export function nodeTransformAtFrame(shot:DirectedShot,id:string,frame:number){
  if(!shot.nodes.some(n=>n.id===id))return fail('TARGET_MISSING');
  const value={rotationZ:0,translateX:0,translateY:0,scaleX:1,scaleY:1};
  for(const track of shot.tracks)if(track.target===id)value[track.transform]=trackAtFrame(track,frame);
  return value;
}
/** Source coordinates remain y-down; Three flips y/rotation exactly once. */
export function transformSourcePoint(shot:DirectedShot,id:string,point:[number,number],frame:number):[number,number]{
  const n=shot.nodes.find(v=>v.id===id)??fail('TARGET_MISSING');
  const t=nodeTransformAtFrame(shot,id,frame),a=t.rotationZ*Math.PI/180;
  const x=(point[0]-n.pivot[0])*t.scaleX,y=(point[1]-n.pivot[1])*t.scaleY;
  const result:[number,number]=[n.pivot[0]+t.translateX+x*Math.cos(a)-y*Math.sin(a),
    n.pivot[1]+t.translateY+x*Math.sin(a)+y*Math.cos(a)];
  return n.parent===null?result:transformSourcePoint(shot,n.parent,result,frame);
}
/** Undo the actual hierarchy before Three reapplies it to a source-pinned mesh. */
export function inverseTransformSourcePoint(shot:DirectedShot,id:string,point:[number,number],frame:number):[number,number]{
  const n=shot.nodes.find(v=>v.id===id)??fail('TARGET_MISSING');
  const parentPoint=n.parent===null?point:inverseTransformSourcePoint(shot,n.parent,point,frame);
  const t=nodeTransformAtFrame(shot,id,frame),a=t.rotationZ*Math.PI/180;
  if(t.scaleX<=1e-6||t.scaleY<=1e-6)fail('SOURCE_PIN_SCALE_NOT_INVERTIBLE');
  const x=parentPoint[0]-n.pivot[0]-t.translateX,y=parentPoint[1]-n.pivot[1]-t.translateY;
  return [n.pivot[0]+(x*Math.cos(a)+y*Math.sin(a))/t.scaleX,
    n.pivot[1]+(-x*Math.sin(a)+y*Math.cos(a))/t.scaleY];
}
/** An independent, localized *mesh vertex* movement across Kael's back.
 * The jacket remains one source-derived RGBA part; arms/hand/boot NEVER inherit
 * these offsets. Center-back breath follows shoulder inspiration exactly.
 * All four boundaries are pinned to avoid tearing the collar, arm and waist.
 */
export function upperBackDeltaAtFrame(
  node:DirectedNode,shot:DirectedShot,sourceX:number,sourceY:number,
  frame:number
):[number,number]{
  const b=node.mesh?.backBreath;
  if(!b||!node.bbox)return [0,0];
  const driver=shot.tracks.find(t=>
    t.target===b.driverTarget&&t.transform===b.driverTransform);
  if(!driver)fail('UPPER_BACK_DRIVER_REQUIRED');
  const negativeLift=trackAtFrame(driver,frame);
  const breath=clamp01(-negativeLift/b.driverPeakAbsPx);
  if(breath===0||sourceY<=b.sourceTopY||sourceY>=b.sourceBottomY)return [0,0];
  const u=clamp01((sourceX-node.bbox[0])/node.bbox[2]);
  const v=sourceY<=b.sourcePeakY?
    clamp01((sourceY-b.sourceTopY)/(b.sourcePeakY-b.sourceTopY)):
    clamp01((b.sourceBottomY-sourceY)/(b.sourceBottomY-b.sourcePeakY));
  // Exact zero on outer edges, source neck line and pinned waist. The
  // horizontal radial expansion is opposite on the two back halves.
  const cross=4*u*(1-u),vertical=v*v*(3-2*v);
  const weight=cross*cross*vertical*breath;
  return [((u-.5)*2)*b.expansionPx*weight,-b.liftPx*weight];
}

export function directedMeshAtFrame(node:DirectedNode,shot:DirectedShot,frame:number,fps:number){
  if(!node.mesh||!node.bbox)return fail('MESH_REQUIRED');
  const grid=meshGridAtFrame({bbox:node.bbox,canvas:shot.canvas,spec:node.mesh,
    kind:node.mesh.kind,frame:frame-shot.startFrame,fps,
    duration:shot.endFrameExclusive-shot.startFrame,blinkFrames:[]});
  const pin=node.mesh.sourcePin;
  const [bx,by,bw,bh]=node.bbox;
  const {width,height}=shot.canvas;
  if(pin){
    for(let i=0;i<grid.positions.length;i+=3){
      const vertex=i/3,row=Math.floor(vertex/(node.mesh.columns+1)),col=vertex%(node.mesh.columns+1);
      const original:[number,number]=[bx+bw*col/node.mesh.columns,by+bh*row/node.mesh.rows];
      const t=clamp01((original[1]-pin.startY)/(pin.endY-pin.startY));
      if(t===0)continue;
      const weight=t*t*(3-2*t);
      const posed=transformSourcePoint(shot,node.id,
        [grid.positions[i]+width/2,height/2-grid.positions[i+1]],frame);
      const constrained:[number,number]=weight===1?original:
        [posed[0]+(original[0]-posed[0])*weight,posed[1]+(original[1]-posed[1])*weight];
      const local=inverseTransformSourcePoint(shot,node.id,constrained,frame);
      grid.positions[i]=local[0]-width/2;
      grid.positions[i+1]=height/2-local[1];
    }
  }
  if(node.mesh.backBreath){
    for(let i=0;i<grid.positions.length;i+=3){
      const vertex=i/3,row=Math.floor(vertex/(node.mesh.columns+1)),col=vertex%(node.mesh.columns+1);
      const originalX=bx+bw*col/node.mesh.columns;
      const originalY=by+bh*row/node.mesh.rows;
      const [dx,dy]=upperBackDeltaAtFrame(node,shot,originalX,originalY,frame);
      grid.positions[i]+=dx;
      grid.positions[i+1]-=dy; // renderer has up-positive Y
    }
  }
  return grid;
}

/** Fix pixel/world calibration at baseline camera; camera animation then changes framing. */
export function sourceWorldScale(canvas:{width:number;height:number},width:number,height:number):number{
  const visibleSourceHeight=Math.min(canvas.height,canvas.width/(width/height));
  return 2*14*Math.tan(Math.PI/12)/visibleSourceHeight;
}
export function cameraAtFrame(shot:DirectedShot,frame:number):Omit<CameraKey,'frame'>{
  const keys=shot.camera.keyframes;
  if(shot.camera.type==='none'||keys.length===0)return {z:14,fovDeg:30,lookAt:[0,0,0]};
  const read=(get:(key:CameraKey)=>number)=>trackAtFrame({target:'camera',transform:'translateX',
    unit:'pixels_source_canvas',easing:'linear',keyframes:keys.map(k=>({frame:k.frame,value:get(k)}))},frame);
  return {z:read(k=>k.z),fovDeg:read(k=>k.fovDeg),
    lookAt:[read(k=>k.lookAt[0]),read(k=>k.lookAt[1]),read(k=>k.lookAt[2])]};
}
