"""SHA-gated C12 ThreeCanvas preview: archive source pixels, never fabricate art."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01"
PREFIX = "vf-cinema/alchemy-lab/mmorpg-conquiste-a-princesa-ep01/assets/planos"
SOURCES = {
    "C12-P02": (
        "assets/referencias/chat-aprovadas/confronto-trono-c12-p02.png",
        "01eb7c127b0699d2e502d29dacec0bb39c0e1e23bf8205fdcf6fb70976e70535",
        "846358dfc4d2e85961b33c78e0fdf73cbc500ff46ea53af6d2444bdbac7c07cd",
    ),
    "C12-P03": (
        "assets/referencias/chat-aprovadas/elara-close-trono.png",
        "bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a",
        "a89125a1b5b6b46891d7f1306c015183e2e5c781605b3886143bf91cf16b2c15",
    ),
}
PART_SHAS = {
    "kael-cape-loose-fold": "d2db9bb4b9014dac97e8c73b1769b5062e4dd4992c592be43250c13e37e26841",
    "elara-left-face-hair-lock": "611638aa33b8fc72c3654bb141ce92ad59fea2adaced39fcf8b5e742e45d450f",
    "elara-back-hair-fall": "a7eb167c147b399840ccae377d498fce417efb88a5c05fe9e74f17f5fe0bb634",
    "elara-earring-pendant": "d5c73354209eafc11d4042fdef16c6138f5f8b16fe63e62b47c06b73d83e277d",
    "elara-sleeve-lower-fabric": "722b2a4ab6f7fc0f0b2413fd7ad2ce7d39c7165ca274159d386ad5791d9cdb78",
}
SHOT_PARTS = {
    "C12-P02": ["kael-cape-loose-fold"],
    "C12-P03": [
        "elara-left-face-hair-lock", "elara-back-hair-fall",
        "elara-earring-pendant", "elara-sleeve-lower-fabric",
    ],
}

class AssetGateError(ValueError):
    pass

def bbox(polygon):
    if not polygon or any(len(p) != 2 or not all(type(v) is int for v in p)
                          for p in polygon):
        raise AssetGateError("INVALID_POLYGON")
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x, y = min(xs), min(ys)
    w, h = max(xs)-x+1, max(ys)-y+1
    if x < 0 or y < 0 or x+w > 941 or y+h > 1672:
        raise AssetGateError("POLYGON_OUTSIDE_SOURCE_CANVAS")
    return [x, y, w, h]

def plan():
    p = json.loads((EP/"qa-c12-rig-malha-v2.json").read_text(encoding="utf8"))
    if (p.get("schema") != "videoforge/c12-mesh-rig-technical-draft/v2"
        or p.get("meshTotalTriangles") != 512
        or p.get("external_image_generation_calls") != 0
        or p.get("official_render_allowed") is not False
        or len(p.get("meshParts", [])) != 5
        or {m["id"] for m in p["meshParts"]} != set(PART_SHAS)
        or sum(m["columns"]*m["rows"]*2 for m in p["meshParts"]) != 512):
        raise AssetGateError("C12_TECHNICAL_PLAN_INVALID")
    return p

def policy():
    r = json.loads((EP/"pedido-render-c12-tecnico.json").read_text(encoding="utf8"))
    if (r.get("schema") != "videoforge/c12-technical-render-request/v1"
        or r.get("channel") != "alchemy-lab"
        or r.get("video_id") != "mmorpg-conquiste-a-princesa-ep01"
        or r.get("render_mp4") is not True
        or r.get("technical_preview_only") is not True
        or r.get("official_video_approved") is not False
        or r.get("new_image_generation_calls") != 0
        or r.get("youtube_upload") is not False):
        raise AssetGateError("C12_POLICY_BLOCKED")
    state_file=EP/"estado-atual.json"
    policy_file=EP/"autonomy-policy.json"
    if (any(p.is_symlink() or not p.is_file() for p in (state_file,policy_file))
            or (EP/"SEM-GERACAO-NOVAS-IMAGENS.lock").exists()
            or not (EP/"REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md").is_file()):
        raise AssetGateError("C12_REMAKE_ACTIVE_POLICY_MISSING_OR_LEGACY_LOCK")
    current=json.loads(state_file.read_text(encoding="utf8"))
    governance=json.loads(policy_file.read_text(encoding="utf8"))
    if (current.get("active_production_version")!="remake-v2-20261115"
            or current.get("locks",{}).get("no_new_image_generation") is not False
            or current.get("locks",{}).get("official_video_allowed") is not False
            or current.get("locks",{}).get("no_youtube_upload") is not True
            or governance.get("scope")!="alchemy-lab/mmorpg-conquiste-a-princesa-ep01"
            or governance.get("auto_publish_youtube") is not False):
        raise AssetGateError("C12_REMAKE_ACTIVE_POLICY_INVALID")

def required_files(p):
    items = []
    for shot, (source, mother_sha, background_sha) in SOURCES.items():
        items.extend([
            (EP/source, mother_sha, (941,1672), False, "mother_"+shot),
            (EP/"assets/planos"/shot/"background-inpaint-technical.png",
             background_sha, (941,1672), False, "background_"+shot),
        ])
    for m in p["meshParts"]:
        shot, name = m["shot"], m["id"]
        if name not in SHOT_PARTS.get(shot, []):
            raise AssetGateError("C12_LAYER_SHOT_MISMATCH")
        _,_,w,h = bbox(m["polygon"])
        items.append((EP/"assets/planos"/shot/(name+".png"),
                      PART_SHAS[name], (w,h), True, name))
    return items

def validate_png(path, expected, dims, alpha):
    if path.is_symlink() or not path.is_file():
        raise AssetGateError("MISSING_OR_SYMLINK:"+str(path.relative_to(ROOT)))
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise AssetGateError("SHA_MISMATCH:"+str(path.relative_to(ROOT)))
    with path.open("rb") as stream:
        header = stream.read(33)
    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise AssetGateError("PNG_INVALID:"+str(path.relative_to(ROOT)))
    w,h,depth,color = struct.unpack(">IIBB", header[16:26])
    if (w,h) != dims or depth != 8 or color not in (2,6) or (alpha and color != 6):
        raise AssetGateError("PNG_DIMENSIONS_OR_RGBA_INVALID:"+str(path.relative_to(ROOT)))

def prepare(out):
    out.mkdir(parents=True,exist_ok=True)
    result = {
        "schema":"videoforge/c12-technical-three-preflight/v1",
        "status":"ASSETS_PENDING", "technical_preview_only":True,
        "official_video_approved":False,"human_visual_approved":False,
        "youtube_uploaded":False,"image_generation_calls":0,
        "verified":[],"errors":[],
    }
    p = None
    try:
        policy()
        p = plan()
        for path, sha, size, alpha, name in required_files(p):
            try:
                validate_png(path, sha, size, alpha)
            except (AssetGateError,OSError) as exc:
                result["errors"].append(str(exc))
            else:
                result["verified"].append({"id":name,"sha256":sha})
    except (AssetGateError,OSError,KeyError,ValueError) as exc:
        result["errors"].append(str(exc))
    if not result["errors"] and p is not None:
        part = {m["id"]:m for m in p["meshParts"]}
        shots=[]
        for shot, (_,mother_sha,bg_sha) in SOURCES.items():
            prefix=PREFIX+"/"+shot+"/"
            source_folder=EP/"assets/planos"/shot
            public=ROOT/"motion-remotion/public"/prefix
            public.mkdir(parents=True,exist_ok=True)
            bg=source_folder/"background-inpaint-technical.png"
            shutil.copyfile(bg,public/bg.name)
            layers=[]
            for name in SHOT_PARTS[shot]:
                m=part[name]
                png=source_folder/(name+".png")
                shutil.copyfile(png,public/png.name)
                mesh={"kind":m["meshKind"],"columns":m["columns"],
                      "rows":m["rows"],"pinnedRows":[0],
                      "amplitudePx":m["amplitudePx"]}
                if name=="elara-earring-pendant":
                    mesh.update({"pivotPx":m["pivot"],
                                 "frequencyHz":m.get("frequencyHz",.67),
                                 "phaseRad":m.get("phaseRad",0)})
                layers.append({"id":name,"file":prefix+png.name,"sha256":PART_SHAS[name],
                               "bbox":bbox(m["polygon"]), "z":5+SHOT_PARTS[shot].index(name),
                               "mesh":mesh})
            shots.append({"id":shot,"sourceOriginalSha256":mother_sha,
                          "backgroundFile":prefix+bg.name,"backgroundSha256":bg_sha,
                          "layers":layers})
        props={"schema":"videoforge/c12-technical-three-mesh-preview/v1",
               "fps":30,"sourceCanvas":{"width":941,"height":1672},
               "width":720,"height":1280,"totalFrames":240,
               "expectedMeshTriangles":512,
               "status":"TECHNICAL_NO_HUMAN_APPROVAL",
               "sourceOriginalsArchived":True,"officialVideoApproved":False,
               "imageGenerationCalls":0,"shots":shots}
        (out/"props.json").write_text(json.dumps(props,indent=2)+"\n",encoding="utf8")
        result.update({"status":"READY_FOR_TECHNICAL_THREECANVAS_RENDER",
                       "mesh_triangles":512,"independent_rgba_parts":5})
    (out/"preflight.qa.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["status"].startswith("READY") else 2

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,
        default=ROOT/"output/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/c12-mesh-technical")
    args=parser.parse_args()
    return prepare(args.output.resolve())

if __name__=="__main__":
    raise SystemExit(main())
