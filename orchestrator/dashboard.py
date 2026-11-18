"""Render a self-contained, read-only HTML dashboard from a runtime report."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
from typing import Any

AGENT_ROLES = {
    "01": "Diretor-geral", "02": "Roteirista", "03": "Diretor de cenas",
    "04": "Diretor de arte", "05": "Gerador visual", "06": "Separador de camadas",
    "07": "Especialista em rig 2D", "08": "Animador", "09": "Diretor de câmera",
    "10": "Especialista em áudio", "11": "Montador e renderizador",
    "12": "Supervisor de qualidade",
}
AGENT_SLUGS = {
    "01": "diretor-geral", "02": "roteirista", "03": "diretor-cenas",
    "04": "diretor-arte", "05": "gerador-visual", "06": "separador-camadas",
    "07": "especialista-rig", "08": "animador", "09": "diretor-camera",
    "10": "especialista-audio", "11": "montador", "12": "supervisor-qa",
}


def _safe(value: Any) -> str:
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    return html.escape(str(value if value is not None else ""), quote=True)


def _status(report: dict[str, Any], agent_id: str, now: int) -> str:
    labels = {agent_id, AGENT_ROLES[agent_id], AGENT_SLUGS[agent_id]}
    owned = [t for t in report.get("tasks", []) if str(t.get("owner_id", t.get("owner", ""))) in labels]
    if any(t.get("status") == "blocked" for t in owned):
        return "blocked"
    expired = False
    for task in report.get("tasks", []):
        if task.get("status") not in {"running", "reviewing"}:
            continue
        lease = task.get("lease") or {}
        worker = str(lease.get("worker_id", lease.get("worker", "")))
        if worker and worker not in labels:
            continue
        if not worker and task not in owned:
            continue
        expiry = lease.get("expires_at", task.get("lease_expires_at"))
        try:
            expiry = int(expiry)
        except (TypeError, ValueError):
            expired = True
            continue
        if expiry > now:
            return "running"
        expired = True
    return "expired" if expired else "idle"


def render(report: dict[str, Any], now: int | None = None) -> str:
    if not isinstance(report, dict):
        raise ValueError("Report must be an object")
    for key in ("agents", "tasks", "events", "attempts", "checkpoints", "usage"):
        if not isinstance(report.get(key, []), list):
            raise ValueError(f"Report field {key} must be an array")
    now = int(dt.datetime.now(dt.timezone.utc).timestamp()) if now is None else int(now)
    status_names = {"idle": "Ocioso", "running": "Executando", "expired": "Lease expirada", "blocked": "Bloqueado"}

    agents = []
    for agent_id, role in AGENT_ROLES.items():
        raw = next((a for a in report.get("agents", []) if str(a.get("id")) == agent_id), {})
        status = _status(report, agent_id, now)
        agents.append(f'<tr><td>{_safe(agent_id)}</td><td>{_safe(raw.get("role") or role)}</td>'
                      f'<td><span class="status {status}">{status_names[status]}</span></td>'
                      f'<td>{_safe(raw.get("execution_mode", "not reported"))}</td></tr>')

    def rows(items: list[dict[str, Any]], columns: tuple[tuple[str, str], ...]) -> str:
        if not items:
            return f'<tr><td colspan="{len(columns)}" class="empty">Nenhum registro</td></tr>'
        result = []
        for item in items:
            cells = "".join(f"<td>{_safe(item.get(key, ''))}</td>" for key, _ in columns)
            result.append(f"<tr>{cells}</tr>")
        return "".join(result)

    def table(title: str, key: str, columns: tuple[tuple[str, str], ...]) -> str:
        headings = "".join(f"<th>{_safe(label)}</th>" for _, label in columns)
        return (f'<section><h2>{_safe(title)}</h2><div class="scroll"><table><thead><tr>{headings}</tr></thead>'
                f'<tbody>{rows(report.get(key, []), columns)}</tbody></table></div></section>')

    task_fields = (("task_id", "Tarefa"), ("title", "Título"), ("owner", "Agente"), ("status", "Estado"), ("attempts", "Tentativas"))
    event_fields = (("created_at", "Data"), ("task_id", "Tarefa"), ("sender", "Origem"), ("recipient", "Destino"), ("kind", "Tipo"), ("content", "Conteúdo"))
    attempt_fields = (("attempt_id", "Tentativa"), ("task_id", "Tarefa"), ("agent_id", "Agente"), ("status", "Estado"), ("started_at", "Início"), ("finished_at", "Fim"))
    checkpoint_fields = (("task_id", "Tarefa"), ("sha256", "SHA-256"), ("created_at", "Data"), ("status", "Estado"))
    usage_fields = (("task_id", "Tarefa"), ("provider", "Provedor"), ("mode", "Modo"), ("input_tokens", "Tokens entrada"), ("output_tokens", "Tokens saída"), ("estimated_cost", "Custo estimado"))
    safety = report.get("safety", {})
    safety_html = "<pre>" + _safe(safety) + "</pre>"
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>VideoForge — Runtime multiagente</title><style>
:root{{color-scheme:dark;--bg:#10151d;--panel:#192330;--line:#344354;--text:#edf3fa;--muted:#a8b7c8;--accent:#72d6ba}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1440px;margin:auto;padding:28px}}h1{{margin:0}}h2{{font-size:1.15rem;margin:28px 0 10px}}p,.muted{{color:var(--muted)}}
section,.hero{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;margin-top:16px}}
.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:680px}}th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}}th{{color:var(--muted)}}
.status{{display:inline-block;padding:2px 9px;border-radius:99px;background:#344354}}.running{{background:#145b4a}}.blocked,.expired{{background:#713d28}}.idle{{background:#344354}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;margin:0;color:var(--muted)}}.empty{{text-align:center;color:var(--muted)}}
</style></head><body><main><div class="hero"><h1>VideoForge · Runtime multiagente</h1>
<p>Relatório somente leitura. Estados em execução exigem lease válido; agentes ausentes de uma execução aparecem ociosos. Este painel não concede aprovação humana.</p></div>
<section><h2>12 agentes</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Papel</th><th>Estado</th><th>Modo de execução</th></tr></thead><tbody>{''.join(agents)}</tbody></table></div></section>
{table('Tarefas', 'tasks', task_fields)}{table('Mensagens e eventos', 'events', event_fields)}
{table('Tentativas', 'attempts', attempt_fields)}{table('Checkpoints', 'checkpoints', checkpoint_fields)}
{table('Uso', 'usage', usage_fields)}<section><h2>Limites e segurança</h2>{safety_html}</section>
</main></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(report), encoding="utf-8")
    print(json.dumps({"dashboard": str(output), "agents": 12}, ensure_ascii=False))


if __name__ == "__main__":
    main()
