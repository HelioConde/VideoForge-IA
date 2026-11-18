# Piloto automatizado 01 → 03 → 12

O workflow `.github/workflows/agents-01312-pilot.yml` inicia automaticamente no PR quando arquivos de orquestração ou do piloto mudam. Também aceita disparo manual quando disponível no GitHub Actions.

## Execução verificável

- Agente 01: seleciona a tarefa `EP01-C07-C08-V2-CONTINUITY-AUDIT` apenas se estiver pronta, atribuída ao diretor de cenas e sem bloqueios.
- Agente 03: lê o manifesto `CONTINUIDADE-C07-C08-V2.json` e confere nove IDs, sequência temporal dos frames, direção da fuga, responsabilidade pelo carrinho e proteção contra publicação.
- Agente 12: confere novamente o manifesto, a lista de tomadas, o SHA-256 da fonte e o hash do relatório produzido pelo Agente 03.
- Mensagens 01 → 03 → 12 → 01 são registradas em JSON; um checkpoint técnico com status `needs_review` é arquivado como artifact de GitHub Actions.

## Limites

É execução automática **determinística**, não chamada a um modelo de linguagem. Não analisa pixels nem frames do MP4. Passar nos testes significa apenas que o manifesto passou na validação técnica implementada; não aprova arte, montagem, roteiro, MP4 ou episódio. O checkpoint de execução fica no artifact; a fila de produção não é modificada.

O workflow usa somente `contents: read`, não possui permissão para criar Issues, não usa secrets, não aciona proxy nem YouTube. Não publica, regenera ou altera assets do EP01.

## Próximos passos

1. Confirmar a execução do workflow e o artifact.
2. Acrescentar processamento de tarefas por ID, mantendo os checks específicos para cada papel.
3. Conectar persistência transacional para leases/checkpoints e comunicação por Issues.
4. Somente depois considerar executores LLM, com limites explícitos de custo e aprovação.
