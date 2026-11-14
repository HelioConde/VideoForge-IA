/**
 * VideoForge — contrato de render cinematográfico multipersonagem.
 * EDL sem arte nunca deve ser tratada como vídeo renderizável.
 */
import type {ThreeRigManifest} from './rig-three-math';
import {validatePupilPerformance, type GazePerformance} from './eye-gaze-timeline';

export type CinematicShotType =
  'black'|'insert'|'low_angle'|'wide'|'close_up'|'extreme_close_up'|
  'match_cut'|'over_shoulder'|'medium'|'tracking'|'two_shot'|'action';
export type CinematicHudPolicy = 'none'|'remotion_overlay';
export type CinematicActor = {
  id:string;
  rig:ThreeRigManifest;
  motherSha256:string;
  approvedForShot:true;
};
export type CinematicHud = {
  heading:string;
  detail?:string;
};
export type CinematicShot = {
  id:string;
  scene:string;
  startFrame:number;
  endFrameExclusive:number;
  type:CinematicShotType;
  characters:string[];
  hudPolicy:CinematicHudPolicy;
  status:'black_no_art_required'|'ready_for_render';
  renderAllowed:true;
  backgroundFile?:string;
  backgroundSha256?:string;
  sourceMotherSha256?:string;
  sourceCanvas?:{width:number;height:number};
  /** Human-QA focal eye/object box in unscaled original pixels. */
  focalBbox?:[number,number,number,number];
  actors?:CinematicActor[];
  staticShotApproved?:boolean;
  audioFile?:string|null;
  hud?:CinematicHud|null;
  humanVisualApproved?:true;
  originShaVerified?:true;
  performance?:GazePerformance;
};
export type CinematicEpisodeProps = {
  schema:'videoforge/cinematic-remotion-episode/v1';
  channel:string;
  videoId:string;
  fps:30;
  width:1080;
  height:1920;
  totalFrames:number;
  renderApproved:true;
  shots:CinematicShot[];
};

const SHA=/^[a-f0-9]{64}$/;
const SHOT=/^C\d{2}-P\d{2}$/;
/** Native shot sources may be legacy 2:3 or the approved portraits at ~9:16. */
const nativeCanvasAllowed=(size:{width:number;height:number}|undefined):boolean=>
  Boolean(size && Number.isSafeInteger(size.width)&&Number.isSafeInteger(size.height) &&
    ((size.width===1024 && size.height===1536) ||
     (size.width===941 && size.height===1672)));
const CLOSE_TYPES=new Set<CinematicShotType>(['close_up','extreme_close_up']);
const SUBJECT_TYPES=new Set<CinematicShotType>([
  'close_up','extreme_close_up','medium','two_shot','over_shoulder',
  'low_angle','tracking','action',
]);
const isPositive=(value:number):boolean=>Number.isSafeInteger(value)&&value>0;

export const shotDurationFrames=(shot:CinematicShot):number=>
  shot.endFrameExclusive-shot.startFrame;

/** Fail closed before WebGL rendering, even for the black-only opening. */
export const validateCinematicRender=(input:CinematicEpisodeProps):void=>{
  if(!input || input.schema!=='videoforge/cinematic-remotion-episode/v1' ||
    input.channel!=='alchemy-lab' ||
    input.videoId!=='mmorpg-conquiste-a-princesa-ep01' ||
    input.fps!==30 || input.width!==1080 || input.height!==1920 ||
    input.totalFrames!==4890 || input.renderApproved!==true ||
    !Array.isArray(input.shots) || input.shots.length!==37)
    throw new Error('CINEMATIC_RENDER_APPROVED_EDL_REQUIRED');

  let cursor=0;
  const used=new Set<string>();
  for(const [index,shot] of input.shots.entries()){
    if(!shot || !SHOT.test(shot.id) || used.has(shot.id) ||
      shot.scene!==shot.id.slice(0,3) ||
      !Number.isSafeInteger(shot.startFrame) ||
      !isPositive(shotDurationFrames(shot)) ||
      shot.startFrame!==cursor || shot.renderAllowed!==true)
      throw new Error('CINEMATIC_RENDER_FRAME_OR_APPROVAL_INVALID');
    used.add(shot.id);
    cursor=shot.endFrameExclusive;
    if(shot.type==='black'){
      if(index!==0 || shot.id!=='C01-P01' ||
        shot.startFrame!==0 || shot.endFrameExclusive!==60 ||
        shot.status!=='black_no_art_required' ||
        shot.backgroundFile || shot.audioFile || shot.hud ||
        (shot.actors?.length??0)!==0 || shot.characters.length!==0)
        throw new Error('CINEMATIC_BLACK_OPENING_INVALID');
      continue;
    }
    if(shot.status!=='ready_for_render' ||
      shot.humanVisualApproved!==true ||
      shot.originShaVerified!==true ||
      !shot.backgroundFile || !shot.sourceMotherSha256 ||
      !nativeCanvasAllowed(shot.sourceCanvas) ||
      !SHA.test(shot.sourceMotherSha256) ||
      !SHA.test(shot.backgroundSha256??''))
      throw new Error('CINEMATIC_SHOT_VISUAL_QA_OR_ORIGIN_MISSING');
    if(['close_up','extreme_close_up','insert'].includes(shot.type)){
      const c=shot.sourceCanvas!;
      const box=shot.focalBbox;
      const scale=Math.max(input.width/c.width,input.height/c.height);
      const left=(c.width-input.width/scale)/2;
      const top=(c.height-input.height/scale)/2;
      if(!box || box.length!==4 ||
        !box.every(Number.isSafeInteger) ||
        box[2]<1 || box[3]<1 ||
        box[0]<left+2 || box[1]<top+2 ||
        box[0]+box[2]>c.width-left-2 ||
        box[1]+box[3]>c.height-top-2)
        throw new Error('CINEMATIC_FOCAL_POINT_CLIPPED_BY_9_16_CROP');
    }
    if(shot.backgroundFile.includes('..') ||
      shot.backgroundFile.startsWith('/') ||
      !shot.backgroundFile.endsWith('.png') ||
      !shot.backgroundFile.includes('/'+shot.id+'/'))
      throw new Error('CINEMATIC_BACKGROUND_NOT_OWN_SHOT');
    if(shot.hudPolicy==='remotion_overlay'){
      if(!shot.hud?.heading?.trim())
        throw new Error('CINEMATIC_HUD_REMOTION_OVERLAY_REQUIRED');
    }else if(shot.hud)throw new Error('CINEMATIC_UNEXPECTED_HUD');
    const actors=shot.actors??[];
    if(shot.id==='C12-P01'){
      if(!shot.performance)
        throw new Error('CINEMATIC_C12_PUPIL_PERFORMANCE_REQUIRED');
      validatePupilPerformance(shot.performance,shot.id,shotDurationFrames(shot));
      if(actors.length!==1||actors[0]?.id!=='kael')
        throw new Error('CINEMATIC_C12_KAEL_ONLY');
      const r=actors[0].rig;
      const eyes=r.eyeRig;
      const ids=new Set(r.layers.map(l=>l.id));
      if(!eyes || eyes.actorId!=='kael' ||
        r.headMaxRotationDeg!==0 || r.blinkFrames.length!==0 ||
        eyes.eyeUnderlaysVerified!==true ||
        eyes.pupilMasksVerified!==true ||
        eyes.noDuplicatePaintedPupilsInHead!==true ||
        eyes.rotationOrTranslationClippingQA!==true ||
        eyes.humanVisualApproved!==true ||
        eyes.gazePupilMaxPx!==12 || eyes.eyelidMaxPx!==1 ||
        !['pupil-left','pupil-right','eyelid-left','eyelid-right']
          .every(id=>ids.has(id)))
        throw new Error('CINEMATIC_C12_INDEPENDENT_EYES_AND_UNDERLAYS_REQUIRED');
    }else if(shot.performance){
      throw new Error('CINEMATIC_UNEXPECTED_GAZE_PERFORMANCE');
    }
    if(actors.length===0 && (SUBJECT_TYPES.has(shot.type) ||
      shot.staticShotApproved!==true))
      throw new Error('CINEMATIC_SUBJECT_MUST_HAVE_REAL_RIG');
    const ids=new Set<string>();
    for(const actor of actors){
      const rig=actor.rig;
      if(!actor.id || ids.has(actor.id) ||
        actor.approvedForShot!==true ||
        actor.motherSha256!==shot.sourceMotherSha256 ||
        rig.schema!=='videoforge/rig-three/v1' ||
        rig.rigType!=='independent-parts-and-deformable-mesh' ||
        rig.sceneMotherSha256!==shot.sourceMotherSha256 ||
        rig.technicalAssetsVerified!==true ||
        rig.humanVisualReview!==true ||
        rig.youtubeUploaded!==false ||
        rig.canvas.width!==shot.sourceCanvas?.width ||
        rig.canvas.height!==shot.sourceCanvas?.height ||
        rig.layers.length<3 ||
        !rig.layers.some(l=>Boolean(l.mesh)) ||
        !rig.layers.every(l=>SHA.test(l.sha256) &&
          !l.file.includes('..') &&
          l.file.includes('/'+shot.id+'/') &&
          l.file.endsWith('.png')))
        throw new Error('CINEMATIC_ACTOR_RIG_NOT_VERIFIED_FOR_SHOT');
      ids.add(actor.id);
    }
    if(CLOSE_TYPES.has(shot.type) &&
      (actors.length===0 || !shot.backgroundFile.includes('/'+shot.id+'/')))
      throw new Error('CINEMATIC_CLOSEUP_SOURCE_INDEPENDENCE_REQUIRED');
  }
  if(cursor!==input.totalFrames || used.size!==37)
    throw new Error('CINEMATIC_EPISODE_TIMELINE_INCOMPLETE');
};

/** Deterministic absolute-frame lookup for editor and renderer. */
export const cinematicShotAtFrame=(
  shots:readonly CinematicShot[],frame:number
):CinematicShot=>{
  if(!Number.isSafeInteger(frame)||frame<0)
    throw new Error('CINEMATIC_FRAME_OUT_OF_RANGE');
  const shot=shots.find(s=>s.startFrame<=frame && frame<s.endFrameExclusive);
  if(!shot)throw new Error('CINEMATIC_FRAME_OUT_OF_RANGE');
  return shot;
};
