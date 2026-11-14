"""Synthetic-only art for checking real Three.js mesh rendering.

Never use this fixture in official channel videos. It tests geometry/rendering,
not anatomical quality, source fidelity or human approval.
"""
from pathlib import Path
import hashlib
import json
import math
import struct
import zlib

ROOT=Path(__file__).resolve().parents[1]
CANVAS=(1024,1536)
DST=ROOT/"motion-remotion"/"public"/"vf-scene"
ART=DST/"rig-three"


def _chunk(tag:bytes,data:bytes)->bytes:
    return (struct.pack(">I",len(data))+tag+data+
            struct.pack(">I",zlib.crc32(tag+data)&0xffffffff))


def png(path:Path,width:int,height:int,color,rgba=True):
    rows=[]
    for y in range(height):
        line=bytearray()
        for x in range(width):
            components=color(x,y)
            if len(components)!=(4 if rgba else 3):
                raise ValueError("channels")
            line.extend(components)
        rows.append(b"\x00"+line)
    kind=6 if rgba else 2
    raw=(b"\x89PNG\r\n\x1a\n"+
         _chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,kind,0,0,0))+
         _chunk(b"IDAT",zlib.compress(b"".join(rows),7))+
         _chunk(b"IEND",b""))
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def make():
    if DST.exists():
        raise RuntimeError("RIG_THREE_SYNTHETIC_FIXTURE_WOULD_OVERWRITE")
    ART.mkdir(parents=True)
    png(DST/"background.png",*CANVAS,
        lambda x,y:(24+int(18*y/1536),34,62+int(20*y/1536)),rgba=False)
    pieces=[]
    def create(pid,bbox,z,shape,mesh=None):
        filename=pid+".png"
        w,h=bbox[2:]
        digest=png(ART/filename,w,h,shape)
        item={"id":pid,"file":"vf-scene/rig-three/"+filename,"bbox":bbox,
              "sha256":digest,"z":z}
        if mesh:item["mesh"]=mesh
        pieces.append(item)
    # Every generated asset is an independent transparent crop.
    create("body-no-head",[282,735,460,630],10,lambda x,y:
        (58,121,171,255) if .12<x/460<.88 and
        .04<y/630<.94 else (0,0,0,0))
    def head(x,y,closed=False):
        cx,cy=170,185
        face=((x-cx)/154)**2+((y-cy)/172)**2<1
        eye=(76<x<128 or 217<x<269) and 145<y<175
        if face:
            if eye:
                return (48,33,40,255) if closed and 155<y<162 else (
                    (48,33,40,255) if 154<y<170 and not closed else (250,207,177,255))
            return (250,207,177,255)
        return (0,0,0,0)
    create("head-open",[337,430,350,400],20,lambda x,y:head(x,y,False))
    create("head-closed",[337,430,350,400],20,lambda x,y:head(x,y,True))
    create("hair-front",[326,401,372,170],30,lambda x,y:
        (240,142,164,255) if y<70+12*math.sin(x*.09)+.13*x
        and 10<x<362 and 10<y<159 else (0,0,0,0),
        {"columns":7,"rows":9,"pinnedRows":[0],"amplitudePx":5})
    # Render-only test manifest; never a validated asset approval.
    rig={
        "schema":"videoforge/rig-three/v1","canvas":{"width":1024,"height":1536},
        "sceneMotherSha256":"0"*64,"layers":pieces,
        "neckPivot":[512,784],"headMaxRotationDeg":2,"blinkFrames":[74,173],
        "rigType":"independent-parts-and-deformable-mesh",
        "technicalAssetsVerified":True,"humanVisualReview":True,
        "youtubeUploaded":False,
    }
    output=ROOT/"output"
    output.mkdir(exist_ok=True)
    (output/"rig-three-synthetic-props.json").write_text(json.dumps({
        "id":"synthetic-mesh-smoke-only","scene":"demo-sintetico-nao-oficial",
        "durationFrames":240,"rig":rig,
        "background":"vf-scene/background.png",
        "foreground":None,"audio":None,"draftPreview":True,
    },indent=2)+"\n",encoding="utf-8")
    print("SYNTHETIC_ONLY_THREE_MESH_TEST",len(pieces))

if __name__=="__main__":
    make()
