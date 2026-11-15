# Histórico de desenvolvimento — Alchemy Lab / Conquiste a Princesa EP01

## 15/11/2026 — gerador de peças da espada por tomada específica, sem novos gastos

- Implementado `videoforge/remake_sword_source.py`: aceita exclusivamente mãe original `C01-P02` do arquivo SHA verificado, âncora V2 aprovada e custo da política permitido; uma chamada `/v1/images/edits` por run. Prompts específicos para o carrasco, lâmina, bainha e fundo oculto. Nunca usa fonte C01-P04.
- Novo `remake-sword-component.yml` com testes gratuitos em push e execução de produção **manual**, gate de custo ANTES de segredos/cliente proxy, suporte ao proxy precompilado já usado pelo projeto. PNG/QA arquivados pelo script existente, não por biblioteca adicional.
- Testes unitários com mock de proxy e PNGs temporários verificam alpha, opacidade, provenance, hash, archive, recusas e proteção anti-sobrescrita; **sem provedor real nesta etapa**.
- Próximo: confirmar resultados do CI; referência V2 aprovada e eventual liberação explícita de custo, gerar as 4 peças reais e verificar via pack/ThreeCanvas sem publicação.

## 15/11/2026 — reteste após correção do contrato de âncora aprovada

- GitHub Actions `43745676658`: SUCCESS em preflight e smoke Remotion/ThreeCanvas de teste, após remoção da asserção que exigia referência V2 perpetuamente ausente. Futura aprovação da âncora não deve mais derrubar o teste.
- Fonte/MP4 C01-P02 permanecem pendentes. Nenhum custo ou publicação.

## 15/11/2026 — automação de pacote e render pós-arquivo com evidências reais

- Commit `e705a5664bb4359fabc653401b1c3d2097baa6a5` conectou scan de arte permanente, empacotador de mesma mãe, gatilho `workflow_run` e documentação/checkpoint.
- [CI 43745321463](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745321463): 14 testes em 36,416s, todos PASS (fixture temporária com PNGs e QA, sem custo). O scan de `main` bloqueou por falta de anchor/art.
- [CI 43745321451](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745321451): regressão ThreeCanvas PASS. [CI 43745436851](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745436851): workflow_run acionou sozinho, encontrou artifact inexistente e pulou o render com mensagem `REMAKE_SWORD_REAL_SOURCE_NOT_READY_NO_RENDER`, sem declarar vídeo de teste como mídia final.
- Ajustado teste de preflight para futura aprovação canônica não causar falha de CI; o bloqueio correto depois disso é o pacote real ausente, não uma expectativa eterna de âncora ausente.
- Pendências reais: gerar/revisar âncora V2 e peças independentes da C01-P02 em produtor autorizado; implementar underlay original opaco e adaptar RGBA ao shot_id; depois render e QA de MP4 de verdade. Nenhuma chamada paga/YouTube.

## 15/11/2026 — novo produtor de pacotes e encadeamento automático da tomada

- Código de seleção `remake_sword_pack.py`: arquivos permanentes por produtor e run, PNGs SHA válidos, mãe obrigatória `c01`/`C01-P02` e todas as camadas da mesma origem, recusa mistura e repetição de pacote já renderizado. Ajustado contrato do validador para o campo real `scene=c01` no `roteiro.json`.
- Novo workflow `remake-sword-pack.yml`: scan sem API, artifact apenas com pacote real. Alterado `remake-sword-preview.yml` para evento `workflow_run` com checagem do artifact e render automático; a aprovação visual segue false.
- Motion estimado da máscara é rascunho, nunca rig final. Produtor de underlay e gerador RGBA por shot ainda precisam de integração. Fonte V2 também não aprovada.
- Tests novos para pacote válido, origem trocada, SHA inválido, ausência de arquivos e idempotência; validação GitHub Actions a confirmar.

## 15/11/2026 — integracao C01-P02 validada com WebGL real em teste sintético

- `503418d9ba8949cee2a18bb9a3db1e075cac5ae2`: composição Remotion isolada para a espada, origem auditada, SHA, alfa, pivôs, máscara, staging, workflow QA e relatório de evidência; runs `43710782778`, `43710782832`, `43710782768`, `43710782888` todos SUCCESS.
- `43710965103` apontou dependência Pillow ausente no runner GHCR; `94cf7c58b90b1865971900ac877526f3c2604f41` substituiu por FFmpeg (só decode QA) e Python stdlib (composição e PNGs de fixture); run `43711300246` SUCCESS com cinco testes reais de bytes alfa/SHA/mãe/pivô.
- `de60b273ec57c2c1c6ffc01d622dac80b907dfae` adicionou smoke com Remotion/ThreeCanvas `swangle`, criando dois quadros de teste distintos (frames 7 e 71); run `43711476006` SUCCESS, log `THREECANVAS_C01_P02_ACTUAL_WEBGL_FRAME_CHANGE_SYNTHETIC_QA_PASS`.
- **Separação obrigatória:** frames CI sintéticos não são arte do dorama e não comprovam consistência de personagem; C01-P02 MP4 real ainda não existe. C01-P01 MP4 de 2s permanece disponível no run `43709191586`.
- **Próxima:** V2 referência aprovada, camada mãe por plano e quatro PNGs próprios com SHA, empacotamento por artifacts e preview técnico de 90 frames. Nenhuma chamada paga ou upload nesta etapa.

## 15/11/2026 — reduzir dependências do QA C01-P02 após falha real de smoke

- Run `43710965103`: preflight inicial do código em Ubuntu passou, mas smoke no runner GHCR falhou porque não inclui Pillow. Foi falha de ambiente/dependência, **não** da imagem nem do rig (ainda inexistentes).
- Removida dependência externa: FFmpeg existente decodifica PNG RGBA apenas no QA, e Python stdlib recompõe pixels e calcula erro médio; fixtures PNG sintéticas agora escritas com `struct`/`zlib`.
- Nenhum `pip install`, troca de engine, gasto de IA ou upload. Próxima ação: executar smoke corrigido e confirmar a validação positiva/negativa real do algoritmo de QA.

## 15/11/2026 — código de integração direta ThreeCanvas para C01-P02

- **Objetivo:** continuar após C01-P01 real, conectando à C01-P02 para transformar 4 PNGs da mesma imagem-mãe em movimento articular Three.js, com fonte auditada em GitHub.
- **Criados:** `videoforge/remake_sword_preview.py` (conferência de SHA/origem/alfa/FFmpeg para decodificação e Python stdlib para recomposição/pivô/deslocamento), `videoforge/remake_sword_preview_qa.py` (FFprobe/FFmpeg e medição de movimento), `videoforge/remake_sword_checkpoint.py` (checkpoint versionado por SHA após render). Entrada Remotion isolada `motion-remotion/src/remake-sword-preview-index.ts`, componente `remake-sword-preview.tsx`, root próprio, specs do rig técnica corrigidas.
- **Ações:** workflow `remake-sword-preview.yml` com preflight por push e render técnico condicionado a artifact fonte real; pacote documentado em `docs/C01-P02-PACOTE-ARTE-E-RIG.md`; testes Python de bloqueio/fixture sintética e testes Node de entrada sem fallback.
- **Autorização:** apenas código/QA; **0 imagens novas, 0 rigs de arte aprovados, 0 MP4 C01-P02**, nenhuma chamada paga e nenhum YouTube. Fica pendente a âncora canônica visual V2, tomada-mãe e camadas reais.
- **Próximo:** conferir runs do CI, resolver regressões; preparar fonte V2 aprovada e empacotamento automático do artifact de mãe/camadas antes de render técnico.

## 15/11/2026 — primeiro render real C01-P01, falha isolada no commit e reparo

- Run `43708620559`: Remotion criou **MP4 real de 2 s**, 60 frames pretos 1080×1920/30fps, H264 + AAC com WAV próprio. SHA WAV `22879c38726c284f484c1f57c325fc053e0ba8591565e24eba92d4e9c827fb1d`; SHA MP4 `75b8be46c7e609a1c9ff8afad0935bcbf8c6faa2126ba3c74cad3af540f3c44e`; QA da mídia e som passou. Artifact `14159253575`, 90 dias.
- A etapa de `git add` falhou pois runner GHCR de render não traz git. **Não relatar essa execução como sucesso integral**, só o render e QA; não houve commit de checkpoint. Corrigido o design: job de render sem git + job separado do host com Git e segunda validação; adicionado teste anti-regressão.
- Isso não substitui frames de arte/rig C01-P02 e não constitui vídeo completo ou publicado.
- Próximo: confirmar segundo job e persistência de hashes e run no JSON principal.

## 15/11/2026 — abrir C01-P01 por Remotion com efeito sonoro original (programação)

- Criado código procedural determinístico do efeito de espada, sem áudio externo ou gasto de IA, e composição Remotion isolada de 60 frames pretos; nunca usa PNG de personagem nem simula rig.
- Adicionado workflow `remake-opening-preview.yml`: testes Python/TypeScript, WAV PCM original, render H264/AAC e QA de vídeo/preto/som com SHA; binários permanecem em artifact de Actions com 90 dias por causa do `.gitignore`.
- O workflow gravará QA, ID e hashes no checkpoint principal se o render passar; **neste commit nenhum MP4 foi confirmado ainda**. É prévia técnica de apenas 2s, não vídeo oficial.
- Ajustado `remake_starter.py` para reconhecer prova do artifact arquivado e não reiniciar o plano C01-P01 como se faltasse áudio.
- Próxima ação: acompanhar run real e corrigir erros; depois C01-P02 usando âncora canônica aprovada e rig independente de espada.

## 15/11/2026 — validacao concluida das skills e do rig reutilizavel

- `4c797d525966ac0db208ce51bb0679614b995792` integrou 3 skills locais, referencias Remotion oficiais sem instalador remoto, fila de 37 tomadas `remake_starter.py`, codigos reais `remake-sword-motion.ts`/`remake-sword-rig.tsx`.
- `da01ba30f026f985ce8427e5f29704339fb906ac` alinhou a C01-P02 ao perfil `sword-draw-three` com as exatas 4 RGBA previstas em rig.
- **CI verificado:** runs `43706445755` (fila, 37/36), `43706445766` (TypeScript, Remotion/Three e teste espada), `43706445758` (regressoes Remotion legado) e `43706561709` (fila corrigida), todos SUCCESS.
- **Sem trabalho novo de IA paga:** apenas planejamento, codigo e testes. Nao gerar imagens ficticias ou relatar MP4 inexistente.
- **Proxima fase objetiva:** ancora canônica aprovada com SHA + imagem-mae C01-P02 e 4 camadas reais, seguida de rig de pivô e QA, sem alterar V5/C12 antigos nem publicar no YouTube.

## 15/11/2026 — programacao iniciada com skills oficiais de referencia e libs existentes

- **Ordem:** programar o EP01 do zero segundo regras novas, e acelerar com bibliotecas/skills existentes no GitHub sem ficar refazendo.
- **Auditoria:** `motion-remotion/package.json` ja contem `remotion`, `three`, `@react-three/fiber` e `@remotion/three`; nao adicionar engine nova. Referencia oficial `remotion-dev/skills` no commit `7e541aa4d7361dfaca0780a565a47307eb7bdfbb`, usada apenas como guia por skills locais (nao baixado/instalado um pacote externo na Actions).
- **Implementacao:** `videoforge/remake_starter.py` compila fila de 37 trabalhos com IDs idempotentes e dependencia de assets/QA; `.agents/skills/` ganhou diretor de remake, animador Three e inspetor QA; `motion-remotion/src/remake-sword-motion.ts`/`remake-sword-rig.tsx` adicionam o primeiro rig reutilizavel C01-P02, reaproveitando `RigidSprite` de `rig-three-scene.tsx`.
- **Teste:** regressao `tests/test_remake_starter.py` e `motion-remotion/tests/remake-sword-motion.test.cjs` conectados aos workflows existentes; fila exportada como artifact. Nao foi emitida nenhuma chamada externa de geracao de imagem, rig final, MP4 ou video YouTube.
- **Pendencia:** aguarda primeiro CI destes commits e a ancora canônica aprovada + permissao financeira operacional quando aplicavel. So entao produzir de verdade C01-P02 a partir de PNGs verificados; o codigo por si nao e um video concluido.

## 15/11/2026 — CI comprovado: gerador V2, referência SHA e workflows recuperados

- **Gerador V2:** run `43702500080` SUCCESS confirma plano cinematográfico ativo e testes dos 37 planos; commit `f372e8c01f1da1974e13346b01e9cfa3e0027039`.
- **Referência aprovada e workflow de cena:** run `43702919849` SUCCESS confirma integração e QA do módulo `remake_reference.py` com origem de PNG/SHA; commit `510931dd1c13174fdea62c3506ed22b1bf98a28c`.
- **Regressão encontrada:** run `43702917744` FAILURE por QA legado exigir arquivo de lock retirado; **corrigida** em `981362486d73f07bc6701b47297d63095fa7ef38`.
- **Verificação da correção:** run `43703372917` SUCCESS para QA de arquivamento permanente; run `43703372899` SUCCESS para autonomia, testes de referência, proteção de custos e workflows.
- **Integridade:** não gerou imagens de produção, malhas/rigs novos, MP4 do remake ou uploads YouTube; a prévia C01 V5 continua histórica.
- **Próxima ação exata:** obter e aprovar a âncora V2 e a disponibilidade/custo do provedor; dar entrada em `C01-P02` por workflow, arquivando PNG + SHA e iniciando pipeline de camadas/rig real. O sistema ainda não está autonomamente completo.

## 15/11/2026 — reparar QA/workflows legados que exigiam lock revogado

- **Falha detectada em CI:** run `43702917744` do workflow `qa-permanent-image-archive.yml` falhou no preflight: exigia `SEM-GERACAO-NOVAS-IMAGENS.lock`, retirado quando o usuário autorizou o remake.
- **Correção:** todos os workflows de leitura/QA/rig legados inspecionados deixam de exigir o lock ativo; consultam o arquivo de bloqueio **histórico**. O QA de arquivamento também confirma `remake-v2-20261115`, ausência de custo extra autorizado e nenhuma publicação. Fluxos que efetivamente geram imagens mantêm controles de custo e de lock recolocado.
- **Timeline:** ao reexecutar QA V1, preservar rótulos `legacy_scope` e `active_remake_manifest`; o QA de tomadas registra que o prompt atual vem do manifesto V2, não das regras antigas.
- **Regressão:** `tests/test_remake_workflow_compatibility.py`, incluído no workflow de autonomia. Nenhuma mídia gerada, sem serviço externo pago acionado.
- **Próximo:** rodar CI e obter resultados; geração de âncora somente com provedor/custo permitido e validação humana.

## 15/11/2026 — workflow de cenas passa a ler âncora V2 SHA-verificada

- **Causa da inconsistência restante:** apesar de `cinematic_direction.py` estar integrado ao manifesto V2, o workflow `production-scene-by-request.yml` continuava baixando a referência legada da Actions run `43590930215`.
- **Correção:** novo módulo `videoforge/remake_reference.py` prepara a referência canônica aprovada do próprio GitHub, verificando o arquivo PNG, SHA, `manifesto-geracoes.json` e `character-bible.production.json` do mesmo canal, vídeo e run. O workflow usa esse caminho para V2 e preserva download anterior para os demais canais. Cenas V2 requerem `shot_id`; sem referência aprovada, trava antes de qualquer solicitação ao modelo.
- **Regressão:** `tests/test_remake_reference.py` valida recusa de referência ausente, cópia correta a partir de bytes verdadeiros em fixture, manifesto ausente e SHA divergente. Incluído no workflow de autonomia e geração de cenas.
- **Mídia nesta atualização:** nenhuma nova imagem, layer, rig ou vídeo; nenhuma chamada de IA. **Próximo trabalho:** rodar CI e encadear workflows de camadas/rig ao controlador, mantendo gates de custo e revisão humana.

## 15/11/2026 — implementação do seletor cinematográfico V2 e verificação SHA

- **Solicitação:** aplicar a correção técnica que faltava após auditoria das regras principais.
- **Integração:** o gerador atual passa a consumir `remake-ep01-planos.json` quando o checkpoint indica `remake-v2-20261115`, em vez de dirigir a geração pela V1 histórica. A direção V1 permanece somente como fonte de QA e histórico. Planos e emoções do roteiro foram preservados (14 cenas, 37 planos, 163 segundos).
- **Segurança:** checagem de identidade/cast, frames contínuos, estilo oficial, elenco da C01/C02, preto sem imagem, SHA e aprovação humana da âncora, SHA da referência antes de enviar ao proxy. Custo pago e YouTube continuam bloqueados por políticas separadas.
- **Regressões:** novos testes em `tests/test_remake_cinematic_integration.py` cobrindo planos, 36 prompts diferentes, fidelidade do roteiro, negação sem referência e outros canais; adicionados ao workflow `remake-autonomy.yml`.
- **Resultado da etapa:** apenas código e documentação, sem geração ou render. Evidência de CI será conferida separadamente e anexada posteriormente ao checkpoint.

## 15/11/2026 — auditoria de coerência das regras do remake

- **Verificação solicitada:** nem todas as regras estavam coerentemente identificadas. Apesar dos documentos principais já descreverem remake V2/autonomia, trechos antigos em `AGENTS.md`, `ESTADO-ATUAL.md`, `PLANO-ARTE-RIG-EP01.md` e `estilo-visual-oficial-dorama.json` continuavam tratando a proibição histórica de imagens como ativa.
- **Correção editorial e documental:** incluir matriz de precedência atual em `AGENTS.md` e neste checkpoint, rotular plano técnico V1 e EDL/direção V1 como **legado**, corrigir as flags e o próximo passo no manifesto de estilo. Preservar o histórico de 14/11 sem apagar evidências; o remake tem permissão editorial de novas imagens, mas despesas adicionais e publicação permanecem bloqueadas.
- **Regressão automatizada:** `tests/test_remake_policy_consistency.py` confere coerência das flags e distinção explícita de arquivos antigos; incluído na verificação do workflow de autonomia.
- **Pendência técnica não resolvida por documentação:** `videoforge/cinematic_direction.py` ainda valida autorização e referências da pré-produção legada; antes de gerar o EP01 V2 o gerador precisa consumir `remake-ep01-planos.json` e referências canônicas verificadas. O coordenador de retomada existe, mas o encadeamento fim a fim ainda não foi implementado.
- **Resultado desta mudança:** somente documentação/JSON e teste de regressão; sem imagem/rig/render novo e sem upload YouTube. **Próximo passo:** adaptar o gerador antigo ao manifesto ativo e incluir validações de referência por SHA, preservando bloqueios de custo e publicação.

## 15/11/2026 — autorização do remake EP01 e regra de autonomia

- **Ordem do responsável:** refazer todo o episódio conforme novas regras, depois "Continuar". Posteriormente acrescentou a regra de **ensinar o VideoForge a produzir e corrigir animações no GitHub, sem orientação manual a cada passo**.
- **Decisões:** novo EP01 Remake V2 com 14 cenas, 37 planos e 163s como base, sem limite editorial de imagens. Arte nova permitida editorialmente, bloqueio anterior arquivado em `REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md`. Manter antigas C01 V5 e C12 preservadas em histórico; não apagar sprites ou vídeos.
- **Arquivos desta integração:** `REMAKE-EP01-PLANO-OFICIAL.md`, `remake-ep01-planos.json`, estado mestre/JSON, política de geração e coordenador de preflight. Priorização de QA, escolha do próximo estágio por evidência e procedimentos para delegar à automação existente. **Nenhuma geração de PNG, MP4 ou upload efetuado por esta alteração**; não informar autonomia completa ainda.
- **Próxima ação:** rodar preflight automatizado, exigir âncora canônica versionada com SHA para C01, usar geradores e workflows existentes quando houver acesso e custo autorizados; registrar os resultados por etapa no mestre.

## 15/11/2026 — diretriz sem cota de imagens e continuidade centralizada

- **Pedido do responsável:** sem limite editorial numérico de imagens; priorizar beleza, riqueza de detalhes, consistência de identidade/cenário e movimento 2D verdadeiro. Gerar quantas imagens/iterações forem realmente necessárias **somente quando permitidas**.
- **Registro obrigatório:** cada avanço, falha, bloqueio, pesquisa, teste, geração autorizada ou render deve ser registrado no [arquivo mestre ESTADO-ATUAL.md](ESTADO-ATUAL.md), incluindo evidências e próximo passo; também sincronizar `estado-atual.json` e preservar histórico em `HISTORICO-DESENVOLVIMENTO.md`. Consultar a `main` antes de iniciar trabalhos para não repetir feitos.
- **Só documentação e JSON nesta mudança:** nenhuma imagem foi gerada, nenhum render/asset/rig alterado, nenhum upload. `SEM-GERACAO-NOVAS-IMAGENS.lock` ativo no EP01; futura liberação exige autorização expressa. C01-P03 V5 segue aguardando avaliação visual, C12 ainda precisa dos originais.
- **Próximo passo:** revisar vídeo V5 existente, continuar importação dos originais da C12, sem gerar novas artes na condição atual.

Registro cronológico de fatos verificáveis. **Não sobrescrever eventos antigos.** O ponto de retomada, que deve estar sempre atualizado na branch `main`, é [ESTADO-ATUAL.md](ESTADO-ATUAL.md).

## 14/11/2026 — plano cinematográfico, 37 planos e C12

- [Run 43653702785](https://github.com/HelioConde/VideoForge-IA/actions/runs/43653702785) — **PASSOU**: auditoria da timeline e testes de rigor de planos; nenhum MP4 criado por essa execução.
- [Run 43654314863](https://github.com/HelioConde/VideoForge-IA/actions/runs/43654314863) — **PASSOU**: validação do compositor ThreeCanvas/Remotion e malhas C12 de 5 partes, 512 triângulos; sem renderizar MP4.
- [qa-c12-rig-malha-v2.json](qa-c12-rig-malha-v2.json) — documento anterior registra uma prévia local `alchemy_c12_mesh_rig_v2_aprovacao.mp4`, 12 segundos, 360 frames e SHA-256 `e08f79924e6f09bab195e54d49c32b588c2438d28faf2e1db12d626bba018016`. **O arquivo binário original não está no repositório.** Não oferecer o hash como download.
- [PR #49](https://github.com/HelioConde/VideoForge-IA/pull/49), commit de integração `466852e88b23f7a042a0a76fc7bca78164ca049f` — **INTEGRADO À MAIN**: C12 compositor técnico P02+P03, importação de PNGs antigos por SHA e workflow de MP4 de 8 segundos.
- [Run 43658221156](https://github.com/HelioConde/VideoForge-IA/actions/runs/43658221156) — **BLOQUEADO (ASSETS_PENDING)**: zero dos nove arquivos C12 disponíveis nos caminhos esperados; o artifact contém preflight, não vídeo. Registrado em [qa-c12-render-bloqueio-2026-11-14.json](qa-c12-render-bloqueio-2026-11-14.json).
- [PR #50](https://github.com/HelioConde/VideoForge-IA/pull/50) — **ABERTO na consulta**, pipeline alternativo C12 com validação de SHA e preflight. [Run 43659001910](https://github.com/HelioConde/VideoForge-IA/actions/runs/43659001910) passou no contrato mas deixou render ignorado; não equivale a MP4. **Reconciliar** antes de incorporar, evitando duplicar pipelines incompatíveis.

## 14/11/2026 — C01 rig articulado e MP4

- [Run 43630118130](https://github.com/HelioConde/VideoForge-IA/actions/runs/43630118130) — **PASSOU** em prévia técnica C01-P03, 3 s, 1080×1920, 30fps. Defeitos de recorte/lanças visíveis e recomposição incompleta; não aprovado.
- [Run 43633018544](https://github.com/HelioConde/VideoForge-IA/actions/runs/43633018544) — **PASSOU** com correção da costura da cintura de Kael (recuperação de 84 pixels da fonte original e ancoragem). Preservar essa melhoria.
- [PR #51](https://github.com/HelioConde/VideoForge-IA/pull/51), commit `693212eeb32ede9c0dc8f1c6de94a92638b0dc60` — **INTEGRADO À MAIN**: motor C01 de direção por keyframes, pivôs hierárquicos, malhas independentes e workflow.
- [Run 43660106313](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106313) — **PASSOU** na main: gerou MP4 de prévia técnica C01-P03 e relatório QA; artifact temporário `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43660106313`, ID `14139373365`; não é o episódio oficial.
- [Run 43660106308](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106308) — **PASSOU** em TypeScript e testes Remotion.
- A implementação original de C01 continua aberta no [PR #48](https://github.com/HelioConde/VideoForge-IA/pull/48), mas **o núcleo útil já foi portado à main pelo PR #51**. Não mesclar cegamente a branch antiga.

## 14/11/2026 — checkpoint persistente (esta atualização)

- Criados `ESTADO-ATUAL.md`, `HISTORICO-DESENVOLVIMENTO.md` e manifesto legível por máquina `estado-atual.json` na pasta do vídeo; `AGENTS.md` e `README.md` devem apontar para o estado atual na branch `main`.
- **Próximo passo não resolvido:** recuperar os originais RGB, sete PNGs técnicos e executar C12 após os hashes baterem; depois continuar QA das bordas C01. Não habilitar geração de imagem ou upload do YouTube.

## 14/11/2026 — QA C12 e importação que continua automaticamente

- [PR #52](https://github.com/HelioConde/VideoForge-IA/pull/52), **MERGED** commit `a69287356a87c3bbd2f67bf987ce1a0f0ae73f5c`. Implementado `videoforge/c12_render_qa.py` com QA de recomposição neutra em pixels originais e leitura de movimento localizado do H.264 gerado, detecção de MP4 parado/pan global e repetibilidade de dois quadros. [Run de testes 43661690928](https://github.com/HelioConde/VideoForge-IA/actions/runs/43661690928) **SUCCESS** (render `skipped` no PR). [Run main 43661756457](https://github.com/HelioConde/VideoForge-IA/actions/runs/43661756457) **FAIL esperado em `ASSETS_PENDING` (0/9 fontes RGB/RGBA)**, artifact `vf-alchemy-c12-threecanvas-draft-43661756457`, ID `14140665963`, apenas JSON de pendência; **não contém MP4**.
- A Library do projeto lista `/youtube/alchemy_c12_rig_camadas_tecnicas_v2.zip` (6.186.154 B), `/youtube/alchemy-ep01-cinema-3-originais.zip` (7.390.768 B), e a prévia `/youtube/alchemy_c12_mesh_rig_v2_aprovacao.mp4` (999.889 B). **Metadados encontrados**, mas a materialização dos arquivos foi recusada: `This Project file does not have an authorized raw-byte materialization path`. Não há bytes recuperados nem cópia dos PNGs na main; será necessário anexar os ZIPs reais ao chat ou enviá-los ao GitHub.
- [PR #53](https://github.com/HelioConde/VideoForge-IA/pull/53), **MERGED** commit `24c49509b53339a45a413c581435dd817d2028db`: novo coordenador `.github/workflows/c12-after-import.yml` com gatilho `workflow_run` após os dois importadores originais. Ele verifica 9 SHA únicos da main e despacha `workflow_dispatch` do render apenas se tudo estiver pronto; SHA divergente bloqueia, assets ausentes esperam. [Run de testes 43662265188](https://github.com/HelioConde/VideoForge-IA/actions/runs/43662265188) **SUCCESS**.
- [Run main 43662307131](https://github.com/HelioConde/VideoForge-IA/actions/runs/43662307131) **SUCCESS do coordenador**: a etapa `Reportar espera pelos PNGs antigos` foi executada, a etapa `Acionar render` foi **skipped**, e o artifact `c12-after-import-preflight-43662307131`, ID `14140133496`, contém apenas preflight. Foi criada a pasta `uploads/` para os dois ZIPs de imagens anteriores.
- **Próximo passo:** importar os bytes originais dos dois ZIPs para `uploads/`, deixar os workflow importadores archivar exatos RGB/RGBA, verificar a retomada automática do MP4 técnico C12 e inspecionar máscaras/mecha/brinco/underlays. Sem novas imagens, sem aprovação humana e sem YouTube.

## 14/11/2026 — upload verificado e idempotente dos ZIPs C12

- [PR #54](https://github.com/HelioConde/VideoForge-IA/pull/54) **MERGED** na `main` (commit `346a3a80c74a96f39390aa12896916bfd2e9a994`). `videoforge/c12_upload_existing_zips.py` valida os dois ZIPs originais por SHA, IHDR nativo, tipo RGB/RGBA, nomes obrigatórios do RGB e segurança das entradas antes de gravar em `uploads/`. Recusa sobrescrever arquivos diferentes.
- `scripts/enviar-zips-c12.ps1` envia os pacotes preexistentes à `main` pelo `gh`, com teste local, retry de conflito sem `force push`; [manual de uploads](../../../../uploads/README.md).
- [Run 43665498760](https://github.com/HelioConde/VideoForge-IA/actions/runs/43665498760) — testes do PR **SUCCESS**. `render-draft` **skipped** por ser PR; nenhuma fonte C12 original foi acrescentada. **Sem MP4 C12 novo, sem geração de imagens ou publicação**.
- **Bloqueio restante:** os dois ZIPs antigos estão indexados na Library mas os bytes não puderam ser copiados; transferir manualmente ao GitHub ou anexar os arquivos verdadeiros. Em seguida, os workflows já presentes arquivam os PNGs e acionam o render do rig C12 de oito segundos.

## 14/11/2026 — C01 P03: usuário não percebeu movimento; rig articulado V2

- Revisão técnica do MP4 anterior `43660106313` (3s/90f): movimentos originais máximos `-0,6°` da cabeça, `-2px` ombros e `+2°` do pulso; na área de Kael, comparação de frames 0 e 75 encontrou **11.756 pixels** acima de delta RGB 24. Movimento era real, mas insuficiente na leitura visual de plano aberto.
- [PR #55](https://github.com/HelioConde/VideoForge-IA/pull/55), **MERGED** commit `c3a4c6bcee3c2cbe5d180bcf1a5355f625a3398a`. Reescrita focal dos keyframes C01-P03, adicionando braço direito, antebraço e translação independente de cabeça, com rotação de até `-8,5°`, pulso até `+10°`, suporte da cabeça com no máximo `-1,25px` vertical. Câmera e personagens estáticos do fundo preservados. Três tracks adicionais (total de **110**). `atuacao-c01-p03-v2.json` registra a coreografia e guardas visuais.
- [PR run 43666968689](https://github.com/HelioConde/VideoForge-IA/actions/runs/43666968689) **SUCCESS** no primeiro MP4 V2: 23.356 pixels mudaram em Kael, mas a translação de cabeça de `-7px` expôs faixa marrom do cenário na gola; corrigida sem gerar novos pixels.
- [PR run 43667345840](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667345840) **SUCCESS** em typecheck/testes no código corrigido. [PR run 43667345857](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667345857) **SUCCESS** na renderização técnica C01 com amplitude corrigida, 3s/90f, 1080x1920 H.264, SHA `1667c60c61b7e10a5e3d5353599631678709e91b456072069ec3e39a1c48094d`, artifact `14143046357`; delta RGB ≥24 no personagem **20.974 pixels** (antigo: 11.756, +78%). A câmera não se move. A revisão humana ainda mostra parte do fundo na nuca/gola.
- [Run main 43667678291](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667678291) **SUCCESS** na `main`: render real de 90 frames 1080×1920 H.264; artifact `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43667678291`, ID `14142756569`, SHA-256 do MP4 `1667c60c61b7e10a5e3d5353599631678709e91b456072069ec3e39a1c48094d`, idêntico ao PR. QA decodificado 20.974 pixels na região do Kael. **Não publicável**, `human_visual_approved=false`: gola mostra background em parte dos quadros. A rotação experimental de até `8,5°` **excede o limite padrão de cabeça de `2°` do manual principal**, portanto não pode ser aprovada como render oficial sem corrigir o rig e resolver a divergência. Nenhuma imagem nova gerada.
- Arquivos mudados: `direcao-rig-remotion.json`, `direcao-bindings-c01-draft.json`, `atuacao-c01-p03-v2.json`, `pedido-render-c01-direcao.json`, `videoforge/directed_rig_qa.py`, `tests/test_c01_articulated_motion_qa.py`, `motion-remotion/tests/directed-rig.test.cjs` e workflow de testes. **Nenhuma IA gerou imagens.**

## 15/11/2026 — V3 C01-P03: rig de verdade, gola protegida, MP4 e testes na main

- **Pedido:** continuar melhorando o movimento que era quase imperceptível e a região avermelhada que aparecia entre pescoço, jaqueta e braço. Trabalho feito na branch `feat/alchemy-c01-manual-safe-acting-v3-20261114`, integrado pelo [PR #56](https://github.com/HelioConde/VideoForge-IA/pull/56) **MERGED** no commit `69e22458703c7c716f05e205987471ce3595b1c5`. **Não reiniciar** o rig nem o roteiro.
- **Rig V3:** cabeça ≤**1,82°** e sem elevação independente (regra do manual ≤2°); câmera estática; braços independentes, antebraço, punho, ombros, cabelo/jaqueta com malhas secundárias, e nova rotação da **bota direita** apoiada no joelho. Agora **9 keyframe tracks em C01-P03**, **113 tracks no episódio inteiro**. O gesto é distribuído para articulações existentes; não há falso movimento do PNG inteiro nem fechamento de dedos fabricado.
- **Correção de oclusão:** nova parte `kael.costura-gola-pixel-original` derivada **somente da mãe existente**, SHA `544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf`, cortada por `onlyCoveredBy` de jaqueta/braço superior direito, protegida atrás das partes e subordinada ao osso `kael.ombros`. Implementado em `videoforge/directed_rig.py` (origem RGB SHA verificada permitida somente para esse holdout, partes comuns continuam RGBA) e neutralizado em `videoforge/directed_rig_qa.py`. Nada foi desenhado/regenerado.
- **QA novo:** `videoforge/c01_collar_qa.py` conta cenário verdadeiro recém-revelado perto da gola no MP4 já decodificado. `videoforge/directed_rig_qa.py` passou a persistir **os dois resultados** de movimento e gola em `c01-gates-qa.json` mesmo quando a prévia reprova. Novos testes Python `tests/test_c01_collar_qa.py` / `tests/test_directed_rig.py`, regressão JS `motion-remotion/tests/directed-rig.test.cjs`, TypeScript e Remotion no workflow atual. Documento estruturado `atuacao-c01-p03-v3.json`; pedido de render revisão 3. Sequência detalhada de erros anteriores e mudanças no [relatório permanente QA V3](QA-C01-P03-V3-2026-11-15.md).
- **Tentativas reprovadas durante desenvolvimento:** runs `43668744883` (236 pixels de cenário na gola), `43669353700` (148), `43669644633` (149), `43670176688` (125), `43670794052` (109 e movimento 15.633), `43671035076` (74 e movimento 15.791), `43671239999` (76 e 15.917), `43671532481` (68, atuação fraca), `43671750143` (76 e 15.468), `43671967400` (falha antes do último teste de bota). Causas e tratamentos documentados no relatório de QA. **Não apagar histórico das tentativas.**
- **Primeiro sucesso final verificável:** [PR render 43671982404](https://github.com/HelioConde/VideoForge-IA/actions/runs/43671982404) e [testes 43671982444](https://github.com/HelioConde/VideoForge-IA/actions/runs/43671982444), ambos **SUCCESS**. Artifact da PR ID `14145220360`.
- **Reproduzido na main após merge:** [render 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507) **SUCCESS**, [TypeScript/testes 43673610480](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610480) **SUCCESS**. Artifact da main ID **`14145228520`** (temporário) com MP4 3 s, 90 quadros, 1080×1920, 30 fps, H.264 yuv420p, sem áudio, 693.447 bytes, SHA-256 `73993ab7b1f93aead42d1860d16c3db965adcbd3e6bdf2794eb631a9d704100c`, **idêntico** ao MP4 da PR.
- **Gates do MP4 V3 main:** `acting=18.923/16.000` pixels alterados somente na região de Kael entre frames 0–75 (RGB delta ≥24), `collar=73/75` pixels recém-expostos no pior frame (55=67, 75=66, 89=73). Ambos **PASSARAM tecnicamente**, mas a margem de gola é estreita. Determinismo de frame repetido **PASSOU**.
- **Pendências e verdade de produção:** neutral recomp `meanAbsoluteRgbError=11,159474`, `pixelExactRecomposition=false`, 1.075.513 pixels diferentes; guardas, lanças, Aldric/trono, mãos, bota e bordas de gola ainda precisam inspeção/correção visual. `humanVisualReview=false`, `publishable=false`, `officialVideoApproved=false`, `youtubeUploaded=false`. **C12** ainda `ASSETS_PENDING`, nove PNGs originais não importados. O episódio oficial de 163 s não existe.

## 15/11/2026 — revisão visual do C01 V3 e pesquisa externa de skills arquivada

- **Feedback após assistir ao MP4:** a atuação C01 V3 está melhor do que antes, mas o **braço direito de Kael gira indevidamente apesar de apoiado na perna**, a **bota direita apresenta corte** durante o movimento, as **lanças dos soldados aparecem deformadas/incorretas** e **a cabeça do rei Aldric aparece cortada**. A primeira cena deve conter **somente respiração leve do personagem principal**, com movimentos mínimos de tronco/ombros/cabeça, outros elementos imóveis. **Não confundir o sucesso técnico dos gates da V3 com aprovação visual.**
- O usuário pediu pesquisa de skills e bibliotecas, citando [spine-animation-ai](https://github.com/GenielabsOpenSource/spine-animation-ai) e [claude-animated-shorts/SKILL.md](https://github.com/mromidev/claude-animated-shorts/blob/main/SKILL.md). Relatório de pesquisa fornecido pelo usuário em `Texto colado(1).txt` (SHA-256 `950b66530b071e84e75b82ba5357c31629b8473ae908fc8ec5b1eb49a9256e84`).
- **Informações armazenadas na main:** [catálogo e avaliação de projetos](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md) (análise de 14 ferramentas/skills, licenças/compatibilidade a conferir, três arquiteturas, C01/C12 e checklist), [regras visuais da C01-P03 V4](REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md) (locks de contato, bota parada, rei íntegro, lanças fixas e respiração suave). A fonte completa permanece no anexo; o documento do GitHub é síntese operacional com proveniência e decisões. 
- **Decisão arquitetural de pesquisa:** continuar usando Remotion/Three e o rig existente, sem instalar plugins/editores novos nesta etapa. Usar OpenCV/scikit-image e técnicas de `SKILL.md` como candidatas a QA e organização. Cautela com licença PolyForm NC do repositório spine-animation-ai e condições próprias de runtimes/editores.
- **Estado de implementação:** `documentation_only`. Nenhuma nova imagem, alteração de máscara/keyframes, render V4 ou postagem YouTube nesta tarefa. V3 de 3 s continua válida como **prévia técnica não aprovada**, [run main 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507).
- **Próxima ação:** branch V4 de C01, travar braço/punho/pé direito e props, fazer só respiração leve e QA de contato, corrigir rei e lanças a partir dos bytes originais, gerar nova prévia e revisar; C12 permanece bloqueada por PNGs originais ausentes.

## 15/11/2026 — implementação C01 V4 após feedback visual, PR #57 (não afirmar aprovação antes dos testes)

- **Origem:** feedback após o MP4 V3 de 3 segundos: braço e mão direitos apoiados na perna moveram indevidamente, bota direita mostrou corte, lanças duplicadas/deformadas e cabeça do rei cortada. Usuário pediu menos movimento: só respiração delicada do Kael. Regras permanentes em [REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md](REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md); pesquisa em [docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md).
- **PR de implementação:** [#57](https://github.com/HelioConde/VideoForge-IA/pull/57), branch `feat/alchemy-c01-subtle-breathing-static-context-v4-20261115`; V3 preservada em histórico. `direcao-rig-remotion.json` passou de **9 para 2 tracks no C01-P03** (`kael.ombros/translateY` de 0 a -1,25px, `kael.cabeca/rotationZ` até -0,32°). Total do episódio de **113 para 106**. Cabelo `0,45px`, jaqueta `0,55px`. Sem câmera falsa, sem movimento do PNG inteiro.
- **Contato braço/perna garantido por hierarquia:** braço direito e esquerdo agora têm `parent=null`, não herdam a respiração do ombro; antebraço direito e mão continuam filhos da cadeia de braço direito imóvel. Perna/bota direita não recebem keyframes. Testes JavaScript medem transformações de pontos em **coordenadas globais** ao longo da timeline, não só valores locais de keyframes.
- **Rei Aldric, guardas e lanças:** causa de duplicidade era recompor sobre o fundo cinco PNGs de contexto com máscaras ainda provisórias; um candidato de Aldric iniciava em `y=299`, podendo recortar a coroa que começa acima disso. Adicionado `original-mother-static-context-with-kael-cutout/v1` em `videoforge/directed_rig.py`: fundo derivado diretamente de `assets/cenas-mae/cena-01.png`, SHA `544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf`, mantendo integralmente os pixels estáticos. Só a área já identificada por **alfa dos sprites originais de Kael + 3px de margem** é substituída por pixels do fundo reconstruído existente, também com SHA conhecido. Candidatos duplicados de rei/guardas/lanças são removidos da composição final **mas preservados no repositório**. Sem gerar nova arte.
- **QA acrescentado:** `videoforge/c01_v4_breath_qa.py` e `tests/test_c01_v4_breath_qa.py` validam fonte de pixels, pose ancorada, king/coroa e lanças originais, áreas estáticas de H.264 e ausência de keyframes de mão e bota. `videoforge/directed_rig_qa.py` usa limite de movimento **suave** (25–10.000 pixels com RGB delta 8) e verifica também a gola. A meta V3 de 16.000 pixels foi desativada **só para C01 V4** para não obrigar ações antinaturais.
- **Primeira execução de PR** [#43676126787](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676126787): testes Python/JS/TS passaram, mas o empacotamento falhou com `COVERED_HOLDOUT_REFERENCES_NOT_SOURCE_PARTS`; causa: a gola (filha dos ombros) tentava referenciar braço agora filho da raiz. Corrigido para `onlyCoveredBy=["kael.jaqueta"]`, sem devolver movimento ao braço. **Não tratar o render dessa run como MP4 criado.**
- **Nova execução:** [#43676244073](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676244073) gerada após correção; conclusão e MP4 dependem de verificação. [#43676244089](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676244089) valida TypeScript/testes. Rastrear artifact e SHA após término. Aprovação visual **continua falsa**.

**Próximo passo:** verificar conclusão dos dois jobs, consertar falhas concretas mantendo a pose discreta e a identidade das fontes; só integrar na main quando QA técnico passar; conferir novo MP4 visualmente e registrar defectos restantes. C12 ainda bloqueada por originais ausentes. Zero imagens de IA, zero YouTube.

## 15/11/2026 — C01 V4 verificada na main, MP4 e QA concluídos, aguarda revisão visual

- [PR #57](https://github.com/HelioConde/VideoForge-IA/pull/57) **MERGED** no commit `4d010a92212ce77e9c7fbcf762537ecf0e732be2`, com duas tracks de respiração em C01-P03, mão/antebraço/pé direitos travados por hierarquia, rei e lanças originais recuperados ao não sobrepor as cinco camadas estáticas candidatas, processamento determinístico apenas de pixels-mãe e plano de QA específico a atuação sutil.
- [PR render/QA #43676494078](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676494078) **SUCCESS**, [PR TS #43676494086](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676494086) **SUCCESS**. [Main render/QA #43676630976](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630976) **SUCCESS**, [main TS #43676630957](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630957) **SUCCESS**. Artifact de MP4 técnico **ID `14145684036`** na main (temporário).
- O `directed-rig-preview.mp4` do PR e da `main` **tem bytes idênticos**: 599.144 bytes, 3s/90f, 1080×1920 H.264 30fps, SHA-256 `90baea03b4e2b551a21d341c263853a2e9b9d4d5647314fff46a39bf79fbbff7`. **Sem áudio, sem YouTube.** A cena do rei e lanças foi inspecionada nos frames 0 e 74.
- QA técnico da main: V4 `technical_qa_passed=true`, movimento sutil real em 11.115 pixels (delta RGB≥8) com constraints físicas ≤1,25px ombros e ≤0,32° cabeça, sem falso pan de câmera; rei/lanças/bota permanecem estáticos (0 pixels alterados no limiar 24 do ROI); gola exposição **24/75**. **Recomposição neutra melhorada** para erro RGB MAE `0,216449949476454` e 13.015 pixels diferentes em 1.572.864 (antes V3 MAE 11,159474 e 1.075.513 diferenças).
- Erros V4 iniciais preservados no histórico: `43676126787` falhou por referências de holdout com pai divergente; `43676244073` renderizou e falhou por teto de contagem inadequado para micro-respiração, **não por excesso real de ângulo**. Foi corrigido preservando limites de ossos e novas regiões fixas; testes demonstraram.
- Documentação definitiva: [QA-C01-P03-V4-2026-11-15.md](QA-C01-P03-V4-2026-11-15.md), [regras do usuário](REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md), [manifesto V4](atuacao-c01-p03-v4-respiracao.json), [pesquisa de skills](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md), [checkpoint atualizado](ESTADO-ATUAL.md).
- **Estado honesto:** `humanVisualReview=false`, `publishable=false`, `officialVideoApproved=false`, `youtubeUploaded=false`. **V4 não é o episódio de 163s** e faltam correções finas de máscara/borda se a revisão humana encontrar defeitos. C12 continua aguardando origem real dos 2 ZIPs/9 PNGs, sem regenerar.

## 15/11/2026 — C01 V5: respiração localizada nas costas, cabeça da V4 preservada

- **Novo pedido após assistir à V4:** manter o leve movimento da cabeça e acrescentar respiração suave nas **costas** do Kael, sem afrouxar o braço/mão direitos apoiados, bota direita, guardas, lanças ou o rei. O usuário pediu aplicação direta no GitHub.
- [PR #58](https://github.com/HelioConde/VideoForge-IA/pull/58) **MERGED**, squash commit `ae7ca09c3f75ed04498704459a2ac547de810d06`; implementada a V5 no pipeline atual Python + Three.js + Remotion, sem instalar bibliotecas externas ou gastar com geração de imagens.
- Em `direcao-bindings-c01-draft.json`, `kael.jaqueta.mesh.backBreath` foi vinculado à track existente `kael.ombros`: janela Y857–947 da fonte (pico 898), expansão máxima 1,05px, subida vertical 0,6px, laterais e cintura pinadas. `motion-remotion/src/directed-rig-math.ts` calcula deformação **real dos vértices da jaqueta** frame a frame, não movimento de imagem inteira. Cabeça permanece com rotação `-0,32°`, ombros `-1,25px`, braço e pé direitos bloqueados. **2 tracks C01, 106 no episódio**.
- Validação fechada contra uso indevido da malha nos arquivos `videoforge/directed_rig.py`, `videoforge/c01_v4_breath_qa.py` e TypeScript; tests Python/JS de continuidade, juntas, costas/bordas, alfa e UV. O QA lê quadros decodificados H.264 do recorte original das costas, além dos gates de gola e rei/lanças/bota.
- [Run 43680421318](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680421318) **FAILURE**: 53 testes Python passaram, compilador TS pediu narrowing de `DirectedTrack | undefined`; corrigido por `?? fail(...)` sem alterar a direção.
- [Run 43680505866](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680505866) **SUCCESS** (render+QA do PR), [run 43680505879](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680505879) **SUCCESS** (Remotion TS/tests), artifact ID `14147369278`. MP4 técnico **3 segundos, 90 quadros, H.264 1080×1920, 30fps, 598.863 bytes**, SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`.
- QA real da PR: costas na ROI nativa `[405,870,85,65]` alteraram **957, 514, 8 e 191 pixels** com RGB≥8 nos frames 30,55,75,89; **`back_visible_in_mp4=true`**. Ator total 11.698 pixels alterados com RGB≥8, **0 mudança detectada** na coroa, lanças e bota direitas nas ROIs protegidas RGB≥24; gola 24/75; recomposição neutra MAE 0,216449949476454, **13.015 pixels não exatos**. **`technical_qa_passed=true`**, `humanVisualReview=false`.
- **Validação na main confirmada:** [render/QA #43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142) **SUCCESS** e [main TypeScript/testes #43680784182](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784182) **SUCCESS**; artifact MP4 `14147374656`, nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43680784142`. MP4 extraído com 598.863 bytes e SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`; **comparação real de bytes com PR idêntica**. O QA na main repetiu `back_visible_in_mp4=true`, costas 957 px de pico em ROI, ator 11.698, rei/lanças/bota imóveis no limiar medido, gola 24/75, recomposição MAE 0,2164499. Ainda sem aprovação visual, sem YouTube. O binário continua em artifact temporário, não em arquivo versionado no repo.
- Documentação: [QA permanente V5](QA-C01-P03-V5-2026-11-15.md), [manifesto V5](atuacao-c01-p03-v5-respiracao-costas.json), [checkpoint](ESTADO-ATUAL.md). V3/V4 ficam preservados para auditoria. **C12 ainda aguarda ZIPs/PNGs originais**. Nenhum vídeo de 163s pronto, nenhuma geração de novas imagens e nenhum upload ao YouTube.

## 15/11/2026 — guia visual oficial do dorama, sample e alternância de ângulo (documentação, nenhuma imagem nova gerada)

- Usuário enviou imagem original de **Kael ajoelhado ante a princesa e o rei em salão gótico**, solicitando usá-la como qualidade/referência e determinar que **quase toda cena seja dramática, com ângulo distinto**.
- O padrão **`Cinematic Semi-Realistic Fantasy Anime`** agora está documentado em [`PROMPT-OFICIAL-ESTILO-DORAMA.md`](PROMPT-OFICIAL-ESTILO-DORAMA.md) (prompt mestre e negativo, composição, emoção, rotação de câmera, continuidade, lista de falhas), [`estilo-visual-oficial-dorama.json`](estilo-visual-oficial-dorama.json) (metadados e critérios consumíveis por agentes), e [índice próprio da série](../../dorama/README.md). AGENTS/README globais e canal/estratégia foram indexados; não afeta outros canais.
- **Amostra visual original enviada pelo usuário:** JPEG 864×1536 (apesar do nome `1000402660.png`), SHA-256 `2bab99670444001fbccf8a6c861276e93dfb56f04a33ba5f542698ad3419b2e1`. Foi realmente gravada no GitHub **uma miniatura fiel JPEG 96×171** em [`REFERENCIA-VISUAL-DORAMA-PREVIEW-96.jpg`](REFERENCIA-VISUAL-DORAMA-PREVIEW-96.jpg), SHA-256 `58f22420d123561623944e369c08c7d6a1808df29dc2e3f5d795129c5d2192b4` (Git blob SHA `aae13ef3aad66d220ce575fc26b7b4f994a49df8`). **Original full-res não versionado nesta atualização**. Miniatura não é imagem-mãe ou sprite.
- **Restrições editoriais preservadas:** a imagem amostral não é instrução de copiar trono/vitrais em todas as cenas; manter cenários coerentes com o roteiro e olhar dramático, com diversidade de ângulos narrativamente motivada. A **`SEM-GERACAO-NOVAS-IMAGENS.lock` ainda está ativa no EP01**: nenhum novo desenho, edição de IA, alteração de V5, render, upload YouTube ou remoção do lock. Arquivamento de prompt serve para futuras produções **explicitamente autorizadas**, não ativa qualquer workflow de geração.
- **Próxima ação:** usar a bíblia visual em futuros novos planos autorizados e manter 37-planos/163s como direção vigente. C01-P03 V5 é a versão técnica atual aguardando aprovação visual; C12 continua dependente dos PNGs/ZIPs originais. Verificar commit/merge antes de declarar os documentos na `main`.

## Como acrescentar progresso

Acrescentar uma seção datada com: objetivo e cena, arquivos alterados, commit realmente presente na `main`, run/workflow com resultado, mídia/artifact e SHA se houver, problemas abertos e próxima ação. Se ainda for apenas PR/branch, identificar explicitamente como **NÃO INTEGRADO**. Atualizar [ESTADO-ATUAL.md](ESTADO-ATUAL.md) **no mesmo lote de mudanças**; usar `estado-atual.json` para leitura programática. Nenhum agente deve depender do histórico de chats para reconstruir o projeto.

## 2026-11-15T09:36:17Z — diagnóstico automático de retomada

- Etapa: generate_character_bible; alvo: character-bible; bloqueio: provider_cost_permission_required.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-15T11:30:58Z — C01-P01 Remotion 60 frames pretos + SFX próprio

- GitHub Actions run \`43709191586\`, artifact \`vf-remake-c01-p01-opening-43709191586\` (90 dias); MP4 SHA \`75b8be46c7e609a1c9ff8afad0935bcbf8c6faa2126ba3c74cad3af540f3c44e\`, áudio SHA \`22879c38726c284f484c1f57c325fc053e0ba8591565e24eba92d4e9c827fb1d\`.
- Render Remotion real de 2 segundos somente; QA salvo no repositório, mídia guardada em artifact, sem aprovação humana ou upload YouTube. Próximo: âncora V2 e C01-P02.
