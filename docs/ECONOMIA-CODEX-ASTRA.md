# Política de economia de tokens — Codex/Astra para VideoForge-IA

**Atualizado:** 14/11/2026  
**Pesquisa detalhada:** [HelioConde/codex — evidências de GitHub e comunidades](https://github.com/HelioConde/codex/blob/main/docs/07-pesquisa-comunidades-economia-astra.md).  
**Configuração inicial do cliente:** [../.codex/config.toml](../.codex/config.toml).

## Alcance desta implementação

O arquivo .codex/config.toml configura **somente sessões Codex CLI que respeitem a configuração do projeto**. Não muda o funcionamento do [Codex Proxy e seus GitHub Actions](CODEX-PROXY-ACTIONS.md), das APIs de geração de imagem, da política de publicação nem da cobrança da conta. Também não autoriza nenhuma despesa. O manual de [animação 2D](MANUAL-PRINCIPAL-ANIMACAO-2D.md) e o AGENTS.md mantêm prioridade total para QA e produção de vídeo.

Configuração experimental inicial:

~~~toml
model = "gpt-6.1-sol"
model_reasoning_effort = "medium"
tool_output_token_limit = 8000

[agents]
enabled = true
max_concurrent_threads_per_session = 2
default_subagent_model = "gpt-6-luna"
default_subagent_reasoning_effort = "low"
~~~

Referência dos nomes das chaves: [documentação oficial](https://learn.chatgpt.com/docs/config-file/config-reference). Se o cliente ou a conta não oferecer o modelo, testar explicitamente um modelo alternativo autorizado. Não presumir que a CLI aplica .codex/config.toml fora de um projeto confiável.

## Regra operacional de consumo mínimo

1. **Tarefas sem IA primeiro:** antes de convocar um modelo, coletar falha reproduzível com testes, verificador JSON, FFprobe, logs filtrados, hashes e QA de camadas.
2. **Pesquisa e planejamento editorial:** serviço/modelo econômico com dados versionados por canal em canal/<id>/; não enviar todo o histórico ao Astra.
3. **Rig/render Remotion:** componentes determinísticos que interpretam cenas, meshes e keyframes não devem gastar tokens por frame. Codex só é chamado para desenvolver/corrigir os componentes.
4. **Escalada:** Astra Standard apenas após falha comprovada de ferramenta local/modelo econômico ou decisão complexa de arquitetura. Anexar apenas arquivo-alvo, trechos de erro, comando de reprodução e QA esperado.
5. **Subagentes:** evitar que o agente Astra pai consulte a mesma subtask sem mudança; preferência por execução orientada a conclusão em vez de polling constante.
6. **Logs:** reduzir outputs de terminal no histórico, mas preservar stack trace completo em artifact local e trechos relevantes no pacote de escalada. Se o limite 8.000 cortar erro crítico, aumentar pontualmente.
7. **Cache:** prefixos de contexto e definições de ferramentas estáveis; não criar sessões gigantescas como um único processo interminável. Guardar checkpoints compactos por cena/vídeo.
8. **GitHub Actions:** tarefas pagas só em caminhos autorizados, nunca indiretamente por commit de documentação. O documento atual do proxy mantém regras próprias de credenciais, quotas e HTTP 429.

## Exemplo de trabalho de manutenção

**Pedido genérico caro:** "Leia todo o VideoForge-IA, encontre o problema, repense os agentes e refaça o vídeo".

**Pedido reduzido:** "Em rig/cena-3, o rosto fica transparente no frame 142; o teste X reproduz; verifique apenas o arquivo do compositor e a máscara aprovada, corrija sem gerar novas imagens e execute teste de recomposição".

A saída do primeiro estágio deve ser um pequeno pacote de diagnóstico; não um relatório com 50 arquivos e 100 mil tokens de histórico.

## Plano de validação A/B

Separar cinco tarefas **sem geração de mídia paga**: (1) JSON de cenas; (2) bug de Remotion; (3) FFprobe; (4) composição RGBA; (5) workflow de Actions isolado. Rodar baseline com a mesma versão de código e depois mudar **uma configuração por vez**. Registrar:

- modelo, reasoning effort, tier;
- quantidade de chamadas, entrada fresca, cacheada e output;
- créditos realmente consumidos/estimativa de preço API **sem misturar as métricas**;
- testes aprovados, retrabalho, duração e QA;
- commit e versão do Codex CLI.

A economia só será considerada real se custo cair **e** os testes/artefatos continuarem equivalentes. Comparações externas de TokenEconomizer ou Lattice não valem como medição interna.

## Ferramentas externas estudadas, mas não instaladas

[TokenEconomizer](https://github.com/microsoft/TokenEconomizer), [Lattice](https://github.com/moulwyse/lattice), [RepoSpend](https://github.com/mehmetdemircs/RepoSpend), [codex-monitor](https://github.com/falyx6851-byte/codex-monitor) e [Compressoor](https://github.com/M4cs/compressoor). Precisam ser verificadas quanto a segurança, licenças, versões e qualidade dos resultados antes de qualquer instalação. **Não usar ferramentas que prometam driblar cotas, autenticação ou limites de serviço.**

## Medição opcional no computador do desenvolvedor

O repositório de referência oferece um [resumidor offline de sessões Codex](https://github.com/HelioConde/codex/blob/main/scripts/resumo_codex.py) e [testes de exemplo](https://github.com/HelioConde/codex/blob/main/tests/test_resumo_codex.py). Rodar localmente dentro do repositório codex:

~~~bash
python scripts/resumo_codex.py --json
python -m unittest discover -s tests -v
~~~

Não publicar arquivos JSONL em canal/ nem em artifacts; eles podem conter prompts, histórico e detalhes privados. O resumo traz contadores aproximados por sessão, **não** uma medição da cota monetária.

## Conclusões de status

- **Aplicado:** configuração inicial do Codex CLI e registro das regras na documentação.
- **Preservado:** manual principal de animação, regras de produção oficial, estrutura por canal, proxy atual e workflows.
- **Ainda pendente:** medição real de tokens/créditos no ambiente do usuário; configuração de limites efetivos no proxy; testes A/B; instalação de plugin de comunidade; qualquer alteração no render ou publicação.

As referências externas e comparações detalhadas estão no repositório codex; consulte esse documento somente quando precisar de decisões de otimização.
