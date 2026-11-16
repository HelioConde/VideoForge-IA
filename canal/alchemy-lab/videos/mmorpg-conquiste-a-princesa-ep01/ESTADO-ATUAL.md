# Estado atual — MMORPG: Conquiste a Princesa (EP01)

## 16/11/2026 — medição REAL de pixels em camadas de Aldric, abstendo-se sem máscara de Elara

- [Workflow 43882516901](https://github.com/HelioConde/VideoForge-IA/actions/runs/43882516901) **SUCCESS**, 9 testes. Nova auditoria SHA-verificada e offline em `QA-CORES-PIXELS-FIGURINO-V2.json` e [relatório de cores reais](REVISAR-CORES-MEDIDAS-FIGURINO-V2.md). Foram auditados 6 PNGs; **4 camadas RGBA de Aldric** com alfa mensurável, **2 arquivos RGB de Elara** sem máscara semântica adequada (dados de cor da roupa omitidos deliberadamente).
- Nas camadas **misturadas** de Aldric, a vestimenta remanescente tem 24,24% de vermelho e 45,84% de pixels muito escuros; manto esquerdo 2,76% vermelho/74,89% escuro, manto direito 6,10% vermelho/65,14% escuro. Esses valores medem pixels efetivamente amostrados, MAS **não comprovam** se vermelho era exterior ou centro, nem cor exclusiva da barba. A cabeça contém rosto/cabelo/coroa, não uma máscara de barba. O close/câmera RGB de Elara inclui fundo/outros elementos e não permite atribuir roxo à blusa.
- O usuário já REPROVOU troca vermelho-preto e barba de Aldric, e roxo do peitoral palaciano de Elara. Essas decisões permanecem ativas; QA de pixels parcial NÃO aprova nenhuma imagem nem desfaz reprovação. Futura aprovação/reprovação verdadeiramente automática por **cores de subpartes** exige máscaras/ROIs válidas separadas de barba, centro e exterior do rei nas duas poses e do peitoral de Elara em cenas do palácio, com SHA e variante correta. Uma mudança de iluminação não é necessariamente troca de figurino.
- Nenhum PNG foi modificado, nenhuma chamada a modelo de imagem, nenhuma R2, rig oficial, MP4 completo ou upload YouTube nesta rodada.

## 16/11/2026 — filtro obrigatório por personagem: reprovação de cores e barba

- O proprietário confirmou que Aldric **sentado tem veste vermelha externamente com centro preto**, porém em pé apresenta **veste preta externamente com centro vermelho**; também muda a **cor da barba**, deixando de parecer o mesmo rei. Isto é uma REPROVAÇÃO CRÍTICA da referência, independentemente de SHA, resolução, beleza ou pose. Não foi escolhida uma cor de barba canônica sem prova; o usuário precisa confirmar uma referência específica para fixar sua tonalidade.
- Elara no palácio: a parte **roxa** da blusa/corpete some/muda entre imagens. **REPROVADA** a identidade/roupa da candidata atual; no disfarce de rua C07–C10, o roxo do traje real NÃO é obrigatório. Kael permanece sem defeito confirmado, mas **não aprovado**.
- [Filtro para revisão](RELATORIO-APROVACAO-REPROVACAO-FIGURINO.md) e três checklists permanentes `CHECKLIST-FIGURINO-ALDRIC.json`, `CHECKLIST-FIGURINO-ELARA.json`, `CHECKLIST-FIGURINO-KAEL.json` contêm regras de cores por área, barba/rosto, adornos, gola, capa, cabelo, cenários e variantes. [Run 43879682550](https://github.com/HelioConde/VideoForge-IA/actions/runs/43879682550) concluído com sucesso (11 testes). Acompanhamento de **7 tomadas com Aldric** e **6 com Elara real** é dependência da fonte reprovada, NÃO alegação de inspeção individual de pixels em 13 imagens.
- O script usa as diferenças que o proprietário comunicou, validadas semanticamente. **Ainda não existem ROIs/máscaras verificadas nem análise visual automática da roupa e barba em pixels**, portanto nenhuma imagem pode receber aprovação automática. R2 continua bloqueada, nenhuma nova chamada IA, MP4 oficial ou upload YouTube nesta correção.

## 16/11/2026 — detalhe do figurino e regra de 40 tomadas finalizados

- [Comparativo de detalhes run 43876165909](https://github.com/HelioConde/VideoForge-IA/actions/runs/43876165909) **SUCCESS**: dois JPEGs derivados `QA-ALDRIC-ROUPA-DETALE-V2.jpg` e `QA-ELARA-PEITORAL-ROXO-V2.jpg` com 4 imagens cada, original inteiro e *crop central geométrico* (NÃO é detector de personagem), hashes registrados em `QA-FIGURINO-DETALHES-V2.json`. Conferir [REVISAR-DETALHES-FIGURINOS-V2.md](REVISAR-DETALHES-FIGURINOS-V2.md). Sem criação de arte, alteração de PNGs ou aprovação imaginada.
- [Continuidade de 40 tomadas run 43876634280](https://github.com/HelioConde/VideoForge-IA/actions/runs/43876634280) **SUCCESS**: `CONTINUIDADE-FIGURINOS-V2-40-TOMADAS.json` é derivado do `remake-ep01-planos.json`, respeita 40 tomadas e 4890 quadros, e registra disfarce de Elara C07–C10 vs vestido palaciano com painel roxo a partir de C12; roupa real de Aldric constante. O velho `continuidade-figurinos-37-planos.json` é histórico, NÃO usado para instruir agentes nem construir novos vídeos.
- O registro mantém 0/2 figurinos completos aprovados (Aldric e Elara). A nova `character-bible-grounded-r2` exige SHA, imagem completa e decisão explícita do proprietário para ambas. SHA técnico, recorte central ou cenas legadas V1 não valem como aprovação; não renderizar MP4 oficial ou enviar para YouTube com arte reprovada.
- O workflow do coordenador central também testa a regra de 40 tomadas (sem Pillow/sem IA), para impedir regressão ao registro de 37.

## 16/11/2026 — próximas fontes de roupa encontradas sem gerar nenhuma imagem

- [Workflow de inventário 43874152372](https://github.com/HelioConde/VideoForge-IA/actions/runs/43874152372) finalizado com sucesso: examinou **6 PNGs já presentes** no repositório, calculou SHA, e criou `QA-INVENTARIO-FIGURINOS-V2.json` e [galeria revisável](REVISAR-OPCOES-FIGURINO-V2.md) com 3 imagens de Aldric e 3 de Elara. As fontes antigas V1 e suas camadas são apenas *candidatas*, não prova de que o traje é o original aprovado.
- Para Elara, as opções contêm o close importado do chat, o enquadramento original C12-P02 e a cena-mãe antiga C12; **o peitoral roxo tem de ser confirmado antes de aprovar a roupa palaciana completa**. Para Aldric, há RGB extraído da cena 01, camada de vestimenta e cena-mãe antiga; todas exigem inspeção e confirmação explícita do usuário. Nenhum candidato legado foi promovido a referência.
- `videoforge/art_request_gate.py` e workflow `production-art-by-request.yml` encerram com **skip/no-op** se um pedido de geração está concluído/reprovado, se seu PNG+SHA já foi arquivado, ou se a futura `character-bible-grounded-r2` ainda não tem referências de vestuário aprovadas com SHA. Isso evita reprocessar o pedido de arte do run 43868021687; a falha anterior no run 43872223471 foi uma proteção contra repetição, não nova imagem.
- O QA de arquivamento foi alinhado à autorização V2 vigente, mas segue no modo **teste apenas em memória, sem gasto, sem render e sem publicação**. As 40 tomadas continuam planejadas e a aprovação de figurino permanece em 0/2.

## 16/11/2026 — usuário reprovou figurino da prancha V2 referenciada

- `character-bible-grounded.png` SHA `6ed16d498df46b59c38e9c34ab25127b5b032159ab3289c073ac0058fcda6fc3` (run 43868021687) está **tecnicamente íntegro, mas artisticamente REPROVADO**. Diferenças mais graves: vestes do rei Aldric divergentes; parte roxa da blusa/peitoral da princesa Elara inconsistente ou ausente numa das versões. Não afirmar defeito específico de Kael que não foi relatado.
- Regras novas em `REVISAO-FIGURINO-V2.json` e `CONTRATO-FIGURINO-V2.json` exigem fidelidade de vestes, inclusive detalhes pequenos. Nova `character-bible-grounded-r2` foi **planejada, mas bloqueada** até existirem fontes completas, SHA e aprovação humana do traje de Elara e Aldric. Não inferir roupa do rei por prompt e não fazer gasto duplicado.
- Continuam bloqueados imagem-mãe C01-P02, rigs oficiais, MP4 completo e publicação, sem mexer nos PNGs originais ou nas 40 tomadas.

## 16/11/2026 — cenas V2 aceitam referência vertical original sem esticar

- Corrigido o bloqueio de dimensão que tornaria a nova `character-bible-grounded.png` 1199×1312 inutilizável mesmo após aprovação humana. `cinematic_direction._remake_anchor_state` agora aceita **somente PNG retrato SHA-verificado dentro de limites técnicos** para identidade; `remake_reference.prepare_remake_reference` suporta os dois IDs `character-bible` (texto) e `character-bible-grounded` (2 fontes anexadas), com prova de origem estrita e SHA; a cópia fornecida ao editor conserva EXATAMENTE os bytes sem redimensionar.
- `production_scenes.reference_bytes(...,allow_grounded=True)` é usado somente no EP01 remake ativo, após verificação de aprovação da âncora no manifesto. A cena-mãe de saída continua com canvas exigido **1024×1536** e rig por partes reais. Outras produções legadas continuam exigindo 1024×1536 como referência; não se altera sua política. A API de `gpt-image-2` dispensa o parâmetro `input_fidelity`.
- **Nenhuma aprovação foi registrada** nesta mudança, logo o fluxo de cenas continua bloqueado até revisão visual; nenhuma imagem adicional foi solicitada. Testes de path, SHA, proveniência e não-distorção usam apenas PNGs sintéticos temporários.

## 16/11/2026 — segunda prancha ancorada de verdade nos PNGs originais e QA comparativo

- [Geração real 43868021687](https://github.com/HelioConde/VideoForge-IA/actions/runs/43868021687) **SUCCESS**: 1 chamada de `gpt-image-2` para `character-bible-grounded` com **2 fontes PNG originais realmente anexadas** via `images/edits`, fontes com SHA exatos Kael `edb751cd...` e Elara `bf199f3e...`; PNG 1199×1312 arquivado permanentemente com SHA `6ed16d498df46b59c38e9c34ab25127b5b032159ab3289c073ac0058fcda6fc3` no caminho `assets/geracoes/production-art-request/43868021687/character-bible-grounded.png`. A prancha antiga apenas textual segue intacta (run 43784005362).
- [QA comparativo 43868899761](https://github.com/HelioConde/VideoForge-IA/actions/runs/43868899761) **SUCCESS, 3 testes**: comparação tripla offline (original + primeira prancha textual + nova prancha de referências) gerou `QA-KAEL-TRIPLO-V2.jpg`, `QA-ELARA-TRIPLO-V2.jpg`, `QA-IDENTIDADE-GROUNDED-V2.json` e `REVISAR-GROUNDED-V2.md`. O QA confere SHA e `production.json` que comprova que os dois originais foram anexados. Nenhuma chamada paga adicional para os JPEGs.
- A nova prancha é **candidata**, sem aprovação visual; o modelo devolveu 1199×1312 em vez de 1024×1536. O relatório não altera o original nem a versão antiga. Aldric continua sem referência individual, e o primeiro movimento real da espada C01-P02 depende da mãe da tomada e quatro camadas RGBA.
- O coordenador do EP01 deve registrar `grounded_candidate` com SHA/proveniência, manter `human_visual_review_pending` e NÃO liberar cenas, rig, MP4 completo ou YouTube pelo mero sucesso do gerador.

## 16/11/2026 — corrigida a geracao textual da primeira prancha: nova candidata com referencias reais anexadas

- Diagnosticado: a `character-bible` do run 43784005362 foi produzida por `/v1/images/generations` com **texto apenas**, apesar do prompt mencionar as imagens originais. Isso explica parte do risco de inconsistência e não valida identidade.
- Nova candidata isolada `character-bible-grounded`: `videoforge.grounded_identity.edit_payload` exige as duas fontes originais de Kael/Elara com SHA exatos e anexa **os PNGs reais** via `/v1/images/edits`, uma chamada de modelo `gpt-image-2` por run. O modelo usa Kael como fonte 1, Elara como fonte 2. Aldric não tem original individual SHA-verificado, portanto exige revisão separada.
- O produtor `production_art.py` preserva arquivo, SHA, dimensão real, nomes/hash das fontes e bandeiras `human_visual_approval=false`, `youtube_uploaded=false`. O asset novo jamais substitui `character-bible.png` anterior ou vira âncora sem revisão. Criar o pedido `pedido-geracao-arte.json` usa autorização permanente do usuário, mas custos e cotas reais do provedor continuam aplicáveis; não repetir HTTP 429 ou 502 automaticamente.
- O fluxo mantém 40 tomadas e a regra das quatro camadas C01-P02 com rig real. Após resultado e QA técnico, comparar a nova candidata aos dois PNGs originais antes de promover qualquer identidade canônica.

## 16/11/2026 — originais de Kael e Elara recuperados e comparações V2 prontas

- [Importação 43850389922](https://github.com/HelioConde/VideoForge-IA/actions/runs/43850389922) **SUCCESS**: 3 fontes originais por SHA (Kael, Elara, câmera C12-P02), 0 bytes de arte original modificados. O relatório `qa-referencias-chat-cinematograficas.json` agora marca `ORIGINAL_EXACT_SHA_VERIFIED` nos dois closes e `EXACT_SOURCE_ARCHIVED` na câmera.
- [Autonomia 43850993654](https://github.com/HelioConde/VideoForge-IA/actions/runs/43850993654) **SUCCESS**: `reference_sources_current` atualizado para 2/2 closes e câmera C12; pendências de upload zeradas; bloqueio mudou de `original_kael_elara_sha_sources_missing` para `human_visual_review_pending`. Nenhum novo pedido pago de character-bible.
- [Comparação offline 43851593794](https://github.com/HelioConde/VideoForge-IA/actions/runs/43851593794) **SUCCESS**: duas prévias JPEG e `QA-COMPARACAO-IDENTIDADE-V2.json` gerados a partir dos bytes reais sem IA externa. Visualizar `REVISAR-IDENTIDADE-EP01-V2.md` e comparar rosto, olhos, cabelo, roupa e anatomia de Kael e Elara contra `character-bible.png` V2. A identidade de Aldric ainda precisa de fonte/revisão própria.
- `character-bible` gerada por texto sem anexar referências, **não aprovada**. As fontes SHA não autorizam automaticamente a nova identidade, C01-P02, rigs, MP4 ou YouTube. Próximo marco é decisão explícita da revisão visual. O V2 permanece em 40 tomadas; documentos e histórico preservados, nenhum refazimento da V1.

## 16/11/2026 — checkpoint confirmado: referencias originais e C12 aguardam bytes, CI verde

- [Importador de originais 43823567116](https://github.com/HelioConde/VideoForge-IA/actions/runs/43823567116): **SUCCESS**, 13 testes, nenhum PNG novo ou alterado; os dois originais de identidade Kael/Elara e a câmera C12-P02 ainda nao foram enviados/arquivados por SHA (0/3). Busca por caminhos exatos no historico de commits GitHub também nao achou copia anterior. Importar `uploads/alchemy-ep01-cinema-3-originais.zip` usando `scripts/enviar-referencias-cinema.ps1` quando os bytes originais estiverem disponíveis.
- [Coordenador V2 43823850136](https://github.com/HelioConde/VideoForge-IA/actions/runs/43823850136): **SUCCESS**, 95 testes; estado `original_kael_elara_sha_sources_missing` e lista de tres caminhos faltantes gravados automaticamente em `estado-atual.json`. Nenhuma tentativa paga duplicada ou aprovacao humana inventada.
- [C12 source-preflight 43824476754](https://github.com/HelioConde/VideoForge-IA/actions/runs/43824476754): **SUCCESS** com 11 testes; 0/9 PNGs técnicos originais verificados; `C12_DISPATCH_WAIT_FOR_EXISTING_SOURCE_BYTES` classificado corretamente; **render-draft Remotion SKIPPED** (não iniciou contêiner pesado). O controle testa SHA, integridade e política ativa, não cria imagens nem MP4 fictício.
- `C01-P02` continua planejada para 4 partes RGBA originais (underlay, sheath, blade, hand), ThreeCanvas + Remotion sem transformar o PNG inteiro em movimento falso. Identidade de Kael/Elara/Aldric não foi aprovada; vídeo oficial e YouTube continuam bloqueados.
- Os agentes devem preservar exatamente os checkpoints e não reiniciar obras nem copiar imagens legadas V1 como se fossem as fontes aprovadas V2.

## 16/11/2026 — corrigida espera técnica de C12 após o importador

- [Run anterior 43823602889](https://github.com/HelioConde/VideoForge-IA/actions/runs/43823602889) falhou por exigir o lock V1 já arquivado. O `c12_technical_preview.policy()` agora exige versão V2 ativa e bloqueio de vídeo oficial/YouTube, preservando limites de geração. Não cria imagem nem aprova arte.
- `c12-after-import.yml` passa a verificar automaticamente o código corrigido, testar e classificar os 9 arquivos técnicos originais. Faltando PNGs, retorna `ASSETS_PENDING` e espera pelos originais sem despachar Remotion. Arquivos com SHA errado continuam falha bloqueante; `character-bible` V2 não substitui os assets C12.

## 16/11/2026 — agente identifica automaticamente as fontes faltantes antes da revisão

- `videoforge.remake_autopilot.choose_next()` agora consulta a integridade exata dos dois closes originais e da candidata de câmera C12, sem IA nem custo: se os closes de Kael/Elara estiverem ausentes, classifica o bloqueio como `original_kael_elara_sha_sources_missing` (em vez de pedir aprovação sem fontes); se existir arquivo errado, utiliza `invalid_original_reference_sha_stop`.
- Os três caminhos pendentes, o ZIP e o script de importação são incluídos em `source_readiness` e nos relatórios da fila de 40 tomadas. O agente nunca libera uma segunda referência paga ou aprovação visual por este diagnóstico. O original de Aldric permanece sem referência SHA individual aprovada.
- Quando o ZIP certo for anexado ao repositório, o importador por SHA estará pronto para arquivar automaticamente, e o coordenador deverá avançar para a **comparação visual humana**, sem misturar os PNGs antigos V1 com a identidade do remake V2.

## 16/11/2026 — conserto da importação das fontes cinematográficas V2

- Descoberta: a importação original de Kael/Elara/C12-P02 estava presa ao arquivo `SEM-GERACAO-NOVAS-IMAGENS.lock`, já arquivado após autorização de geração do remake V2; a verificação falharia mesmo com um ZIP original correto. O verificador agora exige `estado-atual.json` e `autonomy-policy.json` ativos, preserva proibição de publicação e permite apenas **importação de arquivos existentes sem chamar IA**.
- Fontes exigidas e já documentadas por SHA256: `kael-close-salao.png` (edb751cd...), `elara-close-trono.png` (bf199f3e...) e `confronto-trono-c12-p02.png` (01eb7c12...). Os originais **não foram encontrados** na árvore atual do GitHub nem nos arquivos recuperáveis do projeto; não confundir imagens V1 com essas fontes. Nenhum dos três hashes deve ser presumido verificado até o ZIP passar pelo importador.
- O relatório `QA-CHARACTER-BIBLE-V2.json` passa a calcular a disponibilidade das fontes **em tempo real por SHA**, em vez de usar marcador estático `original_reference_sha_missing_in_repo`. Isso não aprova automaticamente a arte V2 gerada por texto. A fonte individual de Aldric continua sem hash aprovado arquivado.
- Para importar quando o ZIP exato estiver no computador: executar `powershell -File scripts/enviar-referencias-cinema.ps1 -ZipPath <caminho-do-zip>`. O workflow `qa-alchemy-chat-cinematic-references.yml` confere os 3 originais, publica evidências SHA/CRC e mantém MP4/YouTube bloqueados.

## 15/11/2026 — etapa de referência V2: 86 testes e requisitos reais de identidade

- [Run de QA 43786791088](https://github.com/HelioConde/VideoForge-IA/actions/runs/43786791088) **SUCCESS**: 86 testes executados (6 pulados por requisitos do runner); SHA/PNG da `character-bible.png` conferidos; relatório permanente `QA-CHARACTER-BIBLE-V2.json` gerado na `main` pelo próprio workflow. O coordenador não disparou outra chamada paga.
- Novo critério de revisão: aparência de Kael, Elara e Aldric derivada das descrições oficiais de `production-art.json`. A imagem real foi produzida **somente por prompt textual**; as imagens antigas aprovadas não estavam anexadas ao request nem possuem SHA original importado neste estado. Não é possível atestar correspondência visual exata sem comparar as fontes originais. Nenhuma aprovação visual/identidade inferida.
- Proximo passo de cena: revisar a prancha real, importar referencias originais aprovadas com SHA, validar tres identidades e depois trabalhar nas imagens-mae V2 e nas quatro camadas RGBA reais da espada `C01-P02`. Ainda nao existe MP4 oficial completo nem upload no YouTube.

## Continuidade V2: bloquear geracao paga duplicada e auditar referencia real

- Qualquer `production-art-by-request.yml` (inclusive workflow_dispatch manual) DEVE consultar o diretorio permanente `assets/geracoes/production-art-request/<run_id>/`, conferir manifesto, SHA256, integridade PNG e dimensoes antes de criar a mesma arte. Se ja houver PNG valido, abortar com `PRODUCTION_ART_ALREADY_ARCHIVED_SHA_VERIFIED` antes de chamar o provedor. Se o arquivo ja existir mas estiver incompleto/alterado, bloquear para diagnostico, nunca regenerar cegamente.
- `python -m videoforge.reference_art_qa --sync` grava `QA-CHARACTER-BIBLE-V2.json` com tamanho real, SHA e proposta MATEMATICA de encaixe no formato alvo sem editar pixels. Trata-se de evidencia tecnica, NAO de aprovacao de identidade, desenho, estilo ou rig. O PNG de 1199×1312 continua intacto; NAO usar como imagem-mae oficial nem renderizar o episodio antes de revisao humana.
- As proximas 39 tomadas visuais, as 4 partes originais da espada em C01-P02 e o MP4 completo continuam pendentes de revisao visual/recortes reais. Gerar referencias adicionais apenas se for de fato necessario, com reserva identificavel e sem duplicacao.

## 15/11/2026 — sessão OAuth recuperada; primeiro PNG V2 real gerado e preservado

- [Health após login 43783956474](https://github.com/HelioConde/VideoForge-IA/actions/runs/43783956474) **SUCCESS**: 1 conta elegível, OAuth válido, geração liberada. A reconexão funcionou de fato.
- [Gerador 43784005362](https://github.com/HelioConde/VideoForge-IA/actions/runs/43784005362) recebeu imagem real do provedor; etapa de geração falhou exclusivamente por `PRODUCTION_ART_DIMENSIONS_INVALID`: PNG gerado em **1199×1312**, diferente do tamanho pedido **1024×1536**. Mesmo com job marcado FAILURE, o arquivador salvou `assets/geracoes/production-art-request/43784005362/character-bible.png` e `manifesto-geracoes.json`, SHA256 **47b7b0cd83689a72a44e7e44dd61c5ba6beabcfc1e411f0e3850fc78f0e8b5c4**. Sem mascarar as dimensoes, esticar imagem, gerar novamente ou afirmar cobranca confirmada.
- Correção de `production_art.py`: distinguir PNG com dimensões válidas mas fora do pedido; preservar pixels originais e emitir `valid_png_noncanonical_dimensions_visual_review_pending`; `remake_autopilot.py` reforça SHA+CRC e registra dimensoes na referencia candidata. **Aprovação visual NÃO realizada**, sem render oficial e sem upload YouTube. Repetição de geração proibida enquanto houver este PNG valido.

## 15/11/2026 — corrigido erro PROXY_API_KEY local ausente

- Relato do responsavel: `renovar-sessao-videoforge.ps1 -Container chatgpt-codex-proxy` falhou ao exigir `PROXY_API_KEY` no container preexistente.
- [Correção 497094f](https://github.com/HelioConde/VideoForge-IA/commit/497094f829098dc32fe686f97425702ad436fb91): renovacao usa um container isolado com chave efemera, porta somente localhost e volume Docker temporario. O container antigo nao e modificado. Login no navegador e importacao privada seguem necessarios antes da retomada automatica.
- [Testes 43782680348](https://github.com/HelioConde/VideoForge-IA/actions/runs/43782680348) **SUCCESS**: 11 testes offline e sintaxe de ambos os scripts PowerShell. Nao foi feito login real no computador nesta etapa, nem nova geracao. Sem PNG V2 aprovado, sem MP4, sem upload YouTube.

## 15/11/2026 — retomada de OAuth preparada e CI offline aprovado

- [Commit de automacao 5cf744c](https://github.com/HelioConde/VideoForge-IA/commit/5cf744cd4b1421a2212aead68937796558843c4f): reconexao local chama `proxy-health-official.yml` com `resume_remake=true`; conta elegivel confirmada primeiro, script `remake_recovery.py` reserva unica tentativa na main e somente depois dispara `production-art-by-request.yml`. Testes anti-duplicacao, ausencia de PNG anterior, bloqueio de despesas e publicacao.
- [CI de validacao 43781600055](https://github.com/HelioConde/VideoForge-IA/actions/runs/43781600055): **SUCCESS**, 11 testes offline aprovados, sintaxe dos dois scripts PowerShell aprovada; job de health real em push pulado corretamente. O health manual apos login e separado dos testes de codigo.
- **Bloqueio real ainda vigente:** nao ha login OAuth renovado comprovado nem novo PNG gerado; ultima conta importada tinha token expirado. Uma autenticacao no navegador do computador local continua necessaria. A autorizacao permanente de geracao ja esta ativa; o fluxo continua depois da reconexao sem solicitar confirmacao para cada chamada. Nenhum MP4 oficial ou upload YouTube foi realizado.

## 15/11/2026 — automacao segura de retomada depois da reconexao OAuth

O repositorio segue sem nova execucao de imagem desde `43766496772` (tentativa 2): ultimo diagnostico revelou 1 token expirado, 0 contas elegiveis e refresh remoto 502. **Nao existe prova de que o login local ja foi renovado.** Preparada a retomada que exige 1 acao inicial de autenticar no navegador e em seguida executa toda a validacao e 1 nova tentativa da referencia sem pedir liberacao por imagem. O script `renovar-sessao-videoforge.ps1` faz importacao dos secrets e dispara `proxy-health-official.yml` com `resume_remake=true`. Com health aprovado, `remake_recovery.py` verifica o pedido anterior, arquivamento PNG+SHA e regras, grava reserva unica no estado/main e despacha `production-art-by-request.yml`. Nao criar nova imagem sem credenciais validas; nao declarar arte pronta antes do resultado.

## 15/11/2026 — recuperacao OAuth: CI de codigo aprovado, credencial antiga bloqueada
- [Run 43779683428](https://github.com/HelioConde/VideoForge-IA/actions/runs/43779683428): **8 testes offline PASS**, parser PowerShell confirmou os scripts `renovar-sessao-videoforge.ps1` e `migrar-codex-proxy.ps1` sem executar login. O job completo ficou **FAILURE esperada de autenticacao**: o preflight real detectou corretamente `PROXY_OAUTH_SESSION_EXPIRED`; nenhum PNG ou chamada de imagem foi emitido.
- O token importado previamente expirou, a tentativa de renovacao upstream no GH Actions falhou (HTTP 502). **Necessaria autorizacao interativa da conta no navegador**, operacao distinta da permissao permanente de criar imagens. No computador do proprietario, rodar `./scripts/renovar-sessao-videoforge.ps1 -Container chatgpt-codex-proxy` a partir do PowerShell no clone do repositorio (use `.\\scripts\\...` no Windows); autorizar no navegador, reimportar secrets, validar workflow `proxy-health-official.yml`, depois retomar a geração sob SHA/QA e sem duplicacao.
- C01-P02 e o MP4 de 163s permanecem pendentes. YouTube nao publicado. Nao marcar a fase como pronta enquanto a conta nao estiver elegivel.

## 15/11/2026 — incidente OAuth do proxy diagnosticado, recuperacao segura preparada

**Evidencia real de GitHub Actions:** [health 43778717568](https://github.com/HelioConde/VideoForge-IA/actions/runs/43778717568) passou 200/200; [rerun 43766496772, tentativa 2](https://github.com/HelioConde/VideoForge-IA/actions/runs/43766496772) passou health mas `/v1/images/generations` respondeu **HTTP 502**, sem criar PNG; [auditoria 43778920877](https://github.com/HelioConde/VideoForge-IA/actions/runs/43778920877) encontrou **1 conta, 0 elegiveis, OAuth expirado**; [refresh 43779044584](https://github.com/HelioConde/VideoForge-IA/actions/runs/43779044584) tentou renovacao pelo `/admin/accounts/:id/refresh`, que tambem respondeu **HTTP 502**. Nenhuma arte nem aprovacao foi criada. Nao declarar cobranca confirmada ou repetir a requisicao cegamente.

**Correcao de software:** `proxy_images.health` agora confere elegibilidade e validade OAuth via `/admin/accounts` em vez de aceitar somente `accounts>=1`; emite `PROXY_OAUTH_SESSION_EXPIRED` sem expor email/IDs/tokens e bloqueia geracao antes do modelo. O importador PowerShell recusa snapshot expirado. Novo `scripts/renovar-sessao-videoforge.ps1` suporta reautenticacao interativa no proxy Docker do proprio usuario, seguida por reimportacao privada dos GitHub Secrets. Revalidar no CI; **relogin humano e necessario** porque o refresh remoto nao funcionou. Autorizacao editorial para imagens permanece vigente; somente credenciais precisam de renovacao.

## 15/11/2026 — primeiro disparo autônomo executado, proxy HTTP 503
- [Coordenador 43766477030](https://github.com/HelioConde/VideoForge-IA/actions/runs/43766477030) **SUCCESS**: preflight e testes passaram, reserva durável de uma chamada registrada na main antes de `workflow_dispatch`.
- [Gerador 43766496772](https://github.com/HelioConde/VideoForge-IA/actions/runs/43766496772) **FAILURE**: proxy efêmero iniciou e `/health/live` respondeu; a checagem autenticada `python -m videoforge.proxy_images health` retornou **HTTP 503** antes de executar `production_art`. **Nenhuma imagem PNG foi criada nem arquivada; nenhuma cobrança de geração pode ser afirmada.**
- Intenção persistida em `estado-atual.json` com `status=blocked_proxy_authenticated_health_http_503`; não emitir segundo pedido sem diagnosticar proxy/conta/cota. **A autorização permanente continua válida**, sem necessidade de solicitar outra aprovação ao responsável depois de resolver falha técnica. YouTube segue proibido.

## 15/11/2026 — autorização permanente de chamadas para produzir o remake

**Decisão expressa do responsável:** o sistema e seus agentes estão autorizados a fazer todas as chamadas necessárias de IA e geração de imagem **para o EP01 V2** sem solicitar aprovação individual a cada execução. Escopo gravado em `autonomy-policy.json`, manifesto oficial, arquivo de estilo, `AGENTS.md` e skill. A cada run, somente **uma chamada cobrável**; não existe teto editorial para o episódio. Cobrança/cota do provedor podem continuar existindo. `auto_dispatch_generation=true`.

**Execução autônoma implementada neste avanço:** o coordenador de GitHub Actions pode reservar em `estado-atual.json` uma intenção idempotente para a primeira referência `character-bible`, persistir antes de executar `gh workflow run production-art-by-request.yml` e recusar novos disparos para o mesmo alvo sem verificação. A atualização do código/política e o teste do CI precisam confirmar que o workflow iniciou e qual foi o resultado real. **Não declarar PNG, cobrança, arte aprovada ou MP4 sem evidência.** A mãe C01-P02, quatro camadas/rig e YouTube permanecem pendentes até os respectivos controles de QA/proveniência.



## 15/11/2026 — guarda de proveniência e antirrepetição C01-P02 (CI aprovado)

O gerador dedicado de `underlay`, `sheath`, `blade` e `hand` agora consulta o arquivo **permanente** de produções com PNG+SHA da **mesma imagem-mãe e mesmo run** antes de qualquer chamada ao proxy, inclusive em um runner novo. Camada válida já arquivada impede nova cobrança acidental; a camada rejeitada por QA técnico não é confundida com trabalho concluído. O empacotador passa a exigir para **todas** as quatro peças `scene=c01`, `shot_id=C01-P02`, `part_id`, `source_archive_producer` e `source_archive_run_id` da mãe selecionada. Testes cobrem repetição, troca de tomada e troca de run. Qualquer retrabalho artístico voluntário precisa de revisão explícita, não de rerun cego.

**CI confirmado:** [run 43762440988](https://github.com/HelioConde/VideoForge-IA/actions/runs/43762440988) **SUCCESS** com 9/9 testes do gerador/fluxo; [run 43762352508](https://github.com/HelioConde/VideoForge-IA/actions/runs/43762352508) **SUCCESS**, scanner 4/4 e 25/25 testes de pacote/mascara com PNGs sintéticos temporários. Job de pacote com fonte real corretamente **skipped**. O primeiro run do editor 43762352543 falhou por expectativa antiga do teste de duplicação, corrigida em `4b57e743af2bfb844a50351b2e2c90634b00ea39` e validada no segundo run. **Nenhuma chamada de IA foi realizada.** Nada foi gerado de novo: âncora V2 sem SHA humano aprovado; mãe C01-P02 e as quatro camadas reais ainda ausentes. Política `paid_provider_calls_approved=false`, máximo zero chamadas; nenhum MP4 real da C01-P02, nenhuma publicação. Próximo passo: obter âncora V2 verdadeira aprovada, mãe SHA-verificada e só depois produzir camadas em fluxos autorizados; as proteções anti-repetição já estão validadas no CI.

### Validação da auditoria de geometria no GitHub — 15/11/2026

**Pipeline testado até o ponto permitido pela arte disponível:**

- [Run 43758686070](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686070) — **SUCCESS**: 23 testes aprovados no runner GHCR com FFmpeg e PNGs sintéticos temporários. Verificados bbox/centroide de lâmina, bainha, mão; QA de recomposição, SHA e origem, relatório idempotente, rejeição de aprovação falsificada e proibição de underlay RGBA em vez de RGB opaco. O scanner real reportou `REMAKE_SWORD_V2_ANCHOR_NOT_APPROVED_OR_VERIFIED`; job de arte real corretamente **skipped**.
- [Run 43758686035](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686035) — **SUCCESS**: preflight da espada e smoke ThreeCanvas com 2 frames sintéticos diferentes; render com fonte real pulado.
- [Run 43758686062](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686062) — **SUCCESS**: 70 testes de autonomia/roteiro/160 instruções aprovados, 40 tomadas/39 visuais; blocker de gastos `provider_cost_permission_required` preservado.
- [Run 43758686092](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686092) — **SUCCESS**: 23 testes Python e QA do compositor Remotion sem gerar vídeo.
- Falha intermediária [43758376230](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758376230): único teste esperava mensagem errada após substituir relatório por JSON muito curto; **não era falha de segurança**. Corrigido em `21a48bdf6c257d9bd8609f7c540585f4362ba6be`, que agora adultera relatório de tamanho válido, falsifica `official_video_approved=true` e comprova bloqueio em `--verify-report`. Run seguinte foi aprovado.
  
**Estado fiel:** a análise geométrica está integrada e testada com PNGs reais de bytes **sintéticos só para CI**. Nenhuma imagem oficial V2 C01-P02 existe ou foi medida, não há MP4 real dessa tomada, não houve geração paga nem upload YouTube. O relatório de geometria de produção só aparecerá depois de âncora/arte próprias devidamente aprovadas.

## C01-P02 — calibração geométrica dos PNGs reais adicionada ao workflow (15/11/2026)

**Etapa técnica em código, sem arte paga:** `videoforge/remake_rig_geometry.py` analisa máscara de mão, lâmina e bainha em pixels reais após `validate_package` SHA/underlay/recomposição. Registra bbox, centroide, área de alfa, pivô candidato, as quatro poses nos frames locais 0/7/72/89 e SHA de origem/direção em `mask-geometry.qa.json`. O nome "geometria medida" é válido somente quando **PNG original foi realmente decodificado**; nunca preencher valores fictícios no arquivo editorial.

**Integração automática:** `remake-sword-pack.yml` medirá e anexará relatório ao artifact de fonte C01-P02 se o run possuir mãe/4 camadas genuínas; `remake-sword-preview.yml` exigirá e recalculará o relatório antes de renderizar. O agendador `remake_starter` agora marca as 39 tarefas visuais como dependentes de geometria de máscara e não as marca aprovadas. Testes temporários com fixtures isoladas em runner com FFmpeg cobrem pacote válido, máscara inválida, SHA/origem divergente, idempotência e relatório adulterado.

**Estado:** nenhum PNG real dessa tomada foi criado e nenhum relatório geométrico de produção existe; `human_anatomy_contact_review_required=true`, `official_video_approved=false`, sem gastos adicionais. Os testes GitHub devem ser verificados antes de declarar etapa concluída. Os demais 38 cortes visuais ainda não têm pipeline de medição ligado — este é o início reutilizável.

## Integração V2 40 tomadas, 160 ações e áudio original — QA GitHub concluído (15/11/2026)

**Resultados verificados em branch `main`:**

- [Run 43755753904](https://github.com/HelioConde/VideoForge-IA/actions/runs/43755753904) **SUCCESS**: EDL V2 40 planos, roteiro e checkpoint.
- [Run 43755753902](https://github.com/HelioConde/VideoForge-IA/actions/runs/43755753902) **SUCCESS**: TypeScript/Remotion de 40 tomadas, validação de abertura com WAV por SHA e bloqueio de render sem fontes.
- [Run 43756504753](https://github.com/HelioConde/VideoForge-IA/actions/runs/43756504753) **SUCCESS**: 56 testes Python, `REMAKE_MOTION_40_VALIDATED 40 shots 160 keyed stages` e fila `40/39` sem imagens.
- [Run 43756504858](https://github.com/HelioConde/VideoForge-IA/actions/runs/43756504858) **SUCCESS**: validador do compositor, EDL e 160 etapas, com Node/TypeScript completo.
- [Run 43756803890](https://github.com/HelioConde/VideoForge-IA/actions/runs/43756803890) **SUCCESS**: 60 testes Python passaram, SHA original C01-P01 verificado, fila de 40 tomadas/39 visuais/160 direções, bloqueio `provider_cost_permission_required` preservado.
- [Run 43756803794](https://github.com/HelioConde/VideoForge-IA/actions/runs/43756803794) **SUCCESS**: 14 testes Python e compositor Remotion passaram. A WAV original foi reconstruída e gravada localmente no runner do QA; SHA `22879c38726c284f484c1f57c325fc053e0ba8591565e24eba92d4e9c827fb1d` conferido, sem usar artifact antigo e sem renderizar o vídeo.

**Checkpoint final desta implementação:** compositor preparado para exatamente 40 tomadas, EDL V2 editorial preservando EDL V1 histórica, 160 direções por frame, fila dos agentes com movimentos e QA, áudio original C01-P01 reproduzível; **39 imagens-mãe/rigs continuam ausentes**. Não há novo MP4 C01-P02 nem MP4 completo do remake. Não houve geração de imagens paga, aprovação humana falsa ou upload YouTube. A única mídia realmente renderizada para esta versão permanece a abertura técnica preta C01-P01 (2 s) em [artifact 14159517637](https://github.com/HelioConde/VideoForge-IA/actions/runs/43709191586/artifacts/14159517637).

**Próximo trabalho autônomo seguro:** adquirir referência canônica V2 real e aprovada e autorização específica de uso de provedor, então gerar mãe por plano e calibrar RGBA/pivôs medidos da própria arte. Manter QA e materiais em arquivos principais, sem refazer o que foi validado.

## C01-P01 — audio original reproduzível e SHA-verificado para compositor V2 (15/11/2026)

**Nova etapa:** `videoforge/remake_episode_audio.py` recria localmente a WAV original de 2s/48kHz de `remake_opening.py`, confere o SHA dos bytes com a prova permanente `QA-C01-P01-REMAKE-V2.json` e o manifesto `remake-ep01-planos.json`, e só então a armazena como `motion-remotion/public/vf-remake/c01-p01/sword-original.wav` para um render futuro. Aceita reexecução idempotente, mas bloqueia arquivo adulterado, origem indevida, caminho simbólico ou SHA divergente. Sem usar artifact temporário, serviço de áudio pago ou música de terceiros.

**Testes:** `tests/test_remake_episode_audio.py` verifica PCM/SHA, reexecução, QA alterado e proteção de caminhos. O workflow de compositor prepara a WAV real, mas **continua sem renderizar episódio**: faltam 39 imagens com rigs e revisão visual. A aprovação de áudio não substitui aprovação artística. CI pendente de confirmação neste registro.

## Direção articulada de todas as 40 tomadas — 160 etapas temporizadas (15/11/2026)

**Preparado em código e JSON:** `remake-v2-motion-directions.json` contém quatro momentos detalhados por tomada: estabelecer quadro, antecipar gesto, executar rig e resolver ação. Exige 40 tomadas/14 cenas/4890 frames/30fps e mantém C01-P02 espada nos quadros locais 0,7,72,89, C12-P01 olhos nos 0,4,86,119. Novas tomadas recebem direção própria: C01-P05 luvas/lanças, C08-P04 roda/Elara e C12-P04 broche/dedos/vestido. Cada etapa indica texto de atuação, peças RGBA, lente, eixo, orientação, narração/SFX e QA.

**Programa autónomo:** `videoforge/remake_motion_directions.py` valida a direção contra o roteiro e o manifesto 40-shot; `videoforge/remake_starter.py` inclui `motion_phases`, `motion_required_parts`, `motion_qa_requirements` e fingerprint das instruções em cada unidade da fila. Assim um agente que retome a tomada não pode saltar a direção e criar movimentos genéricos de PNG inteiro.

**Importante:** os 160 itens são direção editorial, **não são 160 frames renderizados nem medidas anatômicas prontas**. `pivots_measured_from_real_art=false`, `technically_calibrated=false`, `human_visual_approved=false`. Nenhuma imagem real adicional, nenhum MP4 oficial, nenhuma chamada paga/YouTube. Testes do GitHub Actions pendentes neste registro.

## C40 V2 — renderizador oficial e EDL sem perder audio original (15/11/2026)

**Problema corrigido em código:** `motion-remotion/src/cinematic-timeline.ts` ainda exigia 37 tomadas, enquanto o roteiro/manifesto agora exigem 40. Contrato atualizado para **40 tomadas, 39 visuais, 4890 frames/163s**. Os inserts C01-P05 (310–359), C08-P04 (2880–2939), C12-P04 (4290–4349) possuem ranges obrigatórios; C01-P02 continua 60–149. Nova `remake-v2-cinematic-edl.json` representa somente o **planejamento V2 sem aprovação** e é compilada por `videoforge/remake_v2_edl.py`, sem alterar `timeline-cinematografica.json` V1 de 37 tomadas.

**Audio abertura:** o compositor Remotion agora exige a WAV original `vf-remake/c01-p01/sword-original.wav` e seu SHA auditado `22879c38726c284f484c1f57c325fc053e0ba8591565e24eba92d4e9c827fb1d`. O arquivo binário precisa ser materializado com prova de SHA **antes** de render completo; o manifesto editorial não é aprovação de áudio disponível. Não foi criado vídeo oficial, nem imagem, nem upload; custo de provedor continua bloqueado.

**CI:** testes Python de equivalência entre 40 shots do roteiro/manifesto e EDL, mais TypeScript/Remotion para bloqueio de assets e áudio; resultados aguardam execução GitHub Actions.

## V2 — planejamento ampliado para 40 tomadas (decisão editorial 15/11/2026)

### Verificação automatizada dos 40 planos — 15/11/2026

- **[GitHub Actions 43751714168](https://github.com/HelioConde/VideoForge-IA/actions/runs/43751714168): SUCCESS.** 45 testes do roteiro, direção, autonomia, identidade e execução segura passaram. A fila regenerada confirmou **40 tomadas, 39 visuais, 4.890 frames** e registrou `REMAKE_QUEUE_CREATED shots 40 visual 39 blocker provider_cost_permission_required images 0 video False`. O checkpointer não encontrou mudanças adicionais (`CHECKPOINT_ALREADY_CURRENT`). [Fila gerada no artifact](https://github.com/HelioConde/VideoForge-IA/actions/runs/43751714168/artifacts/14176058160).
- **[GitHub Actions 43751714070](https://github.com/HelioConde/VideoForge-IA/actions/runs/43751714070): SUCCESS.** 14 testes do empacotador/Three.js e QA de PNGs temporários passaram, sem chamadas pagas; scanner de fonte real teve sucesso ao identificar que a âncora V2 ainda falta e **pulou corretamente o pacote de imagens reais**.
- **Comportamento garantido:** C01-P02 continua com 90 frames de espada do carrasco; novos inserts de C01/C08/C12 não usam imagens falsas nem referências não aprovadas. **Nenhum novo MP4 ou PNG foi produzido nesta alteração editorial.**

**Pedido do usuário:** manter as **14 cenas narrativas**, mas adotar **40 tomadas cinematográficas**, no lugar das 37 anteriores. A versão ativa continua `remake-v2-20261115`, com 163 segundos, 4.890 frames, 30fps e 1080×1920. São **39 tomadas com imagem-mãe própria + 1 abertura preta com SFX original**. A contagem de imagens não é teto de criação de camadas: cada rig usa quantos recortes originais realmente precisar.

Três novos cortes sem acrescentar tempo: **C01-P05, 310–359** (mãos dos guardas e lanças cruzadas); **C08-P04, 2880–2939** (roda do carrinho e Elara fugindo); **C12-P04, 4290–4349** (flor prateada e gesto de Elara). As tomadas C01-P04/C08-P03/C12-P03 foram apenas encurtadas no fim para acomodar essas inserções; as outras 34 tomadas mantêm seus frames. **C01-P02 continua em 60–149, com quatro componentes reais previstos**. Elara permanece excluída da corte em C01/C02; sua identidade de princesa só aparece em C12; a espada continua pertencendo ao carrasco.

**Fonte obrigatória para os agentes:** `roteiro.json` e `remake-ep01-planos.json` já atualizados para 40/39; testes de roteiro, identidade, continuidade e fila devem acompanhar. Nenhuma arte das três novas tomadas existe nem foi aprovada; política de custos do provedor continua bloqueada e YouTube não foi publicado. Histórico de 37 planos é uma versão editorial **anterior**, não a ordem de produção ativa.

## C01-P02 — código de geração do fundo oculto e três RGBA (15/11/2026)

### Resultado comprovado do produtor e bloqueio de gastos — 15/11/2026

- **[Run 43749686509](https://github.com/HelioConde/VideoForge-IA/actions/runs/43749686509): SUCCESS.** Primeiro push com o novo `remake_sword_source.py` e `remake-sword-component.yml`. Testes gratuitos e mockados validaram bloqueio de custo, origem da mãe, uma edição por run, RGB opaco/RGBA verdadeiro e arquivamento com SHA; o job real de produção paga ficou **skipped**.
- **[Run 43749824057](https://github.com/HelioConde/VideoForge-IA/actions/runs/43749824057): SUCCESS.** Isolados os testes específicos do produtor das fixtures do empacotador. **8 testes passaram, 0 ignorados**, em 2,945s; confirmação de `REMAKE_C01_P02_SOURCE_CODE_QA_NO_PAID_INFERENCE`. Job pago novamente **skipped**.
- **Código aplicado:** `12f238a6ae2663489fe9b6b38edd19f44ee6dbb5`, com refinamento de testes `efad5702d74224a8eb88793b753be1ba5ceb30f1`.
- **Estado real permanece:** política de custo `paid_provider_calls_approved=false`, `max_chargeable_calls_per_run=0`, âncora V2 não aprovada. Portanto **0 chamadas pagas, 0 PNGs da tomada C01-P02, 0 MP4 real da C01-P02 e 0 upload YouTube**.
- **Pipeline pronto em código:** âncora V2 e imagem-mãe original → uma candidata por run manual protegido → arquivo permanente de PNG/QA por canal/produtor → empacotamento SHA/recomposição → ThreeCanvas e MP4 técnico → checkpoint. Até que as fontes existam, os jobs de arte e render param corretamente.

`videoforge/remake_sword_source.py` e `.github/workflows/remake-sword-component.yml` usam o proxy já instalado, uma edição por run manual, origem `cena-01-c01-p02.png` da mesma mãe SHA arquivada e prompts separados por peça. Criam candidatos `underlay` (RGB 1024×1536) e `sheath/blade/hand` (RGBA alpha), com QA, SHA e arquivamento imutável mesmo quando houver reprovação técnica. Testes gratuitos de política de custo, origem e proxy mockado estão no `tests/test_remake_sword_source.py`; CI pendente de verificação neste registro.

**Regra de custo ativa:** `paid_provider_calls_approved=false`; `max_chargeable_calls_per_run=0`. A nova geração não foi disparada. Não há PNG V2/underlay/espada reais nem MP4 de 3s. É proibido concluir a tomada a partir de imagens de teste. A execução de fontes só poderá ocorrer após aprovação de gasto e da referência canônica V2. A composição/empacotamento sem custo permanece pronta.

## C01-P02 — empacotamento automático de arte real (15/11/2026)

### Verificação GitHub concluída: scanner, empacotamento sintético, gatilho e bloqueio (15/11/2026)

### Regressão após tornar o teste compatível com aprovação futura — 15/11/2026

O [run 43745676658](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745676658) terminou em **SUCCESS**, validando preflight e render de frames sintéticos ThreeCanvas após ajuste do teste que supunha ausência eterna da âncora V2. O teste permanece rigoroso quanto a pacotes inexistentes, mas não impedirá o programa de progredir quando uma âncora verdadeira for aprovada. **Nenhuma arte real ou MP4 C01-P02 foi criado.**

- **[Run 43745321463](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745321463) — SUCCESS.** O scanner gratuito detectou que **não há âncora V2 aprovada nem camadas reais** e pulou corretamente o job de montagem; o teste completo no runner GHCR executou **14 testes aprovados em 36,416s** com fixtures temporárias de PNGs, inclusive pacote válido, mães incompatíveis, SHAs adulterados e anti-repetição. Não gerou nenhuma imagem do usuário.
- **[Run 43745321451](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745321451) — SUCCESS.** Regressão do movimento ThreeCanvas + regra do preflight validada; nenhum vídeo com arte real foi renderizado.
- **[Run 43745436851](https://github.com/HelioConde/VideoForge-IA/actions/runs/43745436851) — SUCCESS.** O evento automático **workflow_run** disparou de verdade depois do empacotador. O job de verificação registrou `REMAKE_SWORD_REAL_SOURCE_NOT_READY_NO_RENDER` e pulou o renderer porque **não existia artifact de arte real**; preservou o bloqueio correto.
- **Correção preventiva adicional:** o teste `tests/test_remake_sword_preview.py` não presume mais que `character-bible` ficará faltando para sempre. Uma âncora futura aprovada não poderá derrubar o CI apenas porque a referência passou a existir.

**Status de produção:** 0 PNGs C01-P02 criados nesta etapa, 0 artifacts reais da espada, 0 MP4 C01-P02 e nenhum gasto de provedor. O MP4 C01-P01 de 2 segundos continua validado, sem publicação. O packer está integrado e testado; restam principalmente: referência canônica V2, produção do underlay e partes RGBA por tomada.

`videoforge/remake_sword_pack.py` e `.github/workflows/remake-sword-pack.yml` escaneiam **apenas** originais SHA-validos arquivados em `assets/geracoes/` por canal/produtor/run. São obrigatórias uma mãe genuína `cena-01-c01-p02.png` (metadata `scene=c01`, `shot_id=C01-P02`, âncora V2 aprovada), `underlay` opaco e `sheath/blade/hand` RGBA com QA apontando ao mesmo SHA. O `workflow_run` do `remake-sword-preview.yml` verifica o artifact antes de iniciar um render; sem imagens, faz somente relatório de bloqueio. O algoritmo de pivô é **rascunho baseado em máscara**, sujeito à revisão de arte e contato. O script impede render duplicado da mesma mãe se já houver QA final técnico.

**Ainda pendente:** aprovação/arquivo `character-bible` V2, gerador de underlay específico, adaptação do gerador de sprites para tomada C01-P02, MP4 real de 3s. Nenhum gasto de API, aprovação humana ou upload YouTube liberado. Testes de pacote/CI devem ser registrados após executar de verdade.

<!-- REMAKE-C01-P01-START -->
### C01-P01 — abertura preta com SFX original (QA técnico)
- **MP4 técnico real:** artifact \`vf-remake-c01-p01-opening-43709191586\` do GitHub run \`43709191586\`; SHA256 \`75b8be46c7e609a1c9ff8afad0935bcbf8c6faa2126ba3c74cad3af540f3c44e\`; 2 s, 60 quadros pretos 1080×1920/30fps H264/AAC por Remotion.
- **Áudio original:** \`sword-original.wav\`, SHA256 \`22879c38726c284f484c1f57c325fc053e0ba8591565e24eba92d4e9c827fb1d\`; efeito procedural inédito, QA de áudio e preto passou.
- **Armazenamento:** MP4/WAV no artifact de GitHub Actions por 90 dias; o repositório ignora *.mp4, *.wav e assets/ para evitar mídia versionada. QA e hashes persistidos em \`QA-C01-P01-REMAKE-V2.json\`.
- **Limites:** não é o episódio completo, não há rig de personagem, imagem nova, aprovação humana, gasto de API ou YouTube. Próxima tomada: C01-P02 depende da âncora V2 aprovada.
<!-- REMAKE-C01-P01-END -->


<!-- REMAKE-AUTOPILOT-START -->
### Diagnóstico autônomo mais recente
- Etapa: review_identity_reference
- Alvo: character-bible
- Bloqueio: wardrobe_identity_rejected_reference_missing
- Despacho de geração permitido: False
- Sem novas imagens, vídeo ou aprovação humana neste diagnóstico.
<!-- REMAKE-AUTOPILOT-END -->


## REGRAS ATIVAS DO REMAKE — LEITURA OBRIGATÓRIA PARA AGENTES

## C01-P02 — integração do rig da espada à produção Real Remotion/Three (15/11/2026)

## C01-P02 — validação de integração ThreeCanvas/QA concluída (15/11/2026)

**Resultado confirmado na branch `main`:**

- [Run 43710782778](https://github.com/HelioConde/VideoForge-IA/actions/runs/43710782778): preflight sem imagens reais/sem proxy, PASS.
- [Run 43710782832](https://github.com/HelioConde/VideoForge-IA/actions/runs/43710782832): TypeScript/contratos Remotion e componente C01-P02, PASS.
- [Run 43710782768](https://github.com/HelioConde/VideoForge-IA/actions/runs/43710782768): regressão do player legado, PASS.
- [Run 43711300246](https://github.com/HelioConde/VideoForge-IA/actions/runs/43711300246): QA de cinco testes com PNGs/alpha reais **sintetizados APENAS para teste**; sem Pillow/novas bibliotecas, PASS.
- [Run 43711476006](https://github.com/HelioConde/VideoForge-IA/actions/runs/43711476006): **primeiro smoke de execução ThreeCanvas da espada**, criou PNG técnico para frames locais **7 e 71** em runner GHCR/Remotion via `swangle` e comprovou hashes/bytes diferentes; PASS. Isso confirma que há movimento independente de sprite, não apenas código compilável.

**Regressão resolvida:** o smoke intermediário [43710965103](https://github.com/HelioConde/VideoForge-IA/actions/runs/43710965103) detectou Pillow ausente. Corrigido sem instalar pacote: FFmpeg existente só decodifica PNG para QA e Python stdlib faz recomposição; ver commits `94cf7c58b90b1865971900ac877526f3c2604f41` e `de60b273ec57c2c1c6ffc01d622dac80b907dfae`.

**Estado honesto:** existe render real de **2s da C01-P01** em [artifact 14159517637](https://github.com/HelioConde/VideoForge-IA/actions/runs/43709191586/artifacts/14159517637), aprovado tecnicamente. Na C01-P02 existe **somente render de frames sintéticos para validar o motor**: 0 imagens finais, 0 MP4 real da tomada, 0 autorização humana de arte, 0 publicação YouTube. O workflow `remake-sword-preview.yml` está pronto para consumir `vf-remake-c01-p02-sword-source-<run_id>` quando o programa reunir uma imagem-mãe V2 e `underlay/sheath/blade/hand` da mesma tomada, com proveniência e QA.

**Próxima ação técnica prioritária para agentes:** obter e arquivar **âncora V2 visual aprovada** mediante provedor/orçamento permitido; gerar imagem-mãe C01-P02 e quatro PNGs independentes (sem repetir fontes V1); implementar empacotamento automático dos artifacts de geração; executar `remake-sword-preview.yml` com a fonte real; revisar alfas, underlay e movimento; só depois ampliar para C01-P03. Não simular etapa pronta.

### Ajuste de QA da C01-P02 após teste do runner — 15/11/2026

A execução de smoke [43710965103](https://github.com/HelioConde/VideoForge-IA/actions/runs/43710965103) identificou **biblioteca Pillow ausente** no contêiner GHCR, apesar de a validação Python de bloqueio ter passado. **Correção:** `videoforge/remake_sword_preview.py` agora usa o FFmpeg já presente APENAS para decodificação de PNG RGBA, e faz o alpha-compositing e diferença RGB pixel a pixel com **biblioteca padrão Python**. Fixtures de regressão agora também geram PNGs em memória via `struct` e `zlib`, sem Pillow, numpy nem downloads de pacotes. A engine de animação segue exclusivamente Three.js + Remotion. O smoke é **sintético e não cria arte de produção**, nem vídeo C01-P02. Teste da revisão corrigida será verificado em CI.

**Código implementado e aguardando verificação do CI:** o movimento prévio `remake-sword-motion.ts` e os sprites do `remake-sword-rig.tsx` agora possuem uma composição isolada `motion-remotion/src/remake-sword-preview-index.ts` com ThreeCanvas, 90 frames, sobreposição fixa **PRÉVIA TÉCNICA • ARTE NÃO APROVADA**. Não movimenta o PNG inteiro, não troca o vídeo oficial e não publica no YouTube.

**Entrada real obrigatória:** pacote com imagem-mãe da **própria C01-P02**, relatório de origem `production-scene/v1`, quatro PNGs de camadas da mesma tela (`underlay`, `sheath`, `blade`, `hand`) e `sword-bundle.json` contendo hashes, run e parâmetros medidos. `videoforge/remake_sword_preview.py` verifica: referência canônica V2 real/aprovada, SHA de cada arquivo, contexto do canal/cena, alfa verdadeira, canvases iguais, decomposição/recomposição com FFmpeg (decodificação de PNG para QA) e Python stdlib (composição de pixels) (MAE ≤ 0,5 RGB), pulso na geometria da mão e deslocamento de lâmina dentro do quadro. Rejeita qualquer pacote inválido, **sem chamadas ao provedor de imagens**.

**GitHub Actions:** `.github/workflows/remake-sword-preview.yml` executa preflight e testes após push, sem gerar arte. Com artifact de fonte `vf-remake-c01-p02-sword-source-<run_id>`, o despacho manual fica disponível para renderizar 3s de movimentação pelo Remotion/ThreeCanvas e validar MP4/movimento com FFmpeg/FFprobe. O job separado do host persiste QA/SHA/ID de run no `QA-C01-P02-REMAKE-V2.json`, `estado-atual.json`, histórico e checkpoint, preservando `.gitignore`. Fonte: [contrato e fluxo](../../../../docs/C01-P02-PACOTE-ARTE-E-RIG.md).

**Status real nesta etapa:** C01-P01 **possui MP4 real** em artifact `vf-remake-c01-p01-opening-43709191586` ([run concluído](https://github.com/HelioConde/VideoForge-IA/actions/runs/43709191586)) e QA em `QA-C01-P01-REMAKE-V2.json`; a C01-P02 **ainda não tem PNGs reais nem MP4**, e o remake 163 s não existe. A âncora V2 `character-bible` está sem arte aprovada, com bloqueio `provider_cost_permission_required`. Não mascarar ausência de referência, gastos ou aprovação. **Próximo passo:** disponibilizar âncora V2 real via provedor autorizado, criar imagem-mãe por plano e os quatro PNGs originais da C01-P02; então o pipeline de prévia pode renderizar sem modificações manuais.

## C01-P01 — primeira cena produzível sem arte (15/11/2026)

### Correção de CI após o primeiro render real — 15/11/2026

- **Prova material:** GitHub Actions [run 43708620559](https://github.com/HelioConde/VideoForge-IA/actions/runs/43708620559) renderizou de verdade 60 frames pretos H264/AAC por Remotion; FFprobe e FFmpeg conferiram todos os pixels pretos, áudio original audível e duração **2,005 s**. WAV SHA `22879c38726c284f484c1f57c325fc053e0ba8591565e24eba92d4e9c827fb1d`, MP4 SHA `75b8be46c7e609a1c9ff8afad0935bcbf8c6faa2126ba3c74cad3af540f3c44e`.
- **Artifact reproduzível:** `vf-remake-c01-p01-opening-43708620559`, ID `14159253575`, contém WAV, MP4, QA inicial e props, por 90 dias. Essa prévia é **técnica, não o episódio completo** e não houve publicação.
- **Falha pontual após QA:** o último passo do workflow tentou `git add` dentro da imagem GHCR de Remotion e falhou porque **git não existe nesse contêiner** (`git: command not found`, exit 127). O áudio e vídeo foram preservados; o checkpoint não foi versionado nessa execução.
- **Correção implementada:** separar os jobs. O contêiner gera e audita mídia; um segundo job no host `ubuntu-24.04` baixa o artifact, verifica os bytes novamente, persiste SHA, QA e checkpoint na branch `main`, sem instalar git na imagem, sem versionar binários e sem chamar IA. Teste preventivo `tests/test_remake_opening_workflow.py`.
- **Pendente:** confirmar execução do workflow corrigido e registro do novo artifact no checkpoint. Não alterar aprovação humana ou render oficial.

**Implementação nova em teste:** `videoforge/remake_opening.py` sintetiza um SFX original de metal/bainha em WAV mono 48 kHz, sem amostras comerciais, internet ou IA. O novo entrypoint `motion-remotion/src/remake-opening-index.ts` renderiza **somente a abertura de 60 frames pretos**, 1080×1920/30fps, com WAV em `<Audio>`. Workflow `.github/workflows/remake-opening-preview.yml` reutiliza o runner Remotion GHCR pré-instalado, executa testes, renderiza MP4 via Remotion, confere com FFmpeg/FFprobe apenas QA (frames inteiramente pretos, AAC audível, 60 frames, H264, SHA), guarda o MP4 e WAV por 90 dias em artifact e versiona **somente** o relatório/hashes e checkpoint, conforme `.gitignore` que proíbe mídia binária no canal. **Não** publica no YouTube.

**Até a execução do workflow, isso é código, não MP4 confirmado.** O comando `python -m videoforge.remake_opening verify --output-dir ...` só declara sucesso com arquivos reais. Após sucesso atualiza automaticamente este checkpoint, histórico, estado JSON e o plano de C01-P01; o relatório `QA-C01-P01-REMAKE-V2.json` apontará run/artifact e SHA. A arte canônica, C01-P02 e os demais rigs continuam pendentes de PNG real, revisão e custo permitido.

## Programacao acelerada por skills e bibliotecas — CI validado em GitHub (15/11/2026)

**Commit inicial:** `4c797d525966ac0db208ce51bb0679614b995792`. **Ajuste do pacote da espada:** `da01ba30f026f985ce8427e5f29704339fb906ac` (C01-P02 exige `underlay`, `sheath`, `blade`, `hand` e o perfil `sword-draw-three`; inserts genericos nao herdam uma espada). Essas sao mudancas de **codigo/producao**, nao arte aprovada.

**Evidencias GitHub Actions (SUCESSO):**
- [Run 43706445755](https://github.com/HelioConde/VideoForge-IA/actions/runs/43706445755): testes Python + exportacao de `output/remake-shot-queue.json` com 37 planos/36 visuais, formatos e bloqueios reais; relatorio no artifact do workflow.
- [Run 43706445766](https://github.com/HelioConde/VideoForge-IA/actions/runs/43706445766): Remotion TS `typecheck`, contrato cinematografico, teste de movimento C01-P02, malha verdadeira e rig C12 existentes.
- [Run 43706445758](https://github.com/HelioConde/VideoForge-IA/actions/runs/43706445758): regressao do legado Remotion, incluindo tipagem, malhas e preview tecnicos sintéticos de teste.
- [Run 43706561709](https://github.com/HelioConde/VideoForge-IA/actions/runs/43706561709): reteste da fila corrigida de C01-P02: sucesso.

**Skills disponiveis:** `.agents/skills/videoforge-dorama-remake/SKILL.md`, `.agents/skills/videoforge-rig-2d-three/SKILL.md`, `.agents/skills/videoforge-qa-and-checkpoint/SKILL.md`. O upstream `remotion-dev/skills` foi **consultado como referencia com commit fixo**, nao instalado como dependencia ativa. `docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md` orienta reutilizacao e impedimento de reimplementacao da engine.

**Proximo passo:** produzir/arquivar ancora canônica V2 aprovada (imagem PNG real e SHA) com provedor/custo permitido e revisao humana; entao produzir a imagem-mae C01-P02, separar `underlay/sheath/blade/hand`, medir `wristPivot`, `axisDeg` e `travelPx` na arte, aplicar `RemakeSwordRig`, executar recomposicao e QA, produzir preview MP4 tecnico pelo Remotion. **Mídia real do remake ainda nao existe**: 0 PNG, 0 rigs novos aprovados, 0 MP4s oficiais, 0 uploads, sem autorizacao automática de gastos.

## Comeco da programacao com bibliotecas e skills prontas (15/11/2026)

**Iniciado o codigo de producao do remake, sem descartar historico tecnico.** A base usa **bibliotecas ja instaladas** (Remotion 4, Three.js, React Three Fiber e `@remotion/three`) e instrucoes originais locais em `.agents/skills/`, com referencia oficial aos [Remotion Agent Skills](https://github.com/remotion-dev/skills/tree/7e541aa4d7361dfaca0780a565a47307eb7bdfbb). Nao instalados novos motores ou pacotes pagos.

**Entregas de software:** `videoforge/remake_starter.py` gera fila GitHub dos **37 planos** e 36 tomadas visuais, calculando `task_fingerprint`, camera, elenco, perfil de rig, camadas a separar e proximo workflow candidato (nao despacha pagamento). `.github/workflows/remake-autonomy.yml` executa teste e exporta `output/remake-shot-queue.json` como artifact. Para a **C01-P02 espada**, componentes novos `motion-remotion/src/remake-sword-motion.ts` + `remake-sword-rig.tsx` reutilizam `RigidSprite` do rig Three.js existente, movimentam lamina e mao separadamente, deixam a bainha fixa, e giram a mao pelo pulso. Tudo deterministicamente por `useCurrentFrame()` e parametros que deverao ser medidos na futura arte. Testes JS/Python e workflow de QA adicionados.

**Estado real:** codigo e skills adicionados; **0 novas imagens**, **0 novos MP4s**, **0 renders oficiais** e **0 uploads** neste trabalho. A C01-P01 continua definida com 60 frames pretos, aguardando SFX original/licenciado; C01-P02 aguarda PNGs separados (blade/sheath/hand/underlay) **da mesma imagem-mae** e SHA+QA. A imagem-ancora `character-bible` ainda nao existe aprovada no repo; `autonomy-policy.json` nao autoriza custo de provedores externos. O programa pode planejar sem chamar a IA paga e sem enganar que o video esta pronto.

**Teste CI:** a nova fila e a matemática da espada estao incluidas nos workflows de autonomia e QA do compositor. **Proximo passo:** confirmar execucoes de CI; preparar referencia canonica e aprovacoes necessarias; depois produzir cada arte por perspectiva, extrair partes, QA neutro, rig verdadeiro, previews e edicao final. Os IDs dos runs precisam ser preenchidos somente quando a execucao for real.

## Integração real do gerador cinematográfico ao remake V2 (15/11/2026)

## Integração do workflow de geração à âncora V2 verificada (15/11/2026)

## Validação final da correção — GitHub Actions (15/11/2026)

**A alteração solicitada foi integrada e testada na `main`.** Implementação V2 em `videoforge/cinematic_direction.py` + `production_scenes.py` validada por [run 43702500080](https://github.com/HelioConde/VideoForge-IA/actions/runs/43702500080) **SUCCESS** (commit `f372e8c01f1da1974e13346b01e9cfa3e0027039`). Referência da cena migrada do artifact V1 para a **âncora V2 aprovada arquivada no GitHub por SHA e proveniência** via `videoforge/remake_reference.py`; [run 43702919849](https://github.com/HelioConde/VideoForge-IA/actions/runs/43702919849) **SUCCESS** (commit `510931dd1c13174fdea62c3506ed22b1bf98a28c`).

O QA de arquivamento [run 43702917744](https://github.com/HelioConde/VideoForge-IA/actions/runs/43702917744) **FAILURE** revelou a exigência obsoleta do lock V1. A correção está no commit `981362486d73f07bc6701b47297d63095fa7ef38` e foi confirmada por [run 43703372917](https://github.com/HelioConde/VideoForge-IA/actions/runs/43703372917) **SUCCESS** (QA de PNGs persistentes) e [run 43703372899](https://github.com/HelioConde/VideoForge-IA/actions/runs/43703372899) **SUCCESS** (autonomia + testes de compatibilidade). **Não é necessário repetir esses testes para diagnosticar a mesma inconsistência.**

**Escopo comprovado:** seleção do manifesto V2, 37 planos/4890 frames, prompts com estilo oficial, referência por SHA e manifesto, salvaguardas contra custos/publicação e compatibilidade com workflows V1 de somente QA. **Ainda não realizado:** geração da nova âncora `character-bible`, qualquer PNG/rig/MP4 oficial do remake, despacho automático integral dos workflows e revisão visual da nova arte. O coordenador atual indica `generate_character_bible` com `provider_cost_permission_required` e `dispatch_allowed=false`.

**Próxima etapa objetiva:** obter referência canônica do remake aprovada e comprovada no GitHub, e confirmar como o provedor autorizado poderá produzir imagem sem despesa adicional não consentida; somente então iniciar `C01-P02` no workflow existente, registrar os arquivos/SHA, produzir camadas RGBA, rig mesh e QA antes de render. Não publicar no YouTube.

## Correção de regressões nos workflows antigos (15/11/2026)

**Falha real encontrada e corrigida:** o [QA do arquivamento](https://github.com/HelioConde/VideoForge-IA/actions/runs/43702917744) falhou porque exigia a presença do arquivo de bloqueio de novas imagens eliminado pelo remake V2. O teste permanece **sem gerar imagens**, mas passa a conferir o registro histórico do bloqueio, `estado-atual.json` e `autonomy-policy.json` para garantir que não existe autorização automática de custo ou YouTube.

**Varredura:** workflows legados de QA, máscaras, rig V5, reconciliação e importação da C12 não devem depender do lock V1 como condição de execução. Atualizados 20 workflows de leitura/técnica para reconhecer `REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md` como histórico e continuar sem gerar nada. Os workflows de geração ainda respeitam a existência de um lock novo se recolocado, além do bloqueio Python separado para custo real.

**Proteção de manifesto:** o QA da timeline cinematográfica V1 mantém os campos `legacy_scope` e `active_remake_manifest` quando reexecutado, sem confundir `noImageGenerationLock=true` histórico com estado ativo do remake; o QA de planos indica quando os prompts vieram do manifesto V2. Testes `tests/test_remake_workflow_compatibility.py` impedem regressão.

**Status:** correções de código e workflow, sem novas imagens, MP4 ou publicação. CI desta atualização ainda precisa ser confirmado. **Próxima ação:** validar workflows corrigidos e preparar produção C01-P02 somente após âncora e autorização de custo.

**Problema corrigido:** `production-scene-by-request.yml` antes utilizava obrigatoriamente um artifact da prancha V1 (run histórico 43590930215). A direção nova podia montar prompts V2, mas o download ainda puxaria o personagem antigo ou ficaria indisponível. **O workflow agora diferencia V2 de projetos legados:** para o EP01 V2, exige `shot_id` específico e extrai a âncora canônica **aprovada** dos arquivos PNG persistidos em `assets/geracoes/production-art-request/<run-id>/` usando `videoforge/remake_reference.py`. Valida SHA da imagem, manifesto de arquivamento, arquivo de produção, dimensões, canal, vídeo e run antes de passar bytes ao proxy. Outros canais continuam no caminho antigo, sem regressão. C01-P01 continua sem imagem.

**Segurança:** a geração por IA permanece bloqueada enquanto `autonomy-policy.json` não autorizar efetivamente o custo da chamada e enquanto a âncora não estiver aprovada. Não há download de PNG legado V1 para o remake, nem autoaprovação artística ou YouTube. `tests/test_remake_reference.py` inclui referência RGB/PNG sintética somente em teste de memória/temporário, nunca salva como arte de produção.

**Status deste avanço:** integração de código, workflow e testes; aguardando CI desta revisão. **0 imagens, 0 rigs e 0 MP4 gerados**. Próximo passo técnico: validar no GitHub Actions; depois seguir para a preparação e geração de arte canônica do remake com custo devidamente autorizado, e implementar encadeamento autônomo das camadas e malhas.

**Mudança de código:** `videoforge/cinematic_direction.py` agora consulta `estado-atual.json` para detectar `remake-v2-20261115`, valida `remake-ep01-planos.json` (37 planos, 4890 frames, cena/cast, duração, foco, princesa ausente de C01/C02, autorização editorial) e converte cada tomada para o formato usado por `production_scenes.py`. O prompt tem o **estilo Cinematic Semi-Realistic Fantasy Anime** e a direção dramática/ângulo específica do manifesto **ativo**. `load_plan()` continua lendo a V1 como legado somente para QA histórico; não voltar à V1 para criar imagens do remake.

**Integridade da arte:** `assert_shot_generation_ready()` exige PNG de âncora V2 realmente presente e SHA validado, dimensões certas e aprovação humana documentada. Antes do proxy, `production_scenes.generate_scene()` também compara o SHA da referência baixada com o SHA da âncora canônica aprovada. A política `image_generation_policy.py` continua impedindo consumo de provedor sem aprovação explícita de custo. Zero chamadas pagas nesta mudança.

**Status desta integração:** código + testes de regressão preparados; aguardando confirmação do CI neste commit. **Não é** animação completa, aprovação artística, geração de PNG/rig/MP4 ou publicação. **Próximo passo:** testar em Actions; depois, quando a âncora e o custo estiverem autorizados e verificados, iniciar C01-P02 com os workflows existentes e persistir SHA; implementar encadeamento do rig por tomada.

**Ordem vigente (15/11/2026):** remake integral do EP01 autorizado editorialmente; sem limite editorial numérico de imagens; estilo cinematográfico anime semirrealista com identidade constante; rig 2D verdadeiro em ThreeCanvas/Remotion (não pan/zoom de PNG); produção por workflows GitHub, orientação humana focada nas decisões artísticas; qualquer avanço entra neste arquivo mestre e no JSON/histórico, com SHA, run e próximo passo. Preservar materiais e QA legados, sem relançar trabalhos concluídos.

**Distinção obrigatória:** o lock de 14/11 **não está mais ativo**; foi arquivado em `REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md`. Mas **imagem autorizada editorialmente não equivale a chamada paga autorizada**, nem a identidade artística aprovada, nem a vídeo publicável. O coordenador autônomo está operacional para diagnóstico e retomada; **o gerador antigo ainda precisa conectar a referência canônica e o novo manifesto V2** antes de conseguir produzir o remake. Não alterar flags de QA para contornar essas pendências.

**Fontes vigentes:** `AGENTS.md` → `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md` → `REMAKE-EP01-PLANO-OFICIAL.md` → `remake-ep01-planos.json` → `autonomy-policy.json` → este checkpoint. O histórico e o antigo plano de arte são arquivos de evidências, não políticas novas.

## REMAKE EP01 V2 — DIREÇÃO ATUAL E AUTONOMIA DO PROGRAMA (15/11/2026)

**ORDEM RECENTE:** refazer EP01 do drama pelas regras de qualidade, sem teto editorial de imagens, e continuar. **O lock antigo de 14/11 foi arquivado em `REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md`, não está mais ativo**. O remake pode gerar novas imagens **editorialmente**; **custos adicionais e publicação ainda não autorizados**.

**Objetivo de autonomia reforçado pelo usuário:** é o **programa GitHub**, não o assistente manual, que deve aprender o ciclo `arte → camadas → rig/malha → render Remotion → QA → reparo seguro → checkpoint → próxima tomada`. Os agentes devem orientar/validar a produção; falhas corrigíveis devem ser diagnosticadas e retomadas automaticamente por workflows quando os requisitos técnicos estiverem implementados. Criado plano oficial [REMAKE-EP01-PLANO-OFICIAL.md](REMAKE-EP01-PLANO-OFICIAL.md) e manifesto [remake-ep01-planos.json](remake-ep01-planos.json). Não afirmar que a automação completa existe: o coordenador atual inicialmente executa preflight/seleção da próxima etapa, bloqueando pagamentos não aprovados e decisões de aprovação artística.

**Escopo:** 14 cenas, 37 planos iniciais, 163 segundos; C01-P01 não pede imagem; espada em P02 é do carrasco; Elara só revelada na C12; manter C01 V5 e C12 como **legado histórico** sem apagar assets/QA. **Estado novo real:** 0 novos PNGs, 0 rigs, 0 MP4s; nada publicado. **Próxima ação exata:** executar preflight/autopilot GitHub e preparar âncora character-bible após confirmar o provedor e permissão de custo, persistir SHA e retomar primeiro plano visual C01-P02.

**ARQUIVO MESTRE OBRIGATÓRIO:** este `ESTADO-ATUAL.md`. Após cada avanço, erro ou bloqueio, registrar resultado, SHA e próximo passo; sincronizar histórico e JSON. Não voltar à V5 nem reexecutar etapas antigas por perda de contexto.

---
> **PONTO ÚNICO DE RETOMADA DO EPISÓDIO.** Branch de referência: `main`. Atualizado em 15/11/2026 (horário de Brasília, UTC-3). Antes de alterar qualquer coisa, ler `AGENTS.md`, `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`, este documento e `HISTORICO-DESENVOLVIMENTO.md`. **Não começar do zero.**

## DIRETRIZ MAIS RECENTE — QUANTIDADE LIVRE, QUALIDADE ALTA E REGISTRO OBRIGATÓRIO (15/11/2026)

**Regra de produção do responsável:** não estabelecer **nenhum máximo editorial de imagens**. Quando a geração de imagens estiver autorizada, criar e refinar tantas imagens-mãe, vistas de câmera verdadeiramente distintas, cenários, recortes, camadas e expressões quanto o roteiro e o QA pedirem. O único objetivo é dorama **visualmente bonito, detalhado, coerente e animado por ossos/malhas reais**; não simplificar apenas para ficar dentro de cota artificial, nem criar duplicações inúteis. Respeitar custos/limites reais de ferramenta e permissões.

**Este é o arquivo principal e obrigatório do EP01.** Antes de qualquer tarefa, ler o checkpoint atual e confirmar o que há na `main`. Ao terminar qualquer avanço material, incluir neste arquivo: data, cena/plano, trabalho realizado, status, arquivos e SHA, branch/commit, workflows/runs, MP4/artifact se comprovados, QA, erro/bloqueio e **a próxima etapa concreta**. Na mesma integração atualizar `estado-atual.json` e adicionar ao `HISTORICO-DESENVOLVIMENTO.md`; não perder o trabalho nem refazer imagens, cenas, rigs ou renders já existentes. Relatar se ficar em PR/branch e não na main.

**Registro histórico anterior ao remake:** na atualização anterior o lock seguia ativo; a autorização posterior de refação revogou o bloqueio editorial para o remake V2. Esta integração é documental, sem imagens ou renders novos. **Estado técnico não mudou:** C01-P03 V5 integrada, QA técnico passou mas falta aprovação visual; C12 depende dos originais ZIP/PNG. **Próxima ação:** verificar visualmente V5 e recuperar os arquivos C12 existentes, antes de executar trabalho adicional.

## Objetivo e limites

Concluir o dorama MMORPG no VideoForge-IA com animação 2D genuína: imagem-mãe → fundo sem personagens → partes originais PNG RGBA → reconstrução de oclusões → pivôs/malhas Three.js → Remotion/ThreeCanvas/SWANGLE → vídeo MP4 → QA visual e audiovisual. Canal: `alchemy-lab`. Vídeo: `mmorpg-conquiste-a-princesa-ep01`.

- Roteiro / direção: 14 cenas de origem, **37 planos cinematográficos**, **106 trilhas de direção atuais após V4 (107 no planejamento original; V3 teve 113)** e duração planejada **163 s / 4890 frames em 30 fps**.
- **REMAKE V2 ATUAL:** novas imagens editorialmente autorizadas. Bloqueio de 14/11 arquivado; custo pago extra e upload YouTube não autorizados.
- `video_oficial_do_programa=false`, `human_visual_approved=false` e `youtube_uploaded=false`. Teste técnico de MP4 **não** significa aprovação de personagem, rig ou episódio.
- Manter arquivos de cada vídeo em `canal/<id>/videos/<video-id>/`. O código de componentes reaproveitáveis pode estar em `videoforge/`, `motion-remotion/`, `tests/` e `.github/workflows/`.

## C01 — animação realmente renderizada, rig integrado à main

**Último marco confirmado:** o motor de direção por keyframes, hierarquia de pivôs e malhas foi integrado à `main` no **PR #51**, commit `693212eeb32ede9c0dc8f1c6de94a92638b0dc60`.

- [GitHub Actions run 43660106313](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106313): **success**, render da prévia técnica **C01-P03** no fluxo já integrado à main. MP4 H.264, **3 s / 90 frames, 1080×1920, 30 fps**, sem áudio, com marca de rascunho.
- Artifact: `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43660106313`, ID `14139373365`; arquivo temporário de Actions (retém por 14 dias), não mídia arquivada permanentemente no repositório.
- [Run 43660106308](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106308): **success** no typecheck/regressões.
- Arquivos integrados: `direcao-bindings-c01-draft.json`, `direcao-rig-remotion.json`, `videoforge/directed_rig.py`, `videoforge/directed_rig_qa.py`, `motion-remotion/src/directed-rig-*.tsx` e `.github/workflows/directed-rig-preview.yml`.
- A versão anterior com **costura da cintura de Kael corrigida** foi registrada na [execução 43633018544](https://github.com/HelioConde/VideoForge-IA/actions/runs/43633018544). Reutilizar correções existentes, não reescrever o rig do zero.

**Ainda pendente em C01:** contaminação/cortes nas lanças e nas bordas; underlays/anatomia escondida incompletos; revisão das máscaras de Aldric e dos guardas; prova de recomposição neutra e aprovação humana. Lança já cruzada no quadro de origem não pode ser animada como se estivesse inicialmente aberta. O relatório de C01 indica recomposição provisória com diferença RGB média `11,16/255`; não confundir prova de movimento com prova de qualidade artística.

## C12 — malhas existentes, integração pronta, arquivos originais ainda ausentes

**Não perder o progresso da C12:**

- [Run 43653702785](https://github.com/HelioConde/VideoForge-IA/actions/runs/43653702785): **success** em auditoria de timeline e testes Python; **não renderizou o MP4**.
- [Run 43654314863](https://github.com/HelioConde/VideoForge-IA/actions/runs/43654314863): **success** em contratos/typecheck de Remotion e malha de **5 sprites / 512 triângulos**; **não renderizou o MP4**.
- `qa-c12-rig-malha-v2.json`: registra prova anterior de malha e **MP4 local de 12 s / 360 frames**, `alchemy_c12_mesh_rig_v2_aprovacao.mp4` com SHA `e08f79924e6f09bab195e54d49c32b588c2438d28faf2e1db12d626bba018016`. **Esse MP4 existiu como arquivo local de chat, mas seus bytes não foram arquivados no GitHub; o SHA em JSON não é um download.**
- C12-P01: movimento independente dos olhos de Kael, ainda sem camadas RGBA/underlays de olhos verificadas e prontas no GitHub.
- C12-P02: malha da capa de Kael com **96 triângulos**.
- C12-P03: mecha frontal **100**, cabelo traseiro **144**, brinco **72** e manga **100** triângulos (total **512**).
- O compositor técnico de **8 segundos** `render-alchemy-c12-three-mesh-technical.yml` usa P02+P03; **não substitui** P01 nem a prévia local anterior de 12 segundos.
- [Run 43658221156](https://github.com/HelioConde/VideoForge-IA/actions/runs/43658221156): tentativa de render da C12 na main **bloqueada por ASSETS_PENDING (0/9 originais encontrados)**. [Relatório de bloqueio](qa-c12-render-bloqueio-2026-11-14.json).
- O [PR #50](https://github.com/HelioConde/VideoForge-IA/pull/50) é **outra proposta, ainda aberta**, de importação por hashes/MP4 C12. Analisar e reconciliar com o fluxo já integrado, sem criar duplicidade de renderizadores ou afirmar merge.

**Faltam no GitHub:** duas imagens-mãe RGB dos planos P02/P03, dois backgrounds técnicos e cinco PNGs RGBA isolados (nove arquivos com SHA conhecido). O plano original inclui um terceiro RGB de Kael para P01. Consultar `RENDER-C12-TECNICO.md`, `qa-c12-rig-malha-v2.json` e `IMPORTAR-TRES-REFERENCIAS-ORIGINAIS.md`.

Pacotes **anteriormente produzidos fora do GitHub** e ainda pendentes de importação: `alchemy-ep01-cinema-3-originais.zip` e `alchemy_c12_rig_camadas_tecnicas_v2.zip` (o fluxo de importação da main usa o nome `uploads/alchemy-c12-rig-camadas-tecnicas-v2.zip`). Confirmar bytes reais e SHA antes de marcar importado, jamais regenerar substitutos. Corrigir as máscaras do brinco e da mecha frontal que ainda contêm pele/fundo; verificar underlays e silhuetas.

## 14/11/2026 — avanço registrado: QA do C12, sem alterar a arte

**Novo marco na `main`:** [PR #52](https://github.com/HelioConde/VideoForge-IA/pull/52) integrado no commit `a69287356a87c3bbd2f67bf987ce1a0f0ae73f5c`. [Run de testes 43661690928](https://github.com/HelioConde/VideoForge-IA/actions/runs/43661690928) **SUCCESS** para o contrato; render foi `skipped` no PR. Novos módulos `videoforge/c12_render_qa.py` e `tests/test_alchemy_c12_render_qa.py`:

- Compara **pose neutra** por recomposição de fundo + sprites RGBA com a imagem-mãe 941×1672, usando originais SHA antes de testar movimento. Os limites automáticos não significam aprovação humana.
- Decodifica o **H.264 real** para medir movimento localizado da capa em C12-P02 e de cabelo/brinco/manga em C12-P03, rejeitando MP4 parado ou deslocamento de toda a imagem. Reproduz e compara hashes de dois quadros para testar determinismo; valida 240 frames/30fps.
- [Run de produção técnica 43661756457](https://github.com/HelioConde/VideoForge-IA/actions/runs/43661756457) **FAIL esperado por `ASSETS_PENDING`**, na etapa de preflight dos PNGs. Artifact `vf-alchemy-c12-threecanvas-draft-43661756457` (ID `14140665963`) contém **somente o relatório de pendência, nenhum MP4**. A nova análise neutral/movimento ainda **não foi executada com os originais reais**, e não deve ser declarada aprovada.

**Localização descoberta:** a biblioteca pessoal deste projeto tem metadados dos arquivos **pré-existentes** (não arquivos novos):

- `/youtube/alchemy_c12_rig_camadas_tecnicas_v2.zip` — **6.186.154 bytes**, contém sete PNGs técnicos segundo manifesto anterior;
- `/youtube/alchemy-ep01-cinema-3-originais.zip` — **7.390.768 bytes**, três PNGs RGB de referência;
- `/youtube/alchemy_c12_mesh_rig_v2_aprovacao.mp4` — **999.889 bytes**, prévia local histórica de 12 segundos.

A tentativa de ler/copiar os bytes por integração de arquivos **falhou com `This Project file does not have an authorized raw-byte materialization path`**. **Metadados de Library não provam recuperação dos ZIPs.** Por isso os nove PNGs seguem não arquivados no GitHub. Não copiar conteúdos por aproximação ou gerar artes substitutas.

**Desbloqueio exato:** anexar os **dois ZIPs originais** à conversa como arquivos reais, ou colocá-los diretamente na **raiz** `uploads/` do repositório com os nomes indicados em [RENDER-C12-TECNICO.md](RENDER-C12-TECNICO.md). Depois conferir SHA, importação para `assets/` do episódio, preflight, recomposição neutra, MP4 de 8s, movimentos locais e QA visual (mecha e brinco ainda precisam correção). C12-P01/olhos e episódio completo continuam pendentes.

## 14/11/2026 — importação dos ZIPs agora reativa o MP4 técnico automaticamente

**Implementado na `main`:** [PR #53](https://github.com/HelioConde/VideoForge-IA/pull/53), commit `24c49509b53339a45a413c581435dd817d2028db`. Os workflows de importação dos **três RGB** e **sete PNGs técnicos** já existiam, mas os commits deles feitos com `GITHUB_TOKEN` não disparam outros workflows por `push`. O novo coordenador [`c12-after-import.yml`](../../../../.github/workflows/c12-after-import.yml) escuta a conclusão de **ambos** os importadores (`workflow_run`), consulta a `main` e somente com **nove fontes SHA-256 verificadas** dispara explicitamente `render-alchemy-c12-three-mesh-technical.yml` via `workflow_dispatch` e token Actions autorizado. Origem ausente = **aguardar sem gerar MP4**; origem adulterada/máscara inválida = **erro**.

- [Testes PR run 43662265188](https://github.com/HelioConde/VideoForge-IA/actions/runs/43662265188) **SUCCESS** para o classificador `videoforge/c12_dispatch_gate.py`.
- [Run na main 43662307131](https://github.com/HelioConde/VideoForge-IA/actions/runs/43662307131) **SUCCESS**: confirmou `WAIT_FOR_EXISTING_SOURCE_BYTES` e **não despachou** o render enquanto faltam os PNGs; artifact temporário `c12-after-import-preflight-43662307131` ID `14140133496` só contém relatório.
- Criada a pasta visível [`uploads/README.md`](../../../../uploads/README.md). Enviar pelo GitHub, preservando os PNGs internos, exatamente `uploads/alchemy-ep01-cinema-3-originais.zip` e `uploads/alchemy-c12-rig-camadas-tecnicas-v2.zip`. Os dois ZIPs foram encontrados em metadados da Library, mas **não foi possível acessar seus bytes por esta integração**.
- A prévia C12 de 8 segundos ainda **não existe como novo MP4 de GitHub Actions**; o rig C01 de três segundos permanece disponível na [run 43660106313](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106313). Nenhuma imagem foi gerada, nenhum vídeo publicado.

## 14/11/2026 — dois ZIPs originais: validação e envio direto para a main

**Nova melhoria integrada:** [PR #54](https://github.com/HelioConde/VideoForge-IA/pull/54), commit `346a3a80c74a96f39390aa12896916bfd2e9a994`. [Workflow de testes 43665498760](https://github.com/HelioConde/VideoForge-IA/actions/runs/43665498760): **SUCCESS** nos testes de contrato, enquanto render da PR permaneceu `skipped`.

- `videoforge/c12_upload_existing_zips.py` valida **10 PNGs existentes** nos dois arquivos ZIP (3 RGB originais e 7 técnicos = 2 fundos + 5 sprites RGBA), exige os SHA e tamanhos nativos cadastrados e recusa arquivos adulterados, descompactação insegura e sobrescritas.
- `scripts/enviar-zips-c12.ps1` oferece um único comando no Windows para fazer clone temporário da `main`, validar ambos os ZIPs, preservar seus bytes e enviar o commit; instruções em [`uploads/README.md`](../../../../uploads/README.md). Não edita arte, não gera imagens e não publica vídeo.
- **Situação real:** pasta `uploads/` da `main` permanece somente com `README.md`. Os ZIPs estão listados na Library, mas a API não liberou acesso aos seus bytes. **Nenhum arquivo RGB/RGBA C12 foi importado e nenhum MP4 novo C12 foi gerado nesta etapa.**
- **Próxima ação exata:** baixar os dois ZIPs antigos da Library para `Downloads` e executar `./scripts/enviar-zips-c12.ps1` em PowerShell dentro do clone do VideoForge-IA; alternativa: anexar os ZIPs à conversa ou enviá-los na pasta `uploads/` do GitHub. Os workflows de importação/coordenação fazem o resto e só renderizam após hashes verificados.

## 14/11/2026 — C01-P03: atuação articulada perceptível V2, ainda não aprovada visualmente

**Feedback do usuário:** a primeira prévia MP4 C01 de 3 s não transmitia movimento. Análise dos keyframes antigos na `main`: cabeça `-0.6°`, ombros `-2 px`, punho `+2°`. Diferença visível insuficiente no plano aberto.

**Correção integrada:** [PR #55](https://github.com/HelioConde/VideoForge-IA/pull/55), commit `c3a4c6bcee3c2cbe5d180bcf1a5355f625a3398a`. Em `C01-P03`, a câmera permanece **travada**, e Kael ganha **seis trilhas de atuação com pivôs independentes**: `kael.punhos/rotationZ`, `kael.ombros/translateY`, `kael.cabeca/rotationZ`, `kael.cabeca/translateY`, `kael.braco-direito/rotationZ`, `kael.antebraco/rotationZ`. Cabelo e jaqueta mantêm suas malhas RGBA existentes, agora com amplitudes 4,2 e 2,8 px. O episódio passou de **107 para 110 trilhas** após adicionar as três ausentes. Coreografia por quadros registrada em [`atuacao-c01-p03-v2.json`](atuacao-c01-p03-v2.json), pedido de render em `pedido-render-c01-direcao.json` revisão 2.

- [PR run 43667345840](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667345840) **SUCCESS** em TypeScript e testes. [PR run 43667345857](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667345857) **SUCCESS** na renderização real de MP4 V2, artifact técnico ID `14143046357` nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43667345857` (retido por prazo limitado).
- MP4 de aprovação técnica V2 (gerado em PR): **3 segundos, 90 frames, 1080×1920, 30fps, H.264, vídeo sem áudio**, SHA256 `1667c60c61b7e10a5e3d5353599631678709e91b456072069ec3e39a1c48094d`.
- QA real decodificado, câmera estática, área de Kael e sem textos: **20.974 pixels** com mudança RGB ≥24 entre frames 0 e 75, contra **11.756** na prévia antiga medida com o mesmo critério/corte (~78% mais); teste mínimo 16.000 passou. Não confundir a métrica com atuação convincente/aprovação artística.
- Após primeira renderização da revisão, foi observada a **faixa cor-de-vinho do cenário exposta na junção da gola**, devido à translação vertical de cabeça sem underlay. Foi reduzida de `-7 px` para `-1,25 px`, mantendo a rotação até `-8,5°`; a faixa **ainda aparece parcialmente** com a rotação. **REVISÃO HUMANA NÃO APROVADA.**
- Permanecem pendentes em C01: reconstrução/overlap da **gola e nuca com pixels originais**, bordas/costuras de mão e ombro, mascaramento do rei/guardas/lanças, QA de recomposição neutra, e movimento convincente para o roteiro completo. Não alegar fechamento de dedos: a mão é um sprite articulado no pulso, sem dedos isolados.
- [Run da main 43667678291](https://github.com/HelioConde/VideoForge-IA/actions/runs/43667678291) **SUCCESS** (teste e render oficial do workflow técnico, NÃO vídeo oficial do programa); artifact ID `14142756569`, nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43667678291`. MP4 da main teve SHA256 `1667c60c61b7e10a5e3d5353599631678709e91b456072069ec3e39a1c48094d`, idêntico byte a byte à prévia do PR; QA decodificado 20.974 pixels; sem nova geração de imagens e sem upload para YouTube. **Visual não aprovado por abertura na gola**.

**Atenção ao manual global:** `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md` define, para aprovação de rigs, rotação de cabeça absoluta de até 2°. A V2 testa até 8,5° **somente como rascunho técnico experimental não publicável** para avaliar a legibilidade; a exceção não está aprovada e de fato revelou falha de underlay na gola. A animação não pode ser oficializada até cumprir a regra existente, ou até haver revisão fundamentada do rig e das fontes com aprovação expressa do projeto. Não ocultar a divergência nem substituir avaliação visual por contagem de pixels.

**Próxima ação C01:** melhorar a região **nuca/gola** usando apenas as fontes anteriores e QA dos recortes, sem inventar preenchimento/anatomia. Regerar o MP4 da `main`, inspecionar o movimento em close de QA e só então avançar os planos de guarda e rei. Este trabalho não substitui a pendência dos originais de C12.

## 15/11/2026 — C01-P03 V3 integrada e renderizada na `main` (QA técnico passou)

**Situação: `FEITO` no código e no MP4 técnico; `PENDENTE` na aprovação visual.** O [PR #56](https://github.com/HelioConde/VideoForge-IA/pull/56) foi **MERGED** com commit `69e22458703c7c716f05e205987471ce3595b1c5`. É a continuação do rig já existente, sem recomeçar e **sem gerar imagens novas**. O relatório integral de correções, tentativas que falharam e amostras está em [**QA-C01-P03-V3-2026-11-15.md**](QA-C01-P03-V3-2026-11-15.md); roteiro por parte/quadro em [`atuacao-c01-p03-v3.json`](atuacao-c01-p03-v3.json).

- **Sucesso comprovado no PR:** [run de render/QA 43671982404](https://github.com/HelioConde/VideoForge-IA/actions/runs/43671982404) e [run TypeScript/testes 43671982444](https://github.com/HelioConde/VideoForge-IA/actions/runs/43671982444) — ambas `success`.
- **Sucesso reproduzido na main:** [run de render/QA 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507), **SUCCESS**, e [run de TypeScript/testes 43673610480](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610480), **SUCCESS**. Artifact técnico da main ID `14145228520`, nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43673610507` (temporário, não arquivo MP4 permanente no GitHub).
- **MP4 real verificado (mesmo SHA entre PR e main):** `directed-rig-preview.mp4`, 3 s, **90 quadros**, **1080×1920**, 30 fps, H.264 `yuv420p`, **sem áudio**, 693.447 bytes. SHA-256 `73993ab7b1f93aead42d1860d16c3db965adcbd3e6bdf2794eb631a9d704100c`.
- **Atuação independente:** `c01-gates-qa.json` confirma **18.923 pixels em movimento** apenas na região de Kael, entre quadros 0 e 75, delta RGB ≥24; gate mínimo 16.000 **PASSOU**. A câmera permanece fixa; a imagem inteira não é deslocada para simular atuação.
- **Junção gola/manga:** no verdadeiro background original verificado por SHA, foram identificados **67, 66 e 73 pixels recém-expostos** nos quadros 55, 75 e 89, dentro da ROI nativa `[495,855,83,28]`. Limite 75, pior = **73**, **PASSOU o gate técnico por margem estreita de 2 pixels**. Não significa que a gola esteja perfeita em inspeção visual.
- **Rig seguro conforme manual:** cabeça no máximo **1,82°** (limite 2°), sem translação Y da cabeça. Nove trilhas neste plano, **113 trilhas de direção no episódio**: cabeça, ombros, braço superior direito, antebraço, pulso, braço esquerdo e flexão independente da **bota direita**; movimentos secundários de cabelo e jaqueta. `kael.costura-gola-pixel-original` é um holdout feito **somente com pixels reais da imagem-mãe** previamente cobertos pela manga e jaqueta, com o mesmo osso `kael.ombros`, atrás das peças. Pixels novos inventados = **0**.
- **QA neutro NÃO aprovado:** `neutral-qa.json` registra `pixelExactRecomposition=false`, média de erro RGB **11,159474** e 1.075.513 pixels diferentes de 1.572.864. Também faltam inspeção visual de recortes na mão, braço, bota/joelho, gola, guardas, lanças e máscara de Aldric/trono. **`humanVisualReview=false`, `publishable=false`, `officialVideoApproved=false`, `youtubeUploaded=false`.**

**Próxima ação C01 (sem refazer o que passou):** revisar visualmente o MP4 V3 no enquadramento final e ampliado, consertar apenas máscaras/underlays existentes sem inventar pixels, melhorar fidelidade neutra à imagem-mãe e separar corretamente rei/guardas/lanças. C01 é **só 3 segundos** dos 163 segundos planejados. Em paralelo, C12 segue `ASSETS_PENDING` (dois ZIPs antigos não importados / nove PNGs originais ausentes). Não retomar o roteiro nem a criação do motor.

## 15/11/2026 — pesquisa GitHub armazenada + direção C01 V4 definida pelo usuário (AINDA NÃO IMPLEMENTADA)

**Estado:** `PESQUISA_ARQUIVADA`, `REGRAS_VISUAIS_C01_ATUALIZADAS`, `V3_REVISADA_PELO_USUARIO_COM_ERROS`, `V4_AINDA_NAO_RENDERIZADA`. A V3 da [run 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507) permanece **tecnicamente validada** e armazenada como referência, mas **NÃO está aprovada visualmente**. Usuário assistiu e relatou movimentos antinaturais e recortes defeituosos; o sucesso dos dois testes numéricos não revoga esse feedback.

**Documentos permanentes adicionados à `main`:**

- [Pesquisa aprofundada de bibliotecas/skills para rigging 2D](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md) — comparação de *spine-animation-ai*, *claude-animated-shorts*, Rev2D, Rigby2D, Three.js, OpenCV, scikit-image, IKPy, SAM, PixiJS, Rive, DragonBones, MediaPipe e FFmpeg; casos de uso, licenças a validar, 3 caminhos técnicos, C01/C12, QA e links. Fonte: relatório anexado `Texto colado(1).txt`, SHA-256 `950b66530b071e84e75b82ba5357c31629b8473ae908fc8ec5b1eb49a9256e84`. **Bibliotecas e skills pesquisadas, NÃO instaladas nem integradas.**
- [Regras C01-P03 de respiração sutil e correção de recortes](REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md) — ordem e critérios de aceitação para a **V4**, sem alterar a V3.
- Recomendação técnica: **manter Remotion + Three.js já implantados**, aproveitar métodos de alinhamento OpenCV/segmentação e QA, usar `SKILL.md` como referência organizacional; não trocar de motor nem importar código de licenciamento não comercial sem validação.

**Correções obrigatórias para C01-P03 V4 após feedback visual real:**

1. **Somente Kael respirando**: micro movimento de tórax/ombros (`~±1–2 px` da arte nativa como ponto de partida), cabeça até `~0,5°`, tecido e cabelo com malha minimamente responsiva. Câmera imóvel. Não aumentar o gesto artificialmente para satisfazer `16.000 pixels` de movimento.
2. **Braço/antebraço/punho direitos travados e encostados na perna**; não animar o gesto de punho da V3. Restringir o contato no espaço global, porque apenas travar keyframes locais não impede que ombros móveis arrastem a mão.
3. **Pé e bota direitos inteiramente imóveis**: a track da bota V3 produziu corte/silhueta ruim. Não usar movimento do pé para somar pixels no gate de animação.
4. **Lanças e guardas estáticos, lanças rígidas**; corrigir recortes duplicados e contaminação da máscara.
5. **Rei Aldric com cabeça inteira** na composição neutra original; corrigir máscara/corte antes de aprovar qualquer MP4.
6. **QA apropriado à cena**: comparar frame 0 com arte-mãe, estabilidade dos elementos fixos, mão na perna sem desencaixe, pé sem corte, rei com cabeça íntegra; medir respiração localizada e suavidade, em vez de exigir globalmente a contagem de pixels alta da V3. Tudo sem novas imagens, sem publicação no YouTube.

**Próxima ação C01 exata:** criar uma branch V4 a partir da `main` e **aplicar as regras acima ao rig atual**, executar testes de composição/contatos/máscaras, gerar MP4 de 3 s para revisão humana. **Não executar trabalho de animação por causa do simples arquivamento desta pesquisa.** C12 mantém pendência independente dos ZIPs e PNGs originais.

## 15/11/2026 — C01-P03 V4 integrada, respiração suave e rei/lanças recuperados da mãe

**FEITO no código e no MP4 técnico da `main`. PENDENTE de aprovação visual humana.** [PR #57](https://github.com/HelioConde/VideoForge-IA/pull/57) integrado por squash commit `4d010a92212ce77e9c7fbcf762537ecf0e732be2`. [Relatório completo de implementação, falhas, testes e QA V4](QA-C01-P03-V4-2026-11-15.md); [regras do usuário](REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md); [pesquisa GitHub de skills/bibliotecas](../../../../docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md); [JSON da atuação V4](atuacao-c01-p03-v4-respiracao.json).

- **Status verificado:** [PR render 43676494078](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676494078) **SUCCESS**, [PR TS/tests 43676494086](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676494086) **SUCCESS**; [main render 43676630976](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630976) **SUCCESS**, [main TS/tests 43676630957](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630957) **SUCCESS**. Artifact técnico da main `14145684036`, nome `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43676630976`. O binário **só está em artifact temporário do Actions**, não em pasta persistente do GitHub.
- **MP4 real validado:** `directed-rig-preview.mp4`, **3s, 90 quadros, 1080×1920, 30fps, H.264, 599.144 bytes** e **SHA-256 `90baea03b4e2b551a21d341c263853a2e9b9d4d5647314fff46a39bf79fbbff7`**. Verificado **idêntico byte a byte** entre PR e `main`; sem áudio e sem publicação.
- **A animação da C01-P03 é agora apenas respiração:** 2 keyframe tracks (`kael.ombros/translateY` até **-1,25px**, `kael.cabeca/rotationZ` até **-0,32°**). Malha secundária cabelo **0,45px** e jaqueta **0,55px**; câmera parada; episódio passou de **113 para 106 trilhas** de direção, sem alterar os outros 36 planos.
- **Mão/antebraço direito apoiados na perna** e **pé/bota direitos fixos**: a cadeia direita é independente do osso móvel dos ombros, e nenhum keyframe move essas peças; braço esquerdo também não faz gesto. Testes verificam pontos no **espaço global** ao longo dos quadros.
- **Aldric, guardas e lanças recuperados da imagem-mãe original:** a composição utiliza a mãe RGB SHA `544548f0ac5f9e4686e2cf0d1477470f77e2fd7f15678d82799609b678fd6ebf` e copia fundo reconstruído previamente existente apenas sob máscara dos sprites originais do Kael +3px. Recortes estáticos provisórios (`aldric`, guardas e lanças) não são sobrepostos; eles permanecem arquivados para possível trabalho futuro. No frame 0 o **rei com coroa inteira** e as **duas lanças cruzadas originais** foram inspecionados. Não se gerou imagem nova.
- **QA real da `main`:** `c01-gates-qa.json technical_qa_passed=true`. Respiração detectada em **11.115 pixels** da região de Kael (RGB delta≥8, limite V4 25–20.000; regida adicionalmente por pivôs máximos e contatos físicos); rei/coroa, lanças superiores e bota **0 alterações detectadas** entre frames medidos no limiar RGB≥24; gola com **24 pixels** do fundo expostos, abaixo do limite 75. **Não é aprovação visual.**
- **Recomposição muito melhor, mas ainda não exata:** `neutral-qa.json meanAbsoluteRgbError=0,216449949476454`, **13.015 pixels diferentes** em 1.572.864; na V3 eram erro ~11,159474 e 1.075.513 pixels diferentes. `pixelExactRecomposition=false` exige inspeção de contornos Kael, manga, bota/solo, cabelo/gola e máscara alfa. Mantém **`humanVisualReview=false`, `publishable=false`, `officialVideoApproved=false`, `youtubeUploaded=false`.**
- **Histórico de falhas (não apagado):** [run 43676126787](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676126787) falhou devido à proteção da gola tentando seguir braço fixo (referência corrigida). [run 43676244073](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676244073) gerou MP4 mas reprovou um limite de movimento numérico errado para a cena suave; recalibrado sem aumentar amplitudes dos ossos. O relatório V4 detalha essa causa e os resultados verificados.
- **Skills e bibliotecas:** pesquisa de GitHub arquivada e suas práticas de rigging/QA adaptadas ao **Three.js/Remotion existente**; **nenhum código externo não-comercial copiado** e nenhum editor alternativo/IA instalados.

**Próximo passo C01:** assistir ao MP4 V4 em celular e em aproximação para confirmar que a respiração está natural, a mão permanece apoiada, bota sem corte, lanças rígidas e rei inteiro; corrigir qualquer artefato nos poucos pixels de máscara divergentes usando exclusivamente fontes originais. Apenas depois expandir os planos. **C12 continua ASSETS_PENDING**, aguardando ZIPs/PNGs originais; **episódio final de 163s não foi produzido**.

## 15/11/2026 — V5 integrada: costas respiram por malha real, cabeça continua suave

**Estado confirmado no código da `main`:** [PR #58](https://github.com/HelioConde/VideoForge-IA/pull/58) **MERGED**, commit `ae7ca09c3f75ed04498704459a2ac547de810d06`. [Relatório técnico completo V5](QA-C01-P03-V5-2026-11-15.md) com métricas reais, [manifesto do movimento das costas](atuacao-c01-p03-v5-respiracao-costas.json), [manual de rig](../../../../docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). A V4 permanece como base histórica bem-sucedida.

**Pedido visual:** o usuário gostou do leve movimento de cabeça na V4, mas quer **também as costas se movendo um pouco na respiração**. Portanto, a V5 **mantém** as 2 trilhas `kael.ombros/translateY` até `-1,25px` e `kael.cabeca/rotationZ` até `-0,32°`, **sem gesto extra no braço direito apoiado, bota, guardas, lanças ou rei**. Acrescenta apenas `kael.jaqueta.mesh.backBreath`: deformação independente de vértices do tecido RGB/RGBA já existente na imagem original, com **expansão de até 1,05 px** e **elevação até 0,6 px**, zona Y nativa `857–947` (pico 898); laterais, gola e cintura (sourcePin desde 950) imóveis. A câmera permanece fixa. **A cena continua com 2 tracks e o episódio com 106.**

**Testes e prévia na branch PR:** [render/QA 43680505866](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680505866) **SUCCESS**, [Remotion/TS testes 43680505879](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680505879) **SUCCESS**, após falha inicial [43680421318](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680421318) por tipagem TypeScript TS2345 corrigida. MP4 de 3s/90 quadros/1080×1920 H.264, tamanho **598.863 bytes**, SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`, artifact PR `14147369278`, temporário. Amostragem real do ROI das costas `[405,870,85,65]` detecta **957/514/8/191 pixels** alterados nos frames 30/55/75/89 (limiar 8), o suficiente para confirmar deformação visível no MP4 técnico. Ator **11.698 pixels** de alteração em ROI ampla; rei/lanças/bota sem mudanças detectadas no limiar 24; gola **24 de 75 pixels** permitidos, QA PASS. Recomposição neutra igual à V4: MAE **0,21645**, 13.015 pixels diferentes em 1.572.864, portanto `pixelExactRecomposition=false`.

**Main após merge confirmada:** [render/QA 43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142) **SUCCESS** e [TS/testes 43680784182](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784182) **SUCCESS**. Artifact da main `14147374656` (temporário), MP4 H.264 de **3 s / 90 quadros / 1080×1920 / 30 FPS / 598.863 bytes**, SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`; **bytes idênticos ao MP4 de PR #58**. QA das costas, regiões imóveis e gola passou também na main; ver [relatório definitivo V5](QA-C01-P03-V5-2026-11-15.md). Próxima etapa é **revisão humana da V5 no celular**, especialmente a suavidade das costas e a integridade de cabeça, gola, jaqueta, mão apoiada, bota, rei e lanças. Nenhuma imagem nova; sem YouTube, sem áudio, sem vídeo oficial de 163 segundos. C12 continua esperando os PNG/ZIPs originais. **Não voltar à V4 por falta de memória da conversa; V5 agora é a versão com código mais recente na main, mas não tem aprovação artística.**

## 15/11/2026 — Padrão visual oficial do dorama arquivado (somente editorial)

**Pedido do responsável:** usar o estilo da imagem enviada como amostra para o dorama e fazer com que **quase toda cena tenha clima dramático e ângulo de câmera diferente**, sem perder consistência de Kael, princesa, rei, guardas ou cenários. Nome aprovado neste registro: **Cinematic Semi-Realistic Fantasy Anime** (estilo da ilustração); **Cinematic 2D Mesh Animation** continua o método de animação. A regra é **apenas para o dorama**, não para os outros canais.

- **Bíblia oficial e prompt mestre:** [`PROMPT-OFICIAL-ESTILO-DORAMA.md`](PROMPT-OFICIAL-ESTILO-DORAMA.md). Inclui prompt em inglês parametrizado por plano, negative prompt, 10 tipos de ângulo, tabela de continuidade e checklist de arte.
- **Registro histórico original (supersedido pelo remake):** o manifesto de estilo inicialmente marcava autorização **false** para novas imagens. Após o pedido de refazer o EP01, o estado vigente passou a permitir imagens editorialmente, mas mantém aprovação de custos e revisões técnicas independentes; ver `autonomy-policy.json`.
- **Amostra arquivada no repositório:** [miniatura autêntica da imagem do usuário, 96×171](REFERENCIA-VISUAL-DORAMA-PREVIEW-96.jpg), sem regeneração por IA, SHA-256 `58f22420d123561623944e369c08c7d6a1808df29dc2e3f5d795129c5d2192b4`. A imagem original enviada tem dimensão **864×1536**, bytes JPEG apesar da extensão `.png`, SHA-256 `2bab99670444001fbccf8a6c861276e93dfb56f04a33ba5f542698ad3419b2e1`; **original em resolução plena NÃO foi versionado no GitHub**. Esta miniatura **não serve para recorte ou rig**.
- **Entrada fixa no canal:** [`canal/alchemy-lab/dorama/README.md`](../../dorama/README.md), [README do canal](../../README.md), [estratégia editorial](../../ESTRATEGIA.md), README e AGENTS globais. Todo agente de imagens **futuras e autorizadas** deverá consultar esse padrão antes de propor novos quadros.
- **Nenhuma alteração de sprites, imagens-mãe, direção do rig V5, assets do C12, workflow, render ou YouTube foi feita** por este registro editorial.
- **Histórico da regra de 14/11 — não vigente no remake:** o arquivo `SEM-GERACAO-NOVAS-IMAGENS.lock` impedia imagens novas quando o padrão visual foi registrado. A ordem posterior de refazer o EP01 em 15/11 substituiu essa restrição e o lock foi arquivado em [`REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md`](REMAKE-EP01-HISTORICO-BLOQUEIO-2026-11-14.md). A V5 permanece prévia técnica e C12 legado com originais pendentes.

**Próxima ação editorial vigente no remake:** usar o manifesto V2 para preparar referência canônica, planos individuais e rigs conforme forem autorizados e verificados os recursos reais; o bloqueio editorial antigo não é mais uma restrição, mas os custos adicionais, a aprovação artística, a integração do gerador e o upload continuam pendentes.

## Próxima ação concreta, em ordem

1. **Prioridade:** recuperar os **bytes reais dos dois ZIPs já localizados na Library, porém inacessíveis para cópia**, ou enviá-los à raiz `uploads/`; importar os arquivos *já existentes* da C12; verificar exatamente SHA, RGBA, bbox, 941×1672 e presença real no GitHub. Antes de repetir o render, verificar se os ZIPs já apareceram no repositório. Se faltarem, informar `assets_pendentes` e manter o relatório.
2. Quando estiverem arquivados, **o coordenador aciona automaticamente** o workflow técnico C12 na **main**; verificar MP4, repetibilidade de frames, recomposição, bordas, costuras e oclusões. Não inferir aprovação humana do sucesso do workflow.
3. **C01 V5 já integrada à main e MP4 técnico da main confirmado:** [consultar QA V5](QA-C01-P03-V5-2026-11-15.md), verificar render [da main 43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142), assistir MP4 da V5 no celular, conferir costas respirando suavemente com cabeça ainda leve, mão apoiada, bota sem cortes, rei/coroa e lanças originais. **Não restaurar tracks V3 de braço/pé nem recrear fundos**, preservar V5 com fonte aprovada.
4. Depois ampliar para os demais 36 planos visuais com imagem-mãe própria e rig por cena, narração, legendas e QA; **episódio oficial de 163 s permanece pendente** enquanto não houver assets e aprovação.

## Regra permanente para o próximo agente / próxima conversa

Ao terminar **qualquer avanço no dorama**, atualizar **este arquivo na `main`** com estado e **o próximo passo exato**, e acrescentar um evento em `HISTORICO-DESENVOLVIMENTO.md` com commit, workflow/run, artifact, SHA, QA e pendências. Links de artifact expiram; não tratá-los como arquivamento permanente. Marcar claramente `feito`, `teste_tecnico`, `pendente`, `bloqueado`. Não repetir tarefas concluídas, não mover progresso apenas para branches ou chat, nem sobrescrever histórico anterior. Para regras globais, obedecer `AGENTS.md` e `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md`.

## 2026-11-16T01:03:42Z — retomada apos OAuth validado no runner

- Reserva unica de recuperacao persistida ANTES de redisparar o workflow de arte. Nenhuma imagem, cobranca confirmada, aprovacao humana ou upload ao criar reserva.
- Proxy health autenticado e elegibilidade foram exigidos pelo workflow. Sem resultado de arte ainda; proximo passo: geracao e QA por SHA.
