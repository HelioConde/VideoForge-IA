/**
 * Smoothly returns ALL animation transforms to their shared neutral pose
 * BEFORE an open/closed character image swap. No frame gets reset abruptly.
 * Also blends back to normal breathing/head motion AFTER the blink.
 */
export const blinkNeutralWeightAtFrame=(
  frame:number, centers:readonly number[], holdFrames=3, rampFrames=12
):number=>{
  if(!Number.isFinite(frame)||!Number.isFinite(holdFrames)||!Number.isFinite(rampFrames)
    ||holdFrames<2||rampFrames<3)throw new Error('BLINK_NEUTRAL_PARAMETERS_INVALID');
  if(!Array.isArray(centers)||centers.some(c=>!Number.isInteger(c)||c<0))
    throw new Error('BLINK_NEUTRAL_CENTERS_INVALID');
  if(centers.length===0)return 1;
  const distance=Math.min(...centers.map(c=>Math.abs(frame-c)));
  if(distance<=holdFrames)return 0;
  if(distance>=holdFrames+rampFrames)return 1;
  const t=(distance-holdFrames)/rampFrames;
  // C1 continuous, 0 derivative at neutral and at full-motion boundary.
  return t*t*(3-2*t);
};

export type SynchronizedPose={translateX:number;translateY:number;rotateDeg:number};
export const synchronizedPoseAtFrame=(
  pose:SynchronizedPose, frame:number, centers:readonly number[],
  holdFrames=3,rampFrames=12
):SynchronizedPose=>{
  const scale=blinkNeutralWeightAtFrame(frame,centers,holdFrames,rampFrames);
  // Explicit +0 avoids -0 from negative sine waves at a blink boundary.
  if(scale===0)return {translateX:0,translateY:0,rotateDeg:0};
  return {
    translateX:pose.translateX*scale,
    translateY:pose.translateY*scale,
    rotateDeg:pose.rotateDeg*scale,
  };
};

/**
 * Optional for a genuine independently extracted head sprite. Does NOT
 * deform/guess a head from a flattened character image. Its phase and
 * pivot are shared with the body, and its delta is neutral at all swaps.
 */
export const subtleHeadPoseAtFrame=(
  frame:number, fps:number, centers:readonly number[]
):SynchronizedPose=>{
  if(!Number.isInteger(frame)||!Number.isFinite(fps)||fps<=0)
    throw new Error('HEAD_POSE_TIME_INVALID');
  const t=frame/fps;
  const y=.55*(Math.sin(2*Math.PI*.22*t)-Math.sin(0));
  const rotate=.18*(Math.sin(2*Math.PI*.17*t)-Math.sin(0));
  const x=.18*(Math.sin(2*Math.PI*.14*t)-Math.sin(0));
  return synchronizedPoseAtFrame({translateX:x,translateY:y,rotateDeg:rotate},frame,centers);
};
