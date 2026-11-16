# AGENTS.md — VideoForge IA (reconstrução)

**CHECKPOINT 16/11/2026 — CONTINUIDADE DE FIGURINO ATUALIZADA:** considerar APENAS o plano oficial de 40 tomadas `remake-ep01-planos.json` e o derivado [CONTINUIDADE-FIGURINOS-V2-40-TOMADAS.json](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CONTINUIDADE-FIGURINOS-V2-40-TOMADAS.json). O arquivo `continuidade-figurinos-37-planos.json` é histórico e não pode guiar novas cenas. Ver [QA de detalhes do traje de Aldric e do painel roxo de Elara](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-DETALHES-FIGURINOS-V2.md). Pranchas JPEG são imagens derivadas SEM IA, mostram full-frame e recorte central que NÃO localiza automaticamente o torso. Todos os figurinos completos seguem 0/2 aprovados e R2 está bloqueada; nunca assumir identidade aprovada pela imagem bonita, SHA ou zoom. O objetivo é impedir mudança de roupas e continuidade nas 40 tomadas, não bloquear a preparação técnica independente da abertura.

**PRÓXIMA ETAPA EP01 V2 — REFERÊNCIAS DE FIGURINO:** ver a [galeria com 6 fontes reais](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-OPCOES-FIGURINO-V2.md) e seu [inventário SHA](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-INVENTARIO-FIGURINOS-V2.json). Três opções de Elara e três de Aldric, mas são candidatas (várias V1) ainda NÃO aprovadas; jamais passar seus hashes ao modelo como fontes canônicas sem revisão. O pedido antigo foi encerrado/reprovado; o workflow produtor verifica `videoforge.art_request_gate` antes do proxy, pulando R2 sem traje completo de ambos, para evitar gasto duplicado. Ver estado atual e revisão do usuário. R2 não gerada, vídeo não publicado.

**REGRA PRIORITÁRIA 16/11/2026 — FIGURINOS REPROVADOS:** owner REPROVOU `character-bible-grounded` (SHA `6ed16d498df46b59c38e9c34ab25127b5b032159ab3289c073ac0058fcda6fc3`) por roupa diferente do rei Aldric e parte roxa do peitoral da Elara ausente/inconsistente. Ler `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAO-FIGURINO-V2.json` e `CONTRATO-FIGURINO-V2.json` antes de qualquer arte. SHA técnico NÃO aprova figurino. Não promover/prender rigs a esta imagem, nem gerar R2 sem imagens de roupa completas aprovadas por SHA da princesa e do rei. R2 planejada, não gerada. Preservar arquivos e histórico.

**EP01 V2 — NOVA CANDIDATA DE IDENTIDADE (16/11/2026):** O run 43868021687 gerou `character-bible-grounded.png` com dois originais SHA realmente enviados ao `images/edits`. O SHA da nova arte é `6ed16d498df46b59c38e9c34ab25127b5b032159ab3289c073ac0058fcda6fc3`. O run 43868899761 gerou `QA-KAEL-TRIPLO-V2.jpg` e `QA-ELARA-TRIPLO-V2.jpg`, com relatório `QA-IDENTIDADE-GROUNDED-V2.json`; aprovação ainda pendente, imagem anterior preservada, tamanho real 1199×1312. Antes de tentar cena-mãe C01-P02 ou autorizar as 40 tomadas, revisar a nova prancha e identidade de Aldric. O coordenador `remake_autopilot` deve detectar essa nova candidata mas nunca promovê-la sozinho ao status approved, nem repetir a imagem paga, nem enviar YouTube.

**GERACAO DE IDENTIDADE ANCORADA NOS PNGs REAIS:** Para `alchemy-lab/mmorpg-conquiste-a-princesa-ep01`, o asset `character-bible-grounded` deve usar `videoforge.grounded_identity.edit_payload` e anexar por `/v1/images/edits` os exatos PNGs de Kael (edb751c...) e Elara (bf199f3...) por SHA. Não usar texto dizendo "imagem anexada" sem incluir bytes. Nunca sobrescrever a primeira `character-bible` gerada só por texto, nem aprovar nova identidade sem revisão visual. Aldric segue sem original individual. Uma chamada por run, sem retry cego; registrar tudo no episódio e não publicar YouTube.

**CHECKPOINT EP01 V2 — 16/11/2026:** três arquivos cinematográficos originais de Kael, Elara e C12-P02 foram importados por SHA exato. `reference_sources_current` sinaliza 2/2 closes e câmera C12 true. A `character-bible` V2 ainda é candidata (não aprovada, gerada por texto sem imagens de referência anexadas). Para revisão, abrir `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-IDENTIDADE-EP01-V2.md` e as duas prévias JPEG derivadas, com SHA no relatório `QA-COMPARACAO-IDENTIDADE-V2.json`. Os originais não foram modificados, nenhum provedor foi chamado para as prévias e nenhuma aprovação é inferida pelo SHA. Proibido despachar novas cenas/MP4 oficial/YouTube sem identidade humana aprovada; C01-P02 precisa de 4 camadas verdadeiras vindas de sua mãe específica. Registro factual consolidado em `estado-atual.json` e `ESTADO-ATUAL.md`.

**CHECKPOINT 16/11/2026 — ORIGINAIS E C12:** importador SHA sem lock V1: run 43823567116 SUCCESS, 0/3 fontes originais disponíveis. Coordenador V2 run 43823850136 SUCCESS (95 testes), bloqueio `original_kael_elara_sha_sources_missing`. Render C12 protegido pelo job `source_preflight`: run 43824476754 SUCCESS (11 testes), `C12_DISPATCH_WAIT_FOR_EXISTING_SOURCE_BYTES`, 0/9 originais, job Remotion SKIPPED. Nunca alegar MP4 pronto, identidade aprovada nem renderizar a partir das mães antigas V1. Próximo gatilho real é importar `uploads/alchemy-ep01-cinema-3-originais.zip` com SHA exato e as sete camadas técnicas antigas C12 antes do render técnico. Registro definitivo em `estado-atual.json` e `ESTADO-ATUAL.md`.

**AGENTE AUTONOMO: REFERENCIAS EM FALTA:** ao encontrar `character-bible.png` com SHA mas sem closes originais aprovados por SHA, `remake_autopilot.choose_next` deve emitir `source_readiness`, `original_kael_elara_sha_sources_missing` e informar os arquivos exatos faltantes. Nao solicitar aprovacao impossivel nem repetir chamada de imagem. Quando fonte chegar, o workflow `qa-alchemy-chat-cinematic-references.yml` importa bytes originais; identidade de Kael/Elara/Aldric continua exigindo revisao visual humana, independentemente do SHA.

**IMPORTACAO DE ORIGINAIS V2 SEM LOCK V1:** `videoforge.cinematic_chat_references` deve validar `estado-atual.json` e `autonomy-policy.json` em vez de exigir o antigo `SEM-GERACAO-NOVAS-IMAGENS.lock` (arquivado). Workflow `qa-alchemy-chat-cinematic-references.yml` só aceita originais por hash exato, não gera imagens e não modifica autorização de geração V2. `QA-CHARACTER-BIBLE-V2.json` deve refletir SHA realmente importados, não flag obsoleta; sem aprovação automática de Kael/Elara/Aldric ou MP4. Fontes antigas V1 não substituem os closes originais aprovados de 941×1672.

**REFERENCIAS ORIGINAIS ANTES DE APROVACAO:** a `character-bible` V2 gerada por prompt textual nao recebeu anexos com imagens aprovadas de Kael, Elara e Aldric. O relatorio `QA-CHARACTER-BIBLE-V2.json` marca identidade e original visual como pendentes. NUNCA supor a identidade correta nem aprovar uma prancha somente por SHA/tamanho. Comparar com fontes aprovadas (originais SHA-registrados) antes de qualquer canonizacao/rig/roteiro de cena.

**PROTECAO ANTI-DUPLICACAO DE GASTO:** antes de disparar imagem, verificar o PNG permanentemente arquivado por canal/episodio/asset e seu SHA+PNG+manifesto mesmo em runners novos. `videoforge.production_art.archived_reference` bloqueia recompra da mesma referencia; o workflow autonomo grava `QA-CHARACTER-BIBLE-V2.json` com dimensoes e revisao humana pendente. Nao inventar aprovacao ou converter/cortar rostos para forcar 9:16.

**RECONECTAR PROXY SEM CHAVE LOCAL (15/11/2026):** se `chatgpt-codex-proxy` nao tiver `PROXY_API_KEY`, o script `scripts/renovar-sessao-videoforge.ps1` agora usa container+volume Docker temporarios com chave efemera e login oficial no navegador; nao altera container original, nao salva tokens em arquivos versionados, destroi container+volume no final. Teste de sintaxe PowerShell e 11 testes offline passaram em Actions 43782680348. Executar `git pull origin main` antes do script; somente apos novo login e importacao de secrets o workflow manual com `resume_remake=true` podera retomar uma unica arte. Nao afirmar OAuth renovado sem evidencia de nova execucao.

**RECUPERACAO OAuth AUTONOMA APOS LOGIN DO RESPONSAVEL:** `scripts/renovar-sessao-videoforge.ps1` reimporta secrets e dispara `proxy-health-official.yml` com `resume_remake=true`. Somente se o health confirmar conta OAuth valida, `videoforge/remake_recovery.py` reserva UMA nova tentativa no checkpoint mestre, envia commit para `main` e entao dispara `production-art-by-request.yml`. Repeticao de health, antigo `workflow_run` ou push de codigo NAO pode gerar imagem. Sem segunda tentativa quando a reserva ja mudou ou a imagem foi arquivada. Nunca contornar autenticacao expirada, limites de fornecedor ou aprovacao visual.
**BLOQUEIO REAL DE CREDENCIAIS (15/11/2026):** Codex Proxy respondeu `/health` 200 mas snapshot importado tem OAuth expirado e 0 contas elegiveis; `/admin/accounts/:id/refresh` falhou HTTP 502. A aprovacao permanente de geracao NAO restaura tokens. Rodar `scripts/renovar-sessao-videoforge.ps1` no computador do responsavel, reimportar secret por canal, testar `python -m videoforge.proxy_images health` e somente entao liberar uma nova geracao. NUNCA repetir imagens cegamente, mascarar diagnosticos e atualizar checkpoint. Video nao publicado.

**AUTORIZAÇÃO PERMANENTE DE CHAMADAS — EP01 V2 (pedido expresso em 15/11/2026):** o responsável autorizou o VideoForge a executar **todas as chamadas necessárias de geração de imagens e de IA para este episódio sem voltar a solicitar autorização individual**. Fonte: `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/autonomy-policy.json`. `paid_provider_calls_approved=true`, `auto_dispatch_generation=true`; uma chamada faturável por run do produtor, sem teto **editorial total** de imagens. Isso não suspende cota externa, preço, 429, proteção de segredos, controle de duplicação por SHA nem QA de personagem/rig. O coordenador pode reservar e despachar **uma** primeira candidata `character-bible` automaticamente; a reserva deve persistir na `main` ANTES do `workflow_dispatch`, não reemitir pedido após falha ambígua. Nova permissão por imagem não é exigida. **Não publicar no YouTube nem declarar aprovação visual humana por conta própria.** Para outros canais/episódios, usar política própria.

**C01-P02 — não repetir edição paga de componente já arquivado.** Consultar `remake_sword_source.preflight` e `remake_sword_pack._find_part` com mãe SHA+run, `scene=c01` e `shot_id=C01-P02` antes de cada edição. Novos runners não têm o `output/` anterior: somente o acervo permanente evita retrabalho. Não forçar nova geração quando `REMAKE_SWORD_COMPONENT_ALREADY_ARCHIVED_SAME_MOTHER`; revisão artística pode exigir planejamento específico de nova versão. Nunca inferir aprovação de um teste sintético.

**Auditoria obrigatória de geometria real (C01-P02):** `videoforge/remake_rig_geometry.py` mede bbox, centro e máscaras das três peças móveis da espada em pixels decodificados do PNG SHA-verificado; testa o underlay RGB opaco e deriva poses nos quadros 0/7/72/89 usando somente o `sword-bundle.json` de fonte real. O workflow `remake-sword-pack.yml` salva `mask-geometry.qa.json` dentro do artifact; o preview `remake-sword-preview.yml` exige `--verify-report` que recalcule o relatório e recuse alteração. **Isso é uma proposta técnica, não aprova anatomia/visual, não libera render oficial ou imagem paga.** Todos os outros 38 planos visuais também requerem validação de geometria quando tiverem fonte; ainda não há fonte aprovada.

**Áudio original C01-P01 preservado por SHA:** executar `python -m videoforge.remake_episode_audio --verify-only` antes de planejar o render oficial e `--prepare --destination motion-remotion/public/vf-remake/c01-p01` na preparação dos assets. A síntese procedural já aprovada tecnicamente em 43709191586 é reproduzível sem baixar artifact com prazo de expiração, e o código falha se SHA da WAV divergir da prova `QA-C01-P01-REMAKE-V2.json`. Preparar som NÃO significa 40 tomadas prontas nem autoriza YouTube.

**Direção por tomada executável como tarefa (40 shots):** ler `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-v2-motion-directions.json` (160 etapas/4 por shot) ANTES de produzir rig ou editar. Validar com `python -m videoforge.remake_motion_directions`. O compilador de fila `remake_starter.py` inclui marcos temporais, peças RGBA e QA por shot. NUNCA fabricar pivôs/medidas em pixel quando `source_geometry_calibration_required=true`; tais parâmetros só podem vir da mãe real SHA-verificada. C01-P02 usa 0/7/72/89; C12-P01 usa 0/4/86/119. O plano é direção, não mídia renderizada, não autorização de custo ou aprovação visual.

**Fonte de render V2 (40 tomadas):** usar `remake-v2-cinematic-edl.json` gerada por `python -m videoforge.remake_v2_edl --check` e o `remake-ep01-planos.json` atual. `timeline-cinematografica.json` de 37 permanece **legado imutável** e não pode alimentar o vídeo oficial V2. O Remotion só aceita 40 tomadas com QA humana por fonte e áudio **original C01-P01** SHA-verificado (não mudo). Sem 39 artes e WAV materializado, nenhum MP4 completo. Testes Python e Node precisam passar.

**V2 atualizado por solicitação editorial (15/11/2026):** trabalhar com **14 cenas, exatamente 40 tomadas, 39 visuais + C01-P01 preta, 4890 frames/163s**, conforme `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/{roteiro.json,remake-ep01-planos.json}`. As três tomadas adicionadas são C01-P05 (mãos/lanças), C08-P04 (roda e fuga) e C12-P04 (broche); não alterar C01-P02 (espada do carrasco, frames 60–149), identidades, proibição de Elara no tribunal inicial ou custos. **A menção histórica a 37 planos em commits/testes antigos não prevalece contra os dois arquivos ativos.** Nunca inventar mídia ou marcar aprovação sem QA e revisão reais.

**Produção específica da espada C01-P02 (15/11):** `videoforge/remake_sword_source.py` e `remake-sword-component.yml` reutilizam o proxy existente e a referência arquivada para preparar **uma** candidata RGB opaca (underlay) ou RGBA com alfa real (bainha, lâmina, mão) por **workflow_dispatch manual**. A política atual `paid_provider_calls_approved=false` e máximo 0 impede toda geração paga; NUNCA acionar manualmente, em push ou via agente sem custo explicitamente aprovado e âncora V2 SHA/human approved. O produtor legado da cena C01-P04 não é fonte desta tomada. Salvar cada PNG real (mesmo reprovado por alfa) em `assets/geracoes` com produtor/run/sha; empacotador só deve aceitar `candidate_*_verified` e recomposição do mesmo SHA. Resultado técnico NÃO equivale à aprovação visual ou MP4 oficial.

**Regra C01-P02: arquivos permanentes e disparo autônomo.** `remake_sword_pack.py` só empacota PNGs SHA-verificados dos produtores `production-scene-request`, `production-rgba-request` e `production-sword-underlay-request`; todos devem apontar para a **mesma mãe C01-P02**, `scene=c01`. Workflow `remake-sword-pack.yml` faz scan gratuito por push e publica artifact se a fonte existir. Workflow `remake-sword-preview.yml` escuta `workflow_run` e só renderiza depois de encontrar esse artifact. A estimativa de pivô de máscara é apenas rascunho técnico, nunca aprovação humana. **Ainda faltam** a âncora visual V2 aprovada, o gerador de underlay opaco e a adaptação do gerador RGBA legado para `shot_id=C01-P02`. [Contrato](docs/C01-P02-PACOTE-ARTE-E-RIG.md).

## Skills e bibliotecas reutilizaveis — prioridade obrigatoria do VideoForge (15/11/2026)

**C01-P02, integração da prévia:** `videoforge/remake_sword_preview.py` valida arte PNG de origem por SHA, comprova a recomposição neutra real (FFmpeg para decodificar, Python stdlib para compor) e exige referência canônica aprovada; `motion-remotion/src/remake-sword-preview-index.ts` roda o rig independente em ThreeCanvas, com watermark obrigatório **ARTE NÃO APROVADA**. `.github/workflows/remake-sword-preview.yml` faz preflight em push, e só renderiza com artifact autêntico via despacho. `videoforge/remake_sword_checkpoint.py` registra SHA e QA após render. Faltando art, registrar bloqueio, NUNCA criar imagem sintética de produção nem afirmar que o MP4 existe. Manual: `docs/C01-P02-PACOTE-ARTE-E-RIG.md`.

**Abertura C01-P01:** código `videoforge/remake_opening.py` produz áudio de aço totalmente original e entrypoint `motion-remotion/src/remake-opening-index.ts` faz 60 frames pretos por Remotion. O workflow `remake-opening-preview.yml` executa QA rigoroso antes de declarar produção concluída e atualiza o checkpoint; mídia não é commitada devido ao `.gitignore`. **Esse trecho isolado não é MP4 do episódio inteiro, nem substitui o rig de C01-P02.**

**ANTES de criar codigo novo, consultar** [catalogo verificado](docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md) e as skills locais `.agents/skills/videoforge-dorama-remake/SKILL.md`, `.agents/skills/videoforge-rig-2d-three/SKILL.md` e `.agents/skills/videoforge-qa-and-checkpoint/SKILL.md`. O projeto ja instala `remotion`, `three`, `@react-three/fiber` e `@remotion/three`; preferir componentes existentes (`CharacterParts`, `RigidSprite`, `DeformableSprite`) e skills oficiais do Remotion **como referencia**, com origem em commit fixo e sem executar instaladores externos em CI. **Nao substituir a engine por Rigby2D/Spine/PixiJS ou criar outro renderer sem justificativa e aprovacao.**

**Nova base concreta para remake:** `videoforge/remake_starter.py` cria fila deterministica das 40 tomadas, com `task_fingerprint`, workflow candidato e dependencias; o workflow de autonomia deve arquivar esse relatorio como artifact, sem gerar imagem nem fingir aprovacao. Para o plano C01-P02, `motion-remotion/src/remake-sword-motion.ts` + `remake-sword-rig.tsx` reutilizam Three.js e o `RigidSprite` existente para mover MAO, LAMINA e BAINHA como pecas separadas sobre underlay, com pivo do pulso e parametros medidos dos PNGs reais. **Nenhuma arte faltante pode ser substituida por desenho sintetico, crop ou PNG chapado.** O renderer completo nao esta liberado antes dos SHA e QA.

## PRECEDÊNCIA DAS REGRAS — DORAMA EP01 REMAKE V2 (vigente em 15/11/2026)

**Workflows V1 somente para QA técnico/legado:** não exigir o arquivo `SEM-GERACAO-NOVAS-IMAGENS.lock` revogado para realizar auditoria/rig/importação de imagens antigas. O arquivo de 14/11 é histórico, não um veto atual. **Qualquer geração nova continua sujeita** a `autonomy-policy.json`, fonte SHA aprovada, limites de provedor, revisão humana e upload bloqueado. Testar `tests/test_remake_workflow_compatibility.py` para impedir regressões de compatibilidade.

**Workflow corrigido:** para produzir uma imagem-mãe do remake, `production-scene-by-request.yml` deve usar `videoforge/remake_reference.py` (âncora V2 já aprovada, arquivada em `assets/geracoes/production-art-request/<run-id>`, SHA+metadados), **não** baixar a prancha V1 de run histórico. `shot_id` obrigatório no EP01 remake. Não burlar autorização de provedor/custos, revisão estética ou upload.

**CORREÇÃO NO CÓDIGO:** `videoforge/cinematic_direction.py` agora seleciona e valida o manifesto ativo `remake-ep01-planos.json` para a produção V2. A V1 continua nos testes/arquivos históricos. `production_scenes.py` confere o SHA de uma âncora real aprovada antes de chamada ao modelo. A geração de imagens ainda depende de autorização de custo e uma referência V2 confirmada, e o encadeamento do rig/MP4 ainda não é automático.

1. **Fonte de retomada:** `canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md` + `estado-atual.json`; as instruções mais recentes de remake prevalecem sobre restrições de 14/11 preservadas como histórico.
2. **Arte:** estilo `Cinematic Semi-Realistic Fantasy Anime`; 14 cenas/40 tomadas/163s são base inicial, **não um teto de imagens**. Identidade de Kael, Elara, Aldric e guardas consistente; novas imagens devem ter ângulo coerente e fonte versionada.
3. **Animação:** manual principal `docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md` prevalece sobre efeitos de câmera; rig Three.js e malhas reais, PNGs RGBA, underlays, Remotion, QA de movimento no MP4.
4. **Autonomia:** o software GitHub deverá aprender a delegar, validar, corrigir erros determinísticos, retomar e registrar automaticamente. O coordenador atual cobre diagnóstico, SHA e checkpoint, **ainda não** produção integral.
5. **Segurança e aprovação:** imagens do remake autorizadas editorialmente; despesas adicionais/provedor pago não autorizado; não presumir revisão visual humana nem publicar no YouTube.
6. **Prioridade documental:** `REMAKE-EP01-PLANO-OFICIAL.md` e `remake-ep01-planos.json` são o plano vigente. `PLANO-ARTE-RIG-EP01.md` e trechos com lock antigo são **histórico técnico**, não nova proibição. O gerador cinematográfico antigo continua bloqueado pela validação de identidade legada e precisa ser adaptado antes da produção V2.

## REGRA NOVA — AUTONOMIA DO VIDEOFORGE (15/11/2026)

**O VideoForge deve fazer os vídeos e animações no GitHub sem depender de repetidas correções manuais feitas pelo assistente.** Nossa função é orientar objetivos, estilo, histórias e aprovações subjetivas. **O próprio programa** deve ler estado e arquivos SHA, organizar a fila, chamar geradores existentes, separar sprites, criar rigs verdadeiros, renderizar Remotion, executar QA, identificar causa dos erros, corrigir defeitos técnicos determinísticos e retomar do próximo passo sem recriar o que está pronto. Cada falha recorrente deve virar regra e teste de regressão. Referência obrigatória: [manual de autonomia e limites reais](docs/AUTONOMIA-PRODUCAO-VIDEOS.md) e [coordenador inicial](videoforge/remake_autopilot.py).

**Implementação realmente alcançada até aqui:** diagnóstico periódico automatizado, detecção da próxima etapa, verificação dos PNGs arquivados por SHA, atualização do checkpoint e bloqueio de geração paga não autorizada. **Ainda não está pronto o despacho idempotente nem o fluxo integral autônomo de arte → rig → vídeo.** Não declarar o episódio pronto ou o sistema independente antes de comprovar os próximos módulos. Nunca aprovar qualidade artística ou publicação sem autorização.

## REGRA PRIORITÁRIA — IMAGENS SEM COTA EDITORIAL + MEMÓRIA OPERACIONAL (15/11/2026)

**Prioridade do usuário:** qualidade final do dorama: bonito, animado de verdade, rico em detalhes, consistente entre tomadas. **Não existe limite numérico editorial de imagens/iterações.** Quando a geração estiver autorizada, usar tantas imagens-mãe, enquadramentos realmente diferentes, fundos, camadas RGBA e melhorias quantas forem necessárias para o roteiro e o QA. Não reduzir a qualidade só para caber em 5, 10, 30 ou qualquer máximo artificial; não criar duplicações inúteis. Limites efetivos do provedor, segurança, permissões e custos não autorizados continuam válidos.

**Nova autorização específica (15/11/2026):** o remake do EP01 pode produzir novas imagens conforme a direção V2. Preservar V5 como legado técnico sem destruí-lo. Ainda NÃO há aprovação para publicar nem autorização irrestrita de custos.

**Uma fonte mestre obrigatória por vídeo:** `canal/<id>/videos/<video-id>/ESTADO-ATUAL.md`, sempre na `main`. Cada agente deve ler esse arquivo, `AGENTS.md`, manual técnico, `HISTORICO-DESENVOLVIMENTO.md`, `estado-atual.json`, os assets e hashes **antes de começar**. A cada avanço material (arte autorizada, roteiro, pesquisa, rig, QA, render, correção, falha ou bloqueio), atualizar **o arquivo mestre** com data, cena/plano, ação e resultado, status (feito/teste/bloqueado), arquivos/SHA, commit, workflow/run/artifact se existentes, QA, problemas e **próximo passo exato**. Sincronizar JSON e adicionar evento ao histórico na mesma alteração. PR/branch não é `main`; não afirmar integração sem confirmação. Proibido recriar etapas, imagens ou vídeos prontos por perda de contexto. Consultar [checkpoint do EP01](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md) antes de agir.

## REGRA VISUAL OFICIAL EXCLUSIVA DO DORAMA — ESTILO E CÂMERA

**Aplicação:** somente ao conjunto de doramas do canal `alchemy-lab`. [Índice oficial da área dorama](canal/alchemy-lab/dorama/README.md), [prompt mestre e bíblia visual](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PROMPT-OFICIAL-ESTILO-DORAMA.md), [JSON para agentes](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/estilo-visual-oficial-dorama.json) e [miniatura autêntica da amostra](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REFERENCIA-VISUAL-DORAMA-PREVIEW-96.jpg).

**Estética principal:** `Cinematic Semi-Realistic Fantasy Anime`. Quase toda imagem do dorama deve transmitir **emoção/drama e ter ângulo de câmera narrativamente diferente do plano anterior** (alternar posição espacial, altura, tamanho de plano, perspectiva por ombro, plongée, contraplongée, perfil, detalhe, reação etc.). Manter **rosto, cabelos, figurino, cenário, eixo de cena, luz e paleta coerentes**. A amostra enviada pelo usuário mostra guerreiro ajoelhado com capa vermelha, princesa, rei, guardas e vitrais em salão gótico, com luz volumétrica, profundidade e acabamento de ilustração anime semirrealista. **Não copiar o salão/trono automaticamente para outros lugares.** O enquadramento deve seguir o roteiro, evitando repetição ou cortes de cabeça/coroa/membros.

**ESTADO DE AUTORIZAÇÃO ATUAL:** há autorização editorial do usuário para novas imagens **do remake EP01**, não para publicação ou custos adicionais não aprovados. O lock histórico foi arquivado; C01 V5 é histórico. Preservar este estilo visual exclusivamente para doramas de Alchemy Lab.

## REGRA VISUAL ATUAL DO DORAMA C01-P03 — V5, RESPIRAÇÃO DAS COSTAS E CABEÇA

**VERSÃO ATUAL INTEGRADA À MAIN: C01-P03 V5**, não V4. Ler em ordem [checkpoint do episódio](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md), [QA completo V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V5-2026-11-15.md), [manifesto V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/atuacao-c01-p03-v5-respiracao-costas.json), [direção e princípios da V4](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md), [manual de animação](docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). **Não voltar à V4 por falta de contexto.**

A revisão humana da V4 pediu **manter o leve movimento da cabeça e acrescentar respiração sutil nas costas**. Regra de atuação C01: duas tracks, `kael.ombros/translateY` até -1,25px e `kael.cabeca/rotationZ` até -0,32°; jaqueta `mesh.backBreath` original com expansão até 1,05px e elevação até 0,6px, restrita às costas Y857–947, sourcePin da cintura desde Y950 e bordas da gola/laterais fixas. O movimento deve ser uma deformação verdadeira **dos vértices do tecido**, não animação do PNG inteiro. Braço/antebraço/mão direitos apoiados no joelho e **sem transformação global**, bota/perna estáticas; guardas, rei e lanças sem deformação, usando imagem-mãe SHA-verificada como cenário. Não adicionar braços/pés só para aumentar contagem de pixels. **Sem criar novas imagens, sem publicar no YouTube; aprovação visual pendente.**

**Prova técnica atual:** [PR #58](https://github.com/HelioConde/VideoForge-IA/pull/58) integrado à `main`, commit `ae7ca09c3f75ed04498704459a2ac547de810d06`; [main render 43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142) e [TS/testes 43680784182](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784182) **SUCCESS**, artifact temporário da main `14147374656`, MP4 de 3s SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`, QA real da respiração das costas `back_visible_in_mp4=true` com máximo 957 pixels H.264 alterados em ROI, gola 24/75, rei/lanças/bota imóveis no limiar. `humanVisualReview=false`, `publishable=false`. Próximo passo: revisão visual da V5, não nova geração. **Cena C12 segue bloqueada por PNGs/ZIPs originais faltantes.**

## REGRA PERMANENTE — CONTINUIDADE DO DESENVOLVIMENTO NA MAIN (LER PRIMEIRO)

**Nunca reiniciar um projeto, cena, vídeo ou rig do zero sem consultar seu checkpoint.** A branch `main` é a fonte de verdade dos trabalhos integrados. Ler obrigatoriamente [protocolo de continuidade](docs/CONTINUIDADE-DO-PROJETO.md), depois `canal/<id>/videos/<video-id>/ESTADO-ATUAL.md`, `HISTORICO-DESENVOLVIMENTO.md` e `estado-atual.json` (se existirem), além do manual principal de animação e dos arquivos de direção relevantes.

**Ao concluir QUALQUER alteração técnica, asset, QA, render, correção ou etapa de vídeo:**
1. Confirmar primeiro os fatos reais: branch, commit da **main** (ou PR ainda não integrado), workflow/run, status, artifacts, hashes e a existência dos arquivos, sem considerar um mero log como MP4 arquivado.
2. Atualizar **na mesma alteração enviada à main** o checkpoint por vídeo, relatando de forma objetiva o que está concluído, o que é apenas teste técnico, pendências, falhas e o **próximo comando/etapa exatos**.
3. Acrescentar um registro datado ao histórico (sem apagar versões) e sincronizar o JSON. Se o merge/push falhar, **não declarar registro na main**; relatar que está somente numa branch.
4. Sempre reutilizar o código, as imagens originais e os rigs já implementados. Não duplicar pipelines ou recriar trabalho por não consultar o histórico.
5. Separar aprovação estética, código testado, MP4 técnico gerado, aprovação humana e MP4 oficial: **são estados diferentes**. Não arquivar segredos ou tokens nesses registros.

**Episódio ativo do dorama:** [checkpoint Alchemy Lab — Conquiste a Princesa EP01](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md), [relatório ATUAL C01 V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V5-2026-11-15.md) e [histórico integral](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/HISTORICO-DESENVOLVIMENTO.md). **A V5 É A MAIS RECENTE NA MAIN**, PR #58, render/QA 43680784142 **SUCCESS**, artifact `14147374656` e SHA gravado no checkpoint. **C01 tem 2 tracks de ombro/cabeça, malha das costas animada dentro da jaqueta e episódio tem 106 tracks no total**. Cabeça V4 preservada, mão/bota direitos imóveis, rei/coroa e lanças intactos. **Sem aprovação visual humana**; não publicar YouTube. C12 ainda requer 9 PNGs originais. **Não recomeçar roteiro, motor ou imagens.**

## REGRA PRINCIPAL — ARQUIVAR TODAS AS IMAGENS NO GITHUB POR CANAL

**Nenhum gerador VideoForge pode depender somente de artifacts temporários do GitHub Actions.** Sempre que um workflow gerar PNGs (imagem-mãe, referência, camadas RGBA, sprites, olhos, cenários), arquivar os bytes originais em canal/CHANNEL/videos/VIDEO_ID/assets/geracoes/PRODUCER/GITHUB_RUN_ID/ antes de declarar a geração concluída, mesmo que ela ainda não esteja aprovada artisticamente. O histórico de versões fica imutável: nunca sobrescrever arquivos anteriores.

Utilizar os programas videoforge/persist_generated_assets.py e scripts/persistir-imagens-gh.sh. Eles validam PNG e SHA-256, origem de canal/vídeo, limites de tamanho e metadados sem segredos, e criam commit no GitHub. O workflow precisa de permissions: contents: write e checkout com persist-credentials: true. Se o arquivamento ou o push falhar, **marcar a execução como falha**, nunca como produção concluída. Artifacts temporários são apenas cópia de segurança.

**Imagens produzidas fora do runner (ex.: imagem criada no chat do ChatGPT)** requerem uma importação real dos bytes. JSON com SHA, arquivo ZIP apenas preparado ou a exibição de uma imagem no chat não são prova de que o PNG chegou ao GitHub. Verificar a existência e os hashes no repositório antes de informar conclusão. O episódio Alchemy Lab EP01 mantém o bloqueio de NOVA geração: arquivar antigos originais é permitido; produzir novas imagens continua proibido sem autorização explícita.

**Durante revisões visuais, mostrar ao usuário as imagens também no chat**, rotulando referência, rascunho, aprovada ou rejeitada. Arquivamento no GitHub e exibição no chat são obrigações separadas.

## PRIORIDADE MÁXIMA DAS ANIMAÇÕES — MANUAL PRINCIPAL OBRIGATÓRIO

**Antes de produzir, editar, gerar imagens, animar, revisar ou renderizar QUALQUER vídeo, ler integralmente [docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md](docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md).** Esse manual foi definido pelo usuário a partir da pesquisa aprofundada de rig 2D/Three.js/Remotion e **TEM PRECEDÊNCIA SOBRE INSTRUÇÕES CONFLITANTES DE ANIMAÇÃO** em AGENTS.md, README, modelos, prompts, agentes e workflows.

**Contrato obrigatório:** cena-mãe → background reconstruído → PNGs RGBA independentes de personagem/corpo-sem-cabeça/cabeça aberta-fechada/cabelo/roupa/objetos → reconstrução das regiões ocultas → recomposição (diff/QA) → pivôs e malhas reais no Remotion ThreeCanvas → render SWANGLE frame-driven → QA visual → somente revisão/publicação autorizada.

**Proibido tratar movimento de câmera, bob da imagem inteira, sticker de pálpebras por cima do cabelo, deformação do corpo achatado ou vídeo sintético como animação articulada aprovada.** Em personagens animados, somente sprites internos com rig e malha reais; se faltar arte ou aprovação, declarar `pipeline_pendente`. Para piscar, editar a MESMA imagem/cabeça original mudando somente os olhos; preservar os demais pixels e a transparência. Sem novos custos não autorizados, sem modo workflow `private-quota-live`, sem upload automático.

**Precedência:** regra geral nº 1 (tudo pelo programa GitHub e sem publicação não autorizada) + este manual para toda decisão de animação. Instruções antigas abaixo sobre overlay de olhos ou bob devem ser interpretadas como histórico de prévias **LEGADAS E REPROVADAS**; não autorizam repetir tais técnicas no vídeo oficial.


## REGRA DE ENQUADRAMENTOS CINEMATOGRÁFICOS — doramas, anime e narrativas

**Para histórias com múltiplas tomadas, ler [docs/GUIA-ENQUADRAMENTOS-CINEMATOGRAFICOS.md](docs/GUIA-ENQUADRAMENTOS-CINEMATOGRAFICOS.md) antes de solicitar imagens.** Um plano geral não pode ser duplicado 20 vezes como pôster. Alternar conforme o roteiro entre close do rosto, extremo close de olhos, sobre-o-ombro, contraplano, planos médios, detalhes de mãos/objetos e planos de estabelecimento. Expressão e continuidade visual são obrigatórias.

O planejamento é `direcao-cinematografica-planos.json` por vídeo e a API reutilizável `videoforge/cinematic_direction.py`. O gerador `videoforge/production_scenes.py` aceita `--shot-id C12-P01` (quando autorizado); é **uma imagem-mãe nova por ângulo necessário**, da mesma referência canônica, com SHA e recortes RGBA específicos. **Não** usar pan, zoom ou recorte de uma arte ampla como substituto de personagem em close de qualidade. UI/HUD e legendas entram no Remotion, não ficam impressos na arte.

**Não quebrar o Manual Principal:** direção de câmera não equivale a rig real; sem underlays/pivôs/QA `pipeline_pendente`. **Situação atual do Alchemy Lab EP01:** o remake V2 foi autorizado editorialmente em 15/11/2026 e o antigo bloqueio foi arquivado; porém o gerador de tomadas legado ainda depende de referências canônicas aprovadas e integração do manifesto do remake. Não mesclar figurinos, não liberar render sem QA, não executar chamadas pagas sem permissão.

## ESTILO V2 DO DORAMA ALCHEMY-LAB EP01 — sem alterar imagens existentes

Para o episódio **mmorpg-conquiste-a-princesa-ep01**, antes de preparar qualquer tomada, ler [a bíblia visual v2](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/biblia-visual.md) e o [manifesto SHA das duas referências aprovadas como estética no chat](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/referencias-cinematograficas-aprovadas-no-chat.json). Kael: cabelo castanho quase preto volumoso, arranhões no rosto, capa vinho rasgada, ombreira metálica. Elara: cabelo loiro dourado, olhos violeta, vestido branco e violeta com bordados dourados. Não usar descrições de cabelo preto/vestido azul de Elara e Kael sem capa/armadura da v1, que foi preservada como histórico.

**A aprovação é da preferência visual; os PNGs originais ainda estão pendentes no GitHub** e os 71 PNGs antigos não foram recortados, alterados nem aprovados na v2. Validar os arquivos por SHA e revisar eixos, iluminação, ocultações e continuidade antes de produzir; nunca liberar rig ou MP4 a partir de referência de estilo. Apresentar a arte existente também diretamente no chat para revisão e distinguir claramente imagens de referência, rascunho e aprovada. O bloqueio antigo de **não gerar novas imagens** foi substituído pela autorização de remake V2. A aprovação da identidade visual por imagem, a integração técnica do gerador e a autorização de custo continuam pendentes; não confundir estas pendências com o lock histórico.

## REGRA Nº 1 — Vídeos exclusivamente pelo programa VideoForge-IA no GitHub

**Todo vídeo solicitado como produção oficial deve ser criado pelo fluxo de produção do repositório [HelioConde/VideoForge-IA](https://github.com/HelioConde/VideoForge-IA), executado e rastreável no GitHub Actions.** Esta regra tem prioridade sobre qualquer exemplo, demonstração, script temporário, renderer externo ou solução improvisada.

1. Usar o **programa reutilizável do projeto**, seus modelos, agentes e etapas reais, organizados em `canal/<id>/videos/<video-id>/`. Não criar um gerador paralelo específico de um único vídeo para contornar componentes ausentes.
2. Pesquisa/roteiro → arte consistente por cena → separação de personagens e cenários em camadas → animação → narração → edição/legendas → QA técnico e visual. Executar cada etapa disponível e registrar as que ainda faltam. **Não simular agentes ou artes como se tivessem sido gerados.**
3. Gerar MP4 no runner do GitHub Actions do próprio repositório; registrar workflow, run ID, commit, entrada, manifesto por canal, SHA-256, artefato e relatórios de QA. Baixar ou mostrar a cópia do MP4 é permitido, mas **não** criar/substituir a produção fora do programa.
4. Se faltarem agentes, imagens ou integração do fluxo principal, **parar como `assets_pendentes` / `pipeline_pendente` e explicar a limitação**. Não substituir por desenho vetorial, cartões ou narração sintética genérica e apresentar o resultado como o vídeo oficial solicitado. Previews experimentais podem existir para testar motores, sempre marcadas claramente como **`preview_tecnico_nao_oficial`**.
5. Apenas uma execução verificável do fluxo principal, com materiais realmente gerados e verificados, pode receber o rótulo `video_oficial_do_programa=true`. Render bem-sucedido no GitHub, por si só, **não significa** produção completa pelos agentes.
6. **Sem limite artificial para quantidade de cenas**. Segurança, licenças, orçamento aprovado, duração e QA permanecem obrigatórios. Publicação no YouTube exige autorização e verificação próprias.

**Correção histórica:** o teste *Spy x Family* da execução [43545398967](https://github.com/HelioConde/VideoForge-IA/actions/runs/43545398967) foi renderizado pelo GitHub Actions, mas usou `videoforge.spy_family_animated` e desenhos vetoriais de prévia, **não** o fluxo oficial completo de artes/agentes. É um teste técnico, não produção oficial do VideoForge-IA.

## REGRA OBRIGATÓRIA — cena-mãe → camadas RGBA → rig → montagem

**Para QUALQUER vídeo animado, não basta deslocar a ilustração inteira.** Cada cena deve cumprir:

1. **Cena-mãe original:** gerar e guardar a imagem completa no programa, com SHA-256, ID de canal/vídeo/cena, dimensões, enquadramento, pose, figurino, perspectiva, luz e estilo. É a única referência visual para derivar os recortes dessa cena.
2. **Background reconstruído:** editar A PRÓPRIA cena-mãe para retirar personagens e objetos móveis, preenchendo a parte originalmente escondida. Preservar tamanho, perspectiva, iluminação e coordenadas; não inventar um cenário novo.
3. **Personagens separados:** editar A MESMA cena-mãe para extrair cada personagem/parte que se moverá em PNG **RGBA com transparência alfa real** e na mesma posição/escala. Extrair objetos móveis e foreground separadamente se existirem na cena; não inventar objetos ausentes.
4. **Sem duplicação:** a camada base não pode manter o cabelo/capa/braço/objeto que será desenhado novamente como sprite animável. Restaurar partes encobertas de corpo/cenário antes do movimento. Sobrepor tecido na costura, manter pivôs corretos e rosto-base opaco durante piscadas.
5. **Animação verdadeira:** Remotion/rig movimenta personagem, olhos/cabelo/roupas/objetos isolados, com movimentos sutis naturais e vento quando cabível. Movimento de câmera ou pan **é adicional**, não substituto do rig.
6. **QA fail-closed:** verificar SHA da cena-mãe em todas as camadas, PNG RGBA/transparência real, dimensões, alinhamento, ausência de recortes/duplicações, movimento de partes independentes, olhos, rosto, bordas e costuras em vários quadros, narração e legendas. Se algum componente essencial faltar: `pipeline_pendente`; `rig_animado_aplicado=false`; `video_oficial_do_programa=false`. Nunca declarar vídeo oficial com MP4 de pan.
7. **Sem teto de cenas:** a quantidade vem do roteiro; limites de orçamento de inferência, tempo de execução, licenças e duração são controles **separados**. Não consumir chamadas adicionais sem orçamento autorizado.
8. **Local de execução:** usar exclusivamente os módulos reutilizáveis do `HelioConde/VideoForge-IA` e GitHub Actions. Guardar assets e QA por canal/cena, publicar artifacts de revisão, nunca publicar no YouTube sem aprovação.

Ver `docs/PADRAO-ANIMACAO-POR-CAMADAS.md` e `docs/TESTE-CAMADAS-CENA.md`. O exemplo da capa vermelha foi um experimento de rig para outra cena: jamais reutilizar automaticamente seus prompts de aventureiro, cabelo castanho, espada ou capa em outros personagens.

## [LEGADO — NÃO USAR EM PRODUÇÃO] Regra antiga de microanimação e QA visual

Evitar flutuação: amplitude vertical máxima de **2,8 pixels por personagem** na composição 1080×1920; câmera e objetos mais sutis que a animação principal. Piscar somente com overlay RGBA de pálpebras compatível com a cena-mãe, mantendo cabeça/rosto-base opacos; nunca fingir piscada via transparência do rosto. Cabelo, roupas e objetos exigem sprites próprios e prova de remoção da base; não inventar elementos nem afirmar rig completo quando só há movimento de grupo/câmera. Testar quadros de olhos abertos/fechados e cortes; manter workflow **normal**, nunca o modo `private-quota-live`. Toda prévia sem rig integral é teste técnico não oficial.

## [LEGADO — SUBSTITUÍDO PELO MANUAL] Antigo QA de overlay de olhos

Uma piscada **não pode cobrir a franja** nem criar uma mancha de pele sobre cabelo, sobrancelhas ou acessórios. A imagem de olhos fechados gerada por IA é somente material bruto: restringir sua máscara alfa à área exata dos olhos da cena-mãe, excluir todos os pixels classificados como cabelo frontal e colocar a franja REAL extraída do personagem original em **z-index maior** que o sprite de pálpebras. A ordem de composição é `background -> personagem RGBA original -> olhos-fechados-SEGUROS -> franja-original-foreground -> objetos independentes reais -> legendas`. Não habilitar `eyesClosed` sem `hairForeground` validado, SHA de origem correspondente, QA dos pixels e avaliação visual. O cabelo desenhado no personagem-base pode ser usado no foreground somente sem movimento independente até existir underlay e rig próprios; não duplicar cortes móveis.

## Correção prioritária da piscada — editar a MESMA imagem inteira (substitui adesivos)

A partir desta revisão, para vídeos novos, a piscada NÃO deve ser construída por um sticker de olhos ou sobreposição de pele. **Enviar exatamente o `character-main.png` original da cena-mãe ao endpoint de edição de imagem**, com uma única alteração permitida no prompt: **a mesma personagem de olhos fechados**. Cabelo, franja, roupa, rosto, acessórios, pose, escala, cor, iluminação, fundo/transparência e os demais personagens não podem mudar. Gerar uma segunda imagem completa com os olhos fechados, de mesmas dimensões e coordenadas; **alternar entre imagens completas de olhos abertos e fechados**, com o mesmo pivô de animação e sem qualquer overlay.

QA fail-closed: verificar SHA-256 da imagem original de referência, modelo/resultado, dimensões; em seguida restaurar EXATAMENTE os pixels e o canal alfa da imagem original em todas as regiões fora dos olhos (inclusive cabelo e franja). Se a IA devolver PNG opaco, usar só sua informação de cor dentro dos olhos e sempre restaurar o alfa original. Exigir diferença visível exclusivamente nos olhos, nenhum pixel não ocular ou alfa alterado, e revisão visual humana. O pipeline antigo de overlay de pálpebras/cabelo-foreground permanece legado e NÃO é usado nesta nova prévia. Usar GitHub Actions normal, nunca `private-quota-live`. Não declarar aprovação de rig completo.

## [HISTÓRICO — VER MANUAL PRIORITÁRIO] Sincronização antiga de PNG inteiro

A troca `character-main.png` ↔ `character-eyes-closed-safe.png` exige **posição e transformações idênticas** nos dois lados. Nunca reinicializar o seno ou a animação abruptamente no frame da troca. O corpo e todos os elementos anexados devem desacelerar por `12` quadros até a **pose neutra**, mantê-la pelo intervalo de `3` quadros antes/depois do centro da piscada e retomar a respiração de forma suave nos `12` seguintes. Mesmo envelope de neutralização para a câmera: nenhum recorte, zoom, rotação ou deslocamento pode dar um salto nos quadros de transição. Em cada frame de troca: deslocamento X/Y = 0, rotação = 0, zoom = 1, pan = 0 em relação à composição-base. QA testa limites de variação quadro a quadro.

Cabeça e corpo separados só podem ter movimento **independente** quando existirem sprites RGBA reais, corpo **sem a cabeça**, cabeça aberta/fechada consistente e pivot validado; sem estes assets, o vídeo de teste usa microanimação do corpo/conjunto e `independent_head_motion_active=false`. Nunca mostrar falsamente um rig individual. O movimento deve terminar e começar com neutralidade antes/depois dos cortes. Ver `motion-remotion/src/blink-motion-sync.ts`.

## REGRA DE RIG REAL — movimento interno, NÃO PNG inteiro

Quando o usuário solicitar movimento de cabeça, cabelo, roupa, capa, braços ou objetos (como na pesquisa detalhada de 14/11/2026), a implementação oficial deve usar **Remotion ThreeCanvas + malhas reais e partes independentes**. O protótipo de character idle, pan da câmera, zoom, filtros FFmpeg e o movimento de personagem achatado são apenas prévias legadas, nunca satisfazem o requisito de rig articulado.

1. **Arte canônica:** usar cena-mãe, background limpo, corpo sem cabeça, cabeça aberta/fechada, mechas e tecido/objetos SEPARADOS. Todas as peças RGBA vêm da mesma referência, coordenadas originais e hashes verificáveis.
2. **Animação:** pivô no pescoço, máximo ±2° no MVP, olhos como duas versões da MESMA cabeça com só os olhos alterados, malha 7x9 ou similar com vértices superiores fixos e deformação suave nas pontas. Movimento calculado exclusivamente com useCurrentFrame(), sem useFrame()/requestAnimationFrame, relógio ou física de estado acumulado.
3. **Transições:** quadro de troca possui pose/pivô iguais. Easing para neutro e retorno gradual, evitando salto perceptível.
4. **QA:** render de pose neutra deve recompor a arte original com tolerâncias e inspeção visual; SHA, RGBA, bbox, z-index, ausência de duplicação de rosto/capa/cabelo e revisão humana são obrigatórios. Se faltar qualquer sprite ou QA, rig pendente, vídeo não oficial.
5. **Runner:** nova imagem pré-compilada GHCR rig-three-remotion4-v1, workflow normal do GitHub Actions com --gl=swangle --concurrency=1 e sem modo private. Preservar runner e workflows legados isolados para não comprometer produções anteriores.
6. **Não inventar assets:** não aplicar capa/espada de aventureiro em Anya ou outros personagens que não os possuam. O smoke 43580456827 usa figuras sintéticas e **não** é vídeo de canal. O primeiro vídeo real com este motor somente após gerar e validar head/body/hair/props da cena 01.

Ver documentação: docs/RIG-THREE-MALHA.md. O modelo permanece operacional=false até QA real do vídeo por malha.

## Instruções obrigatórias para cada tarefa

**Ler nesta ordem, antes de pesquisar ou produzir qualquer vídeo:** `README.md`, `AGENTS.md`, `docs/ARQUITETURA.md`, `docs/REGRAS-EDITORIAIS.md`, `canal/README.md`, `canal/<id>/README.md`, **`canal/<id>/ESTRATEGIA.md`**, `canal/<id>/canal.json`, histórico e reservas do canal e, se útil, `docs/referencias/CATALOGO-CURSOS-YOUTUBE.md` e `docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md` (para pesquisa, Analytics, SEO, Shorts, direitos, classificação infantil e IA) e **`docs/CODEX-PROXY-ACTIONS.md` antes de qualquer trabalho envolvendo ferramentas de IA, Go ou Actions**.

**Hierarquia com precedência:** a estrutura canônica é **`canal/` no singular**, conforme `docs/ARQUITETURA.md`. Não criar `canais/` alternativo. Separar rigorosamente canais; dados do vídeo em `canal/<id>/videos/<video-id>/editorial.json`, manifesto renderizável em `video.json`, índice de histórico em `canal/<id>/editorial/historico-videos.json`. Não substituir o formato técnico do manifesto. Conferir histórico e temas relacionados antes de criar nova pauta. Não presumir que o índice inicial vazio comprova ausência de vídeos no YouTube.

Ler `docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md` como síntese **de fontes oficiais consultadas**, e revalidar os links originais quando decisões envolverem regras atuais. Antes de qualquer publicação futura, checar duração e Content ID em Shorts de mais de um minuto, originalidade contra conteúdo massificado/repetitivo, direitos, classificação infantil e eventual obrigação de declarar uso de IA. Nenhuma dessas instruções habilita publicação no MVP.

Os cursos listados são **fontes sugeridas para estudo**, não prova de acesso, aprendizado ou método validado. Não inventar conteúdo das aulas. Não registrar geração, QA ou publicação sem evidências.

## Integração central com Codex Proxy\n\nTodas as integrações futuras de pesquisa, roteirização e imagens devem usar o gateway definido em `docs/CODEX-PROXY-ACTIONS.md`, sem instalar Go ou clonar o upstream em cada workflow. A imagem do proxy é compilada uma vez em build isolado no GHCR; jobs posteriores usam serviço persistente ou contêiner pré-compilado. O modo efêmero não persiste tokens OAuth renovados, logo não é a opção principal. Nunca imprimir ou versionar `CODEX_PROXY_ACCOUNTS_JSON`, `CODEX_PROXY_API_KEY` ou `CODEX_PROXY_BASE_URL` privado; credenciais somente via GitHub Actions Secrets. Não habilitar geração paga em push/PR; `health` não gera imagens e `generate` é disparo manual único. Se upstream privado mudar, falhar com erro verificável, jamais tentar contornar limites 429. Geração não equivale a aprovação visual nem MP4.\n\n## Autenticação do projeto antigo: migração local

A cópia antiga usa o Environment `proxy-runtime`, mas os valores de Secrets não podem ser recuperados por API. O script `scripts/migrar-codex-proxy.ps1`, para uso **local no Windows**, importa o `accounts.json` existente no Docker ou em arquivo privado e registra os novos Secrets via stdin no `gh` CLI. Nunca armazenar tokens, senhas, chaves, dumps ou arquivos de conta em commits, logs, discussões, PRs, artifacts ou GitHub Pages. Não afirmar que houve migração até ela ser executada localmente e verificada em Actions. Consulte `docs/CODEX-PROXY-ACTIONS.md`.

## Testes de separacao generativa por camadas

Antes de modificar ou executar rotinas de edicao de cenas, leia `docs/TESTE-CAMADAS-CENA.md`. Os workflows `scene-layers-basic.yml` e `scene-layers-advanced.yml` executam somente por `workflow_dispatch`, reutilizam o mesmo PNG original verificado por hash, usam o proxy Go PRECOMPILADO e limitam no maximo 2 imagens por run, sem retry automatico. Resultados vao exclusivamente para `output/<canal>/videos/<video-id>/assets/<cena>/` como artifacts; nunca sao versionados, enviados ao YouTube ou classificados como animacao pronta. O manifesto tem `human_visual_approval=false`, `pixel_alignment_verified=false` e `animation_implemented=false` ate verificacao adequada. Uma edicao por IA NAO e recorte fiel e nao pode substituir QA humano.

## Prévia de animação de camadas verificável

O workflow manual `animate-separated-layers.yml` consome somente o artifact do Teste 2, sem chamadas ao proxy, sem reinstalação de Go/FFmpeg e sem upload ao YouTube. O motor `videoforge/animate_layers.py` anima 3 camadas independentes via FFmpeg, verifica SHA-256, RGBA real, movimento entre quadros e codecs do MP4. A capa e demais peças que ainda existem no personagem-base **não podem ser adicionadas como overlays**, pois isso duplicaria roupa/objetos. É obrigatório criar personagem-base sem a peça e pivôs revistos antes do rig. `modelos/camadas-animadas` permanece desabilitado para produção completa. Ver `docs/ANIMACAO-CAMADAS.md`.

## Motor Remotion reaproveitado do projeto antigo

Para prévias animadas de PNGs, usar como **primeira escolha** a composição React em `motion-remotion/src/scene-layer-preview.tsx` e o [guia](docs/REMOTION-ANIMACAO.md). Os módulos `character-idle.ts`, `cinematic-motion.ts` vieram do `AutoEditorVideo/motion-remotion` fixado em `ec85db5bc74455122e4501aba05bd2dd3fd0df2c`, e `videoforge-motion.ts` do antigo VideoForge. A renderização é executada no workflow `remotion-animate-layers.yml` usando imagem GHCR de Node/Remotion/Chrome já compilada, sem npm ci ou download do navegador a cada job. FFmpeg somente gera silêncio e verifica codecs/quadros. Validar SHA, RGBA e identidade do canal antes de compor, **não duplicar a capa**, não fingir rig de membros/cabelo, não enviar ao YouTube. Modelo `camadas-animadas` ainda não é produção pronta.

## Rig 2D de malha (opt-in, nao aprovado para producao)

Ler [docs/RIG-MALHA-2D.md](docs/RIG-MALHA-2D.md) antes de preparar sprites ou alterar `motion-remotion/src/mesh-rig.tsx`. O rig SVG so pode ser ativado com cinco sprites RGBA sem partes duplicadas, hashes vinculados a cena e `human_review` verdadeiro **apos** revisao real. Nao usar `character-main.png` no mesmo modo de render que `body-no-head-no-cape.png` e `cape.png`. Validacao automatica nao prova qualidade visual; manter `publishable=false` e `visual_review=pending` ate revisar MP4. A existencia de codigo nao significa que os PNGs ou o artifact de rig ja existam. Nao executar inferencia IA nem upload por conta propria.

## Preparacao do rig candidato por cena (sem aprovacao automatica)

Consultar [docs/PREPARAR-RIG-CANDIDATO.md](docs/PREPARAR-RIG-CANDIDATO.md) e `canal/<id>/videos/<video-id>/rig-plan.json` antes de alterar máscaras. `videoforge/rig_candidate.py` **nao** executa SAM2/LaMa nem reconstrói anatomia escondida; apenas gera recortes e previews de risco. Na cena piloto o desenho inclui **segundo olho parcialmente visível** e capa frontal/traseira; separar as partes evita duplicações. Sempre manter `human_review=false` no rascunho; não renomear seu artifact para `rig-...` nem alimentar o workflow de MP4 final sem correção de arte, checagem de oclusão e aprovação humana. O workflow `rig-candidate.yml` não chama API de IA nem publica vídeos.

## Regra permanente — não limitar cenas por número

Nunca acrescentar `MAX_SCENES`, faixas como `3 <= len(scenes) <= 24`, ou checagens exigindo exatamente 10 cenas nos geradores de vídeo. O número de cenas é consequência do **roteiro e dos cortes visuais necessários**, não um teto arbitrário. Validar que a lista é não vazia, caminhos e conteúdo de cada cena, direitos, tempo final do formato, QA e uso de recursos; jamais truncar ou descartar cenas automaticamente para caber em número máximo. Dividir trabalhos em lotes técnicos quando necessário preservando a ordem e o conteúdo, sem limitar o número total de cenas. Orçamento de geração de imagens, quotas de APIs, timeout e limites de duração do Shorts permanecem controles separados e não podem ser burlados.

## Padrão universal da animação de personagens

Antes de desenhar, separar sprites, montar rig ou renderizar personagens de **qualquer canal**, leia [`docs/PADRAO-ANIMACAO-POR-CAMADAS.md`](docs/PADRAO-ANIMACAO-POR-CAMADAS.md). A regra geral é: base do rosto sempre opaca durante a piscada; cabelo e roupas separados apenas quando houver underlay e sobreposição nas costuras; junções ancoradas nos ombros/pescoço; movimento determinístico de corpo, cabelo, roupa e câmera sem fendas, duplicação ou esticar a cabeça. Todo vídeo exige continuidade entre cenas, QA de quadros e aprovação visual. A prévia vetorial de Spy x Family prova apenas o motor: **não** tratá-la como ilustração final ou publicação.

## Objetivo inicial

**No MVP técnico**, comprovar MP4 vertical do Otaku Multicena com 90–180 segundos, áudio audível e QA. **Na produção oficial**, usar exclusivamente o programa integrado no GitHub, com agentes/etapas reais, ilustrações e mídia comprovadas. Validar o renderizador não equivale a gerar vídeo final pelo programa.

## Regras de execução

- O comando smoke usa mídia sintética para testar tecnologia; **jamais**
  registrar esse clipe como produção realizada por agentes.
- O comando render só usa mídia real explicitamente fornecida;
  não inventar identidade de personagem, fontes ou artefatos.
- Sem upload para YouTube e sem chamadas pagas de IA nesta etapa.
- Jamais adicionar credenciais, respostas privadas, imagens geradas,
  áudio de produção ou MP4s ao Git.
- Registrar origem, orçamento e autorização antes de integrar provedores
  de imagem, voz ou pesquisa; não contornar 429 com repetição cega.
- Manter QA fail-closed; qualquer falha de áudio, duração, resolução
  ou integridade bloqueia declaração de vídeo concluído.
- Alterar código em branch/PR e verificar CI antes de integrar.
- Não tocar no repositório antigo. Organizar arquivos por canal,
  preservar documentação e não introduzir agentes visuais fictícios.

## Regra de execução sem instalações repetidas

Os workflows de produção devem reutilizar imagens GHCR pré-compiladas. Usar `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2` para renderização e o proxy pinado do `docs/CODEX-PROXY-ACTIONS.md` para IA. Nunca reinstalar Go, FFmpeg ou serviços em cada job de vídeo; builds/atualizações são feitos só nos workflows de infraestrutura, com cache e tags estáveis. Runners hospedados ainda precisam baixar a imagem, pois não persistem disco entre execuções. Toda troca de imagem exige smoke real H.264/AAC com QA.

## Validação

    python -m unittest discover -s tests -v
    python -m videoforge.mvp smoke --output dist/smoke.mp4

Conferir artefato de Actions: video H.264, áudio AAC, 1080 × 1920 e QA JSON.
Esse teste não autoriza vídeo público nem consumo de IA.

## Organização permanente — mesmo contrato do VideoForge anterior

Sempre consultar `README.md`, `docs/ARQUITETURA.md` e
`docs/ESTRATEGIA_SHORTS.md` antes de editar ou planejar Shorts.
O guia de Shorts é orientação **editorial**, não autorização para novos jobs,
provedores pagos, pesquisa privada ou publicação.
A estrutura do repositório anterior `HelioConde/video-forge-ia2` é a
referência **apenas para organização**, sem copiar credenciais, pipelines
complexos nem trabalhos fictícios.

- Cada canal vive exclusivamente em `canal/<id>/`; seus dados não podem
  migrar nem ser misturados com os de outro canal.
- Em `canal/<id>/`, manter `canal.json`, `README.md`, 
  `conteudos/indice.json`, `editorial/candidatos.json`,
  `editorial/reservas.json` e `videos/README.md`.
- Pesquisas com fontes ficam em `editorial/pesquisas/YYYY-MM-DD.json`.
  Pastas de arquivo editorial têm valor histórico, **não são fila de produção**.
- Cada vídeo real usa `canal/<id>/videos/<video-id>/video.json`. O modelo
  técnico padrão vem de `canal.json.modelo_padrao`, com sobrescrita opcional
  em `video.json.modelo`; modelos reutilizáveis em `modelos/<id>/modelo.json`.
- Geradores específicos de nicho podem viver em `geradores/<id>/` somente
  quando houver implementação e testes reais; não inferir trabalho ativo a
  partir de arquivos de configuração.
- Manter resultados e dados temporários em `output/<id>/editorial/` ou
  `output/<id>/videos/<video-id>/`, nunca versionados.
- O MVP só processa `otaku-br` e `imagem-estatica` fornecida. O modelo
  `camadas-animadas` está **planejado, não implementado**. 
- `videoforge/paths.py` deve falhar antes de gerar mídia se o canal,
  diretório, receita técnica ou destino de saída estiverem incorretos.
- Em toda mudança: organizar antes e depois, atualizar docs,
  testar regressões, verificar Actions; nunca editar outros repositórios,
  gastar IA ou publicar YouTube sem autorização explícita.

## Diagnosticar rig sem aprovar sprites

Para ver movimento antes de reconstruir partes ocultas, o workflow `rig-draft-preview.yml` produz MP4 **com marca d'água de rascunho** e quadros de revisão. O módulo `videoforge/rig_draft_preview.py` deve aceitar somente `rig-candidate` com `human_review=false`, SHA validado e origem/canal corretos; nunca converter rascunho em aprovação ou publicar o vídeo. Marcar `publishable=false` e registrar inpainting pendente no QA. A versão de produção segue exigindo `validate_rig_dir` com aprovação visual humana.
