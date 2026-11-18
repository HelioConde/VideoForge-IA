# Runtime multiagente — implementação de 18/11/2026

Continuação da PR #71, sem merge e sem chamadas pagas. O EP01 é fonte somente leitura. Os chats em `agents/chat-directory.json` continuam sendo referências, nunca endpoints de API.

## O que existe de fato

`orchestrator/runtime.py` seleciona automaticamente duas auditorias derivadas da fila existente, carrega as instruções completas de `agents/<role>/AGENT.md`, executa o especialista, encaminha resultado ao revisor e registra checkpoint pelo coordenador. A seleção e as ferramentas são controladas por código; respostas de modelo não executam shell nem escolhem APIs arbitrárias.

- **Determinístico:** Python inspeciona estrutura/timing/regras declaradas do manifesto (03) e inventário de referências (04). Revisor 12 reabre as fontes e verifica o relatório independentemente. Isso não inspeciona pixels.
- **Mock:** adiciona respostas estruturadas determinísticas para testar o contrato de modelo, sem rede. Não são agentes de IA reais.
- **OpenAI:** adaptador real de texto Responses, configurável, com instruções completas para 01 → especialista → 12 → 01. Implementado e testado com transporte controlado; nenhuma inferência real autorizada/executada nesta entrega.
- **12 papéis:** registro, instruções, roteamento de análise textual somente leitura e revisão com responsável distinto testados para todos. Geração visual, separação de camadas, rig, animação, áudio e render de produção **não estão habilitados**. Infraestrutura comum não significa 12 especialistas produzindo mídia autonomamente.

Os hashes legados da fila não coincidem com os bytes atuais de alguns manifestos. As novas tarefas têm IDs `*-MANIFEST-<hash>` e escopo menor: auditoria de metadados com SHA-256 atual. Registram o hash antigo como achado; não reescrevem a fila original, não concluem seus critérios de inspeção visual e não aprovam o episódio.

## Persistência e concorrência

`runtime_store.py` usa SQLite (`BEGIN IMMEDIATE`, WAL, synchronous FULL). Estado, revisão, lease, tentativa, mensagem, evidência e checkpoint são escritos em transações. Duas instâncias competindo pelo mesmo arquivo não recebem a mesma tentativa de produção. Owner e reviewer distintos são obrigatórios. Leases expiradas não podem entregar resultados; recuperação usa backoff limitado e até três tentativas por fase, depois dead-letter queue.

O backend remoto `github_state.py` guarda snapshots JSON em `state/multi-agent-runtime:runtime/state.json`, usando o SHA do blob exigido pela Contents API para compare-and-swap. A criação da branch/arquivo requer `--initialize-store`. Cada claim e reserva é persistido remotamente **antes** de retornar ao executor. Conflito interrompe a instância e exige recarregar; comparação em memória não é considerada escrita atômica. O SQLite temporário do runner é descartável: o snapshot remoto é canônico nesse modo.

Se o processo cair após qualquer chamada paga, inclusive uma resposta com usage já recebido, a tentativa expirada fica bloqueada para reconciliação manual. Não se promete exactly-once da API externa: não há replay automático quando seu resultado pode ter sido perdido. A reserva de orçamento é durável, compartilhada entre tarefas e não é devolvida automaticamente em timeout/429. Sem backoff/retry de inferência paga.

O snapshot contém histórico completo e tem limite de tamanho explícito; não é um banco ilimitado. Esse piloto atende baixo volume. Para produção concorrente em escala, migrar o mesmo contrato para um banco transacional gerenciado, com política de retenção e autorização de custo, antes de aumentar a carga. Runners locais devem compartilhar o mesmo arquivo SQLite; arquivos independentes não coordenam workers entre si.

## Executar sem IA paga

Na raiz do repositório:

```sh
python -m orchestrator.runtime --db output/agent-runtime/state.sqlite --mode mock --max-tasks 2 --output output/agent-runtime/report.json
python -m orchestrator.runtime --db output/agent-runtime/state.sqlite --mode mock --max-tasks 2 --output output/agent-runtime/report.json
python -m orchestrator.dashboard --report output/agent-runtime/report.json --output output/agent-runtime/index.html
python -m unittest discover -s tests -p 'test_runtime*.py' -v
```

A segunda execução deve manter o SHA de estado quando não existe trabalho novo. O HTML é um snapshot, não uma conexão ao vivo: mostra 12 papéis, tarefas, mensagens, tentativas, checkpoints e consumo. `running` exige lease válida; papéis cadastrados não aparecem como agentes ativos. Os relatórios diferenciam modo mock, execução Python, chamadas LLM, QA técnico e ausência de aprovação humana.

Com `GITHUB_REPOSITORY` e `GITHUB_TOKEN` já configurados de modo protegido:

```sh
python -m orchestrator.runtime --db output/agent-runtime/unused.sqlite --github-state --initialize-store --mode mock --max-tasks 2 --output output/agent-runtime/remote-report.json
# Em outro processo, sem initialize-store:
python -m orchestrator.runtime --db output/agent-runtime/unused.sqlite --github-state --mode mock --max-tasks 2 --output output/agent-runtime/remote-report-reopened.json
```

Não imprimir a chave. O token precisa escrever conteúdo apenas no repositório escolhido. A branch principal e a branch da PR não são bancos de estado.

## API real: preparada, desligada

Template: `config/agent-runtime.env.example`. Defaults: `AI_ENABLED=false`, `PAID_CALLS_ENABLED=false`, `IMAGE_GENERATION_ENABLED=false`, `YOUTUBE_PUBLICATION_ENABLED=false`. Modelo e preços não têm defaults inventados.

Depois de autorização explícita, configurar `AI_MODEL`, `OPENAI_API_KEY`, `AI_INPUT_USD_PER_MILLION`, `AI_OUTPUT_USD_PER_MILLION`, habilitar os dois gates de texto e passar os três limites positivos `--budget-usd`, `--max-tokens`, `--max-calls`. Usar `--mode openai`. Uma auditoria completa usa até quatro respostas (01, especialista, revisor, 01). Falta de configuração bloqueia a tarefa, sem fallback silencioso para mock. O workflow incluído mantém esses gates desligados, inclusive se `openai` for selecionado.

Estimativas usam bytes de entrada mais margem de protocolo, teto de saída e preços explicitamente configurados. São reservas conservadoras **não uma garantia do faturamento do provedor**. Usage observado é registrado quando retornado; valor USD é cálculo pelos preços configurados, não fatura. Ausência de usage é desconhecida, nunca custo zero. Timeout máximo do adaptador: 120 s; runtime usa 60 s. Saída: 1.200 tokens por resposta no piloto. Inputs limitados; chaves e corpos de erro não são registrados. Redirects de HTTP são recusados.

O modo `codex_proxy` exige também `CODEX_PROXY_TEXT_AUTHORIZED=true`, `CODEX_PROXY_BASE_URL`, `CODEX_PROXY_API_KEY`, modelo e preços. A rota compatível é documentada no projeto existente, mas a integração de texto com o proxy não foi validada em rede nesta entrega. Ele não é a API oficial da OpenAI.

## Actions e Issues

`.github/workflows/agent-runtime.yml` executa testes e piloto mock em PR, com `contents:read`, sem secrets de modelos. O job manual usa limites de tarefas, timeout e concurrency group. Não adiciona schedule. A definição de workflow manual precisa estar disponível na branch padrão para `workflow_dispatch`; **não fazer merge só para contornar isso**. A checagem de PR é o caminho de verificação antes do merge.

Issues são uma projeção opcional. `--github-state --publish-checkpoints --publish-only --issue-number N` não executa agentes; publica checkpoints existentes com intenção durável antes do POST e marcador pelo SHA. Um POST de resultado desconhecido não é repetido: próxima execução reconcilia pelo marcador ou mantém pendência manual. Não cria Issues nem mensagens por padrão. Publicação exige permissão adicional `issues:write`; comentários não substituem o armazenamento CAS. Nenhum vídeo é publicado.

## Fontes e limites técnicos

- [OpenAI Responses create](https://platform.openai.com/docs/api-reference/responses/create): endpoint oficial do adaptador.
- [GitHub Contents API](https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents): atualização com SHA e conflitos.
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html): serialização de gravações via BEGIN IMMEDIATE.
- Componentes anteriores reutilizados: `agent_bus.ROLES/fingerprint`, helpers de `task_leases`; `dispatch_plan`, `recovery_plan` e `state_transitions` permanecem exemplos/propostas puros, não substituem o Store transacional. Reconciliação e propostas de Issue antigas continuam separadas do outbox novo.

EP01, Bíblia Visual, imagens e workflows de produção permanecem intactos. Continuidade física, anatomia, aprovação criativa e mídia final continuam dependendo de QA visual e decisão humana. Este runtime pode funcionar sem o chat aberto quando executado por CLI/Actions; nenhum serviço contínuo ou agendamento de produção foi ativado.


## Codex proxy: verificação segura, sem inferência (18/11/2026)

- A integração foi conferida com o cliente `HelioConde/codex/proxy_ai`: o formato de texto usa `POST /v1/responses` e `stream: false`; o adaptador do runtime agora declara explicitamente `stream: false`.
- `orchestrator/proxy_preflight.py` faz **apenas** `GET /health` e `GET /v1/models`, com chave protegida, resposta limitada e redirects recusados. O relatório contém contagem de modelos e contas, nunca URLs, chaves ou prompts. **Não prova comunicação de IA**.
- `tests/test_runtime_proxy_contract.py` testa offline o handshake do proxy e o fluxo 01→03→12→01 com respostas HTTP **falsas**, sem nenhum socket externo. O teste valida a transferência de resultados, QA e checkpoints; não representa uso real de modelo.
- Workflow `.github/workflows/agent-proxy-preflight.yml`: execução **manual**, reutiliza a mesma configuração de geração de imagens do VideoForge-IA: `CODEX_PROXY_API_KEY` + `CODEX_PROXY_ACCOUNTS_JSON` para iniciar o contêiner efêmero fixado no GHCR (`127.0.0.1:18080`), ou `CODEX_PROXY_BASE_URL` + chave para origem persistente HTTPS. Não é necessário `CODEX_PROXY_BASE_URL` no modo efêmero. Os Secrets de `codex` não são compartilhados automaticamente com este repositório. O job mantém IA/publicação desligadas e limpa o contêiner/arquivo privado ao terminar. A definição de workflow manual precisa existir na branch padrão para ser acionada manualmente; não fazer merge somente para isso.
- Para execução local autorizada (somente GET): `python -m orchestrator.proxy_preflight --output output/agent-runtime/proxy-preflight.json`. Use somente URL HTTPS autorizada ou loopback local fixo; não envie credenciais ao repositório.
- Se o proxy só atende em `127.0.0.1:18080` no computador do usuário, runners hospedados do GitHub não terão acesso a esse processo externo. Entretanto, quando `CODEX_PROXY_ACCOUNTS_JSON` está configurado, **o próprio job inicia um novo contêiner efêmero no runner**, e o loopback passa a funcionar dentro do job. Não expor contas, cookies, tokens ou proxy sem TLS e autenticação.
- O serviço descrito em `HelioConde/codex/docs/08-proxy-ia-texto-codex.md` usa integração upstream não oficial: disponibilidade, permissões e cotas precisam ser confirmadas pelo responsável. Nunca presumir acesso gratuito ilimitado.
- **Preflight real aprovado em 18/11/2026:** [execução #44308778166](https://github.com/HelioConde/VideoForge-IA/actions/runs/44308778166), usando Secrets existentes do VideoForge-IA e o mesmo contêiner efêmero da geração de imagens. Verificados: `/health/live`, autenticação `/health` (`accounts_configured=1`), `/v1/models` (`model_count=10`). Artifact sanitizado `proxy-preflight-44308778166`. Contabilizados `inference_requests=0`, `image_requests=0`, `youtube_publications=0`; **o modelo não foi consultado para gerar texto**. O gatilho temporário por PR usado exclusivamente nesse diagnóstico foi retirado após o sucesso, deixando novamente o workflow apenas manual.
- **Próximo marco pendente:** iniciar esse mesmo contêiner no job de runtime dos agentes e executar uma conversa REAL 01→03→12→01, somente com autorização específica para inferência, controle de custos/cota, teto de chamadas e evidência de usage. O funcionamento de `/health` e `/v1/models` **não comprova** que `/v1/responses` está autorizado/disponível. Nenhuma chamada de texto/imagem deve ser iniciada pelo preflight ou por CI de PR.


## Runtime Codex pelo contêiner efêmero de imagens — implantação segura

Novo workflow: `.github/workflows/agent-proxy-runtime.yml`. Diferentemente de `.github/workflows/agent-runtime.yml`, ele monta o **mesmo proxy já usado nas imagens**, a partir do par de Secrets já disponível `CODEX_PROXY_API_KEY` + `CODEX_PROXY_ACCOUNTS_JSON`, dentro do runner. Não depende de URL HTTPS persistente. O contêiner local não é exportado para a rede pública. Faz `GET /health` e `GET /v1/models` antes de usar o runtime.

**Na PR:** somente job `pr-offline-contract`, com respostas HTTP simuladas, sem secrets de modelo e sem chamadas reais ao proxy. O contrato 01→03→12→01 é testado, mas **não é inferência de IA**.

**Execução manual futura (após disponibilizar workflow na branch padrão, sem merge automático):**
- Modo `mock_with_proxy` (padrão): inicia o proxy, autentica em GET e executa auditoria de metadados com 01→03→12→01 via `MockProvider`, registrando mensagens/checkpoint SQLite. `confirm=NO_INFERENCE`, sem consumo de inferência.
- Modo `codex_proxy_ping`: primeiro contato com o **Agente 01**, limitado a uma única solicitação de texto e resposta JSON validada (`agent_id=01`, `status=received`). Usa as instruções oficiais de `agents/<role>/AGENT.md`, sem ferramentas de produção, sem retries. Requer autorização explícita, modelo presente no catálogo e orçamento estimado de 0,01–0,25 USD; **não foi executado com IA real**. Testes com provedor falso estão em `tests/test_agent_01_ping.py`.
- Modo `codex_proxy`: **somente após autorização explícita para consumo de cota**, `confirm=AUTHORIZE_TEXT_INFERENCE`, ID de modelo previamente existente no catálogo, preço configurado por milhão de tokens, orçamento total de 0,01–0,25 USD informado manualmente. Executa uma auditoria, até 4 chamadas de texto (`01, especialista, 12, 01`), `--max-tokens 40000`, sem fallback automático. Os controles são reservas por cálculo estimado e não garantem valor de fatura ou custo zero. Uso da integração não oficial está sujeito à autorização, cotas e condições do provedor.
- Em qualquer modo, `IMAGE_GENERATION_ENABLED=false` e `YOUTUBE_PUBLICATION_ENABLED=false`. Não há agendamento nem ferramentas de produção; o EP01 é somente leitura. Secrets e sessão efêmera ficam no runner e são descartados após o trabalho. O primeiro teste manual usa SQLite local e artifact por sete dias, **não persistência entre jobs**; migração para estado remoto exige etapa adicional.

A integração de rede `codex_proxy` agora desativa HTTP_PROXY/HTTPS_PROXY apenas para `127.0.0.1:18080`, impedindo que a autenticação de loopback seja desviada ao proxy da rede. O `proxy_preflight` aceita `--require-model` e verifica a existência do modelo somente por GET.

**Estado:** o GET autenticado foi comprovado na [execução #44308778166](https://github.com/HelioConde/VideoForge-IA/actions/runs/44308778166) com 1 conta e 10 IDs de modelo. Isso **não valida o POST /v1/responses**. Nenhuma inferência real foi executada por este desenvolvimento. Um teste com POST necessita autorização específica de chamadas/cota e valor de orçamento.
