"""Read-only daily channel production readiness, never fake publications."""
import argparse,json
from datetime import date
from pathlib import Path
from .remake_autopilot import ROOT
from .errors import VideoForgeError
CHANNELS=("alchemy-lab","gamer","manu-kids","otaku-br","otaku-en")
def load(p):
    if p.is_symlink() or not p.is_file() or p.stat().st_size>1000000:
        raise VideoForgeError("DAILY_FILE_UNAVAILABLE")
    return json.loads(p.read_text(encoding="utf-8"))
def inspect(root=ROOT,day=None):
    day=day or date.today().isoformat()
    try:date.fromisoformat(day)
    except ValueError as exc:raise VideoForgeError("DAILY_DATE_INVALID") from exc
    rows=[]
    for ch in CHANNELS:
        base=Path(root)/"canal"/ch/"editorial"
        cand=load(base/"candidatos.json")
        hist=load(base/"historico-videos.json")
        reserve=load(base/"reservas.json")
        if (cand.get("schema")!="videoforge/channel-candidates/v1" or
            cand.get("channel")!=ch or
            hist.get("schema")!="videoforge/channel-video-history/v1" or
            hist.get("canal_id")!=ch or
            reserve.get("schema")!="videoforge/channel-topic-reservations/v1" or
            reserve.get("channel")!=ch):
            raise VideoForgeError("DAILY_SCHEMA_INVALID")
        candidates=cand.get("candidates")
        videos=hist.get("videos")
        if not isinstance(candidates,list) or not isinstance(videos,list):
            raise VideoForgeError("DAILY_LIST_INVALID")
        posted=sum(isinstance(v,dict) and v.get("publicado") is True and
            isinstance(v.get("youtube_video_id"),str) and bool(v["youtube_video_id"]) and
            v.get("publication_date")==day for v in videos)
        ready=sum(isinstance(v,dict) and v.get("video_oficial_do_programa") is True and
            v.get("arte_final") is True and v.get("narracao_final") is True and
            v.get("producao_oficial_pendente") is False for v in videos)
        state=("LOCAL_POST_RECORDED_VERIFY_API" if posted else
               "OFFICIAL_ASSETS_RECORDED_VERIFY_MP4" if ready else
               "TOPICS_REQUIRE_VERIFICATION" if candidates else
               "NO_VERIFIED_CANDIDATE")
        rows.append({"channel":ch,"date":day,"target_publications":1,
            "candidate_records":len(candidates),"recorded_official_ready":ready,
            "local_post_records":posted,
            "history_incomplete":hist.get("historico_youtube_importado") is not True,
            "status":state,"youtube_upload_claimed":False})
    return {"schema":"videoforge/daily-production-readiness/v1",
        "date":day,"timezone":"America/Sao_Paulo","channels":rows,
        "target_videos_per_day":5,"generated_videos":0,"uploads":0,
        "alchemy_ep01_r2_blocked":True,"manual_approvals_not_inferred":True,
        "next_engineering_priority":"integrate_actual_render_and_youtube_publishing_executor"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date",default=None)
    p.add_argument("--output",default="output/daily-production-readiness.json")
    args=p.parse_args()
    report=inspect(day=args.date)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for row in report["channels"]:
        print("DAILY",row["channel"],row["status"],"candidates",row["candidate_records"])
    print("DAILY_GOAL",report["target_videos_per_day"],"GENERATED",report["generated_videos"])
if __name__=="__main__":main()
