# 12 agentes — execução comprovada e limites (18/11/2026)

## Painel operacional verificavel (19/11/2026)

O painel unico e publico dos 12 agentes esta na [issue #91](https://github.com/HelioConde/VideoForge-IA/issues/91), atualizado pelo workflow [agent-operational-status.yml](../.github/workflows/agent-operational-status.yml) a cada 6 horas, no merge do novo workflow e por acionamento manual.

- A Action executa/retoma **quatro auditorias de fontes reais e deterministicas** dos especialistas 03, 04, 07 e 10, com revisor 12 e orquestrador tecnico 01. Cada entrega tem checksum, estado CAS persistente e relatorio no artifact. Nao envia modelos, nao gera midia e nao modifica imagens-mãe.
- O painel verifica separadamente o historico de 13 respostas **reais** Astra dos 12 agentes no run #44414591676. O historico nao equivale a chamadas recentes.
- Mostra **todos os 12 papeis**. Para os demais, registra expressamente ausencia de executor operacional comprovado; atribuicao na fila nao e trabalho executado.
- A fila de producao principal **continua** `mode=planning_only`, `dispatch_enabled=false`, para nao desbloquear a geracao ou publicacao automaticamente. O dispatcher tecnico e separado, com allowlist e limites.
- O painel da issue, o resumo da Action e os artifacts mostram links de execucao, estado de cada tarefa, aprovacao tecnica independente e bloqueios. Nenhum `success` do GitHub aprova por si so imagens, rigs, audio, MP4 ou YouTube.

Este painel resolve **transparencia e execucao limitada de auditorias**, nao a autonomia completa dos 12 agentes de producao. A segunda etapa sera ligar executores especificos a suas tarefas com provas, revisao e limites.


## Camadas de funcionamento

1. **Registro (12/12):** arquivos de instrução e IDs presentes.
2. **Diagnóstico de fontes (12 papéis):** o Agente 01 despacha dez auditorias específicas dos agentes 02–11; o Agente 12 revisa as fontes e as entregas. Cada auditoria tem checkpoint transacional e hash, sem usar IA ou produzir mídia.
3. **Piloto Astra textual real (13/13 executadas e verificadas):** no run #44414591676, 01 delegou, 02–11 responderam com Astra real, 12 revisou e 01 consolidou. Checkpoint transacional de QA concluído, sem produção audiovisual.
4. **Produção audiovisual (pendente):** geração de imagens, camadas RGBA, rig, animação, áudio e renderização não são habilitados por esse piloto textual.

## Diagnóstico com execução comprovada

- Workflow: https://github.com/HelioConde/VideoForge-IA/actions/runs/44402644867
- Artefato: agent-01-12-source-diagnostics-44402644867
- Dez diagnósticos específicos completos e revisados, repetição sem novas tarefas nem eventos.
- production_ready=false, model_calls=0, media_created=0, youtube_publications=0.
- O relatório role_diagnostic.readiness lista bloqueios por especialidade e SHA-256 da evidência.

## Preflight autenticado com o proxy real — 18/11/2026

- [GitHub Actions: preflight autenticado #44411070070](https://github.com/HelioConde/VideoForge-IA/actions/runs/44411070070) — **success**.
- O runner restaurou a sessão efêmera sem registrar tokens nos logs, iniciou o proxy e verificou autenticação por `GET /health` e o catálogo por `GET /v1/models`.
- `authenticated=true`, `accounts_configured=1`, `model_count=10`.
- **`gpt-6.2-astra` não apareceu nesse catálogo autenticado**. O modelo selecionado foi `gpt-6-astra`, motivo `fallback_primary_absent_from_catalog`. Essa disponibilidade pode mudar numa futura execução.
- `inference_requests=0`, `image_requests=0`, `youtube_publications=0`, `paid_inference_authorized=false`, `agent_communication_proven=false`.
- O smoke sem IA nesse mesmo runner confirmou: Agente 01 mock recebeu resposta, 12 mensagens, dois checkpoints e reabertura idempotente.
- **Limite do preflight isolado:** o catálogo autenticado não provava uma resposta real. Esse limite foi superado posteriormente pelo run real #44414591676, descrito abaixo.
- O preflight foi adicionado por meio da [PR #73](https://github.com/HelioConde/VideoForge-IA/pull/73), já integrada. Sua única execução automática adicional ocorre quando o próprio workflow de preflight for alterado na branch `main`; as demais execuções são manuais.

## Resposta real do Agente 01 — 18/11/2026

- [Execução #44412920056](https://github.com/HelioConde/VideoForge-IA/actions/runs/44412920056) — **success**; [PR #75](https://github.com/HelioConde/VideoForge-IA/pull/75) integrada.
- O Agente 01 recebeu uma mensagem de conexão e respondeu pela API do proxy com **`gpt-6-astra` real**, `llm_executed=true`, `simulated=false`, `status=received`.
- A resposta foi validada com o contrato do Agente 01, 844 tokens de entrada, 43 de saída; o artifact `authorized-agent-01-astra-ping-44412920056` guarda o relatório e o preflight sanitizados.
- A execução foi única e limitada a 500 tokens máximos de saída, sem retry, geração de imagens, mídia, alterações no episódio ou publicação no YouTube.
- **Não existe custo em USD confirmado**: o ping usou a opção do proxy sem tabela de tarifas, que não equivale a custo zero nem a limite monetário.
- **Status da época deste ping:** esta execução isolada comprovou somente o Agente 01. A posterior execução #44414591676 comprovou a cadeia textual real completa dos 12 papéis.
- O ciclo de 13 chamadas foi posteriormente autorizado e realizado com limites de chamadas/tokens, sem uma afirmação de teto financeiro em USD. Não confundir a prova do texto com a produção de mídia.

## Prova real dos 12 agentes com Astra — 18/11/2026

- [Execução GitHub Actions #44414591676](https://github.com/HelioConde/VideoForge-IA/actions/runs/44414591676) — **success**. [PR #77](https://github.com/HelioConde/VideoForge-IA/pull/77) integrada à `main`.
- **Modelo de execução: `gpt-6.2-astra`**, selecionado por GET autenticado nesse run. Diferentemente do preflight anterior, o modelo preferencial já estava disponível.
- **13 chamadas reais liquidadas (`settled`) de 13**, na ordem `01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 01`.
- **12/12 papéis participaram.** Os dez especialistas 02–11 retornaram análises textuais individuais. O Agente 12 devolveu dez decisões `supported`, marcou `technical_passed=true`, e o Agente 01 consolidou `needs_human_review`.
- **Evidência persistida:** `state/multi-agent-runtime`, arquivo `runtime/agent-12-text-roundtrip-v1.json`. Um checkpoint, tarefa `completed`, hashes por resposta e origem. Entrada: **13.443 tokens**; saída: **5.373 tokens** (total informado pelo proxy).
- O limite desse workflow foi de **13 chamadas** e **250.000 unidades conservadoras de reserva de tokens**, sem retry. Por falta de tabela tarifária do proxy, **nenhum teto ou custo em USD foi comprovado**; não equiparar isso a custo zero.
- `human_visual_approval=false`, `production_ready=false`, `youtube_publication=false`. Os dados textuais não demonstram camadas RGBA aprovadas, rig ou renderização do EP01.
- Próximos bloqueios citados pelo Diretor: continuidade espacial C07/C08 e direção de fuga; conferir referências e hashes de imagens; validação do rig/carrinho, animação temporal, áudio e MP4 único.
- Este sucesso comprova a **comunicação textual real entre os doze papéis**, não execução autônoma de suas ferramentas de produção audiovisual.

## Piloto de respostas reais do Astra

O workflow já está na branch padrão; a execução real continua manual e usa Agents - Codex proxy runtime (manual, gated), com:

- mode: codex_proxy_all_roles
- model: auto; priorizar gpt-6.2-astra e usar gpt-6-astra somente se o primeiro estiver ausente do catálogo autenticado.
- confirm: AUTHORIZE_THIRTEEN_ASTRA_CALLS
- budget_usd: de 0.01 até 0.25, com taxas explícitas input_usd_per_million e output_usd_per_million que correspondam ao serviço real.
- Secrets necessários: CODEX_PROXY_API_KEY e CODEX_PROXY_ACCOUNTS_JSON.

O cálculo é uma reserva por preços configurados, não uma fatura. O runner registra respostas verificáveis e impede repetição automática após resultado incerto. Nenhuma execução do piloto habilita ferramentas de produção ou publicação.

## Critérios reais de liberação do EP01

Antes de animar o carrinho são necessários: aprovação da Bíblia Visual, manifesto de camadas RGBA verdadeiro, rig com pivôs e contato mecânico validado, animação quadro a quadro e QA visual independente. O render final depende também do áudio e revisão humana.

Não criar assets falsos para desbloquear gates. A PR #71 foi integrada à `main` no commit `1265894`, mas nenhum procedimento acima autoriza publicação no YouTube ou comprova produção de mídia.
