"""Build a self-contained EP01 layer gallery from the plan and reconciled receipts."""
import base64
from collections import Counter
from html import escape
from io import BytesIO
import json
from pathlib import Path
import sys
from urllib.parse import quote

from PIL import Image
from scripts.ep01_action_production_queue import ROOT, EP, digest

REPO = "https://github.com/HelioConde/VideoForge-IA"


def gallery(tasks, attempts, root=ROOT):
    shots = {}
    counts = Counter()
    for task in tasks:
        receipt = attempts.get(task["task_id"], {})
        status = receipt.get("status", task["status"])
        shot = shots.setdefault(task["shot_id"], [])
        kind = task["kind"]
        label = escape(task.get("part") or kind)
        links = []
        run = str(receipt.get("child_run_id", ""))
        if run.isdecimal():
            links.append(f'<a href="{REPO}/actions/runs/{run}">Action {run}</a>')
            artifact = str(receipt.get("artifact_id", ""))
            if artifact.isdecimal():
                links.append(f'<a href="{REPO}/actions/runs/{run}/artifacts/{artifact}">Arquivo da prévia</a>')
        filename = receipt.get("source_file") or task.get("source_file")
        expected = receipt.get("sha256") or task.get("file_sha256")
        thumb = ""
        if filename and expected:
            path = (root / filename).resolve()
            if path.is_relative_to((root / EP).resolve()) and path.suffix.lower() == ".png":
                if path.is_file() and digest(path) == expected:
                    links.append(f'<a href="{REPO}/blob/main/{quote(filename)}">PNG</a>')
                    with Image.open(path) as image:
                        image.thumbnail((180, 200))
                        buf = BytesIO()
                        image.convert("RGBA").save(buf, "PNG")
                    thumb = '<img alt="Miniatura" src="data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode() + '">'
                    if kind == "image":
                        counts["verified"] += 1
                else:
                    links.append("SHA indisponível nesta cópia")
        timing = receipt.get("elapsed_seconds")
        details = receipt.get("technical_qa") or receipt.get("reason") or task.get("reason", "")
        shot.append(f'<tr><td>{thumb}</td><td>{label}<br>Agente {escape(task["owner"])}</td>'
                    f'<td>{escape(status)}<br>{escape(str(details))}</td><td>{" · ".join(links)}'
                    + (f'<br>{timing} s no controlador' if isinstance(timing, int) else '') + '</td></tr>')
    sections = [f'<h2>{escape(key)}</h2><table><tr><th>Imagem</th><th>Tarefa</th><th>Estado</th>'
                f'<th>Evidência</th></tr>{"".join(rows)}</table>' for key, rows in shots.items()]
    return ('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>EP01 — produção</title>'
            '<style>body{font:16px system-ui;margin:2rem}table{border-collapse:collapse}td,th{padding:.5rem;'
            'vertical-align:top;text-align:left;border-bottom:1px solid #aaa}img{background:#888}</style>'
            f'<h1>EP01 — produção por tomada</h1><p>{counts["verified"]} PNGs de peças conferidos por SHA-256. '
            'A miniatura mostra o arquivo arquivado. A aprovação artística exige revisão independente.</p>'
            + ''.join(sections)+'</html>')


if __name__ == "__main__":
    plan, ledger, output = map(Path, sys.argv[1:])
    output.write_text(gallery(json.loads(plan.read_bytes())["queue"]["tasks"],
                              json.loads(ledger.read_bytes())["attempts"]), encoding="utf-8")
