"""Block duplicate or closed paid art requests before starting the proxy."""
from __future__ import annotations
from .production_art import archived_reference
from .wardrobe_review import source_readiness
EP=("alchemy-lab","mmorpg-conquiste-a-princesa-ep01")
def decide(channel:str,video_id:str,asset_id:str,event:str="workflow_dispatch",status:str|None=None)->dict:
    ready,reason=True,"ready_unarchived_request"
    if (channel,video_id)==EP and event=="push" and (
        not isinstance(status,str) or not status.startswith(("requested","queued"))
    ):
        ready,reason=False,"request_closed_or_not_queued"
    if archived_reference(channel,video_id,asset_id) is not None:
        ready,reason=False,"already_archived_sha_no_repeat"
    if (channel,video_id)==EP and asset_id=="character-bible-grounded-r2":
        if not source_readiness()["r2_ready"]:
            ready,reason=False,"r2_full_outfit_approval_missing"
    return {"ready":ready,"reason":reason,"provider_calls":0,"youtube_uploaded":False}
