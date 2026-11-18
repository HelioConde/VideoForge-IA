# Comunicação entre agentes — implementação inicial

## O que está implementado
- `orchestrator/agent_communication.py`: protocolo determinístico de mensagens com `event_id` idempotente, identificador de tarefa e encaminhamento 01 → 03 → 12 → 01.
- `tests/test_agent_communication.py`: teste de integridade e restrições.
- `.github/workflows/agent-communication-demo.yml`: execução manual segura. Por padrão **não cria Issue**; quando `publish_issue=true`, publica mensagens **simuladas** em uma Issue única por run, evitando duplicação de comentários no reprocessamento.
- Artifact de 14 dias com checkpoint JSON e mensagens.

## Executar
1. Abrir Actions → `Agents - comunicacao 01 03 12 (teste seguro)` → Run workflow.
2. Selecionar a branch `architecture/multi-agent-studio-v1`.
3. Manter `publish_issue=false` no primeiro teste; conferir logs e artifact.
4. Repetir com `publish_issue=true` para testar GitHub Issues e comentários. Isso cria conteúdo de teste no repositório, sem usar modelos ou proxy.

**Observação:** o GitHub pode exigir que o workflow exista na branch padrão para aparecer na lista de Actions e permitir disparo por `workflow_dispatch`. Se não aparecer, concluir revisão e merge da PR antes de executar. Nenhuma execução foi iniciada por esta alteração.

## Limites
Este piloto não envia mensagens para chats ChatGPT, não aciona LLMs e não executa especialistas reais. Os 12 chats são links de referência, não endpoints de automação. A expansão para 12 agentes requer executores autenticados e um barramento de tarefas, com política explícita de custos e permissões. Nunca colocar tokens em Issues ou artifacts.

## Proteções EP01
Não modificar imagens, vídeo, plano de continuidade, aprovação visual ou workflows existentes. O EP01 C07/C08 V2 permanece pendente de revisão humana. Não executar proxy nem publicar YouTube.

## Próximas etapas
1. Validar execução manual, artifact e Issue real.
2. Criar roteamento para todos os 12 papéis, retries idempotentes, leases por tarefa, autenticação e revisão.
3. Integrar executores reais **somente após aprovação do usuário e limites de custo**.
