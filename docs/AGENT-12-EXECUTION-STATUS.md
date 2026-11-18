# 12 agentes — execução comprovada e limites (18/11/2026)

## Camadas de funcionamento

1. **Registro (12/12):** arquivos de instrução e IDs presentes.
2. **Diagnóstico de fontes (12 papéis):** o Agente 01 despacha dez auditorias específicas dos agentes 02–11; o Agente 12 revisa as fontes e as entregas. Cada auditoria tem checkpoint transacional e hash, sem usar IA ou produzir mídia.
3. **Piloto Astra textual (implementado, ainda não executado com o modelo real):** o modo manual codex_proxy_all_roles oferece 13 inferências reais: 01 delega dez tarefas; 02–11 respondem; 12 faz QA; 01 consolida. Requer autorização explícita, orçamento configurado e secrets.
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
- **Limite de evidência:** catálogo e credenciais válidos **não** provam uma resposta real do Astra. Só um `workflow_dispatch` autorizado e com orçamento, contendo respostas e logs reais dos 12 papéis, poderá comprovar essa etapa.
- O preflight foi adicionado por meio da [PR #73](https://github.com/HelioConde/VideoForge-IA/pull/73), já integrada. Sua única execução automática adicional ocorre quando o próprio workflow de preflight for alterado na branch `main`; as demais execuções são manuais.

## Resposta real do Agente 01 — 18/11/2026

- [Execução #44412920056](https://github.com/HelioConde/VideoForge-IA/actions/runs/44412920056) — **success**; [PR #75](https://github.com/HelioConde/VideoForge-IA/pull/75) integrada.
- O Agente 01 recebeu uma mensagem de conexão e respondeu pela API do proxy com **`gpt-6-astra` real**, `llm_executed=true`, `simulated=false`, `status=received`.
- A resposta foi validada com o contrato do Agente 01, 844 tokens de entrada, 43 de saída; o artifact `authorized-agent-01-astra-ping-44412920056` guarda o relatório e o preflight sanitizados.
- A execução foi única e limitada a 500 tokens máximos de saída, sem retry, geração de imagens, mídia, alterações no episódio ou publicação no YouTube.
- **Não existe custo em USD confirmado**: o ping usou a opção do proxy sem tabela de tarifas, que não equivale a custo zero nem a limite monetário.
- **Status de IA real por papel:** Agente 01 comprovado para uma resposta de conectividade. Agentes 02–11 e o QA real do Agente 12 ainda **não foram comprovados** nesta cadeia.
- O ciclo de 13 chamadas só deve prosseguir com tarifa confiável e limite de gasto explícito (`budget_usd` e taxas de tokens), sem estimar preços inventados ou transformar uma chamada bem-sucedida em prova da produção audiovisual.

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
