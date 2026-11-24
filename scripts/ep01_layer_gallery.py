"""Build a self-contained EP01 layer gallery from the plan and reconciled receipts."""
import argparse
import base64
from collections import Counter
from html import escape
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import quote

from PIL import Image
from scripts.ep01_action_production_queue import ROOT, EP, digest

REPO = "https://github.com/HelioConde/VideoForge-IA"


def feedback_state(task, receipt):
    """Current source restrictions cannot be cleared by an older receipt."""
    status = task["status"]
    reason = task.get("reason", "")
    if (status.startswith("blocked") or status in {
            "archived_version_check_needed", "archived_rejected_needs_review"}):
        return {"status": status, "reason": reason}
    if (receipt and task.get("source_sha256")
            and receipt.get("source_sha256") != task["source_sha256"]):
        return {"status": "blocked_receipt_source_mismatch",
                "reason": "Receipt does not identify the current source SHA; review provenance"}
    return {"status": receipt.get("status", status),
            "reason": receipt.get("technical_qa") or receipt.get("reason") or reason}


def feedback_snapshot(tasks, attempts):
    states = {}
    for task in tasks:
        key = task["task_id"]
        if key in states:
            raise ValueError("Duplicate feedback task identity")
        states[key] = feedback_state(task, attempts.get(key, {}))
    return {"states": states}


def gallery(tasks, attempts, root=ROOT):
    shots = {}
    counts = Counter()
    for task in tasks:
        receipt = attempts.get(task["task_id"], {})
        current = feedback_state(task, receipt)
        status = current["status"]
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
        details = current["reason"]
        history = ""
        if receipt:
            history = (f'<br>Registro histórico: {escape(str(receipt.get("status", "")))}'
                       f' · {escape(str(receipt.get("technical_qa", "")))}')
        shot.append(f'<tr><td>{thumb}</td><td>{label}<br>Agente {escape(task["owner"])}</td>'
                    f'<td>{escape(status)}<br>{escape(str(details))}{history}</td><td>{" · ".join(links)}'
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--feedback-json", type=Path)
    args = parser.parse_args()
    tasks = json.loads(args.plan.read_bytes())["queue"]["tasks"]
    attempts = json.loads(args.ledger.read_bytes())["attempts"]
    snapshot = feedback_snapshot(tasks, attempts)
    args.output.write_text(gallery(tasks, attempts), encoding="utf-8")
    if args.feedback_json:
        args.feedback_json.write_text(json.dumps(snapshot, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
