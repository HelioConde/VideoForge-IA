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

## Piloto de respostas reais do Astra

Após a integração do workflow à branch padrão, a execução manual usa Agents - Codex proxy runtime (manual, gated), com:

- mode: codex_proxy_all_roles
- model: auto; priorizar gpt-6.2-astra e usar gpt-6-astra somente se o primeiro estiver ausente do catálogo autenticado.
- confirm: AUTHORIZE_THIRTEEN_ASTRA_CALLS
- budget_usd: de 0.01 até 0.25, com taxas explícitas input_usd_per_million e output_usd_per_million que correspondam ao serviço real.
- Secrets necessários: CODEX_PROXY_API_KEY e CODEX_PROXY_ACCOUNTS_JSON.

O cálculo é uma reserva por preços configurados, não uma fatura. O runner registra respostas verificáveis e impede repetição automática após resultado incerto. Nenhuma execução do piloto habilita ferramentas de produção ou publicação.

## Critérios reais de liberação do EP01

Antes de animar o carrinho são necessários: aprovação da Bíblia Visual, manifesto de camadas RGBA verdadeiro, rig com pivôs e contato mecânico validado, animação quadro a quadro e QA visual independente. O render final depende também do áudio e revisão humana.

Não criar assets falsos para desbloquear gates. A PR #71 continua em rascunho; nenhum procedimento acima autoriza publicação no YouTube.
