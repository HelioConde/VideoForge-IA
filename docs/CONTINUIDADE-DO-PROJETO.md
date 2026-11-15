# Protocolo de continuidade — VideoForge-IA

**Objetivo:** qualquer agente ou conversa deve continuar o último trabalho real, sem reconstruir o projeto do zero.

## Fonte de verdade

- `main` é a referência de fatos concluídos. Uma alteração em branch/PR ainda aberta não é estado consolidado.
- Para um vídeo, ler **primeiro** `canal/<id>/videos/<video-id>/ESTADO-ATUAL.md`, depois `HISTORICO-DESENVOLVIMENTO.md` e `estado-atual.json` quando existirem; se ainda não existirem, criá-los como parte do próximo trabalho.
- Conferir `AGENTS.md` e o manual técnico específico ANTES de editar/renderizar. Não deduzir aprovação a partir de logs ou de um SHA anotado.
- Cada canal mantém seus próprios vídeos, fontes, histórico e QA. Não usar branches antigas como fonte final se já houve port para `main`.

## Encerramento obrigatório de cada etapa

1. Confirmar o resultado **real**: código alterado, commit na `main`, testes/workflows (ID e `success/failure/skipped`), artifact, SHA e presença dos bytes. Se somente PR, registrar `nao_integrado`.
2. Atualizar `ESTADO-ATUAL.md` com **feito / teste técnico / pendente / bloqueado**, o **próximo passo concreto** e o motivo de qualquer bloqueio.
3. Acrescentar evento datado ao `HISTORICO-DESENVOLVIMENTO.md` (sem reescrever entradas antigas) e sincronizar campos centrais em `estado-atual.json`.
4. Integrar essas alterações de documentação **na mesma mudança que chega à `main`**. Se a execução não pôde fazer merge, declarar isso e não afirmar que foi salvo em `main`.
5. **Antes de nova execução**, verificar estado atualizado e artefatos já existentes. Não recriar vídeos/rigs/camadas já produzidos; reparar somente o que estiver pendente.
6. Nunca armazenar credenciais, tokens, imagens com dados privados ou informações sensíveis nos checkpoints. Links de artifacts do Actions expiram; separar sempre `artifact_temporario` de `binario_permanente_no_repo`.

## Episódio em desenvolvimento

[Alchemy Lab — MMORPG Conquiste a Princesa EP01](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md) é o ponto atual. Os trabalhos de C01 e C12 são distintos e ambos relevantes. O estado consolidado registra explicitamente os MP4s técnicos e os originais ausentes.
