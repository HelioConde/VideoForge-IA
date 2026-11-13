"""Fixtures geometrico/sinteticas para smoke real de SVG no Chromium.

NAO sao assets do usuario, nem validacao visual de anime.
"""
from pathlib import Path
import json
import struct
import wave
import zlib

ROOT = Path(__file__).resolve().parents[1]
W, H = 256, 384


def png(path, paint):
    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload +
                struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff))
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        for x in range(W):
            raw.extend(paint(x, y))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" +
        chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0)) +
        chunk(b"IDAT", zlib.compress(bytes(raw), 6)) +
        chunk(b"IEND", b""))


def main():
    public = ROOT / "motion-remotion/public/vf-scene"
    if public.exists():
        raise SystemExit("Nao sobrescrever assets existentes de outro teste")
    public.mkdir(parents=True)
    rig_dir = public / "rig"
    rig_dir.mkdir()
    transparent = (0, 0, 0, 0)

    def background(x, y):
        return (26 + y // 30, 45 + y // 20, 92 + y // 22, 255)

    def cape(x, y):
        if 84 <= x <= 176 and 150 <= y <= 285:
            # trapezio vermelho, atras do corpo azul
            half = 15 + int((y - 150) * .31)
            if abs(x - 128) <= half:
                return (232, 34, 54, 255)
        return transparent

    def body(x, y):
        return (55, 145, 220, 255) if 104 <= x <= 152 and 147 <= y <= 305 else transparent

    def head(x, y):
        return (206, 146, 96, 255) if (x-128)**2 + (y-116)**2 < 33**2 else transparent

    def open_eyes(x, y):
        return (255, 255, 245, 255) if (115 <= x <= 122 or 136 <= x <= 143) and 114 <= y <= 119 else transparent

    def closed_eyes(x, y):
        return (30, 25, 24, 255) if (115 <= x <= 122 or 136 <= x <= 143) and y == 118 else transparent

    png(public / "background.png", background)
    png(public / "character-main.png", body)
    png(public / "foreground-roof.png",
        lambda x, y: (40, 37, 55, 255) if y >= 315 else transparent)
    for filename, paint in [
        ("body-no-head-no-cape.png", body),
        ("head-no-eyes.png", head),
        ("eyes-open.png", open_eyes),
        ("eyes-closed.png", closed_eyes),
        ("cape.png", cape),
    ]:
        png(rig_dir / filename, paint)

    with wave.open(str(public / "silence.wav"), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        wav.writeframes(b"\0" * 48000 * 2 * 2 * 8)

    props = {
        "id": "mesh-smoke", "scene": "cena-01", "durationFrames": 240,
        "preset": "equilibrado", "background": "vf-scene/background.png",
        "character": "vf-scene/character-main.png",
        "foreground": "vf-scene/foreground-roof.png",
        "silence": "vf-scene/silence.wav", "layerSourceHash": "0" * 64,
        "rig": {
            "schema": "videoforge/mesh-rig/v1",
            "canvas": {"width": W, "height": H},
            "layers": {
                "body": "vf-scene/rig/body-no-head-no-cape.png",
                "head": "vf-scene/rig/head-no-eyes.png",
                "eyesOpen": "vf-scene/rig/eyes-open.png",
                "eyesClosed": "vf-scene/rig/eyes-closed.png",
                "cape": "vf-scene/rig/cape.png",
            },
            "neckPivot": {"x": 128, "y": 150},
            "headMaxDeg": 1.6,
            "blinkFrames": [40, 132],
            "capeMesh": {
                "bounds": {"x": 84, "y": 150, "width": 92, "height": 135},
                "columns": 4, "rows": 6, "amplitudePx": 7,
            },
        },
    }
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    (output / "mesh-smoke-props.json").write_text(
        json.dumps(props), encoding="utf-8")


if __name__ == "__main__":
    main()
