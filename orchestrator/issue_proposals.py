#!/usr/bin/env python3
"""Prepare bounded GitHub Issue proposals from the read-only dispatch plan.

No GitHub API calls, model calls, file mutations or publication.
"""
import argparse
import json
from pathlib import Path
from dispatch_plan import plan
from agent_bus import fingerprint

def proposals(queue_path, limit=10):
    if not 1 <= limit <= 25:
        raise ValueError("limit must be between 1 and 25")
    dispatch = plan(queue_path)
    queue = json.loads(Path(queue_path).read_text(encoding="utf-8"))
    by_id = {t["task_id"]: t for t in queue["tasks"]}
    result = []
    for candidate in dispatch["candidates"][:limit]:
        task = by_id[candidate["task_id"]]
        key = fingerprint({"task_id": task["task_id"], "queue": dispatch["source_sha256"]})[:20]
        body = (
            "<!-- videoforge-task:" + task["task_id"] + " -->\n"
            "## Proposta de tarefa (não executada)\n"
            f"- **task_id:** `{task['task_id']}`\n"
            f"- **Agente responsável:** {candidate['agent_id']} / {candidate['owner']}\n"
            f"- **Revisor independente:** {candidate.get('reviewer') or 'a definir'}\n"
            f"- **Prioridade:** {candidate.get('priority') or 'não definida'}\n"
            f"- **Checkpoint:** `{key}`\n"
            "- **Status:** proposta; nenhuma IA executada\n"
            "- **EP01:** nenhuma aprovação automática; não modificar assets aprovados\n"
            "- **Restrições:** sem proxy, sem YouTube, sem publicação\n\n"
            "### Critérios de aceite\n"
            + ("\n".join("- " + str(x) for x in task.get("acceptance_criteria", []))
               or "- Revisão humana necessária antes de qualquer execução") + "\n"
        )
        result.append({"task_id": task["task_id"], "marker": f"videoforge-task:{task['task_id']}",
                       "title": f"[AGENT TASK] {task['task_id']}", "body": body,
                       "owner": candidate["owner"], "agent_id": candidate["agent_id"],
                       "execute": False, "checkpoint": key})
    return {"schema_version": 1, "mode": "proposal_only", "issue_count": len(result),
            "issues": result, "github_writes": 0, "ai_calls": 0, "proxy_calls": 0,
            "youtube_publications": 0, "ep01_visual_approval": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default="orchestrator/tasks.json")
    parser.add_argument("--output", default="")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    result = proposals(args.queue, args.limit)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(payload, encoding="utf-8")
    print(payload)

if __name__ == "__main__":
    main()
