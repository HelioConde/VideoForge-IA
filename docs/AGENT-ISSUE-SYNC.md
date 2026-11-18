# Sincronização controlada de propostas com GitHub Issues

O workflow `.github/workflows/agent-issue-sync.yml` converte propostas de `orchestrator/issue_proposals.py` em Issues, sem executar agentes.

## Operação
- Somente `workflow_dispatch` com `confirm=SYNC_PROPOSALS`.
- `limit` inteiro de 1 a 10 (padrão 3).
- Serialização por `concurrency.group` para evitar duas sincronizações simultâneas.
- Paginação de Issues abertas e fechadas; compara o marcador `<!-- videoforge-task:TASK_ID -->` e ignora as já existentes.
- Publica apenas título e corpo de proposta; não atribui tokens, não aciona Actions de produção e não aprova entregas.
- GitHub Actions job summary indica tarefas criadas e ignoradas.
- Checkpoint JSON de propostas arquivado por 14 dias.

## Limites e riscos
O marcador protege contra duplicação em execuções serializadas deste workflow, mas não é uma garantia transacional caso outras ferramentas criem a mesma Issue simultaneamente. Não apaga nem edita Issues existentes. Reexecutar pode criar novas propostas se tarefas diferentes forem adicionadas à fila.

O workflow precisa estar disponível para disparo manual no GitHub; workflows novos podem exigir presença na branch padrão para aparecer em Actions. **Não fazer merge da PR #71 sem revisão.**

## Estado de segurança
O EP01 permanece em revisão; Issues de propostas não significam trabalho executado. Nenhum modelo, proxy, upload de vídeo, geração visual ou aprovação humana é acionado por este workflow.
