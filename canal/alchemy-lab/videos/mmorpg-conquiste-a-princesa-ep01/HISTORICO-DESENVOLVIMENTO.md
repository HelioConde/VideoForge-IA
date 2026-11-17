## 2026-11-17 — Continuação C02-P02 até C05-P02 + Arken

- Avanço de **5 para 12 mães originais arquivadas** entre 39 tomadas visuais: adicionadas C02-P02, C03-P01, C03-P02, C04-P01, C04-P02, C05-P01 e C05-P02, todas em PNG original 941×1672, SHA e run registrados. Imagens não aprovadas automaticamente.
- QA editorial por pranchas originais, sem chamar proxy: #44084847732 (C02-C03) e #44086630803 (quarto). Achados principais: C03-P01 ainda não é macro da íris; intensidade dos ferimentos muda; possível diferença de coroa/gola do rei; Kael em pé/sentado na transição do quarto.
- Corrigida referência indevida de C03-P02 (trono medieval) para quarto gamer, monitor e Kael casual V2. Uma tentativa bloqueada por câmera fora do contrato, corrigida restaurando foco/movimento canônicos antes de qualquer geração paga.
- Novo cenário `arken-muralhas` inserido em `INDEX-BIBLIA.json` e gerado [#44087301592](https://github.com/HelioConde/VideoForge-IA/actions/runs/44087301592), antes de C05-P02. Teste da Bíblia inicialmente impunha 39 itens e depois apresentou escapes inválidos; corrigido e [CI #44087741614](https://github.com/HelioConde/VideoForge-IA/actions/runs/44087741614) passou.
- Novo `CHECKPOINT-IMAGENS-EP01-AUTO.json` calcula contagem diretamente das imagens-mãe verificadas por SHA; atualiza no script de arquivamento, sem IA e sem aprovação fictícia. [Teste #44086150957](https://github.com/HelioConde/VideoForge-IA/actions/runs/44086150957) aprovado.
- **Gates de rig/MP4/YouTube permanecem fechados**, sem geração de recortes de imagem-mãe para animação.

## 17/11/2026 — Checkpoint consolidado: 5 mães, V2 reparadas e QA visual

- **40 tomadas = 39 com arte + C01-P01 preta.** Mães originais arquivadas para **C01-P02, C01-P03, C01-P04, C01-P05 e C02-P01** (5/39); **34 tomadas ainda sem mãe original**. O registro de geração tem 84 PNGs de diferentes papéis, não 84 tomadas.
- **C01-P03 V1 reprovada:** apareciam guardas/lanças/espada antecipados. [V2 versionada #44080234599](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080234599) remove esses elementos, preserva Kael ajoelhado e Aldric ao fundo (SHA `bfc1249dc1f83b004b620c333f5aa81689b0ba0c23a3e7573d57c09dcf3539e3`).
- **C01-P04 V1 reprovada:** Kael em pé. [V2 gerada #44080462345](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080462345) corrige Kael ajoelhado, rei sentado e lanças cruzadas, mas o original saiu 941×1671; [alinhamento gratuito #44080887693](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080887693) produziu versão 941×1672 (SHA `2d11099a536999409a33dae2fc30c517e260c4ad640e41c6942c85b9db499ec5`) mantendo pixels da IA. [Prancha real V1×V2](QA-MAES-C01-P03-P04-V2.jpg), [revisão visual assistida](REVISAO-VISUAL-MAES-C01-P03-P04-V2.md), [QA gratuito #44080972625](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080972625).
- **Novas mães de outras tomadas:** C01-P05 [#44079588294](https://github.com/HelioConde/VideoForge-IA/actions/runs/44079588294), C02-P01 [#44081215706](https://github.com/HelioConde/VideoForge-IA/actions/runs/44081215706), ambas arquivadas com SHA; revisão artística ainda pendente.
- A recomposição de C01-P03 com peças geradas do **V1** foi reprovada por escala e elenco. **Não usar sprites V1 no rig**; depois de aprovação de mãe V2, pedir ao proxy novas imagens de background/Kael/Aldric/objetos separadamente, com escala/posição referenciadas; **sem recortes locais como arte**.
- Novo produtor `videoforge/ep01_corrected_mother_v2.py`, workflow `ep01-corrected-mother-v2.yml`, alinhamento local de 1px e QA V1×V2 com arquivamento imutável. Testes anti-repetição/SHAs (GitHub Actions #44079337714 e #44079911430) passaram sem geração paga. Correções e histórico: [RESUMO-PRODUCAO-IMAGENS-EP01.md](RESUMO-PRODUCAO-IMAGENS-EP01.md).
- **Todos os gates de aprovação humana, rig, MP4 e publicação continuam bloqueados**. Não promover sucesso de API, SHA, padding ou QA de imagem para aprovação anatômica.

## 17/11/2026 — Resultado da recomposição C01-P03: REPROVADO para rig

- **Aldric separado foi realmente gerado pelo proxy** no [run #44076356345](https://github.com/HelioConde/VideoForge-IA/actions/runs/44076356345), PNG 941×1671 SHA `a6eb021cb6c2788530a6fc541831f14d8f99e0392c21de02510f2fdf2312a0f0`. O original foi arquivado e a cópia técnica foi alinhada SEM nova IA para 941×1672 no [run #44076886141](https://github.com/HelioConde/VideoForge-IA/actions/runs/44076886141), SHA `0bcdbc8ef6263bef8c063f1ea696019998efa32a5a45789a9e3054b8b1544285`.
- **QA C01-P03 com três partes separadas do proxy concluído tecnicamente:** [run #44077543911](https://github.com/HelioConde/VideoForge-IA/actions/runs/44077543911). [Comparação verdadeira](QA-C01-P03-PROXY-RECOMPOSICAO.jpg) e [métricas](QA-C01-P03-PROXY-RECOMPOSICAO.json): MAE RGB `36,6056/255`, `58,21%` dos pixels com diferença de intensidade ≥18; Kael RGBA bbox `[0,32,907,1643]`, Aldric `[0,16,941,1671]`.
- **Reprovação da recomposição (inspeção assistida):** escala/posição dos dois PNGs de personagens NÃO reproduzem a mãe. Ambos foram engrandecidos/reposicionados. A mãe C01-P03 também contém guardas com lanças e espada que deveriam ser revelados na C01-P04; foram omitidos indevidamente da separação e estão fora da intenção editorial de C01-P03. Detalhes em [REVISAO-VISUAL-C01-P03-PROXY.md](REVISAO-VISUAL-C01-P03-PROXY.md). A diferença RGB alta também reflete props ausentes, não apenas erro de escala.
- **Correção de regras:** plano C01-P03 passa a declarar **somente Kael e Aldric** visíveis, com guardas/lanças/espada ocultos. Fonte V1 é rejeitada; exige **nova mãe V2 versionada**, sem sobregravar os arquivos existentes. Prompts dos PNGs separados agora exigem escala e bbox exatos, sem zoom/recentragem. Gate impede novas peças da mãe C01-P03 reprovada; testes `tests/test_ep01_proxy_separate_parts.py` e verificação gratuita do plano atualizados.
- **Não usar nenhuma das 3 partes atuais para rig** apesar do padding e da transparência tecnicamente válidos. Não fingir que o gate automático equivale a aprovação humana. `human_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`.


## 2026-11-17 — Mães C01-P03/P04, background e Kael do proxy + alinhamento técnico

- Criadas imagens-mãe C01-P03 (#44073592014, SHA `89bc3b1b...`) e C01-P04 (#44075357179, SHA `156a9376...`), com 3 e 6 referências da Bíblia respectivamente. São candidatas, não arte aprovada. Mãe V1 C01-P02 segue rejeitada, V3/V4 em revisão.
- Criados `videoforge/ep01_proxy_separate_parts.py`, workflow `ep01-proxy-separate-part-by-request.yml` e testes. Gerador desenha novo PNG por background/figura/objeto, com referências SHA verificadas; máscara/crop não produz sprite final.
- Background C01-P03 via proxy #44074495093 e Kael separado RGBA #44075692204: ambos em 941×1671, falharam QA de igualdade de canvas. Preservados originais, corrigida somente 1 linha inferior por processo **offline auditável**: #44074895225 e #44075946150 (941×1672), mantendo todos os pixels da IA. Nenhuma IA paga para alinhamento.
- Ajustes de confiabilidade: testes históricos de C01-P02 isolados, validação por produtor para não aceitar máscara V1, Pillow carregado antes da chamada paga, verificação de request via SHA do evento em vez de HEAD. Primeira falha local de Pillow ocorreu **depois** de retorno do proxy e não salvou o PNG; corrigida antes de próximas chamadas. Registro completo [RESUMO-PRODUCAO-IMAGENS-EP01.md](RESUMO-PRODUCAO-IMAGENS-EP01.md).
- 39 visuais planejados, 3 mães originais registradas (somente C01-P03/P04 novas nesta etapa); 36 ainda sem mãe. Sem aprovações visuais, rig, MP4 ou publicação.

## 2026-11-17 — Seis especialidades com oito skills locais validadas

- Incorporadas 3 skills originais em `.agents/skills/`: `videoforge-shot-direction` (câmera/continuidade), `videoforge-audio-editing` (narração, áudio, SFX e montagem) e `videoforge-technical-research` (versões/licenças/segurança). Preservadas as 5 preexistentes: arte/peças, rig 2D, atuação, QA independente e gerente de dorama.
- Corrigido o frontmatter do gerente `videoforge-dorama-remake` e adicionado roteamento explícito às seis áreas. Atualizados `AGENTS.md`, `README.md` e `docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md`.
- Auditoria externa: CloudAI-X Three.js MIT (loop de tempo precisa de adaptação a `useCurrentFrame()`); Blender Skills MIT (conceitos, não runtime); OpenMontage diverge entre skill `license: MIT` e licença raiz AGPL-3.0, portanto não foi copiado/instalado.
- Criados `tests/test_video_skill_routing.py` e `.github/workflows/qa-videoforge-skills.yml`. [GitHub Actions #44072866500](https://github.com/HelioConde/VideoForge-IA/actions/runs/44072866500): **success** (sem proxy, imagens, MP4 ou publicação). O catálogo de skills é instrução, **não prova de novos subagentes executáveis** nem de roteamento pelo runtime autónomo.
- Gate de imagem C01-P02 ainda aguarda mãe aprovada e PNGs individuais gerados pelo proxy; não liberar rig, MP4 ou YouTube por causa da instalação das skills.

## 2026-11-17 — Regra definitiva de animação: gerar imagens separadas pelo proxy, não recortar

- Decisão do responsável: a cena-mãe é **referência** para o proxy; ele deve gerar background vazio, cada personagem/objeto animável e cada parte de rig em **imagens próprias PNG/RGBA**, com desenho de partes escondidas e consistência canônica. Não criar sprites finais por crop, máscara de pixels, polígonos ou segmentação. Ferramentas locais são apenas QA.
- Contrato global criado em `docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md`, integrado ao manual geral, manual EP01, `AGENTS.md` e `README.md`. Plano de 40 tomadas (39 visuais) atualizado com pedidos explícitos por peça e validador fail-closed.
- Workflows legados de recortes/máscaras e produtor antigo ancorado à V1 rejeitada desativados; arquivos permanecem preservados para comparação, não para rig. O `ep01_contact_gate.py` agora rejeita explicitamente máscaras V1 como fontes finais. [Verificação de política CI #44068898163](https://github.com/HelioConde/VideoForge-IA/actions/runs/44068898163) **success**, sem geração de imagens nem cobrança do proxy.
- Nenhuma nova imagem visual produzida por esta alteração; C01-P02 V3/V4 candidatas em revisão. A integração do produtor autônomo de novos PNGs por peça para as demais tomadas segue pendente. Nada de rig, MP4 ou publicação.

## 2026-11-17 — C01-P02: V4 a partir do patch V3

- Implementados produtor V4, testes de pré-voo e arquivamento com SHA, além da prancha comparativa de oito painéis.
- A primeira execução GitHub #44063003598 retornou HTTP 400 sem gerar mídia; a execução controlada #44063304090 criou dois PNGs (edição e patch), arquivados; QA #44063462507 validou dimensões, hashes, origem e invariância fora da ROI. [Revisão visual](REVISAO-VISUAL-ASSISTIDA-C01-P02-V4.md).
- Novo ponto visual a conferir: bocal dourado simplificado em V4. V1 rejeitada, V3/V4 apenas candidatas. Não foram gerados rig, MP4 ou upload YouTube.

# Histórico de desenvolvimento — Alchemy Lab / Conquiste a Princesa EP01

## 16/11/2026 — ROIs reais e comparador de cores preparados, sem falsificar aprovação

- [Run 43885264961](https://github.com/HelioConde/VideoForge-IA/actions/runs/43885264961) **SUCCESS (7 testes)**: duas pranchas de 6 imagens reais `QA-ALDRIC-ROI-PROPOSTAS-V2.jpg` (C01 com polígonos do rig V1, mais C02/C03 com pose/identidade por verificar) e `QA-ELARA-ROI-CENAS-V2.jpg` (close original, câmera C12 original e cena V1), com manifestos SHA `QA-ROI-FIGURINOS-V2.json` e [guia de conferência](REVISAR-ROI-FIGURINOS-V2.md). **Os polígonos são candidatos V1**, não máscaras individuais de barba, centro/exterior da roupa ou peitoral.
- [Run 43885838968](https://github.com/HelioConde/VideoForge-IA/actions/runs/43885838968) **SUCCESS (3 testes)**: `videoforge/wardrobe_roi_color.py` compara cromaticamente pares de regiões apenas quando há SHA correto, pose/variante e polígonos semanticamente verificados, com teste sintético reproduzindo vermelho→preto e REPROVAÇÃO automática. Contrato `CONTRATO-ROI-SEMANTICAS-V2.json`. Em imagens reais, `QA-COMPARACAO-ROI-SEMANTICA-V2.json` mostra **4/4 regiões com EVIDÊNCIA INSUFICIENTE**; nenhuma aprovação/reprovação numérica foi inventada. A reprovação anterior do usuário para Aldric (cores/barba) e Elara (roxo do vestido) permanece em vigor.
- **Para avançar com validação efetiva:** conferir a identidade e pose da C02/C03, delimitar máscaras de barba/tecido externo/centro nas duas poses e corpete de Elara nas duas imagens palacianas. O comparador só pode gerar alertas/reprovações por diferenças cromáticas; histogramas semelhantes não bastam para aprovação visual completa. Nenhuma imagem paga, MP4 oficial ou upload YouTube nesta etapa.

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

## 15/11/2026 — programada retomada idempotente de referencia apos login OAuth

- Nenhuma nova execucao comprovada depois dos testes anteriores; a conta importada permanece com ultimo status `PROXY_OAUTH_SESSION_EXPIRED`.
- Criado `videoforge/remake_recovery.py` + testes de repeticao/politica/origem e conectado o workflow de health ao unico pedido da arte quando `resume_remake=true`.
- Script Windows passa a disparar health e retomada unica apos login no navegador/importacao dos secrets, mantendo uma chamada por run, arquivo SHA, sem aprovacao visual falsa e sem publicar no YouTube.
- Testes e CI do novo fluxo ainda devem ser confirmados e checkpoint atualizado depois da execucao.

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

## 15/11/2026 — autorização prévia permanente e disparo único por coordenador

- Pedido do responsável: todas as chamadas de geração do EP01 V2 sem autorização individual; documentado nos arquivos principais e policy do canal.
- Política mudou de `paid_provider_calls_approved=false/auto_dispatch_generation=false` para ambos `true`, mantendo **1 chamada por execução** e `auto_publish_youtube=false`.
- Adicionada reserva em `remake_autopilot.py` e chamada a `gh workflow run production-art-by-request.yml` depois de o estado ser gravado na main. Teste de idempotência, custeio e não publicação incluído.
- Registro documental/código **não é evidência de execução paga**. Confirmar run/artifact PNG+SHA depois do CI; novas chamadas só podem ocorrer sem repedir permissão, mas nunca com origem incerta ou retry cego.



## 15/11/2026 — CI da proteção de origem/antirrepetição aprovado

- [43762440988](https://github.com/HelioConde/VideoForge-IA/actions/runs/43762440988) **SUCCESS**, editor com 9/9 testes e nenhuma chamada de provedor. Correção da expectativa antiga em [commit 4b57e743](https://github.com/HelioConde/VideoForge-IA/commit/4b57e743af2bfb844a50351b2e2c90634b00ea39), após primeira falha de teste [43762352543](https://github.com/HelioConde/VideoForge-IA/actions/runs/43762352543).
- [43762352508](https://github.com/HelioConde/VideoForge-IA/actions/runs/43762352508) **SUCCESS**, scanner com 4/4 e fixture de pacote/rig com 25/25 testes. `pack_real_source_only` **skipped**, bloqueio real `REMAKE_SWORD_V2_ANCHOR_NOT_APPROVED_OR_VERIFIED` confirmado.
- Código de origem no [commit 8e536070](https://github.com/HelioConde/VideoForge-IA/commit/8e5360709a915b6f0d7d0a8e7a9960ab3d0fa1fe). QA técnico em fixture ≠ imagem/MP4 real. Sem chamada paga e sem publicação.

## 15/11/2026 — correção anti-cobrança duplicada e vínculo estrito de componentes

- O editor `remake_sword_source.py` passou a verificar o acervo permanente antes do proxy, eliminando reruns pagos de uma parte já verificada para a mesma mãe.
- O `remake_sword_pack.py` rejeita partes de outra tomada, outro produtor ou outro run de fonte, mesmo com um SHA de PNG válido; as quatro peças precisam de prova `C01-P02`.
- Casos adicionados a `tests/test_remake_sword_source.py` e `tests/test_remake_sword_pack.py`. Estado **código enviado para CI (a verificar)**; não inventar resultado antes dos runs.
- Sem imagens, MP4 ou autorização paga novos. Pendência preservada: referência visual V2 validada por humano e os quatro PNGs reais da espada.

## 15/11/2026 — verificação definitiva do medidor de máscara C01-P02

- `6e92be296fcb8ddc8d1e3759973c463cba9b258f`: módulo `remake_rig_geometry.py` e relatório `mask-geometry.qa.json` ligados ao packer e ao renderer da espada; testes gerados com PNGs temporários, sem aprovação artística falsa.
- Primeiro run `43758376230`: 1/23 testes falhou devido a um JSON adulterado de 13 bytes ser rejeitado corretamente como relatório ausente/inválido antes da etapa de comparação (expectativa do teste incorreta, e não violação do gate).
- `21a48bdf6c257d9bd8609f7c540585f4362ba6be`: teste de adulteração corrigido para falsificar `official_video_approved=true` em relatório válido. [Run 43758686070](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686070) SUCCESS: **23/23 testes**, SHA/RGBA/centroide/anti-repetição, scanner de fonte real bloqueado pela âncora ausente.
- [Run 43758686035](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686035) SUCCESS: smoke ThreeCanvas; [43758686062](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686062) SUCCESS: 70 testes da autonomia; [43758686092](https://github.com/HelioConde/VideoForge-IA/actions/runs/43758686092) SUCCESS: compositor e 23 testes Python.
- PNGs sintéticos usados só em `TemporaryDirectory`, sem arte/custos/publicação. Nenhum MP4 C01-P02 real criado. Próximo: âncora visual V2 aprovada, mãe própria e quatro PNGs reais, então pack + medição + preview automático + QA humano.

## 15/11/2026 — medição de máscaras e auditoria de pivôs no workflow de C01-P02

- Criado `videoforge/remake_rig_geometry.py` como prova técnica SHA/pixels da fonte C01-P02; bbox, centroide, alpha count, pivô candidato, 4 poses derivadas do draw e fingerprint da direção. FFmpeg só decodifica para QA e ThreeCanvas continua motor de animação.
- `remake-sword-pack.yml` agora inclui `mask-geometry.qa.json` no artifact verdadeiro antes de entregar ao renderer. `remake-sword-preview.yml` exige `--verify-report` para rejeitar relatório alterado, SHA incompatível ou ausência de fonte; sem aprovação automática do rig/anatomia.
- Fila `remake_starter.py` informa dependência explícita de calibração nas 39 tomadas visuais, mantendo `geometry_pixels_measured=false` onde falta arte real. Adicionados testes isolados e workflow QA; resultados CI aguardando.
- Nenhum MP4 real novo, imagem paga ou envio YouTube; orçamento permanece fechado. Próximo: conferir testes e reutilizar o contrato por tomada após mães próprias aprovadas.

## 15/11/2026 — seis runs de QA confirmam compositor V2, 160 movimentos e audio

- Commit `c50da2e59ef9241a3b9aa3a8038700252fc9aec1`: compositor Remotion corrigido para 40 tomadas, C01-P01 WAV original obrigatória e nova EDL editorial V2; runs `43755753904`, `43755753902`, `43755753960` SUCCESS (inclusive legado TS).
- Commit `6b7f7df7d1c2fc581a2e401a84599943118b8f17`: JSON de 160 momentos de rig/câmera/sons, validador integrado à fila, fingerprint por tomada; runs `43756504753` (56 testes) e `43756504858` SUCCESS.
- Commit `a1c2d0816847998c2171f05ed78255acc0a7b003`: síntese determinística original do SFX da espada para o futuro compositor; runs `43756803890` (60 testes) e `43756803794` (14 testes + TypeScript) SUCCESS. WAV gerada no runner QA, hash idêntico à prova original; nada de trilha de terceiros nem novas despesas.
- O roteiro ficou em 40 tomadas e 14 cenas, 4890 frames/163 s; 39 planos com imagem permanecem pendentes. Zero MP4 oficial novo, zero autorização/consumo de imagens pagas e nenhum YouTube.

## 15/11/2026 — eliminar dependência do artifact temporário para WAV C01-P01

- Novo módulo `remake_episode_audio.py` reutiliza síntese procedural original `remake_opening.py`, exige QA permanente da C01-P01 e SHA da WAV antes de disponibilizar `sword-original.wav` para `motion-remotion/public`.
- Os jobs de autonomia só verificam hash; o QA do compositor prepara WAV idêntica para teste, sem MP4 novo, imagens, publicação ou inferência. Testes contra alterações de evidência e bytes.
- CI aguardando prova. Permanece bloqueado render oficial sem as 39 imagens reais e aprovação humana.

## 15/11/2026 — quatro ações independentes para cada tomada, integradas aos agentes

- Criado `remake-v2-motion-directions.json` (40 tomadas × 4 ações = 160 marcos temporais) com direção cinematográfica concreta de espada, malha de cabelo/roupas, pulsação de olhos, rodas, mãos, trono, broche, visemas e som original.
- `videoforge/remake_motion_directions.py` confronta cada shot, duração, elenco, câmera, falas e cenas com `roteiro.json`/`remake-ep01-planos.json`; rejeita plano adulterado, etapas ausentes, fake de SHA/aprovação e pivôs declarados medidos sem arte real.
- A fila `remake_starter.py` fornece as quatro instruções, peças e QA por tarefa aos agentes, com fingerprint; workflows de autonomia e compositor validam. A edição e custo externos permanecem bloqueados e nenhum vídeo é declarado pronto.
- CI de integração pendente de resultado. Próximo: buscar referência real V2 aprovada, calibrar pivôs e malhas a partir das imagens, não de números editoriais.

## 15/11/2026 — alinhamento do compositor oficial V2 com 40 tomadas e som

- Descoberta de gate 37 fixo no `cinematic-timeline.ts`: teria recusado o episódio 40-shot; corrigido para 40 com exigência dos 3 novos inserts e 4890 frames.
- `remake-v2-cinematic-edl.json` + `videoforge/remake_v2_edl.py`: nova lista editorial da V2; `timeline-cinematografica.json` V1 preservada integralmente.
- Abrir C01-P01 com SFX original em Remotion exige WAV SHA verificada, sem fallback mudo; sem bytes staging a EDL continua não renderizável.
- Workflows de autonomia e QA do compositor passam a validar os dois contratos, sem IA paga; CI pendente.

## 15/11/2026 — V2 com 40 tomadas validado integralmente no CI

- Commit `967fd5211eb619f57944f59e6d48537c3d05cdca` atualizou roteiro/manifesto oficial, testes, autonomia e documentação para 40 tomadas em 14 cenas e 163s; criadas C01-P05, C08-P04, C12-P04 como inserts não aprovados.
- Run `43751714168` SUCCESS: 45 testes passaram, fila real do VideoForge compilou `shots 40 visual 39`, arte gerada=0, vídeo gerado=false; artifact `14176058160`; bloqueio de gasto preservado.
- Run `43751714070` SUCCESS: 14 testes do empacotador e máscara/QA passaram com somente fixtures temporárias, job de pack de arte real pulado por falta de âncora; sem gasto.
- A versão V2 permanece `remake-v2-20261115` e C01-P02 permanece 60–149. Os relatórios históricos de 37 planos descrevem a etapa **anterior**, não o plano ativo de 40.
- Próximo: aprovação/arquivo da âncora visual V2 e autorização separada de custo para continuar geração real, sem upload de YouTube.

## 15/11/2026 — usuário define 40 tomadas mantendo 14 cenas

- Atualizado o roteiro `roteiro.json` e o manifesto ativo `remake-ep01-planos.json` juntos: 40 tomadas, 39 com arte-mãe e C01-P01 preta; duração preservada em 163 segundos/4890 frames.
- Novos cortes cinematográficos independentes: C01-P05 (mãos/lanças atrás de Kael), C08-P04 (roda articulada e fuga de Elara), C12-P04 (broche prateado de Elara; revelação só C12). Preservada a C01-P02/rig da espada, 60–149, e o restante dos eventos.
- Adaptados os testes e a fila determinística para 40, contratos do autocoordenador, README, AGENTS.md e plano oficial. Mantida a versão `remake-v2-20261115` para não invalidar mídias e hashes técnicos já auditados.
- **Status:** atualização editorial do plano, sem gerar imagem paga, sem MP4 novo, sem aprovação artística e sem upload. Confirmar GitHub Actions antes de chamar os testes de sucesso.

## 15/11/2026 — produtor de underlay e RGBA C01-P02 com QA GitHub validado

- Commit `12f238a6ae2663489fe9b6b38edd19f44ee6dbb5`: gerador específico `remake_sword_source.py` e workflow `remake-sword-component.yml` (manual pago somente após gate). Reuso do Codex Proxy e archiver existente; uma chamada por execução, fonte `cena-01-c01-p02.png` SHA auditada e âncora V2.
- [Run 43749686509](https://github.com/HelioConde/VideoForge-IA/actions/runs/43749686509): SUCCESS, tests de custo/origem/arquivo e job pago skipped.
- Commit `efad5702d74224a8eb88793b753be1ba5ceb30f1`: testes do produtor usam fixture do empacotador sem coletar seus testes não relacionados. [Run 43749824057](https://github.com/HelioConde/VideoForge-IA/actions/runs/43749824057): **8 tests, 8 PASS, 0 SKIP**, 2,945s; produção paga skipped.
- **Não ocorreu qualquer geração real**; nenhum modelo de imagem foi chamado, nenhum PNG V2 foi produzido, não houve aprovação humana nem YouTube. Gatilho de custo permanece fechado, preservando limite financeiro.
- Próximo: gerar/revisar referência canônica V2 com custo autorizado, mãe C01-P02 real, executar quatro runs de componentes quando explicitamente permitido; packer e rig técnico já têm integração validada.

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

## 2026-11-15T21:57:01Z — diagnóstico automático de retomada

- Etapa: generate_character_bible; alvo: character-bible; bloqueio: no_verified_reference_png.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T01:03:42Z — retomada apos OAuth validado no runner

- Reserva unica de recuperacao persistida ANTES de redisparar o workflow de arte. Nenhuma imagem, cobranca confirmada, aprovacao humana ou upload ao criar reserva.
- Proxy health autenticado e elegibilidade foram exigidos pelo workflow. Sem resultado de arte ainda; proximo passo: geracao e QA por SHA.

## 2026-11-16T01:09:47Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: archived_png_verified_human_review_pending.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T01:31:58Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: human_visual_review_pending.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T07:26:28Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: original_kael_elara_sha_sources_missing.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T10:41:03Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: human_visual_review_pending.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T12:45:23Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: human_visual_review_pending.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T13:04:04Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: human_visual_review_pending.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T13:06:23Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: wardrobe_identity_rejected_reference_missing.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 2026-11-16T13:55:16Z — diagnóstico automático de retomada

- Etapa: review_identity_reference; alvo: character-bible; bloqueio: wardrobe_identity_rejected_reference_missing.
- Apenas verificação de estado/arquivos. Nenhuma mídia criada ou aprovação inventada.

## 16/11/2026 — Integridade dos pixels das exclusões (branch de revisão)

Validador integrado a `wardrobe_roi_exclusions.run`: RGB do PNG deve coincidir com a fonte no recorte; alfa só pode ser mantido ou zerado; contagem removida deve conferir; recorte deve conter todos os pixels retidos. Ver `QA-ROI-INTEGRIDADE-PIXELS-V2.json`. Oito regiões reais passaram; 6 testes de exclusão e 34 testes relacionados passaram localmente. Base main `976e779`; esta mudança ainda não foi integrada nem executada em Actions. Não altera polígonos, PNGs arquivados, contrato oficial ou aprovação: 0 máscaras semânticas, R2/MP4/YouTube bloqueados. Próximo passo: revisar este patch e validar em CI; depois conferir as exclusões sobre os originais completos.

## 16/11/2026 — Candidatas V3 e integridade de pixels (PR #63)

Corrigida a direção da exclusão no tecido externo de Aldric sentado, após inspeção do original: V2 atingia dobras acima da haste. V3 recupera 472 pixels e remove outros 258 em relação à V2; total excluído frente à máscara inicial: 487. Sete máscaras restantes idênticas por SHA. V2 e fontes originais preservadas. Não é aprovação semântica: EVIDENCIA_INSUFICIENTE nas oito regiões.

Programa valida RGB original, alfa somente subtrativo, recorte completo e contagem. Áreas protegidas bloqueiam exclusões sobre tecido anotado. 22 testes locais de ROI passaram; CI da branch será conferida antes do merge. Novo workflow qa-wardrobe-roi-pr.yml não gera imagens nem escreve no repositório. Produtor existente exporta V3 sem sobrescrever V2.

Arquivos: ROI-EXCLUSOES-CANDIDATAS-V3.json, QA-ROI-EXCLUSOES-V3.json, QA-ROI-EXCLUSOES-V3.jpg e assets/qa-roi-exclusions-v3/. Revisão: REVISAR-MASCARAS-FILTRADAS-V3.md. R2, MP4 e YouTube continuam bloqueados, zero chamadas pagas. Próximo passo: validar CI e integração; revisar barba/boca/gola, bordados e corpete pequeno contra as fontes completas antes de alterar contrato semântico.

## 16/11/2026 — V3 integrada e executada no GitHub

PR [#63](https://github.com/HelioConde/VideoForge-IA/pull/63) integrado: [f5a7f3e](https://github.com/HelioConde/VideoForge-IA/commit/f5a7f3e779c0f9284a5f3947f51bfd74084963e5). QA do PR [43942403827](https://github.com/HelioConde/VideoForge-IA/actions/runs/43942403827): SUCCESS, 22 testes ROI. Produtor main [43942596191](https://github.com/HelioConde/VideoForge-IA/actions/runs/43942596191): SUCCESS, 8 testes de exclusões e exportação V3. Commit de saída: f3ce91e. Depois do fetch, SHA das oito fontes e oito máscaras conferidos. PNGs V2 preservados; JPEG V3 foi reexportado pelo Pillow do runner.

A candidata de tecido externo Aldric A recupera 472 pixels e remove outros 258 versus V2; sete máscaras restantes idênticas por SHA. Nenhuma máscara semanticamente aprovada: 0/8, 0/4 pares oficiais; R2/MP4/YouTube bloqueados, zero chamadas pagas. Próximo passo: inspecionar os originais completos e as bordas V3 para barba/boca/gola, adornos e corpete B; não promover contrato por testes de integridade.

## 16/11/2026 — Separar alerta cromático de dúvida de iluminação

Correção em wardrobe_roi_color: divergência forte de histograma com lighting_differences_may_be_present verdadeiro, ausente ou inválido retorna EVIDENCIA_INSUFICIENTE, preservando métricas e chromatic_alert, sem reprovação automática nova. Só False booleano, após revisão externa, permite a reprovação cromática em ROIs verificadas. Nunca preencher esse campo apenas para obter resultado. Reprovações prévias do proprietário continuam ativas.

Regressão reproduzida: fixture sintética com mesma proporção RGB e exposição 10x menor era reprovada; após correção mantém incerteza. Controle vermelho versus preto com iluminação descartada continua reprovado. 23 testes ROI locais passaram. PNGs, polígonos V3 e contrato real não foram alterados: 0/8 máscaras semânticas e 0/4 pares, R2 bloqueada, nenhuma chamada paga. CI e integração pendentes nesta entrada; consultar registro mais recente antes de retomar. Próximo passo: revisar fontes e anotar diferenças de iluminação sem apagar a reprovação conhecida dos figurinos.

## 16/11/2026 — QA iluminação integrado (PR #64)

Commit [5285f51](https://github.com/HelioConde/VideoForge-IA/commit/5285f5150b73279fd26941373e31508b22f6977a) confirmado na main. Workflow [43944144582](https://github.com/HelioConde/VideoForge-IA/actions/runs/43944144582) SUCCESS: 23 testes ROI e recálculo das oito regiões sem escrever imagens. Fixtures de exposição testam o mecanismo, não aprovam os figurinos reais. Nenhuma máscara modificada nesta rodada; 0/8 aprovações semânticas e R2 bloqueada. Próximo passo: revisar as fontes completas, cobertura e iluminação; não definir flags de aprovação por histograma.

Verificação pós-merge: workflow semântico da main [43944320147](https://github.com/HelioConde/VideoForge-IA/actions/runs/43944320147) também terminou SUCCESS. Mantidos quatro pares reais sem evidência suficiente e nenhuma aprovação automática.

## 16/11/2026 — Revisão contextual das oito máscaras V3

Programa agora exporta QA-ROI-CONTEXTO-V3.jpg com quatro colunas alinhadas: fonte com contexto, máscara anterior, pixels removidos e máscara final. O contexto é recortado da fonte SHA e amplia apenas a prévia; coordenadas e SHA da prancha constam no relatório V3. Medições continuam em pixels nativos, nunca no JPEG. Oito PNGs finais mantêm exatamente os hashes anteriores.

Inspeção: corpete B representa cobertura parcial e oclusões de manga/cabelo/adornos. Não expandir por cor nem preencher partes ocultas automaticamente. Barba B ainda exige separação boca/bigode. 25 testes ROI locais passaram, incluindo alinhamento, pixels removidos exatos e bordas sem padding. CI e publicação concluídos; ver checkpoint PR #65 nesta página. Zero máscaras aprovadas e R2 bloqueada; próxima etapa é revisão semântica no contexto original.


## 16/11/2026 — Revisão contextual integrada (PR #65)

PR https://github.com/HelioConde/VideoForge-IA/pull/65 integrado no commit 69e6d90c5057952bb995500a046861a9a907f1a1. CI https://github.com/HelioConde/VideoForge-IA/actions/runs/43945520844 SUCCESS, 25 testes ROI. Exportação na main https://github.com/HelioConde/VideoForge-IA/actions/runs/43945693308 SUCCESS; artefatos versionados em 123e004d4c838137137f6e3c117b604e021e293d. Hash da prancha e oito referências de fonte e oito máscaras conferidos após fetch; máscaras idênticas ao checkpoint anterior. Nenhuma aprovação semântica, 0/4 pares oficiais e R2 bloqueada. Próximo passo: revisão contextual das oclusões de Elara B e boca/bigode de Aldric B. Nenhuma chamada paga.

## 16/11/2026 — C01-P04, nova imagem do julgamento gerada pelo próprio Github

- Run [#43965460068](https://github.com/HelioConde/VideoForge-IA/actions/runs/43965460068) SUCCESS. Fonte original Kael anexada e conferida SHA; criado e arquivado PNG `assets/geracoes/production-art-request/43965460068/c01-p04-imagem-inicial-v3.png`, SHA `605ccd361ad9a867eb8b92948010fdbb7d87a031d8b3601c663d815917b1b6cc`, 941×1672; visual ainda não aprovada. Sem imagem do chat usada, sem YouTube.
- Registro e checklist: `REVISAR-IMAGEM-INICIAL-C01-P04-V3.md`. A primeira tentativa (run 43965291280) foi encerrada antes de chamar o provedor por um teste pré-API incorreto, corrigido em commit próprio. Retrabalho evitado via asset idempotente e arquivo SHA.

## 16/11/2026 — Referência C01-P04 escolhida para toda a continuidade do tribunal

- O usuário aprovou o visual da nova imagem C01-P04 ("tá bonito") e determinou que as imagens seguintes preservem as MESMAS características dos personagens. Registrada a aprovação **como âncora visual/identidade visível e estilo**, não como aprovação retrospectiva de máscaras antigas.
- Criado [registro SHA com regras por personagem](CONTINUIDADE-VISUAL-APROVADA-C01-P04.json) e [manual de continuidade](REGRA-CONTINUIDADE-PERSONAGENS-C01-P04.md). O gerador `videoforge.production_art` passou a usar `videoforge.dorama_continuity`: nas novas tomadas elegíveis, envia o **PNG original C01-P04 em /v1/images/edits**, validando SHA/manifests/cast e rejeitando ausência da fonte ANTES do provedor.
- [Workflow QA #43969088308](https://github.com/HelioConde/VideoForge-IA/actions/runs/43969088308) **SUCCESS**: testes de bytes PNG, SHA, elenco, geração por imagem edit e impedimento de recuperar imagens já rejeitadas.
- Próximo plano oficial: **C01-P05**, close dos guardas/lanças, mantendo sua aparência, sem duplicar braços ou alterar o salão. O asset `c01-p05-guardas-lancas-v1` já está no catálogo e a geração deve vir somente do workflow do GitHub.
- A imagem C01-P04 foi produzida em 941×1672; manter pixels originais. Elara não aparece e deve ter referência própria quando for sua vez. Nenhuma publicação é liberada por aprovação de estilo.


## 16/11/2026 — Continuidade real C01-P05 e C02-P01 gerada no GitHub

- Aprovada a imagem C01-P04 **como referência visual de estilo e personagens**. Implementados registro `CONTINUIDADE-VISUAL-APROVADA-C01-P04.json`, `videoforge/dorama_continuity.py`, referências PNG anexadas à edição e verificações de SHA/elenco. A imagem original permanece imutável.
- **C01-P05 guardas:** [run #43969450680](https://github.com/HelioConde/VideoForge-IA/actions/runs/43969450680) **SUCCESS**. Novo PNG SHA `ad5b40722c786b0c9ba761687eedf1b5626cd3ee1c9b4a3ac43fd788841ae4b5` em `assets/geracoes/production-art-request/43969450680/c01-p05-guardas-lancas-v1.png`, 941×1671. Fonte C01-P04 original anexada realmente.
- **C02-P01 close Aldric:** [run #43970462482](https://github.com/HelioConde/VideoForge-IA/actions/runs/43970462482) **SUCCESS**. Novo PNG SHA `a18d2284ed7878e7b81537d1673384e8a506df647e2fd1ea0c1d7f81eb5aaf5d` em `assets/geracoes/production-art-request/43970462482/c02-p01-aldric-rosto-v1.png`, 941×1672, com mesmo SHA da âncora efetivamente enviado.
- [Comparações visuais lado a lado e links](QA-IMAGENS-V3-CONTINUIDADE.md) arquivadas pelo workflow [#43970937395](https://github.com/HelioConde/VideoForge-IA/actions/runs/43970937395) **SUCCESS**. Visualmente a paleta e os materiais do cenário, armaduras, barba, traje e iluminação mantêm boa coerência inicial; o usuário ainda deve confirmar detalhes da coroa, rosto e mãos. Nenhum quadro novo é automaticamente aprovado apenas por SHA.
- Código agora liga `dorama_visual_compare` à geração de novas imagens ancoradas: futura comparação automática tenta ocorrer no mesmo workflow do PNG, sem novo custo de IA. **Automação ainda não exercitada ponta a ponta após integração**. Prévia C01-P03 antiga e rejeições anteriores não foram promovidas.
- Temos três PNGs reais: uma referência aprovada visualmente e duas tomadas candidatas para revisão; ainda não é episódio MP4 oficial nem upload YouTube.



## Skills de animação instaladas — 17/11/2026

Adicionadas videoforge-animation-parts (peças independentes geradas pelo proxy, placement, geometria oculta e diagnóstico de torso cortado) e videoforge-character-acting (poses, intenção e timing). Complementadas rig-2d-three com contatos/deformação e qa-and-checkpoint com QA temporal. Recortes e máscaras permanecem exclusivos de QA conforme CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md. Instalação de instruções; nenhuma geração, rig, render ou aprovação visual ocorreu nesta etapa. Próximo passo: aplicar preparação de peças à tomada selecionada, respeitando aprovação da mãe e proveniência.
