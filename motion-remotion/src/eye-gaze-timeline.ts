/**
 * Pupil-only acting, from original C12-P01 shot direction.
 * Keyframes are LOCAL to the shot (source global frames 3990..4109).
 * No camera moves, no head rotation, no body breathing.
 */
export type GazeKeyframe={frame:number;value:number};
export type GazePerformance={
  mode:'pupils_only_locked_head';
  actorId:'kael';
  pupilKeyframes:GazeKeyframe[];
  eyelidKeyframes:GazeKeyframe[];
  headRotationDeg:0;
  bodyMotionEnabled:false;
  cameraLocked:true;
  humanMotionApproved:true;
};

const cubic=(t:number):number=>{
  const v=Math.max(0,Math.min(1,t));
  return v*v*(3-2*v);
};

/** Deterministic frame positions with hold between stages, no stateful tween. */
export const evaluateGaze=(keys:readonly GazeKeyframe[],
  frame:number,duration:number,maxAbs:number):number=>{
  if(!Number.isSafeInteger(frame)||frame<0||frame>=duration||
    !Number.isSafeInteger(duration)||duration<2||
    !Number.isFinite(maxAbs)||maxAbs<0)
    throw new Error('CINEMATIC_GAZE_FRAME_INVALID');
  if(!Array.isArray(keys)||keys.length<2||
    keys[0].frame!==0||keys[keys.length-1].frame!==duration-1)
    throw new Error('CINEMATIC_GAZE_KEYFRAME_COVERAGE_INVALID');
  let previous=-1;
  for(const k of keys){
    if(!Number.isSafeInteger(k.frame)||k.frame<=previous||
      !Number.isFinite(k.value)||Math.abs(k.value)>maxAbs)
      throw new Error('CINEMATIC_GAZE_KEYFRAME_INVALID');
    previous=k.frame;
  }
  for(let index=1;index<keys.length;index++){
    const a=keys[index-1],b=keys[index];
    if(frame<=b.frame){
      const fraction=cubic((frame-a.frame)/(b.frame-a.frame));
      return a.value+(b.value-a.value)*fraction;
    }
  }
  return keys[keys.length-1].value;
};

export const validatePupilPerformance=(p:GazePerformance,
  shotId:string,duration:number):void=>{
  if(shotId!=='C12-P01' || !p ||
    p.mode!=='pupils_only_locked_head'||p.actorId!=='kael' ||
    p.headRotationDeg!==0||p.bodyMotionEnabled!==false||
    p.cameraLocked!==true||p.humanMotionApproved!==true||
    duration!==120)
    throw new Error('CINEMATIC_GAZE_PERFORMANCE_NOT_APPROVED');
  const pupils=p.pupilKeyframes;
  const lids=p.eyelidKeyframes;
  if(JSON.stringify(pupils)!==JSON.stringify([
    {frame:0,value:0},{frame:4,value:0},
    {frame:86,value:12},{frame:119,value:12},
  ])||JSON.stringify(lids)!==JSON.stringify([
    {frame:0,value:0},{frame:7,value:0},
    {frame:86,value:1},{frame:119,value:1},
  ]))
    throw new Error('CINEMATIC_GAZE_SOURCE_KEYFRAMES_MISMATCH');
  evaluateGaze(pupils,0,duration,12);
  evaluateGaze(lids,0,duration,1);
};

