/**
 * C01-P02: original 2D sword-and-hand articulated animation.
 * Pure frame math; shaft/blade moves independently from sheath; a wrist
 * pivot rotates only the hand. No full-PNG move or simulated source artwork.
 */
export type SwordDrawTuning={
  beginFrame:number;
  finishFrame:number;
  travelPx:number;
  axisDeg:number;
  handFollow:number;
  handRotationDeg:number;
};

export type SwordPose={
  progress:number;
  bladeDx:number;
  bladeDy:number;
  handDx:number;
  handDy:number;
  handAngleDeg:number;
};

const bounded=(v:number,lo:number,hi:number)=>Math.max(lo,Math.min(hi,v));
const smooth=(t:number)=>t*t*(3-2*t);

export const swordPoseAtFrame=(
  frame:number,
  durationFrames:number,
  tuning:SwordDrawTuning,
):SwordPose=>{
  if(!Number.isInteger(durationFrames)||durationFrames<12||
    !Number.isInteger(frame)||frame<0||frame>=durationFrames ||
    !Number.isInteger(tuning.beginFrame)||
    !Number.isInteger(tuning.finishFrame)||
    tuning.beginFrame<0||tuning.finishFrame>durationFrames-1||
    tuning.finishFrame<=tuning.beginFrame+2||
    !Number.isFinite(tuning.travelPx)||tuning.travelPx<1||tuning.travelPx>400||
    !Number.isFinite(tuning.axisDeg)||Math.abs(tuning.axisDeg)>180||
    !Number.isFinite(tuning.handFollow)||tuning.handFollow<0||tuning.handFollow>1||
    !Number.isFinite(tuning.handRotationDeg)||Math.abs(tuning.handRotationDeg)>8)
    throw new Error('REMAKE_SWORD_DRAW_RIG_PARAMETERS_INVALID');

  const progress=smooth(bounded(
    (frame-tuning.beginFrame)/(tuning.finishFrame-tuning.beginFrame),0,1));
  const direction=tuning.axisDeg*Math.PI/180;
  const bladeDx=tuning.travelPx*Math.cos(direction)*progress;
  const bladeDy=tuning.travelPx*Math.sin(direction)*progress;
  return {
    progress,bladeDx,bladeDy,
    handDx:bladeDx*tuning.handFollow,
    handDy:bladeDy*tuning.handFollow,
    handAngleDeg:tuning.handRotationDeg*progress,
  };
};
