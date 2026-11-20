**EP01 — Revisão V3 de ambientes e trono (20/11/2026):** [instruções](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CORRECAO-CENARIOS-TRONO-V3.md) · [plano](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CORRECAO-CENARIOS-TRONO-V3.json). Corrigir repetição do beco com mercado, portão de serviço e escadaria; carroça sozinha como barricada; Aldric sempre sentado com C01-P04 aprovada intocada. 14 imagens novas versionadas necessárias; fila por Actions e render V3 apenas depois de todas existirem. O MP4 V2 anterior é histórico/reprovado nos trechos citados, não episódio final.

**EP01 — revisão corrigida C07/C08 (19/11):** [MP4 único V2 de 42 tomadas/2min43s](https://github.com/HelioConde/VideoForge-IA/actions/runs/44266014731/artifacts/14411045741) renderizado e verificado; 7 novas imagens-mãe arquivadas, 9 tomadas de perseguição contextualizadas. [Estado técnico](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RESULTADO-EP01-CONTINUIDADE-V2.json). Aguardando revisão visual, sem animação articulada/áudio/publicação; NÃO regenerar os PNGs existentes.

**Runtime multiagente — 18/11/2026, PR #71 em desenvolvimento:** implementação de auditorias somente leitura com SQLite/CAS, mensagens persistentes e provedores desligados. [Execução, escopo e limites](docs/AGENT-RUNTIME.md). Não confundir cadastro de 12 papéis com produção audiovisual autônoma. Não fazer merge nem chamadas pagas sem autorização.

**EP01 — C07/C08 CORREÇÃO V2 (18/11/2026):** a revisão visual identificou fuga com eixo quebrado, soldados parecendo ajudar Kael e carrinho deslocado sem causa. Novo plano versionado com 42 tomadas (mesmos 163s), 7 imagens candidatas geradas sob revisão e preservação dos 39 PNGs antigos. [Guia de continuidade](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CONTINUIDADE-C07-C08-V2.md). Renders V2 devem exigir fontes novas por SHA; não publicar nem aprovar automaticamente.

**EP01 — evidências atuais (17/11/2026):** [Action #44215462090](https://github.com/HelioConde/VideoForge-IA/actions/runs/44215462090) passou: quatro prévias e montagem experimental de 10,33 s, sem áudio/rig; cinco saídas reaproveitadas na retomada. [QA e limites](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-CAMERA-BATCH-V1.json). 38 tomadas visuais sem aprovação; próximo plano técnico C01-P05. Registros anteriores abaixo são históricos.

**EP01 — continuação de câmera (17/11/2026):** nova [Action C01-P04 #44213509153](https://github.com/HelioConde/VideoForge-IA/actions/runs/44213509153) passou. Pipeline de prévias retomáveis e limitações em [EP01-CAMERA-BATCH-PREVIEWS](docs/EP01-CAMERA-BATCH-PREVIEWS.md); estado operacional no [EP01](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-RETOMADA-PRODUCAO-EP01.json). Histórico abaixo preservado. Sem mãos independentes e sem promoção automática de arte ou rig.

**EP01 — C01-P04 / PREVIEW MP4 CÂMERA SEM MÃOS (17/11/2026):** O [MP4 técnico no artifact da execução #44211299311](https://github.com/HelioConde/VideoForge-IA/actions/runs/44211299311) foi **renderizado e verificado**: 70 frames, 30fps, H.264, 540×960, SHA `f4ee6c4c9c1f18432c9ba7d9b7d41c85bbc63a9d9cd6949a4fd09340e017bf38`; 0 chamadas de IA. A Action ficou vermelha apenas porque o contêiner não tem `git` para commitar QA após render; artifact foi enviado, correção posterior removendo comando git aplicada no workflow. [QA persistido](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-CAMERA-SEM-MAOS-V1.json), [estado principal](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). **Preview = câmera sobre mãe aprovada, NÃO rig nem MP4 oficial**; não aprovar animação de mãos, não reenviar partes rejeitadas. Inventário 39/39, próximos passos C01-P02/C01-P03 e QA de rig de peças realmente móveis.

**EP01 — RETOMADA 39/39 / NÃO REGERAR IMAGENS (17/11/2026):** Inventário oficial [39/39 mães arquivadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CHECKPOINT-IMAGENS-EP01-AUTO.json), C01-P01 preto. `EP01-40-TOMADAS-PRODUCAO.json` descreve fila inicial e NÃO é inventário atual: **não gerar novamente as 37 listadas como faltantes**. Somente C01-P04 V3 está aprovada individualmente por SHA. Regra vigente: mãos nunca separadas [política](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/POLITICA-SEM-MAOS-INDEPENDENTES-C01-P04.json). Priorizar prévia câmera-only da C01-P04, depois C01-P02/P03 e rigs de partes animáveis. [Estado consolidado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-RETOMADA-PRODUCAO-EP01.json), [checkpoint narrado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). Nunca declarar MP4 oficial nem YouTube final sem QA.

**EP01 C01-P04 — REGRA VIGENTE 17/11/2026: NÃO SEPARAR MÃOS**: O criador rejeitou TODAS as pegadas reconstruídas dos guardas (inclusive R3 e W3) e decidiu **ignorar a criação e rig de mãos/dedos/polegares**. Esta regra tem prioridade sobre os checkpoints antigos de hand grip abaixo, que são apenas histórico. NÃO fazer novas chamadas ao proxy para essas peças, NÃO reaproveitar versões reprovadas e NÃO cobrar QA de mão como gate da C01-P04. A mãe V3 aprovada preserva a pegada correta: manter mão e lança visualmente integradas/estáticas e, nessa tomada, usar **direção de câmera, zoom/pan, iluminação/efeitos** sem deformar ou soltar a arma. Se os PNGs de guarda/lança separados não recompõem a mãe, usar a imagem-mãe aprovada na tomada estática — não fingir rig articulado com movimento de PNG inteiro. Seguir com as demais tomadas/rig de partes que realmente se movem; manter QA próprio desses movimentos. Os workflows de geração de mãos e QA de pegada da C01-P04 estão desativados. [Regra executável](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/POLITICA-SEM-MAOS-INDEPENDENTES-C01-P04.json) e [estado principal](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). `rig_ready` global continua falso até os demais testes; MP4/upload não foram feitos.

**EP01 C01-P04 — CHECKPOINT DAS DUAS PEGADAS (17/11/2026):** [Prancha de confronto com a mãe aprovada](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-DUAS-PEGADAS-CONFERENCIA.jpg) concluída na [Action #44193979239](https://github.com/HelioConde/VideoForge-IA/actions/runs/44193979239). Candidatas: **esquerda R3 e direita W3**, ambas apenas para QA de composição, não para rig. Guarda direito tem três RGBA originais independentes (cuff, palma e dedos) com SHAs no [plano direito](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-PEGADA-DIREITA-C01-P04-V3.json); [plano anatômico geral](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-PEGADA-ANATOMICA-C01-P04-V3.json) vincula todos. O primeiro workflow direito #44190779781 pulou geração por preflight errado, já corrigido; não contabilizar arte nessa execução. QA do guarda direito R3 falhou por espaço entre braçadeira e palma, W3 melhora após deslocamento, mas **ainda exige validação visual humana** (contato, polegar, contorno das juntas, escala/rig e revisão temporal). Não usar PNG completo como animação, não dar aprovação automática por overlap 2D; preservar mãe aprovada e PNGs nativos, gates `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`. [Estado atualizado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md).

**EP01 / C01-P04 V3 — novo checkpoint anatômico (17/11/2026):** Três imagens RGBA INDEPENDENTES pelo proxy (antebraço, palma traseira, dedos dianteiros) foram geradas nas execuções `44186735696`, `44187319568`, `44187678728`; SHAs e canvas nativos registrados no [plano de pegada](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-PEGADA-ANATOMICA-C01-P04-V3.json). A [prancha de zoom R1/R2/R3](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-PEGADA-CONTATO-REGISTRO-V2-MAO-ZOOM.jpg) mostra melhora no posicionamento, e as [métricas alfa](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-PEGADA-CONTATO-METRICAS.json) indicam contato 2D positivo entre braço, palma, lança e dedos no R2/R3. **Isso NÃO é aprovação de anatomia, geometria de rig ou continuidade em movimento**; R3 é hipótese editorial de QA apenas. Não reutilizar V1 de dedos/punho fechado ou palma V2 grande como sprites finais. Manter `human_visual_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`. [Estado detalhado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). Priorizar revisão do encaixe da mão esquerda e só então repetir método no guarda direito.

**EP01 — PEGADA / CHECKPOINT V3 (17/11/2026):** A pegada ORIGINAL da imagem-mãe C01-P04 V3 foi confirmada como correta pelo criador: madeira da lança passa pela palma, dedos e polegar envolvem a haste e a base fica abaixo da mão. [Manifesto da referência](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REFERENCIA-PEGADA-APROVADA-C01-P04-V3.json). As tentativas de peças V1 foram reprovadas porque ambas mostraram punhos fechados; a palma V2 [#44184932210](https://github.com/HelioConde/VideoForge-IA/actions/runs/44184932210) gerou só braçadeira grande (1268×1241), foi **reprovada e arquivada**, não é palma. [Guia anatômico completo com lança visível](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-GUIA-PEGADA-V1-PREVIEW.jpg) foi gerado e continua apenas como referência de QA. Seguir [plano de 4 subcamadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-PEGADA-ANATOMICA-C01-P04-V3.json): antebraço/cuff; palma atrás; lança separada; dedos e polegar à frente. **Nenhuma mão/guarda separado aprovado; rig/Remotion/MP4/YouTube bloqueados.** [Estado com SHAs](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). Não repetir V1/V2, não recortar mãe em sprites finais.

**Dorama EP01 — QA da C01-P04 V3 (17/11/2026):** o [teste de registro espacial](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-REGISTRO-ESPACIAL.jpg) gerou três sobreposições por personagem para Aldric e o guarda esquerdo (sem novas imagens por IA). [Relatório de geometria e SHA](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-REGISTRO-ESPACIAL.json) registra alerta: o guarda esquerdo ocupa **95,07% da altura do PNG nativo**. Nenhuma proposta equivale a aprovação; as sete imagens foram arquivadas, mas o rig continua bloqueado. [Estado do projeto](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md) · [Plano das sete camadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-PECAS-C01-P04-V3.json).

**EP01 C01-P04 V3 — peças independentes (17/11/2026):** Após aprovação visual da imagem-mãe e alinhamento não destrutivo, o proxy produziu 7 PNGs independentes (fundo, Kael, Aldric, guardas e duas lanças), preservados com SHA. [Prancha QA da C01-P04 V3](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-CAMADAS-INDEPENDENTES.jpg) · [Manifesto de QA](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P04-V3-CAMADAS-INDEPENDENTES.json) · [Plano por componente](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-PECAS-C01-P04-V3.json) · [Estado completo](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). **5 peças têm canvas 941×1672; Aldric (981×1602) e guarda esquerdo (981×1602) são RGBA nativos pendentes de registro espacial.** Aldric saiu do proxy em canvas não conforme e NÃO está aprovado para composição/rig. Todas as peças aguardam QA visual e nenhuma foi liberada para animação ou publicação. [Fila de 4 partes #44160839815](https://github.com/HelioConde/VideoForge-IA/actions/runs/44160839815) e [QA #44161922010](https://github.com/HelioConde/VideoForge-IA/actions/runs/44161922010) concluíram com sucesso; ambos não aprovam arte automaticamente.

**EP01 — ESTADO ATUAL (17/11/2026):** **39/39 imagens-mãe geradas e arquivadas**, conforme [inventário automático](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CHECKPOINT-IMAGENS-EP01-AUTO.json). A abertura preta C01-P01 completa o plano de 40 tomadas. Em resposta à revisão do criador, foram geradas três **candidatas V3 da C01**, nas quais Kael ajoelhado deve se orientar para o trono e o rei (C01-P03, C01-P04 e alternativa); preservar versões anteriores e conferir composição/anatomia antes de promover. [Regra da correção](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CORRECAO-C01-EIXO-KAEL-TRONO-V3.md) · [Estado principal](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). **O estilo geral está aprovado; as V3 não estão aprovadas individualmente. Rig, sprites finais, MP4 e YouTube pendentes.**

**Dorama EP01 (17/11/2026):** [checkpoint automático](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CHECKPOINT-IMAGENS-EP01-AUTO.json) — **20 de 39 imagens-mãe geradas, 19 faltantes**. Foram geradas C04-P03, C05-P03, C06-P02, C07-P01/P02/P03 e C08-P01 com estilo geral aprovado pelo criador e referências SHA. [Detalhes e links no estado do EP01](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). Próxima tomada: C08-P02 (carrinho). PNGs continuam candidatos até QA específico; personagens/objetos móveis serão **novas imagens separadas pelo proxy**, jamais recortes da cena-mãe. Rig, MP4 e upload pendentes.

**Dorama EP01:** [inventário atualizado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CHECKPOINT-IMAGENS-EP01-AUTO.json) = **13 de 39 imagens-mãe geradas**, 26 sem mãe. Nova C06-P01 [Kael e bolsa vazia](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-scene-mother-v2/44088754480/c06-p01-scene-mother.png); [QA Arken](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C05-ARKEN-CONTINUIDADE.jpg) e [relatório visual](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAO-VISUAL-C05-ARKEN.md) concluídos sem IA. São arquivos candidatos com SHA, sem aprovação humana, rig ou publicação.

**Atualização do dorama EP01 (17/11):** [inventário automático de imagens](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/CHECKPOINT-IMAGENS-EP01-AUTO.json) mostra **12/39 tomadas visuais com mãe gerada, 27 restantes**; inclui fontes antigas reprovadas, não significa 12 cenas aprovadas. Novas C02-P02, C03-P01/P02, C04-P01/P02, C05-P01/P02 geradas via proxy e arquivadas. [QA de identidade C02-C03](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C02-C03-CONTINUIDADE-IMAGENS.jpg) e [QA do quarto gamer](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C03-C04-CONTINUIDADE-QUARTO.jpg) disponíveis. Novo cenário mestre [muralhas de Arken](canal/alchemy-lab/biblia-visual/INDEX-BIBLIA.json) criado antes de C05-P02. Gerar partes RGBA como **imagens independentes pelo proxy**, não recortes locais. Sem rig/MP4/upload aprovado.

**Dorama EP01 — checkpoint de imagens em 17/11:** [registro atualizado de 5 mães / 34 pendentes](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RESUMO-PRODUCAO-IMAGENS-EP01.md). C01-P05 e close C02-P01 gerados; C01-P03/P04 receberam **V2 corrigidas e arquivadas**. [Comparação visual](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-MAES-C01-P03-P04-V2.jpg): guardas removidos de P03 e Kael ajoelhado em P04. [Revisão técnica e limitações](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAO-VISUAL-MAES-C01-P03-P04-V2.md). As peças separadas produzidas pelo proxy para V1 de P03 foram reprovadas por escala; **não usar no rig V2**. Nada de aprovação humana, rig, MP4 ou YouTube nesta etapa.

**Dorama EP01 — produção de imagens retomada em 17/11:** [estado verificável](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RESUMO-PRODUCAO-IMAGENS-EP01.md). Criadas mães C01-P03 e C01-P04, mais PNGs **separados pelo proxy** para background e Kael de C01-P03. Modelos retornaram altura 1671 em vez de 1672; os PNGs foram preservados e alinhados em 1px sem recorte/resize ou gasto de IA. São candidatos sem aprovação visual. Pipeline e QA no GitHub; ainda faltam 36 mães das 39 tomadas visuais (C01-P02 mãe V1 está rejeitada). Próxima etapa: Aldric separado, recomposição e QA, sem rig/MP4/publicação até aprovação.

**Skills atualizadas (17/11):** catálogo local com **8 skills**, cobrindo arte/camadas, rig + atuação, QA independente, direção de tomadas, áudio/montagem e pesquisa técnica; há uma skill de coordenação do dorama. [Ver roteamento e auditoria das referências externas](docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md). Três novas skills: [direção](.agents/skills/videoforge-shot-direction/SKILL.md), [áudio/montagem](.agents/skills/videoforge-audio-editing/SKILL.md), [pesquisa técnica](.agents/skills/videoforge-technical-research/SKILL.md). **Não foram instaladas bibliotecas externas, nem criados agents executáveis.** As orientações só são aplicadas quando invocadas no fluxo e não garantem imagem/MP4 aprovado.

**NOVO FLUXO OBRIGATÓRIO — IMAGENS SEPARADAS PELO PROXY (17/11):** cena completa → pedir ao proxy **background vazio, personagem individual e cada objeto animável em imagens PNG próprias** usando cena-mãe e Bíblia como referências → pedir ao proxy as peças para rig → QA de transparência e recomposição → rig Remotion/Three.js e câmera. **Não usar recortes locais, máscaras por pixels ou segmentação para construir as peças animáveis.** O uso de máscara local fica restrito a QA. Ver [Contrato oficial](docs/CONTRATO-CAMADAS-GERADAS-PELO-PROXY.md) e [plano das 40 tomadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-CAMADAS-CAMERA-EP01.json). Legados desativados; cenas restantes ainda precisam de imagens reais e aprovação. O código antigo descrito nas notas históricas não substitui essa regra.

**Dorama EP01 — V4 C01-P02 gerada e QA concluído (17/11):** [prancha V1 × V3 × V4](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P02-CONTATO-V4.jpg) · [revisão de anatomia e continuidade](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAO-VISUAL-ASSISTIDA-C01-P02-V4.md). Duas imagens candidatas V4 SHA-verificadas e QA técnico aprovado; **mudança no ornamento do bocal exige revisão visual**. Nada foi aprovado como fonte canônica, ainda sem rig, MP4 ou upload.

**EP01 C01-P02 / V4 de reparo anatômico preparada (17/11):** nova geração versionada usa o patch V3 SHA-verificado e preserva fontes anteriores. Workflow [`ep01-contact-v4-by-request.yml`](.github/workflows/ep01-contact-v4-by-request.yml) gera no máximo uma candidata; [`qa-ep01-contact-v4-preview.yml`](.github/workflows/qa-ep01-contact-v4-preview.yml) compara V1/V3/V4. Avaliar pegada da luva e entrada física da lâmina antes de escolher mãe e reextrair camadas RGBA. Preparar fluxo não equivale a imagem gerada. Sem rig/MP4/upload até QA e aprovação.

**C01-P02 — Revisão visual da V3 (17/11):** [relatório assistido](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAO-VISUAL-ASSISTIDA-C01-P02-V3.md): bainha aparentemente externa ao traje, mas contato da mão inferior e alinhamento da lâmina com o bocal ainda não aprovados. O gate e a recomposição antigos referem-se às máscaras da V1; para V3 é obrigatória nova extração/QA de uma única mãe escolhida. Sem rig/MP4/publicação.

**Correção V3 do contato mão+bainha (painéis 2/4, 17/11):** usuário rejeitou painéis 2 e 4; o painel 4 é um close da própria mãe e exige correção local da fonte, não somente sobreposição. Uma nova [edição V3 + patch localizado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P02-CONTATO-V3.jpg) foi gerada e arquivada em [Actions #44047381550](https://github.com/HelioConde/VideoForge-IA/actions/runs/44047381550), QA comparativo [#44047543396](https://github.com/HelioConde/VideoForge-IA/actions/runs/44047543396). Tudo candidato pendente; origem V1 preservada, nenhum render/YouTube liberado.

**Falha de oclusão corrigida no planejamento: bainha na frente da roupa (17/11):** as imagens 3 e 4 da antiga prancha de deslocamentos foram rejeitadas. Ver [antes/depois e zoom C01-P02](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P02-BAINHA-FRENTE-ROUPA.jpg). O código agora compõe cenário → personagem/roupa → bainha → espada → mãos, sem refazer imagens por IA. QA passou; diferença média 7,654/255 ainda exige refinamento. Rig e YouTube bloqueados.

**C01-P02: extração original de bainha, espada e luvas sem IA (17/11):** [ver comparação com cena-mãe](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P02-ESPADA-PIXELS.jpg). O GitHub arquivou quatro máscaras RGBA em canvas 941×1672 derivadas dos pixels da composição original, preservando a ordem das luvas sobre as armas. O teste reduziu o delta RGB de 9,698 para 9,151/255, mas **não aprovou a composição**. `videoforge/ep01_contact_gate.py` impede render enquanto houver diferença excessiva ou faltar aprovação visual. Versões deslocadas e geração anterior da bainha continuam rejeitadas; MP4 não gerado.

**Fluxo oficial de vídeo: cena-mãe, camadas e câmera (17/11/2026):** utilizar imagens de referência SHA da Bíblia para gerar composição completa de cada tomada via proxy, separar background/figuras/objetos RGBA da **mesma cena**, articular o rig e depois aplicar movimentos de **câmera virtual e mudanças de foco** no Remotion. Não gerar biblioteca obrigatória de poses isoladas. Os 12 pedidos antigos foram desativados; os 42 mestres/9 reparos ficam preservados. [Plano de 40 tomadas com câmera](https://github.com/HelioConde/VideoForge-IA/blob/main/canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PLANO-CAMADAS-CAMERA-EP01.json) · [Manual oficial](https://github.com/HelioConde/VideoForge-IA/blob/main/canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/MANUAL-CENA-MAE-CAMADAS-CAMERA.md).

**Bíblia Visual EP01 completa na etapa de referências (17/11):** **42/42 referências individuais + 9/9 reparos V2**, 57 PNGs históricos SHA-verificados, sem aprovações humanas automáticas. Ver [galeria final](canal/alchemy-lab/biblia-visual/GALERIA-EP01.md), [laudo técnico das fontes](canal/alchemy-lab/biblia-visual/LAUDO-TECNICO-EP01.md) e [inspeção visual preliminar](canal/alchemy-lab/biblia-visual/QA-VISUAL-CANDIDATOS.md). A automação das 12 interações está preparada, mas **sem produzir poses/40 cenas/MP4 até revisão canônica e contato correto da mão na base da lança**.

**Atualização do dorama EP01 (17/11):** [QA das imagens](canal/alchemy-lab/biblia-visual/QA-VISUAL-CANDIDATOS.md) encontrou clonagem visual de Kael em coadjuvantes/mascarados e desviou a referência desses 5 personagens para o **salão do trono vazio**, sem elenco. São **9 candidatos de reparo V2** em [fila separada](canal/alchemy-lab/biblia-visual/FILA-REPAROS-EP01.json). Corrigido limite de 200KB do plano; [lote retomado pelo primeiro SHA faltante](https://github.com/HelioConde/VideoForge-IA/actions/runs/44009318478). Sem aprovação visual, rig de cenas ou publicação automática.

**QA do dorama EP01:** foram detectados desvios em Kael casual e na base da lança; [relatório visual](canal/alchemy-lab/biblia-visual/QA-VISUAL-CANDIDATOS.md), [4 correções V2 cadastradas](canal/alchemy-lab/biblia-visual/FILA-REPAROS-EP01.json). Os reparos são disparados após 42 referências-mestre para evitar chamadas simultâneas; nenhum candidato recebe aprovação automática.

**Atualização da geração EP01 (16/11/2026):** os mestres derivados usam PNG mestre real anexado por SHA; 12 interações físicas estão preparadas mas bloqueadas até aprovação humana, sem usar V3/V4 de pegada rejeitada. Gerador de lotes [visual-bible-batch.yml](.github/workflows/visual-bible-batch.yml); conferir o andamento real em [REGISTRO-GERACOES.json](canal/alchemy-lab/biblia-visual/REGISTRO-GERACOES.json). Nenhum vídeo final foi autorizado. 

# VideoForge IA — reconstrução orientada a MP4

**Geração em lote da Bíblia Visual:** [Fila de 42 referências individuais](canal/alchemy-lab/biblia-visual/FILA-GERACAO-MESTRES.json) · [GitHub Actions — orquestrador sequencial](.github/workflows/visual-bible-batch.yml) · [Primeira execução](https://github.com/HelioConde/VideoForge-IA/actions/runs/44005370074). No início havia 3 já geradas e 39 a produzir; 12 interações/poses e 37 tomadas novas ficam suspensas até aprovação visual e QA físico das mãos/lanças. Falhas interrompem a fila; **não afirmar que todas estão geradas sem conferir `REGISTRO-GERACOES.json`.**

**Bíblia Visual EP01 — primeiro cenário-mestre gerado (16/11):** [salão do trono vazio](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/assets/geracoes/production-art-request/44002126578/biblia-sala-do-trono-vazio-v1.png) criado em [GitHub Actions #44002126578](https://github.com/HelioConde/VideoForge-IA/actions/runs/44002126578) com fonte de estilo SHA-verificada. PNG 941×1672, SHA `1397aebed67213d0593ac32d1d7ba8d6a83511d39212368639833bec52cb43ee`; **7 imagens** registradas, sem aprovação humana do novo cenário. [Plano dos próximos mestres](canal/alchemy-lab/biblia-visual/PLANO-MESTRES-EP01.md): Kael, Aldric, Elara, guardas e lanças com contato na BASE. **37 tomadas do episódio continuam bloqueadas** até a Bíblia estar aprovada.

**Nova Bíblia Visual estruturada (P0):** [índice de personagens/cenários/objetos/interações](canal/alchemy-lab/biblia-visual/INDEX-BIBLIA.json), [39 fichas e status](canal/alchemy-lab/biblia-visual/README.md), [histórico por imagem com SHA](canal/alchemy-lab/biblia-visual/REGISTRO-GERACOES.md) e [fila das 40 tomadas do EP01](canal/alchemy-lab/biblia-visual/FILA-EP01.json). O arquivamento por GitHub agora registra PNG original + SHA + estado no mesmo commit. Nenhuma cena nova foi autorizada enquanto a pega na base das lanças estiver reprovada. [QA da Bíblia Visual](https://github.com/HelioConde/VideoForge-IA/actions/runs/43999926099) aprovado.

**Dorama EP01 V2 — comparação semântica preparada:** [pranchas das ROIs candidatas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-ROI-FIGURINOS-V2.md) e [resultado por região](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RELATORIO-ROI-SEMANTICA-V2.md). Quatro partes aguardam máscaras específicas validadas; nenhuma aprovação de identidade ou figurino foi inferida. O filtro novo consegue reprovar mudança vermelho/preto em regiões verificadas e passa nos testes sintéticos.

**Controle de qualidade de pixels no dorama V2:** [medição das cores nas camadas reais de Aldric](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-CORES-MEDIDAS-FIGURINO-V2.md), com [metadados e SHA](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-CORES-PIXELS-FIGURINO-V2.json). Quatro camadas RGBA são mensuráveis; barba, exterior/centro e corpete de Elara ainda sem ROI validada. Nenhuma arte foi aprovada pelo histograma.

**Filtro EP01 V2 de figurinos:** [reprovações detalhadas de Aldric (inversão vermelho/preto e barba), Elara (corpete roxo) e checklist de Kael](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RELATORIO-APROVACAO-REPROVACAO-FIGURINO.md). Fonte: diferenças reportadas pelo proprietário; sem alegar medição automática de cor por pixel. O roteiro tem 40 tomadas, nenhuma aprovação visual ou publicação automática.

**Dorama EP01 V2 — nova revisão de figurinos:** [Aldric e Elara em comparação ampliada](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-DETALHES-FIGURINOS-V2.md) e [contrato de continuidade das 40 tomadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REGRAS-FIGURINOS-V2-40-TOMADAS.md). O antigo registro de 37 tomadas é histórico. Não gerar R2 nem vídeo com trajes reprovados. Não há aprovação automática de identidade.

**Dorama MMORPG EP01 — revisão de figurinos:** [ver 6 referências existentes de Aldric e Elara](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-OPCOES-FIGURINO-V2.md). A prancha V2 anterior foi reprovada por diferenças de roupas; as referências estão em revisão, não são canônicas. Nenhuma nova imagem R2 foi solicitada ou gerada.

**EP01 V2 — revisão visual de identidade (16/11/2026):** os três PNGs originais de Kael, Elara e C12-P02 estão SHA-verificados. [Comparar personagens e prancha V2](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REVISAR-IDENTIDADE-EP01-V2.md) antes de autorizar rig/animação: [Kael](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-KAEL-V2-COMPARACAO.jpg) | [Elara](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-ELARA-V2-COMPARACAO.jpg). As prévias são apenas para QA, não aprovam o novo desenho. O MP4 final e a publicação continuam pendentes.

> **AUTORIZAÇÃO DE CHAMADAS DO EP01 V2 — 15/11/2026:** o responsável autorizou permanentemente as chamadas de IA/imagem necessárias ao remake, sem pedir confirmação por imagem; `autonomy-policy.json` permite um gasto de geração por execução do produtor e não define teto editorial total. O coordenador reserva e solicita automaticamente a primeira candidata `character-bible` uma vez, com registro durável e sem repetição cega. A existência de autorização **não** comprova que a API respondeu, que houve cobrança, que alguma arte foi aprovada nem que um vídeo foi publicado. YouTube segue bloqueado.

> **Rig da espada: QA de geometria por pixels reais adicionado.** `remake_rig_geometry.py` e os workflows de pacote/preview exigem relatório `mask-geometry.qa.json` revalidável para C01-P02, com máscara, centroide, SHA e quatro poses. O restante dos 39 planos ainda depende de arte própria; não foi criado MP4 oficial nem liberado custo.

> **Abertura original do remake V2:** `videoforge/remake_episode_audio.py` prepara a mesma WAV por síntese procedural + SHA auditado para o futuro vídeo integral; independe da retenção de 90 dias dos artifacts. O render oficial continua bloqueado pelos 39 planos visuais sem QA.

> **Direção animada V2 disponível:** [40 tomadas e 160 ações temporizadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-v2-motion-directions.json), com câmera, elenco, rig, fases e QA por plano; validador `videoforge/remake_motion_directions.py` e integração à fila dos agentes. **São instruções**, não PNGs/MP4 gerados. Sem rig/autorização visual/custo não renderiza vídeo oficial.

> **Compositor V2 corrigido para 40 tomadas:** [EDL editorial oficial](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-v2-cinematic-edl.json) · `videoforge/remake_v2_edl.py` · `motion-remotion/src/cinematic-timeline.ts`. O legado 37-shot permanece intocado. A abertura preta exige o áudio original no render do episódio. Aguardando assets reais e revisão.

> **Plano V2 agora com 40 tomadas (14 cenas, 163s):** [manifesto ativo](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-ep01-planos.json) · [roteiro atualizado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/roteiro.json) · [direção oficial](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REMAKE-EP01-PLANO-OFICIAL.md). Três novos inserts: C01-P05, C08-P04, C12-P04. Existem 39 tomadas visuais planejadas, mas não foram geradas imagens adicionais nem liberados custos.

> **C01-P02:** novo produtor `videoforge/remake_sword_source.py` + `remake-sword-component.yml` prepara underlay RGB e três peças RGBA por tomada verdadeira, com gate de custo e apenas execução manual. A automação de pacote e render já está ligada; ainda **sem âncora V2 aprovada/sem PNGs finais/sem MP4 da tomada**. [Documentação da fonte/rig](docs/C01-P02-PACOTE-ARTE-E-RIG.md).

> **C01-P02:** empacotamento de arte por SHA e gatilho de render autônomo conectados em `remake-sword-pack.yml` → `remake-sword-preview.yml`. [Pacote e requisitos técnicos](docs/C01-P02-PACOTE-ARTE-E-RIG.md). Fonte V2 e underlay ainda ausentes: sem novos PNGs nem MP4 da tomada.

> **EP01 C01-P02:** prévia articulada agora tem entrada própria no Remotion + validação SHA/PNG/recomposição com FFmpeg (decodificação de PNG para QA) e Python stdlib (composição de pixels): [pacote de arte e rig](docs/C01-P02-PACOTE-ARTE-E-RIG.md). O preflight de GitHub Actions não gera PNG e só libera render com fonte real e referência V2 aprovada.

> **Reutilizacao de bibliotecas e skills:** [catalogo integrado](docs/BIBLIOTECAS-E-SKILLS-VIDEOFORGE.md) · [direcao do remake](.agents/skills/videoforge-dorama-remake/SKILL.md) · [rig Three.js](.agents/skills/videoforge-rig-2d-three/SKILL.md) · [QA e memoria](.agents/skills/videoforge-qa-and-checkpoint/SKILL.md). Novos geradores devem consumir a fila `videoforge/remake_starter.py`, o `remake_autopilot.py` e componentes ThreeCanvas ja instalados. Nenhum novo gasto/MP4 foi habilitado.

> **INTEGRAÇÃO DE CENAS DO REMAKE V2:** o workflow de imagens agora separa o EP01 remake do caminho legado, exige tomada específica e confere o PNG de referência aprovado no próprio GitHub por SHA + manifesto. Essa ligação de software **não cria imagens automaticamente** nem dá autorização para serviços pagos ou YouTube.

> **AUTONOMIA DO VIDEOFORGE (15/11/2026):** [manual de operação autônoma](docs/AUTONOMIA-PRODUCAO-VIDEOS.md) · [coordenador verificável](videoforge/remake_autopilot.py) · [workflow diário](.github/workflows/remake-autonomy.yml). A meta é o programa produzir e corrigir os vídeos por si, enquanto damos direção editorial. O primeiro módulo já diagnostica o próximo passo e atualiza o checkpoint; o encadeamento completo de imagens, rigs, QA e MP4 ainda precisa ser integrado e testado. **Não tratar planejamento como vídeo gerado, nem chamar API paga sem permissão.**

> **REMAKE EP01 ATIVO (15/11/2026):** [plano de refação](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REMAKE-EP01-PLANO-OFICIAL.md) · [manifesto das 40 tomadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/remake-ep01-planos.json) · [checkpoint obrigatório](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). **Geração de novas artes autorizada editorialmente para o remake**, sem cota artificial, preservando V5/C12 anteriores como legado. O lock de 14/11 foi arquivado, não está mais ativo. Ainda não existem novas imagens, rig aprovado ou MP4 oficial do remake; não gastar serviços externos nem publicar sem permissão específica.

> **REGRA NOVA DE QUALIDADE DO DORAMA (15/11/2026):** sem teto editorial de imagens — quando autorizadas, criar quantos ângulos, imagens-mãe, camadas e refinamentos forem necessários para uma animação bonita, detalhada e consistente. **Antes e depois de todo avanço, consultar e atualizar o arquivo mestre [ESTADO-ATUAL.md](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md)**, sincronizando [histórico](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/HISTORICO-DESENVOLVIMENTO.md) e [JSON](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/estado-atual.json). Não perder o progresso nem refazer etapas concluídas. **O usuário autorizou posteriormente refazer o EP01 com novas imagens (remake V2)**; o bloqueio anterior está arquivado. Esta mudança documental não gera mídia, não concede orçamento e não autoriza publicação.

> **NOVO PADRÃO VISUAL EXCLUSIVO DO DORAMA / Alchemy Lab:** [área dorama](canal/alchemy-lab/dorama/README.md) · [prompt oficial — Cinematic Semi-Realistic Fantasy Anime](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PROMPT-OFICIAL-ESTILO-DORAMA.md) · [manifesto JSON](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/estilo-visual-oficial-dorama.json) · [amostra em miniatura](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REFERENCIA-VISUAL-DORAMA-PREVIEW-96.jpg). Quase toda cena deverá ser dramática e filmada de ângulo diferente, com continuidade de rostos, armaduras, luz e arquitetura. **Regra editorial aplicada ao remake autorizado em 15/11/2026:** o lock anterior é histórico, não vigente. O registro da política isoladamente não produz render, geração ou publicação.

> **CONTINUIDADE OBRIGATÓRIA NA MAIN — NÃO RECOMEÇAR DO ZERO:** antes de trabalhar, ler [AGENTS.md](AGENTS.md) e o [protocolo de continuidade](docs/CONTINUIDADE-DO-PROJETO.md), depois o `ESTADO-ATUAL.md` e o `HISTORICO-DESENVOLVIMENTO.md` do vídeo. **Cada conclusão/alteração precisa atualizar esses arquivos na mesma integração à `main`**, com run, commit, artifact, SHA, pendências e próximo passo. Branches antigas e chats não substituem esse registro. Episódio ativo: [dorama MMORPG — checkpoint e MP4s técnicos C01/C12](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md).


> **ATUAL — C01-P03 V5 (15/11/2026):** [relatório do movimento das costas e QA real](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V5-2026-11-15.md) · [manifesto V5](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/atuacao-c01-p03-v5-respiracao-costas.json) · [checkpoint](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md). [PR #58](https://github.com/HelioConde/VideoForge-IA/pull/58) **integrado na main**, commit `ae7ca09c3f75ed04498704459a2ac547de810d06`; [render + QA main #43680784142](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784142) e [TS/testes #43680784182](https://github.com/HelioConde/VideoForge-IA/actions/runs/43680784182) **SUCCESS**. **Respiração suave das costas em malha RGBA original** (até 1,05px expansão / 0,6px elevação), **cabeça continua mexendo levemente** (máximo 0,32°); braço/mão/joelho/pé direitos travados, rei/coroa e lanças estáticos com pixels originais. MP4 3s/90f/1080×1920/30fps SHA-256 `d84361f693f4e1c83b4d5ad7bd7ed55c253044e672fbf80af803ace58b865481`, artifact temporário `14147374656` idêntico ao PR. **QA técnico aprovado, aprovação artística humana pendente; sem geração de imagens, sem YouTube.** V4/V3 são checkpoints **históricos**, não a versão ativa.

> **C01-P03 V4 — direção corrigida pelo usuário em 15/11/2026:** [pesquisa de bibliotecas e skills](docs/PESQUISA-SKILLS-BIBLIOTECAS-RIGGING-2D-2026-11-15.md) · [regras de animação — somente respiração](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/REGRAS-ATUACAO-C01-P03-RESPIRACAO-2026-11-15.md) · [roteiro técnico de atuação V4](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/atuacao-c01-p03-v4-respiracao.json) · [PR #57](https://github.com/HelioConde/VideoForge-IA/pull/57). **A V3 passou QA técnico, mas foi rejeitada visualmente:** braço direito afastava-se do apoio, pé ficava cortado, lanças ruins e cabeça do rei incompleta. A V4 trabalha com 2 tracks leves de respiração e cabeça, mão/bota ancoradas em mundo e rei/lanças da imagem-mãe original, sem gerar imagens novas. **V4 integrada à main (PR #57, commit `4d010a92212ce77e9c7fbcf762537ecf0e732be2`):** [render/QA 43676630976](https://github.com/HelioConde/VideoForge-IA/actions/runs/43676630976) **SUCCESS**; [relatório permanente V4](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V4-2026-11-15.md). MP4 técnico de 3s/90f/1080×1920, SHA `90baea03b4e2b551a21d341c263853a2e9b9d4d5647314fff46a39bf79fbbff7`. **Aprovado tecnicamente, NÃO visualmente nem para YouTube.**

> **DORAMA ALCHEMY LAB — C01-P03 V3 EM MAIN (15/11/2026):** [Checkpoint atualizado](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/ESTADO-ATUAL.md) · [relatório técnico completo, inclusive tentativas reprovadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/QA-C01-P03-V3-2026-11-15.md) · [histórico permanente](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/HISTORICO-DESENVOLVIMENTO.md). [PR #56](https://github.com/HelioConde/VideoForge-IA/pull/56) integrado, [render da main 43673610507](https://github.com/HelioConde/VideoForge-IA/actions/runs/43673610507) **SUCCESS** com MP4 técnico de 3 s/1080×1920/90 frames (SHA-256 `73993ab7b1f93aead42d1860d16c3db965adcbd3e6bdf2794eb631a9d704100c`). **Movimento real 18.923 ≥16.000 e exposição da gola 73 ≤75: gates técnicos passaram; a aprovação visual não.** O rig usa nove trilhas independentes nesse plano, 113 no episódio, cabeça ≤1,82°, proteção de gola feita somente de pixels originais, nenhum novo desenho. **Pendências:** recomposição neutra ainda com erro RGB ≈11,16, recortes de guardas/lanças/Aldric, inspeção de bota/mão e demais planos; C12 bloqueada por PNGs originais. **Não publicar no YouTube.**

> **ARQUIVAMENTO AUTOMÁTICO DE IMAGENS:** imagens produzidas pelos geradores do GitHub devem ser preservadas permanentemente em canal/ID/videos/ID/assets/geracoes/PRODUCER/RUN_ID/, com SHA-256 e manifesto. Os artifacts do Actions, com prazo de expiração, não são o arquivo definitivo. **[Guia e recuperações verificadas de PNGs antigos](docs/ARQUIVAMENTO-PERMANENTE-IMAGENS.md)**. A implementação reutilizável está em videoforge/persist_generated_assets.py e scripts/persistir-imagens-gh.sh. Os jobs de arte, cenas, lotes, sprites e imagens manuais devem commitar os PNGs antes de reportar sucesso. As imagens criadas fora do runner (ChatGPT) ainda exigem importação dos bytes: referências catalogadas no chat não são PNGs já arquivados. O bloqueio de novas imagens do episódio Alchemy Lab EP01 permanece inalterado.


> **MANUAL PRINCIPAL DE ANIMAÇÃO 2D (OBRIGATÓRIO PARA TODOS OS CANAIS):** [Leia primeiro o manual de malha Three.js + Remotion](docs/MANUAL-PRINCIPAL-ANIMACAO-2D.md). Ele tem prioridade sobre regras antigas de bob/câmera/pálpebras em overlay. Nenhuma animação oficial deve ser classificada como rig articulado quando apenas o PNG inteiro se move. Exigir cena-mãe, partes RGBA independentes, reconstrução de regiões ocultas, rig por pivôs/malhas, comparação com arte original, QA e aprovação. **Sem sprites reais completos, manter como pipeline pendente.**

> **ECONOMIA DE TOKENS (Codex CLI):** [Configuração econômica inicial](.codex/config.toml) e [guia com pesquisa da comunidade](docs/ECONOMIA-CODEX-ASTRA.md). Usar Sol para manutenção normal, Astra Standard somente por escalada; não ativar Ultrafast por padrão. **Isso não modifica o Codex Proxy, não gera imagens e não autoriza novos custos**. O manual principal de animação mantém precedência.

> **LEITURA OBRIGATÓRIA (antes de qualquer tarefa):** [AGENTS.md](AGENTS.md) → [Arquitetura das pastas](docs/ARQUITETURA.md) → [Regras editoriais dos vídeos](docs/REGRAS-EDITORIAIS.md) → [Regras do canal](canal/README.md) → **[Estratégia específica do canal](canal/README.md#estratégias-específicas-por-canal) e `canal/<id>/ESTRATEGIA.md`** → [Cursos de referência](docs/referencias/CATALOGO-CURSOS-YOUTUBE.md) → [Guia oficial YouTube Creators](docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md) → [Infraestrutura Codex Proxy](docs/CODEX-PROXY-ACTIONS.md).
>
> **Prioridade absoluta:** preservar a estrutura existente **`canal/<id>/`** (singular), `modelos/`, `geradores/`, `videoforge/`, `tests/` e `docs/`. Cada vídeo tem seus dados e histórico dentro de seu próprio canal; não criar `canais/` nem misturar informações entre canais. Cursos de YouTube são **referências para estudo**, não aulas já assistidas. A análise oficial do YouTube Creators está registrada com fontes e ressalvas; políticas devem ser revalidadas antes de publicar.
>
> Esta organização mantém o MVP apenas como **teste técnico**. Vídeo oficial exige o fluxo real e integrado do programa (agentes, arte, animação, voz, edição, QA e proveniência no GitHub); nenhuma prévia substitui essa integração. Sem publicação automática ou IA paga nesta etapa.

## Regra nº 1 — Vídeos exclusivamente pelo programa VideoForge-IA no GitHub

**Todo vídeo solicitado como produção oficial deve ser criado pelo fluxo de produção do repositório [HelioConde/VideoForge-IA](https://github.com/HelioConde/VideoForge-IA), executado e rastreável no GitHub Actions.** Esta regra tem prioridade sobre qualquer exemplo, demonstração, script temporário, renderer externo ou solução improvisada.

1. Usar o **programa reutilizável do projeto**, seus modelos, agentes e etapas reais, organizados em `canal/<id>/videos/<video-id>/`. Não criar um gerador paralelo específico de um único vídeo para contornar componentes ausentes.
2. Pesquisa/roteiro → arte consistente por cena → separação de personagens e cenários em camadas → animação → narração → edição/legendas → QA técnico e visual. Executar cada etapa disponível e registrar as que ainda faltam. **Não simular agentes ou artes como se tivessem sido gerados.**
3. Gerar MP4 no runner do GitHub Actions do próprio repositório; registrar workflow, run ID, commit, entrada, manifesto por canal, SHA-256, artefato e relatórios de QA. Baixar ou mostrar a cópia do MP4 é permitido, mas **não** criar/substituir a produção fora do programa.
4. Se faltarem agentes, imagens ou integração do fluxo principal, **parar como `assets_pendentes` / `pipeline_pendente` e explicar a limitação**. Não substituir por desenho vetorial, cartões ou narração sintética genérica e apresentar o resultado como o vídeo oficial solicitado. Previews experimentais podem existir para testar motores, sempre marcadas claramente como **`preview_tecnico_nao_oficial`**.
5. Apenas uma execução verificável do fluxo principal, com materiais realmente gerados e verificados, pode receber o rótulo `video_oficial_do_programa=true`. Render bem-sucedido no GitHub, por si só, **não significa** produção completa pelos agentes.
6. **Sem limite artificial para quantidade de cenas**. Segurança, licenças, orçamento aprovado, duração e QA permanecem obrigatórios. Publicação no YouTube exige autorização e verificação próprias.

**Correção histórica:** o teste *Spy x Family* da execução [43545398967](https://github.com/HelioConde/VideoForge-IA/actions/runs/43545398967) foi renderizado pelo GitHub Actions, mas usou `videoforge.spy_family_animated` e desenhos vetoriais de prévia, **não** o fluxo oficial completo de artes/agentes. É um teste técnico, não produção oficial do VideoForge-IA.

**Estado atual:** há renderizadores de testes técnicos, mas a produção oficial ainda exige integrar pesquisa, agentes, modelos de imagem, animação, voz e QA ao fluxo principal. Não classificar MP4 experimental como trabalho concluído do gerador. O repositório
anterior, agora `HelioConde/video-forge-ia2`, permanece intacto e serve
somente como referência para organização.

## Estratégia editorial de Shorts

Os materiais de crescimento/SEO enviados em 2026-11-13 foram sintetizados
em [Estratégia de YouTube Shorts](docs/ESTRATEGIA_SHORTS.md), que inclui
pesquisa, antirrepetição por canal, retenção, consistência visual,
métricas e fontes oficiais atualizadas. **Leia o guia antes de planejar**;
essas práticas ainda não são automações implementadas.

## Infraestrutura IA: Codex Proxy e Actions\n\nO componente central planejado de IA é [10/chatgpt-codex-proxy](https://github.com/10/chatgpt-codex-proxy). Os workflows manuais [build de imagem do proxy](.github/workflows/proxy-image.yml) e [teste/geração de imagem](.github/workflows/proxy-images.yml) usam imagem Docker precompilada ou um serviço HTTPS com sessão persistente, sem reinstalar Go em todo job. **Confira o passo a passo de secrets e os limites** em [docs/CODEX-PROXY-ACTIONS.md](docs/CODEX-PROXY-ACTIONS.md). Esta infraestrutura não significa que credenciais já foram configuradas, imagem foi gerada ou publicação foi habilitada.\n\n## Ferramentas de mídia reutilizadas nos workflows

O workflow [MVP MP4](.github/workflows/mvp.yml) usa a imagem pré-compilada `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2`, com Python 3.12, FFmpeg 6.x e fontes. O build fica isolado em [media-image.yml](.github/workflows/media-image.yml); cada job faz apenas pull da imagem, **não** reinstala Go, Python ou FFmpeg. O Codex Proxy tem sua imagem separada.

## Aproveitar as contas do Codex Proxy anterior

Para migrar a sessão já autorizada do contêiner Docker antigo sem novo login no Codex, o [script local de migração](scripts/migrar-codex-proxy.ps1) envia o estado privado aos Secrets do novo repositório pelo `gh` CLI. Consulte [as instruções e limitações](docs/CODEX-PROXY-ACTIONS.md). Secrets antigos do GitHub não podem ser lidos de volta pela API.

## Testes de decomposicao de cena com IA (separados do MVP)

Os workflows [Teste 1 - background e personagem](.github/workflows/scene-layers-basic.yml) e [Teste 2 - foreground e objetos animaveis](.github/workflows/scene-layers-advanced.yml) usam **a mesma cena-base** obtida no artifact do Codex Proxy. A geracao e manual e limitada a no maximo 2 edicoes de imagem por run; PNGs e manifesto ficam somente em artifacts organizados por canal. Consulte o [guia de testes de camadas](docs/TESTE-CAMADAS-CENA.md). A edicao e generativa: transparencia tecnica nao garante recorte fiel, coordenadas ou animacao pronta.

## Prévia animada das camadas em MP4 (sem IA)

O [Teste 3 de animação](.github/workflows/animate-separated-layers.yml) usa os PNGs de background, personagem e telhado obtidos pela separação para criar uma prévia parallax de 6–10 segundos com **movimentos independentes**. O motor `videoforge/animate_layers.py` verifica o artifact, renderiza H.264/AAC e confere movimento real entre quadros. **A capa isolada ainda não é usada** porque permanece dentro do sprite completo e seria duplicada; o vídeo é técnico, sem narração e sem envio ao YouTube. [Instruções](docs/ANIMACAO-CAMADAS.md).

## Remotion original — nova prévia animada por camadas

O motor **principal para a nova prévia** é agora [Remotion do AutoEditorVideo](motion-remotion/): reutilizamos as funções do projeto anterior em uma composição React que movimenta camera, personagem e foreground por frame. O novo [workflow manual Remotion](.github/workflows/remotion-animate-layers.yml) usa os PNGs dos artifacts reais com validação de SHA-256, renderiza MP4 com H.264/AAC e QA de movimento, **sem gastar IA ou instalar npm/Chrome toda vez**. Consulte [guia do Remotion](docs/REMOTION-ANIMACAO.md). O renderizador antigo de parallax FFmpeg permanece somente como teste/fallback documentado; a capa não é sobreposta até remover sua versão duplicada do personagem.

## Preparacao visual do rig com pixels da cena original (rascunho)

A nova etapa de [preparação dos sprites](docs/PREPARAR-RIG-CANDIDATO.md) usa o artifact original verificado para produzir **seis camadas candidatas**, separando a capa em frente e trás e reconhecendo os dois olhos parcialmente visíveis. O workflow `rig-candidate.yml` gera máscaras, contact sheet, hashes e proveniência **sem IA e sem publicar**. Os recortes ainda não reconstroem anatomia escondida e permanecem bloqueados para uso como rig aprovado.

## Rig 2D por malha — implementacao opt-in (ainda sem sprites aprovados)

O novo [MVP de rig 2D](docs/RIG-MALHA-2D.md) acrescenta ao Remotion um **warp por triangulos da capa**, **pivo da cabeca no pescoco** e **piscadas em quadros definidos**. O codigo e validadores existem; a ativacao depende de cinco PNGs RGBA sem partes duplicadas, hashes e revisao visual humana. Sem rig, o workflow permanece no modo legado; **nao existe ainda MP4 real aprovado deste modo novo**. Nao habilita publicacao nem o modelo `camadas-animadas` para producao.

## Regra permanente: sem teto de quantidade de cenas

**O gerador não deve impor limite fixo de cenas** (nem 10, 24, 30 ou outro valor arbitrário). Roteiros, manifestos e renderizadores devem aceitar qualquer número **positivo** de cenas válido, determinado pela narrativa. O motor renderiza e valida cena a cena, sem reduzir, mesclar, cortar ou descartar cenas apenas por terem ultrapassado uma contagem pré-definida.

Esta regra não remove o QA, a exigência de assets reais, as verificações de direitos, a segurança contra abuso, o orçamento autorizado de IA, os limites operacionais do GitHub Actions nem a **duração** do formato. Por enquanto o piloto Shorts do Otaku BR permanece com 90–180 segundos; se a narrativa não couber, deve ser adaptada ou planejada para formato mais longo, não ter cenas apagadas automaticamente. Mudanças no número de cenas não significam publicação ou geração de IA automática.

## O que já funciona

- Compositor FFmpeg de **imagens e narrações fornecidas**, com legendas,
  MP4 H.264/AAC vertical 1080 × 1920.
- QA automático de vídeo, áudio, duração, resolução e SHA-256.
- Smoke test no GitHub Actions produz clipe técnico sintético de ~5 segundos
  (não é vídeo editorial, não é produção de agentes, sem IA paga).
- Produção do primeiro Otaku Multicena exige **90–180 segundos**
  e a autorização humana para qualquer integração futura de IA.
- Não há publicação no YouTube, nem credenciais no Git.

## Pastas — igual ao VideoForge anterior

```text
canal/
  otaku-br/                         # Otaku Multicena, piloto
    canal.json                      # opções / modelo padrão
    conteudos/indice.json           # referências, não fila automática
    editorial/
      candidatos.json               # pesquisas autenticadas futuras
      reservas.json                 # antirrepetição, começa vazio
      pesquisas/YYYY-MM-DD.json     # futuro, só pesquisa verificável
    videos/
      <video-id>/video.json         # manifesto por vídeo
  otaku-en/                         # Otaku Reframe
  gamer/                            # Conde Games
  manu-kids/                        # Emanuelly Kids
  alchemy-lab/                      # Alchemy Lab
modelos/
  imagem-estatica/modelo.json       # implementado: imagens fornecidas
  camadas-animadas/modelo.json      # PLANEJADO, ainda não implementado
geradores/                          # receitas de nicho futuras
videoforge/                         # código reutilizável
tests/                              # testes offline e FFmpeg
docs/ARQUITETURA.md                 # regra permanente de organização
output/
  <channel>/videos/<video-id>/      # MP4 e QA; ignorado pelo Git
```

Confira [regras dos canais](canal/README.md),
[modelos](modelos/README.md) e
[arquitetura](docs/ARQUITETURA.md).

**Isolamento:** nenhum vídeo, métrica, pauta ou reserva de um canal pode ser
usado como se fosse de outro. O código valida canal e modelo, e bloqueia
o destino de saída fora de seu diretório.

## Executar

Requer Python 3.12+ e FFmpeg/FFprobe no PATH, sem dependências Python extras.

```bash
python -m unittest discover -s tests -v
python -m videoforge.mvp smoke --output dist/smoke.mp4
```

Após fornecer **mídia realmente existente** e o manifesto aprovado:

```bash
python -m videoforge.mvp render --video canal/otaku-br/videos/episodio-001/video.json
```

Esse comando gera o arquivo e relatório QA em:
`output/otaku-br/videos/episodio-001/video.mp4` e
`output/otaku-br/videos/episodio-001/video.qa.json`.

O manifesto `video.json` tem este formato **ilustrativo**:

```json
{
  "schema": "videoforge/mvp/v1",
  "channel": "otaku-br",
  "modelo": "imagem-estatica",
  "youtube_upload": false,
  "scenes": [
    {"image": "imagens/cena-01.png", "audio": "voz/cena-01.mp3", "caption": "Legenda 1"},
    {"image": "imagens/cena-02.png", "audio": "voz/cena-02.mp3", "caption": "Legenda 2"},
    {"image": "imagens/cena-03.png", "audio": "voz/cena-03.mp3", "caption": "Legenda 3"}
  ]
}
```

Os arquivos de imagens e voz devem existir ao lado de `video.json` nos
respectivos subdiretórios, mas **não são versionados**. A narração somada
precisa durar 90–180 segundos. O manifesto de exemplo **não contém mídia
nem aprova a escolha do tema**.

`modelo` é opcional no vídeo e usa por padrão `canal.json.modelo_padrao`.
O Otaku Multicena tinha `camadas-animadas` como padrão provisório no antigo
projeto; nesta reconstrução usa `imagem-estatica` **temporariamente** para
entregar um MP4 real primeiro. O modelo de camadas ainda está desativado.

## Próximos marcos

1. Preservar o MP4 técnico aprovado pelo CI após organização por canal.
2. Renderizar vídeo de 90–180s com áudio e imagens reais, sem falar em
   agentes até haver evidências dos trabalhos deles.
3. Só depois implementar pesquisa, três agentes independentes,
   provedores de IA com limites, identidade visual e animações.
4. YouTube Analytics, QA editorial e publicação são etapas separadas;
   nunca enviar conteúdo automaticamente.

**QA técnico não é aprovação editorial ou visual.**

## Rig de direção cinematográfica — C01

A [animação por direção](docs/ANIMACAO-POR-DIRECAO.md) usa o motor real ThreeCanvas/Remotion para executar pivôs, hierarquia de peças e keyframes do roteiro com PNGs originais. O [manifesto de C01-P03](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/direcao-bindings-c01-draft.json) e o [workflow](.github/workflows/directed-rig-preview.yml) reproduzem uma prévia técnica de 3 segundos da cena do trono e arquivam MP4 e evidências em GitHub Actions.

**Importante:** a prévia possui arte ainda não aprovada, máscaras e underlays pendentes e marca de rascunho. Não é o episódio completo nem autoriza geração de imagens ou publicação. O C12 tem [pré-voo de fontes separadas](canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/RENDER-C12-TECNICO.md) e permanece bloqueado até importar seus originais.

**Revisão rápida das artes do dorama:** [Galeria da Bíblia Visual EP01](canal/alchemy-lab/biblia-visual/GALERIA-EP01.md) — pranchas JPG atualizadas por lote usando PNGs reais SHA-verificados; só exibição, sem geração nem aprovação automática.
