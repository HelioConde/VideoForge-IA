"""Truthful, verifiable public reports for all twelve VideoForge roles.

Only a persisted specialist result plus independent QA counts as executed work.
An old real Astra pilot never implies ongoing inference, and deterministic
audits never imply image, rig, sound, video or publication operations.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from .agent_bus import ROLES
from .runtime import report as runtime_report
from .runtime_store import Store

REPO = "HelioConde/VideoForge-IA"
DASHBOARD_ISSUE = 91
OLD_ASTRA_RUN = 44414591676
SAFE_ROLES = {"03", "04", "07", "10"}
NAMES = {
    "01":"Diretor Geral", "02":"Roteirista", "03":"Diretor de Cenas",
    "04":"Diretor de Arte", "05":"Gerador Visual", "06":"Separador de Camadas",
    "07":"Especialista em Rig", "08":"Animador", "09":"Diretor de Camera",
    "10":"Especialista em Audio", "11":"Montador", "12":"Supervisor QA",
}

def historical_proof(data):
    if data is None:
        return {"validated":False, "calls":0, "model":None}
    from .agent_live_roundtrip import validate_live_roundtrip_result
    expected = ["01"] + [f"{i:02d}" for i in range(2,12)] + ["12","01"]
    calls = data.get("usage",[])
    tasks = data.get("tasks",[])
    if (len(calls)!=13 or len(tasks)!=1
            or [x.get("agent_id") for x in calls]!=expected
            or any(x.get("state")!="settled" for x in calls)):
        raise ValueError("Unverified real Astra role history")
    model=tasks[0].get("model")
    if model not in ("gpt-6.2-astra","gpt-6-astra"):
        raise ValueError("Unverified historical model identity")
    if validate_live_roundtrip_result(data, model)!="needs_human_review":
        raise ValueError("Historical Astra QA was not completed")
    return {"validated":True, "calls":13, "model":model}

def make_status(dispatch,queue,historical=None,*,run_id,now):
    if not isinstance(run_id,int) or run_id<1 or not isinstance(now,str) or not now:
        raise ValueError("Real run ID/time required")
    safe=dispatch.get("dispatch",{})
    gates=dispatch.get("safety",{})
    if (safe.get("contract")!="deterministic-safe-dispatch-v1"
            or safe.get("model_inference_requests")!=0
            or safe.get("image_requests")!=0
            or safe.get("youtube_publications")!=0
            or gates.get("human_visual_approval") is not False
            or gates.get("production_tools_enabled") is not False
            or queue.get("mode")!="planning_only"
            or queue.get("dispatch_enabled") is not False):
        raise ValueError("Unsafe or mislabeled source-audit dispatcher")
    tasks=dispatch.get("tasks")
    cps=dispatch.get("checkpoints")
    qtasks=queue.get("tasks")
    if not all(isinstance(x,list) for x in (tasks,cps,qtasks)):
        raise ValueError("Missing queue, task or checkpoint arrays")
    queue_by_id={t["task_id"]:t for t in qtasks}
    if len(queue_by_id)!=len(qtasks):
        raise ValueError("Duplicate source task IDs")
    proofs={x["task_id"]:x for x in cps}
    role_executions={}
    completed=[]
    for task in tasks:
        owner=task.get("owner")
        source_id=task.get("source_task_id")
        if owner not in SAFE_ROLES or source_id not in queue_by_id:
            raise ValueError("Unexpected dispatched agent/task")
        if queue_by_id[source_id].get("owner")!=ROLES[owner]:
            raise ValueError("Source owner does not match executed owner")
        if task.get("status")=="completed":
            cp=proofs.get(task["task_id"])
            review=(cp or {}).get("review",{})
            if (not cp or cp.get("result_sha256")!=task.get("result_sha256")
                    or cp.get("human_visual_approval") is not False
                    or cp.get("scope")!="read_only_technical_audit"
                    or review.get("agent_id")!="12"
                    or review.get("technical_passed") is not True):
                raise ValueError("Technical completion claimed without independent QA")
            completed.append(source_id)
            desc="Auditoria de fonte concluida; QA tecnico do Agente 12"
            proof=cp["sha256"]
        else:
            desc="Tarefa registrada, sem entrega tecnica validada"
            proof=None
        role_executions[owner]={
            "source_task_id":source_id, "result":desc,
            "status":task.get("status"), "checkpoint_sha256":proof}
    past=historical_proof(historical)
    roles=[]
    for role_id in sorted(ROLES):
        plan=[{"task_id":q["task_id"],"status":q.get("status"),
               "blocked_by":q.get("blocked_by",[])} for q in qtasks
              if q.get("owner")==ROLES[role_id]]
        row={
            "id":role_id,"name":NAMES[role_id],
            "mode":"sem executor de producao conectado",
            "current_activity":"sem execucao recente comprovada",
            "source_task_id":None,"checkpoint_sha256":None,
            "reviewed_visual_media":False,"media_produced":False,
            "historical_astra_response":past["validated"],
            "queue_tasks":plan,
        }
        if role_id in role_executions:
            result=role_executions[role_id]
            row["mode"]="auditoria deterministica; nenhuma chamada Astra"
            row["current_activity"]=result["result"]
            row["source_task_id"]=result["source_task_id"]
            row["checkpoint_sha256"]=result["checkpoint_sha256"]
        elif role_id=="01" and completed:
            row["mode"]="orquestracao tecnica automatizada, sem IA"
            row["current_activity"]="Despachou quatro auditorias tecnicas limitadas"
        elif role_id=="12" and completed:
            row["mode"]="QA tecnico deterministico, nao visual"
            row["current_activity"]=f"Revisou {len(completed)} resultados tecnicos"
        roles.append(row)
    counts={}
    for q in qtasks:
        s=q.get("status","desconhecido")
        counts[s]=counts.get(s,0)+1
    return {
        "schema_version":1,"repository":REPO,"issue_number":DASHBOARD_ISSUE,
        "updated_utc":now,"github_run_id":run_id,
        "run_url":f"https://github.com/{REPO}/actions/runs/{run_id}",
        "historical_astra":past,
        "technical_dispatch":{
            "source_audits_completed":len(completed),
            "source_ids_completed":sorted(completed),
            "new_model_calls":0,"media_tools_executed":False,
            "state_sha256":dispatch["state_sha256"],
            "max_tasks_per_dispatch":4,
        },
        "queue":{"mode":"planning_only","dispatch_enabled":False,
                 "size":len(qtasks),"statuses":counts},
        "agents":roles,
        "human_visual_approval":False,"rig_ready":False,
        "mp4_final_ready":False,"youtube_publications":0,
    }

def render_markdown(data):
    q=chr(96)
    link=data["run_url"]
    result=[
        "<!-- videoforge-agent-dashboard:v1 -->",
        "# Painel operacional dos 12 agentes — VideoForge-IA",
        "",
        f"**Atualizado:** {data['updated_utc']} UTC. "
        f"[GitHub Actions #{data['github_run_id']}]({link}).",
        "",
        "**O que esta funcionando:** auditorias de arquivos e QA tecnico automatizado, "
        "com registros persistentes. **O que nao esta funcionando ainda:** "
        "delegacao continua via Astra de todas as tarefas de arte, rig, audio e video.",
        "",
        f"- Astra real: **{data['historical_astra']['calls']}/13 respostas** "
        f"na [execucao historica #{OLD_ASTRA_RUN}]"
        f"(https://github.com/{REPO}/actions/runs/{OLD_ASTRA_RUN}); "
        "**nao sao novas respostas deste ciclo**.",
        f"- Auditorias de fonte realmente executadas com QA independente: "
        f"**{data['technical_dispatch']['source_audits_completed']}/4**.",
        f"- Fila principal: {q}planning_only{q} e {q}dispatch_enabled=false{q}; "
        "o despachante tecnico limitado e separado.",
        "- Modelo chamado neste ciclo: **0 vezes**. Operacoes de producao de midia "
        "pelos agentes: **0 verificadas**. Aprovacoes visuais automaticas: **0**.",
        "",
        "## Atividade individual (evidencias, nao simulacao)",
        "",
        "| Agente | Funcao | Trabalho comprovado | Tarefa / checkpoint |",
        "|---|---|---|---|",
    ]
    for a in data["agents"]:
        ref=a["source_task_id"] or "Nenhuma nesta esteira"
        suffix= f" ({q}{a['checkpoint_sha256'][:12]}{q})" if a["checkpoint_sha256"] else ""
        result.append(f"| **{a['id']}** | {a['name']} | "
                      f"{a['current_activity']} | {ref}{suffix} |")
    result.extend(["", "## Fila real de trabalho e bloqueios", "",
                   "| Tarefa | Responsavel | Estado original | Dependencias |",
                   "|---|---|---|---|"])
    for a in data["agents"]:
        for task in a["queue_tasks"]:
            deps=", ".join(task["blocked_by"]) or "—"
            result.append(f"| {q}{task['task_id']}{q} | "
                          f"{a['id']} — {a['name']} | "
                          f"{task['status']} | {deps} |")
    result += ["", "## Proximas correcoes necessarias", "",
        "1. Integrar um executor real que permita ao Agente 01 distribuir tarefas "
        "de producao e receber resultados assinados; nenhuma tarefa so pelo nome "
        "do agente significa trabalho executado.",
        "2. Vincular agentes 02, 05, 06, 08, 09 e 11 a ferramentas reais e "
        "checkpoints. Os agentes 03, 04, 07 e 10 fazem somente auditorias "
        "tecnicas nesta etapa.",
        "3. Liberar cada camada, rig e MP4 apenas depois de QA independente e "
        "aprovacao humana quando necessaria; nunca publicar YouTube por este workflow.",
        "",
        f"**SHA do estado persistente:** {q}"
        f"{data['technical_dispatch']['state_sha256']}{q}.",
        f"**Relatorio integral:** [artifact da Action]({link}).",
        "",
        "> Este painel nao e comprovante de 12 agentes executando IA "
        "continuamente, de animacao finalizada ou de episodio aprovado.",
        ""]
    return "\n".join(result)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dispatch-report",type=Path,required=True)
    p.add_argument("--queue",type=Path,default=Path("orchestrator/tasks.json"))
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--run-id",type=int,required=True)
    p.add_argument("--read-astra-history",action="store_true")
    args=p.parse_args()
    dispatch=json.loads(args.dispatch_report.read_text(encoding="utf-8"))
    queue=json.loads(args.queue.read_text(encoding="utf-8"))
    historical=None
    if args.read_astra_history:
        from .github_state import GitHubState
        import tempfile
        snap=GitHubState(path="runtime/agent-12-text-roundtrip-v1.json").load()
        if snap is None:
            raise ValueError("Missing historical real Astra evidence")
        with tempfile.TemporaryDirectory(prefix="vf-agent-status-") as temp:
            store=Store(Path(temp)/"astra.sqlite")
            try:
                store.import_snapshot(snap)
                historical=runtime_report(store)
            finally:
                store.close()
    status=make_status(dispatch,queue,historical,
          run_id=args.run_id,now=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    out=args.output_dir
    out.mkdir(parents=True,exist_ok=True)
    (out/"agent-status.json").write_text(
        json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    markdown=render_markdown(status)
    (out/"agent-status.md").write_text(markdown,encoding="utf-8")
    (out/"issue-body.md").write_text(markdown,encoding="utf-8")
    print(json.dumps({"roles":12,
                      "audits":status["technical_dispatch"]["source_audits_completed"],
                      "historical_calls":status["historical_astra"]["calls"],
                      "new_model_calls":0,"media_published":0}))

if __name__=="__main__":
    main()
